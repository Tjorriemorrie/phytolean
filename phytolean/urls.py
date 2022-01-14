"""phytolean URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
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
    path('what-we-do', views.what_we_do_view, name='whatwedo'),
    path('how-it-works', views.howitworks_view, name='howitworks'),
    path('transformative-works-courses-events', views.events_view, name='events'),
    path('happy-clients', views.clients_view, name='clients'),
    path('empowering-resources', views.resources_view, name='resources'),
    path('contact-us', views.contact_view, name='contact'),
]
