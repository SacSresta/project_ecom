from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
import time
from .models import Order, OrderItems
from store.models import Product, Profile, ProductVariant

@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    # Adding a pause for PayPal to send IPN data
    time.sleep(5)
    
    # Grab the info that PayPal sends
    paypal_obj = sender
    # Grab the invoice
    my_Invoice = paypal_obj.invoice
    
    # Match the invoice to the Order invoice
    try:
        # Lookup the order
        my_Order = Order.objects.get(invoice=my_Invoice)
        
        # Check if the order has already been marked as paid
        if not my_Order.paid:
            # Record the Order was paid
            my_Order.paid = True
            my_Order.save()

            # Get the associated order items
            order_items = OrderItems.objects.filter(order_id=my_Order.id)
            
            # Reduce stock for each product
            for item in order_items:
                try:
                    variant = ProductVariant.objects.get(id=item.variant_id)
                    if variant.stock_qty >= item.quantity:
                        variant.stock_qty -= item.quantity
                        variant.save()
                    else:
                        # Handle the case where stock is insufficient
                        # You might want to notify someone or log this event
                        pass
                except ProductVariant.DoesNotExist:
                    # Handle the case where the product variant is not found
                    pass

            # Optionally clear the cart or perform other actions
            if my_Order.user:
                profile = Profile.objects.filter(user=my_Order.user).first()
                if profile:
                    profile.old_cart = ""
                    profile.save()
            
            # Send email with order summary
            send_order_confirmation_email(my_Order)
            
            print(f'Payment received for Invoice: {my_Invoice}')
            print(f'Amount Paid: {paypal_obj.mc_gross}')
        else:
            print(f'Order with Invoice {my_Invoice} has already been processed.')

    except Order.DoesNotExist:
        print(f'Order with Invoice {my_Invoice} does not exist.')

def send_order_confirmation_email(order):
    subject = f'Order Confirmation - Invoice {order.invoice}'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = order.email
    print("Order Details:",order)
    # Prepare context for email template
    context = {
        'order': order,
        'order_items': OrderItems.objects.filter(order_id=order.id),
        'total_amount': order.amount_paid
    }

    # Render email body from template
    email_body = render_to_string('payment/order_confirmation.html', context)

    # Send email
    send_mail(subject, '', from_email, [to_email], html_message=email_body)