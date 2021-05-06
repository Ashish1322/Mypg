from django.contrib import admin
from .models import Contact,Pg,Images,Booking,RegisterPg,recommended,Testmotional
# Register your models here.
admin.site.register((Contact,Pg,Images,Booking,RegisterPg,recommended,Testmotional))