from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Booking, Complaint, DeliveryRequest, Machine, Profile, Review


class RegistrationForm(UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES[1:])
    phone = forms.CharField(max_length=20)
    location = forms.CharField(max_length=160)

    class Meta:
        model = User
        fields = ("username", "email", "role", "phone", "location", "password1", "password2")


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=80, required=False)
    last_name = forms.CharField(max_length=80, required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = Profile
        fields = ("phone", "location")


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = (
            "category",
            "name",
            "description",
            "specifications",
            "image",
            "hourly_rate",
            "daily_rate",
            "weekly_rate",
            "availability_status",
        )


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("start_date", "end_date")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        start_date = cleaned.get("start_date")
        end_date = cleaned.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date must be after start date.")
        return cleaned


class DeliveryRequestForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ("pickup_location", "drop_location")


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {"rating": forms.NumberInput(attrs={"min": 1, "max": 5})}


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("message",)
