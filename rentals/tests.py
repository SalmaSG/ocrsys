from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Machine, Profile


class RentalSmokeTests(TestCase):
    def setUp(self):
        User.objects.filter(username="test_owner").delete()
        self.owner = User.objects.create_user(username="test_owner", password="owner123")
        self.owner.profile.role = Profile.ROLE_OWNER
        self.owner.profile.save()
        category, _ = Category.objects.get_or_create(name="Drills")
        self.machine = Machine.objects.create(
            owner=self.owner,
            category=category,
            name="Hammer Drill",
            description="Concrete drilling machine",
            daily_rate=1200,
            approved=True,
        )

    def test_home_and_detail_render(self):
        self.assertEqual(self.client.get(reverse("home")).status_code, 200)
        self.assertEqual(self.client.get(reverse("machine_detail", args=[self.machine.pk])).status_code, 200)

    def test_customer_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_login_requires_valid_captcha(self):
        self.client.get(reverse("login"))
        session = self.client.session
        expected = session["login_captcha_answer"]

        bad_response = self.client.post(
            reverse("login"),
            {"username": "test_owner", "password": "owner123", "captcha_answer": expected + 1},
        )
        self.assertEqual(bad_response.status_code, 200)
        self.assertContains(bad_response, "Invalid captcha code")

        good_response = self.client.post(
            reverse("login"),
            {"username": "test_owner", "password": "owner123", "captcha_answer": expected},
        )
        self.assertEqual(good_response.status_code, 302)

# Create your tests here.
