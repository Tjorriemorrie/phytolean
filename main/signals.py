import logging
from typing import Type

from django.db import transaction
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

import main.constants as c
from main.models import Discovery, Booking, Participant, Status
from main.send_emails import send_new_discovery_email, send_booking_email, \
    send_appointment_email, send_appointment_email_notification, send_participant_email

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Discovery)
def discovery_email_hook(sender: Type[Discovery], instance: Discovery, **kwargs):
    if instance.status == c.STATUS_NEW and not instance.has_sent_new_email:
        send_new_discovery_email(instance)
        instance.has_sent_new_email = True
    elif instance.status == c.STATUS_APPROVED and not instance.has_sent_booking_email:
        booking = Booking.objects.create(discovery=instance)
        send_booking_email(instance, booking)
        instance.has_sent_booking_email = True
    elif instance.status == c.STATUS_BOOKED and not instance.has_sent_appointment_email:
        booking = instance.bookings.last()
        send_appointment_email(instance, booking)
        send_appointment_email_notification(instance, booking)
        instance.has_sent_appointment_email = True


@receiver(pre_save, sender=Participant)
def participant_email_hook(sender: Type[Participant], instance: Participant, **kwargs):
        send_participant_email(instance)


@receiver(pre_save, sender=Status)
def set_prev_allowed(sender, instance: Status, **kwargs):
    """
    Populate `prev_allowed` before saving a Status row.
    - True if the immediate previous row for the same psychic
      has status in [ONLINE, ONCALL].
    """
    if instance.pk:  # updating existing row → leave prev_allowed as is
        return

    # Find the immediate previous row
    prev = (
        Status.objects
        .filter(psychic=instance.psychic, status_at__lt=instance.status_at)
        .order_by('-status_at')
        .first()
    )

    instance.prev_allowed = bool(
        prev and prev.status in (c.PSYCHIC_STATUS_ONCALL, c.PSYCHIC_STATUS_ONLINE)
    )


@receiver(post_save, sender=Status)
def update_next_row(sender, instance: Status, created, **kwargs):
    """
    After inserting a row, the next chronological row (if any)
    might need its prev_allowed recomputed.
    """
    if not created:
        return

    def _update_next():
        next_row = (
            Status.objects
            .filter(psychic=instance.psychic, status_at__gt=instance.status_at)
            .order_by('status_at')
            .first()
        )
        if next_row:
            allowed = instance.status in (c.PSYCHIC_STATUS_ONCALL, c.PSYCHIC_STATUS_ONLINE)
            if next_row.prev_allowed != allowed:
                next_row.prev_allowed = allowed
                next_row.save(update_fields=['prev_allowed'])

    # Run after the transaction commits (safe for bulk inserts too)
    transaction.on_commit(_update_next)
