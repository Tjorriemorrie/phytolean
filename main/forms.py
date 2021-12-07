from captcha.fields import CaptchaField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, Div
from django import forms

from main.models import Booking


class BookingForm(forms.ModelForm):
    captcha = CaptchaField()

    class Meta:
        model = Booking
        fields = '__all__'
        exclude = ['created_at', 'updated_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'bookingForm'
        self.helper.form_class = 'form'
        self.helper.form_method = 'post'
        # self.helper.form_action = 'submit_survey'
        self.helper.layout = Layout(
            Fieldset(
                'Personal details',
                Field('source'),
                Field('first_name'),
                Field('last_name'),
                Field('email'),
                Field('cell'),
                Field('age'),
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
        )

        self.helper.add_input(Submit('submit', 'Submit'))
