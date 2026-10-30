from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from .models import CustomerProfile
from .services import normalize_email


class CustomerEmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None or password is None:
            return None
        profile = CustomerProfile.objects.select_related('user').filter(email=normalize_email(email)).first()
        if profile is None:
            get_user_model()().set_password(password)
            return None
        if profile.user.check_password(password) and self.user_can_authenticate(profile.user):
            return profile.user
        return None
