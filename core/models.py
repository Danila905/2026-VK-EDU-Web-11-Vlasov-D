from django.conf import settings
from django.db import models

# Create your models here.


class ProfileManager(models.Manager):
    def best_members(self):
        return self.select_related('user').annotate(
            question_count=models.Count('user__questions'),
        ).order_by('-question_count', 'pk')[:3]


class Profile(models.Model):
    objects = ProfileManager()

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.user.get_username()
