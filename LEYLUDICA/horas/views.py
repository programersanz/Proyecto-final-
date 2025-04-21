from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from .models import HorasLudicas, Actividad, RegistroAsistencia, Profile
from django.contrib.auth.models import User, Group
from .forms import HorasLudicasForm, RegistroForm, CustomUserCreationForm, HorasLudicasBienestarForm, EditUserForm, EditProfileForm, EliminarHorasForm, RegistroAsistenciaForm, PasswordConfirmationForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import Group
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Sum, Count
# Create your views here.

def es_aprendiz(user):
    return user.groups.filter(name='Aprendiz').exists()

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

@login_required
def agregar_horas_bienestar(request):
    # Verificar si el usuario está en el grupo "Bienestar"
    if not request.user.groups.filter(name="Bienestar").exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")

    if request.method == 'POST':
        form = HorasLudicasBienestarForm(request.POST)
        if form.is_valid():
            form.save()  # Guarda la nueva instancia de HorasLudicas
            return redirect('dashboard_bienestar')  # Redirige al dashboard de Bienestar
    else:
        form = HorasLudicasBienestarForm()

    return render(request, 'horas/agregar_horas_bienestar.html', {'form': form})

def dashboard(request):
    user = request.user
    if user.groups.filter(name="Aprendiz").exists():
        return redirect("dashboard_aprendiz")
    elif user.groups.filter(name="Bienestar").exists():
        return redirect("dashboard_bienestar")
    elif user.groups.filter(name="Administrativo").exists():
        return redirect("dashboard_administrativo")
    else:
        # Si no tiene ningún rol asignado, muestra un mensaje o redirige a home
        return render(request, "horas/dashboard_default.html", {"mensaje": "No tienes un rol asignado."})
    
@login_required
def dashboard_aprendiz(request):
    # Horas lúdicas del usuario
    horas_ludicas = HorasLudicas.objects.filter(usuario=request.user)
    total_horas = horas_ludicas.aggregate(total=Sum('horas'))['total'] or 0

    # Ranking de los 10 perfiles con más asistencias
    ranking_asistencias = (
        RegistroAsistencia.objects
        .filter(perfil__user__isnull=False)
        .values('perfil__user__first_name', 'perfil__user__last_name', 'perfil__user__id')
        .annotate(total_asistencias=Count('id'))
        .order_by('-total_asistencias')[:10]
    )

    # Verificamos si el usuario está en el top 3
    mensaje_ranking = None
    for posicion, item in enumerate(ranking_asistencias):
        if item['perfil__user__id'] == request.user.id:
            if posicion == 0:
                mensaje_ranking = "🏆 ¡FELICIDADES! ESTÁS EN EL PRIMER LUGAR DEL RANKING DE ASISTENCIAS"
            elif posicion == 1:
                mensaje_ranking = "🥈 ¡GENIAL! ESTÁS EN EL SEGUNDO LUGAR DEL RANKING"
            elif posicion == 2:
                mensaje_ranking = "🥉 ¡MUY BIEN! ESTÁS EN EL TERCER LUGAR DEL RANKING"
            break

    context = {
        "horas_ludicas": horas_ludicas,
        "total_horas": total_horas,
        "ranking_asistencias": ranking_asistencias,
        "mensaje_ranking": mensaje_ranking,
    }

    return render(request, "horas/dashboard_aprendiz.html", context)


@login_required
def dashboard_administrativo(request):
    # Por ejemplo, mostrar la lista de todos los usuarios.
    usuarios = User.objects.all()
    context = {"usuarios": usuarios}
    return render(request, "horas/dashboard_administrativo.html", context)


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

