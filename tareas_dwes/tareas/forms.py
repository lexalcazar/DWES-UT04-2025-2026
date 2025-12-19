from django import forms
from django.core.validators import RegexValidator
from tareas.models import TareaIndividual, Usuario

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
    

class CrearTareaIndividualForm(forms.ModelForm):
    # Campo extra que NO está en el modelo
    dni = forms.CharField(
        label='DNI del creador',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '12345678Z'
        })
    )
    
    class Meta:
        model = TareaIndividual

        fields = ['alumno_asignado', 'titulo', 'enunciado','fecha_entrega']
        
        # Excluir campos
        # exclude = ['activo']
        
        widgets = {
            'alumno_asignado': forms.Select(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Introduzca titulo'}),
            'enunciado':forms.Textarea(attrs={'class':'form-control'}),
            'fecha_entrega': forms.DateTimeInput(attrs={'type': 'datetime-local','class': 'form-control'})
        }
        
     
    
    # Validación personalizada
    def clean_dni(self):
        dni = (self.cleaned_data.get("dni") or "").strip().upper()
        if not dni:
            raise forms.ValidationError("Introduce el DNI del creador.")

        creador = Usuario.objects.filter(dni=dni).first()
        if not creador:
            raise forms.ValidationError("No existe un usuario con ese DNI.")
        return dni