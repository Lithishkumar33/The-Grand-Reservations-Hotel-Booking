from django.conf import settings
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

            #  SEND EMAIL SAFELY
            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or '7760lithish@gmail.com'
            try:
                send_mail(
                    'Your Login OTP - The Grand Reservations',
                    f'Hello {user.username},\n\nYour Login OTP is: {otp}\nThis code will expire in 2 minutes.\n\nBest regards,\nThe Grand Reservations Team',
                    from_email,
                    [user.email],
                    fail_silently=False,
                )
                request.session['otp_delivery_failed'] = False
            except Exception as e:
                print(f"[SMTP Warning] Could not send OTP email via SMTP: {e}. Fallback OTP: {otp}")
                request.session['otp_delivery_failed'] = True

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

            from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or '7760lithish@gmail.com'
            context = {}
            try:
                send_mail(
                    'Your New Login OTP - The Grand Reservations',
                    f'Hello {user.username},\n\nYour New Login OTP is: {otp}\nThis code will expire in 2 minutes.\n\nBest regards,\nThe Grand Reservations Team',
                    from_email,
                    [user.email],
                    fail_silently=False,
                )
                context['success'] = 'New OTP sent to your email'
                request.session['otp_delivery_failed'] = False
            except Exception as e:
                print(f"[SMTP Warning] Could not send resend OTP email: {e}. Fallback OTP: {otp}")
                request.session['otp_delivery_failed'] = True
                context['demo_otp'] = str(otp)
                context['success'] = f'New OTP: {otp}'

            return render(request, 'accounts/verify_login_otp.html', context)

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
            if 'otp_delivery_failed' in request.session:
                del request.session['otp_delivery_failed']
            messages.success(request, "✅ OTP Verified Successfully")
            messages.success(request, "✅ Successfully LoggedIn")
            return redirect('home')

        # ❌ WRONG OTP
        context = {'error': 'Invalid OTP'}
        if request.session.get('otp_delivery_failed'):
            context['demo_otp'] = request.session.get('login_otp')
        return render(request, 'accounts/verify_login_otp.html', context)

    context = {}
    if request.session.get('otp_delivery_failed'):
        demo_otp = request.session.get('login_otp')
        context['demo_otp'] = demo_otp
        context['error'] = f"Email delivery unavailable on serverless. Your OTP is: {demo_otp}"

    return render(request, 'accounts/verify_login_otp.html', context)


# ================= LOGOUT =================
def user_logout(request):

    logout(request)

    messages.success(
        request,
        "👋 Logged out successfully"
    )

    return redirect('landing')