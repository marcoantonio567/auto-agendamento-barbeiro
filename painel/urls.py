from django.urls import path
from . import views


urlpatterns = [
    path('admin/entrar/', views.login_view, name='login'),
    path('admin/sair/', views.logout_view, name='logout'),
    path('admin/painel/', views.admin_list, name='admin_list'),
    path('admin/painel/<int:appointment_id>/', views.admin_detail, name='admin_detail'),
    path('admin/historico/', views.admin_history, name='admin_history'),
    path('admin/financeiro/', views.admin_finance, name='admin_finance'),
]