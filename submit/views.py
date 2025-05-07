from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import VerificationForm, DocumentUploadForm
from .forms import UserRegisterForm, UserUpdateForm
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest, VerificationDocument
from django.utils.crypto import get_random_string
from django.contrib.auth.models import User


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

def signup_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        phone = request.POST['phone']
        user_type = request.POST['user_type']
        country = request.POST['country']
        company_name = request.POST['company_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match. Please try again.")
            return redirect('signup')
        
        # Check if the user already exists with this email
        if  CustomUser.objects.filter(email=email).exists():
            messages.error(request, "An account with this email already exists. Please log in or use a different email.")
            return redirect('signup')
        
        # Validate password according to Django's rules
        try:
            validate_password(password)  # This will raise a ValidationError if the password is weak
        except ValidationError as e:
            messages.error(request, f"Password is too weak: {', '.join(e.messages)}")
            return redirect('signup')

        try:
            # Create the user after passing validation checks
            user = CustomUser.objects.create_user(
                username=email,
                email=email,
                phone=phone,
                user_type=user_type,
                country=country,
                company_name=company_name,
                password=password,
            )
            login(request, user, backend='submit.backends.EmailBackend')
            messages.success(request, 'Signup successful!')
            return redirect('index')
        
        except IntegrityError:
            # This shouldn't happen now because we check for existing email earlier
            messages.error(request, 'An account with this email already exists. Please log in or use a different email.')
            return redirect('signup')  

    return render(request, 'submit/register.html', {'COUNTRY_CHOICES': CustomUser.COUNTRY_CHOICES, 'USER_CHOICES': CustomUser.USER_CHOICES})

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        print(f"Attempting to log in with email: {email}")  

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)  # Add this line to log in the user
            return redirect('index')
        else:
            print("Authentication failed")  
            messages.error(request, 'Invalid credentials')
    return render(request, 'submit/login.html')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        user = CustomUser.objects.filter(email=email).first()

        if user:
            token = get_random_string(32)
            reset_request = PasswordResetRequest.objects.create(user=user, email=email, token=token)
            reset_request.send_reset_email()
            messages.success(request, 'Reset link sent to your email.')
        else:
            messages.error(request, 'Email not found.')

    return render(request, 'submit/login.html')


def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()

    if not reset_request or not reset_request.is_valid():
        messages.error(request, 'Invalid or expired reset link')
        return redirect('index')

    if request.method == 'POST':
        new_password = request.POST['new_password']
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        messages.success(request, 'Password reset successful')
        return redirect('login')

    return render(request, 'submit/reset_password.html', {'token': token})



def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()

    if not reset_request or not reset_request.is_valid():
        messages.error(request, 'Invalid or expired reset link')
        return redirect('index')

    if request.method == 'POST':
        new_password = request.POST['new_password']
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        messages.success(request, 'Password reset successful')
        return redirect('login')

    return render(request, 'submit/reset_password.html', {'token': token})
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Your account has been created! You are now able to log in')
            return redirect('index')
    else:
        form = UserRegisterForm()
    return render(request, 'submit/register.html', {'form': form})

# views.py
# views.py
@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)

        if u_form.is_valid():
            u_form.save()
            messages.success(request, f'updated!')
            return redirect('profile')

    else:
        u_form = UserUpdateForm(instance=request.user)

    # Fetch saved reflections
    
    # Fetch user's own reflections
    

    context = {
        'u_form': u_form,
        
    }

    return render(request, 'submit/profile.html', context)

    

@login_required
def verification_request(request):
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Save required documents for all users
            VerificationDocument.objects.create(
                user=request.user,
                document_type='business_registration',
                file=request.FILES['business_registration']
            )
            
            VerificationDocument.objects.create(
                user=request.user,
                document_type='tin',
                file=request.FILES['tin_document']
            )
            
            VerificationDocument.objects.create(
                user=request.user,
                document_type='director_id',
                file=request.FILES['director_id']
            )

            # Save optional documents if provided
            if form.cleaned_data.get('bank_account'):
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='bank_account',
                    file=request.FILES['bank_account']
                )

            if form.cleaned_data.get('company_logo'):
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='company_logo',
                    file=request.FILES['company_logo']
                )

            # Handle role-specific documents
            if request.user.user_type == 'customs Agent':
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='government_id',
                    file=request.FILES['government_id']
                )
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='department_letter',
                    file=request.FILES['department_letter']
                )

            elif request.user.user_type == 'seller':
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='product_catalog',
                    file=request.FILES['product_catalog']
                )
                if form.cleaned_data.get('seller_license'):
                    VerificationDocument.objects.create(
                        user=request.user,
                        document_type='seller_license',
                        file=request.FILES['seller_license']
                    )

            elif request.user.user_type == 'buyer' and form.cleaned_data.get('import_license'):
                VerificationDocument.objects.create(
                    user=request.user,
                    document_type='import_license',
                    file=request.FILES['import_license']
                )

            messages.success(request, "Your verification documents have been submitted for review.")
            return redirect('verification_status')
    else:
        form = VerificationForm(user=request.user)

    return render(request, 'submit/verification.html', {'form': form})
