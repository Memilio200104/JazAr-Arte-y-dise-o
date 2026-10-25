from django.contrib import admin
from django.utils import timezone
from .models import PackageProfile, ProductPacking


class PackingAdmin(admin.ModelAdmin):
    readonly_fields = ('validated_at', 'validated_by')
    actions = ['validate_packing']

    @admin.action(description='Confirmar medidas y capacidad revisadas', permissions=['change'])
    def validate_packing(self, request, queryset):
        for packing in queryset:
            packing.full_clean()
            packing.validated_at = timezone.now()
            packing.validated_by = request.user
            packing.save()
        self.message_user(request, 'Datos de empaque confirmados.')


@admin.register(PackageProfile)
class PackageProfileAdmin(PackingAdmin):
    list_display = ('name', 'capacity', 'max_weight_kg', 'active', 'validated_at')
    list_filter = ('active',)


@admin.register(ProductPacking)
class ProductPackingAdmin(PackingAdmin):
    list_display = ('product', 'profile', 'capacity_units', 'protected_unit_weight_kg', 'validated_at')
    list_select_related = ('product', 'profile')
    autocomplete_fields = ('product',)
