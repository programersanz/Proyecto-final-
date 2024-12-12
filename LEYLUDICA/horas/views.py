from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
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

def es_admin(user):
    return user.groups.filter(name='Admin').exists()

def listar_horas(request):
    if request.user.groups.filter(name='Aprendiz').exists():
        horas = HorasLudicas.objects.filter(aprendiz=request.user)
    elif request.user.groups.filter(name='Instructor').exists():
        horas = HorasLudicas.objects.all()
    elif request.user.groups.filter(name='Admin').exists():
        horas = HorasLudicas.objects.all()
    else:
        horas = HorasLudicas.objects.none()

    return render(request, 'horas/listar_horas.html', {'horas': horas})

def agregar_horas(request):
    if request.method == 'POST':
        actividad = request.POST.get('actividad')
        fecha = request.POST.get('fecha')   
        horas_otorgadas = request.POST.get('horas_otorgadas')
        HorasLudicas.objects.create(
            aprendiz=request.user,
            actividad=actividad,
            fecha=fecha,
            horas_otorgadas=horas_otorgadas,
            registrado_por=request.user
        )
        return redirect('listar_horas')
    return render(request, 'horas/agregar_horas.html')

def dashboard(request):
    if request.user.groups.filter(name='Aprendiz').exists():
        return redirect('dashboard_aprendiz')
    elif request.user.groups.filter(name='Instructor').exists():
        return redirect('dashboard_instructor')
    elif request.user.groups.filter(name='Admin').exists():
        return redirect('dashboard_admin')
    else:
        return render(request, '403.html')
    
def dashboard_aprendiz(request):
    horas = request.user.horas_aprendiz.all()  
    return render(request, 'horas/dashboard_aprendiz.html', {'horas': horas})

@login_required
def dashboard_instructor(request):
    horas = HorasLudicas.objects.all()  
    return render(request, 'horas/dashboard_instructor.html', {'horas': horas})

@login_required
def dashboard_admin(request):
    horas = HorasLudicas.objects.all()  
    usuarios = User.objects.all()  
    return render(request, 'horas/dashboard_admin.html', {'horas': horas, 'usuarios': usuarios})

def dashboard_admin(request):
    horas = HorasLudicas.objects.all()
    usuarios = User.objects.all()
    return render(request, 'horas/dashboard_admin.html', {'horas': horas, 'usuarios': usuarios})