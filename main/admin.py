from django.contrib import admin

from main.models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass
