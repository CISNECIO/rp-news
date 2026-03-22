# RP — Visualizador de Noticias Financieras

Aplicación local para visualizar y clasificar noticias financieras con interfaz editorial premium inspirada en portadas de medios financieros.

## Arquitectura

**HTML + CSS + JavaScript + Python (conversión)**

Se eligió esta arquitectura porque:
- **Zero dependencias del frontend**: un solo archivo HTML con todo embebido
- **Fácil de ejecutar**: solo necesitas Python y un navegador
- **Mantenimiento mínimo**: reemplazas el Excel, ejecutas el script y listo
- **Sin servidor permanente**: Python solo se usa para la conversión; la app corre estática

## Estructura del proyecto

```
rp-news/
├── index.html          ← Aplicación principal (abrir en navegador)
├── convert.py          ← Script Python para convertir Excel → JSON
├── Sample.xlsx         ← Tu archivo Excel con las noticias
├── data/
│   └── news.json       ← JSON generado automáticamente
└── README.md           ← Este archivo
```

## Requisitos

- **Python 3.7+** con `pandas` y `openpyxl`
- **Navegador moderno** (Chrome, Firefox, Edge, Safari)

## Instalación rápida

```bash
# 1. Instalar dependencias de Python (si no las tienes)
pip install pandas openpyxl

# 2. Colocar tu Excel en la carpeta del proyecto como Sample.xlsx

# 3. Ejecutar la conversión
python convert.py

# 4. Abrir index.html en el navegador
# Opción A: doble clic en index.html
# Opción B: servidor local (recomendado para imágenes externas)
python -m http.server 8000
# Luego abrir http://localhost:8000 en tu navegador
```

## Cómo actualizar las noticias

1. Reemplaza `Sample.xlsx` con tu nuevo archivo Excel
2. Ejecuta `python convert.py` (o `python convert.py mi_archivo.xlsx` si tiene otro nombre)
3. Recarga la página en el navegador

¡Eso es todo! No necesitas modificar ni reconstruir nada más.

## Funcionalidades

- **Portada editorial** con noticia destacada, feed y sidebar de "Últimas"
- **Navegación por categorías** desde la barra superior
- **Búsqueda general** por título, resumen, palabras clave y fuente
- **Filtros combinables**: categoría, fuente, rango de fechas
- **Ordenamiento** ascendente/descendente por fecha
- **Vista de detalle (modal)** con toda la información de la noticia
- **Enlace al artículo original** en nueva pestaña
- **Manejo elegante de datos faltantes**
- **Diseño responsive** para laptop, tablet y móvil

## Lógica de datos

- **Fuente**: se extrae del texto entre paréntesis al final del título, e.g. "(Gestión)"; si no existe, se usa el dominio de la URL
- **Categoría**: se usa la columna "Clasificación"; si falta, se infiere de palabras clave y título
- **Fechas**: ordenadas de más reciente a más antigua por defecto
- **Imágenes**: se usa "URL imagen"; si falla la carga, se muestra placeholder

## Mejoras futuras opcionales

- Exportar noticias filtradas a CSV/PDF
- Modo oscuro
- Gráficos de tendencias por categoría o fuente
- Automatización con cron para conversión periódica
- Integración con feeds RSS para importar noticias automáticamente
- Paginación para datasets grandes (100+ noticias)
- Estadísticas editoriales (noticias por categoría/fuente/semana)
