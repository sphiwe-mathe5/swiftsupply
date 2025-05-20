# collects additional info name etc
from allauth.account.forms import SignupForm
from django import forms

class CustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=100, label='Full Name')

    def save(self, request):
        user = super().save(request)
        user.full_name = self.cleaned_data['full_name']
        user.save()
        return user
