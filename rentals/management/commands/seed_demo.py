from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rentals.models import Category, Machine, Profile


class Command(BaseCommand):
    help = "Create demo users, categories, and approved machines."

    def handle(self, *args, **options):
        owner, _ = User.objects.get_or_create(username="owner", defaults={"email": "owner@example.com"})
        owner.set_password("owner123")
        owner.save()
        owner.profile.role = Profile.ROLE_OWNER
        owner.profile.phone = "9876543210"
        owner.profile.location = "Kochi"
        owner.profile.is_otp_verified = True
        owner.profile.save()

        customer, _ = User.objects.get_or_create(username="customer", defaults={"email": "customer@example.com"})
        customer.set_password("customer123")
        customer.save()
        customer.profile.role = Profile.ROLE_CUSTOMER
        customer.profile.phone = "9123456780"
        customer.profile.location = "Ernakulam"
        customer.profile.is_otp_verified = True
        customer.profile.save()

        samples = [
            ("Mowers", "Cuttings", "Heavy duty ride-on mower for site clearing.", "42 inch deck, petrol engine", 450, 2200, 12500),
            ("Hammer Drills", "Drills", "Rotary hammer drill for concrete and masonry jobs.", "1500 W, SDS-max chuck", 280, 1400, 7800),
            ("Jackhammers", "Breakers", "Electric breaker for demolition and road repair.", "29 kg, anti-vibration handle", 350, 1800, 9800),
            ("Sewer Snake", "Cleaning", "Drain cleaning machine for sewer and pipeline clearing.", "75 ft cable, wheel mounted", 300, 1600, 8700),
            ("Concrete Cutter", "Cuttings", "Precision cutter for concrete slabs and road surfaces.", "14 inch blade, water feed", 500, 2600, 14500),
            ("Mini Excavator", "Earthmoving", "Compact excavator for trenching and loading.", "0.8 ton, diesel engine", 900, 5200, 29500),
        ]

        for name, category_name, description, specifications, hourly, daily, weekly in samples:
            category, _ = Category.objects.get_or_create(name=category_name)
            Machine.objects.update_or_create(
                name=name,
                owner=owner,
                defaults={
                    "category": category,
                    "description": description,
                    "specifications": specifications,
                    "hourly_rate": Decimal(hourly),
                    "daily_rate": Decimal(daily),
                    "weekly_rate": Decimal(weekly),
                    "availability_status": Machine.STATUS_AVAILABLE,
                    "approved": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo data ready. Users: owner/owner123 and customer/customer123"))
