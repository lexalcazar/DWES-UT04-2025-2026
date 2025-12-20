from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from tareas.models import Tarea, TareaEvaluable, TareaGrupal, TareaIndividual, Usuario

#Formulario crear usuario

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
    
# Formulario tarea Individual

class CrearTareaIndividualForm(forms.Form):
   
    dni_creador = forms.CharField(
        label="DNI del creador",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "12345678Z"})
    )


    titulo = forms.CharField(
        label="Título",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    enunciado = forms.CharField(
        label="Enunciado",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6})
    )

    fecha_entrega = forms.DateTimeField(
        label="Fecha de entrega",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    # Individual
    alumno_asignado = forms.ModelChoiceField(
        label="Alumno asignado",
        queryset=Usuario.objects.filter(rol="alumno").order_by("last_name", "first_name"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

    evaluable = forms.BooleanField(
        label="¿Requiere validación de profesor?",
        required=False
    )

    def clean_dni_creador(self):
        dni = (self.cleaned_data.get("dni_creador") or "").strip().upper()
        if not Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("No existe un usuario con ese DNI.")
        return dni
    def clean(self):
        cleaned = super().clean()
        dni = (cleaned.get("dni_creador") or "").strip().upper()
        evaluable = cleaned.get("evaluable")

        # 1) Si es evaluable, solo profesor
        if evaluable:
            creador = Usuario.objects.filter(dni=dni).first()
            if not creador or creador.rol != "profesor":
                self.add_error("evaluable", "Solo un profesor puede crear tareas evaluables.")

       

        return cleaned

    def save(self):
        creador = get_object_or_404(Usuario, dni=self.cleaned_data["dni_creador"])

        tarea = Tarea.objects.create(
            titulo=self.cleaned_data["titulo"],
            enunciado=self.cleaned_data["enunciado"],
            fecha_entrega=self.cleaned_data["fecha_entrega"],
            creado_por=creador,
        )

       
        TareaIndividual.objects.create(
                tarea=tarea,
                alumno_asignado=self.cleaned_data["alumno_asignado"]
            )
      

        # Evaluable: asignar el profesor creador como validador
        if self.cleaned_data["evaluable"]:
            TareaEvaluable.objects.create(
                tarea=tarea,
                validada=False,
                validada_por=creador,   # aquí se le asigna “a él”
            )

        return tarea
    
# Formulario crear tarea grupal

class CrearTareaGrupalForm(forms.Form):


    dni_creador = forms.CharField(
        label="DNI del creador",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "12345678Z"})
    )
    titulo = forms.CharField(
        label="Título",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    enunciado = forms.CharField(
        label="Enunciado",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6})
    )

    fecha_entrega = forms.DateTimeField(
        label="Fecha de entrega",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

 # Grupal
    alumnos = forms.ModelMultipleChoiceField(
        label="Alumnos",
        queryset=Usuario.objects.filter(rol="alumno").order_by("last_name", "first_name"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-control"})
    )

    evaluable = forms.BooleanField(
        label="¿Requiere validación de profesor?",
        required=False
    )

    def clean_dni_creador(self):
        dni = (self.cleaned_data.get("dni_creador") or "").strip().upper()
        if not Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("No existe un usuario con ese DNI.")
        return dni
    def clean(self):
        cleaned = super().clean()
        dni = (cleaned.get("dni_creador") or "").strip().upper()
        evaluable = cleaned.get("evaluable")

        # 1) Si es evaluable, solo profesor
        if evaluable:
            creador = Usuario.objects.filter(dni=dni).first()
            if not creador or creador.rol != "profesor":
                self.add_error("evaluable", "Solo un profesor puede crear tareas evaluables.")

        return cleaned

    def save(self):
        creador = get_object_or_404(Usuario, dni=self.cleaned_data["dni_creador"])

        tarea = Tarea.objects.create(
            titulo=self.cleaned_data["titulo"],
            enunciado=self.cleaned_data["enunciado"],
            fecha_entrega=self.cleaned_data["fecha_entrega"],
            creado_por=creador,
        )

        #  grupal
     
        tg = TareaGrupal.objects.create(tarea=tarea)
        tg.alumnos.set(self.cleaned_data["alumnos"])

        # Evaluable: asignar el profesor creador como validador
        if self.cleaned_data["evaluable"]:
            TareaEvaluable.objects.create(
                tarea=tarea,
                validada=False,
                validada_por=creador,   # aquí se le asigna “a él”
            )

        return tarea