@login_required
def dashboard_bienestar(request):
    # Permitir búsqueda de aprendices por número de documento.
    query = request.GET.get("q", "")
    if query:
        # Se asume que tienes un modelo Profile relacionado al User con el campo document_number.
        aprendices = User.objects.filter(groups__name__iexact="Aprendiz", profile__document_number__icontains=query).distinct()
    else:
        aprendices = User.objects.filter(groups__name__iexact="Aprendiz").distinct()
    context = {
        "aprendices": aprendices,
        "query": query,
    }
    return render(request, "horas/dashboard_bienestar.html", context)

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Activamos la cuenta inmediatamente
            user.save()
            # Guardar datos extra en el perfil
            user.profile.document_number = form.cleaned_data["document_number"]
            user.profile.phone_number = form.cleaned_data["phone_number"]
            user.profile.save()
            
            # Asignar el grupo "Aprendiz"
            grupo_aprendiz, created = Group.objects.get_or_create(name="Aprendiz")
            user.groups.add(grupo_aprendiz)
            
            return redirect("home")
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

@login_required
def editar_perfil(request):
    user = request.user

    if request.method == "POST":
        user_form = EditUserForm(request.POST, instance=user)
        profile_form = EditProfileForm(request.POST, instance=user.profile)
        pass_form = PasswordConfirmationForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid() and pass_form.is_valid():
            pwd = pass_form.cleaned_data['current_password']
            if not user.check_password(pwd):
                pass_form.add_error('current_password', 'Contraseña incorrecta')
            else:
                user_form.save()
                profile_form.save()
                messages.success(request, "Perfil actualizado exitosamente.")
                return redirect("home")
    else:
        user_form = EditUserForm(instance=user)
        profile_form = EditProfileForm(instance=user.profile)
        pass_form = PasswordConfirmationForm()

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "pass_form": pass_form,
    }
    return render(request, "horas/editar_perfil.html", context)

class EditarHoraView(LoginRequiredMixin, UpdateView):
    model = HorasLudicas
    form_class = HorasLudicasForm
    template_name = "horas/editar_horas.html"
    success_url = reverse_lazy("dashboard_aprendiz")
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        # Si el usuario está en el grupo "Bienestar", puede editar cualquier registro
        if user.groups.filter(name="Bienestar").exists():
            return qs
        # De lo contrario, el usuario solo puede editar sus propios registros
        return qs.filter(usuario=user)

class EliminarHoraView(LoginRequiredMixin, DeleteView):
    model = HorasLudicas
    template_name = "horas/eliminar_horas.html"
    success_url = reverse_lazy("dashboard_aprendiz")
    
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.groups.filter(name="Bienestar").exists():
            return qs
        return qs.filter(usuario=user)
    
@login_required
def ver_perfil(request):
    # Se asume que el usuario tiene un Profile creado mediante la señal.
    return render(request, "horas/ver_perfil.html", {"user": request.user})

@login_required
def detalle_aprendiz(request, user_id):
    # Solo el rol "Bienestar" puede ver detalles de aprendices
    if not request.user.groups.filter(name="Bienestar").exists():
        return HttpResponseForbidden("No tienes permiso para acceder a esta vista.")
    
    try:
        aprendiz = User.objects.get(id=user_id, groups__name__iexact="Aprendiz")
    except User.DoesNotExist:
        return HttpResponse("Aprendiz no encontrado", status=404)
    
    # Se asume que en el modelo HorasLudicas usaste related_name="horas_ludicas" en el FK a User
    horas = aprendiz.horas_ludicas.all()
    total_horas = sum(h.horas for h in horas)
    
    context = {
        "aprendiz": aprendiz,
        "horas": horas,
        "total_horas": total_horas,
    }
    return render(request, "horas/detalle_aprendiz.html", context)

