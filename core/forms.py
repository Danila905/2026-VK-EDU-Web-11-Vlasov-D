from pathlib import Path

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import IntegrityError, transaction

from .models import Profile


User = get_user_model()


class AvatarField(forms.ImageField):
    def __init__(self):
        super().__init__(
            label='Аватар',
            required=False,
            help_text='JPG или PNG, до 2 МБ.',
            widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png'}),
        )

    def to_python(self, data):
        if data and data.size > 2 * 1024 * 1024:
            raise forms.ValidationError('Размер аватара должен быть не больше 2 МБ.')

        image = super().to_python(data)
        if image:
            formats = {'.jpg': 'JPEG', '.jpeg': 'JPEG', '.png': 'PNG'}
            extension = Path(image.name).suffix.lower()
            if formats.get(extension) != image.image.format:
                raise forms.ValidationError('Выберите изображение JPG или PNG с верным расширением.')
        return image


class LoginForm(AuthenticationForm):
    remember = forms.BooleanField(label='Запомнить меня', required=False)


class SignupForm(UserCreationForm):
    first_name = forms.CharField(label='Имя', max_length=150)
    email = forms.EmailField(label='Email', max_length=254)
    avatar = AvatarField()

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'password1', 'password2', 'avatar')

    def save(self):
        try:
            with transaction.atomic():
                user = super().save()
                Profile.objects.create(user=user, avatar=self.cleaned_data['avatar'])
                return user
        except IntegrityError:
            if User.objects.filter(username=self.cleaned_data['username']).exists():
                self.add_error('username', 'Этот логин уже занят.')
                return None
            raise


class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label='Никнейм', max_length=150)
    email = forms.EmailField(label='Email', max_length=254)
    avatar = AvatarField()

    class Meta:
        model = User
        fields = ('first_name', 'email', 'avatar')

    @transaction.atomic
    def save(self):
        user = self.instance
        user.save(update_fields=['first_name', 'email'])
        profile, _ = Profile.objects.get_or_create(user=user)
        if self.cleaned_data['avatar']:
            profile.avatar = self.cleaned_data['avatar']
            profile.save(update_fields=['avatar'])
        return user
