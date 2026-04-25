from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("accounts/login/", views.RentalLoginView.as_view(), name="login"),
    path("accounts/logout/", LogoutView.as_view(next_page="home"), name="logout"),
    path("accounts/register/", views.register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),
    path("machines/add/", views.machine_create, name="machine_create"),
    path("machines/<int:pk>/", views.machine_detail, name="machine_detail"),
    path("machines/<int:pk>/edit/", views.machine_edit, name="machine_edit"),
    path("machines/<int:pk>/delete/", views.machine_delete, name="machine_delete"),
    path("machines/<int:pk>/book/", views.book_machine, name="book_machine"),
    path("machines/<int:pk>/review/", views.review_machine, name="review_machine"),
    path("bookings/<int:booking_id>/payment/", views.payment, name="payment"),
    path("bookings/<int:booking_id>/invoice/", views.invoice, name="invoice"),
    path("bookings/<int:booking_id>/delivery/", views.delivery_request, name="delivery_request"),
    path("bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("bookings/<int:booking_id>/complaint/", views.complaint, name="complaint"),
    path("reports/", views.reports, name="reports"),
]
