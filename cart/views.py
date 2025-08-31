from django.shortcuts import render,redirect,get_object_or_404
from django.urls import reverse
from .cart import Cart
from store.models import Product,ProductVariant
from django.utils import timezone
from .models import PromoCode
from .forms import PromoCodeForm  # We'll create this form shortly
from .cart import Cart  # Assuming you have a Cart utility
from django.http import JsonResponse
from django.contrib import  messages
import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY


def cart_summary(request):
    cart = Cart(request)
    variants = cart.get_prods()
    cart_products = [v.product for v in variants]
    quantities = cart.get_quants()
    total = cart.cart_total()
    stock_qty_ranges = [range(1, variant.stock_qty + 1) for variant in variants]

    # Ensure total is a Decimal for consistent calculations
    total = Decimal(total)

    discount = Decimal('0')  # Initialize discount as a Decimal
    promo_code = None
    promo_message = ''
    final_total = total  # Initialize final_total to total by default

    # Handle Promo Code Form Submission
    if request.method == 'POST':
        promo_code_form = PromoCodeForm(request.POST)
        if promo_code_form.is_valid():
            code = promo_code_form.cleaned_data['code']
            try:
                promo_code = PromoCode.objects.get(code__iexact=code, active=True)
                if promo_code.is_valid():
                    # Calculate Discount
                    if promo_code.discount_percent:
                        discount = total * (promo_code.discount_percent / 100)
                    elif promo_code.discount_amount:
                        discount = promo_code.discount_amount

                    # Ensure discount does not exceed total
                    discount = min(discount, total)

                    # Store promo code and discount in session
                    request.session['promo_code'] = promo_code.code
                    request.session['discount'] = str(discount)  # Store as string to prevent serialization issues

                    promo_message = f'Promo code "{promo_code.code}" applied successfully!'
                else:
                    promo_message = 'Promo code is invalid or expired.'
            except PromoCode.DoesNotExist:
                promo_message = 'Promo code does not exist.'
    else:
        # Check if a promo code is already applied in the session
        applied_code = request.session.get('promo_code')
        if applied_code:
            try:
                promo_code = PromoCode.objects.get(code__iexact=applied_code, active=True)
                if promo_code.is_valid():
                    if promo_code.discount_percent:
                        discount = total * (promo_code.discount_percent / 100)
                    elif promo_code.discount_amount:
                        discount = promo_code.discount_amount

                    # Ensure discount does not exceed total
                    discount = min(discount, total)
                else:
                    # Remove invalid promo code from session
                    del request.session['promo_code']
                    del request.session['discount']
            except PromoCode.DoesNotExist:
                # Remove non-existent promo code from session
                del request.session['promo_code']
                del request.session['discount']

        # Retrieve discount from session if available
        discount = Decimal(request.session.get('discount', '0'))

    # Calculate final total after discount
    final_total = total - discount
    request.session['total'] = str(final_total)  # Store as string for serialization

    # Initialize the promo code form
    promo_code_form = PromoCodeForm()

    return render(request, "cart_summary.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": total,
        "discount": discount,
        "final_total": final_total,
        "stock_qty_ranges": stock_qty_ranges,
        "variants": variants,
        "promo_code_form": promo_code_form,
        "promo_message": promo_message,
        "applied_promo_code": promo_code.code if promo_code else None
    })
    
def remove_promo_code(request):
    if request.method == 'POST':
        request.session.pop('promo_code', None)
        request.session.pop('discount', None)
    return redirect(reverse('cart_summary'))
def cart_add(request):
    # Get the cart
    cart = Cart(request)
    
    if request.POST.get('action') == 'post':
        # Get product details from the request
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product_size = request.POST.get('product_size')
        product_variant = int(request.POST.get('product_variant_Id'))
        
        # Fetch the product
        product = get_object_or_404(Product, id=product_id)
        product_variant = ProductVariant.objects.get(id=product_variant)
        # Add to cart with size
        cart.add(product=product_variant, quantity=product_qty, size=product_size)
        
        # Return JSON response with the cart quantity
        cart_quantity = cart.__len__()
        response = JsonResponse({'qty': cart_quantity})
        
        messages.success(request, "Product added to cart.")
        return response
def cart_delete(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        cart.delete(product=product_id)
        
        response = JsonResponse({'product': product_id})
        messages.success(request, "Product deleted")
        return response
def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_qty = int(request.POST.get('product_qty'))
        product_size = int(request.POST.get('size'))
        
        print(f"Updating product {product_id} with quantity {product_qty}")
        cart.update(product=product_id, quantity=product_qty, size = product_size)
        
        response = JsonResponse({'qty': product_qty})
        messages.success(request, "Cart Updated")
        return response