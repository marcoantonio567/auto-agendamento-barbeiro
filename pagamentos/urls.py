from django.urls import path
from . import views


urlpatterns = [
    path('pagamento/<int:appointment_id>/', views.pagamento, name='pagamento'),
    path('pagamento/<int:appointment_id>/confirmar/', views.pagamento_confirmar, name='pagamento_confirmar'),
    path('pagamento/<int:appointment_id>/falhar/', views.pagamento_falhar, name='pagamento_falhar'),
]