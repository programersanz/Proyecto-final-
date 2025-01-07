from django import forms
from .models import HorasLudicas

class HorasLudicasForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['campo1', 'campo2', 'campo3']  # Cambia los campos por los de tu modelo