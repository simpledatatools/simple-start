from django.shortcuts import render

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404
from django.template import loader
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import logout
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils import timezone
from django.utils.text import slugify

import logging
logger = logging.getLogger('SimpleStart')

import json
from operator import itemgetter

# Dates and
from django.utils import timezone
from datetime import datetime, timedelta

# Settings  
from django.conf import settings

# Models
from accounts.models import *
from files.models import *
from django.db.models import Q

# Utils
from core.utils import *
from accounts.utils import *

# Accounts
from accounts.forms import *
from accounts.user_mailing import *

# Forms
from accounts.forms import *

# Tasks
from files.tasks import *

# Messaging
from messaging.tasks import *

import time
from django.contrib.auth import authenticate, login


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('apps', )
        else:
            form = UserLoginForm()
            hide_login = True
            return render(request, self.template_name, locals())

    def post(self, request):
        form = UserLoginForm(request.POST)
        email = request.POST.get('email')
        password = request.POST.get('password')

        if form.is_valid():
            user = get_object_or_404(CustomUser, email=email)
            auth_obj = authenticate(request=request, username=user.username, password=password)
            if auth_obj:
                login(request, auth_obj)
                return redirect('apps', )

        else:
            hide_login = True
            return render(request, self.template_name, locals())


class UserRegistrationView(View):
    
    def get(self, request):
        form = SignUpForm()
        hide_signup = True
        return render(request, 'accounts/register.html', locals())

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():

            # Save the new user
            user = form.save()

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
            link, key = create_link(link_for='sign-up')
            obj, created = MailLinkModel.objects.update_or_create(user=user, link_type="sign_up", is_delete=False)
            obj.key = key
            obj.save()
            send_email.delay(recipient_name=user.first_name, link=link, recipient_list=user.email, subject="Verify your Simple Start account", mail_for="sign-up", body=None)

            context = {'email': user_email, 'render_kind': 'signup', 'hide_signup': True}

            return render(request, 'accounts/confirmation.html', context)
        else:
            hide_signup = True
            return render(request, 'accounts/register.html', locals())


class VerifyUserLinkView(View):
    
    def get(self, request):
        get_key = request.GET.get('key')
        link_obj = get_object_or_404(MailLinkModel, key=get_key)
        if link_obj:
            #if link_obj.is_delete is False:
            user = get_object_or_404(CustomUser, pk=link_obj.user_id)
            if link_obj.link_type == 'sign_up':
                user.is_active = True
                user.save()
                link_obj.is_delete = True
                link_obj.save()

                user_name = user.get_full_name()

                return render(request, 'accounts/confirmation.html', {'render_kind': 'signup_confirmed', 'hide_signup': True})
            elif link_obj.link_type == 'reset_password':
                request.session['forgot_password_user_pk'] = user.pk
                request.session['forgot_password_link_pk'] = link_obj.pk
                return redirect('create_new_password')
        return render(request, 'accounts/confirmation.html', {'render_kind': 'invalid_key', 'hide_signup': True})


class ResetPasswordView(View):
    template_name = 'accounts/password-reset.html'
    
    def get(self, request):
        hide_signup = True
        form = UserPasswordResetForm()
        return render(request, self.template_name, locals())

    def post(self, request):
        email = request.POST.get('email')
        user = get_object_or_404(CustomUser, email=email)

        if user:
            if user.is_active:
                user_email = user.email
                user_name = user.get_full_name()
                link, key = create_link(link_for='reset-password')
                obj, created = MailLinkModel.objects.update_or_create(user=user, link_type="reset_password", is_delete=False)
                obj.key = key
                obj.save()
                send_email.delay(recipient_name=user_name, link=link, recipient_list=user_email, subject="Reset your Canvas Docs password", mail_for="reset-password", body=None)
                context = {'email': user_email, 'render_kind': 'reset_password', 'hide_signup': True}
                return render(request, 'accounts/confirmation.html', context)
        return self.get(request)


class CreateNewPasswordView(View):
    template_name = 'accounts/password-reset-form.html'

    def get(self, request):
        user_pk = request.session.get('forgot_password_user_pk')
        user = get_object_or_404(CustomUser, pk=user_pk)
        form = UserSetPasswordForm(user=user)
        return render(request, self.template_name, locals())

    def post(self, request):
        user_pk = request.POST.get('user_id')
        user = get_object_or_404(CustomUser, pk=user_pk)
        form = UserSetPasswordForm(data=request.POST, user=user)
        if form.is_valid():
            form.save()
            request.session.pop('forgot_password_user_pk')
            link_obj_pk = request.session.get('forgot_password_link_pk')
            link_obj = get_object_or_404(MailLinkModel, pk=link_obj_pk)
            link_obj.is_delete = True
            link_obj.save()
            request.session.pop('forgot_password_link_pk')
        else:
            return render(request, self.template_name, locals())

        user_email = user.email
        user_name = user.get_full_name()
        send_email.delay(recipient_name=user_name, link='', recipient_list=user_email, subject="Your Canvas Docs password was changed", mail_for="password-change", body=None)
        return render(request, 'accounts/confirmation.html', {'render_kind': 'password_updated', 'hide_signup': True})


@require_http_methods(['GET'])
@login_required(login_url='login')
def account_logout(request):

    logout(request)
    
    return redirect('login')


@require_http_methods(['GET'])
@login_required(login_url='login')
def profile(request):
    
    context = {
    }
    
    return render(request, 'accounts/profile.html', context)


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_profile(request):

    user = request.user
    if not is_ajax(request):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    # TODO check the required params here
    data = json.loads(request.body)
    name = None
    if 'name' in data:
        name = data['name']

    user.display_name = name
    user.save()
    
    response_object = {
        'message': 'User profile saved successfully',
    }

    return JsonResponse(response_object, status=200)


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_profile_photo(request):

    user = request.user
    
    # TODO check the required params here
    data = json.loads(request.body)
    file_to_save = None
    if 'file_to_save' in data:
        file_to_save = data['file_to_save']
    if file_to_save == None:
        return JsonResponse({'error': "Missing the 'file_to_save' parameter."}, status=400)

    original_name = file_to_save['file_original_name']
    file_type = file_to_save['file_type']
    file_extension = file_to_save['file_extension']
    file_size = file_to_save['file_size']
    file_size_mb = file_to_save['file_size_mb']
    file_name = 'private/uploads/' + randomlongstr() + '.' + file_extension
    url = file_to_save['url']
    S3_BUCKET = settings.AWS_STORAGE_BUCKET_NAME
    root_url = 'https://%s.s3.amazonaws.com/private/' % S3_BUCKET
    save_url = url.replace(root_url, '')

    # Create a new user file
    media_file = File()
    media_file.file = save_url
    media_file.display_id = randomstr()
    media_file.file_name = file_name
    media_file.original_name = original_name
    media_file.display_name = original_name
    media_file.file_type = file_type
    media_file.file_size = file_size
    media_file.file_size_mb = file_size_mb
    media_file.file_display_type = 'image'
    splited_name = file_name.split('.')
    media_file.file_extension = '.' + splited_name[-1]
    media_file.user = request.user
    media_file.save()

    user.profile_photo = media_file
    user.save()
    
    # Background processing for thumbnails if the file is an image
    process_thumbnails.delay(media_file.id)
    
    response_object = {
        'message': 'Profile photo saved successfully',
        'url': media_file.file.url,
        'file_to_save': file_to_save,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_profile_photo(request):

    user = request.user

    # TODO check the required params here
    user.profile_photo = None
    user.save()
    
    response_object = {
        'message': 'Profile photo removed',
    }

    return JsonResponse(response_object, status=200)