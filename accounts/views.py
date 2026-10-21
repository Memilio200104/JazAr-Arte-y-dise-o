from functools import wraps
from smtplib import SMTPException
from urllib.parse import urlsplit
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetConfirmView, PasswordResetCompleteView
from django.core.exceptions import PermissionDenied, ValidationError, ImproperlyConfigured
from django.db import DatabaseError
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_http_methods, require_POST
from website.store_presenters import store_context
from .forms import RegistrationForm, LoginForm, NameForm, AddressForm, CustomerResetForm
from .models import CustomerProfile
from .services import register_customer, save_address, delete_address, set_default_address
from .limits import consume_limits
from .mail import send_verification, account_origin
from .tokens import verify_email


def page(request, title, **context):
    return render(request,'accounts/page.html',{**store_context(),'page_title':title,**context})


def limited(request,action,email=''):
    try:
        allowed,retry=consume_limits(action,request.META.get('REMOTE_ADDR',''),email)
    except DatabaseError:
        return HttpResponse('No pudimos completar la solicitud. Inténtalo de nuevo en unos momentos.',status=503)
    if not allowed:
        response=HttpResponse('Demasiados intentos. Espera unos minutos antes de intentarlo de nuevo.',status=429)
        response['Retry-After']=str(retry)
        return response
    return None


def customer_required(view):
    @wraps(view)
    def wrapped(request,*args,**kwargs):
        profile=CustomerProfile.objects.filter(user=request.user,user__is_active=True).first()
        if profile is None:
            raise PermissionDenied
        request.customer=profile
        return view(request,*args,**kwargs)
    return never_cache(login_required(wrapped))


@never_cache
@sensitive_post_parameters('password1','password2')
@require_http_methods(['GET','POST'])
def register(request):
    if request.method=='POST':
        blocked=limited(request,'register')
        if blocked is not None: return blocked
    form=RegistrationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:
            profile=register_customer(form.cleaned_data['full_name'],form.cleaned_data['email'],form.cleaned_data['password1'])
        except ValidationError as exc:
            form.add_error(None,exc)
        except DatabaseError:
            form.add_error(None,'No pudimos guardar la cuenta. Inténtalo de nuevo en unos momentos.')
        else:
            login(request,profile.user,backend='accounts.backends.CustomerEmailBackend')
            sent=send_verification(profile)
            messages.info(request,mail_notice(sent))
            return redirect('account')
    return page(request,'Crea tu cuenta',form=form,action_label='Crear cuenta',kind='register')


def mail_notice(sent):
    if not sent:
        return 'No pudimos enviar el enlace. Tu cuenta sigue pendiente de verificación; puedes volver a solicitarlo.'
    if settings.CONTACT_LOCAL_MODE:
        return 'El enlace de verificación se generó en la consola local; no se envió un correo real.'
    return 'Solicitamos el envío del enlace de verificación a tu correo.'


@never_cache
@sensitive_post_parameters('password')
@require_http_methods(['GET','POST'])
def sign_in(request):
    if request.method=='POST':
        blocked=limited(request,'login',request.POST.get('email',''))
        if blocked is not None: return blocked
    form=LoginForm(request.POST or None,request=request)
    if request.method=='POST' and form.is_valid():
        login(request,form.user)
        target=request.GET.get('next','')
        if not target.startswith('/') or target.startswith('//') or '\\' in target or not url_has_allowed_host_and_scheme(target,allowed_hosts=set()):
            target='/cuenta/'
        return redirect(target)
    return page(request,'Qué bueno verte',form=form,action_label='Ingresar',kind='login')


@require_POST
@never_cache
def sign_out(request):
    logout(request)
    return redirect('home')


@customer_required
@require_http_methods(['GET','POST'])
def account(request):
    form=NameForm(request.POST or None,instance=request.customer)
    if request.method=='POST' and form.is_valid():
        try:
            form.save()
        except DatabaseError:
            form.add_error(None,'No pudimos guardar tu nombre. Inténtalo de nuevo.')
        else:
            messages.success(request,'Tu nombre se actualizó.')
            return redirect('account')
    return page(request,'Tu espacio creativo',form=form,action_label='Guardar nombre',kind='account',customer=request.customer)


