# Sistema Q&A Banco de Occidente: Asistente Virtual Corporativo

Este repositorio contiene el diseño e implementación de un sistema de preguntas y respuestas (Q&A) diseñado para centralizar y facilitar el acceso a la información pública del Banco de Occidente. El proyecto abarca desde la construcción técnica de una base de conocimiento sólida hasta el diseño final de una arquitectura de Generación Aumentada por Recuperación (RAG) de base léxica, garantizando respuestas precisas, controladas y alineadas exclusivamente con la documentación oficial de la entidad.

## 🎓 Contexto Académico
* **Institución:** Universidad Autónoma de Occidente (UAO)
* **Programa:** Maestría en Inteligencia Artificial y Ciencias de Datos
* **Asignatura:** Técnicas Avanzadas de IA Aplicadas en Modelos de Lenguaje
* **Módulo:** 1
* **Docente:** Jan Polanco Velasco
* **Autores:**
  * Juan Manuel García Ortiz
  * Ricardo Muñoz Bocanegra
  * Deybar Andres Mora Segura
  * Luisa María Candelo Angulo
* **Fecha:** Mayo de 2026

## 📋 Descripción del Proyecto
El sistema aborda la necesidad de un canal de comunicación automatizado que mitigue las limitaciones de las búsquedas tradicionales en sitios web complejos. El alcance de este entregable abarca el ciclo completo de desarrollo: parte desde la construcción exhaustiva de la base de conocimiento hasta el diseño e implementación final de un motor de recuperación léxica (Baseline RAG). Esta solución combina técnicas de **web scraping** con modelos de lenguaje de gran escala (LLM), evitando alucinaciones mediante el uso de un corpus documental restringido y reglas estrictas de *Prompt Engineering*.

## ⚙️ Arquitectura y Metodología
El flujo de trabajo se divide en cuatro etapas técnicas fundamentales, centradas en la construcción de una base de conocimiento robusta:

1.  **Adquisición de Datos (Extraction Pipeline):**
    * Ejecución de un *crawling* y *scraping* exhaustivo utilizando **Selenium**.
    * Procesamiento de 375 URLs del dominio oficial y documentos PDF institucionales para capturar la oferta completa de productos y servicios.
2.  **Procesamiento y Refinamiento (Data Refining):**
    * **Limpieza:** Eliminación de ruido de interfaces web (scripts, etiquetas HTML, menús de navegación).
    * **Normalización:** Estandarización del texto para asegurar la coherencia semántica.
    * **Segmentación:** División del contenido en secciones lógicas basadas en encabezados para optimizar la recuperación por palabras clave.
3.  **Modelado y Recuperación (Motor de Paso Cero):**
    * **Representación:** Construcción de un `CORPUS MASTER` estructurado en formato Markdown.
    * **Motor de Búsqueda:** Implementación de recuperación léxica mediante vectorización **TF-IDF** y **BM25**, utilizando **similitud coseno** para identificar los fragmentos de texto con mayor coincidencia de términos ante cada consulta.
    * **Generación (LLM):** Orquestación con modelos **Google Gemini**, configurados mediante prompts de sistema para responder únicamente con base en el contexto recuperado.
4.  **Consulta e Interfaz (Front-end):**
    * Desarrollo de una aplicación web interactiva en **Streamlit** que gestiona la comunicación entre el usuario y el motor de IA en tiempo real.

![Texto alternativo de la imagen](https://drive.google.com/uc?export=view&id=1w3I-21Mzl4JSo8Ngk4fxbip_Z6vrsAFC)

## 💻 Instalación y Ejecución

### Requisitos Previos
* Python 3.9 o superior.
* Google Gemini API Key (obtenida en Google AI Studio).

### Configuración del Entorno
1. Clonar el repositorio:
   ```bash
   git clone [https://github.com/deybar/qna_banco_occidente.git](https://github.com/deybar/qna_banco_occidente.git)
   cd qna_banco_occidente

2. Instalar las dependencias requeridas:
   ```bash
   pip install streamlit selenium webdriver-manager pypdf scikit-learn python-dotenv google-genai

3. Configurar las variables de entorno:

 * Crear un archivo `.env` en la raíz del proyecto.
 * Agregar tu API Key: `GEMINI_API_KEY=tu_clave_aqui`.

### Ejecución de la Interfaz
Para iniciar el asistente virtual, ejecuta el siguiente comando:
 ```bash
 streamlit run app.py
 ```

### 🔄 (Opcional) Reproducción del Pipeline de Datos

Si deseas regenerar el `corpus_master.md` desde cero, puedes ejecutar los scripts del pipeline en orden secuencial:
```bash
python 00_reset.py               # Limpia directorios antiguos
python 01_crawling.py            # Obtiene URLs
python 02_scraping_selenium.py   # Extrae texto web y PDFs
python 03_cleaner.py             # Limpia ruido de UI
python 04_markdown_builder.py    # Estructura en Markdown
python 05_corpus_master.py       # Consolida el corpus final
```
---

## 📊 Análisis y Calidad de los Resultados

El sistema demostró una alta precisión en temas de cuentas de ahorro, créditos, tarjetas y canales digitales.

Se prioriza la **fiabilidad sobre la cobertura**: cuando la información no existe en el corpus o no hay coincidencia exacta de términos, el sistema utiliza una plantilla estándar de insuficiencia.

### 📌 Ejemplos de Interacción

| Consulta del Usuario | Respuesta del Sistema |
|---------------------|----------------------|
| ¿Cuáles son los requisitos para una tarjeta? | Los requisitos incluyen ser mayor de edad, ingresos mínimos y buen historial crediticio. |
| ¿Cómo puedo abrir una cuenta? | Puedes acudir a sucursales o realizar el proceso en línea en nuestro portal. |
| ¿De qué color son los zapatos del gerente? | No cuento con información específica sobre ese tema en la base documental. |

---

## 🛠️ Estructura de Datos y Entregables

- `data/corpus_master.md`: Base de conocimiento final generada  
- `data/urls.txt`: Evidencia de las 375 fuentes procesadas  
- `.env.example`: Plantilla para configuración de secretos  

---

## ⚠️ Limitaciones

- **Actualización del Corpus:** Dependencia de la información estática actual  
- **Búsqueda Léxica:** El sistema depende de coincidencia de palabras (TF-IDF); se proyecta la migración a búsqueda semántica (embeddings) en el Módulo 2  
- **Restricciones de Cuota:** Limitaciones asociadas al uso gratuito de la API de Gemini  

---

## 💡 Conclusiones

Este primer entregable demuestra la viabilidad de estructurar conocimiento institucional bajo límites claros de alcance.

El éxito radica en:
- El diseño del prompt  
- La calidad de la preparación de los datos  

Esto establece la arquitectura base para la evolución hacia sistemas RAG basados en redes neuronales.

---

## 🚀 Seguridad

- Las credenciales (`.env`) están excluidas del repositorio  
- Se utiliza un entorno controlado para fines académicos  
