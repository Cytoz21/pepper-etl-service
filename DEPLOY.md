# Despliegue en Dokploy - Guía Rápida

## Pasos para desplegar:

### 1. Preparar el repositorio
```bash
# Asegúrate de que todo esté commiteado
git add .
git commit -m "Preparado para despliegue web"
git push
```

### 2. En Dokploy:

1. **Crear nuevo proyecto**:
   - Ve a "Projects" → "New Project"
   - Nombre: `pepper-etl-service`

2. **Configurar el servicio**:
   - Tipo: **Application**
   - Source: **Git Repository**
   - Repository URL: Tu repositorio Git
   - Branch: `main` (o la que uses)

3. **Variables de entorno** (en Settings → Environment):
   ```
   PRODUCTION=true
   API_SCHEME=http
   API_HOST=35.190.132.15
   API_PORT=8087
   API_BASE=/WS_AB/api
   EXCEL_RPT_PATH=/Fitosanidad/ZABG_ExcelRptEvaluacionesXVariable
   AUTHORIZATION=Basic NGdyMUJyNCFuTVM6NDg2Mjc1OTEz
   ```

4. **Configurar dominio** (en Settings → Domains):
   - Agrega tu dominio (ej: `reportes.tudominio.com`)
   - Dokploy configurará automáticamente HTTPS con Let's Encrypt

5. **Deploy**:
   - Click en "Deploy"
   - Espera a que termine el build

### 3. Acceder a la aplicación:
- Abre tu navegador en: `https://reportes.tudominio.com`

## Notas importantes:

### Diferencias en modo Web:
- ✅ La aplicación funciona igual visualmente
- ⚠️ **Selector de carpetas**: En web, los archivos se descargan automáticamente a la carpeta de "Descargas" del navegador
- ⚠️ No puedes elegir la ubicación de descarga (limitación del navegador)

### Alternativa para control de carpetas:
Si necesitas control total sobre dónde se guardan los archivos, considera:
1. Mantener la app de escritorio para usuarios internos
2. Usar la web solo para consultas/visualización
3. O implementar un sistema de almacenamiento en el servidor (S3, etc.)

## Troubleshooting:

Si hay errores:
1. Revisa los logs en Dokploy: "Logs" tab
2. Verifica que las variables de entorno estén correctas
3. Asegúrate de que el puerto 8080 esté expuesto

## Actualizar la aplicación:
```bash
git push
```
Dokploy detectará automáticamente los cambios y redesplegará.
