# Home/views.py
from django.shortcuts import render, redirect
from Payment.models import Course
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import email.utils
from Home.models import SuperMentor
# Home page view
def home_view(request):
    super_mentors = SuperMentor.objects.all()
    return render(request, "index.html", {
        "super_mentors": super_mentors
    })

# Courses page view  
def courses_view(request):
    courses = Course.objects.all()
    return render(request, "course.html", {"courses": courses})

# Contact page view - FIXED VERSION
# Home/views.py - DIRECT SMTP APPROACH

# Home/views.py - PROFESSIONAL VERSION
from django.shortcuts import render, redirect
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib import messages

def contact_view(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        message_content = request.POST.get('message', '').strip()
        
        # Validation
        if not name or not email:
            messages.error(request, 'Please provide your name and email address.')
            return redirect('contact')
        
        # Professional subject line
        subject = f"Contact Request: {name} - Nirvant Website"
        
        # HTML Email Template (Professional MNC Style)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Contact Form Submission</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333333;
                    margin: 0;
                    padding: 0;
                    background-color: #f8f9fa;
                }}
                .email-container {{
                    max-width: 650px;
                    margin: 0 auto;
                    background-color: #ffffff;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
                }}
                .header {{
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    color: white;
                    padding: 30px 40px;
                    text-align: center;
                }}
                .logo {{
                    font-size: 28px;
                    font-weight: 700;
                    letter-spacing: 1px;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    font-size: 16px;
                    opacity: 0.9;
                    font-weight: 300;
                }}
                .content {{
                    padding: 40px;
                }}
                .section {{
                    margin-bottom: 30px;
                    padding-bottom: 25px;
                    border-bottom: 1px solid #eaeaea;
                }}
                .section-title {{
                    color: #1e3c72;
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                .section-title i {{
                    font-size: 20px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 12px;
                }}
                .info-item {{
                    display: flex;
                    gap: 15px;
                    padding: 8px 0;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #555555;
                    min-width: 80px;
                }}
                .info-value {{
                    color: #222222;
                    flex: 1;
                }}
                .message-box {{
                    background: #f8f9ff;
                    border-left: 4px solid #4a6fdc;
                    padding: 20px;
                    border-radius: 8px;
                    margin-top: 10px;
                    white-space: pre-line;
                    line-height: 1.8;
                }}
                .footer {{
                    background: #f5f7ff;
                    padding: 25px 40px;
                    text-align: center;
                    border-top: 1px solid #eaeaea;
                }}
                .footer-text {{
                    color: #666666;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .badge {{
                    display: inline-block;
                    background: #e8f4ff;
                    color: #1e3c72;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-top: 10px;
                }}
                .button {{
                    display: inline-block;
                    background: #1e3c72;
                    color: white;
                    padding: 12px 28px;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                    margin-top: 20px;
                }}
                @media (max-width: 600px) {{
                    .content {{
                        padding: 25px;
                    }}
                    .header {{
                        padding: 25px 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <!-- Header -->
                <div class="header">
                    <div class="logo">NIRVANT</div>
                    <div class="subtitle">Education • Wellness • Technology</div>
                </div>
                
                <!-- Content -->
                <div class="content">
                    <!-- Greeting -->
                    <div class="section">
                        <h2 style="color: #222; margin: 0 0 10px 0;">New Contact Form Submission</h2>
                        <p style="color: #666; margin: 0;">You have received a new inquiry via the Nirvant website contact form.</p>
                    </div>
                    
                    <!-- Sender Information -->
                    <div class="section">
                        <div class="section-title">
                            <span>📋 Sender Details</span>
                        </div>
                        <div class="info-grid">
                            <div class="info-item">
                                <div class="info-label">Name:</div>
                                <div class="info-value"><strong>{name}</strong></div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Email:</div>
                                <div class="info-value">{email}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Phone:</div>
                                <div class="info-value">{phone if phone else 'Not provided'}</div>
                            </div>
                            <div class="info-item">
                                <div class="info-label">Time:</div>
                                <div class="info-value">{request.POST.get('timestamp', 'Just now')}</div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Message -->
                    <div class="section" style="border-bottom: none;">
                        <div class="section-title">
                            <span>💬 Message</span>
                        </div>
                        <div class="message-box">
                            {message_content if message_content else 'No message provided.'}
                        </div>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <div class="footer-text">
                        This inquiry was submitted through the official Nirvant website contact form.<br>
                        <div class="badge">ID: {hash(f"{name}{email}") % 10000:04d}</div>
                        <br>
                        <p style="margin: 20px 0 10px 0;">
                            <a href="mailto:{email}" class="button">📧 Reply to {name.split()[0] if name else 'Sender'}</a>
                        </p>
                        <p style="font-size: 12px; color: #999; margin-top: 20px;">
                            © 2025 Nirvant. All rights reserved.<br>
                            This is an automated message. Please do not reply to this email.
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Plain text version (for email clients that don't support HTML)
        text_content = f"""
        NEW CONTACT FORM SUBMISSION - NIRVANT WEBSITE
        ==============================================
        
        SENDER INFORMATION:
        -------------------
        Name: {name}
        Email: {email}
        Phone: {phone if phone else 'Not provided'}
        
        MESSAGE:
        --------
        {message_content if message_content else 'No message provided.'}
        
        ==============================================
        This inquiry was submitted through the official Nirvant website contact form.
        Submission ID: {hash(f"{name}{email}") % 10000:04d}
        
        To respond, please reply directly to: {email}
        ==============================================
        """
        
        try:
            # Send email with professional headers
            email_msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                # FROM: Shows as user's email in inbox (Professional MNC style)
                from_email=f"{name} <{email}>",
                # TO: Company email
                to=['nirvant.trgyy@gmail.com'],
                # REPLY-TO: User's email for easy reply
                reply_to=[f"{name} <{email}>"],
                # Custom headers for better display
                headers={
                    'X-Contact-Form': 'Yes',
                    'X-Sender-Email': email,
                    'X-Sender-Name': name,
                    'X-Priority': '1',
                    'X-MSMail-Priority': 'High',
                    'Importance': 'high',
                }
            )
            
            # Attach HTML version
            email_msg.attach_alternative(html_content, "text/html")
            
            # Send with company SMTP credentials
            email_msg.connection = None  # Force new connection
            email_msg.send()
            
            # SUCCESS MESSAGE with user's name
            messages.success(request, f'Thank you {name}! Your inquiry has been submitted successfully. We will contact you at {email} shortly.')
            
            # Auto-reply to user (Professional)
            try:
                user_html_content = f"""
                <!DOCTYPE html>
                <html>
                <head><style>body{{font-family:Arial,sans-serif;line-height:1.6;color:#333;}} 
                .container{{max-width:600px;margin:0 auto;padding:20px;}}
                .header{{background:#1e3c72;color:white;padding:20px;text-align:center;border-radius:8px 8px 0 0;}}
                .content{{padding:30px;background:#f9f9f9;border:1px solid #ddd;}}
                .footer{{text-align:center;padding:20px;color:#666;font-size:12px;}}</style></head>
                <body>
                <div class="container">
                    <div class="header"><h2>NIRVANT</h2><p>Confirmation of Your Inquiry</p></div>
                    <div class="content">
                        <h3>Dear {name},</h3>
                        <p>Thank you for contacting <strong>Nirvant</strong>. We have successfully received your inquiry and one of our representatives will get back to you within <strong>24-48 business hours</strong>.</p>
                        <p><strong>Reference ID:</strong> NIR-{hash(f"{name}{email}") % 10000:04d}</p>
                        <p>For urgent matters, please contact us at <strong>+91 77359 32023</strong>.</p>
                        <p>Best regards,<br><strong>The Nirvant Team</strong></p>
                    </div>
                    <div class="footer">© 2025 Nirvant. This is an automated message.</div>
                </div>
                </body>
                </html>
                """
                
                user_msg = EmailMultiAlternatives(
                    subject=f"Confirmation: Your Inquiry to Nirvant (Ref: NIR-{hash(f'{name}{email}') % 10000:04d})",
                    body=f"Dear {name},\n\nThank you for contacting Nirvant. We have received your inquiry and will respond within 24-48 hours.\n\nReference: NIR-{hash(f'{name}{email}') % 10000:04d}\n\nTeam Nirvant",
                    from_email="Nirvant Team <nirvant.trgyy@gmail.com>",
                    to=[email],
                    headers={'X-Auto-Response': 'yes'}
                )
                user_msg.attach_alternative(user_html_content, "text/html")
                user_msg.send(fail_silently=True)
                
            except Exception as auto_error:
                print(f"Auto-reply failed (not critical): {auto_error}")
            
            return redirect('contact')
            
        except Exception as e:
            print(f"Email error: {e}")
            # Fallback to simple email if HTML fails
            try:
                send_mail(
                    subject=f"Contact Form: {name}",
                    message=f"Name: {name}\nEmail: {email}\nPhone: {phone}\nMessage: {message_content}",
                    from_email=f"{name} <{settings.EMAIL_HOST_USER}>",
                    recipient_list=['nirvant.trgyy@gmail.com'],
                    fail_silently=False,
                )
                messages.success(request, f'Thank you {name}! Your message has been sent.')
            except:
                messages.error(request, 'Unable to send message. Please email us directly at nirvant.trgyy@gmail.com')
            
            return redirect('contact')
    
    # GET request - show contact form
    return render(request, 'contact.html')

## adding Super mentor model to admin panel

def terms_view(request):
    return render(request, 'terms.html')

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
import random
from .models import EmailOTP
from django.core.mail import EmailMessage

# SEND OTP EMAIL

def send_otp_email(email, otp, first_name=None):
   
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
    context = {}

    if request.method == "POST":
        action = request.POST.get("action")

        # ================= REGISTER =================
        if action == "register":
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            username = request.POST.get("username")
            email = request.POST.get("email")
            age = request.POST.get("age")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            # VALIDATION
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

            # DELETE OLD OTP IF EXIST
            EmailOTP.objects.filter(email=email).delete()

            # GENERATE OTP
            otp = str(random.randint(100000, 999999))

            # SAVE TO EmailOTP MODEL
            email_otp_obj = EmailOTP.objects.create(
                user=None,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password1,
                otp=otp
            )

            # SEND OTP
            send_otp_email(email, otp)
            messages.success(request, "OTP sent to your email!")

            # SAVE ID IN SESSION
            request.session["emailotp_id"] = email_otp_obj.id
            context = {"email": email, "show_otp": True}

        # ================= VERIFY OTP =================
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

            # LINK USER TO EmailOTP
            email_otp_obj.user = user
            email_otp_obj.save()

            # CLEAR SESSION
            del request.session["emailotp_id"]

            messages.success(request, "Registration successful! Please login.")
            return redirect("login")

        # ================= RESEND OTP =================
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


# ----------------------------------------------------
# LOGIN VIEW
# ----------------------------------------------------



from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect


def login_view(request):
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


#--------------------------------------------------------------------------
#---------DASHBOARD VIEW WILL BE ADDED IN FUTURE----------------#
#--------------------------------------------------------------------------
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect


@login_required(login_url="login")
def dashboard(request):
    context = {
        "user": request.user
    }
    return render(request, "dashboard.html", context)


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    return redirect("home")