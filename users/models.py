import random
from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class PhoneNumber(models.Model):
    user = models.OneToOneField(
        User, related_name='phone', on_delete=models.CASCADE)
    phone_number = PhoneNumberField(unique=True)
    security_code = models.CharField(max_length=120)
    is_verified = models.BooleanField(default=False)
    sent = models.DateTimeField(null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    invite_code = models.CharField(max_length=6, blank=True, null=True)
    activated_invite_code = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.phone_number.as_e164

    def generate_security_code(self):
        code = str(random.randint(1000, 9999))
        print('_' * 20, code)
        return code

    def send_confirmation(self):
        self.security_code = self.generate_security_code()

        print(
            f'Sending security code {self.security_code} to phone {self.phone_number}')
        try:
            self.save()
            return True
        except Exception as e:
            print(e)

    def check_verification(self, security_code):
        if (
                security_code == self.security_code and
                self.is_verified == False
        ):
            self.is_verified = True
            self.save()
        else:
            print("Your security code is wrong, expired or this phone is verified before.")

        return self.is_verified
