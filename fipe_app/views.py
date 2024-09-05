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
url_modelos, url_ano_modelos, url_todos_parametros, referencias_anos, referencias, tipo_veiculo, marcas_desejadas, imagens_marcas)

from .business import print_session_data, adjust_percentage_by_model, get_fipe_value, calculate_final_price, create_lead, format_currency


def listar_marcas(request):
    termo_pesquisa = request.GET.get('search', '')

    dados_veiculo_marca = {
        'codigoTabelaReferencia': referencias,
        'codigoTipoVeiculo': tipo_veiculo
    }

    todas_marcas = req(url_marcas, dados_veiculo_marca)

    marcas_filtradas = [
        {
            'Label': marca['Label'],
            'Value': marca['Value'],
            'Image': imagens_marcas.get(marca['Label'], 'media/brands_images/default.png')
        }
        for marca in todas_marcas if marca['Label'] in marcas_desejadas and (termo_pesquisa.lower() in marca['Label'].lower())
    ]

    return render(request, 'leads/listar_marcas.html', {'marcas': marcas_filtradas})


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

