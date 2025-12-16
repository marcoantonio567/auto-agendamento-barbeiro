from django.urls import path
from . import views


urlpatterns = [
    path('admin/entrar/', views.LoginView.as_view(), name='login'),
    path('admin/sair/', views.LoginView.logout, name='logout'),
    path('admin/dashboard/', views.admin_list, name='admin_list'),
    path('admin/dashboard/<int:appointment_id>/', views.admin_detail, name='admin_detail'),
    path('admin/dashboard/<int:appointment_id>/shift/<str:direction>/', views.admin_shift_hour, name='admin_shift_hour'),
    path('admin/dashboard/<int:appointment_id>/cash/confirm/', views.admin_confirm_cash, name='admin_confirm_cash'),
    path('admin/historico/', views.admin_history, name='admin_history'),
    path('admin/financeiro/', views.admin_finance, name='admin_finance'),
    path('api/whatsapp/send/', views.whatsapp_send, name='whatsapp_send'),
]
