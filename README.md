# DWES-UT04-Practica-2025-2026

## Listado de elementos a implementar

Vistas

- [X] Vista en la que un alumno/profesor pueda ver sus datos.
- [X] Vista con el listado de todo el alumnado/profesorado.
- [X] Vista en la que un alumno puede ver todas las tareas que ha creado o colabora.
- [X] Vista en la que un profesor puede ver todas las tareas que requieren su validación.


Formularios

- [X] Formulario para el alta del alumnado/profesorado.
- [X] Formulario de creación de una tarea individual (puede necesitar o no evaluación de un profesor)
- [X] Formulario de creación de una tarea grupal (puede necesitar o no evaluación de un profesor)


## Temporalización del repositorio

### 12/12/25 

Clonamos repositorio tarea 3 DWES, y lo añadomos al repositorio tema 4, para la práctica 4.

Creo esta rama para hacer pruebas gordas sin tener miedo de romper todo.

He probado ha crear los modelos y una vista en esta rama (Desarrollo), lo he hecho mal tenia mal planteado el ER.

Tengo que darle una vuelta, además creo la rama pruebas para hacer el bruto ahí.

### 14/12/25

Conectamos con base de datos y probamos el modelo usuario

Conseguimos hacer un modelo usuario

Conseguimos una pequeña lista y funciona

### 15/12/25

Vamos ha hacer unos cambios para pulir el modelo usuario

Hago un formulario, la vista, la url y la template

Me cargo la base de datos y la conexion en DBeaver, perfecto.

### 16/12/25

Darío arregla la conexión a postgre

Hago migraciones y conecto con la base de datos

Consigo hacer funcionar el formulario, guarda datos

Consigo traer de la base de datos la lista de usuarios

Pulo cosas del front, y añado página de inicio en /tareas

Merge con Desarrollo para tener en pruebas todo y seguir trabajando

### 17/12/25

Hago los modelos en la rama pruebas y empiezo la view de  buscar_dni

### 18/12/25

Acabo view buscar_dni, sigo con ver_tareas_por_dni

Migro los modelos a bd pruebas

Y vista funcionando tanto con alumno como con profesor para ver tareas asignadas o 
que necesitan validacion de u profesor

### 19/12/25

Vista para datos personales hecha

Hago formulario para crear tarea individual, falta si es evaluable tengo que añadir algo más

### 20/12/25

Cambio modelos de herencia a OneToOneField

Realizo formulario para tareas individual y grupal, evaluable o no

Todo funciona

Hago pequeños cambios en front

Elimino errores 404 y los cambio por mensajes

### 23/12/25

Ajusto formularios para que actualicen datos en tabla entregas

creo vista para ver las entregas y el estado en el que se encuentran

creo vista para realizar entrega y que actualice la bd 

falta aplicar las validaciones de tareas

falta en buscar tareas asignadas arreglar los mensajes que salen

### 24/12/25

validaciones aplicadas

se arregla los mensajes en buscar tareas asignadas

quitare del modelo final los comentarios en la entrega

hay que arreglar los mensajes que se quedan en la pagina y no se van al crear tareas, y revisar y hay mas fallos

