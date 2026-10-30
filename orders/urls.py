from django.urls import path
from payments.views import checkout
from . import views

urlpatterns=[
    path('pedido/solicitud/',views.request_order,name='order_request'),
    path('cuenta/pedidos/',views.order_list,name='order_list'),
    path('pedido/<uuid:public_id>/',views.order_detail,name='order_detail'),
    path('pedido/<uuid:public_id>/cancelar/',views.cancel_order,name='order_cancel'),
    path('pedido/<uuid:public_id>/pago/',checkout,name='order_payment'),
]
