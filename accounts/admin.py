from django.contrib import admin
from .models import CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['full_name','email','email_verified_at']
    readonly_fields = ['user','email','email_verified_at','default_address']
    search_fields = ['full_name','email']

    def has_add_permission(self,request):
        return False

    def has_delete_permission(self,request,obj=None):
        return False
