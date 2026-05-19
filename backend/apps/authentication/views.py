from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP
from .serializers import (
    SignupSerializer, LoginSerializer, OTPSendSerializer,
    OTPVerifySerializer, PINSetupSerializer, UserSerializer
)
from .utils import generate_otp, create_jwt_token, simulate_send_otp
from django.conf import settings

class SignupView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate and save OTP
            otp_code = generate_otp()
            OTP.objects.create(
                user=user,
                otp_code=otp_code,
                purpose='verification',
                expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
            )
            
            # Send OTP via email
            email_sent = simulate_send_otp(user.email, otp_code, 'verification')
            
            return Response({
                'message': 'User created successfully. Please verify your email with OTP.',
                'user': UserSerializer(user).data,
                'email_sent': email_sent
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPSendSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            purpose = serializer.validated_data['purpose']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Invalidate old OTPs
            OTP.objects.filter(user=user, purpose=purpose, is_used=False).update(is_used=True)
            
            # Generate new OTP
            otp_code = generate_otp()
            OTP.objects.create(
                user=user,
                otp_code=otp_code,
                purpose=purpose,
                expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
            )
            
            # Send OTP via email
            email_sent = simulate_send_otp(email, otp_code, purpose)
            
            if not email_sent and settings.DEBUG:
                return Response({
                    'warning': 'Failed to send email. Check console for OTP.',
                    'otp_for_development': otp_code
                }, status=status.HTTP_200_OK)
            
            return Response({
                'message': f'OTP sent successfully to {email}'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            purpose = serializer.validated_data['purpose']
            
            try:
                user = User.objects.get(email=email)
                otp = OTP.objects.get(
                    user=user,
                    otp_code=otp_code,
                    purpose=purpose,
                    is_used=False
                )
                
                if not otp.is_valid():
                    return Response({
                        'error': 'OTP has expired'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Mark OTP as used
                otp.is_used = True
                otp.save()
                
                # Update user based on purpose
                if purpose == 'verification':
                    user.is_verified = True
                    user.save()
                    return Response({
                        'message': 'Email verified successfully. You can now login.'
                    }, status=status.HTTP_200_OK)
                
                elif purpose == 'login':
                    # Generate JWT token
                    token = create_jwt_token(user)
                    return Response({
                        'message': 'Login successful',
                        'token': token,
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                
                elif purpose == 'pin_setup':
                    return Response({
                        'message': 'OTP verified. You can now set your PIN.'
                    }, status=status.HTTP_200_OK)
                
            except User.DoesNotExist:
                return Response({
                    'error': 'User not found'
                }, status=status.HTTP_404_NOT_FOUND)
            except OTP.DoesNotExist:
                return Response({
                    'error': 'Invalid OTP'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Check if user is verified
            if not user.is_verified:
                return Response({
                    'error': 'Please verify your email first. Check your email for OTP.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Send OTP for login
            otp_code = generate_otp()
            OTP.objects.create(
                user=user,
                otp_code=otp_code,
                purpose='login',
                expires_at=timezone.now() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
            )
            
            # Send OTP via email
            email_sent = simulate_send_otp(user.email, otp_code, 'login')
            
            if not email_sent and settings.DEBUG:
                return Response({
                    'message': 'OTP sent to your email for login verification',
                    'email': user.email,
                    'otp_for_development': otp_code
                }, status=status.HTTP_200_OK)
            
            return Response({
                'message': 'OTP sent to your email for login verification',
                'email': user.email
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetupPINView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = PINSetupSerializer(data=request.data)
        if serializer.is_valid():
            pin = serializer.validated_data['pin']
            
            # Set the PIN for the user
            request.user.set_pin(pin)
            
            return Response({
                'message': 'PIN setup successful'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyPINView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        pin = request.data.get('pin')
        
        if not pin:
            return Response({
                'error': 'PIN is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.verify_pin(pin):
            return Response({
                'message': 'PIN verified successfully'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Invalid PIN'
        }, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(' ')[1]
            try:
                from .models import UserSession
                session = UserSession.objects.get(token=token, user=request.user)
                session.is_active = False
                session.save()
            except:
                pass
        
        return Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        user = request.user
        if 'full_name' in request.data:
            user.full_name = request.data['full_name']
        if 'phone_number' in request.data:
            user.phone_number = request.data['phone_number']
        user.save()
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)