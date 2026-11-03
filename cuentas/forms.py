from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import Group, User

from zonaocio.formularios import FormularioBootstrap

from .roles import ROLES


class LoginForm(FormularioBootstrap, AuthenticationForm):
    """Formulario de inicio de sesión (usuario y contraseña) con estilos Bootstrap."""


class PerfilMixin(forms.Form):
    """Campo para asignar el perfil (grupo) del usuario y validación de correo único."""

    perfil = forms.ModelChoiceField(
        queryset=Group.objects.filter(name__in=ROLES).order_by("name"),
        label="Perfil", help_text="Define los permisos del usuario en el sistema.",
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        repetidos = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            repetidos = repetidos.exclude(pk=self.instance.pk)
        if repetidos.exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo electrónico.")
        return email

    def save(self, commit=True):
        usuario = super().save(commit=commit)
        if commit:
            usuario.groups.set([self.cleaned_data["perfil"]])
        return usuario


class UsuarioCrearForm(FormularioBootstrap, PerfilMixin, UserCreationForm):
    email = forms.EmailField(
        label="Correo electrónico", help_text="Se usa para recuperar la contraseña."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username", "first_name", "last_name", "email"]


class UsuarioModificarForm(FormularioBootstrap, PerfilMixin, forms.ModelForm):
    email = forms.EmailField(
        label="Correo electrónico", help_text="Se usa para recuperar la contraseña."
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["is_active"].help_text = "Desmarca para bloquear el acceso sin eliminar al usuario."
        grupo = self.instance.groups.filter(name__in=ROLES).first()
        if grupo:
            self.initial["perfil"] = grupo.pk
