from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin

User = get_user_model() 


class FakeAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not request.user.is_authenticated:
            fake_user, created = User.objects.get_or_create(
                email="dev_user@example.com",
                defaults={"first_name": "Dev", "last_name": "User"},
            )
            request.user = fake_user
