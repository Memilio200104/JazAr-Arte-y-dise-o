from django import forms
from django.utils import timezone


INTERESTS = [
    ("", "Selecciona una opci\u00f3n"), ("prendas", "Prendas"), ("regalos", "Regalos"),
    ("textiles", "Textiles"), ("piezas-3d", "Piezas 3D"),
    ("regalo", "Un regalo con intenci\u00f3n"), ("equipo", "Tu equipo, con identidad"),
    ("marca", "Tu marca, en cada detalle"), ("orientacion", "A\u00fan no lo s\u00e9"),
]


class ContactForm(forms.Form):
    name = forms.CharField(label="Nombre", max_length=120,
                           widget=forms.TextInput(attrs={"autocomplete": "name"}))
    email = forms.EmailField(label="Correo electr\u00f3nico", max_length=254,
                             widget=forms.EmailInput(attrs={"autocomplete": "email", "spellcheck": "false"}))
    interest = forms.ChoiceField(label="\u00bfQu\u00e9 quieres crear?", choices=INTERESTS)
    quantity = forms.IntegerField(label="Cantidad aproximada", min_value=1, max_value=100000,
                                   widget=forms.NumberInput(attrs={"inputmode": "numeric"}))
    desired_date = forms.DateField(label="Fecha deseada (opcional)", required=False,
                                   widget=forms.DateInput(attrs={"type": "date"}))
    message = forms.CharField(label="Cu\u00e9ntame tu idea", max_length=5000, min_length=10,
                              widget=forms.Textarea(attrs={"rows": 4}))
    website = forms.CharField(required=False, label="Deja este campo vac\u00edo", max_length=200,
                               widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "input"
        self.fields["desired_date"].widget.attrs["min"] = timezone.localdate().isoformat()

    def clean_desired_date(self):
        value = self.cleaned_data["desired_date"]
        if value and value < timezone.localdate():
            raise forms.ValidationError("Elige una fecha de hoy en adelante.")
        return value

    def clean_website(self):
        if self.cleaned_data["website"]:
            raise forms.ValidationError("No pudimos validar esta solicitud.")
        return ""
