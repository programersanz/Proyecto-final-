# horas/context_processors.py

def user_groups(request):
    if request.user.is_authenticated:
        return {
            "is_aprendiz": request.user.groups.filter(name="Aprendiz").exists(),
            "is_bienestar": request.user.groups.filter(name="Bienestar").exists(),
            "is_administrativo": request.user.groups.filter(name="Administrativo").exists(),
        }
    return {}
