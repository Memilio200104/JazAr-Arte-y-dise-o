from django.conf import settings
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET
from .store_presenters import eligible_products, store_context


@require_GET
def product_detail(request, slug):
    context = store_context()
    context["product"] = get_object_or_404(eligible_products(), slug=slug)
    return render(request, "store/product_detail.html", context)


@require_GET
def screen(request, page):
    if page == "review" and not settings.DEBUG:
        raise Http404
    titles = {"cart": "Tu selección", "sign_in": "Qué bueno verte",
              "register": "Tu próxima idea empieza aquí", "recover": "Recupera tu acceso",
              "account": "Tu espacio creativo", "order_request": "Demos forma a tu pedido",
              "payment": "El siguiente paso", "review": "Ejemplos de estados"}
    context = store_context()
    context.update(page=page, page_title=titles[page])
    return render(request, "store/screen.html", context)
