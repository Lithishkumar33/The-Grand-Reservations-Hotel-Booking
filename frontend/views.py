from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from booking.models import Room, Booking, Payment, Trip, TripBooking
from django.shortcuts import get_object_or_404
from booking.models import TripBooking
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
import os
from django.conf import settings
from datetime import datetime
import io
from django.core.mail import EmailMessage
from django.contrib import messages
import requests
import json
from django.db.models import Q
from django.db.models import Min

CASHFREE_APP_ID = os.getenv("CASHFREE_APP_ID", "TEST110659890be6f06041cce46e06f398956011")
CASHFREE_SECRET_KEY = os.getenv("CASHFREE_SECRET_KEY", "TEST_SECRET_KEY")


def link_callback(uri, rel):
    if uri.startswith(settings.STATIC_URL):
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.STATIC_URL, "static/"))
    elif uri.startswith(settings.MEDIA_URL):
        path = os.path.join(settings.BASE_DIR, uri.replace(settings.MEDIA_URL, "media/"))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception('Media file not found: ' + path)

    return path

def trip_invoice_pdf(request, booking_id):
    booking = TripBooking.objects.get(id=booking_id)

    template = get_template('trip_invoice_pdf.html')
    html = template.render({'booking': booking})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking_id}.pdf"'

    pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    return response





# ================= ROOMS =================
from collections import defaultdict

def rooms(request):

    location = request.GET.get('location')

    grouped_hotels = {}
    locations = Room.objects.values_list('location', flat=True).distinct()

    if location:
        rooms = Room.objects.filter(location=location).prefetch_related('images')

        grouped = defaultdict(list)

        for room in rooms:
            grouped[room.hotel].append(room)

        grouped_hotels = dict(grouped)

    return render(request, 'rooms.html', {
        'grouped_hotels': grouped_hotels,
        'locations': locations,
        'selected_location': location
    })
# ================= HOME =================
from collections import defaultdict

def home(request):

    all_rooms = Room.objects.prefetch_related('images')

    grouped_hotels = {}

    for room in all_rooms:

        key = (room.hotel, room.location)

        if key not in grouped_hotels:
            grouped_hotels[key] = {
                'rooms': [],
                'image': None
            }

        grouped_hotels[key]['rooms'].append(room)

        # ✅ take first image
        if not grouped_hotels[key]['image'] and room.images.exists():
            grouped_hotels[key]['image'] = room.images.first()

    return render(request, 'home.html', {
        'grouped_hotels': grouped_hotels
    })
# ================= ROOM DETAILS =================

from django.db.models import Q

@login_required(login_url='/accounts/login/')
def room_detail(request, room_id):

    room = get_object_or_404(Room, id=room_id)

    if request.method == 'POST':

        check_in_str = request.POST.get('check_in')
        check_out_str = request.POST.get('check_out')
        package = request.POST.get('package')

        # 🚨 EMPTY VALIDATION
        if not check_in_str or not check_out_str:
            return render(request, 'room_detail.html', {
                'room': room,
                'popup_error': "Please select check-in and check-out dates"
            })

        # ✅ DATE CONVERT
        try:
            check_in = datetime.strptime(check_in_str, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_str, "%Y-%m-%d").date()
        except:
            return render(request, 'room_detail.html', {
                'room': room,
                'popup_error': "Invalid date format"
            })

        # ❌ INVALID ORDER
        if check_in >= check_out:
            return render(request, 'room_detail.html', {
                'room': room,
                'popup_error': "Check-out must be after check-in"
            })

        # 🔥 DATE OVERLAP CHECK
        bookings = Booking.objects.filter(
            room=room,
            status__in=['Pending', 'Paid']
        ).filter(
            Q(check_in__lt=check_out) & Q(check_out__gt=check_in)
        )

        if bookings.exists():

            booked_dates = [
                f"{b.check_in.strftime('%d %b')} → {b.check_out.strftime('%d %b')}"
                for b in bookings
            ]

            return render(request, 'room_detail.html', {
                'room': room,
                'popup_error': f"Already booked for: {', '.join(booked_dates)}"
            })

        # ✅ CALCULATE DAYS
        days = (check_out - check_in).days

        # ✅ PRICE
        if package == "Room Only":
            price_per_day = room.price_room_only
        elif package == "Room + Breakfast":
            price_per_day = room.price_with_breakfast
        elif package == "Room + Breakfast + Dinner":
            price_per_day = room.price_with_breakfast_dinner
        else:
            price_per_day = 0

        total_amount = price_per_day * days

        Booking.objects.create(
            user=request.user,
            room=room,
            check_in=check_in,
            check_out=check_out,
            package=package,
            total_amount=total_amount,
            status='Pending'
        )

        return redirect('my_bookings')

    return render(request, 'room_detail.html', {'room': room})
