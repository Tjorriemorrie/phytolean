from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

import main.constants as c
from main.forms import DiscoveryForm, BookingForm, ParticipantBookingForm, SurveyForm
from main.models import Booking
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


def events_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events.html', ctx)


def event_202303_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202303-nutrition-essentials.html', ctx)


def event_202303_form(request):
    if request.method == 'POST':
        form = ParticipantBookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('event_202303_success'))
    else:
        form = ParticipantBookingForm()
    ctx = _get_ctx({
        'nav': 'events',
        'form': form,
    })
    return render(request, 'main/events/202303-nutrition-essentials-form.html', ctx)


def event_202303_success(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202303-nutrition-essentials-success.html', ctx)


def event_202303_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('event_202303_thankyou'))
    else:
        form = SurveyForm()
    ctx = _get_ctx({
        'nav': 'events',
        'form': form,
    })
    return render(request, 'main/events/202303-nutrition-essentials-feedback.html', ctx)


def event_202303_thanks(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202303-nutrition-essentials-thanks.html', ctx)


def event_202306_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202306-kickstart.html', ctx)


def event_202306_poppe_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202306-poppe.html', ctx)


def event_202306_puppet_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202306-puppet.html', ctx)


def event_20230609_poppe_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230609-agape.html', ctx)


def event_20230612_poppe_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230612-ghs.html', ctx)


def event_20230616_poppe_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230616-market.html', ctx)


def event_20230715_poppe_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230715-sda.html', ctx)


def event_20230819_fitness_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230819-fitness.html', ctx)


def resources_source_view(request, src):
    titles = {
        'bread': 'The Life-Changing Loaf of Bread',
        'breakfast': 'The Healing Breakfast',
        'grain': 'The Three Grain Super Cereal',
        'juicing': 'Why Juice?',
        'forksoverknives': 'Forks over Knives',
        'sexhormones': 'Nutrition and Sex Hormones',
        'diabetesthyroidmood': 'Nutrition for Diabetes, Thyroid Conditions and Mood Disorders',
        'brocollisoup': 'Cream of Broccoli Soup',
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
        'msg': c.DISCOVERY_SUCCESS_MSG,
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
