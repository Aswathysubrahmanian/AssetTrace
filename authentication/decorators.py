from functools import wraps
from django.core.exceptions import PermissionDenied
from .models import RolePermission

def custom_permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                raise PermissionDenied
            user_role = get_user_role(request.user)
            if RolePermission.objects.filter(role=user_role, permission=permission, enabled=True).exists():
                return view_func(request, *args, **kwargs)
            else:
                raise PermissionDenied
        return _wrapped_view
    return decorator

def get_user_role(user):
    if user.is_superuser:
        return 'super_admin'
    elif user.groups.filter(name='Super Admin').exists():
        return 'super_admin'
    elif user.groups.filter(name='Admin').exists():
        return 'admin'
    else:
        return 'unknown'
