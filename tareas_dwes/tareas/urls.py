from django import views
from django.urls import path
from . import views  
from .views import ListaUsuariosView
#from .views import listar_usuarios



urlpatterns = [

  path("", views.tareas_index, name="tareas_index"),
  path("usuarios/", views.ListaUsuariosView.as_view(), name="lista_usuarios"),
  path("usuarios/crear/", views.crear_usuario, name="crear_usuario"),
  path("buscar_usuario/", views.buscar_usuario, name="buscar_usuario"),
  path("filtrar/<str:dni>/", views.filtrar_dni, name="filtrar_dni"),
  path("mis-tareas/<str:dni>/", views.ver_tareas_por_dni, name="mis_tareas"),
  path("validaciones/<str:dni>/", views.validacion_profesor, name="validaciones"),
  path("datos_personales/<str:dni>/", views.mis_datos, name="mis_datos"),
  path("crear_tarea/", views.crear_tarea, name="crear_tarea"),
  path("crear_tarea_grupal/", views.crear_tarea_grupal, name="crear_tarea_grupal"),
  path("entregas/<str:dni>/",views.ver_entregas,name="ver_entregas"),
  path("entregas/<str:dni>/entregar/<uuid:tarea_id>/", views.entregar_tarea, name="entregar_tarea"),
  path("validar/<str:dni>/<uuid:tarea_id>/", views.validar, name="validar"),
  path("validar/<str:dni>/<uuid:tarea_id>/<uuid:alumno_id>/", views.validar, name="validar_profesor"),
  path("usuario/<str:dni>",views.usuario,name="usuario"),
  path("ver/", views.crear_tarea, name="crear_tarea"),
]
