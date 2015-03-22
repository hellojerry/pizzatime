from django.contrib import admin
from .models import UserProfile, Location, ZipData, Surcharges


class SurchargeAdmin(admin.ModelAdmin):
    class Meta:
        model = Surcharges

class SurchargeInline(admin.TabularInline):
    model = Surcharges


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('role', 'first_name', 'last_name', 'street_address', 'city', 'state', 'zipcode', 'phone')
    search_fields = ['role', 'first_name', 'last_name', 'street_address', 'city', 'state', 'zipcode', 'phone']
    list_filter = ['role', 'last_name', 'city']
    
    class Meta:
        model = UserProfile

        
class LocationAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'street_address', 'city', 'state', 'zipcode', 'phone', 'name')
    inlines = [SurchargeInline]
    class Meta:
        model = Location
        
class ZipDataAdmin(admin.ModelAdmin):
    list_display =  ('zipcode','statecode','lat','long','city','state')
    search_fields = ['zipcode','statecode','lat','long','city','state']
    class Meta:
        model = ZipData
    
        
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Location, LocationAdmin)
admin.site.register(ZipData, ZipDataAdmin)
admin.site.register(Surcharges, SurchargeAdmin)




