# from django.http import HttpResponseForbidden
# from django.contrib.auth import get_user_model
# from .models import RolePermission

# class CustomUserMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         return response

#     def process_view(self, request, view_func, view_args, view_kwargs):
#         user = request.user
#         if user.is_authenticated:
#             if user.is_superuser:
#                 return None
#             allowed_roles = ['superadmin', 'admin']
#             if user.role in allowed_roles and not self.check_permissions(user):
#                 return self.permission_denied(request)
#         return None

#     def check_permissions(self, user):
#         perms = RolePermission.objects.filter(role=user.role)
#         perm_names = [perm.permission.codename for perm in perms]
#         return any(user.has_perm(perm) for perm in perm_names)

#     def permission_denied(self, request):
#         return HttpResponseForbidden("You do not have permission to access this page.")
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.middleware import SessionMiddleware


class CustomSessionMiddleware(SessionMiddleware, MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin'):
            settings.SESSION_ENGINE = 'authentication.session_backend.AdminSessionStore'
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
        else:
            settings.SESSION_ENGINE = 'django.contrib.sessions.backends.db'
            settings.SESSION_COOKIE_NAME = 'sessionid'
        super().process_request(request)
from django.conf import settings

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin'):
            settings.SESSION_ENGINE = settings.ADMIN_SESSION_ENGINE
            settings.SESSION_COOKIE_NAME = 'admin_sessionid'
        else:
            settings.SESSION_ENGINE = 'django.contrib.sessions.backends.db'
            settings.SESSION_COOKIE_NAME = 'sessionid'
        
        response = self.get_response(request)
        return response
    


from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import logout

class SessionExpiryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity', current_time.isoformat())
            last_activity_time = timezone.datetime.fromisoformat(last_activity)

            if current_time - last_activity_time > timedelta(seconds=settings.SESSION_COOKIE_AGE):
                logout(request)
                request.session.flush()
            else:
                request.session['last_activity'] = current_time.isoformat()

        response = self.get_response(request)
        return response
    
from django.utils.deprecation import MiddlewareMixin

class CacheControlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response




