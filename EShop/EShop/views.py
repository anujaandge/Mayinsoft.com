import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth  import authenticate,  login, logout
from django.contrib import messages
from shop.models import Product, Contact, Order, OrderUpdate
import openai
from math import ceil

# Set OpenAI API Key
openai.api_key = settings.OPENAI_API_KEY
# Create your views here.

def index(request):
    return render(request,'index.html')


#Authentication Apis
def handleSignUp(request):
    if request.method=="POST":
        # Get the post parameters
        username=request.POST['username']
        email=request.POST['email']
        fname=request.POST['fname']
        lname=request.POST['lname']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        # check for errorneous input
        if len(username)>10:
            messages.error(request, " Your user name must be under 10 characters")
            return redirect('ShopHome')

        if not username.isalnum():
            messages.error(request, " User name should only contain letters and numbers")
            return redirect('ShopHome')
        if (pass1!= pass2):
            messages.error(request, " Passwords do not match")
            return redirect('ShopHome')
        
        # Create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name= fname
        myuser.last_name= lname
        myuser.save()
        messages.success(request, " Your Mayinsoft account has been successfully created")
        return redirect('ShopHome')

    else:
        return HttpResponse("404 - Not found")   
    
def handleLogin(request):
    if request.method=="POST":
        # Get the post parameters
        loginusername=request.POST['loginusername']
        loginpassword=request.POST['loginpassword']

        user=authenticate(username= loginusername, password= loginpassword)
        if user is not None:
            login(request, user)
            messages.success(request, "Successfully Logged In")
            return redirect("ShopHome")
        else:
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("ShopHome")

    return HttpResponse("404- Not found")

def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully logged out")
    return redirect('ShopHome')    
        
        
def detect_intent(user_input):
    if "recommend" in user_input or "suggest" in user_input:
        return "recommendation"
    elif "track" in user_input:
        return "order_tracking"
    elif "details of" in user_input:
        return "product_details"
    else:
        return "general_query"

        
def chatbot_response(request):
    if request.method == "POST":
        data = json.loads(request.body)

        user_input = data.get('message', '').lower()
        print(f"Received message: {user_input}")
        
        # Fetch categories dynamically from the database
        categories = Product.objects.values_list('category', flat=True).distinct()
        print(f"Available categories: {categories}")

        
        # Dynamic Product Recommendation (e.g., "recommend books", "suggest shoes", etc.)
        if "recommend" in user_input or "suggest" in user_input:
            # Check if the user input matches any category partially
            recommended_category = None
            for category in categories:
                if any(word in category.lower() for word in user_input.split()):
                    recommended_category = category
                    break

            print(recommended_category)
            if recommended_category:
                # Query products by category (case-insensitive search)
                products = Product.objects.filter(category__icontains=recommended_category).all()[:5]  # Adjust as needed
                if products:
                    response = f"Here are some recommended {recommended_category}:\n"
                    for product in products:
                        response += f"\n- {product.product_name} (${product.price})\n"  # Correct field name
                else:
                    response = f"Sorry, I couldn't find any {recommended_category} recommendations at the moment."
            else:
                response = "Sorry, I couldn't detect a category in your recommendation request. Please try again."

            return JsonResponse({'reply': response})
     
        # Product Details (e.g., "details of Nike shoes")
        elif "details of" in user_input:
            product_name = user_input.replace("details of", "").strip()
            try:
                product = Product.objects.get(product_name__icontains=product_name)  # Use product_name, not name
                response = f"{product.product_name} - ${product.price}\n{product.desc}"  # Use desc, not des
            except Product.DoesNotExist:
                response = "Sorry, I couldn't find that product."
            return JsonResponse({'reply': response})
        
        
        # Order Tracking (e.g., "track order 12345")
        elif "track" in user_input:
            # Extract order ID from user input
            order_id = ''.join(filter(str.isdigit, user_input))  # Extract digits (assumes order ID is numeric)
            print(order_id)
            if order_id:
                try:
                    order = Order.objects.get(order_id=order_id)
                    # Get the latest update from the OrderUpdate model
                    latest_update = OrderUpdate.objects.filter(order_id=order_id).order_by('-timestamp').first()
            
                     # Construct the response
                    response = (f"Order ID: {order.order_id}\n"
                        f"\nStatus: {latest_update.update_desc if latest_update else 'No updates available'}\n"
                        f"\nExpected Delivery: {latest_update.expected_delivery_date if latest_update else 'No updates available'}")
                                
                except Order.DoesNotExist:
                    response = f"Sorry, I couldn't find any order with ID {order_id}."
            else:
                response = "Please provide a valid order ID to track your order."

            return JsonResponse({'reply': response})
        
        # OpenAI Chat-based responses (fallback for other queries)
        else:
            try:
                # Updated API call for general queries
                response = openai.Completion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_input}],
                    max_tokens=150
                )
                chatbot_reply = response['choices'][0]['message']['content'].strip()
                return JsonResponse({'reply': chatbot_reply})
            except Exception as e:
                return JsonResponse({'error': f"Error with OpenAI API: {str(e)}"}, status=500)

    return JsonResponse({'error': 'Invalid request'})
