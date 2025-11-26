# Informe Técnico – Avance 1  
## Proyecto PP3 – Digitalización y Gestión de Datos del Departamento Jurídico de Vialidad Provincial  
### Tecnicatura en Ciencia de Datos e Inteligencia Artificial – Año 2025

---

## 1. Descripción general del proyecto
El proyecto tiene como objetivo diseñar una solución que permita digitalizar los registros del Departamento Jurídico de la Dirección de Vialidad de Santiago del Estero. Actualmente, la información se gestiona en papel, lo que dificulta la organización, el seguimiento y la posibilidad de generar indicadores.

La propuesta incluye el desarrollo de:
- Una aplicación de carga de datos.
- Una base de datos simulada en formato CSV.
- Análisis exploratorios y primeros indicadores.
- Un dashboard para visualizar información relevante.

---

## 2. Diagnóstico y situación actual
El Departamento Jurídico no cuenta con un sistema digital para registrar expedientes o resoluciones. La información se guarda en carpetas físicas, lo que genera:

- Dificultad para recuperar datos históricos.  
- Ausencia de estadísticas institucionales.  
- Riesgo de pérdida o deterioro de documentos.  
- Limitaciones en la trazabilidad y control del trabajo administrativo.

Esta situación impide aprovechar herramientas de análisis y dificulta la toma de decisiones basada en datos.

---

## 3. Propuesta general del proyecto
El proyecto propone implementar un sistema básico de digitalización compuesto por:

- Una aplicación en Python (Tkinter) para la carga de datos.
- Un archivo CSV como base de datos inicial.
- Scripts de análisis y visualización desarrollados en notebooks.
- Un dashboard interactivo en Streamlit y Looker Studio.

El objetivo es establecer una estructura organizada que permita mejorar la gestión de expedientes y preparar a la entidad para futuras implementaciones de analítica avanzada o modelos predictivos.

---

## 4. Objetivo y alcance
**Objetivo general:**  
Digitalizar, centralizar y organizar los registros jurídicos del Departamento de Vialidad.

**Alcance de los Avances:**  
- Diagnóstico inicial de la situación.  
- Definición de la estructura del proyecto.  
- Creación del dataset simulado (1550 registros, 20 variables).  
- Desarrollo preliminar de la aplicación de carga en Tkinter.  
- Estructura del repositorio en GitHub.  
- Inicio del notebook de análisis exploratorio.

**Fuera de alcance:**  
- Implementación real en la institución.  
- Uso de datos reales y confidenciales.  
- Conexión a sistemas internos del organismo.

---

## 5. Flujo de datos inicial
El flujo propuesto para el manejo de datos es el siguiente:

1. **Carga de datos:**  
   Los expedientes se ingresan mediante la aplicación Tkinter.

2. **Almacenamiento:**  
   La información se guarda en un archivo CSV con formato estructurado.

3. **Visualización:**  
   Los resultados se presentan en dashboards interactivos desarrollados en Looker Studio.

4. **Procesamiento:**  
   Los datos se limpian y analizan en Python utilizando Jupyter Notebook.

Este flujo asegura consistencia, trazabilidad y la posibilidad de realizar análisis más avanzados en etapas posteriores.

---

## 6. Estructura de datos propuesta
Los datos se almacenan en un archivo CSV y una hoja de cálculo (Google Sheets) con varias columnas (22)

Esta estructura permite organizar la información de forma clara y facilita su procesamiento mediante Python.

---

## 7. Estructura del repositorio

data/dataset_simulado.csv
notebooks/EDA_Vialidad.ipynb
          ModeloPredictivo_RF.ipynb
app/app.py
docs/informe_tecnico.md
    video_demo_link.txt
README.md