@login_required
def eliminar_horas_parcial(request, pk):
    # Solo los usuarios con rol "Bienestar" pueden eliminar horas.
    if not request.user.groups.filter(name="Bienestar").exists():
        return HttpResponseForbidden("No tienes permiso para eliminar horas.")

    try:
        registro = HorasLudicas.objects.get(pk=pk)
    except HorasLudicas.DoesNotExist:
        return HttpResponse("Registro no encontrado.", status=404)
    
    if request.method == "POST":
        form = EliminarHorasForm(request.POST)
        if form.is_valid():
            horas_a_eliminar = form.cleaned_data["horas_a_eliminar"]
            # Si se quiere eliminar igual o más horas de las registradas, elimina el registro
            if horas_a_eliminar >= registro.horas:
                registro.delete()
            else:
                registro.horas -= horas_a_eliminar
                registro.save()
            # Redirige al detalle del aprendiz, usando el id del usuario asociado al registro
            return redirect("detalle_aprendiz", user_id=registro.usuario.id)
    else:
        form = EliminarHorasForm()
    
    context = {
        "registro": registro,
        "form": form,
    }
    return render(request, "horas/eliminar_horas_parcial.html", context)

def listar_actividades(request):
    actividades = Actividad.objects.all()
    return render(request, "horas/listar_actividades.html", {"actividades": actividades})

def detalle_actividad(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)
    return render(request, "horas/detalle_actividad.html", {"actividad": actividad})

def registrar_horas_qr(request, actividad_id):
    actividad = get_object_or_404(Actividad, id=actividad_id)

    if request.method == "POST":
        nombres = request.POST.get("nombres_completos")
        correo = request.POST.get("correo")
        tipo_documento = request.POST.get("tipo_documento")
        identificacion = request.POST.get("numero_identificacion")

        if nombres and correo and identificacion and tipo_documento:
            aprendiz_obj = aprendiz.objects.filter(numero_identificacion=identificacion).first()

            RegistroAsistencia.objects.create(
                aprendiz=aprendiz_obj,
                nombres_completos=nombres,
                correo=correo,
                tipo_documento=tipo_documento,
                numero_identificacion=identificacion,
                actividad=actividad
            )

            messages.success(request, "Asistencia registrada correctamente.")
            return redirect("registro_exitoso")
        else:
            messages.error(request, "Todos los campos son obligatorios.")

    return render(request, "horas/registro_qr.html", {"actividad": actividad})

def registrar_asistencia(request):
    if request.method == 'POST':
        form = RegistroAsistenciaForm(request.POST)
        if form.is_valid():
            asistencia = form.save(commit=False)
            try:
                perfil = Profile.objects.get(document_number=asistencia.numero_identificacion)
                asistencia.perfil = perfil
                asistencia.save()

                # 🟢 Crear la entrada de HorasLudicas si hay un usuario asociado al perfil
                if perfil.user:
                    HorasLudicas.objects.create(
                        descripcion=f"Asistencia a {asistencia.actividad.nombre}",
                        horas=asistencia.actividad.valor_horas,
                        fecha=timezone.now().date(),
                        usuario=perfil.user
                    )

                messages.success(request, "Asistencia registrada exitosamente.")
                return redirect('registro_exitoso')

            except Profile.DoesNotExist:
                # ❌ No guardar asistencia si no hay perfil
                messages.error(request, "El número de documento no está asociado a ningún perfil.")
                return redirect('registro_asistencia')  # o podrías quedarte en la misma página
    else:
        form = RegistroAsistenciaForm()
    return render(request, 'registro_asistencia.html', {'form': form})

def registro_exitoso(request):
    return render(request, 'registro_exitoso.html')

@login_required
def ranking_aprendices(request):
    ranking_raw = (
        Profile.objects
        .filter(user__isnull=False)
        .annotate(total_asistencias=Count('registroasistencia'))
        .order_by('-total_asistencias')[:10]
    )

    ranking = []
    for i, perfil in enumerate(ranking_raw):
        mensaje = ""
        if i == 0:
            mensaje = "🎉 ¡FELICIDADES! ESTÁS EN EL PRIMER LUGAR"
        elif i == 1:
            mensaje = "🥈 ¡Muy bien! Estás en el segundo lugar"
        elif i == 2:
            mensaje = "🥉 ¡Buen trabajo! Tercer lugar del ranking"

        ranking.append({
            'perfil': perfil,
            'total_asistencias': perfil.total_asistencias,
            'mensaje': mensaje
        })

    return render(request, 'horas/ranking_aprendices.html', {'ranking': ranking})
