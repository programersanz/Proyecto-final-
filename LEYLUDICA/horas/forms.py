from django import forms
from .models import HorasLudicas
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group 

class HorasLudicasForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['descripcion', 'horas', 'fecha', 'usuario'] # Reemplaza con los campos de tu modelo



class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

class CustomUserCreationForm(UserCreationForm):
    document_number = forms.CharField(max_length=20, required=True, label="Número de documento")
    email = forms.EmailField(required=True, label="Correo electrónico")
    first_name = forms.CharField(max_length=30, required=True, label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, label="Apellidos")
    phone_number = forms.CharField(max_length=20, required=True, label="Número de teléfono")
    
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "document_number", "phone_number", "password1", "password2")
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
            # Guardamos los datos extras en el perfil (la señal se encargará de crearlo si no existe)
            user.profile.document_number = self.cleaned_data["document_number"]
            user.profile.phone_number = self.cleaned_data["phone_number"]
            user.profile.save()
        return user

class HorasLudicasBienestarForm(forms.ModelForm):
    class Meta:
        model = HorasLudicas
        fields = ['descripcion', 'horas', 'fecha', 'usuario']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra el queryset para mostrar sólo usuarios que pertenecen al grupo "Aprendiz"
        self.fields['usuario'].queryset = User.objects.filter(groups__name="Aprendiz")
