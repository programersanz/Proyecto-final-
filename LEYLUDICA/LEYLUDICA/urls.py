"""
URL configuration for LEYLUDICA project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from horas import views
from django.contrib.auth import views as auth_views
from horas.views import home, register, activate, agregar_horas_bienestar, editar_perfil, dashboard_aprendiz, dashboard_bienestar, dashboard_administrativo, agregar_horas_bienestar, EditarHoraView, EliminarHoraView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', register, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('login/', auth_views.LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('editar_perfil/', editar_perfil, name='editar_perfil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('aprendiz/', views.vista_aprendiz, name='vista_aprendiz'),
    path('horas/', views.listar_horas, name='listar_horas'),
    path('ver_perfil/', views.ver_perfil, name='ver_perfil'),
    path('dashboard/aprendiz/', views.dashboard_aprendiz, name='dashboard_aprendiz'),
    path('dashboard/administrativo/', views.dashboard_administrativo, name='dashboard_admin'),
    path('dashboard/bienestar/agregar_horas/', agregar_horas_bienestar, name='agregar_horas_bienestar'),
    path('dashboard/bienestar/', views.dashboard_bienestar, name='dashboard_bienestar'),
    path('registrar_horas/', views.registrar_horas_ludicas, name='registrar_horas'),
    path('horas/editar/<int:pk>/', EditarHoraView.as_view(), name='editar_horas'),
    path('horas/eliminar/<int:pk>/', EliminarHoraView.as_view(), name='eliminar_horas'),

]
