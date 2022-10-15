from random import randint

from django.db import models

STATUS_NEW = 'new'
STATUS_APPROVED = 'approved'
STATUS_DENIED = 'denied'
STATUS_COMPLETED = 'completed'
STATUS_INVALID = 'invalid'
STATUS_BOOKED = 'booked'


class Discovery(models.Model):
    STATUS_CHOICES = (
        (STATUS_NEW, STATUS_NEW),
        (STATUS_APPROVED, STATUS_APPROVED),
        (STATUS_DENIED, STATUS_DENIED),
        (STATUS_BOOKED, STATUS_BOOKED),
        (STATUS_COMPLETED, STATUS_COMPLETED),
    )

    source = models.CharField(
        max_length=200,
        verbose_name='How did you find out about us?')
    first_name = models.CharField(
        max_length=30,
        verbose_name='Your first name')
    last_name = models.CharField(
        max_length=30,
        verbose_name='You last name')
    age = models.PositiveSmallIntegerField(
        verbose_name='How old are you?')
    sex = models.CharField(
        max_length=20,
        choices=[
            ('Male', 'Male'),
            ('Female', 'Female')
        ],
        verbose_name='Your biological sex')
    email = models.CharField(
        max_length=100,
        verbose_name='Your email address')
    cell = models.CharField(
        max_length=20,
        verbose_name='Your phone number')
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
    diagnosis = models.TextField(
        verbose_name='Have you been diagnosed with a condition (diagnosis)?')
    medications = models.TextField(
        verbose_name='List the medications or supplements you are currently using:')
    vaccinations = models.TextField(
        verbose_name='Have you received the covid vaccinations? Which brand and how many?')
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

    # email notifications
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=STATUS_NEW)
    has_sent_new_email = models.BooleanField(default=False)  # submitted discovery
    has_sent_booking_email = models.BooleanField(default=False)  # form approved - link to booking
    has_sent_appointment_email = models.BooleanField(default=False)  # booking made, emailed time

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'<Discovery id={self.id} {self.last_name} {self.created_at}>'

    def is_new(self) -> bool:
        return self.status in (STATUS_NEW,)

    def full_name(self) -> str:
        return ' '.join([self.first_name, self.last_name])


class Booking(models.Model):
    BOOKING_CHOICES = (
        (STATUS_NEW, STATUS_NEW),
        (STATUS_BOOKED, STATUS_BOOKED),
        (STATUS_COMPLETED, STATUS_COMPLETED),
    )

    discovery = models.ForeignKey(
        Discovery, on_delete=models.CASCADE, related_name='bookings', null=True)

    slug = models.SlugField(unique=True, null=False)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=BOOKING_CHOICES, default=STATUS_NEW)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Ensure booking always have a slug"""
        if not self.slug:
            self.slug = randint(100_000_000, 999_999_999)
        super().save(force_insert, force_update, using, update_fields)
