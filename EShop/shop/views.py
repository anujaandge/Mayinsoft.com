from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
from .models import Product, Contact, Order, OrderUpdate
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from math import ceil
import json
# from .Paytm import Checksum
# MERCHANT_KEY = 'kbzk1DSbJiv_03p5'




# Create your views here.

def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)

def about(request):
    return render(request, 'shop/about.html')

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name','')
        email=request.POST.get('email','')
        phone=request.POST.get('phone','')
        desc=request.POST.get('desc','')
        contact=Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        
        # Email to Admin
        admin_message = f"New contact request:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{desc}"
        send_mail(
            subject="New Contact Request - Mayinsoft.com",
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['your admin email'],  # Replace with your admin email
        )
        #confirmation Email to User
        user_message = f"Hello {name},\n\nThank you for contacting Mayinsoft.com. We have received your message:\n\n{desc}\n\nWe will get back to you shortly.\n\nBest,\nMayinsoft.com Team"
        send_mail(
            subject="Thank you for reaching out to Mayinsoft.com",
            message=user_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        # Redirect to a thank-you page or display success message
        return redirect('contact_success')  
    return render(request, 'shop/contact.html')

def contact_success(request):
    return render(request, 'shop/contact_success.html')


def tracker(request):
    if request.method == 'POST':
        orderId = request.POST.get('orderId')
        email = request.POST.get('tracker_email')
        print(orderId ,email)
        
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
    query = request.GET.get('search')
    allProds = []

    # Check if query is valid
    if not query or len(query) < 3:
        params = {'allProds': allProds, 'msg': "Please make sure to enter a relevant search query (at least 3 characters)."}
        return render(request, 'shop/search.html', params)

    # Prepare variations of the query for broader matching
    query_variations = [query, query.rstrip('s'), query + 's']

    # Get all categories and filter products based on query
    catProds = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catProds}
    for cat in cats:
        # Filter products within the category based on the search query and its variations
        prod = Product.objects.filter(
            Q(category=cat) &
            (
                Q(desc__icontains=query) | Q(desc__icontains=query_variations[1]) | Q(desc__icontains=query_variations[2]) |
                Q(product_name__icontains=query) | Q(product_name__icontains=query_variations[1]) | Q(product_name__icontains=query_variations[2]) |
                Q(category__icontains=query) | Q(category__icontains=query_variations[1]) | Q(category__icontains=query_variations[2])
            )
        )
        n = prod.count()
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        
        if n != 0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds': allProds, 'msg': ""}
    if not allProds:
        params['msg'] = "No products match your search criteria."

    return render(request, 'shop/search.html', params)        

def productView(request, myid):
    product=Product.objects.filter(id=myid)
    print(f"Product {product}")
    return render(request, 'shop/prodView.html',{'product':product[0]})

# @login_required(login_url='/login')
def checkout(request):
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


