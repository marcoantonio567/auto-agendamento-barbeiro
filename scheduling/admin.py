from django.contrib import admin
from .models import Appointment


class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        'client_name',
        'client_phone',
        'service',
        'barber',
        'date',
        'hour',
        'payment_status',
        'rescheduled',
        'price',
    )
    list_filter = (
        'service',
        'barber',
        'date',
        'payment_status',
        'rescheduled',
    )
    search_fields = ('client_name', 'client_phone')
    ordering = ('-date', 'hour')
    date_hierarchy = 'date'


admin.site.register(Appointment, AppointmentAdmin)

