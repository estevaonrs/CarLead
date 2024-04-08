from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
from django.db.models import Q
import json
from django.http import JsonResponse
from fipe_app.serializers import LeadSerializer
from .models import FipeBrand, FipeModel, FipePrice, FipeYear, FipeFuel, Lead, FipeVersion
from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from rest_framework import viewsets

import re

# Etapa 1
@require_http_methods(["GET", "POST"])
def step_1(request):
    search_query = request.GET.get('search', '')
    brands = FipeBrand.objects.filter(show_in_template=True)

    if search_query:
        brands = brands.filter(Q(brand__icontains=search_query))

    if request.method == "POST":
        brand_id = request.POST.get('brand_id')
        if FipeBrand.objects.filter(id=brand_id).exists():
            request.session['brand_id'] = brand_id
            return redirect('fipe_app:step_1_1', brand_id=brand_id)
        else:
            return HttpResponse("Marca selecionada não existe.", status=404)

    if request.is_ajax():
        brands_list = list(brands.values('id', 'brand', 'image'))
        return JsonResponse({'brands': brands_list})

    return render(request, 'leads/step-one-form.html', {'brands': brands})

# Etapa 2
@require_http_methods(["GET", "POST"])
def step_1_1(request, brand_id):
    search_query = request.GET.get('search', '')
    brand = get_object_or_404(FipeBrand, pk=brand_id)
    versions = FipeVersion.objects.filter(brand=brand)

    if search_query:
        versions = versions.filter(Q(name__icontains=search_query))

    if request.method == "POST":
        # O código para lidar com POST deve ser indentado aqui
        version_id = request.POST.get('version_id')
        if FipeVersion.objects.filter(id=version_id, brand=brand).exists():
            request.session['version_id'] = version_id
            return redirect('fipe_app:step_2', version_id=version_id)
        else:
            return HttpResponse("Versão selecionada não existe.", status=404)
    elif request.is_ajax():
        # O código após elif deve ser indentado aqui
        versions_list = list(versions.values('id', 'name'))  # Adapte conforme necessário
        return JsonResponse({'versions': versions_list})

    # O resto do código segue normalmente
    return render(request, 'leads/step-one-one-form.html', {'versions': versions, 'brand': brand})

# Etapa 3
def step_2(request, version_id):
    search_query = request.GET.get('search', '')
    version = get_object_or_404(FipeVersion, pk=version_id)
    models = FipeModel.objects.filter(version=version)
    brand = version.brand  # Obtém o objeto brand associado à versão

    if search_query:
        models = models.filter(Q(model__icontains=search_query))

    if request.method == "POST":
        model_id = request.POST.get('model_id')
        if models.filter(id=model_id).exists():
            request.session['model_id'] = model_id
            return redirect('fipe_app:step_3', model_id=model_id)
        else:
            return HttpResponse("Modelo selecionado não existe.", status=404)
    elif request.is_ajax():
        models_list = list(models.values('id', 'model'))  # Certifique-se de que 'model' é o campo correto.
        return JsonResponse({'models': models_list})

    return render(request, 'leads/step-two-form.html', {
        'models': models,
        'version': version,
        'search_query': search_query,
        'brand': brand,  # Adiciona o objeto brand ao contexto
    })

def step_3(request, model_id):
    if request.method == "POST":
        year_id = request.POST.get('year_id')
        model = get_object_or_404(FipeModel, pk=model_id)  # Obtenha o objeto model com base no ID
        # Verifica se o year_id existe para o modelo selecionado
        if FipeYear.objects.filter(id=year_id, model=model).exists():
            request.session['year_id'] = year_id
            return redirect('fipe_app:step_4', year_id=year_id)
        else:
            return HttpResponse("Ano selecionado não existe.", status=404)
    else:
        years = FipeYear.objects.filter(model_id=model_id)
        return render(request, 'leads/step-three-form.html', {'years': years, 'model_id': model_id})

