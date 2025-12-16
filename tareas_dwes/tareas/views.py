from django.shortcuts import redirect, render
from django.views.generic import ListView
from django.contrib import messages
from .forms import UsuarioForm
from .models import Usuario

def tareas_index(request):
    return render(request, "tareas/inicio.html")

class ListaUsuariosView(ListView):
    model = Usuario
    template_name = "tareas/listar_usuarios.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return (
            Usuario.objects
            .filter(rol__in=["alumno", "profesor"])
            .order_by("rol", "last_name", "first_name", "email")
        )


def crear_usuario(request):
     if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Guardar la contraseña de forma segura
            usuario.set_password(form.cleaned_data["password"])

            usuario.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("tareas_index")
     else:
        form = UsuarioForm()

     return render(request, "tareas/crear_usuario.html", {"form": form})
