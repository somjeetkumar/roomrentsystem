from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser

# Create your models here.

class UserModel(AbstractUser):
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    image = models.ImageField(upload_to='images/', null=True,blank=True)
    verify = models.BooleanField(default=False)

    def __str__(self):
        return self.username
    

class Otp(models.Model):
    otp = models.CharField(max_length=10)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        expire_time = self.created_at + timedelta(minutes=5)
        return timezone.now() > expire_time




class Room(models.Model):
    
    onwer = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.CharField()
    room_type = models.CharField()
    available = models.BooleanField(default= True)
    create_at = models.DateTimeField(auto_now_add=True)
    location = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100,default="jaipur")
    near_by = models.CharField(max_length=100, default="Dadi Ka Phatak")
    pin_code = models.CharField(max_length=10, default="000000")
    room_number = models.IntegerField(default=00000,unique=True)
    room_checked = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    



class Room_Image(models.Model):
    
    room = models.ForeignKey(Room, on_delete=models.CASCADE,related_name='room_images')
    image = models.ImageField( upload_to= 'room_images/', null=True, blank=True)
    check_image = models.BooleanField(default=False)

    def __str__(self):
        return self.room.title
    

    




class Payment(models.Model):

    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    amount = models.IntegerField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    razorpay_order_id = models.CharField(max_length=100)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)



