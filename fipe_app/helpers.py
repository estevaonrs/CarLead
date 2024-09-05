import requests

def req(url, data):
    return requests.post(url, data=data).json()

url_api = 'https://veiculos.fipe.org.br/api/veiculos'
url_tabelaref = f'{url_api}/ConsultarTabelaDeReferencia'
url_marcas = f'{url_api}/ConsultarMarcas'
url_modelos = f'{url_api}/ConsultarModelos'
url_ano_modelos = f'{url_api}/ConsultarAnoModelo'
url_todos_parametros = f'{url_api}/ConsultarValorComTodosParametros'
referencias_anos = req(url_tabelaref, '')
referencias = referencias_anos[0]['Codigo']
tipo_veiculo = 1

marcas_desejadas = [
    "Audi","" ,"Citroën", "Fiat", "Ford", "GM - Chevrolet", "Honda", 
    "Hyundai", "Jeep", "Mitsubishi", "Nissan", "Peugeot", 
    "Suzuki", "Toyota", "Troller", "VW - VolksWagen", "Renault"
]

imagens_marcas = {
    "Citroën": "images/brands_images/ford.webp",
    "Fiat": "images/brands_images/ford.webp",
    "Ford": "images/brands_images/ford.webp",
    "GM - Chevrolet": "images/brands_images/chevrolet.webp",
    "Honda": "images/brands_images/ford.webp",
    "Hyundai": "images/brands_images/hyundai.webp",
    "Jeep": "images/brands_images/ford.webp",
    "Mitsubishi": "images/brands_images/ford.webp",
    "Nissan": "images/brands_images/ford.webp",
    "Peugeot": "images/brands_images/ford.webp",
    "Suzuki": "images/brands_images/ford.webp",
    "Toyota": "images/brands_images/ford.webp",
    "Troller": "images/brands_images/ford.webp",
    "VW - VolksWagen": "images/brands_images/ford.webp",
    "Renault": "images/brands_images/renault.webp",
}

marcas_desejadas = imagens_marcas.keys()

