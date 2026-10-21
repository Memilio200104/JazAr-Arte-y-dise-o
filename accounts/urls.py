from django.urls import path
from . import views

urlpatterns=[
    path('',views.account,name='account'),
    path('registro/',views.register,name='register'),
    path('ingresar/',views.sign_in,name='sign_in'),
    path('salir/',views.sign_out,name='sign_out'),
    path('recuperar/',views.recover,name='recover'),
    path('recuperar/listo/',views.recover_done,name='recover_done'),
    path('restablecer/<uidb64>/<token>/',views.ResetConfirm.as_view(),name='password_reset_confirm'),
    path('restablecer/listo/',views.ResetComplete.as_view(),name='reset_complete'),
    path('verificar/reenviar/',views.resend,name='verify_resend'),
    path('verificar/<str:token>/',views.verify,name='verify_email'),
    path('direcciones/',views.addresses,name='addresses'),
    path('direcciones/nueva/',views.address_edit,name='address_new'),
    path('direcciones/<int:pk>/editar/',views.address_edit,name='address_edit'),
    path('direcciones/<int:pk>/eliminar/',views.address_delete,name='address_delete'),
    path('direcciones/<int:pk>/predeterminada/',views.address_default,name='address_default'),
]
