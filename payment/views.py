from django.shortcuts import render,redirect
from django.http import JsonResponse
from cart.cart import Cart
from payment.forms import ShippingForm,PaymentForm,PickupForm
from payment.models import ShippingAddress,Order,OrderItems,PAIDORDER
from django.contrib import messages
from django.contrib.auth.models import User
from store.models import Product,Profile
from .models import Order, OrderItems, ProductVariant
import datetime
from django.views.decorators.csrf import csrf_exempt

#Import some Paypal Stuff
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid #unique user id for duplicate orders

#Email stuff
from django.core.mail import send_mail
import stripe
from .hooks import send_order_confirmation_email
# This is your test secret API key.
stripe.api_key =settings.STRIPE_SECRET_KEY

import traceback
from django.db import transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import stripe
from .models import Order, OrderItems, ProductVariant, Profile

def stripe_success(request):
    return render(request,'payment/payment_success.html',{})

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        print(f'Invalid payload: {e}')
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError as e:
        print(f'Invalid signature: {e}')
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    print(f'Event received: {event.type}')

    if event.type == 'checkout.session.completed':
        session = event.data.object
        print(f'Handling checkout session completed event: {session.id}')
        handle_payment_success(session)
    else:
        print(f'Unhandled event type: {event.type}')

    return JsonResponse({'status': 'success'}, status=200)

@transaction.atomic
def handle_payment_success(session):
    invoice = session.metadata.get('invoice')


    if not invoice:
        return

    try:
        order = Order.objects.select_for_update().get(invoice=invoice)

        if order.paid:
            print(f'Order {order.id} already marked as paid')
            return

        if session.payment_status == 'paid':
            order.paid = True
            order.save()
            send_order_confirmation_email(order)
        else:
            print(f'Payment not completed for session {session.id}. Status: {session.payment_status}')
            return

        order_items = OrderItems.objects.filter(order_id=order.id)

        for item in order_items:
            try:
                variant = ProductVariant.objects.get(id=item.variant_id)
                if variant.stock_qty >= item.quantity:
                    variant.stock_qty -= item.quantity
                    variant.save()
                else:
                    print(f'Insufficient stock for variant ID: {item.variant_id}')
            except ProductVariant.DoesNotExist:
                print(f'ProductVariant with ID {item.variant_id} does not exist')

        if order.user:
            profile = Profile.objects.filter(user=order.user).first()
            if profile:
                profile.old_cart = ""
                profile.save()

    except Order.DoesNotExist:
        print(f'Order with Invoice {invoice} does not exist.')
    except Exception as e:
        traceback.print_exc()

# Rest of the code remains the same...
def stripe_checkout(request):
        return render(request,'payment/stripe_checkout.html',{})
def stripe_payment(request):
    if request.method == 'POST':
        total_amount = request.POST.get('total_amount')
        
        # Convert the total amount to the correct format for Stripe
        total_amount_cents = int(float(total_amount) * 100)

        try:
            # Get the cart
            cart = Cart(request)
            cart_products = cart.get_prods()
            quantities = cart.get_quants()
            subtotal = cart.cart_total()
            variants = cart.get_prods()

            # Get shipping option
            shipping_option = request.POST.get('shipping_option', 'delivery')
            delivery_option = request.POST.get('delivery_option', 'standard')

            # Calculate shipping cost
            if shipping_option == 'pickup':
                shipping_cost = 0
            elif delivery_option == 'express':
                shipping_cost = 25
            else:
                shipping_cost = 15

            # Calculate total with shipping
            total_with_shipping = subtotal + shipping_cost

            # Gather Order Info from POST data
            full_name = request.POST.get('shipping_full_name', '')
            email = request.POST.get('shipping_email', '')
            shipping_address = f"{request.POST.get('shipping_address1', '')}\n{request.POST.get('shipping_address2', '')}\n{request.POST.get('shipping_city', '')}\n{request.POST.get('shipping_state', '')}\n{request.POST.get('shipping_country', '')}"
            phone_number = request.POST.get('shipping_phone', '')
            amount_paid = total_with_shipping
            
        

            # Get the host
            host = request.get_host()
            
            # Create Invoice Number
            my_Invoice = str(uuid.uuid4())

            # Create order
            create_order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=total_amount,
                invoice=my_Invoice,
                phone_number = phone_number
            )
            print(phone_number)
            print(total_amount,"Amount_paid")

            # Add Order Items
            order_id = create_order.pk
            for variant in variants:
                price = variant.product.sale_price if variant.product.is_sale else variant.product.price
                for key, value in quantities.items():
                    if int(key) == variant.id:
                        for qty, size in value.items():
                            OrderItems.objects.create(
                                order_id=order_id,
                                product_id=variant.product.id,
                                variant_id=variant.id,
                                quantity=int(float(qty)),
                                price=price
                            )
                                    
            # Clear the cart from the database (old_cart field)
            if request.user.is_authenticated:
                profile = Profile.objects.filter(user=request.user).first()
                if profile:
                    profile.old_cart = ""
                    profile.save()

            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'aud',
                            'product_data': {
                                'name': 'Order Total (including shipping)',
                            },
                            'unit_amount': int(total_amount_cents),  # Amount in cents
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=f'https://{host}{reverse("payment_success")}',
                cancel_url=f'https://{host}{reverse("payment_failed")}',
                metadata={'invoice': create_order.invoice}  # Include invoice ID in metadata
            )
            return redirect(checkout_session.url, code=303)

        except stripe.error.StripeError as e:
            print(f"Stripe error: {str(e)}")
            messages.error(request, f"An error occurred with the payment processor: {str(e)}")
            return redirect('cart_summary')
        except Exception as e:
            print(f"Unexpected error in stripe_payment view: {str(e)}")
            messages.error(request, "An unexpected error occurred. Please try again later.")
            return redirect('cart_summary')
