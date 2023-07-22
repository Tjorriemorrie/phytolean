from copy import copy
from datetime import timedelta, datetime
from random import randint
from typing import List, Tuple, Dict, Union

from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Div, HTML
from crispy_forms.utils import TEMPLATE_PACK
from django import forms
from django.utils.timezone import now

import main.constants as c
from main.constants import FFL_DISCLAIMER
from main.models import Discovery, Booking, Participant, Survey

BOOK_DAYS_AHEAD = 4


class DateInput(forms.DateInput):
    input_type = 'date'


class DiscoveryForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Discovery
        fields = '__all__'
        exclude = [
            'status', 'has_sent_new_email', 'has_sent_booking_email',
            'created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'discoveryForm'
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        self.helper.layout = Layout(
            Fieldset(
                'Personal details',
                Field('source'),
                Field('first_name'),
                Field('last_name'),
                Field('age'),
                Field('sex'),
                Field('email'),
                Field('cell'),
                Field('reason'),
                Field('timing'),
            ),
            Fieldset(
                'Which of these are areas of concern for you?',
                Div(
                    Div(
                        Field('crn_skin_health'),
                        Field('crn_digestive_health'),
                        Field('crn_stress'),
                        Field('crn_sleep'),
                        Field('crn_pain'),
                        Field('crn_fertility'),
                        Field('crn_child'),
                        Field('crn_sport'),
                        Field('crn_safe'),
                        css_class='col'
                    ),
                    Div(
                        Field('crn_diet'),
                        Field('crn_weight'),
                        Field('crn_eating'),
                        Field('crn_detox'),
                        Field('crn_allergy'),
                        Field('crn_longevity'),
                        Field('crn_nutrition'),
                        Field('crn_lifestyle'),
                        css_class='col'
                    ),
                    css_class='row'
                ),
                Field('crn_other'),
            ),
            Fieldset(
                'Tell us more about you',
                Field('association'),
                Field('expectation'),
                Field('driver'),
                Field('elaboration'),
                Field('diagnosis'),
                Field('medications'),
                Field('vaccinations'),
                Field('duration'),
                Field('expansion'),
                Field('priorities'),
                Field('struggles'),
            ),
            Fieldset(
                'What is your biggest nutritional challenges?',
                Div(
                    Div(
                        Field('chl_emotion'),
                        Field('chl_planning'),
                        Field('chl_crave'),
                        Field('chl_snack'),
                        Field('chl_quick'),
                        Field('chl_sweet'),
                        Field('chl_out'),
                        css_class='col'
                    ),
                    Div(
                        Field('chl_large'),
                        Field('chl_time'),
                        Field('chl_alcohol'),
                        Field('chl_unsure'),
                        Field('chl_dislike'),
                        Field('chl_pressure'),
                        Field('chl_help'),
                        css_class='col'
                    ),
                    css_class='row'
                ),
                Field('chl_other'),
            ),
            Fieldset(
                'Confirmation of your dedication',
                Field('committed'),
                Field('investment'),
                Field('punctual'),
            ),
            Field('captcha'),
            HTML('<br/><p style="color: var(--clr-phytolean)"><strong>All information will be kept confidential.</strong></p>'),
        )

        self.helper.add_input(Submit('submit', 'Submit'))


class BookingField(Field):
    template = 'main/crispy/booking.html'

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if extra_context is None:
            extra_context = {}
        if hasattr(self, "wrapper_class"):
            extra_context["wrapper_class"] = self.wrapper_class

        days, slots = get_booking_data()
        extra_context['days'] = days
        extra_context['slots'] = slots

        template = self.get_template_name(template_pack)

        return self.get_rendered_fields(
            form,
            form_style,
            context,
            template_pack,
            template=template,
            attrs=self.attrs,
            extra_context=extra_context,
            **kwargs,
        )


def get_booking_data() -> Tuple[List[datetime], List[List[Dict[str, Union[bool, datetime]]]]]:
    # for next 7 days
    weekday_nums = [0, 1, 2, 3]
    hour_nums = [12, 13, 14, 15]

    # create headers (days)
    pointer = now()
    days = []
    while len(days) < BOOK_DAYS_AHEAD:
        # move day forward
        pointer += timedelta(days=1)
        if pointer.weekday() not in weekday_nums:
            continue
        days.append(copy(pointer))

    # check time slots for each day/header
    slots = []
    for hour_num in hour_nums:
        # check each slot for day
        row = []
        for day in days:
            slot_dt = day.replace(hour=hour_num, minute=0, second=0, microsecond=0)
            existing_booking = Booking.objects.filter(start_at=slot_dt).first()
            row.append({
                'slot': slot_dt,
                'is_valid': not existing_booking,
            })
        slots.append(row)

    return _make_it_busy(days, slots)


def _make_it_busy(days, slots):
    valid_cnt = sum([i['is_valid'] for r in slots for i in r])
    if valid_cnt <= 14:
        return days, slots
    for _ in range(2):
        slot = slots[randint(0, 3)][randint(0, 3)]
        Booking.objects.create(
            start_at=slot['slot'],
            end_at=slot['slot'] + timedelta(minutes=5),
            duration=5,
            status=c.STATUS_INVALID)
    return get_booking_data()


def get_booking_values():
    days, slots = get_booking_data()
    values = [str(int(i['slot'].timestamp())) for r in slots for i in r]
    return values


class BookingForm(forms.ModelForm):
    booking_slot = forms.ChoiceField(
        choices=[],
        widget=forms.RadioSelect,
        required=True)
    
    class Meta:
        model = Booking
        fields = ['booking_slot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_slot'].choices = get_booking_values()
        self.helper = FormHelper()
        self.helper.form_id = 'bookingForm'
        self.helper.layout = Layout(
            BookingField('booking_slot')
        )
        self.helper.add_input(Submit('submit', 'Submit'))

    def save(self, commit=True):
        """Set start at from form."""
        self.instance.start_at = datetime.fromtimestamp(int(self.data['booking_slot']))
        self.instance.status = c.STATUS_BOOKED
        self.instance.save()

        self.instance.discovery.status = c.STATUS_BOOKED
        self.instance.discovery.save()


class ParticipantBookingForm(forms.ModelForm):
    dob = forms.DateField(label='Date of Birth', widget=DateInput)
    info = forms.CharField(
        label='', initial=FFL_DISCLAIMER, widget=forms.Textarea(
            attrs={'readonly': 'readonly', 'class': 'small-textarea'}))
    waiver = forms.BooleanField(required=True, label='I have read the disclaimer')

    class Meta:
        model = Participant
        exclude = ['event', 'submitted_at']
        labels = {
            'prefix': 'Prefix (Mr, Mrs, Dr, etc):',
            'first_name': 'First name:',
            'last_name': 'Last name:',
            'cellphone': 'Cellphone number:',
            'email': 'Email address:',
            'city': 'In which city do you live?',
            'cancer': 'Are you a cancer survivor?',
            'diseases': 'Any diseases or conditions we should be aware of?',

            'origin': 'Where did you learn about this class series? (If you were referred by someone please mention their name)',
            'occupation': 'What is your occupation or profession?',
            'practitioner': 'Are you a healthcare practitioner?',
            'diet': 'Are you a proponent or supporter of a specific diet currently? Or are you adhering currently to a specific diet? e.g. paleo, banting, keto, carnivore, vegetarian, vegan or gluten free?',
            'intention': 'What is your intention for attending the class?',
            'expectation': 'What is your expectation regarding the class series?',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'participantForm'
        # self.helper.layout = Layout(
        #     BookingField('booking_slot')
        # )
        self.helper.add_input(Submit('submit', 'Submit'))

    def save(self, commit=True):
        """Set start at from form."""
        self.instance.event = 'Nutrition Essentials'
        self.instance.submitted_at = now()
        self.instance.save()


class SurveyForm(forms.ModelForm):

    class Meta:
        model = Survey
        exclude = ['country', 'instructor']
        labels = {
            'name': 'Your name',
            'email': 'Your email address',
            'age': 'Your age',
            'sex': 'Your sex',
            'ethnicity': 'Your ethnicity',
            'num_classes': 'How many classes have you attended?',
            'experience': 'How was the class experience?',
            'quality': 'How was the quality of the information shared?',
            'meat': 'Do you eat meat?',
            'diary': 'Do you eat eggs or dairy?',
            'changes': 'What changes will you make because of this class?',
            'hard': 'What is hard for you about eating a plant-based diet?',
            'tell_a_friend': 'What would you tell a friend or family member about this class?',
            'improve': 'What can we improve about the class?'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'surveyForm'
        # self.helper.layout = Layout(
        #     BookingField('booking_slot')
        # )
        self.helper.add_input(Submit('submit', 'Submit'))

    # def save(self, commit=True):
    #     """Set start at from form."""
    #     self.instance.event = 'Nutrition Essentials'
    #     self.instance.submitted_at = now()
    #     self.instance.save()
