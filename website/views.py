from smtplib import SMTPException
from urllib.parse import urlencode

from django.conf import settings
from django.core import signing
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from .catalog import PACKAGES
from .forms import ContactForm
from .models import Product
from .throttle import allow_contact


def page(request, form=None, contact_status="", status=200):
    return render(request, "website/home.html", {
        "form": form if form is not None else ContactForm(),
        "products": Product.objects.filter(is_active=True), "packages": PACKAGES, "contact_status": contact_status,
        "contact_local_mode": settings.CONTACT_LOCAL_MODE,
    }, status=status)


@require_GET
def home(request):
    status = ""
    try:
        signed = signing.loads(request.GET.get("contact", ""), salt="contact-confirmation", max_age=300)
        if signed in ("sent", "local"):
            status = signed
    except signing.BadSignature:
        pass
    return page(request, contact_status=status)


@require_POST
def contact(request):
    form = ContactForm(request.POST)
    if not form.is_valid():
        return page(request, form, "invalid", 400)
    address = request.META.get("REMOTE_ADDR", "unknown")
    if settings.CONTACT_TRUST_PROXY:
        address = request.META.get("HTTP_X_REAL_IP", address)
    try:
        allowed = allow_contact(address)
    except OSError:
        allowed = False
    if not allowed:
        form.add_error(None, "Has enviado varias solicitudes. Espera unos minutos antes de intentarlo de nuevo.")
        response = page(request, form, "rate_limited", 429)
        response["Retry-After"] = str(settings.CONTACT_RATE_WINDOW)
        return response
    smtp = settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend"
    configured = bool(settings.CONTACT_EMAIL and settings.DEFAULT_FROM_EMAIL)
    configured = configured and ((smtp and settings.EMAIL_HOST_USER and settings.EMAIL_HOST_PASSWORD)
                                 or (not smtp and settings.CONTACT_LOCAL_MODE))
    sent = False
    if configured:
        data = form.cleaned_data
        body = "\n".join([
            "Solicitud de cotizaci\u00f3n JazAr", f"Nombre: {data['name']}",
            f"Correo: {data['email']}",
            f"Inter\u00e9s: {dict(form.fields['interest'].choices)[data['interest']]}",
            f"Cantidad aproximada: {data['quantity']}",
            f"Fecha deseada: {data['desired_date'] or 'Sin definir'}", "", data["message"],
        ])
        try:
            sent = EmailMessage(
                subject="Nueva idea para JazAr", body=body, from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL], reply_to=[data["email"]],
            ).send(fail_silently=False) == 1
        except (SMTPException, OSError, ValueError):
            sent = False
    if not sent:
        form.add_error(None, "No pudimos enviar tu solicitud. Tus datos siguen aqu\u00ed para que puedas intentarlo de nuevo.")
        return page(request, form, "error", 503)
    status = "sent" if smtp else "local"
    token = signing.dumps(status, salt="contact-confirmation")
    return HttpResponseRedirect(reverse("home") + "?" + urlencode({"contact": token}) + "#contacto")
