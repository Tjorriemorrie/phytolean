import datetime
import logging
from datetime import timedelta
import pytz

import pandas as pd
import plotly.graph_objects as go
from django.core.cache import cache
from django.db.models import Count, Q
from django.db.models.functions import TruncHour, ExtractHour, ExtractDay
from django.utils import timezone

import main.constants as c
from main.models import Psychic, Status

logger = logging.getLogger(__name__)

CACHE_TIMEOUT_1_HOUR = 60 * 60
SAST = pytz.timezone('Africa/Johannesburg')


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
    Returns a list of dicts, one per hour (0-23), with counts of online and oncall statuses for the past 30 days.
    All hours are in SAST (GMT+2).
    """
    now_utc = timezone.now()
    start_utc = now_utc - timedelta(days=30)

    # Extract hour in UTC, then shift to SAST in Python
    statuses = (
        Status.objects
        .filter(
            psychic_id=psychic_id,
            status_at__gte=start_utc,
            status_at__lt=now_utc,
        )
        .annotate(hour_utc=ExtractHour('status_at'))
        .values('hour_utc', 'status')
        .annotate(count=Count('id'))
        .order_by('hour_utc')
    )

    hour_status_counts = {}
    for row in statuses:
        # Shift hour from UTC to SAST (GMT+2), wrap around 24
        hour = (row['hour_utc'] + 2) % 24
        status = row['status']
        count = row['count']
        if hour not in hour_status_counts:
            hour_status_counts[hour] = {}
        hour_status_counts[hour][status] = count

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
    Returns a list of dicts, one per hour (0-23), with unique counts of online and oncall psychics for the past 30 days.
    All hours are in SAST (GMT+2).
    """
    cache_key = "all_psychics_halfhourly_unique_counts_v2"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now_utc = timezone.now()
    start_utc = now_utc - timedelta(days=30)

    online_statuses = (
        Status.objects
        .filter(
            status_at__gte=start_utc,
            status_at__lt=now_utc,
            status=c.PSYCHIC_STATUS_ONLINE,
        )
        .annotate(hour_utc=ExtractHour('status_at'))
        .values('hour_utc', 'psychic')
    )

    oncall_statuses = (
        Status.objects
        .filter(
            status_at__gte=start_utc,
            status_at__lt=now_utc,
            status=c.PSYCHIC_STATUS_ONCALL,
        )
        .annotate(hour_utc=ExtractHour('status_at'))
        .values('hour_utc', 'psychic')
    )

    online_by_hour = {}
    oncall_by_hour = {}
    for row in online_statuses:
        hour = (row['hour_utc'] + 2) % 24
        psychic = row['psychic']
        online_by_hour.setdefault(hour, set()).add(psychic)
    for row in oncall_statuses:
        hour = (row['hour_utc'] + 2) % 24
        psychic = row['psychic']
        oncall_by_hour.setdefault(hour, set()).add(psychic)

    result = []
    for slot in range(24):
        result.append({
            "hour": slot,
            "online": len(online_by_hour.get(slot, set())),
            "oncall": len(oncall_by_hour.get(slot, set())),
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


def get_all_psychics_daily_unique_counts():
    """
    Returns a list of dicts, one per day of month (1-31), with unique counts of online and oncall psychics
    for the past 30 days. All times are in SAST (GMT+2).
    """
    cache_key = "all_psychics_daily_unique_counts_v1"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now_utc = timezone.now()
    start_utc = now_utc - timedelta(days=30)

    online_statuses = (
        Status.objects
        .filter(
            status_at__gte=start_utc,
            status_at__lt=now_utc,
            status=c.PSYCHIC_STATUS_ONLINE,
        )
        .annotate(day=ExtractDay('status_at'))
        .values('day', 'psychic')
    )

    oncall_statuses = (
        Status.objects
        .filter(
            status_at__gte=start_utc,
            status_at__lt=now_utc,
            status=c.PSYCHIC_STATUS_ONCALL,
        )
        .annotate(day=ExtractDay('status_at'))
        .values('day', 'psychic')
    )

    online_by_day = {}
    oncall_by_day = {}
    for row in online_statuses:
        day = row['day']
        online_by_day.setdefault(day, set()).add(row['psychic'])
    for row in oncall_statuses:
        day = row['day']
        oncall_by_day.setdefault(day, set()).add(row['psychic'])

    result = []
    for day in range(1, 32):
        result.append({
            "day": day,
            "online": len(online_by_day.get(day, set())),
            "oncall": len(oncall_by_day.get(day, set())),
        })

    cache.set(cache_key, result, CACHE_TIMEOUT_1_HOUR)
    return result


def get_oncall_online_ratio_heatmap():
    """
    Returns a 7x24 grid (day_of_week x hour) of oncall/online ratios
    for the past 90 days. All hours are in SAST (GMT+2).

    Output shape:
    {
        "days": ["Mon", "Tue", ...],
        "hours": [0, 1, ..., 23],
        "data": [[ratio_h0, ratio_h1, ...], ...]  # 7 rows (days) x 24 cols (hours)
    }
    """
    from django.db.models.functions import ExtractWeekDay

    cache_key = "oncall_online_ratio_heatmap_v1"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    now_utc = timezone.now()
    start_utc = now_utc - timedelta(days=90)

    statuses = (
        Status.objects
        .filter(
            status_at__gte=start_utc,
            status_at__lt=now_utc,
            status__in=[c.PSYCHIC_STATUS_ONCALL, c.PSYCHIC_STATUS_ONLINE],
        )
        .annotate(
            hour_utc=ExtractHour('status_at'),
            dow_utc=ExtractWeekDay('status_at'),  # 1=Sunday .. 7=Saturday
        )
        .values('hour_utc', 'dow_utc', 'status')
        .annotate(count=Count('id'))
    )

    # Build counts grid keyed by (sast_dow, sast_hour)
    oncall_grid = {}
    online_grid = {}

    for row in statuses:
        hour_utc = row['hour_utc']
        dow_utc = row['dow_utc']  # 1=Sun..7=Sat
        status = row['status']
        count = row['count']

        # Shift to SAST (UTC+2)
        sast_hour = (hour_utc + 2) % 24
        # If hour wraps past midnight, advance the day
        day_offset = 1 if (hour_utc + 2) >= 24 else 0

        # Convert Django's 1=Sun..7=Sat to 0=Mon..6=Sun
        # Django: 1=Sun,2=Mon,3=Tue,4=Wed,5=Thu,6=Fri,7=Sat
        py_dow = (dow_utc - 2) % 7  # 0=Mon..6=Sun
        sast_dow = (py_dow + day_offset) % 7

        if status == c.PSYCHIC_STATUS_ONCALL:
            oncall_grid[(sast_dow, sast_hour)] = oncall_grid.get((sast_dow, sast_hour), 0) + count
        else:
            online_grid[(sast_dow, sast_hour)] = online_grid.get((sast_dow, sast_hour), 0) + count

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    hours = list(range(24))

    data = []
    for dow in range(7):
        row = []
        for h in range(24):
            oncall = oncall_grid.get((dow, h), 0)
            online = online_grid.get((dow, h), 0)
            if online > 0:
                ratio = round(oncall / online, 2)
            elif oncall > 0:
                ratio = round(oncall, 2)  # all oncall, no online
            else:
                ratio = 0
            row.append(ratio)
        data.append(row)

    result = {"days": days, "hours": hours, "data": data}
    cache.set(cache_key, result, CACHE_TIMEOUT_1_HOUR)
    return result


def get_psychic_sessions(psychic_id, days=30):
    """
    Returns sessions for a psychic, with all datetimes in SAST (GMT+2).
    Consecutive statuses of the same type are merged into a single session.
    Each session's start_at is the first occurrence of that status, and end_at is the next different status's status_at (in SAST).
    For the last session, end_at is the last status's status_at (SAST-adjusted, but not double-adjusted).
    """
    now_utc = timezone.now()
    start_utc = now_utc - timedelta(days=days)

    statuses = list(
        Status.objects
        .filter(psychic_id=psychic_id, status_at__gte=start_utc, status_at__lt=now_utc)
        .order_by('status_at')
        .values('status', 'status_at')
    )

    sessions = []
    current_status = None
    current_start = None
    last_sast_dt = None

    for i, status_record in enumerate(statuses):
        status = status_record["status"]
        status_at = status_record["status_at"]
        if timezone.is_naive(status_at):
            status_at = timezone.make_aware(status_at, datetime.timezone.utc)
        sast_dt = status_at + timedelta(hours=2)
        last_sast_dt = sast_dt

        if current_status is None:
            current_status = status
            current_start = sast_dt
        elif status != current_status:
            end_at = sast_dt
            duration = int((end_at - current_start).total_seconds() // 60)
            duration = max(duration, 0)
            sessions.append({
                "status": current_status,
                "start_at": current_start,
                "end_at": end_at,
                "duration_minutes": duration,
            })
            current_status = status
            current_start = sast_dt

    # Close the last session
    if current_status is not None and current_start is not None:
        end_at = last_sast_dt if last_sast_dt is not None else current_start
        duration = int((end_at - current_start).total_seconds() // 60)
        duration = max(duration, 0)
        sessions.append({
            "status": current_status,
            "start_at": current_start,
            "end_at": end_at,
            "duration_minutes": duration,
        })

    return reversed(sessions)
