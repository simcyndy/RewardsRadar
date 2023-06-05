from django import forms
from .models import Customer, RewardTier


class CustomerRegistrationForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email']  


class RewardTierForm(forms.ModelForm):
    class Meta:
        model = RewardTier
        fields = ['name', 'benefits', 'points_required']

class SubscriptionForm(forms.Form):
    reward_tier = forms.ModelChoiceField(queryset=RewardTier.objects.all())


class AddPointsForm(forms.Form):
    points = forms.IntegerField(min_value=1)

