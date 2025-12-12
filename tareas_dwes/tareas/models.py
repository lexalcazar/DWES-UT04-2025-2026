import uuid
from django.db import models

# Modelo Usuario
class Usuario(models.Model):
    ROL_CHOICES = (
        ('alumno', 'Alumno'),
        ('profesor', 'Profesor'),
    )
    id_usuario = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    dni = models.CharField(max_length=15, unique=True)
    nombre = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)

    def __str__(self):
        return f"{self.nombre} {self.apellidos} ({self.rol})"

# Modelo Tarea

class Tarea(models.Model):
    TIPO_CHOICES = (
        ('evaluable', 'Evaluable'),
        ('no_evaluable', 'No evaluable'),
    )

    MODALIDAD_CHOICES = (
        ('individual', 'Individual'),
        ('grupal', 'Grupal'),
    )
    id_tarea = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    modalidad = models.CharField(max_length=15, choices=MODALIDAD_CHOICES)
    fecha_limite = models.DateField()
    enunciado = models.TextField()

    creador = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='tareas_creadas'
    )

    def __str__(self):
        return self.nombre

# Modelo Entregas

class Entrega(models.Model):
    
    id_entrega = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)

    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('entregada', 'Entregada'),
        ('finalizada', 'Finalizada'),
        ('validada', 'Validada'),
        ('no_validada', 'No validada'),
    )

    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='entregas')
    alumno = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='entregas_realizadas')

    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')

    fecha_entrega_alumno = models.DateTimeField(null=True, blank=True)
    fecha_validacion = models.DateTimeField(null=True, blank=True)

    profesor_validador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='entregas_validadas'
    )

    comentarios_profesor = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ('tarea', 'alumno')

    def __str__(self):
        return f"{self.tarea} - {self.alumno}"
