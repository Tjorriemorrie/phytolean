from django.db import models


class Booking(models.Model):
    source = models.CharField(
        max_length=200,
        verbose_name='How did you find out about us?')
    first_name = models.CharField(
        max_length=30,
        verbose_name='Your first name')
    last_name = models.CharField(
        max_length=30,
        verbose_name='You last name')
    email = models.CharField(
        max_length=100,
        verbose_name='Your email address')
    cell = models.CharField(
        max_length=20,
        verbose_name='Your phone number')
    age = models.PositiveSmallIntegerField(
        verbose_name='How old are you?')
    reason = models.TextField(
        verbose_name='What brings you here to see us?')
    timing = models.TextField(
        verbose_name='What caused you to seek help NOW?')

    crn_skin_health = models.BooleanField(verbose_name='Skin health')
    crn_digestive_health = models.BooleanField(verbose_name='Digestive health')
    crn_stress = models.BooleanField(verbose_name='Stress (mental) health)')
    crn_sleep = models.BooleanField(verbose_name='Sleep health')
    crn_pain = models.BooleanField(verbose_name='Pain / symptom health')
    crn_fertility = models.BooleanField(verbose_name='Fertility / fecudity nutrition')
    crn_child = models.BooleanField(verbose_name='Child / family nutrition')
    crn_sport = models.BooleanField(verbose_name='Sport / excercise nutrition')
    crn_safe = models.BooleanField(verbose_name='Safe / efficient supplementation')
    crn_diet = models.BooleanField(verbose_name='Diet quality / nutritional imbalances')
    crn_weight = models.BooleanField(verbose_name='Weight management')
    crn_eating = models.BooleanField(verbose_name='Emotional eating')
    crn_detox = models.BooleanField(verbose_name='Nutritional detoxification')
    crn_allergy = models.BooleanField(verbose_name='Food allergies and intolerances')
    crn_longevity = models.BooleanField(verbose_name='Healthy longevity nutrition')
    crn_nutrition = models.BooleanField(verbose_name='Nutrition for mitigating cancer risk')
    crn_lifestyle = models.BooleanField(verbose_name='Lifestyle practices / life quality')
    crn_other = models.CharField(max_length=250, null=True, blank=True, verbose_name='Other concern')

    association = models.TextField(
        verbose_name='Why do you want to work with us specifically? What excites you about working together?')
    expectation = models.TextField(
        verbose_name='How do you think we might help?')
    driver = models.TextField(
        verbose_name='What would you like to achieve? How do you want to feel? What do you want to be doing differently?')
    elaboration = models.TextField(
        verbose_name='Can you tell me about your situation?')
    duration = models.TextField(
        verbose_name='How long have you been trying to lose weight?')
    expansion = models.TextField(
        verbose_name='What other things you have not mentioned yet would be important for us to know?')
    priorities = models.TextField(
        verbose_name='Where would you like to begin?')
    struggles = models.TextField(
        verbose_name='When it comes to losing weight - what are your biggest struggles or obstacles you experience?')

    chl_emotion = models.BooleanField(verbose_name='Emotional/stress eating')
    chl_planning = models.BooleanField(verbose_name='Lack of planning')
    chl_crave = models.BooleanField(verbose_name='Cravings')
    chl_snack = models.BooleanField(verbose_name='Snacking when not hungry')
    chl_quick = models.BooleanField(verbose_name='Eating quickly')
    chl_sweet = models.BooleanField(verbose_name='Sweet tooth')
    chl_out = models.BooleanField(verbose_name='Eating out frequently')
    chl_large = models.BooleanField(verbose_name='Large portions')
    chl_time = models.BooleanField(verbose_name='Time to prepare meals')
    chl_alcohol = models.BooleanField(verbose_name='Wine/alcohol')
    chl_unsure = models.BooleanField(verbose_name='Do not know what I should eat')
    chl_dislike = models.BooleanField(verbose_name='Dislike cooking/do not know how to cook')
    chl_pressure = models.BooleanField(verbose_name='Family/peer pressure')
    chl_help = models.BooleanField(verbose_name='Unsupportive environment')
    chl_other = models.CharField(max_length=250, null=True, blank=True, verbose_name='Other reason')

    committed = models.TextField(
        verbose_name='How committed are you to losing weight and reaching your goals?')
    investment = models.BooleanField(
        verbose_name='Are you willing and able to make this financial investment in yourself to achieve your goals?')
    punctual = models.BooleanField(
        verbose_name='As a coach, we deeply value and respect your time. If we invite you to book a call, can you commit to showing up at the scheduled time for our call, fully present without distractions?')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
