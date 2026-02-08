import logging
from datetime import timedelta, datetime

import pandas as pd
import plotly.graph_objects as go
from django.core.cache import cache
from django.db.models import QuerySet, OuterRef, Subquery, Count, IntegerField, \
    Q, Value, Max, Exists
from django.db.models.functions import TruncHour, Coalesce, ExtractHour, ExtractMinute
from django.utils import timezone

import main.constants as c
from main.models import Psychic, Status

logger = logging.getLogger(__name__)

CACHE_TIMEOUT_1_HOUR = 60 * 60


def generate_status_hourly_plot():
    # Query and round to the hour
    qs = (
        Status.objects
        .annotate(hour=TruncHour('status_at'))
        .values('hour', 'status')
        .annotate(count=Count('id'))
        .order_by('hour')
    )
    df = pd.DataFrame(list(qs))

    if df.empty:
        return go.Figure().update_layout(title='No status data available')

    # Ensure all statuses appear even if missing
    expected_statuses = ['Offline', 'Oncall', 'Online']
    df_pivot = df.pivot(index='hour', columns='status', values='count').fillna(0)

    # Add any missing columns manually
    for status in expected_statuses:
        if status not in df_pivot.columns:
            df_pivot[status] = 0

    # Sort by hour and by column name (to avoid plotting order issues)
    df_pivot = df_pivot[expected_statuses].sort_index()

    colors = {
        'Offline': 'royalblue',
        'Oncall': 'tomato',
        'Online': 'mediumseagreen',
    }

    # Plot
    fig = go.Figure()

    for status in expected_statuses:
        fig.add_trace(go.Scatter(
            x=df_pivot.index,
            y=df_pivot[status],
            name=status,
            mode='lines',
            stackgroup='one',  # Ensures stacked plot
            line=dict(width=0.5),
            fillcolor=colors[status],
        ))

    fig.update_layout(
        title='Psychic Statuses Over Time (Hourly) - Latest Status per Psychic',
        xaxis_title='Hour',
        yaxis_title='Status Count',
        hovermode='x unified',
    )

    fig.update_xaxes(
        tickformat="%H:%M\n%b %d"
    )

    return fig


def get_monthly_psychic_status_aggregates(month=None):
    """
    Returns per-psychic status counts for the given month.
    Defaults to the current month.

    Output shape:
    [
        {
            "psychic": <Psychic>,
            "online": int,
            "offline": int,
            "oncall": int,
            "fake_oncall": int,
            "total": int,
        },
        ...
    ]
    """
    now = timezone.now()
    month = month or now

    start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)

    statuses = (
        Status.objects
        .filter(status_at__gte=start, status_at__lt=end)
        .values("psychic")
        .annotate(
            online=Count("id", filter=Q(status=c.PSYCHIC_STATUS_ONLINE)),
            offline=Count("id", filter=Q(status=c.PSYCHIC_STATUS_OFFLINE)),
            oncall=Count("id", filter=Q(status=c.PSYCHIC_STATUS_ONCALL)),
            fake_oncall=Count("id", filter=Q(status=c.PSYCHIC_STATUS_FAKE)),
            total=Count("id"),
        )
    )

    psychics = Psychic.objects.in_bulk([s["psychic"] for s in statuses])

    return [
        {
            "psychic": psychics[row["psychic"]],
            "online": row["online"] * c.MINUTES_PER_SAMPLE,
            "offline": row["offline"] * c.MINUTES_PER_SAMPLE,
            "oncall": row["oncall"] * c.MINUTES_PER_SAMPLE,
            "fake_oncall": row["fake_oncall"] * c.MINUTES_PER_SAMPLE,
            "total": row["total"] * c.MINUTES_PER_SAMPLE,
        }
        for row in statuses
    ]


