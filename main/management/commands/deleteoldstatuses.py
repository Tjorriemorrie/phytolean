import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from main.models import Status

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Delete all Status records older than 3 months'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show how many records would be deleted without actually deleting them',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=90)

        old_statuses = Status.objects.filter(created_at__lt=cutoff_date)
        count = old_statuses.count()

        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'[DRY RUN] Would delete {count} Status records older than {cutoff_date}')
            )
        else:
            deleted, _ = old_statuses.delete()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully deleted {deleted} Status records older than {cutoff_date}')
            )
            logger.info(f'Deleted {deleted} Status records older than 3 months')
