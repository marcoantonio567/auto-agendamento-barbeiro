from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    cpf = models.CharField(max_length=11, blank=True, default='')
    phone = models.CharField(max_length=16, blank=True, default='')
    card_id = models.CharField(max_length=50, blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    theme_name = models.CharField(max_length=32, default='theme-green')

    class Meta:
        db_table = 'tb_usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.username
