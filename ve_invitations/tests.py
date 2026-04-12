from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from virtualEvent.models import VirtualEvent
from ve_invitations.models import EventFollower
from ve_invitations.utils import send_invitation_email, send_material_notification
from unittest.mock import patch

User = get_user_model()


class InvitationTests(TestCase):
    def setUp(self):
        # Crear usuario con los campos que requiere tu modelo (solo email y password)
        self.user = User.objects.create_user(email="test@example.com", password="123")
        self.event = VirtualEvent.objects.create(
            title="Test Event",
            description="Test",
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            duration_minutes=60,
            created_by=self.user,
        )

    @patch("ve_invitations.utils.send_mail")
    def test_send_invitation_email(self, mock_send_mail):
        token = "abc123"
        send_invitation_email("test@example.com", self.event, token)
        mock_send_mail.assert_called_once()
        args, kwargs = mock_send_mail.call_args
        # subject es el primer argumento posicional
        self.assertIn("Invitación al evento privado", args[0])  # args[0] es el subject

    @patch("ve_invitations.utils.send_mail")
    def test_send_material_notification(self, mock_send_mail):
        EventFollower.objects.create(user=self.user, event=self.event)
        self.event.materials = {"recording": "https://youtu.be/abc"}
        self.event.save()
        send_material_notification(self.event)
        mock_send_mail.assert_called_once()
