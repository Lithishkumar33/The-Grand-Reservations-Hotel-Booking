from django.urls import path
from .views import signup, user_login, user_logout, verify_login_otp

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('verify-login-otp/', verify_login_otp, name='verify_login_otp'),
]
