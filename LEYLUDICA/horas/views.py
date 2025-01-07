from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import HorasLudicas
from django.contrib.auth.models import User
from .forms import HorasLudicasForm

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
    user = request.user

    if user.groups.filter(name='Aprendiz').exists():
        return redirect('dashboard_aprendiz')
    elif user.groups.filter(name='Instructor').exists():
        return redirect('dashboard_instructor')
    elif user.groups.filter(name='Admin').exists():
        return redirect('dashboard_admin')
    else:
        rol = "No tienes un rol asignado"
        context = {'rol': rol}
        return render(request, 'horas/ dashboard.html', context)
    
def dashboard_aprendiz(request):
    # Suponiendo que tienes un modelo llamado HorasLudicas relacionado con el usuario
    horas_ludicas = request.user.horasludicas_set.all()
    context = {
        'horas_ludicas': horas_ludicas,
    }
    return render(request, 'horas/dashboard_aprendiz.html', context)

@login_required
def dashboard_instructor(request):
    horas = HorasLudicas.objects.all()  
    return render(request, 'horas/dashboard_instructor.html', {'horas': horas})

@login_required
def dashboard_admin(request):
    usuarios = User.objects.all()  # Lista de todos los usuarios
    context = {'usuarios': usuarios}
    return render(request, 'horas/dashboard_admin.html', context)

@login_required
def registrar_horas_ludicas(request):
    if request.method == 'POST':
        form = HorasLudicasForm(request.POST)
        if form.is_valid():
            horas_ludicas = form.save(commit=False)
            horas_ludicas.usuario = request.user
            horas_ludicas.save()
            return redirect('dashboard_aprendiz')  # Cambia esto si tu URL tiene otro nombre
    else:
        form = HorasLudicasForm()
    return render(request, 'horas/registrar_horas.html', {'form': form})