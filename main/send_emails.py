import logging
from textwrap import dedent

from django.core.mail import send_mail

from main.models import Discovery, Booking
from phytolean import settings

logger = logging.getLogger(__name__)


def send_new_discovery_email(discovery: Discovery):
    logger.info('Sending new discovery email...')
    subject = f'{discovery.first_name} {discovery.last_name} requested a discovery session'
    message = dedent(f"""
        A discovery session was requested!
        
        Please change status of form to approved or denied (if spam).
        It is at the bottom of the form in the admin page.
        
        https://phytolean.co.za/admin/main/discovery/{discovery.id}/change/

        If approved they will receive an email to make their booking.
    """)
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=not settings.DEBUG,
    )
    logger.info('New discovery email sent.')


def send_booking_email(discovery: Discovery, booking: Booking):
    logger.info('Sending booking email...')
    subject = f'Phytolean discovery session booking'
    message = dedent(f"""
        Hi {discovery.first_name},

        Thank you for your interest.
        Make your booking at
        https://phytolean.co.za/make-booking/{booking.slug}

        Regards,
        Phytolean
    """)
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=not settings.DEBUG,
    )
    logger.info('Booking email sent.')


def send_appointment_email(discovery: Discovery, booking: Booking):
    logger.info('Sending appointment email...')
    subject = f'Phytolean discovery session booked'
    message = dedent(f"""
        Hi {discovery.first_name},

        Thank you for your interest.
        Your booking has been confirmed for {booking.start_at:'%a %-d %b at %H:%I'}.

        Regards,
        Phytolean
    """)
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=not settings.DEBUG,
    )
    logger.info('Appointment email sent.')


def send_appointment_email_notification(discovery: Discovery, booking: Booking):
    logger.info('Sending appointment notification...')
    subject = f'Phytolean discovery session booked'
    message = dedent(f"""
        New discovery session booked!
        
        For {discovery.first_name} {discovery.last_name}
        at {booking.start_at:'%a %-d %b at %H:%I'}.
    """)
    send_mail(
        subject,
        message,
        settings.EMAIL_FROM,
        settings.EMAIL_TO,
        fail_silently=not settings.DEBUG,
    )
    logger.info('Appointment email notified.')
