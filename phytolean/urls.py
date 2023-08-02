"""phytolean URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home_snippets, name='home_snippets')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home_snippets')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from main import views
from main.admin import admin_site_urls

urlpatterns = [
    path('admin/', admin_site_urls),
    path('', views.home_view, name='home'),

    path('captcha/', include('captcha.urls')),

    path('book-discovery-session', views.discovery_view, name='discovery'),
    path('discovery-session-submitted', views.discovery_submitted_view, name='discovery_submitted'),
    path('make-booking/<slug:slug>', views.make_booking_view, name='booking'),
    path('booking-submitted', views.booking_submitted_view, name='booking_submitted'),

    path('about', views.about_view, name='about'),
    path('services', views.services_view, name='services'),
    path('how-it-works', views.howitworks_view, name='howitworks'),
    path('why-this-is-for-you', views.for_you_view, name='foryou'),
    path('happy-clients', views.clients_view, name='clients'),
    path('faq', views.faq_view, name='faq'),
    path('contact-us', views.contact_view, name='getintouch'),
    path('resources', views.resources_index_view, name='resources_index'),
    path('resources/<str:src>', views.resources_source_view, name='resources_source'),

    path('events', views.events_view, name='events'),
    path('event/2023/03/nutrional-essentails', views.event_202303_view, name='event_202303'),
    path('event/2023/03/nutrional-essentails/apply', views.event_202303_form, name='event_202303_form'),
    path('event/2023/03/nutrional-essentails/success', views.event_202303_success, name='event_202303_success'),
    path('event/2023/03/nutrional-essentails/survey', views.event_202303_survey, name='event_202303_survey'),
    path('event/2023/03/nutrional-essentails/thankyou', views.event_202303_thanks, name='event_202303_thankyou'),

    path('events/nutrionclasses', views.event_202306_view, name='event_202306'),
    path('event/2023/06/poppe-spel', views.event_202306_poppe_view, name='event_202306_poppe'),
    path('event/2023/06/puppet-show', views.event_202306_puppet_view, name='event_202306_puppet'),
    path('event/2023/06/09/kos-teater', views.event_20230609_poppe_view, name='event_20230609_poppe'),
    path('event/2023/06/12/kos-teater', views.event_20230612_poppe_view, name='event_20230612_poppe'),
    path('event/2023/07/25/kos-teater/shalom', views.event_20230725_shalom_view, name='event_20230725_shalom'),
    path('event/2023/06/', views.event_202306_puppet_view, name='event_202306_puppet'),

    # path('event/2023/07/15/kos-teater', views.event_20230715_poppe_view, name='event_20230715_sda'),
    path('event/2023/08/19/fitness', views.event_20230819_fitness_view, name='event_20230819_fitness'),
]