#Sending emails
def submit_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Logic to handle the email (e.g., saving to a database, sending a confirmation email)
        
        # Example: Sending a confirmation email
        send_mail(
            'Order Confirmation',
            'Thank you for your purchase. Your shipping details will be sent shortly.',
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )
        for key in list(request.session.keys()):
                    if key =="session_key":
                        #delete the key
                        del request.session[key]
        
        return redirect('home')  #Redirect to success page or show a success message

    return render(request, 'home.html')

def orders(request,pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #Get the order
        order = Order.objects.get(id=pk)
        #Get the order items
        items = OrderItems.objects.filter(order=pk)
        
        if request.POST:
            status = request.POST['shipping_status']
            #check if true or false
            if status == "true":
                order = Order.objects.filter(id=pk)
                #Update the status
                now = datetime.datetime.now()
                order.update(shipped = True,date_shipped = now)
            else:
                order = Order.objects.filter(id=pk)
                #Update the status
                order.update(shipped = False)
                
            messages.success(request,"Shipping Status Updated")
            return redirect('home')
                
                
        return render(request,'payment/orders.html', {"order":order,"items":items})
    else:
        messages.success(request,"Access Denied")
        return redirect('home')

def not_shipped_dash(request):
    
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False, paid=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id = num)
            #Update the status
            now = datetime.datetime.now()
            order.update(shipped = True,date_shipped = now)

            messages.success(request,"Shipping Status Updated")
        
        return render(request, "payment/not_shipped_dash.html",{'orders':orders})
    else:
        messages.success(request,"Access Denied")
        return redirect('home')

def shipped_dash(request):
    
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped = True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            order = Order.objects.filter(id = num)
            #Update the status
            now = datetime.datetime.now()
            order.update(shipped = False)
            messages.success(request,"Shipping Status Updated")
        return render(request, "payment/shipped_dash.html",{'orders':orders})
    else:
        messages.success(request,"Access Denied")
        return redirect('home')

