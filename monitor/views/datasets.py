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
def datasets(request, app_id):

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
    
    context = {
        'app': app,
        'smh': 'datasets',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/datasets/datasets.html', context)


@login_required(login_url='login')
def add_dataset(request, app_id):

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

    context = {
        'app': app,
        'smh': 'datasets',
        'form_title': 'Add dataset',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/datasets/add.html', context)


@login_required(login_url='login')
def dataset_details(request, app_id, dataset_id):

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
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'dataset': dataset,
        'smh': 'datasets',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/datasets/details.html', context)


@login_required(login_url='login')
def update_dataset(request, app_id, dataset_id):

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
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'dataset': dataset,
        'smh': 'datasets',
        'form_title': 'Update dataset',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/datasets/update.html', context)


@login_required(login_url='login')
def remove_dataset(request, app_id, dataset_id):

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
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'dataset': dataset,
        'smh': 'datasets',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/datasets/remove.html', context)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_datasets(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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

    response_object = get_datasets_list(request, app)

    return JsonResponse(response_object, status=200)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_dataset_item(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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
    dataset_id = request.GET.get('dataset_id', None)
    if dataset_id == None:
        error = "Missing the 'dataset_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/datasets/components/dataset-item.html",
        context={
            'app': app,
            'dataset': dataset,
            'render_type': 'display',
            'admin': admin,
        'role': role,
        }
    )

    response_object = {
        'html': html,
        'name': dataset.name,
    }

    return JsonResponse(response_object, status=200)
    


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_add_dataset(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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
    name = None
    if 'name' in data:
        name = data['name']
    if name == None:
        error = "Missing the 'name' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------

    # Create the collection
    dataset = create_dataset(request, app, name)

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/datasets/components/dataset-item.html",
        context={
            'app': app,
            'dataset': dataset,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('datasets', args=(app.app_id, )))
    response_object = {
        'app_id': app.app_id,
        'dataset_id': dataset.dataset_id,
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_dataset(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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
    dataset_id = None
    if 'dataset_id' in data:
        dataset_id = data['dataset_id']
    if dataset_id == None:
        error = "Missing the 'dataset_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
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

    dataset.name = name
    dataset.save()

    html = render_to_string(
        template_name="monitor/datasets/components/dataset-item.html",
        context={
            'app': app,
            'dataset': dataset,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('dataset_details', args=(app.app_id, dataset.dataset_id, )))

    response_object = {
        'message': 'Dataset updated successfully',
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_dataset(request, app_id):

    # ----------------------------------------------------------------------------------------
    # Users, Permissions, and Params
    roles = ['admin', 'user']
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
    dataset_id = None
    if 'dataset_id' in data:
        dataset_id = data['dataset_id']
    if dataset_id == None:
        error = "Missing the 'dataset_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    dataset = Dataset.objects.filter(dataset_id=dataset_id, app=app, status='active').first()
    if not dataset:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    dataset.status = 'archived'
    dataset.save()

    redirect = request.build_absolute_uri(reverse('datasets', args=(app.app_id, )))

    response_object = {
        'message': 'Dataset archived successfully',
        'redirect': redirect,
    }

    return JsonResponse(response_object, status=200)



def get_datasets_list(request, app):

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
    
    # Query from app regions that the user a part of
    dataset_items = Dataset.objects.filter(app=app, status="active").order_by('name')

    # Search Term
    if search_term:
        dataset_items = dataset_items.filter(
            Q(dataset_id__icontains=search_term) | 
            Q(name__icontains=search_term)
        )

    # Filters
    if order:
        if order == 'created_at_desc':
            dataset_items = dataset_items.order_by('-created_at')
        if order == 'created_at_asc':
            dataset_items = dataset_items.order_by('created_at')

    # Pagination
    total_pages = None
    load_more = False
    total_count = 0
    if dataset_items:
        total_count = len(dataset_items)
        paginator = Paginator(dataset_items, per_page=page_size)
        total_pages = paginator.num_pages # Number of total pages
        dataset_items = paginator.get_page(page) # Filters current queryset
        if page < total_pages:
            load_more = True

    # Generate the Response Object
    dataset_list_html = []
    for dataset_object in dataset_items:
        html = render_to_string(
            template_name="monitor/datasets/components/dataset-item.html",
            context={
                'app': app,
                'dataset': dataset_object,
                'render_type': render_type,
            }
        )
        dataset_list_html.append(html)

    results = True
    if len(dataset_items) == 0:
        results = False

    # Response
    response_object = {
        'success': True,
        'results': results,
        'items': dataset_list_html,
        'page': page,
        'total_pages': total_pages,
        'load_more': load_more,
        'total_count': total_count,
    }

    return response_object


def create_dataset(request, app, name):
    
    user = request.user
    ip_address = get_ip_address(request)

    dataset = Dataset()
    dataset.dataset_id = randomstr()
    dataset.name = name
    dataset.app = app
    dataset.created_user = user
    dataset.save()

    return dataset