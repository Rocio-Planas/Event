# usuarios/tokens.py
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.crypto import constant_time_compare
from django.utils.http import base36_to_int
import six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    """Generador de tokens para activación de cuenta"""
    
    def _make_hash_value(self, user, timestamp):
        # Incluye email, timestamp y is_active para invalidar si se activa
        return (
            six.text_type(user.pk) + 
            six.text_type(timestamp) + 
            six.text_type(user.is_active)
        )
    
    def check_token(self, user, token):
        """Verifica que el token sea válido y el usuario no esté ya activo"""
        if not super().check_token(user, token):
            return False
        # Si el usuario ya está activo, el token no es válido
        if user.is_active:
            return False
        return True

# Instancias de los generadores
account_activation_token = AccountActivationTokenGenerator()
password_reset_token = PasswordResetTokenGenerator()