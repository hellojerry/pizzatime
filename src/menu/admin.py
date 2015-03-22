from django.contrib import admin

from .models import Pizza, PizzaTopping, Product, Entree, Side


class PizzaToppingsInline(admin.TabularInline):
    model = Pizza.toppings.through

class PizzaToppingAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','name','description','active','price')
    inlines = [PizzaToppingsInline]
    
class PizzaAdmin(admin.ModelAdmin):
    inlines = [PizzaToppingsInline]
    
    class Meta:
        model = Pizza

class EntreeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'product','size')
    class Meta:
        model = Entree
        
class SideAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','name','description','active','price')
    class Meta:
        model = Side


class PizzaInline(admin.TabularInline):
    model = Pizza

class ProductAdmin(admin.ModelAdmin):
    inlines = [PizzaInline]
    list_display = (
        '__unicode__', 'product_type',
        'name', 'description',
        'small_price', 'medium_price',
        'large_price', 'xl_price',
        'jumbo_price')
    class Meta:
        model = Product
        
        
admin.site.register(Pizza, PizzaAdmin)
admin.site.register(PizzaTopping, PizzaToppingAdmin)
admin.site.register(Entree, EntreeAdmin)
admin.site.register(Side, SideAdmin)
admin.site.register(Product, ProductAdmin)
