from django.db import models
from django.contrib.auth.models import User

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