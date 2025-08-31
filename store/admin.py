from django.contrib import admin
from .models import Category, Customer, Product, Order, Profile, About_us, ProductImage,ProductVariant,Contact
from django.contrib.auth.models import User

# Register your models here.
admin.site.register(Category)
admin.site.register(Profile)

# Define ProductImageInline
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of empty forms to display by default

# Define ProductVariantInline
class ProductVariantInline(admin.TabularInline):
    # Define model for inline admin interface
    model = ProductVariant
    # Set number of extra empty forms
    extra = 1
class ProductAdmin(admin.ModelAdmin):
    model = Product
    list_display = ('name', 'price', 'category', 'is_sale')  # Customize fields as needed
    inlines = [ProductImageInline,ProductVariantInline]

# Extend the user model with Profile
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ['username', 'first_name', 'last_name', 'email']
    inlines = [ProfileInline]
    list_display = ('username', 'first_name', 'last_name', 'email')

# Unregister the old User admin and re-register the new User admin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Register the Product and ProductImage models with the admin
admin.site.register(Product, ProductAdmin)
admin.site.register(Contact)
admin.site.register(ProductVariant)

