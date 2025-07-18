import main.constants as c
from datetime import timedelta
from random import randint

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from unidecode import unidecode

import main.constants as c


class Timestamped(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Discovery(models.Model):
    STATUS_CHOICES = (
        (c.STATUS_NEW, c.STATUS_NEW),
        (c.STATUS_APPROVED, c.STATUS_APPROVED),
        (c.STATUS_DENIED, c.STATUS_DENIED),
        (c.STATUS_BOOKED, c.STATUS_BOOKED),
        (c.STATUS_COMPLETED, c.STATUS_COMPLETED),
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
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default=c.STATUS_NEW)
    has_sent_new_email = models.BooleanField(default=False)  # submitted discovery
    has_sent_booking_email = models.BooleanField(default=False)  # form approved - link to booking
    has_sent_appointment_email = models.BooleanField(default=False)  # booking made, emailed time

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f'<Discovery id={self.id} {self.last_name} {self.created_at}>'

    def is_new(self) -> bool:
        return self.status in (c.STATUS_NEW,)

    def full_name(self) -> str:
        return ' '.join([self.first_name, self.last_name])


class Booking(models.Model):
    BOOKING_CHOICES = (
        (c.STATUS_NEW, c.STATUS_NEW),
        (c.STATUS_BOOKED, c.STATUS_BOOKED),
        (c.STATUS_COMPLETED, c.STATUS_COMPLETED),
    )

    discovery = models.ForeignKey(
        Discovery, on_delete=models.CASCADE, related_name='bookings', null=True)

    slug = models.SlugField(unique=True, null=False)
    start_at = models.DateTimeField(null=True, blank=True)
    end_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=BOOKING_CHOICES, default=c.STATUS_NEW)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """Ensure booking always have a slug"""
        if not self.slug:
            self.slug = randint(100_000_000, 999_999_999)
        super().save(force_insert, force_update, using, update_fields)


