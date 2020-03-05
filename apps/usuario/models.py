from django.db import models
from django.contrib.auth.models import User


class UserMetaData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    foto_de_perfil = models.ImageField()
    cuenta_bancaria = models.IntegerField()

    def __str__(self):
        return str(self.user.username)
