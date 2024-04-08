import os
import sys
import concurrent.futures
from django.db import models
from django.db.utils import IntegrityError  # Importe a exceção de integridade
import re
from django.db import transaction

# Configurar o ambiente do Django
sys.path.append('script/fipe_project/')  # Ajuste para o caminho do seu projeto
os.environ['DJANGO_SETTINGS_MODULE'] = 'fipe_project.settings'
import django
django.setup()

# Importar modelos do Django
from fipe_app.models import FipeVehicleType, FipeBrand, FipeModel, FipeVersion, FipeYear, FipeFuel, FipeCodeFipe, FipePrice 

def extract_version_name(model_name):
    # Esta função assume que a versão é sempre a primeira parte do nome do modelo
    # e é separada por espaços. Ajuste a lógica conforme necessário.
    return model_name.split(' ')[0]

def populate_fipe_versions():
    with transaction.atomic():
        for model in FipeModel.objects.all():
            version_name = extract_version_name(model.model)
            # Verifica se a versão já existe para a marca
            version, created = FipeVersion.objects.get_or_create(
                name=version_name,
                brand=model.brand
            )
            # Atualiza o modelo para referenciar a versão correta
            model.version = version
            model.save()

if __name__ == "__main__":
    populate_fipe_versions()
    print("Versões do FIPE populadas com sucesso.")
