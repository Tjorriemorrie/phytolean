from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from import_export.admin import ImportExportModelAdmin, ExportActionMixin
from import_export.resources import ModelResource
from plotly.offline import plot

from main.models import Discovery, Booking, Survey, Psychic, Status, Role
from main.selectors import list_psychics_with_status_monthly, generate_status_hourly_plot, \
    get_last_scrape_date


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


def sa_psychics(request):
    last_status_at = get_last_scrape_date()
    psychics_monthly = list_psychics_with_status_monthly()
    # status_plot = generate_status_hourly_plot()
    context = {
        **admin.site.each_context(request),
        'title': 'SA Psycics',
        'last_status_at': last_status_at,
        'psychics_monthly': psychics_monthly,
        # 'status_plot_html': plot(status_plot, output_type='div', include_plotlyjs=False),
    }
    return TemplateResponse(request, "admin/sa_psychics.html", context)


original_get_urls = admin.site.get_urls


def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('sa-psychics/', admin.site.admin_view(sa_psychics), name='sa-psychics'),
    ]
    return custom_urls + urls


admin.site.get_urls = get_urls
