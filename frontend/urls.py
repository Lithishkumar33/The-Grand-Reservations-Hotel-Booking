from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('home/', views.home, name='home'),

    path('rooms/', views.rooms, name='rooms'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),

    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('invoice/<int:booking_id>/', views.invoice, name='invoice'),

    path('trips/', views.trips_dashboard, name='trips'),
    path('trip/<int:trip_id>/', views.trip_detail, name='trip_detail'),
    path('my-trips/', views.my_trips, name='my_trips'),

    path('pay/<int:booking_id>/', views.pay_now, name='pay_now'),
    path('pay-trip/<int:booking_id>/', views.pay_trip, name='pay_trip'),
    path('payment-success/<int:booking_id>/', views.payment_success, name='payment_success'),
    path('trip-payment-success/<int:booking_id>/', views.trip_payment_success, name='trip_payment_success'),

    path('trip-invoice/<int:booking_id>/', views.trip_invoice, name='trip_invoice'),
    path('trip-invoice-pdf/<int:booking_id>/', views.trip_invoice_pdf, name='trip_invoice_pdf'),

    path('cancel-room/<int:booking_id>/', views.cancel_room_booking, name='cancel_room'),
    path('cancel-trip/<int:booking_id>/', views.cancel_trip_booking, name='cancel_trip'),
    path('room-invoice-pdf/<int:booking_id>/', views.room_invoice_pdf, name='room_invoice_pdf'),
    path('quick-enquiry/', views.quick_enquiry, name='quick_enquiry'),
    path('explore/', views.explore, name='explore'),
]