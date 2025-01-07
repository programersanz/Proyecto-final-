from django.apps import AppConfig
from django import forms
from .models import HorasLudicas


class HorasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'horas'

