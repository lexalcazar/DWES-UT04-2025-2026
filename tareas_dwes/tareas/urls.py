from django.urls import path
from .views import detalle_tarea



urlpatterns = [
    path('<uuid:pk>/', detalle_tarea.as_view(), name='detalle_tarea'),
]