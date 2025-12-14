import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class Usuario(AbstractUser):
    ROLES = [
        ("alumno", "Alumno"),
        ("profesor", "Profesor"),
    ]
    id_usuario = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dni = models.CharField(max_length=9, unique=True)
    rol = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return f"{self.username} ({self.rol})"
