from datetime import date, timedelta
import hashlib
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.contrib.auth.hashers import make_password
import uuid

from django.forms import ValidationError
from submit.managers import CustomUserManager
from django.utils.crypto import get_random_string
from django.utils import timezone



class CustomUser(AbstractUser):
    USER_CHOICES = (
        ('buyer', 'Buyer'),
        ('seller', 'Seller'),
        ('customs Agent', 'Customs Agent'),
    )

    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('GB', 'United Kingdom'),
        ('AU', 'Australia'),
        ('FR', 'France'),
        ('DE', 'Germany'),
        ('IN', 'India'),
        ('JP', 'Japan'),
        ('CN', 'China'),
        ('BR', 'Brazil'),
        ('IT', 'Italy'),
        ('ES', 'Spain'),
        ('NL', 'Netherlands'),
        ('SE', 'Sweden'),
        ('NO', 'Norway'),
        ('ZA', 'South Africa'),
        ('NG', 'Nigeria'),
        ('KE', 'Kenya'),
        ('EG', 'Egypt'),
        ('GH', 'Ghana'),
        # Add more countries as needed
    ]
    username = models.CharField(max_length=100, unique=True, default='none')
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    user_type = models.CharField(max_length=20, choices=USER_CHOICES, blank=True, null=True)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, blank=True, null=True)
    is_authorized = models.BooleanField(default=False)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    login_token = models.CharField(max_length=6, blank=True, null=True)


    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email



class VerificationDocument(models.Model):
    DOCUMENT_TYPES = [
        ('business_registration', 'Business Registration Certificate'),
        ('tin', 'Tax Identification Number (TIN)'),
        ('director_id', "Director's ID/Passport"),
        ('bank_account', 'Bank Account Letter/Swift Code'),
        ('company_logo', 'Company Logo/Stamp'),
        ('government_id', 'Government ID (Customs Agent)'),
        ('department_letter', 'Department Letter (Customs Agent)'),
        ('product_catalog', 'Product Catalog (Seller)'),
        ('seller_license', 'Seller License'),
        ('import_license', 'Import License (Buyer)'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(
        upload_to='verification_documents/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user.email}"
    
class PasswordResetRequest(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=32, default=get_random_string(32), editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD

    def send_reset_email(self):
        reset_link = f"http://localhost:8000/reset-password/{self.token}/"
        send_mail(
            'Password Reset Request',
            f'Click the following link to reset your password: {reset_link}',
            settings.DEFAULT_FROM_EMAIL,
            [self.email],
            fail_silently=False,
        )




class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)


    def __str__(self):
        return f'{self.user.email} Profile'
