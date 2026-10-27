from django import forms
from django.core import signing
from .models import Product


class ProductAdminForm(forms.ModelForm):
    stock_snapshot = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['stock_snapshot'].initial = signing.dumps({'pk': self.instance.pk, 'stock': self.instance.stock},salt='product-stock')

    def clean(self):
        data = super().clean()
        if self.instance.pk:
            try:
                snapshot = signing.loads(data.get('stock_snapshot',''),salt='product-stock')
                if snapshot != {'pk':self.instance.pk,'stock':self.instance.stock}:
                    raise signing.BadSignature()
            except signing.BadSignature:
                raise forms.ValidationError('Las existencias cambiaron o el formulario vencio. Recarga antes de guardar.') from None
        return data
