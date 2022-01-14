from unittest.mock import patch

from django.test import TestCase, Client, override_settings

from main.models import Discovery


# @override_settings(CAPTCHA_TEST_MODE=True)
class BookingTest(TestCase):

    def test_booking_view(self):
        data = {
            'captcha': 'passed',
            'captcha_0': 'passed',
            'captcha_1': 'passed',

            'source': 'srcy',
            'first_name': 'firsty',
            'last_name': 'lasty',
            'email': 'emaily',
            'cell': 'celly',
            'age': 12,
            'reason': 'reasony',
            'timing': 'timingy',

            'crn_skin_health': False,
            'crn_digestive_health': False,
            'crn_stress': False,
            'crn_sleep': False,
            'crn_pain': False,
            'crn_fertility': False,
            'crn_child': False,
            'crn_sport': False,
            'crn_safe': False,
            'crn_diet': False,
            'crn_weight': False,
            'crn_eating': False,
            'crn_detox': False,
            'crn_allergy': False,
            'crn_longevity': False,
            'crn_nutrition': False,
            'crn_lifestyle': False,

            'association': 'assocy',
            'expectation': 'expecty',
            'driver': 'drivey',
            'elaboration': 'elaby',
            'duration': 'dury',
            'expansion': 'expansy',
            'priorities': 'prio',
            'struggles': 'struggly',

            'chl_emotion': False,
            'chl_planning': False,
            'chl_crave': False,
            'chl_snack': False,
            'chl_quick': False,
            'chl_sweet': False,
            'chl_out': False,
            'chl_large': False,
            'chl_time': False,
            'chl_alcohol': False,
            'chl_unsure': False,
            'chl_dislike': False,
            'chl_pressure': False,
            'chl_help': False,

            'committed': 'comy',
            'investment': True,
            'punctual': True,
        }
        client = Client()
        res = client.post(
            '/book-discovery-session',
            data=data,
            follow=True
        )
        booking = Discovery.objects.last()
        assert 'Discovery received!' in str(res.content)
        assert booking.association == 'assocy'

    def test_booking_view_required(self):
        data = {
            'source': 'srcy',
            'first_name': 'firsty',
            'last_name': 'lasty',
        }
        client = Client()
        res = client.post(
            '/book-discovery-session',
            data=data
        )
        assert 'required' in str(res.content)
