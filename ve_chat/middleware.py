from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model()  # Obtiene el modelo de usuario personalizado (usuarios.Usuario)


class FakeAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Solo para desarrollo, simula un usuario autenticado
        if not request.user.is_authenticated:
            # Obtén o crea un usuario de prueba usando el modelo correcto
            fake_user, created = User.objects.get_or_create(
                email="dev_user@example.com",
                defaults={"first_name": "Dev", "last_name": "User"},
            )
            request.user = fake_user
