# Sistema Q&A Banco de Occidente: Asistente Virtual Corporativo

Este repositorio contiene el diseño e implementación de un sistema de preguntas y respuestas (Q&A) diseñado para centralizar y facilitar el acceso a la información pública del **Banco de Occidente**. El proyecto utiliza una arquitectura de Generación Aumentada por Recuperación (RAG) para garantizar respuestas precisas, controladas y alineadas exclusivamente con la documentación oficial de la entidad.

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
El sistema aborda la necesidad de un canal de comunicación automatizado que mitigue las limitaciones de escalabilidad de los canales tradicionales. El núcleo de la solución es un motor RAG que combina técnicas de recuperación de información con modelos de lenguaje de gran escala (LLM), evitando alucinaciones mediante el uso de un corpus documental restringido y reglas estrictas de *Prompt Engineering*.

## ⚙️ Arquitectura y Metodología
El flujo de trabajo se divide en cuatro etapas técnicas fundamentales:

1.  **Adquisición de Datos (Extraction Pipeline):**
    * Ejecución de un *crawling* y *scraping* exhaustivo utilizando **Selenium**.
    * Procesamiento de 375 URLs del dominio oficial y documentos PDF institucionales para capturar la oferta completa de productos y servicios.
2.  **Procesamiento y Refinamiento (Data Refining):**
    * **Limpieza:** Eliminación de ruido de interfaces web (scripts, etiquetas HTML, menús de navegación).
    * **Normalización:** Estandarización del texto para asegurar la coherencia semántica.
    * **Segmentación:** División del contenido en fragmentos lógicos (*chunking*) para optimizar la recuperación.
3.  **Modelado y Recuperación:**
    * **Representación:** Construcción de un `CORPUS MASTER` en formato Markdown.
    * **Motor de Búsqueda:** Implementación de vectorización **TF-IDF** y cálculo de **similitud coseno** para identificar los fragmentos más relevantes ante cada consulta.
    * **Generación (LLM):** Orquestación con modelos **Google Gemini**, configurados para responder únicamente con base en el contexto recuperado.
4.  **Consulta e Interfaz (Front-end):**
    * Desarrollo de una aplicación web interactiva en **Streamlit** que gestiona la comunicación entre el usuario y el motor de IA en tiempo real.

## 📊 Análisis y Calidad de los Resultados
La validación funcional se realizó a través de la interfaz de Streamlit, la cual permite monitorear el estado del sistema de manera transparente. El diseño visual es coherente con el contexto financiero institucional, utilizando una paleta de colores sobria y una estructura de navegación clara.

### Desempeño y Precisión
El sistema demostró una alta precisión en temas de cuentas de ahorro, créditos, tarjetas y canales digitales. Se prioriza la **fiabilidad sobre la cobertura**: cuando la información no existe en el corpus, el sistema utiliza una plantilla estándar de insuficiencia.

#### Ejemplos de Interacción:
| Consulta del Usuario | Respuesta del Sistema |
| :--- | :--- |
| *“¿Cuáles son los requisitos para solicitar una tarjeta de crédito?”* | Ofrecemos tarjetas Visa y Mastercard... Los requisitos incluyen ser mayor de edad, ingresos mínimos verificables y buen historial crediticio. |
| *“¿Cómo puedo abrir una cuenta de ahorros?”* | Puedes acudir a nuestras sucursales con tu documento de identidad o realizar el proceso en línea a través de nuestro portal transaccional. |
| *“¿Qué servicios ofrece para empresas?”* | Contamos con servicios empresariales como banca comercial, leasing, factoring y comercio exterior. |
| *“¿De qué color son los pantalones del presidente del Banco?”* | **No cuento con información específica sobre ese tema en la base documental actual.** |

## 🛠️ Estructura de Datos y Entregables
* `data/corpus_master.md`: Base de conocimiento final generada para el sistema Q&A.
* `data/urls.txt`: Evidencia de las 375 fuentes procesadas mediante scraping.
* `.env.example`: Plantilla para configurar la API Key de Google Gemini.

## ⚠️ Limitaciones
* **Actualización del Corpus:** Dependencia de la información estática actual; requiere actualizaciones periódicas de las fuentes.
* **Representación Semántica:** Uso de TF-IDF; se proyecta la migración a *embeddings* vectoriales más avanzados en fases futuras.
* **Restricciones de Cuota:** Limitaciones asociadas al uso del modelo Gemini en su modalidad gratuita.

## 💡 Conclusiones
El proyecto demuestra la viabilidad de estructurar conocimiento institucional mediante modelos de lenguaje bajo límites claros de alcance. El éxito del sistema radica en el diseño riguroso del prompt y la calidad de la preparación de los datos (limpieza semántica y control semántico), sentando las bases para arquitecturas RAG más complejas.

## 🚀 Seguridad
* Las credenciales y secretos (archivo `.env`) están estrictamente excluidos del repositorio.
* Se utiliza un entorno controlado para pruebas y demostraciones académicas.
