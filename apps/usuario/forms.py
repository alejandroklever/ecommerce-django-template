from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UsuarioRegistroForm(UserCreationForm):
    class Meta:
        model = User

        fields = [
            'username',
            'email',
        ]
