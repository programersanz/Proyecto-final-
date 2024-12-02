from django.contrib import admin
from .models import HorasLudicas

admin.site.register(HorasLudicas)

# Register your models here.

class HorasLudicasAdmin(admin.ModelAdmin):
    list_display = ('actividad', 'aprendiz', 'fecha', 'horas_otorgadas', 'registro_por')
    search_fields = ('actividad', 'aprendiz__username', 'registrado_por__username')
    list_filter = ('fecha', 'horas_otorgadas')