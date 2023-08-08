from django.urls import path

from .views import *

app_name = 'users'

urlpatterns = [
    path('register/', UserRegisterationAPIView.as_view(), name='user_register'),
    path('login/', UserLoginAPIView.as_view(), name='user_login'),
    path('send-sms/', SendOrResendSMSAPIView.as_view(), name='send_resend_sms'),
    path('verify-phone/', VerifyPhoneNumberAPIView.as_view(), name='verify_phone_number'),
    path('list/', UserList.as_view(), name='user_list'),
    path('detail/<int:pk>', UserDetail.as_view(), name='user_detail'),
    path('profile/', Profile.as_view(), name='profile'),

]
