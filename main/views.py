from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from main.constants import DISCOVERY_SUCCESS_MSG
from main.forms import DiscoveryForm, BookingForm
from main.models import Booking, STATUS_BOOKED
from phytolean import settings


def _get_ctx(params: dict = None) -> dict:
    ctx = {
        'schedule_enabled': settings.SCHEDULE_ENABLED,
    }
    if params:
        ctx.update(params)
    return ctx


def home_view(request):
    ctx = _get_ctx({
        'nav': 'home',
    })
    return render(request, 'main/home.html', ctx)


def about_view(request):
    ctx = _get_ctx({
        'nav': 'about',
    })
    return render(request, 'main/about.html', ctx)


def services_view(request):
    ctx = _get_ctx({
        'nav': 'services',
    })
    return render(request, 'main/services.html', ctx)


def howitworks_view(request):
    ctx = _get_ctx({
        'nav': 'howitworks',
    })
    return render(request, 'main/howitworks.html', ctx)


def for_you_view(request):
    ctx = _get_ctx({
        'nav': 'foryou',
    })
    return render(request, 'main/foryou.html', ctx)


def clients_view(request):
    ctx = _get_ctx({
        'nav': 'clients',
    })
    return render(request, 'main/clients.html', ctx)


def contact_view(request):
    ctx = _get_ctx({
        'nav': 'contact',
    })
    return render(request, 'main/contact.html', ctx)


def resources_index_view(request):
    ctx = _get_ctx({
        'nav': 'resources',
    })
    return render(request, 'main/resources.html', ctx)


def nutrition_essentials_view(request):
    ctx = _get_ctx({
        'nav': '',
    })
    return render(request, 'main/nutrition_essentials.html', ctx)


def resources_source_view(request, src):
    titles = {
        'bread': 'The Life-Changing Loaf of Bread',
        'breakfast': 'The Healing Breakfast',
        'grain': 'The Three Grain Super Cereal',
        'juicing': 'Why Juice?',
        'forksoverknives': 'Forks over Knives',
        'sexhormones': 'Nutrition and Sex Hormones',
        'diabetesthyroidmood': 'Nutrition for Diabetes, Thyroid Conditions and Mood Disorders',
    }
    if src not in titles:
        return redirect(reverse('resources_index'))
    ctx = _get_ctx({
        'nav': 'resources',
        'snippet': f'main/resources_snippets/{src}.html',
        'title': titles[src],
    })
    return render(request, 'main/resource.html', ctx)


######################################################################################

def discovery_view(request):
    if request.method == 'POST':
        form = DiscoveryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('discovery_submitted'))
    else:
        form = DiscoveryForm()
    ctx = _get_ctx({
        'nav': 'discovery',
        'form': form,
    })
    return render(request, 'main/discovery.html', ctx)


def discovery_submitted_view(request):
    ctx = _get_ctx({
        'msg': DISCOVERY_SUCCESS_MSG,
        'nav': 'discovery',
    })
    return render(request, 'main/discovery_submitted.html', ctx)


def make_booking_view(request, slug):
    booking = get_object_or_404(Booking, slug=slug)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.data.get('booking_slot'):
            form.save()
            return redirect(reverse('booking_submitted'))
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
    ctx = _get_ctx({
        'nav': 'faq',
    })
    return render(request, 'main/faq.html', ctx)
