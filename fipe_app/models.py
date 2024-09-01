from django.db import models
from django.utils import timezone
from django.utils.formats import number_format

class Lead(models.Model):
    mileage = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    brand = models.CharField(max_length=255)  # ou outro tipo conforme necessário
    model = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    fuel = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_category = models.CharField(max_length=50, null=True, blank=True)
    car_category = models.CharField(max_length=50, null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    revisions_done_in_css = models.BooleanField(default=False)
    under_warranty = models.BooleanField(default=False) 
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.phone}"

    def formatted_price(self):
        return "R$ " + number_format(self.price, 2, force_grouping=True, use_l10n=True)

    def formatted_original_price(self):
        return "R$ " + number_format(self.original_price, 2, force_grouping=True, use_l10n=True)

    def pricing_percentage_display(self):
        return f"{self.pricing_percentage * 100}%"
