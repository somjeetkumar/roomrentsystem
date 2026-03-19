import random
from .models import Room
from django.core.mail import send_mail
from django.conf import settings


def room_number():
    number = random.randint(10000, 99999)
    if Room.objects.filter(room_number=number).exists():
        return room_number()
    else:
        return number
    


def send_email_for_user(sub, msg, receiver):

    if isinstance(receiver, str):
        receiver = [receiver]

    send_mail(
        subject=sub,
        message=msg,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=receiver,
        fail_silently=False,
    )

