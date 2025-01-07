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