from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('agendamento.urls')),
    path('', include('pagamentos.urls')),
    path('', include('painel.urls')),
    path('admin/', admin.site.urls),
]