@customer_required
@require_POST
def resend(request):
    blocked=limited(request,'verify',request.customer.email)
    if blocked is not None: return blocked
    if request.customer.email_verified_at is None:
        messages.info(request,mail_notice(send_verification(request.customer)))
    return redirect('account')


@never_cache
@require_http_methods(['GET','POST'])
def verify(request,token):
    valid=None
    if request.method=='POST':
        valid=verify_email(token)
    return page(request,'Confirma tu correo',kind='verify',verified=valid)


@never_cache
@require_http_methods(['GET','POST'])
def recover(request):
    if request.method=='POST':
        blocked=limited(request,'recovery',request.POST.get('email',''))
        if blocked is not None: return blocked
    form=CustomerResetForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        try:
            origin=urlsplit(account_origin())
            form.save(domain_override=origin.netloc,use_https=origin.scheme=='https',
                      from_email=settings.DEFAULT_FROM_EMAIL,email_template_name='accounts/reset_email.txt',
                      subject_template_name='accounts/reset_subject.txt',request=request)
        except (SMTPException,OSError,ValueError,ImproperlyConfigured):
            # Same response for all addresses, including transport failure.
            pass
        return redirect('recover_done')
    return page(request,'Recupera tu acceso',form=form,action_label='Solicitar enlace',kind='recover')


@never_cache
@require_http_methods(['GET'])
def recover_done(request):
    return page(request,'Revisa el siguiente paso',kind='recover_done',local_mail=settings.CONTACT_LOCAL_MODE)


class ResetConfirm(PasswordResetConfirmView):
    template_name='accounts/reset.html'
    success_url=reverse_lazy('reset_complete')

    def get_context_data(self,**kwargs):
        return {**super().get_context_data(**kwargs),**store_context(),'page_title':'Elige una nueva contraseña'}


class ResetComplete(PasswordResetCompleteView):
    template_name='accounts/reset_complete.html'

    def get_context_data(self,**kwargs):
        return {**super().get_context_data(**kwargs),**store_context(),'page_title':'Contraseña actualizada'}


@customer_required
@require_http_methods(['GET'])
def addresses(request):
    return page(request,'Tus direcciones',kind='addresses',addresses=request.customer.addresses.all(),customer=request.customer)


@customer_required
@require_http_methods(['GET','POST'])
def address_edit(request,pk=None):
    instance=get_object_or_404(request.customer.addresses,pk=pk) if pk else None
    form=AddressForm(request.POST or None,instance=instance)
    if request.method=='POST' and form.is_valid():
        try:
            save_address(request.customer,form.cleaned_data,pk)
        except DatabaseError:
            form.add_error(None,'No pudimos guardar la dirección. Inténtalo de nuevo.')
        else:
            messages.success(request,'Dirección guardada.')
            return redirect('addresses')
    return page(request,'Editar dirección' if pk else 'Nueva dirección',form=form,action_label='Guardar dirección',kind='address_edit')


@customer_required
@require_http_methods(['GET','POST'])
def address_delete(request,pk):
    address=get_object_or_404(request.customer.addresses,pk=pk)
    if request.method=='POST':
        try:
            delete_address(request.customer,pk)
        except DatabaseError:
            messages.error(request,'No pudimos eliminar la dirección. Inténtalo de nuevo.')
        else:
            messages.success(request,'Dirección eliminada.')
            return redirect('addresses')
    return page(request,'Eliminar dirección',kind='address_delete',address=address)


@customer_required
@require_POST
def address_default(request,pk):
    try:
        set_default_address(request.customer,pk)
    except DatabaseError:
        messages.error(request,'No pudimos cambiar la dirección predeterminada. Inténtalo de nuevo.')
    return redirect('addresses')
