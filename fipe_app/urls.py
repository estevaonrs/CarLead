from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from django.conf import settings
from django.conf.urls.static import static

app_name = 'fipe_app'

router = DefaultRouter()
router.register(r'leads', views.LeadViewSet)

urlpatterns = [
    path('', views.index_view, name='index'),
    path('step-4/', views.step_4, name='step_4'),
    path('step-6/', views.step_6, name='step_6'),
    path('show-price/<int:lead_id>/', views.show_price, name='show_price'),
    path('api/', include(router.urls)),
    path('listar-marcas/', views.listar_marcas, name='listar_marcas'),
    path('listar-modelos/', views.listar_modelos, name='listar_modelos'),
    path('listar-ano-modelos/', views.listar_ano_modelos, name='listar_ano_modelos'),


]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
