from django.shortcuts import render
from django.views.generic import DetailView
from .models import Tarea, Usuario



# Create your views here.

   #  class detalle_tarea(DetailView):
    #     model = Tarea
    #     template_name = "tareas/detalle_tarea.html"
    #     context_object_name = "tarea"

# Vista listar usuarios
def listar_usuarios(request):
    alumnos = Usuario.objects.filter(rol='alumno')
    profesores = Usuario.objects.filter(rol='profesor')

    return render(request, 'usuarios/listar_usuarios.html', {
        'alumnos': alumnos,
        'profesores': profesores
    })