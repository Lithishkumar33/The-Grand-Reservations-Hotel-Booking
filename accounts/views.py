from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
import random
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.contrib.messages import get_messages



# ================= SIGNUP =================
def signup(request):

    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        #  CHECK USERNAME
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {
                'error': 'Username already exists'
            })

        #  CHECK EMAIL
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {
                'error': 'Email already exists'
            })

        #  CREATE USER
        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(request, 'accounts/signup.html')


# ================= LOGIN + OTP =================
def user_login(request):

    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(
            username=username,
            password=password
        )

        #  VALID USER
        if user:

            # 🔥 GENERATE OTP
            otp = random.randint(100000, 999999)
            
            request.session['otp_created'] = timezone.now().isoformat()

            #  SAVE SESSION
            request.session['login_otp'] = str(otp)
            request.session['login_user_id'] = user.id

            #  SEND EMAIL
            send_mail(
                'Your Login OTP',
                f'Your OTP is: {otp}',
                'yourgmail@gmail.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('verify_login_otp')

        # ❌ INVALID LOGIN
        return render(request, 'accounts/login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'accounts/login.html')


# ================= VERIFY LOGIN OTP =================
def verify_login_otp(request):

    # 🔥 RESEND OTP
    if request.method == 'POST' and request.POST.get('resend'):

        user_id = request.session.get('login_user_id')

        if user_id:

            user = User.objects.get(id=user_id)

            otp = random.randint(100000, 999999)

            request.session['login_otp'] = str(otp)

            request.session['otp_created'] = timezone.now().isoformat()

            send_mail(
                'Your New Login OTP',
                f'Your OTP is: {otp}',
                'yourgmail@gmail.com',
                [user.email],
                fail_silently=False,
            )

            return render(request,
                'accounts/verify_login_otp.html',
                {
                    'success': 'New OTP sent to your email'
                }
            )

    # 🔥 VERIFY OTP
    if request.method == 'POST':

        entered_otp = request.POST.get('otp')

        session_otp = request.session.get('login_otp')
        user_id = request.session.get('login_user_id')
        otp_created = request.session.get('otp_created')

        # ❌ SESSION EXPIRED
        if not otp_created:
            return render(request,
                'accounts/verify_login_otp.html',
                {
                    'error': 'OTP expired. Please login again.'
                }
            )

        otp_time = timezone.datetime.fromisoformat(otp_created)

        # 🔥 OTP EXPIRES IN 2 MINUTES
        if timezone.now() > otp_time + timedelta(minutes=2):

            del request.session['login_otp']

            return render(request,
                'accounts/verify_login_otp.html',
                {
                    'error': 'OTP expired'
                }
            )

        # ✅ CORRECT OTP
        if entered_otp == session_otp:

            user = User.objects.get(id=user_id)

            login(request, user)

            # 🔥 CLEAR SESSION
            del request.session['login_otp']
            del request.session['login_user_id']
            del request.session['otp_created']
            messages.success(request, "✅ OTP Verified Successfully")
            messages.success(request, "✅ Successfully LoggedIn")
            return redirect('home')

        # ❌ WRONG OTP
        return render(request,
            'accounts/verify_login_otp.html',
            {
                'error': 'Invalid OTP'
            }
        )

    return render(request, 'accounts/verify_login_otp.html')


# ================= LOGOUT =================
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "👋 Logged out successfully"
    )

    return redirect('landing')