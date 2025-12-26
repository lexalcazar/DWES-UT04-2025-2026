
from urllib import request
from django import forms
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from tareas.models import Entrega, Tarea, TareaEvaluable, TareaGrupal, TareaIndividual, Usuario

# ------------------------------------------------------------------------------------------------------------    
# ------------------------------------------------------------------------------------------------------------ 
# ------------------------------------------------------------------------------------------------------------ 

# Formulario crear usuario
# Formulario basado en ModelForm para la creación y edición de usuarios.
# Se encarga de:
# - Recoger los datos básicos del usuario
# - Aplicar validaciones personalizadas (DNI y email)
# - Gestionar la contraseña mediante un campo con input protegido


class UsuarioForm(forms.ModelForm):

    # =========================
    # CAMPOS PERSONALIZADOS
    # =========================

    # Campo DNI:
    # - Longitud máxima de 9 caracteres
    # - Validación mediante expresión regular:
    #   * 8 dígitos seguidos de una letra (formato DNI español)

    dni = forms.CharField(
        max_length=9,
        validators=[RegexValidator(r'^\d{8}[A-Za-z]$', 'El DNI debe tener 8 dígitos seguidos de una letra')]
    )

    # Campo contraseña:
    # - Se define explícitamente para poder usar PasswordInput
    # - El contenido no se muestra en claro en el formulario

    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'})
     )
    
    # =========================
    # CONFIGURACIÓN DEL MODELFORM
    # =========================

    class Meta:

        """
        Clase Meta que define:
        - El modelo asociado al formulario
        - Los campos que se mostrarán
        - Los widgets personalizados para mejorar la experiencia de usuario
        """
        # Modelo asociado

        model = Usuario

         # Campos que se incluirán en el formulario

        fields = ['first_name', 'last_name', 'email','password' ,'dni', 'rol']

        # Widgets personalizados para cada campo

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Alex'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Alcázar Cecilia'}),
            'email': forms.EmailInput(attrs={'placeholder': 'usuario@fpvirtualaragon.com'}),
            'dni': forms.TextInput(attrs={'placeholder': 'Introduzca DNI'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }

    # =========================
    # VALIDACIONES PERSONALIZADAS
    # =========================

    def clean_email(self):

        """
        Validación personalizada del email.
        - Comprueba que no exista otro usuario con el mismo email
        - Ignora el propio usuario cuando se está editando (instance.pk)
        """

        email = self.cleaned_data.get('email')
        if email:
            # Búsqueda de usuarios con el mismo email (sin distinguir mayúsculas)
            qs = Usuario.objects.filter(email__iexact=email)

            # Si el formulario está editando un usuario existente,
            # se excluye a sí mismo de la comprobación
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            # Si existe otro usuario con ese email, se lanza error
            if qs.exists():
                raise forms.ValidationError("Ya existe un usuario con este email.")
        return email
    
# ------------------------------------------------------------------------------------------------------------    
# ------------------------------------------------------------------------------------------------------------ 
# ------------------------------------------------------------------------------------------------------------ 
  
# Formulario para la creación de una tarea individual.
# Se encarga de:
# - Recoger los datos básicos de la tarea
# - Validar reglas de negocio (rol del creador, evaluabilidad)
# - Crear las instancias relacionadas (Tarea, TareaIndividual, Entrega, etc.)

class CrearTareaIndividualForm(forms.Form):
   # =========================
    # DATOS DEL CREADOR
    # =========================

    # DNI del usuario que crea la tarea.
    # Se valida posteriormente que exista en la base de datos.

   
    dni_creador = forms.CharField(
        label="DNI del creador",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "12345678Z"})
    )

    # =========================
    # DATOS DE LA TAREA
    # =========================

    # Título de la tarea

    titulo = forms.CharField(
        label="Título",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    # Enunciado o descripción detallada de la tarea

    enunciado = forms.CharField(
        label="Enunciado",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6})
    )

    # Fecha y hora límite de entrega de la tarea
    # Se usa datetime-local para facilitar la introducción desde el navegador

    fecha_entrega = forms.DateTimeField(
        label="Fecha de entrega",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"})
    )

    # =========================
    # DATOS ESPECÍFICOS DE TAREA INDIVIDUAL
    # =========================

    # Alumno al que se asigna la tarea.
    # Solo se muestran usuarios con rol "alumno".
    # No es obligatorio, ya que se valida posteriormente según la lógica de negocio.

    alumno_asignado = forms.ModelChoiceField(
        label="Alumno asignado",
        queryset=Usuario.objects.filter(rol="alumno").order_by("last_name", "first_name"),
        required=False,
        widget=forms.Select(attrs={"class": "form-control"})
    )

     # Indica si la tarea requiere validación por parte de un profesor

    evaluable = forms.BooleanField(
        label="¿Requiere validación de profesor?",
        required=False
    )
    # =========================
    # VALIDACIONES DE CAMPOS
    # =========================


    def clean_dni_creador(self):

        """
        Validación específica del DNI del creador.
        - Normaliza el DNI (mayúsculas y sin espacios)
        - Comprueba que exista un usuario con ese DNI
        """

        dni = (self.cleaned_data.get("dni_creador") or "").strip().upper()
        if not Usuario.objects.filter(dni=dni).exists():
            raise forms.ValidationError("No existe un usuario con ese DNI.")
        return dni
    
    def clean(self):

        """
        Validaciones generales del formulario.
        Se comprueban reglas de negocio que dependen de varios campos.

        """
        cleaned = super().clean()
        dni = (cleaned.get("dni_creador") or "").strip().upper()
        evaluable = cleaned.get("evaluable")

       # Si la tarea es evaluable, solo puede ser creada por un profesor
        if evaluable:
            creador = Usuario.objects.filter(dni=dni).first()
            if not creador or creador.rol != "profesor":
                self.add_error("evaluable", "Solo un profesor puede crear tareas evaluables.")
               
       

        return cleaned
    
    # =========================
    # PERSISTENCIA DE DATOS
    # =========================

    def save(self):
        """
        Método encargado de crear todas las entidades relacionadas
        con la tarea individual:
        - Tarea
        - TareaIndividual
        - TareaEvaluable (si procede)
        - Entrega (si hay alumno asignado)
        """
        # Recuperamos el usuario creador a partir del DNI validado

        creador = Usuario.objects.get(dni=self.cleaned_data["dni_creador"])
        # Creación de la tarea base
        tarea = Tarea.objects.create(
            titulo=self.cleaned_data["titulo"],
            enunciado=self.cleaned_data["enunciado"],
            fecha_entrega=self.cleaned_data["fecha_entrega"],  # fecha límite (en tu modelo actual)
            creado_por=creador,
        )
          # Alumno asignado a la tarea individual
        alumno = self.cleaned_data["alumno_asignado"]

       # Creación de la tarea individual

        TareaIndividual.objects.create(
            tarea=tarea,
            alumno_asignado=alumno
        )

        evaluable = self.cleaned_data.get("evaluable", False)

        # Si es evaluable, se crea en la tabla TareaEvaluable

        if evaluable:
            TareaEvaluable.objects.create(
                tarea=tarea,
                validada=False,
                validada_por=creador,
            )

    # Crear/actualizar entrega UNA sola vez (si hay alumno)
        if alumno:
            Entrega.objects.update_or_create(
                tarea=tarea,
                alumno=alumno,
                defaults={
                "estado": "pendiente",
                "fecha_entrega": tarea.fecha_entrega,               
                "profesor_validador": creador if evaluable else None,
                }
            )
     # Se devuelve la tarea creada para su uso posterior en la vista   
        return tarea

