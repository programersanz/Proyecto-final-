from django import forms
from .models import HorasLudicas, Profile, RegistroAsistencia
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group 
from django.core.validators import RegexValidator

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
    username = forms.CharField(
        max_length=150,
        label="Nombre de usuario",
    )
    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        help_text="Introduce un email válido.",
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nombres",
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Apellidos",
    )
    document_number = forms.CharField(
        max_length=20,
        required=True,
        label="Número de documento",
        validators=[
            RegexValidator(regex=r'^\d+$', message="Solo se permiten dígitos en el documento.")
        ]
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        label="Número de teléfono",
        validators=[
            RegexValidator(regex=r'^\d{10}$', message="El teléfono debe ser de 10 digitos.")
        ]
    )

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "document_number", "phone_number", "password1", "password2"
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
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
        self.fields['usuario'].queryset = User.objects.filter(groups__name__iexact="Aprendiz").distinct()

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class PasswordConfirmationForm(forms.Form):
    current_password = forms.CharField(
        label="Contraseña actual",
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}),
        strip=False,
    )

class EditProfileForm(forms.ModelForm):
    document_number = forms.CharField(
        max_length=20,
        label="Número de documento",
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message="Sólo se permiten dígitos en el documento."
            )
        ]
    )
    phone_number = forms.CharField(
        max_length=15,
        label="Número de teléfono",
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',

            )
        ]
    )

    class Meta:
        model = Profile
        fields = ['document_number', 'phone_number']

class EliminarHorasForm(forms.Form):
    horas_a_eliminar = forms.IntegerField(min_value=1, label="Horas a eliminar")

class RegistroAsistenciaForm(forms.ModelForm):
    class Meta:
        model = RegistroAsistencia
        fields = [
            'nombres_completos',
            'correo',
            'tipo_documento',
            'numero_identificacion',
            'actividad'
        ]
        widgets = {
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_identificacion': forms.TextInput(attrs={
                'class': 'form-control',
                'pattern': '[0-9]*',
                'inputmode': 'numeric',
                'placeholder': 'Solo números'
            }),
        }

