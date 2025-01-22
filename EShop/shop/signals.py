"""
Signals for the shop application.
"""

import json
from venv import create
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.http import request
from .models import Contact, Order, OrderUpdate
from django.urls import reverse



@receiver(post_save, sender=Contact)
def send_contact_email(sender, instance, created, **kwargs):
    """
    Sends a welcome email to the user after their account is created.
    """
    if created:  # Check if this is a new user
        name = instance.name
        email= instance.email
        phone= instance.phone
        desc=  instance.desc
         
        
        admin_message = f"New contact request:\n\nName: {name}\nEmail: {email}\nPhone: {phone}\nMessage:\n{desc}" 
        send_mail(
            subject="New Contact Request - Mayinsoft.com",
            message=admin_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.EMAIL_HOST_USER],  # Replace with your admin email
            fail_silently=False
        )   
        #confirmation Email to User
        user_message = f"Hello {name},\n\nThank you for contacting Mayinsoft.com. We have received your message:\n\n{desc}\n\nWe will get back to you shortly.\n\nBest,\nMayinsoft.com Team"
        send_mail(
                subject="Thank you for reaching out to Mayinsoft.com",
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
       

@receiver(post_save, sender=Order)
def order_created(sender, instance, created, **kwargs):
    """
    Signal to handle new order creation.
    
    Args:
        sender: The model class (Order)
        instance: The actual instance being saved
        created: Boolean; True if new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        order = instance
        # Create initial order update
        order_update = OrderUpdate.objects.create(
            order_id=instance.order_id,
            update_desc="Order has been placed",
            # Add any other required fields for OrderUpdate
        )
        
        update_desc= order_update.update_desc
        name= order.name
        email= order.email
        phone= order.phone
        address= order.address
        city= order.city
        state= order.state
        zip_code= order.zip_code
        amount= order.amount
        items_json= order.items_json
        order_id= order.order_id
        
        # Parse items_json
        items_dict = json.loads(items_json)

        # Create a formatted string for items
        items_list = []
        
        for key, value in items_dict.items():
            quantity = value[0]
            product_name = value[1]
            items_list.append(f"{product_name}, quantity:{quantity} ")

        # Join items into a single string
        items_str = "\n".join(items_list)
        
        #confirmation Email to User
        user_message=f"""
        Dear {name},
        
        Thank you for your order. Your order ID is: {order_id}
        
        Order Details:
        Items: 
        {items_str}
        
        Amount: ${amount}
        Shipping Address: {address}, {city}, {state}, {zip_code}
        
        Order Status: {update_desc}
        
        We will notify you when your order ships.
        
        Best regards,
        Mayinsoft Team
        """
        try:
            send_mail(
                subject= f'Order Confirmation - Order #{instance.order_id}',
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
@receiver(post_save, sender = OrderUpdate)
def order_status_update(sender,instance,created,**kwargs):
    """
    Signal to handle order status updates.
    
    Args:
        sender: The model class (OrderUpdate)
        instance: The actual instance being saved
        created: Boolean; True if new instance
        **kwargs: Additional keyword arguments
    """
    if created:
        try: 
            order = Order.objects.get(order_id = instance.order_id)
            tracker_url = f"http://{settings.ALLOWED_HOSTS[0]}{reverse('TrackingStatus')}"
            # Send email to customer about order update
            subject = f'Order Status Update - Order #{instance.order_id}'
            user_message = f"""
                Dear {order.name},
                
                Your order #{instance.order_id} has been updated:
                
                Status: {instance.update_desc}
                Your order will be deliverd till {instance.expected_delivery_date}
                Track your order at: {tracker_url}
                
                Best regards,
                Mayinsoft Team
                """
            
            send_mail(
                subject= f'Order Status Update - Order #{instance.order_id}',
                message=user_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                fail_silently=False
                )
        except Order.DoesNotExist:
            print(f"Order not found for order_id: {instance.order_id}")
        except Exception as e:
            print(f"Failed to send email: {str(e)}")  
                