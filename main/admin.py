import json

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.utils import timezone
from django.views.decorators.cache import cache_page
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export.resources import ModelResource

from main.models import Discovery, Booking, Survey, Psychic, Status, Role, PayFastTransaction
from main.selectors import (
    get_monthly_psychic_status_aggregates,
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


@cache_page(60 * 60)
def sa_psychics(request):
    now = timezone.now()

    current_month = now.replace(day=1)

    if current_month.month == 1:
        previous_month = current_month.replace(
            year=current_month.year - 1,
            month=12,
        )
    else:
        previous_month = current_month.replace(
            month=current_month.month - 1,
        )

    if previous_month.month == 1:
        two_months_ago = previous_month.replace(
            year=previous_month.year - 1,
            month=12,
        )
    else:
        two_months_ago = previous_month.replace(
            month=previous_month.month - 1,
        )

    psychics_current_month = get_monthly_psychic_status_aggregates(
        month=current_month
    )
    psychics_previous_month = get_monthly_psychic_status_aggregates(
        month=previous_month
    )

    sort_key = lambda r: (
        -r["oncall"],
        -r["online"],
        -r["fake_oncall"],
        r["offline"],
    )

    psychics_current_month.sort(key=sort_key)
    psychics_previous_month.sort(key=sort_key)

    psychics_two_months_ago = get_monthly_psychic_status_aggregates(
        month=two_months_ago
    )
    psychics_two_months_ago.sort(key=sort_key)

    hourly_unique = get_all_psychics_hourly_unique_counts()
    daily_unique = get_all_psychics_daily_unique_counts()
    daily_oncall = get_daily_oncall_counts()
    heatmap = get_oncall_online_ratio_heatmap()

    # Serialize chart data as JSON for Chart.js
    hourly_chart_data = json.dumps({
        "labels": [f"{h['hour']}:00" for h in hourly_unique],
        "online": [h["online"] for h in hourly_unique],
        "oncall": [h["oncall"] for h in hourly_unique],
    })
    daily_unique_chart_data = json.dumps({
        "labels": [str(d['day']) for d in daily_unique],
        "online": [d["online"] for d in daily_unique],
        "oncall": [d["oncall"] for d in daily_unique],
    })
    daily_chart_data = json.dumps({
        "labels": [d["date_short"] for d in daily_oncall],
        "oncall": [d["oncall"] for d in daily_oncall],
    })
    heatmap_data = json.dumps(heatmap)

    context = {
        **admin.site.each_context(request),
        "title": "SA Psychics",
        "psychics_current_month": psychics_current_month,
        "psychics_previous_month": psychics_previous_month,
        "psychics_two_months_ago": psychics_two_months_ago,
        "hourly_chart_data": hourly_chart_data,
        "daily_unique_chart_data": daily_unique_chart_data,
        "daily_chart_data": daily_chart_data,
        "heatmap_data": heatmap_data,
    }

    return TemplateResponse(
        request,
        "admin/sa_psychics.html",
        context,
    )


def psychic_detail_view(request, psychic_id):
    from main.models import Psychic
    psychic = Psychic.objects.get(id=psychic_id)

    stats = get_psychic_monthly_stats(psychic_id)
    hourly = get_psychic_hourly_activity_aggregates(psychic_id)
    sessions = get_psychic_sessions(psychic_id)

    context = {
        **admin.site.each_context(request),
        "title": f"Psychic: {psychic.name}",
        "psychic": psychic,
        "stats": stats,
        "hourly": hourly,
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
        path('psychic/<int:psychic_id>/', admin.site.admin_view(psychic_detail_view), name='psychic-detail'),
    ]
    return custom_urls + urls


admin.site.get_urls = get_urls
