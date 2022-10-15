import logging
from smtplib import SMTPException
from textwrap import dedent

from django.core.mail import send_mail, EmailMessage
from retry import retry

from main.models import Discovery, Booking
from phytolean import settings

logger = logging.getLogger(__name__)


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
    _send_gridhost_email(subject, message, [settings.DEFAULT_REPLY_EMAIL])
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
    _send_gridhost_email(subject, message, [f'{discovery.full_name()} <{discovery.email}>'])
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
    _send_gridhost_email(subject, message, [f'{discovery.full_name()} <{discovery.email}>'])
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
    _send_gridhost_email(subject, message, [settings.DEFAULT_REPLY_EMAIL])
    logger.info('Appointment email notified done')
