from datetime import timedelta

from django.utils import timezone

import main.constants as c
from django.db.models import QuerySet, OuterRef, Subquery, Count, ExpressionWrapper, IntegerField, \
    F, Q, Value, FloatField, When, Case, BooleanField

from main.models import Psychic, Status


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
