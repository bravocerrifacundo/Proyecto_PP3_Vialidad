# Proyecto_PP3_Vialidad
# Proyecto PP3 – Digitalización y Gestión de Datos del Departamento Jurídico de Vialidad Provincial  

Este repositorio contiene el desarrollo del Proyecto Final PP3 de la Tecnicatura en Ciencia de Datos e Inteligencia Artificial (Año 2025).  
El objetivo principal es digitalizar los registros jurídicos del área mediante una aplicación de carga de datos y herramientas de análisis y visualización.

---

## 📁 Estructura del repositorio

data/ → datasets simulados  
notebooks/ → análisis exploratorio y modelo predictivo  
app/ → código de la aplicación de carga  
docs/ → documentación técnica y demo  
README.md → guía principal del proyecto

## 🔧 Cómo utilizar cada apartado del proyecto

### 1. Carpeta **/data**
Contiene el archivo `dataset_simulado.csv`, que representa la base de datos del proyecto.
- Abrir con Excel, Google Sheets o Pandas.
- Los notebooks utilizan este archivo como fuente principal.
- Si se generan nuevos datos, deben guardarse en esta carpeta.

### 2. Carpeta **/notebooks**
Incluye los análisis y el modelo predictivo.

**analisis_exploratorio.ipynb**
- Cargar el dataset.
- Ejecutar limpieza, visualizaciones y análisis exploratorio.
- Identificar patrones y anomalías.

**modelo_predictivo.ipynb**
- Correr el modelo base de regresión para estimar el tiempo de resolución.
- Probar métricas y validar resultados.


### 3. Carpeta **/app**

- Contiene la aplicación de carga de datos desarrollada en Tkinter.
- Completar los campos de carga.
- Guardar registros (se almacenan como CSV).

### 4. Carpeta /docs

- Incluye la documentación formal del proyecto.
