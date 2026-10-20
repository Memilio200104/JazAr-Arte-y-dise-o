from django.contrib import admin
from django.utils.html import format_html
from .models import Product, Package, SiteContent


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'thumbnail', 'sku', 'sale_mode', 'price', 'technique_key', 'is_active', 'is_concept', 'sort_order')
    list_filter = ('sale_mode', 'is_active', 'is_concept', 'technique_key', 'category')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    fieldsets = (
        ('Contenido', {'fields': ('name', 'slug', 'description', 'category', 'technique_key')}),
        ('Imagen', {'fields': ('photo', 'image_alt', 'is_concept', 'image')}),
        ('Publicacion', {'fields': ('is_active', 'sort_order')}),
        ('Datos comerciales; no habilitan cobros', {'fields': ('sku', 'sale_mode', 'price', 'price_note', 'currency', 'stock', 'catalog_page')}),
    )

    @admin.display(description='Imagen')
    def thumbnail(self, obj):
        return format_html('<img src="{}" alt="" width="48" height="48" style="object-fit:cover">', obj.image_url)


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'sort_order')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return super().has_add_permission(request) and not SiteContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.site_header = 'JazAr · Contenido'
admin.site.site_title = 'JazAr'