# Etapa 4
def step_4(request, year_id):
    if request.method == "POST":
        mileage = request.POST.get('mileage')
        request.session['mileage'] = float(mileage)  # Convertendo para float
        # Corrigido para incluir year_id nos argumentos de redirecionamento
        return redirect('fipe_app:step_5', year_id=year_id)
    else:
        return render(request, 'leads/step-four-form.html', {'year_id': year_id})

# Etapa 5
# Etapa 5: Seleção do Combustível
def step_5(request, year_id):
    if request.method == "POST":
        fuel_type = request.POST.get('fuel_type')  # Atenção ao nome do campo aqui
        revisions_done = request.POST.get('revisions_done') == 'true'
        under_warranty = request.POST.get('under_warranty') == 'true'

        print("Fuel Type:", fuel_type)
        print("Revisions Done:", revisions_done)
        print("Under Warranty:", under_warranty)

        if FipeFuel.objects.filter(id=fuel_type, year_id=year_id).exists():
            request.session['fuel_type'] = fuel_type
            request.session['revisions_done'] = revisions_done
            request.session['under_warranty'] = under_warranty

            print("Session Data:", request.session.items())

            return redirect('fipe_app:step_6')
        else:
            return HttpResponse("Combustível selecionado não existe.", status=404)
    else:
        fuels = FipeFuel.objects.filter(year_id=year_id)
        return render(request, 'leads/step-five-form.html', {'fuels': fuels, 'year_id': year_id})


def currency_to_decimal(value):
    if isinstance(value, (float, Decimal)):
        return Decimal(value)
    # Remove os símbolos de moeda e os separadores de milhar
    number_string = re.sub(r'[^\d,]', '', value)
    # Substitui a vírgula do decimal pelo ponto para conversão
    number_string = number_string.replace(',', '.')
    return Decimal(number_string)

