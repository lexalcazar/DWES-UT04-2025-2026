from datetime import timezone
from gc import get_objects
from django.forms import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.contrib import messages
from .forms import  CrearTareaGrupalForm, CrearTareaIndividualForm, UsuarioForm
from .models import Entrega, Tarea, TareaEvaluable, Usuario
from django.utils import timezone

# vista para el index.html
# Vista de la pagina de bienvenida.

def tareas_index(request):
    return render(request, "tareas/inicio.html")

# Vista para listar a los usuarios de la aplicacion
# Lista los usuarios que hay almacenados en la bd

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

# Vista para crear un usuario
# Esta vista esta relacionada con el formulario para crear un usuario

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

# Vista para buscar por DNI una tarea asignada 
# Con esta vista buscamos al usuario por el dni introducido y nos lleva a las tareas
# que tiene asignadas y tambien se visualizan las tareas creadas por el usuario

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
# Esta vista busca con el dni las tareas que tiene asignadas un usuario y las muestra
# tambien muestra las tareas creadas por el usuario

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
            "dni": dni,
            "tareas_individuales": tareas_individuales,
            "tareas_grupales": tareas_grupales,
            "tareas_creadas": tareas_creadas,
            
          
        }
    )


# Vista un profesor ve las tareas que requieren su validacion

def validacion_profesor(request, dni):

    profesor = get_object_or_404(Usuario, dni=dni)  
    validador=Tarea.objects.filter(evaluable__validada_por=profesor)
    entregas_para_validar = Entrega.objects.filter(
    estado="entregada"
    ).select_related("tarea", "alumno").order_by("tarea__fecha_entrega")


    return render(
        request,
        "tareas/validaciones.html",
        {
            "profesor": profesor,
            "tareas_para_validar": validador,
            "dni": dni,
            "entregas_para_validar": entregas_para_validar,
            
        }
    )
 
# Vista para buscar datos personales
# Con esta vista buscamos el usuario a traves del dni 

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
# Esta vista muestra los datos de un usuario

def mis_datos(request,dni):
    usuario = get_object_or_404(Usuario, dni=dni)
    return render(
        request,
        "tareas/mis_datos.html",
        {
            "usuario": usuario,
            
        }
    )


# Vista crear tarea Individual
# Esa vista esta relacionada con el formulario de crear una tarea individual
# en el se puede seleccionar que sea evaluable
# si lo es tendrá que ser creada por un profesor
# ademas inserta datos en entrega.

def crear_tarea(request):
    form = CrearTareaIndividualForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea creada correctamente.")
        return redirect("tareas_index")
    else:
        messages.success(request, "No se creo la tarea.")
        messages.success(request, "Revise si todos los campos son correctos.")
    return render(request, "tareas/crear_tarea.html", {"form": form})


# Vista crear tarea grupal
# Esa vista esta relacionada con el formulario de crear una tarea grupal
# en el se puede seleccionar que sea evaluable
# si lo es tendra que ser creada por un profesor
# ademas inserta datos en entrega.

def crear_tarea_grupal(request):
    form = CrearTareaGrupalForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Tarea creada correctamente.")
        return redirect("tareas_index")
        
    else:
        messages.success(request, "No se creo la tarea.")
        messages.success(request, "Revise si todos los campos son correctos.")

    return render(request, "tareas/crear_tarea_grupal.html", {"form": form})

# Vista entregar tarea
# Con esta vista podemos realizar la entrega de las tareas que estan pendientes
# si la fecha de entrega almacenada es anterior a la actual nos dara error

def entregar_tarea(request,dni,tarea_id):
    datos= get_object_or_404(Usuario, dni=dni)
    #tarea= Tarea.objects.filter(evaluable__tarea=tarea_id)
    entrega = get_object_or_404(
        Entrega,
        tarea_id=tarea_id,
        alumno_id=datos,
    )

    
    limite = entrega.tarea.fecha_entrega
    if limite and timezone.now() > limite:
        messages.error(request, "La fecha de entrega ha expirado.")
        return redirect("ver_entregas", dni=dni)
    entrega.estado = "entregada"
    entrega.fecha_entrega = timezone.now()  
    entrega.save()

   # messages.success(request, "Tarea marcada como entregada.") esto lo tengo que quitar
    return redirect("ver_entregas", dni=dni)
    
   

# Vista ver entregas 
# En esta vista vemos las entregas que tiene  cada usuario 


def ver_entregas(request, dni):
    usuario = get_object_or_404(Usuario, dni=dni)
    
    entregas = Entrega.objects.filter(
        alumno=usuario
    ).select_related("tarea").order_by("-fecha_entrega")
   
    return render(
        request,
        "tareas/entregas.html",
        {
            "usuario": usuario,
            "entregas": entregas,
            "dni": dni,
            
        }
    )

# vista para validar una tarea
# esta vista se utiliza tanto para que valide una tarea tanto un profesor como un alumno
# para que la pueda validar un alumno tiene que ser una tarea no evaluable
# las tareas evaluables solo las valida un profesor

def validar(request, dni, tarea_id, alumno_id=None):
    usuario = get_object_or_404(Usuario, dni=dni)

    # Si la tarea es evaluable y requiere profesor
    evaluable = TareaEvaluable.objects.filter(tarea_id=tarea_id, requiere_validacion_profesor=True).exists()

    # --- ALUMNO ---
    if usuario.rol == "alumno":
        # solo puede validar NO evaluables
        if evaluable:
            messages.error(request, "Tarea evaluable: requiere validación de un profesor.")
            return redirect("ver_entregas", dni=dni)

        entrega = get_object_or_404(Entrega, tarea_id=tarea_id, alumno=usuario)
        entrega.estado = "validada"
        entrega.fecha_validacion = timezone.now()
        entrega.save()

      

        messages.success(request, "Tarea marcada como validada (no evaluable).")
        return redirect("ver_entregas", dni=dni)

    # --- PROFESOR ---
    if usuario.rol == "profesor":
        if alumno_id is None:
            messages.error(request, "Falta el alumno de la entrega a validar.")
            return redirect("validaciones", dni=dni)

        entrega = get_object_or_404(Entrega, tarea_id=tarea_id, alumno_id=alumno_id)
        entrega.estado = "validada"
        entrega.profesor_validador = usuario
        entrega.fecha_validacion = timezone.now()
        entrega.save()

        if entrega.estado=="validada":
            evaluable=get_object_or_404(TareaEvaluable, tarea_id=tarea_id, validada_por=usuario)
            evaluable.validada= True
            evaluable.save()

        messages.success(request, "Entrega validada por profesor.")
        return redirect("validaciones", dni=dni)