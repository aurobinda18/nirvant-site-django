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
from dashboard.models import StudentProfile

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
            # IMPORTANT: Add this code RIGHT AFTER user.save()
            from dashboard.models import Mentor
            
            # Get user_type
            user_type = request.POST.get('user_type', 'student').strip()
            company_id = request.POST.get('company_id', '').strip()
            
            # IF USER IS MENTOR, CREATE MENTOR RECORD
            if user_type == 'mentor' and company_id:
                mentor_record = Mentor.objects.create(
                    name=email_otp_obj.first_name + " " + email_otp_obj.last_name,
                    qualification="NEET Mentor",
                    specialization="Physics",
                    company_id=company_id,
                    user=user  # Link to User
                )
                
                print(f"Created mentor record for {user.username}")
            # Get user_type from POST, default to 'student'
            user_type = request.POST.get('user_type', 'student').strip()
            company_id = request.POST.get('company_id', '').strip()
            
            # Save user type and company_id to StudentProfile
            from dashboard.models import StudentProfile
            profile, created = StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': user_type,
                    'company_id': company_id
                }
            )
            
            # If student, try to find and assign mentor
            if profile.user_type == 'student':
                if company_id:
                    try:
                        # Find mentor with this company_id
                        from dashboard.models import Mentor
                        mentor = Mentor.objects.get(company_id=company_id)
                        profile.mentor = mentor  # Connect student to mentor
                        profile.save()
                        print(f"DEBUG: Student {user.username} assigned to mentor {mentor.name}")
                    except Mentor.DoesNotExist:
                        # Mentor not found - student entered wrong ID
                        print(f"DEBUG: Mentor with company_id {company_id} not found")
                        pass
                    
            # Update existing profile if needed
            if not created:
                profile.user_type = user_type
                profile.company_id = company_id
                profile.save()
            
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
        login_type = request.POST.get("login_type", "student")
        company_id = request.POST.get("company_id", "")
        
        print(f"DEBUG LOGIN: username={username}, login_type={login_type}, company_id={company_id}")
        
        user = authenticate(
            request,
            username=username,
            password=password
        )
        
        if user is not None:
            try:
                profile = user.studentprofile
                print(f"DEBUG PROFILE: user_type={profile.user_type}, company_id_in_db={profile.company_id}")
                
                if profile.user_type == 'mentor':
                    print(f"DEBUG: User is mentor, checking company_id")
                    if company_id == profile.company_id:
                        print(f"DEBUG: Company ID matches! Redirecting to mentor_dashboard")
                        login(request, user)
                        messages.success(request, "Mentor login successful!")
                        return redirect("mentor_dashboard")
                    else:
                        print(f"DEBUG: Company ID mismatch: entered={company_id}, expected={profile.company_id}")
                        messages.error(request, f"Please enter correct Company ID for mentor account")
                        return render(request, "login.html", {
                            'show_mentor_tab': True,
                            'username': username
                        })
                else:
                    print(f"DEBUG: User is student, redirecting to dashboard")
                    login(request, user)
                    messages.success(request, "Login successful!")
                    return redirect("dashboard")
                    
            except Exception as e:
                print(f"DEBUG ERROR: {e}")
                messages.error(request, "Profile not found. Please register first.")
                return render(request, "login.html")
        else:
            messages.error(request, "Invalid username or password!")
    
    return render(request, "login.html")

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get user profile
    from dashboard.models import StudentProfile
    profile, created = StudentProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'attempt_year': 2025,
            'neet_exam_date': '2025-05-05',
            'batch_enrolled': 'NEET 2025 Batch A',
        }
    )
    
    # ADD THESE 3 LINES HERE ↓↓↓
    # Get student's notices
    student_notices = profile.get_mentor_notices()
    unread_notices_count = len(student_notices)
    
    # Get active PYQ PDFs
    from dashboard.models import PYQPDF
    pyq_pdfs = PYQPDF.objects.filter(is_active=True)
    
    # Calculate counts per subject
    physics_count = pyq_pdfs.filter(subject='Physics').count()
    chemistry_count = pyq_pdfs.filter(subject='Chemistry').count()
    biology_count = pyq_pdfs.filter(subject='Biology').count()
    
    context = {
        'profile': profile,
        'user': request.user,
        'pyq_pdfs': pyq_pdfs,
        'physics_count': physics_count,
        'chemistry_count': chemistry_count,
        'biology_count': biology_count,
        'total_pyq': physics_count + chemistry_count + biology_count,
        # ADD THESE 2 LINES TO CONTEXT ↓↓↓
        'notices': student_notices[:3],  # Show only 3 latest notices
        'unread_notices_count': unread_notices_count,
    }
    
    return render(request, 'dashboard.html', context)

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

# Add this function to your Home/views.py file
# You can add it after the courses_view function

def checkout_view(request):
    """Checkout page view"""
    # Get course details from URL parameters
    course_id = request.GET.get('course_id')
    
    # Default values
    plan_type = request.GET.get('plan_type', 'Free Trial')
    duration = request.GET.get('duration', '3 days')
    price = request.GET.get('price', '0')
    original_price = request.GET.get('original_price', '')
    
    # If course_id is provided, try to get the course details
    if course_id:
        try:
            from Payment.models import Course
            course = Course.objects.get(id=course_id)
            plan_type = course.plan_type
            duration = course.duration_text
            price = str(course.course_price)
            if course.original_price:
                original_price = str(course.original_price)
        except Course.DoesNotExist:
            pass
    
    context = {
        'plan_type': plan_type,
        'duration': duration,
        'price': price,
        'original_price': original_price,
    }
    
    return render(request, "checkout.html", context)

