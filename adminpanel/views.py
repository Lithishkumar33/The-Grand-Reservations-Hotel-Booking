from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from booking.models import Room, RoomImage, Booking, Payment, Trip
from booking.models import TripBooking  
from booking.models import Hotel


# =========================
# ADMIN LOGIN
# =========================
def admin_login(request):

    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user and user.is_staff:
            login(request, user)
            request.session['is_admin'] = True
            return redirect('admin_dashboard')

        return render(request, 'admin/login.html', {
            'error': 'Invalid admin credentials'
        })

    return render(request, 'admin/login.html')


# =========================
# ADMIN DASHBOARD
# =========================
@login_required(login_url='/admin/login/')
def admin_dashboard(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    context = {
    'total_rooms': Room.objects.count(),
    'available_rooms': Room.objects.filter(is_available=True).count(),
    'total_bookings': Booking.objects.count(),
    'total_payments': Payment.objects.count(),
    'total_trips': Trip.objects.count(),
    'trip_bookings': TripBooking.objects.count(),
}

    return render(request, 'admin/dashboard.html', context)


# =========================
# ROOMS MANAGEMENT
# =========================
@login_required(login_url='/admin/login/')
def admin_rooms(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    rooms = Room.objects.all()

    # attach latest booking to each room
    for room in rooms:
        booking = Booking.objects.filter(room=room).order_by('-id').first()
        room.latest_booking = booking

    return render(request, 'admin/rooms.html', {
        'rooms': rooms
    })


# =========================
# ADD ROOM
# =========================
@login_required(login_url='/admin/login/')
def add_room(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    if request.method == 'POST':

        room = Room.objects.create(
            room_number=request.POST['room_number'],
            room_type=request.POST['room_type'],

            hotel=request.POST.get('hotel'),   # ✅ TEXT FIELD
            location=request.POST.get('location'),  
            description=request.POST.get('description', ''),

            price_room_only=request.POST['price_room_only'],
            price_with_breakfast=request.POST['price_with_breakfast'],
            price_with_breakfast_dinner=request.POST['price_with_breakfast_dinner'],

            is_available=True
        )

        images = request.FILES.getlist('images')

        for img in images:
            RoomImage.objects.create(room=room, image=img)

        return redirect('/admin/rooms/')

    return render(request, 'admin/add_room.html')
# =========================
# EDIT ROOM
# =========================
@login_required(login_url='/admin/login/')
def edit_room(request, room_id):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    room = Room.objects.get(id=room_id)

    if request.method == 'POST':

        room.room_number = request.POST.get('room_number')
        room.room_type = request.POST.get('room_type')
        room.hotel = request.POST.get('hotel')
        room.location = request.POST.get('location')

        room.price_room_only = request.POST.get('price_room_only')
        room.price_with_breakfast = request.POST.get('price_with_breakfast')
        room.price_with_breakfast_dinner = request.POST.get('price_with_breakfast_dinner')

        room.description = request.POST.get('description')
        room.is_available = True if request.POST.get('is_available') else False

    

        room.save()

        images = request.FILES.getlist('images')

        for img in images:
            RoomImage.objects.create(
                room=room,
                image=img
            )

        return redirect('/admin/rooms/')

    return render(request, 'admin/edit_room.html', {
    'room': room,
    'images': room.images.all(),
    'hotels': Hotel.objects.all()
})

# =========================
# DELETE ROOM
# =========================
@login_required(login_url='/admin/login/')
def delete_room(request, room_id):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    room = Room.objects.get(id=room_id)

    if Booking.objects.filter(room=room).exists():
        return redirect('/admin/rooms/')

    room.delete()

    return redirect('/admin/rooms/')


# =========================
# BOOKINGS MANAGEMENT
# =========================
@login_required(login_url='/admin/login/')
def admin_bookings(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    bookings = Booking.objects.select_related('user', 'room')

    return render(request, 'admin/bookings.html', {
        'bookings': bookings
    })


# =========================
# PAYMENTS MANAGEMENT
# =========================
@login_required(login_url='/admin/login/')
def admin_payments(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    payments = Payment.objects.select_related('booking')

    return render(request, 'admin/payments.html', {
        'payments': payments
    })


# =========================
# TRIPS MANAGEMENT
# =========================
@login_required(login_url='/admin/login/')
def admin_trips(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    trips = Trip.objects.all()

    return render(request, 'admin/trips.html', {
        'trips': trips
    })


# =========================
# ADD TRIP
# =========================
@login_required(login_url='/admin/login/')
def add_trip(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    if request.method == 'POST':

        famous_place = request.POST.get('famous_place') == "True"

        Trip.objects.create(

            trip_name=request.POST['trip_name'],
            destination=request.POST['destination'],
            description=request.POST['description'],
            route=request.POST.get('route'),
            inclusions=request.POST.get('inclusions'),
            exclusions=request.POST.get('exclusions'),

            package_days=request.POST['package_days'],   # 🔥
            price_with_guide=request.POST['price_with_guide'],
            price_without_guide=request.POST['price_without_guide'],

            image=request.FILES.get('image'),

            famous_place=famous_place
        )

        return redirect('/admin/trips/')

    return render(request, 'admin/add_trip.html')


# =========================
# ADMIN LOGOUT
# =========================
def admin_logout(request):

    logout(request)
    request.session.flush()

    return redirect('/')

@login_required(login_url='/admin/login/')
def admin_trip_bookings(request):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    bookings = TripBooking.objects.select_related('user', 'trip')

    return render(request, 'admin/trip_bookings.html', {
        'bookings': bookings
    })
@login_required(login_url='/admin/login/')
def assign_staff(request, booking_id):

    booking = TripBooking.objects.get(id=booking_id)

    if request.method == 'POST':

        booking.assigned_staff = request.POST.get('staff')

        booking.save()

        return redirect('/admin/trip-bookings/')

    return render(request, 'admin/assign_staff.html', {
        'booking': booking
    })

@login_required(login_url='/admin/login/')
def edit_trip(request, trip_id):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    trip = get_object_or_404(Trip, id=trip_id)

    if request.method == 'POST':

        trip.trip_name = request.POST['trip_name']
        trip.destination = request.POST['destination']
        trip.description = request.POST.get('description', '')
        trip.price_with_guide = request.POST['price_with_guide']
        trip.price_without_guide = request.POST['price_without_guide']

        # ✅ same like room edit (optional image update)
        if request.FILES.get('image'):
            trip.image = request.FILES.get('image')

        trip.save()

        return redirect('admin_trips')

    return render(request, 'admin/edit_trip.html', {
        'trip': trip
    })

@login_required(login_url='/admin/login/')
def delete_trip(request, trip_id):

    if not request.user.is_staff:
        return redirect('/admin/login/')

    trip = get_object_or_404(Trip, id=trip_id)

    # 🔒 Prevent delete if bookings exist
    if TripBooking.objects.filter(trip=trip).exists():
        return redirect('admin_trips')

    trip.delete()

    return redirect('admin_trips')