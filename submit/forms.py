from datetime import date, datetime, timedelta
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import  Profile, CustomUser
from django import forms

from submit import models



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=100, required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'password1', 'password2']  # Removed username

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if len(password1) < 8:
            raise ValidationError(
                "Password must be at least 8 characters long.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "The two password fields must match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.company_name = self.cleaned_data['company_name']
        user.country = self.cleaned_data['country']
        user.phone = self.cleaned_data['phone']
        user.user_type = self.cleaned_data['user_type']
        

        if commit:
            user.save()
            Profile.objects.update_or_create(user=user, defaults={})
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    company_name = forms.CharField()
    country = forms.CharField()
    phone = forms.CharField()
    user_type = forms.CharField()



    class Meta:
        model = User
        fields = ['email', 'company_name', 'country', 'user_type', 'phone']



from .models import VerificationDocument

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = VerificationDocument
        fields = ['document_type', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }

class VerificationForm(forms.Form):
    # Required for all users
    business_registration = forms.FileField(
        label="Business Registration Certificate",
        required=True,
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    tin_document = forms.FileField(
        label="Tax Identification Number (TIN)",
        required=True,
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    director_id = forms.FileField(
        label="Director's ID/Passport",
        required=True,
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )

    # Optional for all users
    bank_account = forms.FileField(
        label="Bank Account Letter/Swift Code",
        required=False,
        widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
    )
    company_logo = forms.FileField(
        label="Company Logo/Stamp",
        required=False,
        widget=forms.FileInput(attrs={'accept': '.jpg,.jpeg,.png'})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add role-specific fields based on user type
        if self.user and self.user.user_type == 'customs Agent':
            self.fields['government_id'] = forms.FileField(
                label="Government ID",
                required=True,
                widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
            )
            self.fields['department_letter'] = forms.FileField(
                label="Department Letter",
                required=True,
                widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
            )

        elif self.user and self.user.user_type == 'seller':
            self.fields['product_catalog'] = forms.FileField(
                label="Product Catalog",
                required=True,
                widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png,.xls,.xlsx'})
            )
            self.fields['seller_license'] = forms.FileField(
                label="Seller License (if applicable)",
                required=False,
                widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
            )

        elif self.user and self.user.user_type == 'buyer':
            self.fields['import_license'] = forms.FileField(
                label="Import License (if applicable)",
                required=False,
                widget=forms.FileInput(attrs={'accept': '.pdf,.jpg,.jpeg,.png'})
            )