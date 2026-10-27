from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import DatabaseError
from .models import PaymentAttempt, StockReservation, ProviderEvent
from .services import reconcile_attempt


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False
    def has_change_permission(self, request, obj=None): return False


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(ReadOnlyAdmin):
    list_display=('public_id','order','state','total_minor','created_at')
    list_filter=('state',)
    search_fields=('public_id','order__public_id','session_id')
    readonly_fields=tuple(f.name for f in PaymentAttempt._meta.fields)
    actions=('reconcile','expire')

    def has_reconcile_permission(self,request):
        return request.user.has_perm('payments.reconcile_payment')

    def _run(self,request,queryset,expire):
        for attempt in queryset[:25]:
            try:
                result=reconcile_attempt(attempt.pk,expire=expire)
                self.message_user(request,f'{attempt.public_id}: {result.get_state_display()}')
            except (ValidationError,DatabaseError):
                self.message_user(request,'No se pudo conciliar un intento. Conservamos la reserva.',messages.ERROR)

    @admin.action(description='Consultar estado de pago',permissions=['reconcile'])
    def reconcile(self,request,queryset): self._run(request,queryset,False)

    @admin.action(description='Expirar sesion y conciliar reserva',permissions=['reconcile'])
    def expire(self,request,queryset): self._run(request,queryset,True)


@admin.register(StockReservation)
class StockReservationAdmin(ReadOnlyAdmin):
    list_display=('attempt','product','quantity','state')


@admin.register(ProviderEvent)
class ProviderEventAdmin(ReadOnlyAdmin):
    list_display=('event_id','attempt','processed_at')
