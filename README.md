# Dashboard Estudiantil Universitario

Dashboard local para analizar datos académicos de estudiantes universitarios. El proyecto incluye una aplicación de escritorio en Python con Tkinter y una versión HTML estática que se puede abrir directamente desde el navegador.

## Características

- Indicadores principales de estudiantes, aplazamientos, deserción voluntaria, bajo rendimiento y distribución por género.
- Filtros por programa, semestre, nombre, condición académica, género y estado.
- Gráficas de evolución de inscripciones, distribución por estado, comparativas por carrera y análisis 3D.
- Tabla detallada con datos de estudiantes.
- Reordenamiento de widgets con persistencia en `config/layout.json`.
- Exportación de reportes en PNG y PDF dentro de `reports/`.
- Generación de una versión web estática en `web/dashboard.html`.

## Tecnologías

- Python 3
- Tkinter / ttk
- Pandas
- NumPy
- Matplotlib
- Plotly
- ReportLab
- tkinterweb
- OpenPyXL

## Estructura del proyecto

```text
.
|-- assets/                 # Estilos y recursos visuales
|-- config/                 # Configuración del layout
|-- core/                   # Carga, procesamiento y exportación de datos
|-- data/                   # Dataset Excel
|-- reports/                # Reportes generados
|-- templates/              # Plantillas HTML de gráficas
|-- ui/                     # Interfaz gráfica de escritorio
|-- web/                    # Dashboard HTML generado
|-- build_static_dashboard.py
|-- main.py
|-- requirements.txt
`-- README.md
```

## Instalación

Clona el repositorio y entra al directorio del proyecto:

```bash
git clone <URL_DEL_REPOSITORIO>
cd dashboard-Interactivo-Universitario
```

Crea y activa un entorno virtual:

```bash
python -m venv venv
```

En Windows:

```bash
venv\Scripts\activate
```

En Linux o macOS:

```bash
source venv/bin/activate
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

Para ejecutar la aplicación de escritorio:

```bash
python main.py
```

Si no existe el archivo `data/estudiantes_universitarios.xlsx`, la aplicación genera automáticamente un dataset de prueba.

## Generar dashboard HTML

Para crear o actualizar la versión web estática:

```bash
python build_static_dashboard.py
```

Después abre el archivo:

```text
web/dashboard.html
```

La versión HTML permite consultar el dashboard desde el navegador y exportar el reporte visual como imagen o abrir una vista imprimible para guardar como PDF.

## Datos esperados

El archivo Excel debe estar ubicado en:

```text
data/estudiantes_universitarios.xlsx
```

Columnas requeridas:

- `id_estudiante`
- `nombre`
- `genero`
- `programa`
- `fecha_inscripcion`
- `semestre_ingreso`
- `aplazamiento`
- `semestre_aplazamiento`
- `desercion_voluntaria`
- `fecha_desercion`
- `bajo_rendimiento`
- `semestre_actual`
- `estado`

## Exportaciones

Desde la aplicación se pueden generar reportes en:

- PNG
- PDF

Los archivos se guardan automáticamente en la carpeta `reports/`.

## Notas para GitHub

Se recomienda no subir el entorno virtual `venv/`, archivos `__pycache__/` ni reportes generados automáticamente. Estos archivos pueden excluirse con un `.gitignore`.
