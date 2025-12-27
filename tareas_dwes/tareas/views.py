
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView
from django.contrib import messages
from .forms import CrearTareaGrupalForm, CrearTareaIndividualForm, UsuarioForm
from .models import Entrega, Tarea, TareaEvaluable, Usuario
from django.utils import timezone
from django.contrib.auth import authenticate, login





# =========================
# VISTA PARA EL INDEX / INICIO
# =========================
# Renderiza la página principal.

def tareas_index(request):
   return render(request, "tareas/inicio.html")


# =========================
# LISTADO DE USUARIOS (CBV)
# =========================
# Muestra usuarios filtrando por rol.

class ListaUsuariosView(ListView):
    model = Usuario
    template_name = "tareas/listar_usuarios.html"
    context_object_name = "usuarios"

    def get_queryset(self):
        """
        Personaliza el queryset:
        - Solo alumnos y profesores
        - Ordena por rol, apellido, nombre y email
        """
        return (
            Usuario.objects
            .filter(rol__in=["alumno", "profesor"])
            .order_by("rol", "last_name", "first_name", "email")
        )


# =========================
# CREAR USUARIO
# =========================
# Crea un usuario usando UsuarioForm. Hashea password con set_password.

def crear_usuario(request):
     if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            # commit=False para poder modificar la instancia antes del guardado definitivo
            usuario = form.save(commit=False)

            # Hashea la contraseña (no se guarda en texto plano)
            usuario.set_password(form.cleaned_data["password"])

            # Guarda usuario ya con password hasheada
            usuario.save()

            messages.success(request, "Usuario creado correctamente.")
            return redirect("tareas_index")
     else:
        # GET: formulario vacío
        form = UsuarioForm()

     # Renderiza tanto el GET como el POST inválido
     return render(request, "tareas/crear_usuario.html", {"form": form})

#==========================
#Busqueda por dni
#=========================
def buscar_usuario(request):
    if request.method == "POST":
        dni = (request.POST.get("dni") or "").strip().upper()

        usuario = Usuario.objects.filter(dni=dni).first()
        if not usuario:
            messages.error(request, "No existe ningún usuario con ese DNI.")
            return render(request, "tareas/buscar_usuario.html", {"dni": dni})

        return redirect("usuario", dni=dni)

    return render(request, "tareas/buscar_usuario.html")


# =========================
# BUSCAR DNI (REDIRECCIONADOR)
# =========================
# Según rol, redirige a "mis_tareas" (alumno) o "validaciones" (profesor).

def filtrar_dni(request, dni):
    dni = (dni or "").strip().upper()

    usuario = Usuario.objects.filter(dni=dni).first()
    if not usuario:
        messages.error(request, "No existe ningún usuario con ese DNI.")
        return render(request, "tareas/buscar_usuario.html", {"dni": dni})

    # Redirección según rol
    if usuario.rol == "alumno":
        return redirect("mis_tareas", dni=dni)

    elif usuario.rol == "profesor":
        return redirect("validaciones", dni=dni)

    # Por seguridad (rol desconocido)
    messages.error(request, "Rol de usuario no reconocido.")
    return redirect("tareas_index")


# =========================
# VER TAREAS DE UN USUARIO
# =========================
# Muestra tareas:
# - individuales asignadas
# - grupales donde participa
# - creadas por el usuario

def ver_tareas_por_dni(request, dni):
    usuario = get_object_or_404(Usuario, dni=dni)

    # Tareas individuales donde el usuario es el alumno asignado
    tareas_individuales = Tarea.objects.filter(
            individual__alumno_asignado=usuario
        )

    # Tareas grupales donde el usuario participa en el grupo
    tareas_grupales = Tarea.objects.filter(
            grupal__alumnos=usuario
        )

    # Tareas creadas por el usuario (alumno o profesor)
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


# =========================
# VALIDACIONES (PROFESOR)
# =========================
# Profesor ve:
# - tareas evaluables asociadas a él
# - entregas en estado "entregada" para validar

def validacion_profesor(request, dni):
    profesor = get_object_or_404(Usuario, dni=dni)

    # Tareas evaluables cuyo "validada_por" coincide con este profesor (según tu lógica)
    validador = Tarea.objects.filter(evaluable__validada_por=profesor)

    # Entregas "entregada" pendientes de validar
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