# ------------------------------------------------------------------------------------------------------------    
# ------------------------------------------------------------------------------------------------------------ 
# ------------------------------------------------------------------------------------------------------------ 


# Formulario para la creación de una tarea grupal.
# Se encarga de:
   #  - Recoger datos básicos de la tarea (título, enunciado, fecha límite)
   #  - Seleccionar múltiples alumnos participantes
   #  - Aplicar regla de negocio: si es evaluable, solo puede crearla un profesor
   #  - Guardar las entidades relacionadas (Tarea, TareaGrupal, TareaEvaluable, Entrega)
  

class CrearTareaGrupalForm(forms.Form):

    # =========================
    # DATOS DEL CREADOR
    # =========================

    # DNI del usuario que crea la tarea.
    # Se valida y se guarda el objeto creador en self._creador para reutilizarlo en save().

    dni_creador = forms.CharField(
        label="DNI del creador",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "12345678Z"}
        )
    )

    # =========================
    # DATOS BÁSICOS DE LA TAREA
    # =========================

    # Título de la tarea

    titulo = forms.CharField(
        label="Título",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    # Enunciado detallado de la tarea
    enunciado = forms.CharField(
        label="Enunciado",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 6})
    )

    # Fecha y hora límite para entregar la tarea.
    # Se usa el input HTML datetime-local para facilitar el formato desde el navegador.
    fecha_entrega = forms.DateTimeField(
        label="Fecha de entrega",
        input_formats=["%Y-%m-%dT%H:%M"],
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local", "class": "form-control"}
        )
    )

    # =========================
    # DATOS ESPECÍFICOS DE TAREA GRUPAL
    # =========================

    # Selección múltiple de alumnos.
    # - Filtra usuarios con rol "alumno"
    # - required=True porque una tarea grupal debe tener participantes
    # - SelectMultiple permite escoger varios elementos en el formulario
   
    alumnos = forms.ModelMultipleChoiceField(
        label="Alumnos",
        queryset=Usuario.objects.filter(rol="alumno").order_by("last_name", "first_name"),
        required=True,
        widget=forms.SelectMultiple(attrs={"class": "form-control"})
    )
    # Checkbox que indica si la tarea requiere validación de un profesor
    evaluable = forms.BooleanField(
        label="¿Requiere validación de profesor?",
        required=False
    )

    # =========================
    # VALIDACIONES
    # =========================

    def clean_dni_creador(self):

        """
        Validación específica del DNI del creador:
        - Normaliza el DNI (quita espacios y pone mayúsculas)
        - Comprueba que exista el usuario
        - Guarda el objeto Usuario en self._creador para poder usarlo luego en clean() y save()
        """

        dni = (self.cleaned_data.get("dni_creador") or "").strip().upper()
        try:
            self._creador = Usuario.objects.get(dni=dni)
        except Usuario.DoesNotExist:
            raise forms.ValidationError("No existe un usuario con ese DNI.")
        return dni

    def clean(self):

        # Validación general del formulario

        cleaned = super().clean()
        evaluable = cleaned.get("evaluable", False)

        # Si es evaluable, el creador debe ser profesor
        if evaluable and self._creador.rol != "profesor":
            self.add_error(
                "evaluable",
                "Solo un profesor puede crear tareas evaluables."
            )

        return cleaned

    # =========================
    # GUARDADO (PERSISTENCIA)
    # =========================

    def save(self):
        """
        Crea todas las entidades relacionadas con la tarea grupal:
        1) Crea Tarea (entidad base)
        2) Crea TareaGrupal y asigna alumnos con .set()
        3) Si es evaluable, crea TareaEvaluable
        4) Crea una Entrega pendiente para cada alumno seleccionado
        """
        creador = self._creador
        # Crear la tarea base
        tarea = Tarea.objects.create(
            titulo=self.cleaned_data["titulo"],
            enunciado=self.cleaned_data["enunciado"],
            fecha_entrega=self.cleaned_data["fecha_entrega"],  # fecha límite
            creado_por=creador,
        )

        # Crear la tarea grupal 
        tg = TareaGrupal.objects.create(tarea=tarea)

        # Recuperamos los alumnos seleccionados en el formulario
        alumnos = self.cleaned_data["alumnos"]

        # Asignamos los alumnos a la relación ManyToMany de la tarea grupal
        tg.alumnos.set(alumnos)

        evaluable = self.cleaned_data.get("evaluable", False)

       # Si es evaluable, tarea pendiente de validar
        if evaluable:
            TareaEvaluable.objects.create(
                tarea=tarea,
                validada=False,
                validada_por=creador,
            )

        # Crear entregas pendientes para cada alumno del grupo
        # (cada alumno tendrá su propia entrega asociada a la misma tarea)
        for alumno in alumnos:
            Entrega.objects.get_or_create(
                tarea=tarea,
                alumno=alumno,
                fecha_entrega= tarea.fecha_entrega, 
                defaults={
                    "estado": "pendiente",
                    "profesor_validador": creador if evaluable else None,
                }
            )
        # Devuelve la tarea creada para usarla en la vista 
        return tarea



