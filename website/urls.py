from django.urls import path

from . import views
from . import store_views

urlpatterns = [
    path("", views.home, name="home"),
    path("contacto/", views.contact, name="contact"),
    path("productos/<slug:slug>/", store_views.product_detail, name="product_detail"),
    path("carrito/", store_views.screen, {"page": "cart"}, name="cart"),
    path("cuenta/", store_views.screen, {"page": "account"}, name="account"),
    path("cuenta/ingresar/", store_views.screen, {"page": "sign_in"}, name="sign_in"),
    path("cuenta/registro/", store_views.screen, {"page": "register"}, name="register"),
    path("cuenta/recuperar/", store_views.screen, {"page": "recover"}, name="recover"),
    path("pedido/solicitud/", store_views.screen, {"page": "order_request"}, name="order_request"),
    path("pedido/pago/", store_views.screen, {"page": "payment"}, name="payment"),
    path("tienda/revision/", store_views.screen, {"page": "review"}, name="store_review"),
]
