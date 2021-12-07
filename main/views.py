from django.shortcuts import render, redirect
from django.urls import reverse

from main.forms import BookingForm


def home_view(request):
    ctx = {
        'nav': 'home',
    }
    return render(request, 'main/home.html', ctx)


def about_view(request):
    ctx = {
        'nav': 'about',
    }
    return render(request, 'main/about.html', ctx)


def howitworks_view(request):
    ctx = {
        'nav': 'howitworks',
    }
    return render(request, 'main/howitworks.html', ctx)


def events_view(request):
    ctx = {
        'nav': 'events',
    }
    return render(request, 'main/events.html', ctx)


def clients_view(request):
    ctx = {
        'nav': 'clients',
    }
    return render(request, 'main/clients.html', ctx)


def resources_view(request):
    ctx = {
        'nav': 'resources',
    }
    return render(request, 'main/resources.html', ctx)


def contact_view(request):
    ctx = {
        'nav': 'contact',
    }
    return render(request, 'main/contact.html', ctx)


def booking_view(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booked')
    else:
        form = BookingForm()
    ctx = {
        'nav': 'booking',
        'form': form,
    }
    return render(request, 'main/booking.html', ctx)


def booked_view(request):
    ctx = {
        'nav': 'booking',
    }
    return render(request, 'main/booked.html', ctx)
