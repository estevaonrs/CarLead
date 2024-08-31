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
