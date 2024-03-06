import locale
from rest_framework import serializers
from .models import Lead

class LeadSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    original_price = serializers.SerializerMethodField()
    pricing_percentage = serializers.SerializerMethodField()
    revisions_done_in_css = serializers.BooleanField()  # Novo campo
    under_warranty = serializers.BooleanField()  # Novo campo

    class Meta:
        model = Lead
        fields = '__all__'  # Incluirá todos os campos do modelo, incluindo os novos campos booleanos

    def to_representation(self, instance):
        locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')  # Definindo a localização para o Brasil
        representation = super().to_representation(instance)
        representation['brand'] = instance.brand.brand
        representation['model'] = instance.model.model
        representation['year'] = instance.year.year
        representation['fuel'] = instance.fuel.fuel
        representation['market_category'] = instance.market_category
        representation['car_category'] = instance.car_category
        # Aqui, os campos booleanos serão incluídos automaticamente
        return representation

    def get_created_at(self, instance):
        return instance.created_at.strftime('%d/%m/%Y')

    def get_price(self, instance):
        return locale.currency(instance.price, grouping=True)

    def get_original_price(self, instance):
        return locale.currency(instance.original_price, grouping=True)

    def get_pricing_percentage(self, instance):
        return f"{instance.pricing_percentage * 100:.0f}%"
