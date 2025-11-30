from django.shortcuts import render
from django.views.generic import DetailView
from .models import Tarea



# Create your views here.
class detalle_tarea(DetailView):
    model = Tarea
    template_name = "tareas/detalle_tarea.html"
    context_object_name = "tarea"
