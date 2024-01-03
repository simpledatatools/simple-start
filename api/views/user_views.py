from django.shortcuts import render
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.models import CustomUser
from api.serializers.user_serializers import UserSerializer, UserSerializerWithToken

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.hashers import make_password
from rest_framework import status

from accounts.models import *
from accounts.user_mailing import *
from messaging.tasks import *
from core.utils import *
from files.models import *
from files.tasks import *

from django.conf import settings
import logging
logger = logging.getLogger('SimpleStart')

# ---------------------------------------------------------------------------------------------------
# Logging in
# ---------------------------------------------------------------------------------------------------

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_verified:
            # Consider adding a mechanism to limit automatic verification code resends
            self.handle_verification_process()

            return {'success': False, 'message': 'User is not active'}

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return {'success': True, 'user': data}

    def handle_verification_process(self):
        user_email = self.user.email
        existing_verify_codes = VerifyCode.objects.filter(user=self.user, code_type='register', status='pending')
        existing_verify_codes.update(status='used') # Updating records in a single query

        code = randomverifycode()
        VerifyCode.objects.create(user=self.user, code=code, code_type="register")

        subject = 'Your new verification code is ' + str(code)
        message = 'Thanks so much for signing up. Your new verification code is ' + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# ---------------------------------------------------------------------------------------------------
