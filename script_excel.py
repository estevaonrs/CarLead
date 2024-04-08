import os
import sys
import concurrent.futures
import requests
import pandas as pd
from datetime import datetime

# Configurar o ambiente do Django (Removido, pois não interagiremos com os modelos do Django)

# Função para fazer requisições à API Fipe
def make_request(endpoint, params=None):
    base_url = "https://parallelum.com.br/fipe/api/v2"
    url = f"{base_url}{endpoint}"
    response = requests.get(url, params=params)
    return response.json() if response.status_code == 200 else None

# Função para acumular dados em um DataFrame
def fetch_and_accumulate_data(vehicle_type, brand, model, year, data_accumulator):
    current_year = datetime.now().year
    if int(year["code"][:4]) >= 2010 and int(year["code"][:4]) <= current_year:
        vehicle_info = make_request(f'/{vehicle_type}/brands/{brand["code"]}/models/{model["code"]}/years/{year["code"]}')
        if vehicle_info:
            data_accumulator.append({
                "Vehicle Type": vehicle_type.capitalize(),
                "Brand": vehicle_info["brand"],
                "Model": vehicle_info["model"],
                "Year": vehicle_info["modelYear"],
                "Fuel": vehicle_info["fuel"],
                "Price": vehicle_info["price"],
                "Fipe Code": vehicle_info["codeFipe"]
            })

# Função para popular o DataFrame e salvar em um arquivo Excel
def populate_and_save_to_excel():
    vehicle_types = ['cars']  # Limitar apenas a carros
    data_accumulator = []
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
                                        executor.submit(fetch_and_accumulate_data, vehicle_type, brand, model, year, data_accumulator)
                                    )
        concurrent.futures.wait(futures)
    
    # Converter acumulador de dados em DataFrame e salvar em Excel
    df = pd.DataFrame(data_accumulator)
    df.to_excel('fipe_data.xlsx', index=False)

if __name__ == "__main__":
    populate_and_save_to_excel()
