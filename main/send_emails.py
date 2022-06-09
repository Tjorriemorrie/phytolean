import logging
from textwrap import dedent

from mailjet_rest import Client

from main.models import Discovery, Booking
from phytolean.settings import MAILJET_API_KEY, MAILJET_API_SECRET, DEBUG

logger = logging.getLogger(__name__)


class EmailError(Exception):
    """Base email error."""


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
    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'phytolean@gmail.com',
                    'Name': 'Phytolean'
                },
                'To': [
                    {
                        'Email': 'phytolean@gmail.com',
                        'Name': 'Phytolean'
                    }
                ],
                'Subject': subject,
                'TextPart': message,
                'CustomID': 'NewDiscoveryEmail',
            }
        ]
    }
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    res = mailjet.send.create(data=data)
    if res.status_code != 200:
        res_data = res.json()
        logger.error(f'Could not send email: {res_data}')
        if DEBUG:
            raise EmailError(res_data)
    logger.info('New discovery email done.')


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
    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'phytolean@gmail.com',
                    'Name': 'Phytolean'
                },
                'To': [
                    {
                        'Email': discovery.email,
                        'Name': discovery.full_name(),
                    }
                ],
                'Reply-To': 'phytolean@gmail.com',
                'Subject': subject,
                'TextPart': message,
                'CustomID': 'SendBookingEmail',
            }
        ]
    }
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    res = mailjet.send.create(data=data)
    if res.status_code != 200:
        res_data = res.json()
        logger.error(f'Could not send email: {res_data}')
        if DEBUG:
            raise EmailError(res_data)
    logger.info('Booking email sent.')


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
    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'phytolean@gmail.com',
                    'Name': 'Phytolean'
                },
                'To': [
                    {
                        'Email': discovery.email,
                        'Name': discovery.full_name(),
                    }
                ],
                'Reply-To': 'phytolean@gmail.com',
                'Subject': subject,
                'TextPart': message,
                'CustomID': 'SendAppointmentEmail',
            }
        ]
    }
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    res = mailjet.send.create(data=data)
    if res.status_code != 200:
        res_data = res.json()
        logger.error(f'Could not send email: {res_data}')
        if DEBUG:
            raise EmailError(res_data)
    logger.info('Appointment email done')


def send_appointment_email_notification(discovery: Discovery, booking: Booking):
    logger.info('Sending appointment notification...')
    subject = f'Phytolean discovery session booked'
    message = dedent(f"""
        New discovery session booked!
        
        For {discovery.full_name()}
        at {booking.start_at:'%a %-d %b at %H:%I'}.
    """)
    data = {
        'Messages': [
            {
                'From': {
                    'Email': 'phytolean@gmail.com',
                    'Name': 'Phytolean'
                },
                'To': [
                    {
                        'Email': 'phytolean@gmail.com',
                        'Name': 'Phytolean',
                    }
                ],
                'Reply-To': 'phytolean@gmail.com',
                'Subject': subject,
                'TextPart': message,
                'CustomID': 'SendNotificationEmail',
            }
        ]
    }
    mailjet = Client(auth=(MAILJET_API_KEY, MAILJET_API_SECRET), version='v3.1')
    res = mailjet.send.create(data=data)
    if res.status_code != 200:
        res_data = res.json()
        logger.error(f'Could not send email: {res_data}')
        if DEBUG:
            raise EmailError(res_data)
    logger.info('Appointment email notified done')
