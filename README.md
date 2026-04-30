# Sistema Q&A Banco de Occidente: Asistente Virtual Corporativo

Este repositorio contiene el diseño e implementación de un sistema de preguntas y respuestas (Q&A) orientado a centralizar y facilitar el acceso a la información pública del **Banco de Occidente**. El proyecto utiliza una arquitectura de Generación Aumentada por Recuperación (RAG) para garantizar respuestas precisas y controladas.

## 🎓 Contexto Académico
* **Institución:** Universidad Autónoma de Occidente (UAO).
* **Programa:** Maestría en Inteligencia Artificial y Ciencias de Datos.
* **Asignatura:** Técnicas Avanzadas de IA Aplicadas en Modelos de Lenguaje.
* **Docente:** Jan Polanco Velasco.
* **Autores:**
    * Juan Manuel García Ortiz
    * Ricardo Muñoz Bocanegra
    * Deybar Andres Mora Segura
    * Luisa María Candelo Angulo

## 📝 Resumen del Proyecto
El sistema aborda la necesidad de un canal de comunicación automatizado que mitigue las limitaciones de los canales tradicionales (escalabilidad y disponibilidad 24/7) y el riesgo de inconsistencias en las respuestas humanas. Mediante el uso de modelos de lenguaje de gran escala (LLM) y técnicas de recuperación de información, el asistente proporciona datos sobre productos, servicios y políticas basados exclusivamente en la documentación oficial.

## ⚙️ Arquitectura y Metodología (RAG)
El proyecto implementa un flujo de trabajo estructurado en cuatro etapas principales:

1.  **Adquisición de Datos (Extraction Pipeline):**
    * Ejecución de un *crawling* exhaustivo y *scraping* mediante Selenium.
    * Procesamiento de 375 URLs del dominio oficial y documentos PDF institucionales.
2.  **Procesamiento y Refinamiento (Data Refining):**
    * Limpieza semántica, normalización de texto y segmentación estructurada (*chunking*) para crear una base de conocimiento coherente.
    * Construcción de un `CORPUS MASTER` en formato Markdown.
3.  **Modelado y Recuperación:**
    * **Motor de Búsqueda:** Utiliza vectorización **TF-IDF** y cálculo de **similitud coseno** para identificar los fragmentos de texto más relevantes ante una consulta.
    * **Generación (LLM):** Integración con la familia de modelos **Gemini de Google**, configurada con reglas estrictas de *Prompt Engineering* para evitar alucinaciones.
4.  **Consulta e Interfaz:**
    * Interfaz de usuario desarrollada en **Streamlit** para la orquestación entre el usuario y el LLM.

## 📊 Análisis de Calidad y Resultados
* **Precisión:** Se evidenció una alta precisión en la recuperación de información relevante, con un promedio de similitud coseno superior a 0.7 en las consultas evaluadas.
* **Fiabilidad:** El sistema prioriza la fiabilidad sobre la cobertura; si la información no se encuentra en el corpus, responde con una plantilla estándar de insuficiencia.

## 🛠️ Estructura del Repositorio
* `data/corpus_master.md`: Base de conocimiento final procesada.
* `data/urls.txt`: Listado de las 375 fuentes oficiales procesadas.
* `.env.example`: Plantilla para la configuración de la API Key de Gemini.

## ⚠️ Limitaciones y Trabajo Futuro
* **Dependencia del Corpus:** Requiere actualizaciones periódicas para reflejar cambios en productos o regulaciones.
* **Representación Semántica:** Actualmente utiliza TF-IDF; se planea migrar a *embeddings* más avanzados en fases posteriores.
* **Restricciones Técnicas:** Uso del *free tier* de Gemini, lo que impone límites de cuota.