def get_psychic_hourly_activity_aggregates(psychic_id):
    """
    Returns hourly activity counts split by status (Online and Oncall) for a specific psychic.
    Uses a rolling 30-day window from now.

    Output shape:
    [
        {"hour": 0, "online": int, "oncall": int},
        {"hour": 1, "online": int, "oncall": int},
        ...
        {"hour": 23, "online": int, "oncall": int},
    ]
    """
    now = timezone.now()
    start = now - timedelta(days=30)

    statuses = (
        Status.objects
        .filter(
            psychic_id=psychic_id,
            status_at__gte=start,
            status_at__lt=now,
        )
        .annotate(hour=ExtractHour('status_at'))
        .values('hour', 'status')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    # Create a nested dict for quick lookup: {hour: {status: count}}
    hour_status_counts = {}
    for row in statuses:
        hour = row['hour']
        status = row['status']
        count = row['count']
        if hour not in hour_status_counts:
            hour_status_counts[hour] = {}
        hour_status_counts[hour][status] = count

    # Return all 24 hours with online and oncall counts
    return [
        {
            "hour": h,
            "online": hour_status_counts.get(h, {}).get(c.PSYCHIC_STATUS_ONLINE, 0),
            "oncall": hour_status_counts.get(h, {}).get(c.PSYCHIC_STATUS_ONCALL, 0),
        }
        for h in range(24)
    ]


def get_psychic_monthly_stats(psychic_id):
    """
    Returns status counts for a specific psychic.
    Uses a rolling 30-day window from now.
    """
    now = timezone.now()
    start = now - timedelta(days=30)

    result = (
        Status.objects
        .filter(psychic_id=psychic_id, status_at__gte=start, status_at__lt=now)
        .aggregate(
            online=Count("id", filter=Q(status=c.PSYCHIC_STATUS_ONLINE)),
            offline=Count("id", filter=Q(status=c.PSYCHIC_STATUS_OFFLINE)),
            oncall=Count("id", filter=Q(status=c.PSYCHIC_STATUS_ONCALL)),
            fake_oncall=Count("id", filter=Q(status=c.PSYCHIC_STATUS_FAKE)),
            total=Count("id"),
        )
    )

    return {
        "online": result["online"] * c.MINUTES_PER_SAMPLE,
        "offline": result["offline"] * c.MINUTES_PER_SAMPLE,
        "oncall": result["oncall"] * c.MINUTES_PER_SAMPLE,
        "fake_oncall": result["fake_oncall"] * c.MINUTES_PER_SAMPLE,
        "total": result["total"] * c.MINUTES_PER_SAMPLE,
    }


def get_daily_oncall_counts():
    """
    Returns daily total oncall counts for all psychics.
    Uses a rolling 60-day window from now.
    This is an absolute sum (not unique psychics).

    Output shape:
    [
        {"date": "2026-02-01", "oncall": int},
        {"date": "2026-02-02", "oncall": int},
        ...
    ]
    """
    from django.db.models.functions import TruncDate

    now = timezone.now()
    start = now - timedelta(days=60)

    statuses = (
        Status.objects
        .filter(
            status_at__gte=start,
            status_at__lt=now,
            status=c.PSYCHIC_STATUS_ONCALL,
        )
        .annotate(date=TruncDate('status_at'))
        .values('date')
        .annotate(oncall=Count('id'))
        .order_by('date')
    )

    # Build lookup dict
    date_counts = {row['date']: row['oncall'] for row in statuses}

    # Generate all dates in the 60-day range
    result = []
    current_date = start.date()
    end_date = now.date()
    while current_date <= end_date:
        result.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "date_short": current_date.strftime("%m/%d"),
            "oncall": date_counts.get(current_date, 0),
        })
        current_date += timedelta(days=1)

    # Calculate max value for scaling to fit 200px container
    max_oncall = max((r["oncall"] for r in result), default=1) or 1
    scale_factor = 200 / max_oncall  # pixels per unit

    # Add pixel heights (scaled to fit 200px container)
    for r in result:
        r["oncall_height_px"] = r["oncall"] * scale_factor

    return result


def get_all_psychics_hourly_unique_counts():
    """
    Returns half-hourly unique psychic counts for online and oncall statuses.
    Uses a rolling 30-day window from now.
    Counts each psychic only once per half-hour slot if they had at least one status of that type.
    If a psychic was oncall during a half-hour, they are NOT counted as online (oncall takes priority).
    Cached for 1 hour.

    Output shape:
    [
        {"slot": 0, "label": "0:00", "online": int, "oncall": int, "online_height_pct": float, "oncall_height_pct": float},
        {"slot": 1, "label": "0:30", "online": int, "oncall": int, "online_height_pct": float, "oncall_height_pct": float},
        ...
        {"slot": 47, "label": "23:30", "online": int, "oncall": int, "online_height_pct": float, "oncall_height_pct": float},
    ]
    """
    cache_key = "all_psychics_halfhourly_unique_counts_v2"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now = timezone.now()
    start = now - timedelta(days=30)

    # Get all online statuses with hour and minute
    online_statuses = (
        Status.objects
        .filter(
            status_at__gte=start,
            status_at__lt=now,
            status=c.PSYCHIC_STATUS_ONLINE,
        )
        .annotate(
            hour=ExtractHour('status_at'),
            minute=ExtractMinute('status_at'),
        )
        .values('hour', 'minute', 'psychic')
    )

    # Get all oncall statuses with hour and minute
    oncall_statuses = (
        Status.objects
        .filter(
            status_at__gte=start,
            status_at__lt=now,
            status=c.PSYCHIC_STATUS_ONCALL,
        )
        .annotate(
            hour=ExtractHour('status_at'),
            minute=ExtractMinute('status_at'),
        )
        .values('hour', 'minute', 'psychic')
    )

    # Build sets of psychics per half-hour slot for oncall
    # slot = hour * 2 + (1 if minute >= 30 else 0)
    oncall_by_slot = {}  # {slot: set of psychic_ids}
    for row in oncall_statuses:
        slot = row['hour'] * 2 + (1 if row['minute'] >= 30 else 0)
        if slot not in oncall_by_slot:
            oncall_by_slot[slot] = set()
        oncall_by_slot[slot].add(row['psychic'])

    # Build sets of psychics per half-hour slot for online (excluding those who were oncall)
    online_by_slot = {}  # {slot: set of psychic_ids}
    for row in online_statuses:
        slot = row['hour'] * 2 + (1 if row['minute'] >= 30 else 0)
        psychic_id = row['psychic']
        # Only count as online if not oncall in this slot
        if psychic_id not in oncall_by_slot.get(slot, set()):
            if slot not in online_by_slot:
                online_by_slot[slot] = set()
            online_by_slot[slot].add(psychic_id)

    # Build result for all 48 half-hour slots
    result = []
    for slot in range(48):
        hour = slot // 2
        is_hour_start = slot % 2 == 0
        minute = "30" if slot % 2 else "00"
        result.append({
            "slot": slot,
            "hour": hour,
            "is_hour_start": is_hour_start,
            "label": f"{hour}:{minute}",
            "online": len(online_by_slot.get(slot, set())),
            "oncall": len(oncall_by_slot.get(slot, set())),
        })

    # Calculate max values for scaling to fit 200px container
    max_combined = max((r["online"] + r["oncall"] for r in result), default=1) or 1
    scale_factor = 200 / max_combined  # pixels per unit

    # Add pixel heights (scaled to fit 200px container for stacked bars)
    for r in result:
        r["online_height_px"] = r["online"] * scale_factor
        r["oncall_height_px"] = r["oncall"] * scale_factor

    cache.set(cache_key, result, CACHE_TIMEOUT_1_HOUR)
    return result
