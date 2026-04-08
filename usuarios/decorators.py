from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorador para restringir acceso a vistas según el rol del usuario.
    Uso: @role_required(['administrador', 'organizador'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in allowed_roles:
                raise PermissionDenied("No tienes permiso para acceder a esta página.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator