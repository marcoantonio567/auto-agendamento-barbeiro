from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('agendamento.urls')),
    path('', include('pagamentos.urls')),
    path('', include('dashboard.urls')),
    path('admin/', admin.site.urls),
]
