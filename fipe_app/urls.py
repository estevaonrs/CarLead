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
    path('step-1', views.step_1, name='step_1'),
    path('step-2/<int:brand_id>/', views.step_2, name='step_2'),
    path('step-3/<int:model_id>/', views.step_3, name='step_3'),
    path('step-4/<int:year_id>/', views.step_4, name='step_4'),
    path('step-5/<int:year_id>/', views.step_5, name='step_5'),
    path('step-6/', views.step_6, name='step_6'),
    path('show-price/<int:lead_id>/', views.show_price, name='show_price'),
    path('api/', include(router.urls)),

    # Adicione uma URL para a página de sucesso
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
