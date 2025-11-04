from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from .models import Category,Shirt,CartItem,Category,ShirtSizeStock,Review
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from .models import Order 
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
import re
from django.views.decorators.http import require_GET
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_http_methods
from django.db import transaction
from datetime import timedelta
from .models import Shirt, Order, OrderItem
from decimal import Decimal
import time

app_name = 'app'

def home(request):
    return render(request,'app/home.html')



def products(request):
    shirts_list = Shirt.objects.exclude(image='').order_by('id')  # Added order_by for consistent pagination
    paginator = Paginator(shirts_list, 6)  # 6 items per page
    
    page = request.GET.get('page')
    try:
        shirts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        shirts = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        shirts = paginator.page(paginator.num_pages)
    
    context = {'shirts': shirts}
    return render(request, 'app/products.html', context)

@login_required
def cart(request):
    return render(request, 'app/cart.html')

@login_required
def checkout_view(request):
    if request.method == "POST":
        # Process the order
        order = Order.objects.create(
            user=request.user,
            product_name=request.POST.get("product_name"),
            quantity=int(request.POST.get("quantity")),
            total_price=float(request.POST.get("total_price")),
            customer_name=request.POST.get("customer_name"),
            country=request.POST.get("country"),
            mobile=request.POST.get("mobile"),
            address=request.POST.get("address"),
            pincode=request.POST.get("pincode"),
            is_ordered=True
        )

        # TEMPORARY use (not stored)
        request.session['payment_method'] = request.POST.get("payment_method")
        request.session['shipping_cost'] = request.POST.get("shipping_cost")

        return redirect('app:order_confirmation')

    # For GET request - handle product details from details page
    product_id = request.GET.get('product_id')
    quantity = request.GET.get('quantity', 1)
    
    try:
        product = Shirt.objects.get(id=product_id)
        quantity = int(quantity)
        total_price = product.price * quantity
        
        context = {
            "product": product,  # Pass the whole product object
            "product_name": product.model_name,
            "quantity": quantity,
            "total_price": total_price,
            "unit_price": product.price,
        }
        return render(request, 'app/checkout.html', context)
    
    except (Shirt.DoesNotExist, ValueError):
        messages.error(request, "Invalid product selected")
        return redirect('app:products')


@login_required
def order_confirmation(request):
    latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
    return render(request, 'app/order_confirmation.html', {'order': latest_order})

@login_required

def details(request, Shirtid):
    shirt = get_object_or_404(Shirt, pk=Shirtid)
    size_stocks = ShirtSizeStock.objects.filter(shirt=shirt)

    # Convert queryset to list of dictionaries
    size_stock_data = [
        {
            'size': s.size,
            'quantity': s.quantity
        } for s in size_stocks
    ]

    context = {
        'shirt': shirt,
        'size_stocks': size_stocks,
        'size_stock_data': size_stock_data,  # serialized data
    }
    return render(request, 'app/details.html', context)

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        profile_pic = request.FILES.get('profile_pic')

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'app/register.html', {'error': 'Username already exists'})
        
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            profile_pic=profile_pic
        )
        return redirect('app:login')
    
    return render(request, 'app/register.html')

@login_required
def profile_view(request):
    user = request.user
    orders = Order.objects.filter(user=user, is_ordered=True).order_by('-created_at')
    return render(request, 'app/profile.html', {
        'user': user,
        'orders': orders
    })

def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            auth_login(request, user)
            return redirect('app:products')
        else:
            return render(request, 'app/login.html', {'error': 'Invalid credentials'})
        
    return render(request, 'app/login.html')



# @login_required
# def profile_view(request):
#     if request.method == 'POST':
#         # Your existing profile update code...
#         pass
    
#     # Get orders from database
#     orders = Order.objects.filter(user=request.user).order_by('-ordered_at')
    
#     context = {
#         'user': request.user,
#         'orders': orders
#     }
#     return render(request, 'app/profile.html', context)

def logout(request):
    auth_logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('app:login')

def search_view(request):
    query = request.GET.get('q', '').strip()
    selected_categories = request.GET.getlist('category', [])
    selected_prices = request.GET.getlist('price', [])
    
    products = Shirt.objects.all().only('id', 'model_name', 'description', 'price', 'category', 'image')

    if query:
        products = products.filter(
            Q(model_name__icontains=query) |
            Q(description__icontains=query)
        )
    
    if selected_categories:
        products = products.filter(category__name__in=selected_categories)
    
    if selected_prices:
        price_query = Q()
        for price_range in selected_prices:
            try:
                min_price, max_price = map(int, price_range.split('-'))
                price_query |= Q(price__gte=min_price, price__lte=max_price)
            except (ValueError, AttributeError):
                continue
        products = products.filter(price_query)
    
    categories = Category.objects.all()
    
    context = {
        'results': products,
        'query': query,
        'categories': categories,
        'selected_categories': selected_categories,
        'selected_prices': selected_prices,
    }
    
    return render(request, 'app/search.html', context)
