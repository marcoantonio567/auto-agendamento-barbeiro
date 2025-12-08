from django.urls import path
from . import views


urlpatterns = [
    path('', views.step_service, name='step_service'),
    path('barbeiro/', views.step_barber, name='step_barber'),
    path('data/', views.step_date, name='step_date'),
    path('hora/', views.step_hour, name='step_hour'),
    path('cliente/', views.step_client, name='step_client'),
    path('api/horarios/', views.horarios_api, name='horarios_api'),
]
