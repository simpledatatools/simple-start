from django.urls import path
from api.views import user_views as views


urlpatterns = [
    
    # Login
    path('login/', views.MyTokenObtainPairView.as_view(), name='api_token_obtain_pair'),
    
    # Sign up
    path('signup/', views.registerUser, name='api_register'),
    path('verify-account/', views.verifyAccount, name='api_verify_account'),
    path('verify-account-resend/', views.verifyAccountResend, name='api_verify_account_resend'),
    
    # Resetting password
    path('password-reset-request/', views.passwordResetRequest, name='api_password_reset_request'),
    path('password-reset-request-resend/', views.passwordResetRequestResend, name='api_password_reset_request_resend'),
    path('verify-password-reset/', views.verifyPasswordReset, name='api_verify_password_reset'),
    path('password-reset/', views.passwordReset, name='api_password_reset'),
    
    # Update profile
    path('profile/', views.getUserProfile, name="api_user_profile"),
    path('profile/update/', views.updateUserProfile, name="api_update_user_profile"),
    path('profile/update/photo/', views.updateUserProfilePhoto, name="api_update_user_profile_photo"),
    
    # Change password
    path('password-change-request/', views.passwordChangeRequest, name='api_password_change_request'),
    path('password-change-request-resend/', views.passwordChangeRequestResend, name='api_password_change_request_resend'),
    path('verify-password-change/', views.verifyPasswordChange, name='api_verify_password_change'),
    path('password-change/', views.passwordChange, name='api_password_change'),

    # Change email
    path('email-change-request/', views.emailChangeRequest, name='api_email_change_request'),
    path('email-change-to-request/', views.emailChangeToRequest, name='api_email_change_to_request'),
    path('email-change-to-request-resend/', views.emailChangeToRequestResend, name='api_email_change_to_request_resend'),
    path('verify-email-change/', views.verifyEmailChange, name='api_verify_email_change'),

]