class Participant(models.Model):
    SEX_CHOICES = (
        (c.SEX_MALE, c.SEX_MALE.title()),
        (c.SEX_FEMALE, c.SEX_FEMALE.title()),
    )
    ETHNICITY_CHOICES = (
        (c.ETHNICITY_AFRICAN, c.ETHNICITY_AFRICAN.title()),
        (c.ETHNICITY_ASIAN, c.ETHNICITY_ASIAN.title()),
        (c.ETHNICITY_LATIN, c.ETHNICITY_LATIN.title()),
        (c.ETHNICITY_PACIFIC, c.ETHNICITY_PACIFIC.title()),
        (c.ETHNICITY_CAUCASIAN, c.ETHNICITY_CAUCASIAN.title()),
        (c.ETHNICITY_OTHER, c.ETHNICITY_OTHER.title()),
    )
    PRACTITIONER_CHOICES = (
        (c.PRAC_NO, c.PRAC_NO),
        (c.PRAC_YES, c.PRAC_YES),
        (c.PRAC_COLLAB, c.PRAC_COLLAB),
    )

    event = models.CharField(max_length=50)
    submitted_at = models.DateTimeField()
    prefix = models.CharField(max_length=10)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    cellphone = models.CharField(max_length=16)
    email = models.CharField(max_length=150)
    city = models.CharField(max_length=50)
    dob = models.DateField()
    sex = models.CharField(max_length=50, choices=SEX_CHOICES, default=c.SEX_FEMALE)
    ethnicity = models.CharField(max_length=50, choices=ETHNICITY_CHOICES, default=c.ETHNICITY_CAUCASIAN)
    cancer = models.BooleanField()
    diseases = models.CharField(max_length=250, null=True, blank=True)

    origin = models.CharField(max_length=250)
    occupation = models.CharField(max_length=50)
    practitioner = models.CharField(max_length=50, choices=PRACTITIONER_CHOICES)
    diet = models.CharField(max_length=250)
    intention = models.CharField(max_length=250)
    expectation = models.CharField(max_length=250)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Survey(models.Model):
    RATING_CHOICES = [
        [c.RATING_VERY_GOOD, c.RATING_VERY_GOOD],
        [c.RATING_GOOD, c.RATING_GOOD],
        [c.RATING_OK, c.RATING_OK],
        [c.RATING_BAD, c.RATING_BAD],
        [c.RATING_VERY_BAD, c.RATING_VERY_BAD],
    ]
    MEAT_CHOICES = [
        [c.MEAT_YES_REGULARLY, c.MEAT_YES_REGULARLY],
        [c.MEAT_YES_SOMETIMES, c.MEAT_YES_SOMETIMES],
        [c.MEAT_YES_FISH, c.MEAT_YES_FISH],
        [c.MEAT_NO, c.MEAT_NO],
    ]
    MILK_CHOICES = [
        [c.ANSWER_YES, c.ANSWER_YES],
        [c.ANSWER_NO, c.ANSWER_NO],
    ]
    AGE_CHOICES = [
        [c.AGE_9_19, c.AGE_9_19],
        [c.AGE_20_29, c.AGE_20_29],
        [c.AGE_30_39, c.AGE_30_39],
        [c.AGE_40_49, c.AGE_40_49],
        [c.AGE_50_59, c.AGE_50_59],
        [c.AGE_60, c.AGE_60],
    ]
    SEX_CHOICES = (
        (c.SEX_MALE, c.SEX_MALE.title()),
        (c.SEX_FEMALE, c.SEX_FEMALE.title()),
    )
    ETHNICITY_CHOICES = (
        (c.ETHNICITY_AFRICAN, c.ETHNICITY_AFRICAN.title()),
        (c.ETHNICITY_ASIAN, c.ETHNICITY_ASIAN.title()),
        (c.ETHNICITY_LATIN, c.ETHNICITY_LATIN.title()),
        (c.ETHNICITY_PACIFIC, c.ETHNICITY_PACIFIC.title()),
        (c.ETHNICITY_CAUCASIAN, c.ETHNICITY_CAUCASIAN.title()),
        (c.ETHNICITY_OTHER, c.ETHNICITY_OTHER.title()),
    )
    CHANGES_CHOICES = [
        [c.CHANGES_MEAT, c.CHANGES_MEAT],
        [c.CHANGES_DIARY, c.CHANGES_DIARY],
        [c.CHANGES_EGGS, c.CHANGES_EGGS],
        [c.CHANGES_PLANT, c.CHANGES_PLANT],
    ]
    HARD_CHOICES = [
        [c.HARD_EAT_OUT, c.HARD_EAT_OUT],
        [c.HARD_GROCERY, c.HARD_GROCERY],
        [c.HARD_CRAVINGS, c.HARD_CRAVINGS],
        [c.HARD_SUPPORT, c.HARD_SUPPORT],
        [c.HARD_MEALS, c.HARD_MEALS],
        [c.HARD_COST, c.HARD_COST],
        [c.HARD_OTHER, c.HARD_OTHER],
    ]

    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    age = models.CharField(max_length=50, choices=AGE_CHOICES, default=c.AGE_30_39)
    sex = models.CharField(max_length=50, choices=SEX_CHOICES, default=c.SEX_FEMALE)
    ethnicity = models.CharField(
        max_length=50, choices=ETHNICITY_CHOICES, default=c.ETHNICITY_CAUCASIAN)
    country = models.CharField(max_length=100, default='South Africa')
    instructor = models.CharField(max_length=250, default='Nerine Jansen')
    num_classes = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    experience = models.CharField(max_length=50, choices=RATING_CHOICES, default=c.RATING_VERY_GOOD)
    quality = models.CharField(max_length=50, choices=RATING_CHOICES, default=c.RATING_VERY_GOOD)
    meat = models.CharField(max_length=50, choices=MEAT_CHOICES, default=c.MEAT_YES_REGULARLY)
    diary = models.CharField(max_length=50, choices=MILK_CHOICES, default=c.ANSWER_YES)
    changes = models.CharField(max_length=50, choices=CHANGES_CHOICES, default=c.CHANGES_PLANT)
    hard = models.CharField(max_length=50, choices=HARD_CHOICES)
    tell_a_friend = models.TextField()
    improve = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Role(Timestamped):
    name = models.CharField(primary_key=True, max_length=100)


class Psychic(Timestamped):
    roles = models.ManyToManyField(Role)
    url = models.URLField(unique=True)
    name = models.CharField(max_length=250)
    tagline = models.CharField(max_length=100)
    img = models.URLField()

    last_online_at = models.DateTimeField(null=True, blank=True)
    last_oncall_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        roles = [r.name for r in self.roles.all()]
        return unidecode(
            f"{self.name:<20} | {', '.join(roles):<30} | {self.tagline} | {self.url} | {self.img}")


class Status(Timestamped):
    psychic = models.ForeignKey(Psychic, on_delete=models.CASCADE, related_name='statuses')
    status = models.CharField(max_length=50, choices=c.PSYCHIC_STATUS_CHOICES)
    status_at = models.DateTimeField()
