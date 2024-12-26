from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class AdminBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if request.path.startswith('/admin'):
            UserModel = get_user_model()
            try:
                user = UserModel.objects.get(email=username)
                if user.is_staff and user.check_password(password):
                    return user
            except UserModel.DoesNotExist:
                return None
        return None