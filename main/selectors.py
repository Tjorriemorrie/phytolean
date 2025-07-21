import logging

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import timedelta, datetime

from django.db.models.functions import TruncHour
from django.utils import timezone

import main.constants as c
from django.db.models import QuerySet, OuterRef, Subquery, Count, ExpressionWrapper, IntegerField, \
    F, Q, Value, FloatField, When, Case, BooleanField, Max

from main.models import Psychic, Status


logger = logging.getLogger(__name__)


def list_psychics_with_status_monthly() -> QuerySet[Psychic]:
    one_month_ago = timezone.now() - timedelta(days=30)

    latest_status_subquery = Status.objects.filter(
        psychic=OuterRef('pk')
    ).order_by('-status_at').values('status')[:1]

    psychics = Psychic.objects.annotate(
        oncall_count=Count(
            'statuses',
            filter=Q(
                statuses__status=c.PSYCHIC_STATUS_ONCALL,
                statuses__status_at__gte=one_month_ago
            )
        ),
        online_count=Count(
            'statuses',
            filter=Q(
                statuses__status=c.PSYCHIC_STATUS_ONLINE,
                statuses__status_at__gte=one_month_ago
            )
        ),
        latest_status=Subquery(latest_status_subquery),
    ).annotate(
        is_currently_online=Case(
            When(latest_status__in=[c.PSYCHIC_STATUS_ONLINE, c.PSYCHIC_STATUS_ONCALL],
                 then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        ),
        oncall_hours=ExpressionWrapper(F('oncall_count') / Value(4.0), output_field=FloatField()),
        online_hours=ExpressionWrapper(F('online_count') / Value(4.0), output_field=FloatField()),
        total_hours=ExpressionWrapper(
            (F('oncall_count') + F('online_count')) / Value(4.0),
            output_field=FloatField()
        ),
        score=ExpressionWrapper(
            (F('oncall_count') / Value(4.0)) + (F('online_count') / Value(4.0) * Value(0.1)),
            output_field=FloatField()
        )
    ).order_by('-score')

    return psychics


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


def get_last_scrape_date() -> datetime:
    return Status.objects.aggregate(last_status_at=Max('status_at'))['last_status_at']
