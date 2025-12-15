from django import views
from django.urls import path
from . import views  
from .views import ListaUsuariosView
#from .views import listar_usuarios



urlpatterns = [
  #  path('<uuid:pk>/', detalle_tarea.as_view(), name='detalle_tarea'),
  #path('usuarios/', listar_usuarios, name='listar_usuarios'),
  path("", ListaUsuariosView.as_view(), name="lista_usuarios"),
  path("usuarios/nuevo/", views.crear_usuario, name="crear_usuario"),
]