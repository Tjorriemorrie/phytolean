import logging
from datetime import timedelta, datetime

import pandas as pd
import plotly.graph_objects as go
from django.db.models import QuerySet, OuterRef, Subquery, Count, IntegerField, \
    Q, Value, Max, Exists
from django.db.models.functions import TruncHour, Coalesce, ExtractHour
from django.utils import timezone

import main.constants as c
from main.models import Psychic, Status

logger = logging.getLogger(__name__)


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


def get_psychic_hourly_activity_aggregates(psychic_id, month=None):
    """
    Returns hourly activity counts (Online + Oncall) for a specific psychic.
    Defaults to the current month.

    Output shape:
    [
        {"hour": 0, "count": int},
        {"hour": 1, "count": int},
        ...
        {"hour": 23, "count": int},
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
        .filter(
            psychic_id=psychic_id,
            status_at__gte=start,
            status_at__lt=end,
            status__in=[c.PSYCHIC_STATUS_ONLINE, c.PSYCHIC_STATUS_ONCALL],
        )
        .annotate(hour=ExtractHour('status_at'))
        .values('hour')
        .annotate(count=Count('id'))
        .order_by('hour')
    )

    # Create a dict for quick lookup
    hour_counts = {row['hour']: row['count'] for row in statuses}

    # Return all 24 hours, filling in zeros for missing hours
    return [
        {"hour": h, "count": hour_counts.get(h, 0)}
        for h in range(24)
    ]


def get_psychic_monthly_stats(psychic_id, month=None):
    """
    Returns monthly status counts for a specific psychic.
    """
    now = timezone.now()
    month = month or now

    start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)

    result = (
        Status.objects
        .filter(psychic_id=psychic_id, status_at__gte=start, status_at__lt=end)
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
