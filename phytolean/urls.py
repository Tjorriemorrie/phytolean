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
from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
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
]
