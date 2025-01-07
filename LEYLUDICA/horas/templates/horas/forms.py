from django import forms
from .models import HorasLudicas


class HorasLudicasForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['descripcion', 'horas', 'fecha']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }