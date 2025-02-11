from django import forms
from .models import HorasLudicas  # Importa tu modelo

class HorasLudicasForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['campo1', 'campo2', 'campo3']  # Reemplaza con los campos de tu modelo