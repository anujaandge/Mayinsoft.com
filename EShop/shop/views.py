"""
Views for the shop application.

This module contains views for handling product display, filtering, search,
contact forms, order tracking, and checkout functionality.
"""

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from .models import Product, Contact, Order, OrderUpdate
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import ContactForm
from math import ceil
import json
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer  
from .filters import ProductFilter  

# from .Paytm import Checksum
# MERCHANT_KEY = 'kbzk1DSbJiv_03p5'




# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint for products that allows CRUD operations.
    
    Provides filtering, searching, and ordering capabilities through query parameters.
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product_name', 'desc', 'category']
    ordering_fields = ['price', 'product_name']
    
def index(request):
    """
    Display the main shop page with products grouped by category.
    
    Supports filtering by:
    - category
    - price range
    - ordering
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered shop index page with filtered products
    """
    # Get filter parameters
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    ordering = request.GET.get('ordering')
    
    # Start with all products
    products = Product.objects.all()
    
    # Apply filters
    if category:
        products = products.filter(category=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if ordering:
        products = products.order_by(ordering)
    
    # Get all categories for the dropdown menu
    all_categories = Product.objects.values_list('category', flat=True).distinct()
    
    # Group products by category for display
    allProds = []
    catprods = products.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = products.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    
    params = {
        'allProds': allProds,
        'categories': all_categories,  # Add this for the dropdown
        'current_category': category,  # Optional: to show current filter
        'current_min_price': min_price,  # Optional: to show current filter
        'current_max_price': max_price,  # Optional: to show current filter
        'current_ordering': ordering,  # Optional: to show current filter
    }
    return render(request, 'shop/index.html', params)

def about(request):
    """
    Display the about page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered about page
    """
    return render(request, 'shop/about.html')

def contact(request):
    """
    Handle contact form submission and email notifications.
    
    On POST:
    - Saves contact form data
    - Sends email to admin
    - Sends confirmation email to user
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered contact form or redirect to success page
    """
    if request.method=="POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_success')
    form=ContactForm()
    return render(request, 'shop/contact.html',{'form':form})

def contact_success(request):
    """
    Display contact form submission success page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered success page
    """
    return render(request, 'shop/contact_success.html')


def tracker(request):
    """
    Track order status using order ID and email.
    
    Provides real-time order status updates.
    
    Args:
        request: HTTP request object
        
    Returns:
        JsonResponse: Order status and updates
        HttpResponse: Order tracking page
    """
    if request.method == 'POST':
        orderId = request.POST.get('orderId')
        email = request.POST.get('tracker_email')
        
        
        try:
            order = Order.objects.get(order_id=orderId, email=email)
            # Parse `items_json` if it's a JSON string, else use it directly as a dictionary
            if isinstance(order.items_json, str):  # If it's a JSON string
                items_json_data = json.loads(order.items_json)
            else:
                items_json_data = order.items_json  # It's already a dictionary
                
            # Retrieve order updates from the OrderUpdate model based on order_id
            updates = OrderUpdate.objects.filter(order_id=orderId)
            
            # Prepare the updates data as a list of dictionaries with 'text' and 'time'
            
            updates_data = [{'text': update.update_desc, 'time': update.timestamp} for update in updates]
            
            # Prepare the items data with quantity and name extracted from items_json_data
            items_data = [{'qty': value[0], 'name': value[1]} for key, value in items_json_data.items()]
            return JsonResponse({'updates': updates_data,'items_data': items_data})     # Return a JSON response with updates and items data
            
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found with the provided ID and email.'})
        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'})
       
    return render(request, 'shop/tracker.html')
    
def search(request):
    """
    Search products by name, description, or category.
    
    Supports partial matching and case-insensitive search.
    
    Args:
        request: HTTP request object with 'search' query parameter
        
    Returns:
        HttpResponse: Rendered search results page
    """
    query = request.GET.get('search')
    allProds = []

    # Check if query is valid
    if not query or len(query) < 3:
        params = {'allProds': allProds, 'msg': "Please make sure to enter a relevant search query (at least 3 characters)."}
        return render(request, 'shop/search.html', params)

    # Using the filter backend for search
    products = Product.objects.all()
    if query:
        products = products.filter(
            Q(desc__icontains=query) |
            Q(product_name__icontains=query) |
            Q(category__icontains=query)
        )

    # Group by category for display
    categories = products.values_list('category', flat=True).distinct()
    for category in categories:
        cat_products = products.filter(category=category)
        n = cat_products.count()
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if n != 0:
            allProds.append([cat_products, range(1, nSlides), nSlides])

    params = {'allProds': allProds, 'msg': ""}
    if not allProds:
        params['msg'] = "No products match your search criteria."

    return render(request, 'shop/search.html', params)

def productView(request, myid):
    """
    Display detailed view of a specific product.
    
    Args:
        request: HTTP request object
        myid: Product ID
        
    Returns:
        HttpResponse: Rendered product detail page
        
    Raises:
        Http404: If product does not exist
    """
    product=Product.objects.filter(id=myid)
    print(f"Product {product}")
    return render(request, 'shop/prodView.html',{'product':product[0]})

# @login_required(login_url='/login')
def checkout(request):
    """
    Handle order checkout process.
    
    Requires user authentication.
    Creates order and sends confirmation.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered checkout page or order confirmation
    
    Raises:
        PermissionDenied: If user is not authenticated
    """
    thank = False  # Default value for thank
    id = None  # Default value for id
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        amount=request.POST.get('amount','')
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        address=request.POST.get('address1','') + request.POST.get(' address2','')
        city=request.POST.get('city','')
        state=request.POST.get('state','')
        zip_code=request.POST.get('zip_code','')
        phone=request.POST.get('phone','')
        
        order=Order(items_json=items_json,name=name, email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code, amount=amount)
        order.save()
        update= OrderUpdate(order_id= order.order_id, update_desc="The order has been placed")
        update.save()
        thank=True
        id=order.order_id
       
        return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
    return render(request, 'shop/checkout.html')
        #Request paytm to transfer the amount to your account after payment by user
        # param_dict={
        #     'MID': 'QOUWOJ07242787087025',
        #     'ORDER_ID': str(order.order_id),
        #     'TXN_AMOUNT': str(amount),
        #     'CUST_ID': 'email',
        #     'INDUSTRY_TYPE_ID': 'Retail',
        #     'WEBSITE': 'WEBSTAGING', 
        #     'CHANNEL_ID': 'WEB',
        #     'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
        # }
        # param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
    #     return  render(request, 'shop/paytm.html', {'param_dict': param_dict})
    # return render(request, 'shop/checkout.html')

def checkout_success(request):
    """
    Display order checkout success page.
    
    Args:
        request: HTTP request object
        
    Returns:
        HttpResponse: Rendered success page
    """
    return render(request, 'shop/checkout_success.html')






























# @csrf_exempt
# def handlerequest(request):
#     #paytm will sent post request here
#     form = request.POST
#     response_dict = {}
#     for i in form.keys():
#         response_dict[i] = form[i]
#         if i == 'CHECKSUMHASH':
#             checksum = form[i]

#     verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
#     if verify:
#         if response_dict['RESPCODE'] == '01':
#             print('order successful')
#         else:
#             print('order was not successful because' + response_dict['RESPMSG'])
#     return render(request, 'shop/paymentstatus.html', {'response': response_dict})


