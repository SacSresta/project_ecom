from django.contrib import admin
from .models import ShippingAddress,Order,OrderItems,PAIDORDER
from django.contrib.auth.models import User


# Register your models here.

admin.site.register(ShippingAddress)
admin.site.register(OrderItems)
admin.site.register(Order)
admin.site.register(PAIDORDER)

#Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItems
    extra = 0
    
    
#Extend our order model

class OrderAdmin(admin.ModelAdmin):
    model = Order
    readonly_fields = ["date_ordered"]
    fields = ["user","full_name","email","shipping_address","date_ordered","amount_paid","shipped","date_shipped","invoice","paid","phone_number"]
    inlines = [OrderItemInline]
    
#UnregisterOrderModel
admin.site.unregister(Order)
#Reregister our order and orderitem
admin.site.register(Order,OrderAdmin)