# =========================
# BUSCAR DATOS PERSONALES POR DNI
# =========================

def buscar_datos(request):
    if request.method == "POST":
        dni = (request.POST.get("dni") or "").strip().upper()

        usuario = Usuario.objects.filter(dni=dni).first()
        if not usuario:
            messages.error(request, "No existe ningún usuario con ese DNI.")
            return render(request, "tareas/buscar_datos_personales.html", {"dni": dni})

        return redirect("mis_datos", dni=dni)

    return render(request, "tareas/buscar_datos_personales.html")


# =========================
# MOSTRAR DATOS PERSONALES
# =========================

def mis_datos(request, dni):
    usuario = get_object_or_404(Usuario, dni=dni)
    return render(
        request,
        "tareas/mis_datos.html",
        {
            "usuario": usuario,
        }
    )


# =========================
# CREAR TAREA INDIVIDUAL
# =========================


def crear_tarea(request):
    form = CrearTareaIndividualForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea creada correctamente.")
            return redirect("tareas_index")
        else:
            # Solo mostramos estos mensajes cuando el usuario HA ENVIADO el formulario y es inválido
            messages.error(request, "No se creó la tarea.")
            messages.error(request, "Revise si todos los campos son correctos.")

    # GET o POST inválido (muestra el form)
    return render(request, "tareas/crear_tarea.html", {"form": form})


# =========================
# CREAR TAREA GRUPAL
# =========================


def crear_tarea_grupal(request):
    form = CrearTareaGrupalForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Tarea creada correctamente.")
            return redirect("tareas_index")
        else:
            messages.error(request, "No se creó la tarea.")
            messages.error(request, "Revise si todos los campos son correctos.")

    return render(request, "tareas/crear_tarea_grupal.html", {"form": form})


# =========================
# ENTREGAR TAREA
# =========================


def entregar_tarea(request, dni, tarea_id):
    # Usuario alumno que entrega
    datos = get_object_or_404(Usuario, dni=dni)

    # Entrega asociada a (tarea, alumno)
    entrega = get_object_or_404(
        Entrega,
        tarea_id=tarea_id,
        alumno=datos,  
    )

    # Control de fecha límite
    limite = entrega.tarea.fecha_entrega
    if limite and timezone.now() > limite:
        messages.error(request, "La fecha de entrega ha expirado.")
        return redirect("ver_entregas", dni=dni)

    # Cambia estado a entregada y registra el momento de entrega
    entrega.estado = "entregada"
    entrega.fecha_entrega = timezone.now()
    entrega.save()

    return redirect("ver_entregas", dni=dni)


# =========================
# VER ENTREGAS (ALUMNO)
# =========================

def ver_entregas(request, dni):
    usuario = get_object_or_404(Usuario, dni=dni)

    entregas = Entrega.objects.filter(alumno=usuario).select_related(
        "tarea", "tarea__individual__alumno_asignado", "tarea__grupal"
    ).order_by("-fecha_entrega")

    return render(
        request,
        "tareas/entregas.html",
        {
            "usuario": usuario,
            "entregas": entregas,
            "dni": dni,
        }
    )


# =========================
# VALIDAR (ALUMNO / PROFESOR)
# =========================


def validar(request, dni, tarea_id, alumno_id=None):
    usuario = get_object_or_404(Usuario, dni=dni)

    # Comprueba si la tarea es evaluable (según tu campo/control actual)
    evaluable = TareaEvaluable.objects.filter(
        tarea_id=tarea_id,
        requiere_validacion_profesor=True
    ).exists()

    # --- ALUMNO ---
    if usuario.rol == "alumno":
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

        if entrega.estado == "validada":
            te = TareaEvaluable.objects.filter(tarea_id=tarea_id).first()
            if te:
                te.validada = True
                te.save()

        messages.success(request, "Entrega validada por profesor.")
        return redirect("validaciones", dni=dni)



    


# =========================
# Vista de inicio de usuario 
# =========================


def usuario(request, dni):
    dni = (dni or "").strip().upper()
    usuario_obj = Usuario.objects.filter(dni=dni).first()

    if not usuario_obj:
        messages.error(request, "No existe ningún usuario con ese DNI.")
        return redirect("buscar_usuario")  # o a tareas_index

    return render(request, "tareas/usuario.html", {"dni": dni, "usuario": usuario_obj})


