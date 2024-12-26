from django.contrib.sessions.backends.db import SessionStore as DBStore

class AdminSessionStore(DBStore):
    @classmethod
    def get_model_class(cls):
        from .models import AdminSession
        return AdminSession