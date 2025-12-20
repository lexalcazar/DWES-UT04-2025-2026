from django import views
from django.urls import path
from . import views  
from .views import ListaUsuariosView
#from .views import listar_usuarios



urlpatterns = [
  #  path('<uuid:pk>/', detalle_tarea.as_view(), name='detalle_tarea'),
  #path('usuarios/', listar_usuarios, name='listar_usuarios'),
  path("", views.tareas_index, name="tareas_index"),
  path("usuarios/", views.ListaUsuariosView.as_view(), name="lista_usuarios"),
  path("usuarios/crear/", views.crear_usuario, name="crear_usuario"),
  path("mis-tareas/", views.buscar_dni, name="buscar_por_dni"),
  path("mis-tareas/<str:dni>/", views.ver_tareas_por_dni, name="mis_tareas"),
  path("validaciones/<str:dni>/", views.validacion_profesor, name="validaciones"),
  path("datos_personales/", views.buscar_datos, name="buscar_datos_personales"),
  path("datos_personales/<str:dni>/", views.mis_datos, name="mis_datos"),
  path("crear_tarea/", views.crear_tarea, name="crear_tarea"),
  path("crear_tarea_grupal/", views.crear_tarea_grupal, name="crear_tarea_grupal"),

]
