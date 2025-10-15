# Descargador de Reportes Excel - ETL Service

Una aplicación de escritorio desarrollada con Flet para descargar reportes de fitosanidad de manera asíncrona desde el servicio web de AB.

## Características

- **Interfaz gráfica moderna**: Desarrollada con Flet para una experiencia de usuario intuitiva
- **Descargas asíncronas**: Descarga múltiples reportes simultáneamente para mayor eficiencia
- **Selección de fechas**: Interfaz de calendario para seleccionar rango de fechas
- **Validación de datos**: Validación automática de rangos de fechas
- **Progreso en tiempo real**: Barra de progreso y mensajes de estado durante la descarga
- **Arquitectura MVC**: Código organizado siguiendo el patrón Modelo-Vista-Controlador

## Estructura del Proyecto

```
etl-service/
├── src/
│   ├── model/           # Modelos de datos
│   │   ├── __init__.py
│   │   ├── api_params.py
│   │   ├── api_request.py
│   │   ├── api_response.py
│   │   └── date_range.py
│   ├── service/         # Servicios de negocio
│   │   ├── __init__.py
│   │   └── download_service.py
│   ├── controller/      # Controladores
│   │   ├── __init__.py
│   │   └── download_controller.py
│   └── view/           # Interfaz de usuario
│       ├── __init__.py
│       └── main_view.py
├── downloads/          # Carpeta de descargas (se crea automáticamente)
├── .env               # Variables de entorno
├── main.py           # Punto de entrada de la aplicación
├── requirements.txt  # Dependencias
└── README.md        # Este archivo
```

## Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd etl-service
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno**
   
   Asegúrate de que el archivo `.env` contenga las siguientes variables:
   ```env
   API_SCHEME=http
   API_HOST=35.190.132.15
   API_PORT=8087
   API_BASE=/WS_AB/api
   EXCEL_RPT_PATH=/Fitosanidad/ZABG_ExcelRptEvaluacionesXVariable
   AUTHORIZATION=Basic NGdyMUJyNCFuTVM6NDg2Mjc1OTEz
   ```

## Uso

### Ejecutar la aplicación

```bash
python main.py
```

### Interfaz de usuario

1. **Seleccionar fechas**: Haz clic en los campos de fecha para abrir el calendario y seleccionar:
   - Fecha de inicio
   - Fecha de fin

2. **Iniciar descarga**: Haz clic en el botón "Descargar Reportes"

3. **Monitorear progreso**: La aplicación mostrará:
   - Barra de progreso
   - Mensajes de estado en tiempo real
   - Resultados al completar la descarga

### Reportes descargados

La aplicación descarga automáticamente reportes de las siguientes cartillas:
- Cartilla 492
- Cartilla 493  
- Cartilla 624
- Cartilla 669

Los archivos se guardan en la carpeta `downloads/` con el formato:
```
reporte_cartilla_{numero_cartilla}_{fecha_inicio}_{fecha_fin}.xlsx
```

## Parámetros de la API

Los reportes se descargan con los siguientes parámetros fijos:
- **Fundo**: 290
- **Cultivo**: 2
- **RUC Empresa**: 20170040938

Los únicos parámetros variables son las fechas de inicio y fin seleccionadas por el usuario.

### Formato de respuesta de la API

La API devuelve los archivos Excel como cadenas base64 en lugar de datos binarios directos. El servicio de descarga maneja automáticamente:

- **Decodificación base64**: Convierte la respuesta de texto a bytes
- **Validación con Polars**: Verifica que los archivos Excel sean válidos
- **Información detallada**: Muestra filas, columnas y estructura de datos
- **Manejo de errores**: Detecta y reporta problemas en la descarga o formato

## Arquitectura

### Modelo (Model)
- `APIParams`: Parámetros para las llamadas a la API
- `APIRequest`: Estructura de peticiones HTTP
- `APIResponse`: Estructura de respuestas HTTP
- `DateRange`: Rango de fechas

### Vista (View)
- `MainView`: Interfaz gráfica principal con Flet

### Controlador (Controller)
- `DownloadController`: Lógica de negocio para las descargas

### Servicio (Service)
- `DownloadService`: Manejo de peticiones HTTP y descarga de archivos

## Dependencias

- **flet**: Framework para interfaces gráficas multiplataforma
- **aiohttp**: Cliente HTTP asíncrono
- **python-dotenv**: Manejo de variables de entorno
- **polars**: Procesamiento y validación de datos Excel de alto rendimiento

## Solución de problemas

### Error de conexión
- Verifica que el servidor esté disponible en `35.190.132.15:8087`
- Comprueba la configuración de red y firewall

### Error de autenticación
- Verifica que la variable `AUTHORIZATION` en `.env` sea correcta

### Archivos no se descargan
- Verifica que tengas permisos de escritura en la carpeta del proyecto
- Comprueba que las fechas seleccionadas sean válidas

### La aplicación no inicia
- Verifica que todas las dependencias estén instaladas
- Comprueba que el archivo `.env` exista y esté configurado correctamente

## Desarrollo

Para contribuir al proyecto:

1. Sigue la arquitectura MVC establecida
2. Mantén el código asíncrono para las operaciones de red
3. Agrega validaciones apropiadas
4. Documenta los cambios en este README

## Licencia

Este proyecto es de uso interno para AB.