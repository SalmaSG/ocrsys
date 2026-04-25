import random

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import (
    BookingForm,
    CaptchaLoginForm,
    ComplaintForm,
    DeliveryRequestForm,
    MachineForm,
    ProfileForm,
    RegistrationForm,
    ReviewForm,
)
from .models import Booking, Category, DeliveryRequest, Machine, Payment, Profile, Review


def role_for(user):
    if user.is_superuser:
        return Profile.ROLE_ADMIN
    if user.is_authenticated and hasattr(user, "profile"):
        return user.profile.role
    return ""


def home(request):
    machines = Machine.objects.filter(approved=True)
    categories = Category.objects.all()
    query = request.GET.get("q", "")
    category = request.GET.get("category", "")
    max_price = request.GET.get("max_price", "")
    available = request.GET.get("available", "")

    if query:
        machines = machines.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category:
        machines = machines.filter(category_id=category)
    if max_price:
        machines = machines.filter(daily_rate__lte=max_price)
    if available:
        machines = machines.filter(availability_status=Machine.STATUS_AVAILABLE)

    return render(
        request,
        "rentals/home.html",
        {
            "machines": machines,
            "categories": categories,
            "query": query,
            "selected_category": category,
            "max_price": max_price,
            "available": available,
        },
    )


class RentalLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CaptchaLoginForm
    redirect_authenticated_user = True

    def _set_captcha(self):
        left = random.randint(10, 40)
        right = random.randint(1, 20)
        self.request.session["login_captcha_question"] = f"{left} + {right}"
        self.request.session["login_captcha_answer"] = left + right

    def dispatch(self, request, *args, **kwargs):
        if request.method == "GET":
            self._set_captcha()
        return super().dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        if "login_captcha_question" not in self.request.session:
            self._set_captcha()
        return super().form_invalid(form)

    def form_valid(self, form):
        self.request.session.pop("login_captcha_question", None)
        self.request.session.pop("login_captcha_answer", None)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["captcha_question"] = self.request.session.get("login_captcha_question")
        return context


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.save()
            profile = user.profile
            profile.role = form.cleaned_data["role"]
            profile.phone = form.cleaned_data["phone"]
            profile.location = form.cleaned_data["location"]
            profile.otp_code = "123456"
            profile.is_otp_verified = True
            profile.save()
            login(request, user)
            messages.success(request, "Registration completed. Demo OTP verification is marked as verified.")
            return redirect("dashboard")
    else:
        form = RegistrationForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    user_role = role_for(request.user)
    if user_role == Profile.ROLE_OWNER:
        machines = Machine.objects.filter(owner=request.user)
        bookings = Booking.objects.filter(machine__owner=request.user)
    elif user_role == Profile.ROLE_ADMIN:
        machines = Machine.objects.all()
        bookings = Booking.objects.all()
    else:
        machines = Machine.objects.filter(approved=True)[:4]
        bookings = Booking.objects.filter(customer=request.user)

    revenue = bookings.aggregate(total=Sum("total_amount"))["total"] or 0
    return render(
        request,
        "rentals/dashboard.html",
        {
            "role": user_role,
            "machines": machines,
            "bookings": bookings[:10],
            "revenue": revenue,
            "machine_count": machines.count(),
            "booking_count": bookings.count(),
        },
    )


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            profile_obj = form.save()
            request.user.first_name = form.cleaned_data["first_name"]
            request.user.last_name = form.cleaned_data["last_name"]
            request.user.email = form.cleaned_data["email"]
            request.user.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(
            instance=request.user.profile,
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
            },
        )
    return render(request, "rentals/form.html", {"form": form, "title": "Profile Management", "button": "Save"})


def machine_detail(request, pk):
    machine = get_object_or_404(Machine, pk=pk, approved=True)
    reviews = machine.reviews.select_related("customer")
    return render(request, "rentals/machine_detail.html", {"machine": machine, "reviews": reviews})


@login_required
def machine_create(request):
    if role_for(request.user) not in (Profile.ROLE_OWNER, Profile.ROLE_ADMIN):
        messages.error(request, "Only equipment owners can list machines.")
        return redirect("dashboard")
    if request.method == "POST":
        form = MachineForm(request.POST, request.FILES)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.owner = request.user
            machine.approved = request.user.is_superuser
            machine.save()
            messages.success(request, "Machine submitted for admin approval.")
            return redirect("dashboard")
    else:
        form = MachineForm()
    return render(request, "rentals/form.html", {"form": form, "title": "Add Machine", "button": "Save Machine"})


