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
def customers(request, app_id):

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
        'smh': 'customers',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/customers/customers.html', context)


@login_required(login_url='login')
def add_customer(request, app_id):

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
        'smh': 'customers',
        'form_title': 'Add customer',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/customers/add.html', context)


@login_required(login_url='login')
def customer_details(request, app_id, customer_id):

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
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'customer': customer,
        'smh': 'customers',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/customers/details.html', context)


@login_required(login_url='login')
def update_customer(request, app_id, customer_id):

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
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'customer': customer,
        'smh': 'customers',
        'form_title': 'Update customer',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/customers/update.html', context)


@login_required(login_url='login')
def remove_customer(request, app_id, customer_id):

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
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        raise Http404()
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    context = {
        'app': app,
        'customer': customer,
        'smh': 'customers',
        'admin': admin,
        'role': role,
    }
    
    return render(request, 'monitor/customers/remove.html', context)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_customers(request, app_id):

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

    response_object = get_customers_list(request, app)

    return JsonResponse(response_object, status=200)



@require_http_methods(['GET'])
@login_required(login_url='login')
def ajax_get_customer_item(request, app_id):

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
    customer_id = request.GET.get('customer_id', None)
    if customer_id == None:
        error = "Missing the 'customer_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/customers/components/customer-item.html",
        context={
            'app': app,
            'customer': customer,
            'render_type': 'display',
            'admin': admin,
        'role': role,
        }
    )

    response_object = {
        'html': html,
        'name': customer.name,
    }

    return JsonResponse(response_object, status=200)
    


@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_add_customer(request, app_id):

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
    customer = create_customer(request, app, name)

    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    html = render_to_string(
        template_name="monitor/customers/components/customer-item.html",
        context={
            'app': app,
            'customer': customer,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('customers', args=(app.app_id, )))
    response_object = {
        'app_id': app.app_id,
        'customer_id': customer.customer_id,
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_update_customer(request, app_id):

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
    customer_id = None
    if 'customer_id' in data:
        customer_id = data['customer_id']
    if customer_id == None:
        error = "Missing the 'customer_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
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

    customer.name = name
    customer.save()

    html = render_to_string(
        template_name="monitor/customers/components/customer-item.html",
        context={
            'app': app,
            'customer': customer,
            'render_type': 'list',
            'admin': admin,
        'role': role,
        }
    )

    redirect = request.build_absolute_uri(reverse('customer_details', args=(app.app_id, customer.customer_id, )))

    response_object = {
        'message': 'Customer updated successfully',
        'redirect': redirect,
        'html': html,
    }

    return JsonResponse(response_object, status=200)



@require_http_methods(['POST'])
@login_required(login_url='login')
def ajax_remove_customer(request, app_id):

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
    customer_id = None
    if 'customer_id' in data:
        customer_id = data['customer_id']
    if customer_id == None:
        error = "Missing the 'customer_id' parameter"
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    customer = Customer.objects.filter(customer_id=customer_id, app=app, status='active').first()
    if not customer:
        error = 'Invalid request'
        create_user_log(request, valid=False, error=error)
        return JsonResponse({'error': error}, status=400)
    # ----------------------------------------------------------------------------------------
    create_user_log(request, data=data)  
    # ----------------------------------------------------------------------------------------

    customer.status = 'archived'
    customer.save()

    redirect = request.build_absolute_uri(reverse('customers', args=(app.app_id, )))

    response_object = {
        'message': 'Customer archived successfully',
        'redirect': redirect,
    }

    return JsonResponse(response_object, status=200)



def get_customers_list(request, app):

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
    customer_items = Customer.objects.filter(app=app, status="active").order_by('name')

    # Search Term
    if search_term:
        customer_items = customer_items.filter(
            Q(customer_id__icontains=search_term) | 
            Q(name__icontains=search_term)
        )

    # Filters
    if order:
        if order == 'created_at_desc':
            customer_items = customer_items.order_by('-created_at')
        if order == 'created_at_asc':
            customer_items = customer_items.order_by('created_at')

    # Pagination
    total_pages = None
    load_more = False
    total_count = 0
    if customer_items:
        total_count = len(customer_items)
        paginator = Paginator(customer_items, per_page=page_size)
        total_pages = paginator.num_pages # Number of total pages
        customer_items = paginator.get_page(page) # Filters current queryset
        if page < total_pages:
            load_more = True

    # Generate the Response Object
    customer_list_html = []
    for customer_object in customer_items:
        html = render_to_string(
            template_name="monitor/customers/components/customer-item.html",
            context={
                'app': app,
                'customer': customer_object,
                'render_type': render_type,
            }
        )
        customer_list_html.append(html)

    results = True
    if len(customer_items) == 0:
        results = False

    # Response
    response_object = {
        'success': True,
        'results': results,
        'items': customer_list_html,
        'page': page,
        'total_pages': total_pages,
        'load_more': load_more,
        'total_count': total_count,
    }

    return response_object


def create_customer(request, app, name):
    
    user = request.user
    ip_address = get_ip_address(request)

    customer = Customer()
    customer.customer_id = randomstr()
    customer.name = name
    customer.app = app
    customer.created_user = user
    customer.save()

    return customer