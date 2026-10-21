from django.urls import path, include

from . import views
from . import store_views
from . import errors

urlpatterns = [
    path("", views.home, name="home"),
    path("contacto/", views.contact, name="contact"),
    path("productos/<slug:slug>/", store_views.product_detail, name="product_detail"),
    path("carrito/", store_views.screen, {"page": "cart"}, name="cart"),
    path("cuenta/", include('accounts.urls')),
    path("pedido/solicitud/", store_views.screen, {"page": "order_request"}, name="order_request"),
    path("pedido/pago/", store_views.screen, {"page": "payment"}, name="payment"),
    path("tienda/revision/", store_views.screen, {"page": "review"}, name="store_review"),
    path("tienda/revision/errores/<int:status>/", errors.preview, name="error_preview"),
]
