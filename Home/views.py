# Home/views.py - COMPLETE WORKING VERSION
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
import random
from .models import EmailOTP
from django.core.mail import EmailMessage
from Payment.models import Course
from Home.models import SuperMentor

# Password reset imports
from django.contrib.auth.views import PasswordResetView
from django.contrib.auth.forms import PasswordResetForm
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect

# ==================== BASIC VIEWS ====================

def home_view(request):
    super_mentors = SuperMentor.objects.all()
    return render(request, "index.html", {
        "super_mentors": super_mentors
    })

def courses_view(request):
    courses = Course.objects.all()
    return render(request, "course.html", {"courses": courses})

def contact_view(request):
    if request.method == "POST":
        # Your contact form logic here
        messages.success(request, 'Your message has been sent!')
        return redirect('contact')
    
    return render(request, 'contact.html')

def terms_view(request):
    return render(request, 'terms.html')

# ==================== REGISTRATION VIEWS ====================

def send_otp_email(email, otp, first_name=None):
    """Send OTP email for registration"""
    welcome_name = first_name if first_name else "User"
    email_message = EmailMessage(
        subject="Welcome to Nirvant! Your OTP Verification Code",
        body=f"Hello {welcome_name},\n\n"
             f"Welcome to Nirvant Learning Platform!\n\n"
             f"Your OTP is: {otp}\n"
             f"This OTP will expire in 5 minutes.\n\n"
             f"Happy Learning!\n\n"
             f"— The Nirvant Team",
        to=[email]
    )
    email_message.send()

def register(request):
    """User registration with OTP"""
    context = {}
    
    if request.method == "POST":
        action = request.POST.get("action")
        
        # REGISTER ACTION
        if action == "register":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            age = request.POST.get("age")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            
            # Validation
            if password1 != password2:
                messages.error(request, "Passwords do not match!")
                return render(request, "register_otp.html")
            
            if len(password1) < 8:
                messages.error(request, "Password must be at least 8 characters!")
                return render(request, "register_otp.html")
            
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists!")
                return render(request, "register_otp.html")
            
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered!")
                return render(request, "register_otp.html")
            
            # Delete old OTP if exists
            EmailOTP.objects.filter(email=email).delete()
            
            # Generate OTP
            otp = str(random.randint(100000, 999999))
            
            # Save to EmailOTP model
            email_otp_obj = EmailOTP.objects.create(
                user=None,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,
                otp=otp
            )
            
            # Send OTP
            send_otp_email(email, otp, first_name)
            messages.success(request, "OTP sent to your email!")
            
            # Save ID in session
            request.session["emailotp_id"] = email_otp_obj.id
            context = {"email": email, "show_otp": True}
        
        # VERIFY OTP ACTION
        elif action == "verify_otp":
            entered_otp = request.POST.get("otp")
            emailotp_id = request.session.get("emailotp_id")
            
            if not emailotp_id:
                messages.error(request, "Session expired! Please register again.")
                return redirect("register")
            
            try:
                email_otp_obj = EmailOTP.objects.get(id=emailotp_id)
            except EmailOTP.DoesNotExist:
                messages.error(request, "Invalid session! Please register again.")
                return redirect("register")
            
            if email_otp_obj.is_expired():
                email_otp_obj.delete()
                messages.error(request, "OTP expired! Please register again.")
                return redirect("register")
            
            if entered_otp != email_otp_obj.otp:
                messages.error(request, "Incorrect OTP!")
                return render(request, "register_otp.html", {
                    "email": email_otp_obj.email,
                    "show_otp": True
                })
            
            # CREATE USER
            user = User.objects.create_user(
                username=email_otp_obj.username,
                email=email_otp_obj.email,
                password=email_otp_obj.password,
                first_name=email_otp_obj.first_name,
                last_name=email_otp_obj.last_name
            )
            user.save()
            
            # Link user to EmailOTP
            email_otp_obj.user = user
            email_otp_obj.save()
            
            # Clear session
            del request.session["emailotp_id"]
            
            messages.success(request, "Registration successful! Please login.")
            return redirect("login")
        
        # RESEND OTP ACTION
        elif action == "resend_otp":
            emailotp_id = request.session.get("emailotp_id")
            if not emailotp_id:
                messages.error(request, "Session expired! Please register again.")
                return redirect("register")
            
            email_otp_obj = EmailOTP.objects.get(id=emailotp_id)
            new_otp = str(random.randint(100000, 999999))
            email_otp_obj.otp = new_otp
            email_otp_obj.created_at = timezone.now()
            email_otp_obj.save()
            
            send_otp_email(email_otp_obj.email, new_otp)
            messages.success(request, "New OTP sent!")
            
            context = {"email": email_otp_obj.email, "show_otp": True}
    
    return render(request, "register_otp.html", context)

# ==================== LOGIN/LOGOUT VIEWS ====================

def login_view(request):
    """User login"""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(
            request,
            username=username,
            password=password
        )
        
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, "login.html")

@login_required(login_url="login")
def dashboard(request):
    """User dashboard"""
    context = {
        "user": request.user
    }
    return render(request, "dashboard.html", context)

@login_required(login_url="login")
def logout_view(request):
    """User logout"""
    logout(request)
    return redirect("home")

# ==================== CUSTOM PASSWORD RESET VIEW ====================

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = '/password-reset/done/'
    
    def form_valid(self, form):
        opts = {
            'use_https': self.request.is_secure(),
            'token_generator': default_token_generator,
            'from_email': 'Nirvant <nirvant.trgyy@gmail.com>',
            'email_template_name': self.email_template_name,
            'subject_template_name': self.subject_template_name,
            'request': self.request,
            'html_email_template_name': self.email_template_name,
            'extra_email_context': None,
        }
        form.save(**opts)
        return HttpResponseRedirect(self.get_success_url())