@login_required
def machine_edit(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if machine.owner != request.user and not request.user.is_superuser:
        messages.error(request, "You cannot edit this machine.")
        return redirect("dashboard")
    if request.method == "POST":
        form = MachineForm(request.POST, request.FILES, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, "Machine updated.")
            return redirect("dashboard")
    else:
        form = MachineForm(instance=machine)
    return render(request, "rentals/form.html", {"form": form, "title": "Edit Machine", "button": "Update Machine"})


@login_required
def machine_delete(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    if machine.owner == request.user or request.user.is_superuser:
        machine.delete()
        messages.success(request, "Machine deleted.")
    return redirect("dashboard")


@login_required
def book_machine(request, pk):
    machine = get_object_or_404(Machine, pk=pk, approved=True)
    if not machine.is_available:
        messages.error(request, "This machine is not currently available.")
        return redirect("machine_detail", pk=machine.pk)
    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.machine = machine
            booking.status = Booking.STATUS_CONFIRMED
            booking.save()
            Payment.objects.create(booking=booking, amount=booking.total_amount)
            messages.success(request, "Booking confirmed. Continue to payment.")
            return redirect("payment", booking_id=booking.pk)
    else:
        form = BookingForm()
    return render(request, "rentals/form.html", {"form": form, "title": f"Book {machine.name}", "button": "Confirm Booking"})


@login_required
def payment(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.customer != request.user and not request.user.is_superuser:
        messages.error(request, "Payment is available only for the booking customer.")
        return redirect("dashboard")
    payment_obj = booking.payment
    if request.method == "POST":
        payment_obj.transaction_id = request.POST.get("transaction_id", f"TXN{booking.pk:05d}")
        payment_obj.mark_paid()
        messages.success(request, "Payment recorded and invoice generated.")
        return redirect("invoice", booking_id=booking.pk)
    return render(request, "rentals/payment.html", {"booking": booking, "payment": payment_obj})


@login_required
def invoice(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    return render(request, "rentals/invoice.html", {"booking": booking})


@login_required
def delivery_request(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.method == "POST":
        form = DeliveryRequestForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.booking = booking
            delivery.save()
            messages.success(request, "Delivery request submitted.")
            return redirect("dashboard")
    else:
        form = DeliveryRequestForm()
    return render(request, "rentals/form.html", {"form": form, "title": "Delivery Request", "button": "Request Delivery"})


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if booking.customer == request.user or request.user.is_superuser:
        booking.status = Booking.STATUS_CANCELLED
        booking.save()
        if hasattr(booking, "payment") and booking.payment.status == Payment.STATUS_PAID:
            booking.payment.status = Payment.STATUS_REFUNDED
            booking.payment.save()
        messages.success(request, "Booking cancelled. Refund status updated where applicable.")
    return redirect("dashboard")


@login_required
def review_machine(request, pk):
    machine = get_object_or_404(Machine, pk=pk)
    review, _ = Review.objects.get_or_create(customer=request.user, machine=machine)
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review submitted.")
            return redirect("machine_detail", pk=pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, "rentals/form.html", {"form": form, "title": "Review & Feedback", "button": "Submit Review"})


@login_required
def complaint(request, booking_id):
    booking = get_object_or_404(Booking, pk=booking_id)
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.booking = booking
            item.save()
            messages.success(request, "Complaint submitted.")
            return redirect("dashboard")
    else:
        form = ComplaintForm()
    return render(request, "rentals/form.html", {"form": form, "title": "Complaint Handling", "button": "Submit"})


@login_required
def reports(request):
    if role_for(request.user) == Profile.ROLE_OWNER:
        bookings = Booking.objects.filter(machine__owner=request.user)
        machines = Machine.objects.filter(owner=request.user)
    elif role_for(request.user) == Profile.ROLE_ADMIN:
        bookings = Booking.objects.all()
        machines = Machine.objects.all()
    else:
        bookings = Booking.objects.filter(customer=request.user)
        machines = Machine.objects.filter(bookings__customer=request.user).distinct()

    usage = machines.annotate(total_bookings=Count("bookings")).order_by("-total_bookings")
    return render(
        request,
        "rentals/reports.html",
        {
            "bookings": bookings,
            "usage": usage,
            "revenue": bookings.aggregate(total=Sum("total_amount"))["total"] or 0,
        },
    )

# Create your views here.
