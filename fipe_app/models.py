from django.db import models
from django.utils import timezone
from django.utils.formats import number_format

class FipeVehicleType(models.Model):
    vehicle_type = models.CharField(max_length=100)

    def get_vehicle_type_display(self):
        translations = {
            "cars": "Carro",
            "motorcycles": "Moto",
            "trucks": "Caminhão",

            # Adicione mais traduções conforme necessário
        }
        return translations.get(self.vehicle_type, self.vehicle_type)

    def __str__(self):
        return self.vehicle_type

class FipeBrand(models.Model):
    brand = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(FipeVehicleType, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='brands_images/', null=True, blank=True)  # Caminho onde as imagens serão armazenadas

    def __str__(self):
        return f"{self.brand} ({self.vehicle_type})"

class FipeModel(models.Model):
    model = models.CharField(max_length=100)
    brand = models.ForeignKey(FipeBrand, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.model} ({self.brand.brand})"

class FipeYear(models.Model):
    year = models.IntegerField()
    model = models.ForeignKey(FipeModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.year} ({self.model.model})"

class FipeFuel(models.Model):
    fuel = models.CharField(max_length=50)
    year = models.ForeignKey(FipeYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.fuel} ({self.year.year})"

class FipeCodeFipe(models.Model):
    code_fipe = models.CharField(max_length=50)
    model = models.ForeignKey(FipeModel, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code_fipe} ({self.model.model})"

class FipePrice(models.Model):
    price = models.CharField(max_length=50)
    brand = models.ForeignKey(FipeBrand, on_delete=models.CASCADE)
    model = models.ForeignKey(FipeModel, on_delete=models.CASCADE)
    fuel = models.ForeignKey(FipeFuel, on_delete=models.CASCADE)
    year = models.ForeignKey(FipeYear, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.price} ({self.model.model})"


class Lead(models.Model):
    mileage = models.IntegerField()
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    brand = models.ForeignKey('FipeBrand', on_delete=models.CASCADE)
    model = models.ForeignKey('FipeModel', on_delete=models.CASCADE)
    year = models.ForeignKey('FipeYear', on_delete=models.CASCADE) 
    fuel = models.ForeignKey('FipeFuel', on_delete=models.CASCADE) 
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    market_category = models.CharField(max_length=50, null=True, blank=True)
    car_category = models.CharField(max_length=50, null=True, blank=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    pricing_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    revisions_done_in_css = models.BooleanField(default=False)  # Novo campo para revisões feitas
    under_warranty = models.BooleanField(default=False)  # Novo campo para garantia
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"{self.name} - {self.email} - {self.phone}"

    def formatted_price(self):
        return "R$ " + number_format(self.price, 2, force_grouping=True, use_l10n=True)

    def formatted_original_price(self):
        return "R$ " + number_format(self.original_price, 2, force_grouping=True, use_l10n=True)

    def pricing_percentage_display(self):
        return f"{self.pricing_percentage * 100}%"
