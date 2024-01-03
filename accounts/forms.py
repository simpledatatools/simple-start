from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm, AuthenticationForm, UsernameField, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext, gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.contrib.auth import password_validation
from django.conf import settings
from .models import *
import string
import random

from accounts.models import *


# ================================================================================
# app FORMS
# ================================================================================

def create_username(name):
    name = name.replace(" ", "")
    choices = string.ascii_letters + string.hexdigits
    choice = "".join(random.choice(choices) for _ in range(10))
    username = f'{name}{choice}'
    return username


class SignUpForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _('The password and confirm password fields didn’t match.'),
    }

    first_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={
                'class':'form-control py-3 mb-3',
                'placeholder': 'Name'
                }
            ),
        label="",
        )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                'class':'form-control py-3 mb-3',
                'placeholder': 'Email'
                }
            ),
        label="",
        )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                 'placeholder': 'Password',
                 'class': 'form-control py-3 mb-3 signup-pswrd',
                 },
            ),
        label="",
        )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autocomplete': 'new-password',
                'placeholder': 'Confirm password',
                'class': 'form-control py-3 mb-3 signup-pswrd',
                }
            ),
        label="",
        )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'email', 'password1', 'password2')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower().strip()
        return email

    def clean(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Email is already exists, please use unique email address")
        return self.cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data.get('email').lower().strip()
        user.is_active = False
        if commit:
            user.save()
        return user


class UpdatePasswordForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UpdatePasswordForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs['class'] = 'form-control form-control-solid'
        self.fields['new_password1'].widget.attrs['class'] = 'form-control form-control-solid'
        self.fields['new_password2'].widget.attrs['class'] = 'form-control form-control-solid'


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label="",
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control py-3 mb-3', 'placeholder': 'Your email'}
        )
        )

    class Meta:
        model = CustomUser
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(UserPasswordResetForm, self).__init__(*args, **kwargs)


class UpdateProfileForm(UserChangeForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control form-control-solid'}))
    last_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class':'form-control form-control-solid'}))
    password = None

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def __init__(self, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)


class UserLoginForm(forms.Form):
    email = forms.EmailField(
        label="",
        required=True,
        widget=forms.EmailInput(
            attrs={'class': 'form-control py-3 mb-3', 'placeholder': 'Email'}
        )
        )
    password = forms.CharField(
        label="",
        required=True,
        widget=forms.PasswordInput(
            attrs={'class': 'form-control py-3 mb-3', 'placeholder': 'Password'}
        )
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        email = email.lower().strip()
        return email

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if CustomUser.objects.filter(email=email).exists() is False:
            raise ValidationError("Email does not exist! Please create an account before logging in.")
        else:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password) is False:
                raise ValidationError("Invalid Password")
            else:
                if user.is_active is False:
                    raise ValidationError("You are not an active user, please confirm your email first or contact to support")
        return self.cleaned_data


class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="",
        required=True,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'New password',
            'class': 'form-control py-3 mb-3 signup-pswrd',
            }),
        strip=False,
        # help_text=password_validation.password_validators_help_text_html(),
    )

    new_password2 = forms.CharField(
        label="",
        required=True,
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'placeholder': 'Confirm new password',
            'class': 'form-control py-3 mb-3 signup-pswrd',
            }),
    )