def step_6(request):
    if request.method == "POST":
        # Recupera e verifica os dados da sessão
        brand_id = request.session.get('brand_id')
        model_id = request.session.get('model_id')
        year_id = request.session.get('year_id')
        fuel_id = request.session.get('fuel_type')  # Corrigido para 'fuel_type'
        mileage = Decimal(request.session.get('mileage', '0'))  # Convertendo de volta para Decimal
        revisions_done = request.session.get('revisions_done', False)
        under_warranty = request.session.get('under_warranty', False)
        revisions_done_in_css = request.session.get('revisions_done', False)
        under_warranty_css = request.session.get('under_warranty', False)

        print("Dados da sessão:")
        print("Marca ID:", brand_id)
        print("Modelo ID:", model_id)
        print("Ano ID:", year_id)
        print("Combustível ID:", fuel_id)
        print("Quilometragem:", mileage)
        print("Revisões feitas:", revisions_done)
        print("Na garantia:", under_warranty)
        print("Revisões feitas:", revisions_done_in_css)
        print("Na garantia:", under_warranty_css)

        # Busca as instâncias relacionadas
        brand = get_object_or_404(FipeBrand, pk=brand_id)
        model = get_object_or_404(FipeModel, pk=model_id)
        year_obj = get_object_or_404(FipeYear, pk=year_id)
        fuel_obj = get_object_or_404(FipeFuel, pk=fuel_id)

        print("\nInstâncias relacionadas encontradas:")
        print("Marca:", brand)
        print("Modelo:", model)
        print("Ano:", year_obj)
        print("Combustível:", fuel_obj)

        # Busca o FipePrice correspondente
        fipe_price_obj = FipePrice.objects.filter(brand=brand, model=model, year=year_obj, fuel=fuel_obj).first()
        if fipe_price_obj is not None:
            original_price = currency_to_decimal(fipe_price_obj.price)
        else:
            return HttpResponse("No FipePrice matches the given query.", status=404)
        
        # Define a porcentagem inicial com base na quilometragem
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

        print("\nPorcentagem inicial com base na quilometragem:", percentage)

        # Adiciona os percentuais de revisões feitas e garantia
        if revisions_done_in_css:
            percentage += Decimal('0.01')
            print("Percentual de revisões adicionado: 0.01")
        else:
            print("Percentual de revisões não adicionado: 0.00")

        if under_warranty_css:
            percentage += Decimal('0.02')
            print("Percentual de garantia adicionado: 0.02")
        else:
            print("Percentual de garantia não adicionado: 0.00")

        print("\nPorcentagem após adicionar revisões e garantia:", percentage)

        # Ajusta a porcentagem baseada na quilometragem por ano
        current_year = timezone.now().year
        years_passed = max(current_year - year_obj.year, 1)  # Evitar divisão por zero
        km_per_year = mileage / years_passed
        if km_per_year < 10000:
            percentage += Decimal('0.02')
            print("Percentual de +2% adicionado devido à baixa quilometragem por ano.")
        elif km_per_year > 10000:
            percentage -= Decimal('0.03')
            print("Percentual de -3% subtraído devido à alta quilometragem por ano.")

        print("\nPorcentagem após ajuste baseado na quilometragem por ano:", percentage)

        # Listas de modelos com ajustes específicos
            
        # Categorias de mercado
        ruim_mercado = ['NSX 3.0']
        queimados = ['Integra GS 1.8']
        valorizar_modelos = ['MARRUÁ AM 100 2.8 CD TDI Diesel']

        market_category = None
        if model.model in ruim_mercado:
            percentage -= Decimal('0.10')
            market_category = 'Ruim de mercado'
            print("Percentual de -10% subtraído devido ao modelo estar na lista de mercado ruim.")
        elif model.model in queimados:
            percentage -= Decimal('0.30')
            market_category = 'Mercado Queimado'
            print("Percentual de -30% subtraído devido ao modelo estar na lista de modelos queimados.")
        elif model.model in valorizar_modelos:
            percentage += Decimal('0.02')
            market_category = 'Modelo valorizado'
            print("Percentual de +2% adicionado devido ao modelo estar na lista de modelos valorizados.")
        else:
            market_category = "Comum"

        # Verifica se o tipo de combustível é diesel
        if fuel_obj.fuel.lower() == 'diesel':
            percentage -= Decimal('0.10')
            market_category = 'Diesel'
            print("Percentual de -10% subtraído devido ao tipo de combustível ser diesel.")

        # Define a categoria do carro com base na quilometragem
        car_category = 'Salão' if mileage <= 75000 else 'Repasse'

       # Calcula o preço final
        final_price = original_price * percentage

        print("\nPreço final calculado:", final_price)

        # Dados do formulário
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        # Cria a Lead
        lead = Lead.objects.create(
            name=name,
            email=email,
            phone=phone,
            mileage=mileage,
            brand=brand,
            model=model,
            year=year_obj,
            fuel=fuel_obj,
            price=final_price.quantize(Decimal('0.01')),  # Assegura duas casas decimais
            market_category=market_category,
            car_category=car_category,
            original_price=original_price.quantize(Decimal('0.01')),  # Assegura duas casas decimais
            pricing_percentage=percentage.quantize(Decimal('0.01')),  # Assegura duas casas decimais
            created_at=timezone.now(),  # Data e hora atuais
            revisions_done_in_css=revisions_done_in_css,
            under_warranty=under_warranty_css,
        )

        # Redireciona para a página de exibição do preço
        return redirect('fipe_app:show_price', lead_id=lead.id)

    else:
        # Renderiza o formulário se o método não for POST
        return render(request, 'leads/step-six-form.html')
    
# Função de utilitário para formatar números como moeda
def format_currency(value):
    try:
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
    except locale.Error:
        locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')  # Tentativa alternativa
    return locale.currency(value, grouping=True)

def show_price(request, lead_id):
    lead = Lead.objects.get(id=lead_id)
    
    # Formatar os preços
    lead.original_price = format_currency(lead.original_price)
    lead.price = format_currency(lead.price)
    
    return render(request, 'leads/show_price.html', {'lead': lead})


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def get_queryset(self):
        # Se você quiser filtrar os dados, pode fazer isso aqui
        return self.queryset


def index_view(request):
    return render(request, 'leads/index.html')





