from django.contrib import admin
from .models import Order, OrderLineItem
# Register your models here.


class OrderLineItemAdmin(admin.ModelAdmin):
    class Meta:
        model = OrderLineItem

class OrderLineItemInline(admin.TabularInline):
    model = OrderLineItem

class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderLineItemInline]
    class Meta:
        model = Order
        
        
admin.site.register(OrderLineItem, OrderLineItemAdmin)        
admin.site.register(Order, OrderAdmin)
