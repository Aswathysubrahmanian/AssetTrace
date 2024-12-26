from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Client,HeadOffice,Branches,RolePermission,Departments

class CustomUserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ()}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_superadmin', 'is_admin', 'groups', 'user_permissions')}),
     
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'is_superadmin', 'is_admin'),
        }),
    )
    list_display = ('username', 'is_staff', 'is_superuser', 'is_superadmin', 'is_admin')
    search_fields = ('username',)
    ordering = ('username',)

class ClientAdmin(admin.ModelAdmin):
    list_display = ('prefix', 'client_name', 'client_address', 'client_contact')
    search_fields = ('prefix', 'client_name')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(HeadOffice)
admin.site.register(Branches)
admin.site.register(RolePermission)
admin.site.register(Departments)