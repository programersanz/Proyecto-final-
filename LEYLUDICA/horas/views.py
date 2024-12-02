from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import HorasLudicas

# Create your views here.

def es_aprendiz(user):
    return user.groups.filter(name='Aprendiz').exists()

def es_instructor(user):
    return user.groups.filter(name='Instructor').exists()

def vista_instructor(request):
    return render(request, 'horas/instructor.html')

def vista_aprendiz(request):
    return render(request, 'horas/aprendiz.html')



