# Guía de Módulos - Asistente Virtual Corporativo para el Banco de Occidente

**Asignatura:** Técnicas Avanzadas de IA Aplicadas en Modelos de Lenguaje  
**Docente:** Jan Polanco Velasco  
**Universidad:** Universidad Autónoma de Occidente  
**Maestría:** Inteligencia Artificial y Ciencias de Datos  
**Fecha:** Mayo de 2026  

**Integrantes:**
- Juan Manuel García Ortíz
- Ricardo Muñoz Bocanegra
- Deybar Andres Mora Segura
- Luisa María Candelo Angulo

**Empresa:** Banco de Occidente

---

## Módulo 1: Creación de la Base de Conocimiento Semántico y Sistema Q&A

### Objetivo
Diseñar y construir el núcleo de conocimiento para un futuro asistente virtual del **Banco de Occidente**, mediante la extracción de información pública oficial y la creación de un sistema de Preguntas y Respuestas (Q&A) basado en Prompt Engineering.

### Descripción del Problema
Las entidades financieras enfrentan dificultades para proporcionar información clara y oportuna debido a la dispersión de su contenido en cientos de páginas web, PDFs y canales digitales. Esto genera fricción en la experiencia del cliente.

### Planteamiento de la Solución
Construcción de un sistema Q&A basado en un núcleo de conocimiento semántico (RAG), que responde exclusivamente con información extraída de fuentes oficiales del Banco de Occidente.

### Preparación de los Datos
- **Scraping:** Crawling exhaustivo del dominio oficial → **375 URLs** recolectadas.
- **Herramientas:** Selenium (para contenido dinámico con JavaScript) + extracción de documentos PDF.
- **Limpieza:** Eliminación de ruido (menús, encabezados repetitivos), preservación de datos financieros (tasas, montos, condiciones).
- **Chunking:** Segmentación estructurada respetando jerarquía de títulos y secciones (no por tamaño arbitrario).

### Modelado
- **Representación:** TF-IDF + similitud coseno.
- **LLM:** Gemini (Google).
- **Prompt Engineering:** Prompt zero-shot robusto que define:
  - Rol: Asistente Virtual Institucional del Banco de Occidente.
  - Restricciones: Responder **solo** con el contexto proporcionado.
  - Comportamiento: Tono formal, admitir falta de información cuando corresponda.

### Interfaz
Aplicación web interactiva desarrollada con **Streamlit**.

### Pruebas
Se definieron y evaluaron **20 preguntas** exhaustivas (ver Anexos del Paper).

**Ejemplos de resultados:**
- Pregunta: "¿Cuáles son los requisitos para solicitar una tarjeta de crédito?"
- Pregunta: "¿Cómo puedo abrir una cuenta de ahorros?"
- Pregunta: "¿De qué color son los pantalones del presidente del Banco de Occidente?" → Respuesta correcta de "insuficiencia de información".

### Limitaciones identificadas
Dependencia del corpus estático, uso de TF-IDF en lugar de embeddings semánticos avanzados y restricciones de cuota del modelo gratuito.

---

## Módulo 2: Transformación a un Agente Conversacional con Memoria y Múltiples Capacidades

### Objetivo
Evolucionar el sistema Q&A a un **agente inteligente** capaz de:
- Mantener memoria conversacional.
- Enrutar consultas entre diferentes herramientas.
- Mejorar precisión y experiencia del usuario.

### Preparación de los Datos (Actualización)
- Corpus expandido a **aproximadamente 950 documentos**.
- Incorporación de: contenido de redes sociales oficiales y **videos institucionales de YouTube**.

### Arquitectura del Agente
El agente utiliza un **enrutador** (Router) que decide dinámicamente qué herramienta utilizar según la consulta del usuario.

**Flujo principal:**
Usuario → Router (LLM) → Herramienta seleccionada → LLM → Respuesta

### Herramientas Implementadas
1. **Herramienta RAG (Corpus Documental)**
   - Embeddings semánticos.
   - Recuperación por similitud para preguntas abiertas (productos, servicios, historia, etc.).

2. **Herramienta de Datos Estructurados**
   - Archivo JSON/CSV con información puntual.
   - Ejemplos: NIT, teléfonos, horarios, direcciones, sedes, etc.
   - Acceso determinista (rápido y preciso).

### Gestión de Memoria
- Memoria conversacional de corto plazo (`ConversationBufferMemory`).
- Permite responder preguntas de seguimiento manteniendo el contexto.

### Prompt Engineering del Agente
Meta-prompt que instruye al modelo sobre:
- Su rol institucional.
- Cuándo usar cada herramienta.
- Reglas estrictas para evitar alucinaciones.

### Resultados
El agente demuestra:
- Correcta selección de herramienta según el tipo de consulta.
- Manejo coherente de conversaciones multi-turno.
- Mayor precisión y eficiencia comparado con el Módulo 1.

**Ejemplos:**
- “¿Cuál es el NIT del banco?” → Herramienta Estructurada → `890.300.279-4`
- “¿Qué servicios ofrece el banco?” → Herramienta RAG
- Preguntas de seguimiento usando memoria.

### Limitaciones
Memoria de corto plazo (no persiste entre sesiones), necesidad de actualización periódica del corpus.

---

## Rúbricas de Evaluación (Resumen)

### Módulo 1
- Análisis y Estrategia de Datos: 15%
- Procesamiento y Tareas LLM: 25%
- Prompt Engineering: 25%
- Aplicación Interactiva: 15%
- Documentación y Presentación: 20%

### Módulo 2
- Memoria Conversacional: 25%
- Herramientas y Enrutamiento: 30%
- Calidad de Aplicación y Código: 20%
- Documentación: 15%
- Presentación: 10%

---

**Estado del Proyecto:**  
- [x] Módulo 1 Completado  
- [x] Módulo 2 Completado  

---
