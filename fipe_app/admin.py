from django.contrib import admin
from .models import Lead

class LeadAdmin(admin.ModelAdmin):
    list_display = ('mileage', 'name', 'email', 'phone', 'brand', 'model', 'year', 'fuel', 'formatted_price', 'market_category', 'car_category', 'formatted_original_price', 'formatted_pricing_percentage', 'under_warranty', 'revisions_done_in_css', 'created_at')

    def formatted_pricing_percentage(self, obj):
        percentage = obj.pricing_percentage
        if percentage is not None:
            return f"{percentage * 100}%"
        return ""

    formatted_pricing_percentage.short_description = "Pricing Percentage"


class FipeVersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand')

admin.site.register(Lead, LeadAdmin)

