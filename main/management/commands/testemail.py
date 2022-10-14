from django.core.management import BaseCommand

from main.send_emails import send_hello_world


class Command(BaseCommand):
    help = 'Test email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        send_hello_world(options['email'])
