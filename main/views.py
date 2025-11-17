import logging
from decimal import Decimal

import requests
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import main.constants as c
from main.forms import DiscoveryForm, BookingForm, ParticipantBookingForm, SurveyForm, SignupForm
from main.models import Booking, PayFastTransaction
from phytolean import settings

logger = logging.getLogger(__name__)


def home(request):
    bookings = Booking.objects.all()

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


def event_20230725_shalom_view(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/20230725-shalom.html', ctx)


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


def event_202312_fitness_survey(request):
    if request.method == 'POST':
        form = SurveyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('event_202312_fitness_thankyou'))
    else:
        form = SurveyForm()
    ctx = _get_ctx({
        'nav': 'events',
        'form': form,
    })
    return render(request, 'main/events/202312-fitness-feedback.html', ctx)


def event_202312_fitness_thanks(request):
    ctx = _get_ctx({
        'nav': 'events',
    })
    return render(request, 'main/events/202312-fitness-thanks.html', ctx)


def event_20251209_fitness_view(request):
    form = SignupForm()

    ctx = _get_ctx({
        'nav': 'events',
        'process_url': settings.PAYFAST_PROCESS_URL,
        'merchant_id': settings.PAYFAST_MERCHANT_ID,
        'merchant_key': settings.PAYFAST_MERCHANT_KEY,
        'return_url': request.build_absolute_uri('/payment/success/'),
        'cancel_url': request.build_absolute_uri('/payment/cancel/'),
        'notify_url': request.build_absolute_uri('/payment/notify/'),
        'form': form,
    })

    return render(request, 'main/events/20251209-fitness.html', ctx)


def signup_submit(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            # ✔️ render a NEW HTML page with a message
            return render(request, "main/events/signup.html", {
                "name": form.cleaned_data["name"],
                "email": form.cleaned_data["email"],
            })
        else:
            # ❗ invalid form → re-render form with errors
            return redirect(reverse('event_20251209_fitness'))


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


def one_time_event_view(request):
    logger.info('One time event viewed.')
    ctx = {
        'process_url': settings.PAYFAST_PROCESS_URL,
        'merchant_id': settings.PAYFAST_MERCHANT_ID,
        'merchant_key': settings.PAYFAST_MERCHANT_KEY,
        'return_url': request.build_absolute_uri('/payment/success/'),
        'cancel_url': request.build_absolute_uri('/payment/cancel/'),
        'notify_url': request.build_absolute_uri('/payment/notify/'),
    }
    return render(request, 'main/one_time_event.html', ctx)


def payment_success(request):
    logger.info('Payment success.')
    # Set a flash message
    messages.warning(request, "Your payment was successful.")
    # Redirect back to the one-time event page
    return redirect('event_20251209_fitness')


def payment_cancel(request):
    logger.info('Payment cancelled.')
    # Set a flash message
    messages.warning(request, "Your transaction was cancelled.")
    # Redirect back to the one-time event page
    return redirect('one_time_event')


@csrf_exempt
def payment_notify(request):
    if request.method == "POST":
        # Step 1: Read POST data
        data = request.POST.dict()

        # Step 2: OPTIONAL: verify the data with PayFast
        logger.info('Verifying payment...')
        verify_url = settings.PAYFAST_VALIDATE_URL
        try:
            response = requests.post(verify_url, data=data, timeout=10)
            if response.text != "VALID":
                logger.info('Payment invalid.')
                return HttpResponse("INVALID", status=400)
        except requests.RequestException:
            logger.exception('Payment failed.')
            return HttpResponse("ERROR", status=500)

        # Step 3: Save to database
        PayFastTransaction.objects.create(
            m_payment_id=data.get("m_payment_id") or None,
            pf_payment_id=data.get("pf_payment_id") or None,
            item_name=data.get("item_name") or "",
            item_description=data.get("item_description") or "",
            amount_gross=Decimal(data.get("amount_gross", "0")),
            amount_fee=Decimal(data.get("amount_fee", "0")),
            amount_net=Decimal(data.get("amount_net", "0")),
            payment_status=data.get("payment_status") or "",
            name_first=data.get("name_first") or None,
            name_last=data.get("name_last") or None,
            email_address=data.get("email_address") or None,
            merchant_id=data.get("merchant_id") or None,
            signature=data.get("signature") or None,
            user_email=data.get("custom_str1") or None,
        )

        # Step 4: Respond with 200 OK
        logger.info('Payment success.')
        return HttpResponse("OK")

    return HttpResponse("Method not allowed", status=405)
