from django.contrib import admin

from .models import Booking, Category, Complaint, DeliveryRequest, Machine, Payment, Profile, Review


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "phone", "location", "is_otp_verified")
    list_filter = ("role", "is_otp_verified")
    search_fields = ("user__username", "phone", "location")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "category", "daily_rate", "availability_status", "approved")
    list_filter = ("category", "availability_status", "approved")
    search_fields = ("name", "owner__username")
    list_editable = ("approved", "availability_status")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("machine", "customer", "start_date", "end_date", "status", "total_amount")
    list_filter = ("status", "start_date")
    search_fields = ("machine__name", "customer__username")


admin.site.register(Payment)
admin.site.register(DeliveryRequest)
admin.site.register(Complaint)
admin.site.register(Review)

# Register your models here.
