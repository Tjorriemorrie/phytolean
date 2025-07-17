from datetime import timedelta

from django.utils import timezone

import main.constants as c
from django.db.models import QuerySet, OuterRef, Subquery, Count, ExpressionWrapper, IntegerField, \
    F, Q, Value, FloatField, When, Case, BooleanField

from main.models import Psychic, Status


def list_psychics_online() -> QuerySet[Psychic]:
    latest_status = Status.objects.filter(
        psychic=OuterRef('pk')
    ).order_by('-status_at')

    psychics = Psychic.objects.annotate(
        last_status=Subquery(latest_status.values('status')[:1])
    ).filter(last_status__in=[c.PSYCHIC_STATUS_ONLINE, c.PSYCHIC_STATUS_ONCALL])

    return psychics


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
        oncall_minutes=ExpressionWrapper(F('oncall_count') * 15, output_field=IntegerField()),
        online_minutes=ExpressionWrapper(F('online_count') * 15, output_field=IntegerField()),
        total_minutes=ExpressionWrapper(
            (F('oncall_count') + F('online_count')) * 15,
            output_field=IntegerField()
        ),
        oncall_online_ratio=ExpressionWrapper(
            Case(
                When(online_count=0, then=Value(0.0)),
                default=F('oncall_count') * 1.0 / F('online_count'),
                output_field=FloatField()
            ),
            output_field=FloatField()
        )
    ).order_by('-oncall_online_ratio')

    return psychics
