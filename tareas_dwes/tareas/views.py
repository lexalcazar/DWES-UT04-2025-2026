from gc import get_objects
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.contrib import messages
from .forms import  CrearTareaGrupalForm, CrearTareaIndividualForm, UsuarioForm
from .models import Tarea, Usuario

# vista para el index.html

def tareas_index(request):
    return render(request, "tareas/inicio.html")

# vista para listar a los usuarios de la aplicacion

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

# vista para crear un usuario

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

# Vista para buscar una tarea por DNI del creador o usuario asignado

def buscar_dni(request):
    if request.method == "POST":
        dni = (request.POST.get("dni") or "").strip().upper()

        usuario = Usuario.objects.filter(dni=dni).first()
        if not usuario:
            messages.error(request, "No existe ningún usuario con ese DNI.")
            return render(request, "tareas/buscar_por_dni.html", {"dni": dni})

        if usuario.rol == "alumno":
            return redirect("mis_tareas", dni=dni)
        return redirect("validaciones", dni=dni)

    return render(request, "tareas/buscar_por_dni.html")

# Vista tareas de un alumno creadas o asignadas

def ver_tareas_por_dni(request, dni):
    usuario = get_object_or_404(Usuario, dni=dni)
     
    tareas_individuales = Tarea.objects.filter(
            individual__alumno_asignado=usuario
        )

    tareas_grupales = Tarea.objects.filter(
            grupal__alumnos=usuario
        )

    tareas_creadas = Tarea.objects.filter(creado_por=usuario)

    return render(
        request,
        "tareas/mis_tareas.html",
        {
            "usuario": usuario,
            "tareas_individuales": tareas_individuales,
            "tareas_grupales": tareas_grupales,
            "tareas_creadas": tareas_creadas,
            
        }
    )


# Vista un profesor ve las tareas que requieren su validacion

def validacion_profesor(request, dni):

    profesor = get_object_or_404(Usuario, dni=dni)  
    validador=Tarea.objects.filter(evaluable__validada_por=profesor)

    return render(
        request,
        "tareas/validaciones.html",
        {
            "profesor": profesor,
            "tareas_para_validar": validador,
            
        }
    )
 
# Vista para buscar datos personales


def buscar_datos(request):
    if request.method == "POST":
        dni = (request.POST.get("dni") or "").strip().upper()

        usuario = Usuario.objects.filter(dni=dni).first()
        if not usuario:
            messages.error(request, "No existe ningún usuario con ese DNI.")
            return render(request, "tareas/buscar_datos_personales.html", {"dni": dni})

        return redirect("mis_datos", dni=dni)

    return render(request, "tareas/buscar_datos_personales.html")



# Vista datos personales

def mis_datos(request,dni):
    usuario = get_object_or_404(Usuario, dni=dni)
    return render(
        request,
        "tareas/mis_datos.html",
        {
            "usuario": usuario,
            
        }
    )


#Vista crear tarea Individual

def crear_tarea(request):
    form = CrearTareaIndividualForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea creada correctamente.")
        return redirect("tareas_index")

    return render(request, "tareas/crear_tarea.html", {"form": form})


# Vista crear tarea grupal

def crear_tarea_grupal(request):
    form = CrearTareaGrupalForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea creada correctamente.")
        return redirect("tareas_index")

    return render(request, "tareas/crear_tarea_grupal.html", {"form": form})
