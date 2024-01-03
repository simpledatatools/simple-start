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
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
import urllib.parse

import json
from operator import itemgetter

# Dates and
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.utils import timezone

# Settings
from django.conf import settings

# Models
from accounts.models import *
from backend.models import *

# Utils
from core.utils import *
from monitor.views.utils import *
from backend.utils import *

# Tasks
from backend.tasks import *
from files.tasks import *
from messaging.tasks import *

import time
from django.apps import apps


@login_required(login_url='login')
def app_users(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    admin = is_admin(app_user)
    role = app_user.role
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'smh': 'users',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/app_users/app_users.html', context)


@login_required(login_url='login')
def add_app_user(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    admin = is_admin(app_user)
    role = app_user.role
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'smh': 'users',
        'form_title': 'Add app user',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/app_users/add.html', context)


@login_required(login_url='login')
def app_user_details(request, app_id, app_user_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    admin = is_admin(app_user)
    role = app_user.role
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'app_user': app_user,
        'smh': 'users',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/app_users/details.html', context)


@login_required(login_url='login')
def update_app_user(request, app_id, app_user_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    admin = is_admin(app_user)
    role = app_user.role
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'app_user': app_user,
        'edit': True,
        'smh': 'users',
        'form_title': 'Update app user',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/app_users/update.html', context)


@login_required(login_url='login')
def remove_app_user(request, app_id, app_user_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    admin = is_admin(app_user)
    role = app_user.role
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'app_user': app_user,
        'smh': 'users',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/app_users/remove.html', context)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_app_users(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    admin = is_admin(app_user)
    role = app_user.role
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    render_type = request.GET.get('render_type', None)
    if render_type == None:
        error = "Missing the 'render_type' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    response_object = get_app_users_list(request, app)

    return JsonResponse(response_object, status=200)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_app_user_item(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    admin = is_admin(app_user)
    role = app_user.role
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user_id = request.GET.get('app_user_id', None)
    if app_user_id == None:
        error = "Missing the 'app_user_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/app_users/components/app_user-item.html",
        context={
            'app': app,
            'app_user': app_user,
            'render_type': 'display',
            'admin': admin,
        'role': role,
        }
    )

    if app_user.user:
        email = app_user.user.email
    else:
        email = app_user.email
    
    response_object = {
        'html': html,
        'email': email,
        'role': app_user.role,
    }

    return JsonResponse(response_object, status=200)
    


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_add_app_user(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    admin = is_admin(app_user)
    role = app_user.role
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    email = None
    if 'email' in data:
        email = data['email']
    if email == None:
        error = "Missing the 'email' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    role = None
    if 'role' in data:
        role = data['role']
    if role == None:
        error = "Missing the 'role' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------

    # Create the collection
    app_user = create_app_user(request, app, email, role)

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/app_users/components/app_user-item.html",
        context={
            'app': app,
            'app_user': app_user,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )
    
    redirect = request.build_absolute_uri(reverse('app_users', args=(app.app_id, )))
    response_object = {
        'app_id': app.app_id,
        'app_user_id': app_user.app_user_id,
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_app_user(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    admin = is_admin(app_user)
    role = app_user.role
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_user_id = None
    if 'app_user_id' in data:
        app_user_id = data['app_user_id']
    if app_user_id == None:
        error = "Missing the 'app_user_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    role = None
    if 'role' in data:
        role = data['role']
    if role == None:
        error = "Missing the 'role' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    app_user.role = role
    app_user.save()

    html = render_to_string(
        template_name="monitor/app_users/components/app_user-item.html",
        context={
            'app': app,
            'app_user': app_user,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('app_user_details', args=(app.app_id, app_user.app_user_id, )))

    response_object = {
        'message': 'AppUser updated successfully',
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_app_user(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    app = App.objects.filter(app_id=app_id, status='active').first()
    if not app:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app=app, user=user, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    if app_user.role not in roles:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    admin = is_admin(app_user)
    role = app_user.role
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_user_id = None
    if 'app_user_id' in data:
        app_user_id = data['app_user_id']
    if app_user_id == None:
        error = "Missing the 'app_user_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_user = AppUser.objects.filter(app_user_id=app_user_id, app=app, status='active').first()
    if not app_user:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    app_user.status = 'archived'
    app_user.save()

    redirect = request.build_absolute_uri(reverse('app_users', args=(app.app_id, )))

    response_object = {
        'message': 'AppUser archived successfully',
        'redirect': redirect,
    }

    return JsonResponse(response_object, status=200)



def get_app_users_list(request, app):

    user = request.user

    # Query Params
    search_term = request.GET.get('search_term', None)
    created_at = request.GET.get('created_at', None)
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 25)
    order = request.GET.get('order', None)
    render_type = request.GET.get('render_type', None)

    # Clean up and checks   
    if isinstance(page, str):
        try:
            page = int(page)
        except ValueError:
            page = 1
    
    if isinstance(page_size, str):
        try:
            page_size = int(page_size)
        except ValueError:
            page_size = 25
    if page_size > 100: # Block super large requests like this
        page_size = 100
    if page_size == 0:
        page_size = 25
    
    # Query from app tags that the user a part of
    app_user_items = AppUser.objects.filter(app=app).order_by('created_at').exclude(status="archived")

    # Search Term
    if search_term:
        app_user_items = app_user_items.filter(
            Q(app_user_id__icontains=search_term) | 
            Q(email__icontains=search_term) | 
            Q(user__email__icontains=search_term)
        )

    # Filters
    if order:
        if order == 'created_at_desc':
            app_user_items = app_user_items.order_by('-created_at')
        if order == 'created_at_asc':
            app_user_items = app_user_items.order_by('created_at')

    # Pagination
    total_pages = None
    load_more = False
    total_count = 0
    if app_user_items:
        total_count = len(app_user_items)
        paginator = Paginator(app_user_items, per_page=page_size)
        total_pages = paginator.num_pages # Number of total pages
        app_user_items = paginator.get_page(page) # Filters current queryset
        if page < total_pages:
            load_more = True

    # Generate the Response Object
    app_user_list_html = []
    for app_user_object in app_user_items:
        html = render_to_string(
            template_name="monitor/app_users/components/app_user-item.html",
            context={
                'app': app,
                'app_user': app_user_object,
                'render_type': render_type,
            }
        )
        app_user_list_html.append(html)

    results = True
    if len(app_user_items) == 0:
        results = False

    # Response
    response_object = {
        'success': True,
        'results': results,
        'items': app_user_list_html,
        'page': page,
        'total_pages': total_pages,
        'load_more': load_more,
        'total_count': total_count,
    }

    return response_object


def create_app_user(request, app, email, role):
    
    user = request.user
    ip_address = get_ip_address(request)

    email = email.lower().strip()

    existing_user = CustomUser.objects.filter(email=email).first()

    if not existing_user:

        send_welcome_email = False
        
        # Check first to see if the same store was added previously
        app_user = AppUser.objects.filter(app=app, email=email).first()
        if not app_user:

            # Create new record
            app_user = AppUser()
            app_user.app_user_id = randomstr()
            app_user.email = email
            app_user.app = app
            app_user.created_user = user
            app_user.role = role
            app_user.status = 'pending'
            app_user.save()
            send_welcome_email = True

        else:

            if app_user.status != 'pending':
                # This user was already added but needs to be readded
                app_user.status = 'pending'
                app_user.save()
                send_welcome_email = True

        if send_welcome_email:
            
            recipient_email = email
            message = f"""
            Hey there,

            {user.display_name} added you to a new app on Simple Start called '{app.name}'. You can register for Simple Start at the link below:
            {settings.BASE_URL}signup/ 

            Sincerely,

            ~ Simple Start
            """
            subject = '[Simple Start] You were added to a new app'
            send_general_email.delay(recipient_email, subject, message)

    else:

        send_welcome_email = False

        # Check first to see if the same store was added previously
        app_user = AppUser.objects.filter(app=app, user=existing_user).first()
        if not app_user:
            
            app_user = AppUser()
            app_user.app_user_id = randomstr()
            app_user.user = existing_user
            app_user.email = existing_user.email
            app_user.app = app
            app_user.created_user = request.user
            app_user.role = role
            app_user.status = 'active'
            app_user.save()
            send_welcome_email = True

        else: 
            
            if app_user.status != 'active':
                app_user.status = 'active'
                app_user.save()
                send_welcome_email = True
        
        if send_welcome_email:

            recipient_name = existing_user.display_name
            recipient_email = existing_user.email
            message = f"""
            Hey there,

            {user.display_name} added you to a new app on Simple Start called '{app.name}'. You can access the app at the link below:
            {settings.BASE_URL}apps/{app.app_id}/

            Sincerely,

            ~ Simple Start
            """
            subject = '[Simple Start] You were added to a new app'
            send_general_email.delay(recipient_email, subject, message)

    return app_user