from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('rooms/', views.admin_rooms, name='admin_rooms'),
    path('add-room/', views.add_room, name='add_room'),
    path('trip-bookings/', views.admin_trip_bookings, name='admin_trip_bookings'),
    path('assign-staff/<int:booking_id>/', views.assign_staff, name='assign_staff'),
    path('bookings/', views.admin_bookings, name='admin_bookings'),
    path('payments/', views.admin_payments, name='admin_payments'),
    path('rooms/<int:room_id>/edit/', views.edit_room, name='edit_room'),
    path('rooms/<int:room_id>/delete/', views.delete_room, name='delete_room'),
    path('trips/', views.admin_trips, name='admin_trips'),
    path('add-trip/', views.add_trip, name='add_trip'),
    path('edit-trip/<int:trip_id>/', views.edit_trip, name='edit_trip'),
    path('delete-trip/<int:trip_id>/', views.delete_trip, name='delete_trip'),
]
