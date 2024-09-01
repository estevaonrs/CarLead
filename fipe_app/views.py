from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from django.db.models import Q
import json
from django.http import JsonResponse
from fipe_app.serializers import LeadSerializer
from .models import Lead
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from rest_framework import viewsets

import re
from .helpers import (req, url_api, url_tabelaref, url_marcas, 
url_modelos, url_ano_modelos, url_todos_parametros, referencias_anos, referencias, tipo_veiculo)


def listar_marcas(request):

    dados_veiculo_marca = {
        'codigoTabelaReferencia': referencias,
        'codigoTipoVeiculo': tipo_veiculo
    }

    marcas = req(url_marcas, dados_veiculo_marca)

    return render(request, 'leads/listar_marcas.html', {'marcas': marcas})


def listar_modelos(request):
    if request.method == 'POST':
        marca_id = request.POST.get('marca_id')
        marca_label = request.POST.get('marca_label')

        dados_veiculo_modelo = {
            'codigoTabelaReferencia': referencias,
            'codigoTipoVeiculo': tipo_veiculo,
            'codigoMarca': marca_id
        }

        modelos = req(url_modelos, dados_veiculo_modelo)

        request.session['marca_id'] = marca_id
        request.session['marca_label'] = marca_label

        return render(request, 'leads/listar_modelos.html', {'modelos': modelos['Modelos'], 'marca_id': marca_id, 'marca_label': marca_label}) 

def listar_ano_modelos(request):
    if request.method == 'POST':
        ano_id = request.POST.get('ano_id')
        modelo_id = request.POST.get('modelo_id')
        marca_id = request.POST.get('marca_id')
        marca_label = request.POST.get('marca_label')
        modelo_label = request.POST.get('modelo_label')

        request.session['marca_id'] = marca_id
        request.session['marca_label'] = marca_label
        request.session['modelo_id'] = modelo_id
        request.session['modelo_label'] = modelo_label
        request.session['ano_id'] = ano_id

        dados_veiculos_ano_modelo = {
            'codigoTabelaReferencia': referencias,
            'codigoTipoVeiculo': tipo_veiculo,
            'codigoMarca': marca_id,
            'codigoModelo': modelo_id 
        }

        anos = req(url_ano_modelos, dados_veiculos_ano_modelo)

        anos_data = [{'label': item['Value'], 'value': item['Label']} for item in anos]

        context = {
            'anos_data': anos_data,
            'modelo_id': modelo_id,
            'marca_id': marca_id,
            'marca_label': marca_label,
            'modelo_label': modelo_label, 
        }

        if ano_id:
            return redirect('fipe_app:step_4') 
        else:
            context['error_message'] = "Ano não selecionado. Por favor, selecione um ano."

        return render(request, 'leads/listar_ano_modelos.html', context)

    return render(request, 'leads/listar_ano_modelos.html')


def step_4(request):
    context = {}

    if request.method == "POST":
        mileage = request.POST.get('mileage')
        revisions_done = request.POST.get('revisions_done') == 'true'
        under_warranty = request.POST.get('under_warranty') == 'true'
        marca_label = request.POST.get('marca_label')
        modelo_label = request.POST.get('modelo_label') 

        if mileage:
            request.session['mileage'] = float(mileage)
            request.session['revisions_done'] = revisions_done
            request.session['under_warranty'] = under_warranty

            marca_id = request.session.get('marca_id')
            modelo_id = request.session.get('modelo_id')
            ano_id = request.session.get('ano_id')

            if marca_id and modelo_id and ano_id:
                return redirect('fipe_app:step_6')

    return render(request, 'leads/step-four-form.html', context)

def step_6(request):
    if request.method == "POST":
        marca_id = request.session.get('marca_id')
        modelo_id = request.session.get('modelo_id')
        ano_id = request.session.get('ano_id')
        marca_label = request.session.get('marca_label')
        modelo_label = request.session.get('modelo_label')

        if not ano_id:
            return redirect('fipe_app:step_4')

        mileage = Decimal(request.session.get('mileage', '0'))
        revisions_done = request.session.get('revisions_done', False)
        under_warranty = request.session.get('under_warranty', False)

        print_session_data(marca_id, marca_label, modelo_id, modelo_label, ano_id, mileage, revisions_done, under_warranty)

        try:
            ano_modelo, fuel_id = ano_id.split(' ', 1)
        except ValueError:
            print("Formato de ano inválido.")
            return redirect('fipe_app:step_4') 

        valor_fipe, fuel_id = get_fipe_value(ano_modelo, marca_id, modelo_id)

        final_price, percentage, market_category = calculate_final_price(valor_fipe, mileage, revisions_done, under_warranty, modelo_id, fuel_id)

        lead = create_lead(request, marca_label, modelo_label, ano_id, fuel_id, final_price, valor_fipe, percentage, revisions_done, under_warranty)

        request.session.flush()

        return redirect('fipe_app:show_price', lead_id=lead.id)

    return render(request, 'leads/step-six-form.html')

