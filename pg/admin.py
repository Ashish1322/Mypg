from django.contrib import admin
from .models import Contact,Pg,Images,Booking,RegisterPg
# Register your models here.
admin.site.register((Contact,Pg,Images,Booking,RegisterPg))