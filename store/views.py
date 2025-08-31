from django.shortcuts import render,redirect,get_object_or_404
from .models import Product,Category,Profile,ProductVariant,ProductImage
from django.contrib.auth import authenticate,login,logout
from django.contrib import  messages
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm,UpdateUserForm,ChangePasswordForm,UserInfoForm,ContactForm
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django import forms
from django.db.models import Q
from django.db.models import Min, Max
from django.shortcuts import render
import json
from cart.cart import Cart





def all_product(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Get min and max prices for the price slider
    price_range = Product.objects.aggregate(Min('price'), Max('price'))
    min_price = int(price_range['price__min'])
    max_price = int(price_range['price__max'])

    context = {
        'products': products,
        'categories': categories,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'all_products.html', context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()  # Save the form data to the database
            messages.success(request,'Enquiry Submitted Successfully')
            return redirect('home')  # Redirect to the home page after submission
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})
def search(request):
    #Determine if they filled out the form
    
    if request.method == "POST":
        
        searched = request.POST['searched']
        #Query the products DB model
        searched = Product.objects.filter(Q(name__icontains = searched)| Q(short_description__icontains = searched) |Q(long_description__icontains = searched))
        if not searched:
            messages.success(request, "That product does not exist....... please try again later")
        return render(request,"search.html",{'searched':searched})
    else:
        return render(request,"search.html",{})

def update_info(request):
    if request.user.is_authenticated:
        current_user = Profile.objects.get(user__id = request.user.id)
        #Get the shipping user
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
        #get original user form
        form = UserInfoForm(request.POST or None,instance=current_user)
        #get user's shipping form
        shipping_form = ShippingForm(request.POST or None,instance=shipping_user)
        if form.is_valid() or shipping_form.is_valid():
            #Save original Form
            form.save()
            #Save shipping form
            shipping_form.save()
            messages.success(request,"Your info has been updated")
            return redirect('home')
        return render(request,"update_info.html",{"form":form,"shipping_form":shipping_form})
    else:
        messages.success(request, "You must be logged in",)
        return redirect('home.html',{})

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # Did they fill out the form?
        if request.method == "POST":
            form = ChangePasswordForm(current_user,request.POST)
            #IS the form valid
            if form.is_valid():
                form.save()
                messages.success(request,"Your Password has been Updated....... ")
                login(request,current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request,error)
                    return redirect('update_password.html')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form': form})
    else:
        messages.success(request, "You must be logged in")
        return redirect('login')

    return render(request, "update_password.html", {})
def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id = request.user.id)
        user_form = UpdateUserForm(request.POST or None,instance=current_user)
        if user_form.is_valid():
            user_form.save()
            
            login(request,current_user)
            messages.success(request,"User has been updated")
            return redirect('home')
        return render(request,"update_user.html",{"user_form":user_form})
    else:
        messages.success(request, "You myust be logged in",)
        return redirect('home.html',{})
    
def category_summary(request):
    categories = Category.objects.all()
    
    return render(request,'category_summary.html',{'categories': categories})
def category(request, foo):
    categories = Category.objects.all()
    print(categories)
    # Check if a hyphen exists in the original string
    if '-' in foo:
        # Replacing hyphens with spaces if a hyphen is found
        foo_original = foo
        foo = foo.replace('-', ' ')
    else:
        foo_original = foo

    # Debugging: print the category name being searched for
    print(f"Original category string: {foo_original}")
    print(f"Processed category string: {foo}")
    
    try:
        # Look up the category
        category = Category.objects.get(name__iexact=foo)
        print(f"Category found: {category.name}")  # Debugging: print the category found
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category, 'categories': categories})
    except Category.DoesNotExist:
        print(f"Category '{foo}' does not exist")  # Debugging: print the error message
        messages.error(request, f"The category '{foo_original}' does not exist")
        return redirect('home')
    
    
def product(request, pk):
    product = get_object_or_404(Product, id=pk)
    variants = ProductVariant.objects.filter(product=product)  # Fetch ProductVariant instances related to the product
    images = product.images.all()  # Fetch all related ProductImage instances
    quantity_ranges = {variant.size: range(1, variant.stock_qty + 1) for variant in variants}  # Create a dictionary of quantity ranges by size
    similar_products = Product.objects.exclude(id=product.id).order_by('?')[:4]
    category_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    return render(request, 'product.html', {
        'product': product,
        'variants': variants,  # Pass ProductVariant instances to the template
        'images': images,
        'quantity_ranges': quantity_ranges,  # Pass the quantity ranges to the template
        'similar_products':similar_products,
        'category_products':category_products,
        
    })

def home(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    sale_products = Product.objects.filter(is_sale=True)  # Get only products that are on sale

    # Check if the welcome modal has been shown
    if 'seen_welcome' not in request.session:
        request.session['seen_welcome'] = True
        show_welcome = True
    else:
        show_welcome = False

    return render(request, 'home.html', {
        'sale_products': sale_products,  # Pass sale products to the template
        'categories': categories,
        'show_welcome': show_welcome,  # Pass to template
        'products':products
    })




def about(request):
    return render(request,'about.html',{})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            
            #Do some shoopping cart stuff
            
            current_user = Profile.objects.get(user__id = request.user.id)
            #get there saved cart
            saved_cart = current_user.old_cart
            #Convert database string to python dict
            
            if saved_cart:
                #Convert the dict using JSON
                converted_cart = json.loads(saved_cart)
                
                #Add the loaded cart dict to our session
                cart= Cart(request)
                #loop throgh the cart and add the items from the database
                
                for key,value in converted_cart.items():
                    print(key)
                    product = key
                    for key,value in value.items():
                        quantity = key
                        size = value
                        cart.db_add(product=product,quantity=quantity,size=size)
            messages.success(request,("You have been logged in "))
            return redirect('home')
        else:
            messages.success(request, ("There was an error logging in"))
            return redirect('login')
    else:
        return render(request,'login.html',{})

def logout_user(request):
    logout(request)
    messages.success(request,("You have been logged out"))
    return redirect('home')


def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                username = form.cleaned_data['username']
                password = form.cleaned_data['password1']

                # Log in user
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.success(request, "User account created successfully. Please fill up your information.")
                    return redirect('update_info')
                else:
                    messages.error(request, "Authentication failed. Please try again.")
                    return redirect('register')
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")
        else:
            error_messages = form.errors.as_data()
            for field, errors in error_messages.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            messages.error(request, "Registration failed. Please check the form and try again.")
    return render(request, 'register.html', {'form': form})


def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def refund_policy(request):
    return render(request, 'refund_policy.html')