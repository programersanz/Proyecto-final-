from django import forms
from .models import HorasLudicas  # Importa tu modelo

class HorasLudicasForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['descripcion', 'horas', 'fecha', 'usuario']  # Reemplaza con los campos de tu modelo