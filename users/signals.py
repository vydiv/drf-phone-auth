import string
import random


def generate_invite_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PhoneNumber


@receiver(post_save, sender=PhoneNumber)
def create_invite_code(sender, instance, created, **kwargs):
    if created:
        instance.invite_code = generate_invite_code()
        instance.save()
