from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import HorasLudicas
from django.contrib.auth.models import User
from .forms import HorasLudicasForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import RegistroForm
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator

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

from .forms import CustomUserCreationForm

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Marcar el usuario como inactivo hasta confirmar el email
            user.is_active = True
            user.save()
            # Los datos extras se guardan en el método save() del formulario
            # Enviar email de activación
            current_site = get_current_site(request)
            subject = "Activa tu cuenta en LEYLUDICA"
            message = render_to_string("registration/activation_email.html", {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": default_token_generator.make_token(user),
            })
            user.email_user(subject, message)
            return HttpResponse("Por favor, revisa tu correo electrónico para activar tu cuenta.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/register.html", {"form": form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return HttpResponse("El enlace de activación no es válido.")

def home(request):
    return render(request, "home.html")