# ================= USER BOOKINGS =================

@login_required(login_url='/accounts/login/')
def my_bookings(request):

    room_bookings = Booking.objects.filter(user=request.user)

    return render(request, 'my_bookings.html', {
        'room_bookings': room_bookings
    })


# ================= PAYMENT =================
@login_required(login_url='/accounts/login/')
def pay_now(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == 'Paid':
        return redirect('my_bookings')

    url = "https://sandbox.cashfree.com/pg/orders"

    headers = {
        "Content-Type": "application/json",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY,
        "x-api-version": "2022-09-01"
    }

    data = {
        "order_id": f"room_{booking.id}",
        "order_amount": float(booking.total_amount),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": str(request.user.id),
            "customer_email": request.user.email,
            "customer_phone": "9999999999"
        },
        "order_meta": {
            "return_url": f"http://127.0.0.1:8000/payment-success/{booking.id}/"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    res = response.json()

    print("CASHFREE RESPONSE:", res)   # 👈 DEBUG

    if "payment_session_id" in res:
        return render(request, "payments/cashfree_payment.html", {
             "payment_session_id": res["payment_session_id"],
             "booking": booking
        })
    else:
        return HttpResponse(f"Cashfree Error: {res}")

# ================= INVOICE =================

@login_required(login_url='/accounts/login/')
def invoice(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    payment = get_object_or_404(
        Payment,
        booking=booking
    )

    return render(request, 'payments/invoice.html', {
        'payment': payment
    })


# ================= STRIPE PAYMENT =================


# ================= DREAM DESTINATIONS =================

def trips_dashboard(request):

    package_days = request.GET.get('package_days')

    # ✅ FILTER BY PACKAGE
    if package_days:
        trips = Trip.objects.filter(package_days=package_days)
    else:
        trips = Trip.objects.all()

    # ✅ PACKAGE DROPDOWN
    packages = Trip.objects.values_list('package_days', flat=True).distinct()

    # ✅ FAMOUS TRIPS (ALWAYS SHOW)
    famous = Trip.objects.filter(famous_place=True)

    return render(request, 'trips/dashboard.html', {
        'trips': trips,
        'packages': packages,
        'famous': famous   # 🔥 ADD THIS
    })


# ================= TRIP DETAILS =================

from django.db.models import Q

@login_required
def trip_detail(request, trip_id):

    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':

        guide_option = request.POST.get('guide')

        start_date_str = request.POST.get('start_date')
        end_date_str = request.POST.get('end_date')

        # 🚨 VALIDATION (EMPTY)
        if not start_date_str or not end_date_str:
            return render(request, 'trips/trip_detail.html', {
                'trip': trip,
                'popup_error': "Please select dates"
            })

        # ✅ CONVERT
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except:
            return render(request, 'trips/trip_detail.html', {
                'trip': trip,
                'popup_error': "Invalid date format"
            })

        # ❌ INVALID DATE
        if start_date >= end_date:
            return render(request, 'trips/trip_detail.html', {
                'trip': trip,
                'popup_error': "End date must be after start date"
            })

        days_selected = (end_date - start_date).days

        if days_selected > trip.package_days:
            return render(request, 'trips/trip_detail.html', {
                'trip': trip,
                'popup_error': f"This is {trip.package_days}-day package"
            })

        # 🔥 DATE OVERLAP CHECK (FIXED)
        bookings = TripBooking.objects.filter(
            trip=trip,
            status__in=['Pending', 'Paid']   # ✅ ONLY block confirmed bookings
        ).filter(
            start_date__lt=end_date,
            end_date__gt=start_date
        )

        if bookings.exists():

            booked_dates = [
                f"{b.start_date.strftime('%d %b')} → {b.end_date.strftime('%d %b')}"
                for b in bookings
            ]

            return render(request, 'trips/trip_detail.html', {
                'trip': trip,
                'popup_error': f"Already booked for: {', '.join(booked_dates)}"
            })

        # ✅ PRICE
        if guide_option == "Guide":
            price = trip.price_with_guide
        else:
            price = trip.price_without_guide

        # ✅ SAVE
        TripBooking.objects.create(
            user=request.user,
            trip=trip,
            guide_option=guide_option,
            total_price=price,
            start_date=start_date,
            end_date=end_date,
            status='Pending'
        )

        return redirect('my_trips')

    return render(request, 'trips/trip_detail.html', {'trip': trip})

# ================= USER TRIPS =================

@login_required(login_url='/accounts/login/')
def my_trips(request):

    bookings = TripBooking.objects.filter(user=request.user)

    return render(request, 'trips/my_trips.html', {
        'bookings': bookings
    })

@login_required
def pay_trip(request, booking_id):

    booking = get_object_or_404(
        TripBooking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'Paid':
        return redirect('my_trips')

    url = "https://sandbox.cashfree.com/pg/orders"

    headers = {
        "Content-Type": "application/json",
        "x-client-id": CASHFREE_APP_ID,
        "x-client-secret": CASHFREE_SECRET_KEY,
        "x-api-version": "2022-09-01"
    }

    data = {
        "order_id": f"trip_{booking.id}",
        "order_amount": float(booking.total_price),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": str(request.user.id),
            "customer_email": request.user.email,
            "customer_phone": "9999999999"
        },
        "order_meta": {
            "return_url": f"http://127.0.0.1:8000/trip-payment-success/{booking.id}/"
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    res = response.json()

    if "payment_session_id" in res:
        return render(request, "payments/cashfree_payment.html", {
           "payment_session_id": res["payment_session_id"],
           "booking": booking
        })
    else:
         return HttpResponse(f"Cashfree Error: {res}")
    
@login_required
def trip_invoice(request, booking_id):

    booking = get_object_or_404(
        TripBooking,
        id=booking_id,
        user=request.user
    )

    return render(request, 'trips/trip_invoice.html', {
        'booking': booking
    })

@login_required
def cancel_room_booking(request, booking_id):

    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    # ❌ Prevent cancel if already cancelled
    if booking.status == 'Cancelled':
        return redirect('my_bookings')

    # ✅ Update status
    booking.status = 'Cancelled'
    booking.save()

    # 🔓 Make room available again
    booking.room.is_available = True
    booking.room.save()

    return redirect('my_bookings')

@login_required
def cancel_trip_booking(request, booking_id):

    booking = get_object_or_404(
        TripBooking,
        id=booking_id,
        user=request.user
    )

    if booking.status == 'Cancelled':
        return redirect('my_trips')

    booking.status = 'Cancelled'
    booking.save()

    return redirect('my_trips')

def room_invoice_pdf(request, booking_id):

    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    payment = get_object_or_404(Payment, booking=booking)

    template = get_template('payments/room_invoice_pdf.html')
    html = template.render({'payment': payment})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="room_invoice_{booking_id}.pdf"'

    pisa.CreatePDF(html, dest=response, link_callback=link_callback)

    return response

@login_required
def payment_success(request, booking_id):

    # ❌ REMOVED user=request.user (IMPORTANT FIX)
    booking = get_object_or_404(Booking, id=booking_id)

    if booking.status == 'Paid':
        return redirect('my_bookings')

    # ✅ SAVE PAYMENT
    payment = Payment.objects.create(
        booking=booking,
        payment_method='Cashfree',
        amount_paid=booking.total_amount
    )

    booking.status = 'Paid'
    booking.save()
    
    # =========================
    # 📄 GENERATE PDF
    # =========================
    template = get_template('payments/room_invoice_pdf.html')
    html = template.render({'payment': payment})

    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result, link_callback=link_callback)
    pdf = result.getvalue()

    # =========================
    # 📧 SEND EMAIL
    # =========================
    email = EmailMessage(
        subject="Room Booking Confirmed",
        body=f"""
Hello {booking.user.username},

Your payment was successful 🎉

Room: {booking.room.room_number}
Stay: {booking.check_in} → {booking.check_out}
Amount Paid: ₹{booking.total_amount}

Invoice attached.

Thank you for choosing The Grand Reservations!
""",
        from_email=settings.EMAIL_HOST_USER,
        to=[booking.user.email],   # ✅ ALWAYS CORRECT USER
    )

    email.attach(
        f"room_invoice_{booking.id}.pdf",
        pdf,
        "application/pdf"
    )

    email.send(fail_silently=False)

    return redirect('my_bookings')

@login_required
def trip_payment_success(request, booking_id):

    # ❌ REMOVED user=request.user (IMPORTANT FIX)
    booking = get_object_or_404(TripBooking, id=booking_id)

    if booking.status == 'Paid':
        return redirect('my_trips')

    # ✅ MARK PAID
    booking.status = 'Paid'
    booking.save()

    # =========================
    # 📄 GENERATE PDF
    # =========================
    template = get_template('trips/trip_invoice_pdf.html')
    html = template.render({'booking': booking})

    result = io.BytesIO()
    pisa.CreatePDF(html, dest=result, link_callback=link_callback)
    pdf = result.getvalue()

    # =========================
    # 📧 SEND EMAIL
    # =========================
    email = EmailMessage(
        subject="Trip Booking Confirmed",
        body=f"""
Hello {booking.user.username},

Your trip has been successfully booked 🎉

Trip: {booking.trip.trip_name}
Destination: {booking.trip.destination}
Duration: {booking.start_date} → {booking.end_date}
Total Paid: ₹{booking.total_price}

Invoice attached.

Thank you for choosing The Grand Reservations!
""",
        from_email=settings.EMAIL_HOST_USER,
        to=[booking.user.email],   # ✅ CORRECT USER
    )

    email.attach(
        f"trip_invoice_{booking.id}.pdf",
        pdf,
        "application/pdf"
    )

    email.send(fail_silently=False)

    return redirect('my_trips')

def quick_enquiry(request):

    if request.method == 'POST':

        name = request.POST.get('name')
        email = request.POST.get('email')
        mobile = request.POST.get('mobile')
        message = request.POST.get('message')

        # 📧 EMAIL CONTENT
        email_body = f"""
New Enquiry Received 🚀

Name: {name}
Email: {email}
Mobile: {mobile}

Message:
{message}
"""

        email_msg = EmailMessage(
            subject="New Enquiry - The Grand Reservations",
            body=email_body,
            from_email=settings.EMAIL_HOST_USER,
            to=["7760lithish@gmail.com"],   # ✅ YOUR EMAIL
        )

        email_msg.send(fail_silently=False)

        messages.success(request, "Enquiry sent successfully!")

        return redirect('home')

    return redirect('home')

def landing(request):
    if request.user.is_authenticated:
        return redirect('home')   # 🔥 skip landing if logged in
    
    return render(request, 'landing.html')

def explore(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return redirect('home')   # or rooms/trips