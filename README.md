# DWES-UT04-Practica-2025-2026

Este repositorio contiene la versión final y estable de una aplicación web desarrollada con Django para la gestión de tareas académicas, que permite diferenciar entre usuarios con rol de alumno y profesor, gestionar tareas individuales y grupales, realizar entregas y llevar a cabo la validación de tareas evaluables.

La rama main incluye el proyecto completamente funcional, con el modelo de datos definitivo y todas las funcionalidades implementadas y verificadas.

## Funcionalidades principales

- Creación de usuarios con rol alumno o profesor

- Creación de tareas:

    - individuales

    - grupales

    - evaluables o no evaluables

- Asignación de tareas a alumnos o grupos

- Creación automática de entregas asociadas a las tareas

- Realización de entregas por parte del alumnado

- Validación de entregas por parte del profesorado

- Validación de entregas por parte del alumnoado si no son tareas evaluables

- Visualización de tareas, entregas y estados según el rol del usuario

- Visualización de  datos personales de los usuarios

- Flujo completo funcional desde la interfaz sin necesidad de datos precargados

## Tecnologías utilizadas

- Python

- Django

- Base de datos PostgreSQL con DVeaber

- HTML 

- Git para control de versiones

## Puesta en marcha del proyecto

- Se clona el proyecto de la tarea 3

- Se crean las ramas de trabajo

- Una vez terminado y comprobada su funcionalidad se fusiona con la rama main

- Se conecta a la base de datos final

- Se ejecutan las migraciones

    - Se ejecuta el comando python manage.py migrate

## Inicialización de datos y datos de prueba

- La aplicación está diseñada para que todos los datos se creen desde la propia interfaz, por lo que no se utilizan fixtures ni datos precargados.

- Desde la página de inicio de la aplicación se puede:

    - Crear usuarios (alumnos y profesores) mediante el formulario de creación de usuario.

    - Crear tareas individuales y grupales mediante los formularios correspondientes.

    - Generar automáticamente las entregas asociadas a las tareas creadas.

Este enfoque permite comprobar el funcionamiento completo de la aplicación partiendo de una base de datos vacía, sin necesidad de introducir datos manualmente desde consola.

## Flujo de uso básico

- Crear un usuario profesor y uno o varios usuarios alumno desde la página de inicio.

- Visualizar los usuarios almacenados.

- Crear tareas (individuales o grupales) desde la interfaz.

- Acceder como alumno o profesor y ver los datos personales.

- Acceder como alumno para realizar las entregas y validar la entregas no evaluables.

- Acceder como profesor para validar las entregas evaluables.

- Consultar el estado de tareas y entregas según el rol del usuario.

