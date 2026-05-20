import random
import jwt
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import UserSession

def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def create_jwt_token(user):
    """Create JWT token for user"""
    payload = {
        'user_id': user.id,
        'email': user.email,
        'exp': timezone.now() + settings.JWT_EXPIRATION_DELTA,
        'iat': timezone.now(),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    # Create user session
    UserSession.objects.create(
        user=user,
        token=token,
        expires_at=timezone.now() + settings.JWT_EXPIRATION_DELTA
    )
    
    return token

def send_email_otp(email, otp_code, purpose):
    """Send OTP via email using Gmail SMTP"""
    subject = f'Ortho Wallet - {purpose.replace("_", " ").title()} OTP'
    
    # Email templates based on purpose
    if purpose == 'verification':
        title = 'Email Verification'
        message_body = f'Thank you for signing up! Please use the following OTP to verify your email address:'
    elif purpose == 'login':
        title = 'Login Verification'
        message_body = f'Use the following OTP to complete your login:'
    elif purpose == 'pin_setup':
        title = 'PIN Setup Verification'
        message_body = f'Use the following OTP to set up your transaction PIN:'
    else:
        title = 'OTP Verification'
        message_body = f'Your OTP code is:'
    
    html_message = f'''
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #4F46E5;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 8px 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .otp-code {{
                font-size: 32px;
                font-weight: bold;
                color: #4F46E5;
                text-align: center;
                padding: 20px;
                background-color: #f0f0ff;
                border-radius: 8px;
                letter-spacing: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Ortho Wallet</h1>
            </div>
            <div class="content">
                <h2>{title}</h2>
                <p>{message_body}</p>
                <div class="otp-code">{otp_code}</div>
                <p>This OTP is valid for {settings.OTP_EXPIRATION_MINUTES} minutes.</p>
                <p>If you didn't request this, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2026 Ortho Wallet. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f" Email sent successfully to {email}")
        return True
    except Exception as e:
        print(f" Failed to send email to {email}: {str(e)}")
        # Fallback to console output for development
        print(f"\n{'='*50}")
        print(f"OTP SIMULATION (Email Failed)")
        print(f"Email: {email}")
        print(f"OTP Code: {otp_code}")
        print(f"Purpose: {purpose}")
        print(f"{'='*50}\n")
        return False

def simulate_send_otp(email, otp_code, purpose):
    """Send OTP via email with fallback to console"""
    return send_email_otp(email, otp_code, purpose)