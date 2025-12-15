from django.shortcuts import render
from django.views.generic import DetailView
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
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
