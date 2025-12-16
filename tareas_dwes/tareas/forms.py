from django import forms
from django.core.validators import RegexValidator
from tareas.models import Usuario

class UsuarioForm(forms.ModelForm):
    dni = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{8}[A-Za-z]$', 'El DNI debe tener 8 dígitos seguidos de una letra')]
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
     )

    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email','password' ,'dni', 'rol']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Alex'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Alcázar Cecilia'}),
            'email': forms.EmailInput(attrs={'placeholder': 'usuario@fpvirtualaragon.com'}),
            'dni': forms.TextInput(attrs={'placeholder': 'Introduzca DNI'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            qs = Usuario.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un usuario con este email.")
        return email