def billing_info(request):
    if request.method == 'POST':
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        subtotal = cart.new_total()
        variants = cart.get_prods()

        # Get the shipping method
        shipping_method = request.POST.get('shipping_method')

        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping
        print(my_shipping)
        
        # Get the total price and shipping fee from the form
        total_with_shipping = request.POST.get('total_with_shipping')
        shipping_fee = request.POST.get('shipping_fee')

        # Get the host
        host = request.get_host()
        
        # Create Invoice Number
        my_Invoice = str(uuid.uuid4())

        # Store order details in session for later use
        if shipping_method == 'pickup':
            request.session['order_details'] = {
                'full_name': my_shipping.get('shipping_full_name', ''),
                'email': my_shipping.get('shipping_email', ''),
                'shipping_address': 'Pickup',
                'amount_paid': total_with_shipping,
                'invoice': my_Invoice,
                'phone_number': my_shipping.get('shipping_phone', ''),
            }
            print(request.session['order_details'])
        else:
            request.session['order_details'] = {
                'full_name': my_shipping.get('shipping_full_name', ''),
                'email': my_shipping.get('shipping_email', ''),
                'shipping_address': f"{my_shipping.get('shipping_address1', '')}\n{my_shipping.get('shipping_address2', '')}\n{my_shipping.get('shipping_city', '')}\n{my_shipping.get('shipping_state', '')}\n{my_shipping.get('shipping_country', '')}",
                'amount_paid': total_with_shipping,
                'invoice': my_Invoice,
                'phone_number':my_shipping.get('shipping_phone', ''),
            }

        # Create PayPal Form Dictionary
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': total_with_shipping,
            'item_name': 'Book Order',
            'invoice': my_Invoice,
            'currency_code': 'AUD',
            'notify_url': f'https://{host}{reverse("paypal-ipn")}',
            'return_url': f'https://{host}{reverse("payment_success")}',
            'cancel_return': f'https://{host}{reverse("payment_failed")}',
        }

        # Create actual PayPal button
        paypal_form = PayPalPaymentsForm(initial=paypal_dict)

        # Get The Billing Form
        billing_form = PaymentForm()

        # Render the template with context
        return render(request, "payment/billing_info.html", {
            "paypal_form": paypal_form,
            "cart_products": cart_products,
            "quantities": quantities,
            "subtotal": subtotal,
            "shipping_info": my_shipping,
            "billing_form": billing_form,
            "variants": variants,
            "total_with_shipping": total_with_shipping,
            "shipping_fee": shipping_fee,
            "shipping_method": shipping_method,
        })
    
    else:
        messages.error(request, "Access Denied")
        return redirect('home')

def payment_success(request):
    # Retrieve order details from session
    order_details = request.session.get('order_details', {})
    
    
    if order_details:
        # Create Order
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(
                user=user,
                full_name=order_details['full_name'],
                email=order_details['email'],
                shipping_address=order_details['shipping_address'],
                amount_paid=order_details['amount_paid'],
                invoice=order_details['invoice'],
                phone_number = order_details['phone_number']
            )
        else:
            create_order = Order(
                full_name=order_details['full_name'],
                email=order_details['email'],
                shipping_address=order_details['shipping_address'],
                amount_paid=order_details['amount_paid'],
                invoice=order_details['invoice'],
                phone_number = order_details['phone_number']
            )
        
        create_order.save()

        # Add Order Items
        cart = Cart(request)
        variants = cart.get_prods()
        quantities = cart.get_quants()
        
        for variant in variants:
            price = variant.product.sale_price if variant.product.is_sale else variant.product.price
            for key, value in quantities.items():
                if int(key) == variant.id:
                    for qty, size in value.items():
                        OrderItems.objects.create(
                            order=create_order,
                            product=variant.product,
                            variant=variant,
                            quantity=int(float(qty)),
                            price=price
                        )

        for key in list(request.session.keys()):
            if key =="session_key":
                #delete the key
                del request.session[key]

        messages.success(request, "Order Placed")
        return render(request, "payment/payment_success.html", {})
    else:
        messages.error(request, "There was an error processing your order.")
        return redirect('home')

def payment_failed(request):
    messages.error(request, "Your payment was unsuccessful. Please try again.")
    return redirect('billing_info')



def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    new_total = cart.new_total()
    total = cart.cart_total()
    discount = total - new_total
    variants = cart.get_prods()
    standard_shipping = 15
    express_shipping = 25
    if cart_products:
        
        # Get or set the shipping method
        shipping_method = request.GET.get('shipping_method', 'pickup')
        
        # Calculate total with shipping
        if shipping_method == 'standard':
            total_with_shipping = new_total + standard_shipping
        elif shipping_method == 'express':
            total_with_shipping = new_total + express_shipping
        else:
            total_with_shipping = new_total

        # Only create shipping form if not pickup
        shipping_form = None
        if shipping_method != 'pickup':
            if request.user.is_authenticated:
                shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
                print(shipping_user.id)
                shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
            else:
                shipping_form = ShippingForm(request.POST or None)

        # Pickup location
        pickup_locations = 'U6/ 51 Dartbrook Road, Auburn'

        context = {
            "cart_products": cart_products,
            "quantities": quantities,
            "new_totals": new_total,
            "discount": discount,
            "totals": total,
            "total_with_shipping": total_with_shipping,
            "shipping_form": shipping_form,
            "variants": variants,
            "express_shipping": express_shipping,
            "standard_shipping": standard_shipping,
            "shipping_method": shipping_method,
            "pickup_locations": pickup_locations,
        }

        return render(request, "payment/checkout.html", context)
    else:
        messages.error(request,'Please add products to your cart before checking out')
        return redirect('cart_summary')