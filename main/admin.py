import requests
from bs4 import BeautifulSoup
from django.contrib import admin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from requests import Response

from main.models import Discovery, Booking, Survey


@admin.register(Discovery)
class DiscoveryAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'first_name', 'last_name', 'email', 'cell', 'created_at']
    ordering = ['status', '-created_at']


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'start_at', 'slug', 'created_at', 'discovery']
    ordering = ['-start_at']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'name']
    ordering = ['-created_at']


#########################################################################################
# SA Psychics
#########################################################################################

class PsychicsView(View):
    # template_name = 'admin/main/psychics/psychics.html'

    # def get_context_data(self, **kwargs):
    #     kwargs = super().get_context_data(**kwargs)
    #     kwargs['cookie'] = self.request.META.get('HTTP_COOKIE')
    #     return kwargs

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'admin/main/psychics/psychics.html')

    def post(self, request, *args, **kwargs):
        res = requests.get('https://www.sa-psychics.com/GetBusiness/SEAH')
        try:
            res.raise_for_status()
        except Exception as exc:
            status = res.text
        else:
            html = BeautifulSoup(res.text, 'html.parser')
            status = html.find('span', id='status').text.strip()
        return HttpResponse(f'<p>{now():%H:%M} {status.title()}</p>')


admin_site_urls = admin.site.urls
admin_site_urls[0].insert(7, path('psychics/', PsychicsView.as_view(), name='psychics_view'))