from django.urls import path
from . import views


urlpatterns = [
    path('pagamento/<str:sid>/', views.pagamento, name='pagamento'),
    path('pagamento/<str:sid>/confirmar/', views.pagamento_confirmar, name='pagamento_confirmar'),
    path('pagamento/<str:sid>/falhar/', views.pagamento_falhar, name='pagamento_falhar'),
    path('pagamento/<str:sid>/check/', views.pagamento_check, name='pagamento_check'),
    path('pagamento/<str:sid>/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
]
