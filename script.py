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
    # Obtendo informações Fipe específicas para o veículo
    vehicle_info = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years/{year["code"]}')
    
    if vehicle_info:
        try:
            # Obtendo ou criando os objetos relacionados
            fipe_vehicle_type, created = FipeVehicleType.objects.get_or_create(vehicle_type=vehicle_type)
            fipe_brand, created = FipeBrand.objects.get_or_create(brand=vehicle_info["brand"], vehicle_type=fipe_vehicle_type)
            fipe_model, created = FipeModel.objects.get_or_create(model=vehicle_info["model"], brand=fipe_brand)
            fipe_year, created = FipeYear.objects.get_or_create(year=int(vehicle_info["modelYear"]), model=fipe_model)
            fipe_fuel, created = FipeFuel.objects.get_or_create(fuel=vehicle_info["fuel"], year=fipe_year)

            # Adicionando dados ao banco de dados
            FipePrice.objects.create(
                price=vehicle_info["price"],
                brand=fipe_brand,
                model=fipe_model,
                fuel=fipe_fuel,
                year=fipe_year,
            )
            print(f"Saved: {vehicle_info['brand']} - {vehicle_info['model']} - Year: {vehicle_info['modelYear']} - Price: {vehicle_info['price']}")
        except IntegrityError as e:
            # Se houver uma violação de integridade (possível duplicata), imprima uma mensagem e ignore
            print(f"Ignored duplicate entry: {vehicle_info['brand']} - {vehicle_info['model']} - Year: {vehicle_info['modelYear']} - Price: {vehicle_info['price']}")


# Função para popular o banco de dados com informações da API Fipe
def populate_database():
    # Populando o banco de dados com dados da API Fipe
    vehicle_type = 'cars'  # Pegando apenas carros
    reference = {'code': '202403', 'month': 'Março de 2024'}  # Especificando a referência do mês desejado (março de 2024)

    print(f'Processing {vehicle_type} - Reference: {reference["month"]}')
    
    # Obtendo marcas para o tipo de veículo
    brands = make_request(f'/{vehicle_type}/brands')
    if brands:
        for brand in brands:
            # Obtendo modelos para a marca
            models = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models')
            if models:
                for model in models:
                    # Obtendo anos para o modelo
                    years = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years')
                    if years:
                        for year in years:
                            # Verificando se o ano é maior que 2014
                            if int(year["code"][:4]) > 2014:
                                # Adicionando tarefa de busca e inserção
                                fetch_and_append_data(vehicle_type, reference, brand, model, year)

if __name__ == "__main__":
    populate_database()
