import logging
from random import randint
from typing import Type

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from main.models import Discovery, STATUS_APPROVED, STATUS_NEW, Booking, STATUS_BOOKED
from main.send_emails import send_new_discovery_email, send_booking_email, \
    send_appointment_email, send_appointment_email_notification

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Discovery)
def discovery_email_hook(sender: Type[Discovery], instance: Discovery, **kwargs):
    if instance.status == STATUS_NEW and not instance.has_sent_new_email:
        send_new_discovery_email(instance)
        instance.has_sent_new_email = True
    elif instance.status == STATUS_APPROVED and not instance.has_sent_booking_email:
        booking = Booking.objects.create(discovery=instance)
        send_booking_email(instance, booking)
        instance.has_sent_booking_email = True
    elif instance.status == STATUS_BOOKED and not instance.has_sent_appointment_email:
        booking = instance.bookings.last()
        send_appointment_email(instance, booking)
        send_appointment_email_notification(instance, booking)
        instance.has_sent_appointment_email = True
