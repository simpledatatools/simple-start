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

import logging
logger = logging.getLogger('SimpleStart')


@login_required(login_url='login')
def apps(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    user = request.user
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'smh': 'apps',
    }
    
    return render(request, 'monitor/apps/apps.html', context)


@login_required(login_url='login')
def add_app(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'smh': 'apps',
        'form_title': 'Add app',
    }
    
    return render(request, 'monitor/apps/add.html', context)


@login_required(login_url='login')
def app(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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

    user.current_app = app
    user.save()

    return redirect('tables', app.app_id)


@login_required(login_url='login')
def app_home(request, app_id):

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

    user.current_app = app
    user.save()

    bottom_menu_items = app.bottom_menu_items()

    context = {
        'app': app,
        'smh': 'home',
        'admin': admin,
        'role': role,
        'bottom_menu_items': bottom_menu_items,
    }
    
    return render(request, 'monitor/apps/home.html', context)


@login_required(login_url='login')
def app_details(request, app_id):

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

    user.current_app = app
    user.save()

    context = {
        'app': app,
        'smh': 'settings',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/apps/details.html', context)


@login_required(login_url='login')
def app_setup(request, app_id):

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

    user.current_app = app
    user.save()

    context = {
        'app': app,
        'smh': 'setup',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/apps/setup.html', context)


@login_required(login_url='login')
def update_app(request, app_id):

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

    user.current_app = app
    user.save()

    context = {
        'app': app,
        'smh': 'apps',
        'form_title': 'Update app',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/apps/update.html', context)


@login_required(login_url='login')
def remove_app(request, app_id):

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

    user.current_app = app
    user.save()
    
    context = {
        'app': app,
        'smh': 'apps',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/apps/remove.html', context)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_apps(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
    user = request.user
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

    response_object = get_apps_list(request)

    return JsonResponse(response_object, status=200)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_app_item(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    app_id = request.GET.get('app_id', None)
    if app_id == None:
        error = "Missing the 'app_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/apps/components/app-item.html",
        context={
            'app': app,
            'render_type': 'display',
            'admin': admin,
        'role': role,
        }
    )

    response_object = {
        'html': html,
        'name': app.name,
    }

    return JsonResponse(response_object, status=200)
    


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_add_app(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    name = None
    if 'name' in data:
        name = data['name']
    if name == None:
        error = "Missing the 'name' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------

    # Create the collection
    app = create_app(request, name)

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/apps/components/app-item.html",
        context={
            'app': app,
            'render_type': 'list',
        }
    )

    redirect = request.build_absolute_uri(reverse('apps', args=()))
    response_object = {
        'app_id': app.app_id,
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_app(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_id = None
    if 'app_id' in data:
        app_id = data['app_id']
    if app_id == None:
        error = "Missing the 'app_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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
    name = None
    if 'name' in data:
        name = data['name']
    if name == None:
        error = "Missing the 'name' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    app.name = name
    app.save()

    html = render_to_string(
        template_name="monitor/apps/components/app-item.html",
        context={
            'app': app,
            'render_type': 'list',
            'admin': admin,
            'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('app_details', args=(app.app_id, )))

    response_object = {
        'message': 'App updated successfully',
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_app_photo(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_id = None
    if 'app_id' in data:
        app_id = data['app_id']
    if app_id == None:
        error = "Missing the 'app_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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
    file_to_save = None
    if 'file_to_save' in data:
        file_to_save = data['file_to_save']
    if file_to_save == None:
        error = "Missing the 'file_to_save' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------
    
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

    app.cover_photo = media_file
    app.save()
    
    # Background processing for thumbnails if the file is an image
    process_thumbnails.delay(media_file.id)
    
    response_object = {
        'message': 'App photo saved successfully',
        'url': media_file.file.url,
        'file_to_save': file_to_save,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_app_photo(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_id = None
    if 'app_id' in data:
        app_id = data['app_id']
    if app_id == None:
        error = "Missing the 'app_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    app.cover_photo = None
    app.save()
    
    response_object = {
        'message': 'App photo removed',
    }

    return JsonResponse(response_object, status=200)




@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_app(request):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin']
    user = request.user
    if not is_ajax(request):
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    data = json.loads(request.body)
    app_id = None
    if 'app_id' in data:
        app_id = data['app_id']
    if app_id == None:
        error = "Missing the 'app_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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
    
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    app.status = 'archived'
    app.save()

    redirect = request.build_absolute_uri(reverse('apps', args=()))

    response_object = {
        'message': 'App archived successfully',
        'redirect': redirect,
    }

    return JsonResponse(response_object, status=200)



def get_apps_list(request):

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
    
    # Query from app apps that the user a part of
    app_users = AppUser.objects.filter(user=user, status='active', app__status='active')
    app_ids = []
    for app_user in app_users:
        app_ids.append(app_user.app.app_id)
    app_items = App.objects.filter(app_id__in=app_ids).order_by('name')

    # Search Term
    if search_term:
        app_items = app_items.filter(
            Q(app_id__icontains=search_term) | 
            Q(name__icontains=search_term)
        )

    # Filters
    if order:
        if order == 'created_at_desc':
            app_items = app_items.order_by('-created_at')
        if order == 'created_at_asc':
            app_items = app_items.order_by('created_at')

    # Pagination
    total_pages = None
    load_more = False
    total_count = 0
    if app_items:
        total_count = len(app_items)
        paginator = Paginator(app_items, per_page=page_size)
        total_pages = paginator.num_pages # Number of total pages
        app_items = paginator.get_page(page) # Filters current queryset
        if page < total_pages:
            load_more = True

    # Generate the Response Object
    app_list_html = []
    for app_object in app_items:
        html = render_to_string(
            template_name="monitor/apps/components/app-item.html",
            context={
                'app': app_object,
                'render_type': render_type,
            }
        )
        app_list_html.append(html)

    results = True
    if len(app_items) == 0:
        results = False

    # Response
    response_object = {
        'success': True,
        'results': results,
        'items': app_list_html,
        'page': page,
        'total_pages': total_pages,
        'load_more': load_more,
        'total_count': total_count,
    }

    return response_object


def create_app(request, name):
    
    user = request.user
    ip_address = get_ip_address(request)

    app = App()
    app.app_id = randomstr()
    app.name = name
    app.created_user = user
    app.save()

    app_user = AppUser()
    app_user.app_user_id = randomstr()
    app_user.user = user
    app_user.email = user.email
    app_user.app = app
    app_user.role = 'admin'
    app_user.save()

    return app