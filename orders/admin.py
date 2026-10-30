from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import DatabaseError, transaction
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, OrderReviewEvent
from .services import review_order, ReviewConflict
from shipping.models import Shipment
from shipping.tracking import register_shipment
from payments.models import Refund


class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ('carrier', 'tracking_number', 'tracking_url', 'status')
        help_texts = {'tracking_url': 'Copia el enlace público HTTPS de la guía creada en Envia. No pegues enlaces del panel privado.'}


class ReviewForm(forms.Form):
    approved=forms.BooleanField(required=False,label='Diseño revisado y aprobado por Jazmin')
    changes=forms.BooleanField(required=False,label='Solicitar cambios al cliente')
    note=forms.CharField(required=False,max_length=1500,label='Nota visible para el cliente',widget=forms.Textarea(attrs={'rows':3}))
    version=forms.IntegerField(min_value=0,widget=forms.HiddenInput)

    def clean(self):
        data=super().clean()
        if data.get('approved') and data.get('changes'):
            raise ValidationError('Elige aprobar o solicitar cambios, no ambas opciones.')
        if data.get('changes') and not data.get('note','').strip():
            self.add_error('note','Describe los cambios necesarios.')
        return data


class ItemInline(admin.TabularInline):
    model=OrderItem
    extra=0
    fields=('sku','name','unit_price','quantity','details')
    readonly_fields=fields
    can_delete=False
    def has_add_permission(self,request,obj=None): return False
    def has_change_permission(self,request,obj=None): return False
    def has_view_permission(self,request,obj=None): return request.user.has_perm('orders.view_order')


class EventInline(ItemInline):
    model=OrderReviewEvent
    fields=('actor','from_status','to_status','note','created_at')
    readonly_fields=fields


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    change_form_template='admin/orders/order/change_form.html'
    list_display=('public_id','created_at','customer','subtotal','review_status')
    list_filter=('review_status','created_at')
    search_fields=('public_id','customer__email')
    fields=('public_id','customer','created_at','subtotal','currency','shipping_address','notes','review_status','review_note','approved_by','approved_at')
    readonly_fields=fields
    inlines=(ItemInline,EventInline)

    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
    def has_change_permission(self,request,obj=None): return False

    def get_urls(self):
        return [path('<int:object_id>/review/',self.admin_site.admin_view(require_POST(self.review)),name='orders_order_review'),
            path('<int:object_id>/shipment/',self.admin_site.admin_view(require_POST(self.shipment)),name='orders_order_shipment')]+super().get_urls()

    def change_view(self,request,object_id,form_url='',extra_context=None):
        order=get_object_or_404(Order,pk=object_id)
        context=dict(extra_context or {})
        context['cancellation'] = Refund.objects.filter(attempt__order=order).first()
        if context['cancellation']:
            context['cancellation_url'] = reverse('admin:payments_refund_change', args=[context['cancellation'].pk])
        if request.user.has_perm('shipping.manage_shipment') and order.payment_attempts.filter(state='paid').exists() and not context['cancellation']:
            context.update(shipment_form=ShipmentForm(instance=Shipment.objects.filter(order=order).first()),
                           shipment_url=reverse('admin:orders_order_shipment',args=[order.pk]))
        if request.user.has_perm('orders.approve_order'):
            context.update(review_form=ReviewForm(initial={'approved':order.review_status=='approved','changes':order.review_status=='changes','note':order.review_note,'version':order.version}),review_url=reverse('admin:orders_order_review',args=[order.pk]))
        return super().change_view(request,object_id,form_url,context)

    @transaction.atomic
    def shipment(self, request, object_id):
        order = get_object_or_404(Order, pk=object_id)
        if not self.has_view_permission(request, order) or not request.user.has_perm('shipping.manage_shipment'):
            raise PermissionDenied
        form = ShipmentForm(request.POST)
        if form.is_valid():
            try:
                shipment = register_shipment(request.user, order.pk, **form.cleaned_data)
                self.log_change(request, order, f'Guía: {shipment.carrier} / {shipment.tracking_number}; {shipment.get_status_display()}')
            except ValidationError as exc:
                form.add_error(None, exc)
            else:
                messages.success(request, 'Guía guardada. El cliente puede verla en Mis pedidos.')
                return redirect('admin:orders_order_change', order.pk)
        return TemplateResponse(request, 'admin/orders/order/shipment_error.html', {
            **self.admin_site.each_context(request), 'title': 'Registrar guía', 'shipment_form': form,
            'shipment_url': reverse('admin:orders_order_shipment',args=[order.pk]),
            'back_url': reverse('admin:orders_order_change',args=[order.pk])}, status=400)

    def review(self,request,object_id):
        order=get_object_or_404(Order,pk=object_id)
        if not self.has_view_permission(request,order) or not request.user.has_perm('orders.approve_order'):
            raise PermissionDenied
        form=ReviewForm(request.POST)
        status=400
        if form.is_valid():
            data=form.cleaned_data
            target='approved' if data['approved'] else ('changes' if data['changes'] else 'pending')
            try:
                review_order(request.user,order.pk,data['version'],target,data['note'])
            except ReviewConflict as exc:
                form.add_error(None,exc); status=409
            except ValidationError as exc:
                form.add_error(None,exc)
            except DatabaseError:
                form.add_error(None,'No pudimos guardar la revisión. Inténtalo de nuevo.'); status=503
            else:
                messages.success(request,'Revisión guardada. No se ha realizado ningún cobro.')
                return redirect('admin:orders_order_change',order.pk)
        return TemplateResponse(request,'admin/orders/order/review_error.html',{
            **self.admin_site.each_context(request),'title':'Revisar pedido','review_form':form,
            'review_url':reverse('admin:orders_order_review',args=[order.pk]),
            'back_url':reverse('admin:orders_order_change',args=[order.pk])},status=status)
