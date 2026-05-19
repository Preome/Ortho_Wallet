from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('send-otp/', views.SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view(), name='verify-otp'),
    path('setup-pin/', views.SetupPINView.as_view(), name='setup-pin'),
    path('verify-pin/', views.VerifyPINView.as_view(), name='verify-pin'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]