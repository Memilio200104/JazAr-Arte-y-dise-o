from django.urls import path
from .views import stripe_webhook

urlpatterns = [path('pagos/stripe/webhook/',stripe_webhook,name='stripe_webhook')]
