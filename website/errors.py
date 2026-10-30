from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.http import Http404
from django.views.decorators.http import require_GET


MESSAGES = {
    400: ('Un trazo fuera del lienzo.', 'No pudimos interpretar esta solicitud. Regresa al inicio e inténtalo de nuevo.'),
    403: ('Esta sala es privada.', 'No podemos completar esta solicitud. Si estabas enviando un formulario, vuelve al inicio y recarga la página antes de intentarlo otra vez.'),
    404: ('Este lienzo está en blanco.', 'La página que buscas no está aquí. Todavía hay muchas ideas por descubrir en JazAr.'),
    500: ('Estamos retocando la obra.', 'Algo no salió como esperábamos. Inténtalo de nuevo en unos momentos o escríbenos por WhatsApp.'),
}


def error_response(status):
    title, message = MESSAGES[status]
    # No database access or request context: the 500 page must survive a DB failure.
    return HttpResponse(render_to_string('errors/page.html', {
        'status': status, 'title': title, 'message': message,
    }), status=status)


def bad_request(request, exception):
    return error_response(400)


def permission_denied(request, exception):
    return error_response(403)


def page_not_found(request, exception):
    return error_response(404)


def server_error(request):
    return error_response(500)


def csrf_failure(request, reason=''):
    return error_response(403)


@require_GET
def preview(request, status):
    if not settings.DEBUG or status not in MESSAGES:
        raise Http404
    response = error_response(status)
    response['Cache-Control'] = 'no-store'
    return response
