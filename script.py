import os
import sys
import concurrent.futures
import requests
from datetime import datetime

# Configurar o ambiente do Django
sys.path.append('C:\\Users\\iTrevo\\Desktop\\teste\\fipe_project')  # Ajuste para o caminho do seu projeto
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fipe_project.settings')
import django
django.setup()

# Importar modelos do Django
from fipe_app.models import FipeVehicleType, FipeBrand, FipeModel, FipeYear, FipeFuel, FipeCodeFipe, FipePrice

# Função para fazer requisições à API Fipe
def make_request(endpoint, params=None):
    base_url = "https://parallelum.com.br/fipe/api/v2"
    url = f"{base_url}{endpoint}"
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Função para obter informações Fipe e adicionar ao banco de dados
def fetch_and_append_data(vehicle_type, brand, model, year):
    # Adicionando filtragem para anos de modelo acima de 2009
    if int(year["code"][:4]) > 2014:  # Ajuste aqui para incluir anos acima de 2009
        vehicle_info = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years/{year["code"]}')
        
        if vehicle_info:
            print(f"Processando: {vehicle_info['brand']} - {vehicle_info['model']} - Ano: {vehicle_info['modelYear']}")  # Adicionado print para monitoramento
            vehicle_type_instance, _ = FipeVehicleType.objects.get_or_create(vehicle_type="Carro")
            brand_instance, _ = FipeBrand.objects.get_or_create(brand=vehicle_info["brand"], vehicle_type=vehicle_type_instance)
            model_instance, _ = FipeModel.objects.get_or_create(model=vehicle_info["model"], brand=brand_instance)
            year_instance, _ = FipeYear.objects.get_or_create(year=int(vehicle_info["modelYear"]), model=model_instance)
            fuel_instance, _ = FipeFuel.objects.get_or_create(fuel=vehicle_info["fuel"], year=year_instance)
            code_fipe_instance, _ = FipeCodeFipe.objects.get_or_create(code_fipe=vehicle_info["codeFipe"], model=model_instance)
            FipePrice.objects.get_or_create(price=vehicle_info["price"], brand=brand_instance, model=model_instance, fuel=fuel_instance, year=year_instance)

# Função para popular o banco de dados com informações da API Fipe
def populate_database():
    vehicle_types = ['cars']  # Continua limitado apenas a carros

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for vehicle_type in vehicle_types:
            brands = make_request(f'/{vehicle_type}/brands')
            if brands:
                for brand in brands:
                    models = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models')
                    if models:
                        for model in models:
                            years = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years')
                            if years:
                                for year in years:
                                    futures.append(
                                        executor.submit(fetch_and_append_data, vehicle_type, brand, model, year)
                                    )

    # Aguardar a conclusão de todas as tarefas
    concurrent.futures.wait(futures)

if __name__ == "__main__":
    populate_database()
