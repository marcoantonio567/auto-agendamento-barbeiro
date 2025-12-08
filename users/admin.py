from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils.translation import gettext_lazy as _


User = get_user_model()
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'cpf', 'phone', 'is_active', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'cpf', 'phone')
    ordering = ('username',)
    fieldsets = UserAdmin.fieldsets + (
        (_('Informações adicionais'), {'fields': ('cpf', 'phone', 'card_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('cpf', 'phone', 'card_id')}),
    )


class CustomGroupAdmin(GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)
