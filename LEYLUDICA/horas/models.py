from django.db import models
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from io import BytesIO
from django.core.validators import RegexValidator

TIPOS_DOCUMENTO = [
    ('CC', 'Cédula de Ciudadanía'),
    ('TI', 'Tarjeta de Identidad'),
    ('CE', 'Cédula de Extranjería'),
    ('PA', 'Pasaporte'),
]

# Create your models here.

class HorasLudicas(models.Model):
    descripcion = models.CharField(max_length=255)
    horas = models.PositiveIntegerField()
    fecha = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="horas_ludicas")

    def __str__(self):
        return self.descripcion



# Nuevo modelo para almacenar datos adicionales del usuario
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    document_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=20)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"

# Señal para crear o actualizar el perfil automáticamente
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
        
        
        
        
class Actividad(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def generar_qr(self):
        """Genera el código QR con un enlace al formulario de registro de horas lúdicas"""
        url = f"http://127.0.0.1:8000/registro_qr/{self.id}/"  # Ajusta la URL según tu dominio
        qr = qrcode.make(url)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        self.qr_code.save(f"qr_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        """Sobreescribe el método save para generar el código QR al guardar la actividad"""
        if not self.qr_code:  # Solo genera el QR si no existe
            self.generar_qr()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre
    
class RegistroAsistencia(models.Model):
    nombres_completos = models.CharField(max_length=150)
    correo = models.EmailField()
    tipo_documento = models.CharField(max_length=2, choices=TIPOS_DOCUMENTO)
    numero_identificacion = models.CharField(
        max_length=20,
        validators=[RegexValidator(regex='^\d+$', message='Solo se permiten números.')]
    )
    actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombres_completos} - {self.actividad.nombre}"
