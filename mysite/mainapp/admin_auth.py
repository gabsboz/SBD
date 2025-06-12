from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import konto

class KontoBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = konto.objects.get(login=username)
            if user.check_password(password):
                return user
        except konto.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return konto.objects.get(pk=user_id)
        except konto.DoesNotExist:
            return None
