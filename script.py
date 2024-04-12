import os
import sys
import concurrent.futures
import requests
from django.db import models
from django.db.utils import IntegrityError  # Importe a exceção de integridade

# Configurar o ambiente do Django
sys.path.append('script/fipe_project/')  # Ajuste para o caminho do seu projeto
os.environ['DJANGO_SETTINGS_MODULE'] = 'fipe_project.settings'
import django
django.setup()

# Importar modelos do Django
from fipe_app.models import FipeVehicleType, FipeBrand, FipeModel, FipeYear, FipeFuel, FipeCodeFipe, FipePrice  # Substitua 'fipe_app' pelo nome do seu aplicativo Django

# Função para fazer requisições à API Fipe
def make_request(endpoint, params=None):
    base_url = "https://parallelum.com.br/fipe/api/v2"
    url = f"{base_url}{endpoint}"
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Função para obter informações Fipe e adicionar ao banco de dados
def fetch_and_append_data(vehicle_type, reference, brand, model, year):
    vehicle_info = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years/{year["code"]}')
    if vehicle_info:
        try:
            fipe_vehicle_type, _ = FipeVehicleType.objects.get_or_create(vehicle_type=vehicle_type)
            fipe_brand, _ = FipeBrand.objects.get_or_create(brand=vehicle_info["brand"], vehicle_type=fipe_vehicle_type)
            fipe_model, _ = FipeModel.objects.get_or_create(model=vehicle_info["model"], brand=fipe_brand)
            fipe_year, _ = FipeYear.objects.get_or_create(year=int(vehicle_info["modelYear"]), model=fipe_model)
            fipe_fuel, _ = FipeFuel.objects.get_or_create(fuel=vehicle_info["fuel"], year=fipe_year)

            fipe_prices = FipePrice.objects.filter(
                brand=fipe_brand,
                model=fipe_model,
                fuel=fipe_fuel,
                year=fipe_year,
            )

            if fipe_prices.exists():
                for fipe_price in fipe_prices:
                    if fipe_price.price != vehicle_info["price"]:
                        print(f"{vehicle_info['brand']} - {vehicle_info['model']} - Ano: {vehicle_info['modelYear']} Já existe, o preço atual é {fipe_price.price} e vamos atualizar para {vehicle_info['price']}")
                        fipe_price.price = vehicle_info["price"]
                        fipe_price.save()
                    else:
                        print(f"O preço para {vehicle_info['brand']} - {vehicle_info['model']} - Ano: {vehicle_info['modelYear']} já está atualizado.")
            else:
                FipePrice.objects.create(
                    price=vehicle_info["price"],
                    brand=fipe_brand,
                    model=fipe_model,
                    fuel=fipe_fuel,
                    year=fipe_year,
                )
                print(f"Salvo: {vehicle_info['brand']} - {vehicle_info['model']} - Ano: {vehicle_info['modelYear']} - Preço: {vehicle_info['price']}")

        except IntegrityError as e:
            print(f"Erro ao atualizar entrada: {vehicle_info['brand']} - {vehicle_info['model']} - Ano: {vehicle_info['modelYear']} - Preço: {vehicle_info['price']} - {e}")

def populate_database():
    vehicle_type = 'cars'
    reference = {'code': '202404', 'month': 'Abril de 2024'}

    print(f'Processing {vehicle_type} - Reference: {reference["month"]}')
    
    brands = make_request(f'/{vehicle_type}/brands')
    if brands:
        for brand in brands:
            models = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models')
            if models:
                for model in models:
                    years = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years')
                    if years:
                        for year in years:
                            if int(year["code"][:4]) > 2014:
                                fetch_and_append_data(vehicle_type, reference, brand, model, year)

if __name__ == "__main__":
    populate_database()