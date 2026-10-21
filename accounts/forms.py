import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordResetForm
from .models import CustomerProfile, ShippingAddress
from .services import normalize_email


class RegistrationForm(forms.Form):
    full_name = forms.CharField(label='Nombre completo', max_length=150, widget=forms.TextInput(attrs={'autocomplete':'name'}))
    email = forms.EmailField(label='Correo electrónico', max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email','spellcheck':'false'}))
    password1 = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))
    password2 = forms.CharField(label='Confirma tu contraseña', strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'new-password'}))

    def clean(self):
        data = super().clean()
        if data.get('password1') != data.get('password2'):
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return data


class LoginForm(forms.Form):
    email = forms.EmailField(label='Correo electrónico', max_length=254, widget=forms.EmailInput(attrs={'autocomplete':'email','spellcheck':'false'}))
    password = forms.CharField(label='Contraseña', strip=False, widget=forms.PasswordInput(attrs={'autocomplete':'current-password'}))

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean(self):
        data = super().clean()
        if data.get('email') and data.get('password'):
            self.user = authenticate(self.request, email=data['email'], password=data['password'])
            if self.user is None:
                raise forms.ValidationError('Revisa tu correo y contraseña e inténtalo de nuevo.')
        return data


class NameForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ['full_name']
        labels = {'full_name':'Nombre completo'}
        widgets = {'full_name':forms.TextInput(attrs={'autocomplete':'name'})}


class AddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['label','recipient','phone','street','exterior','interior','district','postcode','city','state','reference']
        labels = dict(label='Nombre de la dirección (opcional)',recipient='Nombre de quien recibe',phone='Teléfono de contacto',street='Calle',exterior='Número exterior',interior='Número interior (opcional)',district='Colonia',postcode='Código postal',city='Municipio o alcaldía',state='Estado',reference='Referencias de entrega (opcional)')
        widgets = {'reference':forms.Textarea(attrs={'rows':3}), 'postcode':forms.TextInput(attrs={'inputmode':'numeric','autocomplete':'shipping postal-code'}), 'phone':forms.TextInput(attrs={'type':'tel','autocomplete':'shipping tel'}), 'recipient':forms.TextInput(attrs={'autocomplete':'shipping name'}), 'city':forms.TextInput(attrs={'autocomplete':'shipping address-level2'}), 'state':forms.TextInput(attrs={'autocomplete':'shipping address-level1'})}

    def clean_postcode(self):
        value=self.cleaned_data['postcode']
        if not re.fullmatch(r'[0-9]{5}',value):
            raise forms.ValidationError('Escribe los cinco dígitos del código postal.')
        return value

    def clean_phone(self):
        value=self.cleaned_data['phone']
        if not re.fullmatch(r'[+0-9 ()-]+',value) or not 10 <= len(re.sub(r'[^0-9]','',value)) <= 15:
            raise forms.ValidationError('Escribe un teléfono de 10 a 15 dígitos.')
        return value


class CustomerResetForm(PasswordResetForm):
    def get_users(self, email):
        for profile in CustomerProfile.objects.select_related('user').filter(email=normalize_email(email),user__is_active=True):
            if profile.user.has_usable_password():
                yield profile.user
