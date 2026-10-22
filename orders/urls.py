from django.urls import path
from . import views

urlpatterns=[
    path('pedido/solicitud/',views.request_order,name='order_request'),
    path('cuenta/pedidos/',views.order_list,name='order_list'),
    path('pedido/<uuid:public_id>/',views.order_detail,name='order_detail'),
    path('pedido/<uuid:public_id>/pago/',views.order_detail,{'payment':True},name='order_payment'),
]
