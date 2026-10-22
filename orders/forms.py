import json
from django import forms
from django.core.exceptions import ValidationError


class RequestForm(forms.Form):
    rows=forms.CharField(widget=forms.HiddenInput)
    address=forms.ModelChoiceField(queryset=None,label='Dirección de envío',empty_label='Selecciona una dirección')
    notes=forms.CharField(required=False,max_length=1500,label='Notas para Jazmin (opcional)',widget=forms.Textarea(attrs={'rows':3,'autocomplete':'off'}))

    def __init__(self,*args,customer,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['address'].queryset=customer.addresses.all()
        self.fields['address'].label_from_instance=lambda a: f'{a.label or a.recipient}: {a.street} {a.exterior}, {a.postcode}'

    def clean_rows(self):
        try: return json.loads(self.cleaned_data['rows'])
        except (ValueError,TypeError): raise ValidationError('No pudimos leer la selección. Vuelve al carrito.') from None
