from django.shortcuts import render, redirect, get_object_or_404

from main.forms import DiscoveryForm, BookingForm
from main.models import Booking, STATUS_BOOKED


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


def what_we_do_view(request):
    ctx = {
        'nav': 'whatwedo',
    }
    return render(request, 'main/whatwedo.html', ctx)


def howitworks_view(request):
    ctx = {
        'nav': 'howitworks',
    }
    return render(request, 'main/howitworks.html', ctx)


def for_you_view(request):
    ctx = {
        'nav': 'foryou',
    }
    return render(request, 'main/foryou.html', ctx)


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


def discovery_view(request):
    if request.method == 'POST':
        form = DiscoveryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('discovery_submitted')
    else:
        form = DiscoveryForm()
    ctx = {
        'nav': 'discovery',
        'form': form,
    }
    return render(request, 'main/discovery.html', ctx)


def discovery_submitted_view(request):
    ctx = {
        'nav': 'discovery',
    }
    return render(request, 'main/discovery_submitted.html', ctx)


def make_booking_view(request, slug):
    booking = get_object_or_404(Booking, slug=slug)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            booking.status = STATUS_BOOKED
            booking.save()
            booking.discovery.status = STATUS_BOOKED
            booking.discovery.save()
            return redirect('booking_submitted')
    else:
        form = BookingForm()
    ctx = {
        'nav': 'discovery',
        'form': form,
    }
    return render(request, 'main/booking.html', ctx)


def booking_submitted_view(request):
    ctx = {
        'nav': 'discovery',
    }
    return render(request, 'main/booking_submitted.html', ctx)


def faq_view(request):
    ctx = {
        'nav': 'faq',
    }
    return render(request, 'main/faq.html', ctx)