# Registration and sign up
# ---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def registerUser(request):
    data = request.data

    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not all([email, name, password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    email=data['email'].strip().lower()
    existing_user = CustomUser.objects.filter(email=email)
    if existing_user:
        message = 'A user with that email already exists'
        response = {'success': False, 'message': message}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    else: 
        try:
            user = CustomUser.objects.create(
                first_name=data['name'],
                username=data['email'].strip().lower(),
                email=data['email'].strip().lower(),
                password=make_password(data['password']),
            )
            
            # Create the user extras
            user_extras = UserExtras()
            user_extras.display_name = user.first_name
            user_extras.save()
            user.user_extras = user_extras
            user.save()

            # Get all of the streams of the user
            app_users = AppUser.objects.filter(email=user.email)
            for app_user in app_users:
                app_user.user = user
                app_user.email = user.email
                app_user.status = 'active'
                app_user.save()
            
            user_email = user.email
            user_name = user.get_full_name()

            code = randomverifycode()

            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "register"
            verify_code.save()
            
            to = user_email
            subject = 'Your verification code is ' + str(code)
            message = 'Thanks so much for signing up. Your verification code is ' + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {'success': True, 'message': 'Sign up successful'}
            logger.info(response)
            return Response(response)

        except Exception as e:
            logger.info(e)
            message = 'There was a problem with the sign up'
            response = {'success': False, 'message': message}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------------------------------
# Verifying an account (initial registration)
# ---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def verifyAccount(request):

    data = request.data

    email = data.get('email')
    code = data.get('code')

    if not all([email, code]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()
    code = data['code'].strip()
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, code_type='register', status='pending').first()

    if verify_code:
        # Set the verify record to expired
        verify_code.status = 'used'
        verify_code.save()
        # Get the user
        user = verify_code.user
        user.is_verified = True # Set their account to active
        user.save()
        # Return the token
        serializer = UserSerializerWithToken(user, many=False)

        response = {'success': True, 'user': serializer.data}
        logger.info(response)
        return Response(response)

    else:
        used_verify_code = VerifyCode.objects.filter(user__email=email, code=code, code_type='register', status='used').first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


@api_view(['POST'])
@permission_classes([AllowAny])
def verifyAccountResend(request):

    data = request.data

    email = data.get('email')

    if not all([email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    email = data['email'].strip().lower()
    user = CustomUser.objects.filter(email=email, is_verified=False).first()
    
    if user:

        user_email = user.email
        user_name = user.get_full_name()

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='register', status='pending')
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = 'used'
            existing_verify_code.save()

        code = randomverifycode()

        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "register"
        verify_code.save()

        to = user_email
        subject = 'Your new verification code is ' + str(code)
        message = 'Thanks so much for signing up. Your new verification code is ' + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

    response = {'success': True, 'message': 'Account verification code sent if the user exists and is not verified'}
    logger.info(response)
    return Response(response)


# ---------------------------------------------------------------------------------------------------
# Password reset (user not logged in)
# ---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetRequest(request):
    data = request.data

    email = data.get('email')

    if not all([email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()

    user = CustomUser.objects.filter(email=email).first()
    if user:

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='password_reset', status='pending')
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = 'used'
            existing_verify_code.save()
        
        # Generate new code
        code = randomverifycode()
        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "password_reset"
        verify_code.save()

        to = user.email
        subject = 'Your password reset code is ' + str(code)
        message = 'Your password reset code is ' + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

    response = {'success': True, 'message': 'Password reset code sent if the email exists'}
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([AllowAny])
def passwordResetRequestResend(request):
    data = request.data

    email = data.get('email')

    if not all([email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()

    user = CustomUser.objects.filter(email=email).first()
    if user:

        # Remove any previous records
        existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='password_reset', status='pending')
        for existing_verify_code in existing_verify_codes:
            existing_verify_code.status = 'used'
            existing_verify_code.save()
        
        # Generate new code
        code = randomverifycode()
        verify_code = VerifyCode()
        verify_code.user = user
        verify_code.code = code
        verify_code.code_type = "password_reset"
        verify_code.save()

        to = user.email
        subject = 'Your new password reset code is ' + str(code)
        message = 'Your new password reset code is ' + str(code)
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

    response = {'success': True, 'message': 'Password reset code sent if the email exists'}
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([AllowAny])
def verifyPasswordReset(request):

    data = request.data

    email = data.get('email')
    code = data.get('code')

    if not all([email, code]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    email = data['email'].strip().lower()
    code = data['code'].strip()
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, code_type='password_reset', status='pending').first()

    if verify_code:
        
        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = 'used'
        verify_code.key = key
        verify_code.save()
        
        # Get the user
        user = verify_code.user
        user.is_verified = True # Set their account to active just in case this is someone who never verified
        user.save()

        # Return the token
        response = {'success': True, 'key': key}
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(user__email=email, code=code, code_type='password_reset', status='used').first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)



@api_view(['POST'])
@permission_classes([AllowAny])
def passwordReset(request):
    data = request.data

    email = data.get('email')
    code = data.get('code')
    key = data.get('key')
    password = data.get('password')

    if not all([email, code]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    email = data['email'].strip().lower()
    code = data['code'].strip()
    key = data['key']
    password = data['password']
    user = CustomUser.objects.filter(email=email).first()

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, key=key, code_type='password_reset').first()

    if verify_code:
        
        # Reset the password
        user.set_password(password)
        user.save()

        to = user.email
        subject = 'Your password has been reset'
        message = 'Your password has been reset. If this was not you, please reset your password, then reach out to support right away.'
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the token
        response = {'success': True, 'message': 'Password reset successfully'}
        logger.info(response)
        return Response(response)

    else:

        message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


# ---------------------------------------------------------------------------------------------------
# User profile
# ---------------------------------------------------------------------------------------------------

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    if 'name' in data:
        user.first_name = data['name']
    
    user.save()

    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfilePhoto(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    if 'file_data' in data:
        file_data = data['file_data']
        media_file = File()
        media_file.file = file_data['path']
        media_file.display_id = randomstr()
        media_file.file_name = file_data['file_name']
        media_file.original_name = file_data['original_name']
        media_file.display_name = file_data['original_name']
        media_file.file_type = file_data['file_type']
        media_file.file_size = None
        media_file.file_size_mb = None
        media_file.file_display_type = 'image'
        media_file.file_extension = file_data['file_extension']
        media_file.user = request.user
        media_file.save()

        user.profile_photo = media_file
        user.save()

    return Response({'success': True, 'user': serializer.data})
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


# ---------------------------------------------------------------------------------------------------
# Change password (user logged in)
# ---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def passwordChangeRequest(request):

    data = request.data
    user = request.user

    current_password = data.get('current_password')

    if not all([current_password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct

            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='password_change', status='pending')
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = 'used'
                existing_verify_code.save()
            
            # Generate new code
            code = randomverifycode()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "password_change"
            
            verify_code.save()

            to = user.email
            subject = 'Your password change verification code is ' + str(code)
            message = 'Your password change verification code is ' + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {'success': True, 'message': 'Password change code was sent.'}
        else:
            # Password is incorrect
            response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    else:
        # User is not logged in or does not exist
        response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def passwordChangeRequestResend(request):

    data = request.data
    user = request.user

    current_password = data.get('current_password')

    if not all([current_password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct

            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='password_change', status='pending')
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = 'used'
                existing_verify_code.save()
            
            # Generate new code
            code = randomverifycode()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.code = code
            verify_code.code_type = "password_change"
            verify_code.save()

            to = user.email
            subject = 'Your password change verification code is ' + str(code)
            message = 'Your password change verification code is ' + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {'success': True, 'message': 'Password change code was sent.'}
        else:
            # Password is incorrect
            response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    else:
        # User is not logged in or does not exist
        response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verifyPasswordChange(request):

    data = request.data

    code = data.get('code')

    if not all([code]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    code = data['code'].strip()
    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, code_type='password_change', status='pending').first()

    if verify_code:
        
        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = 'used'
        verify_code.key = key
        verify_code.save()

        # Return the token
        response = {'success': True, 'key': key}
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(user=user, code=code, code_type='password_change', status='used').first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def passwordChange(request):
    data = request.data

    code = data.get('code')
    key = data.get('key')
    password = data.get('password')

    if not all([code, key, password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    code = data['code'].strip()
    key = data['key']
    password = data['password']
    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, key=key, code_type='password_change').first()

    if verify_code:
        
        # Reset the password
        user.set_password(password)
        user.save()

        to = user.email
        subject = 'Your password has been changed'
        message = 'Your password has been changed. If this was not you, please reset your password, then reach out to support right away.'
        if settings.LIVE == "True":
            send_general_email.delay(to, subject, message)
        else:
            logger.info(message)

        # Return the token
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {'success': True, 'message': 'Password changed successfully', 'user': user_serializer}
        logger.info(response)
        return Response(response)

    else:

        message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)


# ---------------------------------------------------------------------------------------------------
# Change password (user logged in)
# ---------------------------------------------------------------------------------------------------

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emailChangeRequest(request):
    data = request.data
    user = request.user

    current_password = data.get('current_password')

    if not all([current_password]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)

    if user is not None:
        auth_user = authenticate(username=user.username, password=current_password)
        if auth_user is not None:
            # Password is correct
            
            # Remove any previous records
            existing_verify_codes = VerifyCode.objects.filter(user=user, code_type='email_change', status='pending')
            for existing_verify_code in existing_verify_codes:
                existing_verify_code.status = 'used'
                existing_verify_code.save()
            
            # Generate new code
            key = randomverylongstr()
            verify_code = VerifyCode()
            verify_code.user = user
            verify_code.key = key # Only set the key here on this one, not the code
            verify_code.code_type = "email_change"
            verify_code.save()

            response = {'success': True, 'message': 'Valid.', 'email': user.email, 'key': key}

        else:
            # Password is incorrect
            response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    else:
        # User is not logged in or does not exist
        response = {'success': False, 'message': 'User is not authenticated or does not exist.'}
    
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emailChangeToRequest(request):
    data = request.data
    user = request.user

    key = data.get('key')
    new_email = data.get('new_email')

    if not all([key, new_email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    key = data['key']
    new_email = data['new_email'].strip().lower()

    # Check if that email is already registered
    existing_users = CustomUser.objects.filter(email=new_email).exclude(email=user.email)
    if existing_users:
        # Email is already taken / and account with that email already exists
        response = {'success': False, 'message': 'Email is already registered.'}
    else:
        # Verify the key and get the existing verify code
        existing_verify_code = VerifyCode.objects.filter(user=user, key=key, code_type='email_change', status='pending').first()
        if existing_verify_code:
            
            code = randomverifycode()
            existing_verify_code.code = code
            existing_verify_code.email = new_email
            existing_verify_code.save()

            to = new_email
            subject = 'Your email change verification code is ' + str(code)
            message = 'Your email change verification code is ' + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {'success': True, 'message': 'Password change code was sent.'}

        else:
            response = {'success': False, 'message': 'Invalid request.'}
    
    logger.info(response)
    return Response(response)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def emailChangeToRequestResend(request):
    
    data = request.data
    user = request.user

    key = data.get('key')
    new_email = data.get('new_email')

    if not all([key, new_email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    key = data['key']
    new_email = data['new_email'].strip().lower()

    # Check if that email is already registered
    existing_users = CustomUser.objects.filter(email=new_email).exclude(email=user.email)
    if existing_users:
        # Email is already taken / and account with that email already exists
        response = {'success': False, 'message': 'Email is already registered.'}
    else:
        # Verify the key and get the existing verify code
        existing_verify_code = VerifyCode.objects.filter(user=user, key=key, email=new_email, code_type='email_change', status='pending').first()
        if existing_verify_code:
            
            code = randomverifycode()
            existing_verify_code.code = code
            existing_verify_code.save()

            to = new_email
            subject = 'Your email change verification code is ' + str(code)
            message = 'Your email change verification code is ' + str(code)
            if settings.LIVE == "True":
                send_general_email.delay(to, subject, message)
            else:
                logger.info(message)

            response = {'success': True, 'message': 'Password change code was sent.'}

        else:
            response = {'success': False, 'message': 'Invalid request.'}
    
    logger.info(response)
    return Response(response)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verifyEmailChange(request):

    data = request.data

    code = data.get('code')
    key = data.get('key')
    new_email = data.get('new_email')

    if not all([key, new_email]):
        return Response({'success': False, 'message': 'Missing required parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    
    code = data['code'].strip()
    key = data['key']
    new_email = data['new_email'].strip().lower()

    user = request.user

    # Check the verify table
    verify_code = VerifyCode.objects.filter(user=user, code=code, key=key, email=new_email, code_type='email_change', status='pending').first()

    if verify_code:
        
        # Set the verify record to expired
        key = randomverylongstr()
        verify_code.status = 'used'
        verify_code.key = key
        verify_code.save()
        
        # Get the user
        user.email = new_email
        user.username = new_email
        user.save()

        # Return the token
        serializer = UserSerializerWithToken(user, many=False)
        user_serializer = serializer.data
        response = {'success': True, 'message': 'Email changed successfully', 'user': user_serializer}
        logger.info(response)
        return Response(response)

    else:

        used_verify_code = VerifyCode.objects.filter(user=user, code=code, key=key, email=new_email, code_type='email_change', status='used').first()
        message = ""
        if used_verify_code:
            message = "Code has already been used"
        else:
            message = "Code is invalid"
        response = {'success': False, 'message': message}
        logger.info(response)
        return Response(response)
