import logging

import requests
from django.core.management import BaseCommand

from main.send_emails import _send_smtp2go_api_email
from phytolean import settings

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send test api email'

    # def add_arguments(self, parser):
    #     parser.add_argument('shop_name', nargs='+', type=str)
    #     parser.add_argument('--fail_fast', action='store_true')

    def handle(self, *args, **options):
        logger.info('testing smtp2go api email')
        res = _send_smtp2go_api_email(
            'test subject',
            'test message',
            ['Me <jacoj82@gmail.com>']
        )
        logger.info('finished testing smtp2go api email')
