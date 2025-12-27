import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

# Modelo Usuario
# Lo creamos a taves de AbstracUser, un modelo que tiene Django ya con ciertos campos.
# Nosotros anulamos el campo user name y añadimos los campos DNI, id_usuario, 
# rol, email.


class Usuario(AbstractUser):
    username = None

    ROLES = (
        ("alumno", "Alumno"),
        ("profesor", "Profesor"),
    )

    id_usuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dni = models.CharField(max_length=9, unique=True)
    rol = models.CharField(max_length=10, choices=ROLES, default="alumno")
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["dni"]  # para createsuperuser (y porque es único)

    def __str__(self):
        return f"{self.email} ({self.rol})"

# Modelo tarea
# 

class Tarea(models.Model):
    id_tarea = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_por = models.ForeignKey(Usuario,on_delete=models.CASCADE,related_name='tareas_creadas') # FK Usuario
    titulo = models.CharField(max_length=200)
    enunciado = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_entrega = models.DateTimeField()

    def __str__(self):
        return self.titulo
    
# Modelo Tarea Individual

class TareaIndividual(models.Model):
    tarea = models.OneToOneField(Tarea,on_delete=models.CASCADE,related_name='individual')
    alumno_asignado = models.ForeignKey(
        Usuario,
        on_delete = models.SET_NULL,
        null=True,
        blank=True,
        related_name = 'tareas_individuales',
        limit_choices_to = {'rol': 'alumno'}
    )

    def __str__(self):
        if self.alumno_asignado:
            return f"{self.titulo} - {self.alumno_asignado}"
        return self.titulo
    
# Modelo tarea Grupal

class TareaGrupal(models.Model):
    tarea = models.OneToOneField(Tarea,on_delete=models.CASCADE,related_name='grupal')
    alumnos = models.ManyToManyField(
        Usuario,
        related_name='tareas_grupales',
        limit_choices_to={'rol': 'alumno'}
    )

    def __str__(self):
        return f"{self.titulo} (Grupal)"


#Modelo Tarea Evaluable

class TareaEvaluable(models.Model):
   tarea = models.OneToOneField(Tarea,on_delete=models.CASCADE,related_name='evaluable')
   requiere_validacion_profesor = models.BooleanField(default=True)
   puntuacion_maxima = models.PositiveIntegerField(default=10)# este va fuera, deberia ir en tabla evaluacion
   validada = models.BooleanField(default=False) 
   validada_por = models.ForeignKey( #tendre que cambiar esto por validar_por
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tareas_validadas',
             limit_choices_to={'rol': 'profesor'}
    )
   

# Modelo Entrega

class Entrega(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('entregada', 'Entregada'),
        ('validada', 'Validada'),
        ('no_validada', 'No validada'),
    ]

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='entregas')
    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='entregas',
        limit_choices_to={'rol': 'alumno'}
    )

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_entrega = models.DateTimeField(null=True, blank=True)

    profesor_validador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entregas_validadas',
        limit_choices_to={'rol': 'profesor'}
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    comentarios_profesor = models.TextField(null=True, blank=True)# este hay que quitarlo en la bd final seria para una tabla de evaluacion

# Restricción para que solo haya una entrega por alumno
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['tarea', 'alumno'], name='entrega_unica_por_alumno')
        ]

    def __str__(self):
        return f'Entrega: {self.alumno} -> {self.tarea}'


