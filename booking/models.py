from django.db import models
from django.contrib.auth.models import User

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)  # Goa / Ooty
    image = models.ImageField(upload_to='hotels/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.location})"
# ================= ROOMS =================
class Room(models.Model):
    ROOM_TYPE_CHOICES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Deluxe', 'Deluxe'),
        ('Suite', 'Suite'),
    ]

    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES)

    #  NEW PRICING (PER DAY)
    price_room_only = models.DecimalField(max_digits=8, decimal_places=2)
    price_with_breakfast = models.DecimalField(max_digits=8, decimal_places=2)
    price_with_breakfast_dinner = models.DecimalField(max_digits=8, decimal_places=2)

    #  OPTIONAL 
    hotel = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Room {self.room_number}"


# ================= ROOM IMAGES =================
class RoomImage(models.Model):
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='images'
    )

    image = models.ImageField(upload_to='rooms/')

    def __str__(self):
        return f"Image for Room {self.room.room_number}"


# ================= ROOM BOOKING =================
class Booking(models.Model):

    PACKAGE_CHOICES = [
        ('Room Only', 'Room Only'),
        ('Room + Breakfast', 'Room + Breakfast'),
        ('Room + Breakfast + Dinner', 'Room + Breakfast + Dinner'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()

    package = models.CharField(max_length=50, choices=PACKAGE_CHOICES)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    booking_date = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Paid', 'Paid'),
            ('Cancelled', 'Cancelled'),
        ],
        default='Pending'
    )

    def __str__(self):
        return f"Booking #{self.id} - {self.room.room_number}"


# ================= PAYMENTS =================
class Payment(models.Model):

    PAYMENT_METHODS = [
        ('UPI', 'UPI'),
        ('Card', 'Card'),
        ('Cash', 'Cash'),
        ('Online', 'Online'),  # ✅ Added because your view uses it
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)

    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS
    )

    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)

    paid_on = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, default='Paid')

    def __str__(self):
        return f"Payment #{self.id}"
    



# =========================================================
# ================= TRIP MODULE ============================
# =========================================================

class Trip(models.Model):

    trip_name = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    description = models.TextField()

    image = models.ImageField(upload_to='trips/', blank=True, null=True)
    route = models.TextField(blank=True, null=True)
    inclusions = models.TextField(blank=True, null=True)
    exclusions = models.TextField(blank=True, null=True)

    # ✅ PACKAGE DAYS
    package_days = models.IntegerField()
    price_with_guide = models.DecimalField(max_digits=10, decimal_places=2)
    price_without_guide = models.DecimalField(max_digits=10, decimal_places=2)

    famous_place = models.BooleanField(default=False)

    def __str__(self):
        return self.trip_name


# ================= TRIP BOOKING =================
class TripBooking(models.Model):

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)

    guide_option = models.CharField(max_length=20)

    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    assigned_staff = models.CharField(max_length=100, blank=True, null=True)

    booking_date = models.DateTimeField(auto_now_add=True)

    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"Trip Booking #{self.id}"