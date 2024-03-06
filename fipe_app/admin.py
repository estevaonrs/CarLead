from django.contrib import admin
from .models import FipeVehicleType, FipeBrand, FipeModel, FipeYear, FipeFuel, FipeCodeFipe, FipePrice, Lead

class FipeVehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'vehicle_type')

class FipeBrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'vehicle_type')

class FipeModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'model', 'brand')

class FipeYearAdmin(admin.ModelAdmin):
    list_display = ('id', 'year', 'model')

class FipeFuelAdmin(admin.ModelAdmin):
    list_display = ('id', 'fuel', 'year')

class FipeCodeFipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'code_fipe', 'model')

class FipePriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'price', 'model', 'brand',  'fuel')

def formatted_pricing_percentage(obj):
    percentage = obj.pricing_percentage
    if percentage is not None:
        return f"{percentage * 100}%"
    return ""


class LeadAdmin(admin.ModelAdmin):
    list_display = ('mileage', 'name', 'email', 'phone', 'brand', 'model', 'year', 'fuel', 'formatted_price', 'market_category', 'car_category', 'formatted_original_price', 'formatted_pricing_percentage', 'under_warranty', 'revisions_done_in_css', 'created_at')

    def formatted_pricing_percentage(self, obj):
        percentage = obj.pricing_percentage
        if percentage is not None:
            return f"{percentage * 100}%"
        return ""

    formatted_pricing_percentage.short_description = "Pricing Percentage"



admin.site.register(Lead, LeadAdmin)
admin.site.register(FipeVehicleType, FipeVehicleTypeAdmin)
admin.site.register(FipeBrand, FipeBrandAdmin)
admin.site.register(FipeModel, FipeModelAdmin)
admin.site.register(FipeYear, FipeYearAdmin)
admin.site.register(FipeFuel, FipeFuelAdmin)
admin.site.register(FipeCodeFipe, FipeCodeFipeAdmin)
admin.site.register(FipePrice, FipePriceAdmin)
