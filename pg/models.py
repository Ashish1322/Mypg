from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User
import os
# Create your models here.
class Contact(models.Model):
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField()
    message = models.TextField()
    responded = models.BooleanField()
    def __str__(self):
        return self.name

class Pg(models.Model):
    type_choices = (
        ("Girls","girls"),
        ("Boys","boys"),
        ("Both","both"),
    )
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500,default="")
    type_pg = models.CharField(max_length=50,choices=type_choices,default='Both')
    description = models.TextField()
    distance = models.CharField(max_length=1000,default="")
    
    verified = models.BooleanField()
    price = models.IntegerField()
    phone_number = models.IntegerField()
    ratings = models.IntegerField()
    location = models.CharField(max_length=1000,default="")
    rules = models.TextField( default=" ")
    thumbnail = models.ImageField(upload_to = "images/")
    video = models.CharField(max_length=500,default="")
    available = models.BooleanField(default=1)
    def __str__(self):
        return str(self.sno) +" "+ (self.name)[0:10]

@receiver(models.signals.post_delete, sender=Pg)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)

class Images(models.Model):
    pg = models.ForeignKey(Pg,default=None,on_delete=models.CASCADE)
    imgae = models.ImageField(upload_to="images_pg/")
    def __str__(self):
        return self.pg.name
    
class Booking(models.Model):
    sno = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=40,default=" ")
    last_name = models.CharField(max_length=40,default=" ")
    email = models.CharField(max_length=50,default=' ')
    address = models.CharField(max_length=500,default=" ")
    phone_number = models.BigIntegerField()
    state = models.CharField(max_length=40,default=' ')
    zip_code = models.IntegerField()
    college = models.CharField(max_length=200,default=" ")
    order_confirmed = models.BooleanField()
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    pg = models.ForeignKey(Pg,on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username
    

class RegisterPg(models.Model):
    type_choices = (
        ("Girls","girls"),
        ("Boys","boys"),
        ("Both","both"),
    )
    sno = models.AutoField(primary_key=True)
    name = models.CharField(max_length=80,default=" ")
    location = models.CharField(max_length=40,default=" ")
    typepg = models.CharField(choices=type_choices,default='Both',max_length=20)
    phonenumber = models.BigIntegerField()
    description = models.TextField()
    owner_name = models.CharField(max_length=50,default=" ")
    verified = models.BooleanField()

    def __str__(self):
        return self.name

class recommended(models.Model):
    pg = models.ForeignKey(Pg,on_delete=models.CASCADE)
    def __str__(self):
        return self.pg.name

class Testmotional(models.Model):
    sno = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    test = models.TextField()
    def __str__(self):
        return self.user.username
    