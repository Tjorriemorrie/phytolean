import json

from django.contrib import admin
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export.resources import ModelResource

from main.models import Discovery, Booking, Survey, Psychic, Status, Role, PayFastTransaction
from main.selectors import (
    get_monthly_psychic_status_aggregates,
    get_rolling_psychic_status_aggregates,
    get_psychic_hourly_activity_aggregates,
    get_psychic_monthly_stats,
    get_all_psychics_hourly_unique_counts,
    get_all_psychics_daily_unique_counts,
    get_daily_oncall_counts,
    get_psychic_sessions,
    get_oncall_online_ratio_heatmap,
)


@admin.register(Discovery)
class DiscoveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'first_name', 'last_name', 'email', 'cell', 'created_at']
    ordering = ['status', '-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'start_at', 'slug', 'created_at', 'discovery']
    ordering = ['-start_at']


class SurveyResource(ModelResource):
    class Meta:
        model = Survey


@admin.register(Survey)
class SurveyAdmin(ImportExportModelAdmin, ExportActionMixin):
    resource_class = SurveyResource
    list_display = ['id', 'created_at', 'name']
    ordering = ['-created_at']


@admin.register(Psychic)
class PsychicAdmin(admin.ModelAdmin):
    pass


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(PayFastTransaction)
class PayFastTransactionAdmin(admin.ModelAdmin):
    # List view columns
    list_display = (
        'id', 'user_email', 'm_payment_id', 'pf_payment_id',
        'item_name', 'amount_gross', 'amount_fee', 'amount_net',
        'payment_status', 'created_at'
    )

    # Searchable fields
    search_fields = ('user_email', 'm_payment_id', 'pf_payment_id', 'email_address')

    # Filters
    list_filter = ('payment_status', 'created_at')

    # Ordering
    ordering = ('-created_at',)

    # Read-only fields
    readonly_fields = (
        'm_payment_id', 'pf_payment_id', 'amount_gross', 'amount_fee',
        'amount_net', 'payment_status', 'signature', 'created_at'
    )


def sa_psychics(request):
    context = {
        **admin.site.each_context(request),
        "title": "SA Psychics",
    }
    return TemplateResponse(
        request,
        "admin/sa_psychics.html",
        context,
    )


TABLE_CURRENT_CACHE_SECONDS = 5 * 60
TABLE_HISTORICAL_CACHE_SECONDS = 20 * 60 * 60


def _month_offset(offset):
    now = timezone.now()
    month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    for _ in range(offset):
        if month.month == 1:
            month = month.replace(year=month.year - 1, month=12)
        else:
            month = month.replace(month=month.month - 1)
    return month


_TABLE_SORT_KEY = lambda r: (
    -r["oncall"],
    -r["online"],
    -r["fake_oncall"],
    r["offline"],
)


def _table_payload(rows):
    rows.sort(key=_TABLE_SORT_KEY)
    return {
        "rows": [
            {
                "rank": i + 1,
                "name": r["psychic"].name,
                "url": reverse("admin:psychic-detail", args=[r["psychic"].id]),
                "oncall": r["oncall"],
                "online": r["online"],
                "fake_oncall": r["fake_oncall"],
                "offline": r["offline"],
            }
            for i, r in enumerate(rows)
        ],
    }


def _monthly_table_payload(month):
    return _table_payload(get_monthly_psychic_status_aggregates(month=month))


@cache_page(TABLE_CURRENT_CACHE_SECONDS)
def sa_psychics_table_rolling(request):
    return JsonResponse(_table_payload(get_rolling_psychic_status_aggregates(days=120)))


@cache_page(TABLE_CURRENT_CACHE_SECONDS)
def sa_psychics_table_current(request):
    return JsonResponse(_monthly_table_payload(_month_offset(0)))


@cache_page(TABLE_HISTORICAL_CACHE_SECONDS)
def sa_psychics_table_previous(request):
    return JsonResponse(_monthly_table_payload(_month_offset(1)))


@cache_page(TABLE_HISTORICAL_CACHE_SECONDS)
def sa_psychics_table_two_months_ago(request):
    return JsonResponse(_monthly_table_payload(_month_offset(2)))


CHART_CACHE_SECONDS = 20 * 60 * 60


@cache_page(CHART_CACHE_SECONDS)
def sa_psychics_hourly_chart(request):
    hourly_unique = get_all_psychics_hourly_unique_counts()
    return JsonResponse({
        "labels": [f"{h['hour']}:00" for h in hourly_unique],
        "online": [h["online"] for h in hourly_unique],
        "oncall": [h["oncall"] for h in hourly_unique],
    })


@cache_page(CHART_CACHE_SECONDS)
def sa_psychics_daily_unique_chart(request):
    daily_unique = get_all_psychics_daily_unique_counts()
    return JsonResponse({
        "labels": [str(d['day']) for d in daily_unique],
        "online": [d["online"] for d in daily_unique],
        "oncall": [d["oncall"] for d in daily_unique],
    })


@cache_page(CHART_CACHE_SECONDS)
def sa_psychics_daily_chart(request):
    daily_oncall = get_daily_oncall_counts()
    return JsonResponse({
        "labels": [d["date_short"] for d in daily_oncall],
        "oncall": [d["oncall"] for d in daily_oncall],
        "is_weekend": [d["is_weekend"] for d in daily_oncall],
    })


@cache_page(CHART_CACHE_SECONDS)
def sa_psychics_heatmap_chart(request):
    return JsonResponse(get_oncall_online_ratio_heatmap())


def psychic_detail_view(request, psychic_id):
    from main.models import Psychic
    psychic = Psychic.objects.get(id=psychic_id)

    now = timezone.now()
    month = now.replace(day=1)

    monthly_stats = []
    for _ in range(6):
        monthly_stats.append({
            "label": month.strftime("%b %Y"),
            "stats": get_psychic_monthly_stats(psychic_id, month=month),
        })
        if month.month == 1:
            month = month.replace(year=month.year - 1, month=12)
        else:
            month = month.replace(month=month.month - 1)

    hourly = get_psychic_hourly_activity_aggregates(psychic_id)
    hourly_chart_data = json.dumps({
        "labels": [f"{h['hour']}:00" for h in hourly],
        "online": [h["online"] for h in hourly],
        "oncall": [h["oncall"] for h in hourly],
    })

    sessions = get_psychic_sessions(psychic_id, days=7)

    context = {
        **admin.site.each_context(request),
        "title": f"Psychic: {psychic.name}",
        "psychic": psychic,
        "monthly_stats": monthly_stats,
        "hourly_chart_data": hourly_chart_data,
        "sessions": sessions,
    }

    return TemplateResponse(
        request,
        "admin/psychic_detail.html",
        context,
    )


original_get_urls = admin.site.get_urls


def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('sa-psychics/', admin.site.admin_view(sa_psychics), name='sa-psychics'),
        path(
            'sa-psychics/charts/hourly.json',
            admin.site.admin_view(sa_psychics_hourly_chart),
            name='sa-psychics-chart-hourly',
        ),
        path(
            'sa-psychics/charts/daily-unique.json',
            admin.site.admin_view(sa_psychics_daily_unique_chart),
            name='sa-psychics-chart-daily-unique',
        ),
        path(
            'sa-psychics/charts/daily.json',
            admin.site.admin_view(sa_psychics_daily_chart),
            name='sa-psychics-chart-daily',
        ),
        path(
            'sa-psychics/charts/heatmap.json',
            admin.site.admin_view(sa_psychics_heatmap_chart),
            name='sa-psychics-chart-heatmap',
        ),
        path(
            'sa-psychics/tables/rolling-120-days.json',
            admin.site.admin_view(sa_psychics_table_rolling),
            name='sa-psychics-table-rolling',
        ),
        path(
            'sa-psychics/tables/current.json',
            admin.site.admin_view(sa_psychics_table_current),
            name='sa-psychics-table-current',
        ),
        path(
            'sa-psychics/tables/previous.json',
            admin.site.admin_view(sa_psychics_table_previous),
            name='sa-psychics-table-previous',
        ),
        path(
            'sa-psychics/tables/two-months-ago.json',
            admin.site.admin_view(sa_psychics_table_two_months_ago),
            name='sa-psychics-table-two-months-ago',
        ),
        path('psychic/<int:psychic_id>/', admin.site.admin_view(psychic_detail_view), name='psychic-detail'),
    ]
    return custom_urls + urls


admin.site.get_urls = get_urls