def print_session_data(marca_id, marca_label, modelo_id, modelo_label, ano_id, mileage, revisions_done, under_warranty):
    print("Dados da sessão:")
    print("Marca ID:", marca_id)
    print("Marca LABEL:", marca_label)
    print("Modelo ID:", modelo_id)
    print("Modelo LABEL:", modelo_label)
    print("Ano ID:", ano_id)
    print("Quilometragem:", mileage)
    print("Revisões feitas:", revisions_done)
    print("Na garantia:", under_warranty)

def get_fipe_value(ano_id, marca_id, modelo_id):
    ano_id = ano_id.strip()
    
    if ' ' in ano_id:
        ano_modelo, fuel_id = ano_id.split(' ', 1) 
    else:
        ano_modelo = ano_id
        fuel_id = '1' 

    dados_veiculos_ano_modelo = {
            'codigoTabelaReferencia': referencias,
            'codigoTipoVeiculo': 1,
            'codigoMarca': marca_id,
            'codigoModelo': modelo_id,
            'ano': ano_id,
            'anoModelo': ano_modelo,
            'codigoTipoCombustivel': fuel_id,
            'tipoConsulta': 'tradicional'
    }

    response = req(url_todos_parametros, dados_veiculos_ano_modelo)

    valor_fipe = Decimal(response.get('Valor', '0.00').replace('R$', '').replace('.', '').replace(',', '.'))
    return valor_fipe, fuel_id


def calculate_final_price(valor_fipe, mileage, revisions_done, under_warranty, modelo_id, fuel_id):
    km_brackets = [
        (0, 9999, Decimal('0.82')),
        (10000, 19999, Decimal('0.80')),
        (20000, 29999, Decimal('0.79')),
        (30000, 49999, Decimal('0.78')),
        (50000, 59999, Decimal('0.77')),
        (60000, 74999, Decimal('0.72')),
        (75000, 99999, Decimal('0.62')),
        (100000, 130000, Decimal('0.60')),
    ]
    
    percentage = next((perc for min_km, max_km, perc in km_brackets if min_km <= mileage <= max_km), Decimal('0.60'))

    if revisions_done:
        percentage += Decimal('0.01')
    if under_warranty:
        percentage += Decimal('0.02')

    market_category = adjust_percentage_by_model(modelo_id, fuel_id, percentage)

    final_price = valor_fipe * percentage
    print("\nPreço final calculado:", final_price)
    return final_price, percentage, market_category

def adjust_percentage_by_model(modelo_id, fuel_id, percentage):
    ruim_mercado = ['NSX 3.0']
    queimados = ['Integra GS 1.8']
    valorizar_modelos = ['MARRUÁ AM 100 2.8 CD TDI Diesel']

    market_category = "Comum"
    if modelo_id in ruim_mercado:
        percentage -= Decimal('0.10')
        market_category = 'Ruim de mercado'
    elif modelo_id in queimados:
        percentage -= Decimal('0.30')
        market_category = 'Mercado Queimado'
    elif modelo_id in valorizar_modelos:
        percentage += Decimal('0.02')
        market_category = 'Modelo valorizado'

    if fuel_id.lower() == 'diesel':
        percentage -= Decimal('0.10')
        market_category = 'Diesel'

    return market_category

def create_lead(request, marca_label, modelo_label, ano_id, fuel_id, final_price, valor_fipe, percentage, revisions_done, under_warranty):
    name = request.POST.get('name')
    email = request.POST.get('email')
    phone = request.POST.get('phone')

    lead = Lead.objects.create(
        name=name,
        email=email,
        phone=phone,
        mileage=request.session.get('mileage', '0'),
        brand=marca_label,
        model=modelo_label,
        year=ano_id,
        fuel=fuel_id,
        price=final_price,
        market_category='Comum',
        car_category='Salão',
        original_price=valor_fipe,
        pricing_percentage=percentage,
        revisions_done_in_css=revisions_done,
        under_warranty=under_warranty
    )
    return lead
    
def format_currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
    return locale.currency(value, grouping=True)

def show_price(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    
    lead.original_price = format_currency(lead.original_price)
    lead.price = format_currency(lead.price)
    
    return render(request, 'leads/show_price.html', {'lead': lead})


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def get_queryset(self):
        return self.queryset


def index_view(request):
    return render(request, 'leads/index.html')





