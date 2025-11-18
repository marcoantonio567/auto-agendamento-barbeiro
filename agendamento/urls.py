from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('servico/', views.step_service, name='step_service'),
    path('barbeiro/', views.step_barber, name='step_barber'),
    path('data/', views.step_date, name='step_date'),
    path('hora/', views.step_hour, name='step_hour'),
    path('cliente/', views.step_client, name='step_client'),
    path('api/horarios/', views.horarios_api, name='horarios_api'),
    path('pagamento/<int:appointment_id>/', views.pagamento, name='pagamento'),
    path('pagamento/<int:appointment_id>/confirmar/', views.pagamento_confirmar, name='pagamento_confirmar'),
    path('pagamento/<int:appointment_id>/falhar/', views.pagamento_falhar, name='pagamento_falhar'),
    path('admin/painel/', views.admin_list, name='admin_list'),
    path('admin/painel/<int:appointment_id>/', views.admin_detail, name='admin_detail'),
]