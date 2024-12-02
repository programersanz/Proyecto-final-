from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class HorasLudicas(models.Model):
    aprendiz = models.ForeignKey(User, on_delete=models.CASCADE, related_name='horas_ludicas')
    registrado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='horas_registradas')
    actividad = models.CharField(max_length=255)
    horas_otorgadas = models.PositiveBigIntegerField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.estudiante.username} - {self.actividad} ({self.horas} horas)"