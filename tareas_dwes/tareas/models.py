from django.db import models
import uuid

# Create your models here.
class Tareas(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    titulo=models.CharField(max_length=100)
    descripcion=models.TextField(blank=True, null=True)
    completada=models.BooleanField(default=False)
    fecha_creacion=models.DateTimeField(auto_now_add=True)
    fecha_recordatorio=models.DateTimeField(blank=True, null=True)    

    def __str__(self):
        return self.titulo