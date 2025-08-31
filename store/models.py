from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class About_us(models.Model):
    about_us = models.CharField(max_length=3000, blank=True)
    
    def __str__(self):
        return self.about_us
    


#Create customer profile
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User,auto_now=True)
    phone = models.CharField(max_length=30,blank=True) 
    address1 = models.CharField(max_length=200,blank=True) 
    address2 = models.CharField(max_length=200,blank=True) 
    city = models.CharField(max_length=200,blank=True)
    state = models.CharField(max_length=200,blank=True)
    zipcode = models.CharField(max_length=200,blank=True)
    country = models.CharField(max_length=200,blank=True)
    old_cart = models.CharField(max_length=200,blank=True,null=True)
    
    def __str__(self):
        return self.user.username

#Create a user Profile by default when user signs up

def create_profile(sender,instance,created,**kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()
        
#Automate the profile thing
post_save.connect(create_profile,sender=User)


class Category(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Add this line for image input

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'

class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1,related_name='category')
    short_description = models.CharField(max_length=250, default='', blank=True, null=True)
    long_description = models.CharField(max_length=1000, default='', blank=True, null=True)
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6, blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/', default='default.jpg')
    
    def __str__(self):
        return self.name

    def get_variants(self):
        return self.variants.all()  # returns all variants related to this product
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    size = models.CharField(max_length=100,blank=True, null=True)  # Adjust max_digits and decimal_places as needed
    stock_qty = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.product} - {self.size}"

    def is_in_stock(self):
        return self.stock_qty > 0
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/product/')

    def __str__(self):
        return f"Image for {self.product.name}"
    
#Customers Orders

class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=100, default='')
    phone = models.CharField(max_length=20, default='', blank=True)
    date = models.DateField(default=datetime.date.today)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} for {self.customer}"
    
class Contact(models.Model):
    name = models.CharField(max_length=50, default='')
    email = models.EmailField(max_length=100, default='')
    subject = models.CharField(max_length=100, default='')
    enquiry = models.CharField(max_length=2000, default='')
    product = models.CharField(max_length=100, default='')  # Add product field
    image = models.ImageField(upload_to='contact_images/', blank=True, null=True)

    def __str__(self):
        return f"Enquiry from {self.name} about {self.product}"