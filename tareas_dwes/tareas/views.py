from pyexpat.errors import messages
from urllib import request
from django.shortcuts import redirect, render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import UsuarioForm

from .models import Usuario
#from .models import Tarea, Usuario



# Create your views here.

   #  class detalle_tarea(DetailView):
    #     model = Tarea
    #     template_name = "tareas/detalle_tarea.html"
    #     context_object_name = "tarea"

# Vista listar usuarios
#    def listar_usuarios(request):
#        alumnos = Usuario.objects.filter(rol='alumno')
#        profesores = Usuario.objects.filter(rol='profesor')

#        return render(request, 'usuarios/listar_usuarios.html', {
#            'alumnos': alumnos,
#            'profesores': profesores
#        })


class ListaUsuariosView(ListView):
    model = Usuario
    template_name = "tareas/listar_usuarios.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        return Usuario.objects.filter(
            rol__in=["alumno", "profesor"]
        ).order_by("rol", "last_name", "first_name", "username")

# Pruebas
def crear_usuario(request):
    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)

            # Si tu Usuario usa email como USERNAME_FIELD y has quitado username,
            # y en tu modelo aún existe el campo "username" heredado (pero anulado),
            # no hace falta asignarlo.
            # Si tuvieras algún campo extra, lo pondrías aquí.

            usuario.save()
            messages.success(request, "Usuario creado correctamente.")
            return redirect("listar_usuarios")
    else:
        form = UsuarioForm()

    return render(request, "tareas/crear_usuario.html", {"form": form})