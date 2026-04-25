from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone


class Profile(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_OWNER = "owner"
    ROLE_CUSTOMER = "customer"
    ROLE_CHOICES = (
        (ROLE_ADMIN, "Admin"),
        (ROLE_OWNER, "Equipment Owner"),
        (ROLE_CUSTOMER, "Customer"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=160, blank=True)
    otp_code = models.CharField(max_length=8, blank=True)
    is_otp_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Machine(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_UNAVAILABLE = "unavailable"
    STATUS_MAINTENANCE = "maintenance"
    STATUS_CHOICES = (
        (STATUS_AVAILABLE, "Available"),
        (STATUS_UNAVAILABLE, "Unavailable"),
        (STATUS_MAINTENANCE, "Under Maintenance"),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="machines")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="machines")
    name = models.CharField(max_length=120)
    description = models.TextField()
    specifications = models.TextField(blank=True)
    image = models.ImageField(upload_to="machines/", blank=True)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    daily_rate = models.DecimalField(max_digits=10, decimal_places=2)
    weekly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    availability_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def is_available(self):
        return self.approved and self.availability_status == self.STATUS_AVAILABLE


class Booking(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELLED = "cancelled"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_COMPLETED, "Completed"),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.machine} for {self.customer}"

    @property
    def rental_days(self):
        return max((self.end_date - self.start_date).days + 1, 1)

    def calculate_total(self):
        return self.machine.daily_rate * self.rental_days

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)


class Payment(models.Model):
    STATUS_PENDING = "pending"
    STATUS_PAID = "paid"
    STATUS_REFUNDED = "refunded"
    STATUS_FAILED = "failed"
    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_PAID, "Paid"),
        (STATUS_REFUNDED, "Refunded"),
        (STATUS_FAILED, "Failed"),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    transaction_id = models.CharField(max_length=80, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Payment {self.status} for booking #{self.booking_id}"

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.paid_at = timezone.now()
        self.save()


class DeliveryRequest(models.Model):
    STATUS_REQUESTED = "requested"
    STATUS_ACCEPTED = "accepted"
    STATUS_IN_USE = "in_use"
    STATUS_RETURNED = "returned"
    STATUS_CHOICES = (
        (STATUS_REQUESTED, "Requested"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_IN_USE, "In Use"),
        (STATUS_RETURNED, "Returned"),
    )

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="delivery")
    pickup_location = models.CharField(max_length=180)
    drop_location = models.CharField(max_length=180)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_REQUESTED)
    owner_response = models.TextField(blank=True)

    def __str__(self):
        return f"Delivery for booking #{self.booking_id}"


class Complaint(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="complaints")
    message = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Complaint #{self.pk}"


class Review(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("customer", "machine")

    def __str__(self):
        return f"{self.rating}/5 for {self.machine}"

# Create your models here.
