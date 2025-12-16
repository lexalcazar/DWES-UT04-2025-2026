import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

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

