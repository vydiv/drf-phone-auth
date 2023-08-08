from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from dj_rest_auth.registration.serializers import RegisterSerializer
from phonenumber_field.serializerfields import PhoneNumberField

from .exceptions import InvalidCredentialsException, AccountDisabledException, AccountNotRegisteredException
from .models import PhoneNumber

User = get_user_model()


class UserRegistrationSerializer(RegisterSerializer):
    """
    Serializer for registrating new users using phone number.
    """
    username = None
    phone_number = PhoneNumberField(
        required=False,
        write_only=True,
        validators=[
            UniqueValidator(
                queryset=PhoneNumber.objects.all(),
                message=_(
                    "A user is already registered with this phone number."),
            )
        ],
    )
    email = None

    def validate(self, validated_data):
        phone_number = validated_data.get('phone_number', None)

        if not phone_number:
            raise serializers.ValidationError(
                _("Enter a phone number."))

        if validated_data['password1'] != validated_data['password2']:
            raise serializers.ValidationError(
                _("The two password fields didn't match."))

        return validated_data

    def get_cleaned_data_extra(self):
        return {
            'phone_number': self.validated_data.get('phone_number', ''),
        }

    def create_phone(self, user, validated_data):
        phone_number = validated_data.get("phone_number")

        if phone_number:
            PhoneNumber.objects.create(user=user, phone_number=phone_number)
            user.phone.save()

    def custom_signup(self, request, user):
        self.create_phone(user, self.get_cleaned_data_extra())


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer to login users with email or phone number.
    """
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})

    def _validate_phone_email(self, phone_number, password):
        user = None

        if str(phone_number) and password:
            user = authenticate(username=str(phone_number), password=password)
        else:
            raise serializers.ValidationError(
                _("Enter a phone number or an email and password."))

        return user

    def validate(self, validated_data):
        phone_number = validated_data.get('phone_number')
        password = validated_data.get('password')

        user = None

        user = self._validate_phone_email(phone_number, password)

        if not user:
            raise InvalidCredentialsException()

        if not user.is_active:
            raise AccountDisabledException()

        if not user.phone.is_verified:
            raise serializers.ValidationError(
                ('Phone number is not verified.'))

        validated_data['user'] = user
        return validated_data


class PhoneNumberSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize phone number.
    """
    phone_number = PhoneNumberField()

    class Meta:
        model = PhoneNumber
        fields = ('phone_number',)

    def validate_phone_number(self, value):
        try:
            queryset = User.objects.get(phone__phone_number=value)
            if queryset.phone.is_verified == True:
                err_message = _('Phone number is already verified')
                raise serializers.ValidationError(err_message)

        except User.DoesNotExist:
            raise AccountNotRegisteredException()

        return value


class VerifyPhoneNumberSerialzier(serializers.Serializer):
    """
    Serializer class to verify OTP.
    """
    phone_number = PhoneNumberField()
    otp = serializers.CharField(max_length=4)

    def validate_phone_number(self, value):
        queryset = User.objects.filter(phone__phone_number=value)
        if not queryset.exists():
            raise AccountNotRegisteredException()
        return value

    def validate(self, validated_data):
        phone_number = str(validated_data.get('phone_number'))
        otp = validated_data.get('otp')

        queryset = PhoneNumber.objects.get(phone_number=phone_number)

        queryset.check_verification(security_code=otp)

        return validated_data


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(read_only=True, source="user.username")

    class Meta:
        model = PhoneNumber
        fields = ('username', 'phone_number', 'invite_code', 'activated_invite_code')


class UserSerializerT(serializers.ModelSerializer):
    another_invite_code = serializers.CharField(write_only=True, required=False)
    phone_number = serializers.StringRelatedField(source='phone.phone_number')
    invite_code = serializers.StringRelatedField(source='phone.invite_code')
    activated_invite_code = serializers.StringRelatedField(source='phone.activated_invite_code')

    invited_users = serializers.SerializerMethodField()

    class Meta:
        model = PhoneNumber
        fields = ['phone_number', 'another_invite_code', 'invite_code', 'activated_invite_code',
                  'invited_users', ]

    def get_invited_users(self, obj):
        # Get all users who entered the current user's invite code
        users = User.objects.filter(phone__activated_invite_code=obj.phone.invite_code)
        # Return a list of their phone numbers
        print([user.phone.phone_number for user in users])
        return [
            (f'+{user.phone.phone_number.country_code}{user.phone.phone_number.national_number}') for user in users]

    def update(self, instance, validated_data):
        another_invite_code = validated_data.pop('another_invite_code', None)

        if another_invite_code:
            phone_number = instance.phone
            if phone_number.activated_invite_code:
                raise serializers.ValidationError("You have already activated the invite code.")
            if not PhoneNumber.objects.filter(invite_code=another_invite_code).exists():
                raise serializers.ValidationError("The entered invite code does not exist.")
            phone_number.activated_invite_code = another_invite_code
            phone_number.save()

        return instance
