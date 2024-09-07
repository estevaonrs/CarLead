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
    "Citroën": "images/brands_images/citroen.webp",
    "Fiat": "images/brands_images/fiat.png",
    "Ford": "images/brands_images/ford.png",
    "GM - Chevrolet": "images/brands_images/chevrolet.png",
    "Honda": "images/brands_images/honda.png",
    "Hyundai": "images/brands_images/hyundai.png",
    "Jeep": "images/brands_images/jeep.png",
    "Mitsubishi": "images/brands_images/mitsubishi.webp",
    "Nissan": "images/brands_images/nissan.png",
    "Peugeot": "images/brands_images/peugeot.png",
    "Suzuki": "images/brands_images/suzuki.png",
    "Toyota": "images/brands_images/toyota.png",
    "Troller": "images/brands_images/troller.png",
    "VW - VolksWagen": "images/brands_images/volks.png",
    "Renault": "images/brands_images/renault.png",
}

marcas_desejadas = imagens_marcas.keys()

