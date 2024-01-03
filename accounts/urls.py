from django.urls import path
from accounts.views import accounts as accounts

urlpatterns = [
    
    # Accounts
    path('login/', accounts.LoginView.as_view(), name='login'),
    path('signup/', accounts.UserRegistrationView.as_view(), name='sign_up'),
    path('create-account/', accounts.VerifyUserLinkView.as_view(), name='create_account'),
    path('reset-password/', accounts.ResetPasswordView.as_view(), name='reset_password'),
    path('forgot-password/', accounts.VerifyUserLinkView.as_view(), name='forgot_password'),
    path('create-new-password/', accounts.CreateNewPasswordView.as_view(), name='create_new_password'),
    path('logout/', accounts.account_logout, name='logout'),

    path('profile/', accounts.profile, name='profile'),
    path('ajax/profile/update/', accounts.ajax_update_profile, name='ajax_update_profile'),
    path('ajax/profile/photo/update/', accounts.ajax_update_profile_photo, name='ajax_update_profile_photo'),
    path('ajax/profile/photo/remove/', accounts.ajax_remove_profile_photo, name='ajax_remove_profile_photo'),
    
]
