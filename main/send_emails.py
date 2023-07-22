import logging
from smtplib import SMTPException
from textwrap import dedent

import requests
from django.core.mail import send_mail, EmailMessage
from django.core.serializers import serialize
from retry import retry

from main.models import Discovery, Booking, Participant
from phytolean import settings

logger = logging.getLogger(__name__)


def _send_smtp2go_api_email(subject: str, message: str, to: list) -> dict:
    """Send email via smtp2go api."""
    payload = {
        'api_key': settings.EMAIL_API_KEY,
        'to': to,
        'sender': settings.DEFAULT_FROM_EMAIL,
        'subject': subject,
        'text_body': message,
        # 'html_body': '<h1>You're my favorite test person ever</h1>',
        'custom_headers': [
            {
                'header': 'Reply-To',
                'value': settings.DEFAULT_REPLY_EMAIL,
            }
        ],
        # 'attachments': [
        #     {
        # 'filename': 'test.pdf',
        # 'fileblob': '--base64-data--',
        # 'mimetype': 'application/pdf'
        # },
        # ]
    }
    logger.info(f'Email payload: {payload}')
    res = requests.post(
        f'{settings.EMAIL_API_URL}/email/send',
        json=payload
    )
    try:
        res.raise_for_status()
    except requests.HTTPError as exc:
        raise ValueError(f'{res.content}') from exc
    data = res.json()
    logger.info(f'Response: {data}')
    return data


def _send_gridhost_email(subject: str, message: str, to: list) -> int:
    email = EmailMessage(
        subject,
        message,
        to=to,
        reply_to=[settings.DEFAULT_REPLY_EMAIL])
    return email.send()


@retry(SMTPException)
def send_new_discovery_email(discovery: Discovery):
    logger.info('Sending new discovery email...')
    prev = Discovery.objects.last()
    next_pk = prev.pk + 1 if prev else 1
    subject = f'{discovery.first_name} {discovery.last_name} requested a discovery session'
    message = dedent(f"""
        A discovery session was requested!

        Please change status of form to approved or denied (if spam).
        It is at the bottom of the form in the admin page.

        https://phytolean.co.za/admin/main/discovery/{next_pk}/change/

        If approved they will receive an email to make their booking.
    """)
    _send_smtp2go_api_email(subject, message, settings.DEFAULT_TO_EMAILS)
    logger.info('New discovery email done.')


@retry(SMTPException)
def send_booking_email(discovery: Discovery, booking: Booking):
    logger.info('Sending booking email...')
    subject = 'Phytolean discovery session booking'
    message = dedent(f"""
        Hi {discovery.first_name},

        Thank you for your interest.
        Make your booking at
        https://phytolean.co.za/make-booking/{booking.slug}

        Regards,
        Phytolean
    """)
    _send_smtp2go_api_email(subject, message, [f'{discovery.full_name()} <{discovery.email}>'])
    logger.info('Booking email sent.')


@retry(SMTPException)
def send_appointment_email(discovery: Discovery, booking: Booking):
    logger.info('Sending appointment email...')
    subject = 'Phytolean discovery session booked'
    message = dedent(f"""
        Hi {discovery.first_name},

        Thank you for your interest.
        Your booking has been confirmed for {booking.start_at:'%a %-d %b at %H:%I'}.

        Regards,
        Phytolean
    """)
    _send_smtp2go_api_email(subject, message, [f'{discovery.full_name()} <{discovery.email}>'])
    logger.info('Appointment email done')


@retry(SMTPException)
def send_appointment_email_notification(discovery: Discovery, booking: Booking):
    logger.info('Sending appointment notification...')
    subject = f'Phytolean discovery session booked'
    message = dedent(f"""
        New discovery session booked!
        
        For {discovery.full_name()}
        at {booking.start_at:'%a %-d %b at %H:%I'}.
    """)
    _send_smtp2go_api_email(subject, message, settings.DEFAULT_TO_EMAILS)
    logger.info('Appointment email notified done')


@retry(SMTPException)
def send_participant_email(participant: Participant):
    logger.info('Sending participant notification...')
    subject = f'Phytolean participant application'
    data = serialize("json", [participant])
    message = dedent(f"""
        New participant
        
        Event: {participant.event}
        Name: {participant.prefix} {participant.first_name} {participant.last_name}
        Cellphone: {participant.cellphone}
        Email: {participant.email}
        City: {participant.city}
        Date of birth: {participant.dob}
        Sex: {participant.sex}
        Ethnicity: {participant.ethnicity}
        Cancer: {participant.cancer}
        Diseases: {participant.diseases}
        Origin: {participant.origin}
        Occupation: {participant.occupation}
        Practitioner: {participant.practitioner}
        Diet: {participant.diet}
        Intention: {participant.diet}
        Expectation: {participant.expectation}
    """)
    _send_smtp2go_api_email(subject, message, settings.DEFAULT_TO_EMAILS)
    logger.info('Participant email notified done')
