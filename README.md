# Feedy

Proyecto mobile-first para un comedero automático para mascotas, desarrollado con Flask y SQLite.

## Objetivo

Crear una interfaz visual y funcional para:

- configurar la porción de comida,
- guardar horarios de alimentación,
- visualizar y eliminar horarios,
- mantener la configuración persistida en base de datos local.

## Estructura del proyecto

```text
Feedy/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── routes.py
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   ├── trash.webp
│   │   │   └── kk.png
│   │   └── js/
│   │       └── app.js
│   └── templates/
│       └── index.html
├── tests/
│   └── test_feedy_db.py
├── run.py
├── feedy.db
├── requirements.txt
├── README.md
└── src/
```

## Tecnologías usadas

- Python 3
- Flask
- SQLite
- HTML + CSS + JavaScript
- Jinja2

## Funcionalidades implementadas

### Interfaz mobile-first

- diseño en tonos verdes inspirados en la referencia visual,
- estructura orientada a dispositivos móviles,
- botones principales para configuración y cámara,
- tarjeta de horarios con estilo adaptado al mockup.

### Persistencia de configuración

Se implementó una base de datos SQLite para guardar:

- la última porción configurada,
- los horarios cargados por el usuario.

La lógica se encuentra en:

- `app/database.py`
- `app/routes.py`

### Guardado de porción

La porción configurada se guarda en la tabla `settings` bajo la clave `last_portion_ms`.

Endpoints relevantes:

- `GET /api/portion`
- `POST /api/portion`
- `POST /api/portion/test`

### Horarios

Los horarios se guardan en la tabla `schedules` y se devuelven ordenados por hora.

Endpoints:

- `GET /api/schedules`
- `POST /api/schedules`
- `DELETE /api/schedules/<id>`

## Ajustes desarrollados

### Selector de hora en formato 24 horas

Se reemplazó el selector con AM/PM por un control `HH:mm` en formato 24 horas para mantener consistencia con la tabla y con la lógica de persistencia.

### Tabla responsive según contenido

La altura de la tabla ajusta según la cantidad de horarios cargados:

- si hay pocas comidas, ocupa solo el espacio necesario,
- si hay muchas, crece hasta el máximo disponible en la pantalla,
- se respeta el espacio anterior al footer para que no quede pegada.

### Eliminación con confirmación

La eliminación de un horario cuenta con un flujo claro:

- `Eliminar`
- `Confirmar`
- `Cancelar`

Esto evita borrados accidentales y mejora la experiencia.

### Assets e iconos

Se revisó la carga de archivos estáticos para que no fallen ni el logo ni el icono de basura, y se validó el acceso a los recursos desde la aplicación.

## Validación funcional

Se comprobó que:

- la aplicación puede levantarse con Flask,
- la porción se guarda correctamente,
- los horarios persisten en SQLite,
- la eliminación funciona,
- los assets y favicon sirven correctamente,
- la visual del selector y la tabla se mantienen coherentes con el diseño.

## Cómo correr la app

Desde la raíz del proyecto:

```bash
python run.py
```

Luego abrir en el navegador:

```text
http://localhost:5000
```

## Estado actual

El proyecto quedó estructurado como una base funcional de frontend + backend con persistencia real, lista para continuar con integración de hardware y lógica de dispensado.
