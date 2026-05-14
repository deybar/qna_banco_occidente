# Asistente Virtual Corporativo para el Banco de Occidente

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-0.3+-green.svg)](https://www.langchain.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.41+-red.svg)](https://streamlit.io/)
[![ChromaDB](https://img.shields.io/badge/ChromaDB-0.5+-purple.svg)](https://www.trychroma.com/)

## 📋 Descripción General

Sistema inteligente de Preguntas y Respuestas (Q&A) + Agente Conversacional para el **Banco de Occidente**, desarrollado como proyecto académico en la **Maestría en Inteligencia Artificial y Ciencias de Datos** de la **Universidad Autónoma de Occidente (UAO)**.

El proyecto demuestra la evolución desde un sistema Q&A basado en Retrieval-Augmented Generation (RAG) hacia un agente conversacional inteligente con memoria contextual, enrutamiento dinámico de consultas y múltiples herramientas especializadas.

---

## 👥 Equipo de Desarrollo

| Rol | Nombre |
|-----|--------|
| **Docente** | Jan Polanco Velasco |
| **Estudiante 1** | Juan Manuel García Ortíz |
| **Estudiante 2** | Ricardo Muñoz Bocanegra |
| **Estudiante 3** | Deybar Andres Mora Segura |
| **Estudiante 4** | Luisa María Candelo Angulo |
| **Empresa** | Banco de Occidente |

**Institución:** Universidad Autónoma de Occidente (UAO)  
**Maestría:** Inteligencia Artificial y Ciencias de Datos  
**Asignatura:** Técnicas Avanzadas de IA Aplicadas en Modelos de Lenguaje  
**Fecha:** Mayo de 2026

---

## 🎯 Objetivos del Proyecto

### Módulo 1: Base de Conocimiento Semántico y Sistema Q&A ✅

**Objetivo:** Diseñar y construir el núcleo de conocimiento para un asistente virtual del Banco de Occidente mediante extracción de información pública y creación de un sistema Q&A basado en Prompt Engineering.

**Problema:** Las entidades financieras enfrentan dificultades para proporcionar información oportuna debido a la dispersión de contenido en cientos de páginas web, PDFs y canales digitales.

**Solución:**
- Construcción de un corpus de conocimiento semántico mediante **web scraping exhaustivo** (375+ URLs).
- Implementación de un sistema Q&A basado en **RAG (Retrieval-Augmented Generation)**.
- Uso de **Prompt Engineering** con restricciones estrictas para evitar alucinaciones.
- Interfaz interactiva con **Streamlit**.

**Resultados:**
- ✅ Base de conocimiento con ~950 documentos procesados.
- ✅ Extracción exitosa de PDFs y contenido HTML dinámico.
- ✅ Evaluación positiva en 20 preguntas de prueba.
- ✅ Manejo correcto de consultas fuera del corpus.

### Módulo 2: Agente Conversacional con Memoria y Múltiples Capacidades 🚀

**Objetivo:** Evolucionar el sistema Q&A hacia un **agente inteligente** con:
- Memoria conversacional de corto plazo.
- Enrutamiento dinámico entre múltiples herramientas.
- Mejora en precisión y experiencia del usuario.

**Mejoras Implementadas:**

1. **Arquitectura de Agente Inteligente:**
   - **Router (LLM):** Decide dinámicamente qué herramienta usar según la consulta.
   - **Flujo:** Usuario → Router → Herramienta Seleccionada → LLM → Respuesta

2. **Herramientas Especializadas:**
   - **Herramienta RAG:** Embeddings semánticos para consultas abiertas (productos, servicios, historia).
   - **Herramienta Estructurada:** JSON/CSV con datos precisos (NIT, teléfonos, horarios, sedes).

3. **Gestión de Memoria:**
   - Conversaciones multi-turno coherentes.
   - Contexto mantenido durante la sesión.

**Resultados:**
- ✅ Selección correcta de herramientas según tipo de consulta.
- ✅ Conversaciones multi-turno contextuales.
- ✅ Mayor precisión y eficiencia vs. Módulo 1.

---

## 🛠️ Stack Tecnológico

### Lenguaje y Entorno
- **Python:** 3.10+ (tipado dinámico, amplio ecosistema)
- **Entorno Virtual:** `.venv/` (aislamiento de dependencias)
- **Gestor de Paquetes:** UV (rápido, moderno, resolver robusto)

### IA y LLMs
- **LangChain:** Framework para orquestación de LLMs y cadenas de procesamiento
- **LangChain-Google-GenAI:** Integración con Gemini (Google AI)
- **Gemini 2.5-Flash:** Modelo de lenguaje para generación de respuestas
- **Sentence Transformers:** Embeddings locales de alta calidad (sin cuotas)

### Recuperación y Búsqueda
- **ChromaDB:** Base de datos vectorial para almacenamiento y búsqueda de embeddings
- **LangChain-Chroma:** Integración de ChromaDB con LangChain

### Web Scraping
- **Requests:** Descarga de contenido HTTP
- **BeautifulSoup4:** Parsing de HTML estático
- **Selenium:** Scraping de contenido dinámico (JavaScript)
- **WebDriver Manager:** Gestión automática de drivers (Chrome, Firefox, Edge)
- **PyPDF:** Extracción de texto de archivos PDF

### APIs y Multimedia
- **Google API Client:** Acceso a APIs de Google
- **YouTube Transcript API:** Extracción de transcripciones de videos

### Interfaz de Usuario
- **Streamlit:** Desarrollo rápido de aplicaciones web interactivas
- **Configuración:** `config.toml` (temas, colores, ajustes de servidor)

### Herramientas de Desarrollo
- **Ruff:** Linting y formateo de código (rendimiento optimizado)
- **Git:** Control de versiones
- **Make:** Automatización de tareas del pipeline

---

## 📦 Requisitos Previos

Antes de comenzar, asegúrate de tener instalado:

- **Python 3.10 o superior**
  ```bash
  python --version  # Debe mostrar Python 3.10+
  ```

- **Git**
  ```bash
  git --version
  ```

- **Make** (para Windows):
  ```bash
  # Opción 1: Usar winget (recomendado)
  winget install GnuWin32.Make
  
  # Opción 2: Usar Chocolatey
  choco install make
  
  # Opción 3: Usar WSL (Windows Subsystem for Linux)
  wsl make --version
  ```
  
  **Para Linux/macOS:** Generalmente ya viene preinstalado.

---

## ⚡ Guía de Instalación Rápida

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu_usuario/qna_banco_occidente.git
cd qna_banco_occidente
```

### 2. Configurar Variables de Entorno

Copia el archivo de ejemplo y configúralo con tus claves API:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales:

```env
# Google Gemini API
GEMINI_API_KEY=tu_clave_aqui
GEMINI_MODEL=gemini-2.5-flash

# YouTube API (opcional, para scraping de videos)
YOUTUBE_API_KEY=tu_clave_aqui
```

**Nota:** No subes `.env` al repositorio (está en `.gitignore` por seguridad).

### 3. Instalar Dependencias y Entorno

```bash
make setup
```

Este comando automáticamente:
- Crea un entorno virtual con UV
- Instala todas las dependencias del `pyproject.toml`
- Prepara el entorno para ejecutar el proyecto

---

## 🚀 Ejecución del Proyecto

### Opción A: Ejecutar el Pipeline Completo

Para ejecutar todo el proceso de datos (crawling → scraping → limpieza → corpus → chunking):

```bash
make pipeline
```

**Pasos que se ejecutan:**
1. `crawl` - Descubrimiento de URLs del sitio del banco
2. `scrape` - Extracción de contenido HTML + PDFs
3. `clean` - Limpieza y filtrado del corpus
4. `md` - Conversión a Markdown estructurado
5. `corpus` - Construcción del corpus maestro
6. `chunks` - Chunking semántico + embeddings ChromaDB

### Opción B: Ejecutar Pasos Individuales

```bash
make crawl      # Solo crawling de URLs
make scrape     # Solo scraping de contenido
make clean      # Solo limpieza
make corpus     # Solo construcción de corpus
make chunks     # Solo chunking y embeddings
```

### Opción C: Lanzar la Interfaz Streamlit

Una vez completado el pipeline, inicia la aplicación interactiva:

```bash
make app
```

La aplicación se abrirá en: `http://localhost:8501`

---

## 📊 Comandos Disponibles (Makefile)

| Comando | Descripción |
|---------|-------------|
| `make help` | Muestra esta lista de comandos |
| `make setup` | Instala entorno y dependencias con UV |
| `make crawl` | Crawling de URLs del sitio del banco |
| `make scrape` | Scraping HTML + descarga de PDFs |
| `make clean` | Limpieza inteligente del corpus |
| `make corpus` | Construir corpus maestro final |
| `make pipeline` | Pipeline completo (crawl→scrape→clean→corpus→chunks) |
| `make youtube` | Scraping del canal YouTube del banco |
| `make chunks` | Chunking semántico + ChromaDB embeddings |
| `make app` | Lanzar interfaz Streamlit |
| `make reset` | Eliminar todos los datos generados |
| `make status` | Ver estado del proyecto |
| `make lint` | Verificar calidad del código con Ruff |

---

## 📁 Estructura del Proyecto

```
qna_banco_occidente/
│
├── 01_codigos/                      # Código principal del proyecto
│   ├── 00_reset.py                 # Limpieza de datos generados
│   ├── 01_crawling.py              # Descubrimiento de URLs
│   ├── 02_scraping_selenium.py     # Extracción de contenido
│   ├── 03_cleaner.py               # Limpieza del corpus
│   ├── 04_markdown_builder.py      # Conversión a Markdown
│   ├── 05_corpus_master.py         # Construcción de corpus maestro
│   ├── 06_youtube_scraper.py       # Scraping de YouTube
│   ├── 07_chunking.py              # Chunking + ChromaDB
│   ├── agent_router.py             # Router del agente conversacional (Módulo 2)
│   ├── app.py                      # Interfaz Streamlit
│   ├── config.py                   # Configuración global
│   ├── llm_chains.py               # Cadenas y prompts de LLM
│   ├── tools.py                    # Herramientas especializadas
│   └── config.toml                 # Configuración de Streamlit
│
├── data/                            # Directorio de datos
│   ├── 01_urls/                    # URLs descubiertas (versionadas en .git)
│   ├── 02_scraping/                # HTML extraído (ignorado en .git)
│   ├── 03_pdfs/                    # PDFs descargados (ignorado en .git)
│   ├── 04_clean/                   # Documentos limpios (ignorado en .git)
│   ├── 05_markdown/                # Documentos en Markdown (ignorado en .git)
│   ├── 06_corpus/                  # Corpus maestro (versionado)
│   ├── 07_estructurado/            # Datos estructurados JSON/CSV (versionado)
│   ├── 08_chroma/                  # ChromaDB vectorstore (ignorado en .git)
│   └── memoria/                    # Memoria del agente (ignorado en .git)
│
├── contexto/                        # Documentación del proyecto
│   └── contexto.md                 # Guía de módulos y objetivos
│
├── .env                            # Variables de entorno (IGNORADO - crear localmente)
├── .env.example                    # Plantilla de variables de entorno
├── .gitignore                      # Reglas de Git
├── .venv/                          # Entorno virtual (IGNORADO)
├── .git/                           # Historial de Git
├── main.py                         # Entry point del pipeline
├── pyproject.toml                  # Configuración de dependencias (UV/Hatchling)
├── uv.lock                         # Lock file de dependencias
├── Makefile                        # Automatización de tareas
└── README.md                       # Este archivo
```

---

## 🔐 Gestión de Datos y Seguridad

### ✅ Archivos Versionados (En Git)

Estos archivos se suben al repositorio porque son entregables fundamentales:

```
data/01_urls/urls.txt                    # Lista de URLs crawleadas
data/06_corpus/corpus_master.md          # Base de conocimiento final
data/07_estructurado/datos_banco.json    # Datos estructurados (NIT, sedes, etc.)
```

### ❌ Archivos Ignorados (Regenerables)

Estos directorios NO se suben a Git (están en `.gitignore`) porque se regeneran automáticamente:

```
data/02_scraping/          # HTML extraído (>100 MB)
data/03_pdfs/              # PDFs descargados (variable)
data/04_clean/             # Documentos limpios (regenerable)
data/05_markdown/          # Markdown temporal (regenerable)
data/08_chroma/            # Vectorstore ChromaDB (regenerable)
data/memoria/              # Memoria del agente (temporal)
.venv/                     # Entorno virtual (regenerable con make setup)
__pycache__/               # Cache de Python (generado)
*.log, *.tmp               # Archivos temporales
```

### 🔑 Variables de Entorno (.env)

El archivo `.env` **NUNCA** se versiona (está en `.gitignore`). Se proporciona `.env.example` como plantilla:

**Variables requeridas:**
- `GEMINI_API_KEY` - Clave de API de Google Gemini
- `GEMINI_MODEL` - Modelo a usar (ej. `gemini-2.5-flash`)
- `YOUTUBE_API_KEY` - Clave de API de YouTube (opcional)

---

## 📖 Cómo Contribuir

### 1. Clonar y Configurar Entorno Local

```bash
git clone https://github.com/tu_usuario/qna_banco_occidente.git
cd qna_banco_occidente
make setup
cp .env.example .env
# Edita .env con tus claves API
```

### 2. Crear una Rama para tu Feature

```bash
git checkout -b feature/mi-feature
```

### 3. Hacer Cambios y Commit

```bash
# Realizar cambios en el código
git add .
git commit -m "feat: descripción clara del cambio"
```

### 4. Verificar Calidad del Código

```bash
make lint
```

### 5. Push y Pull Request

```bash
git push origin feature/mi-feature
# Abre un Pull Request en GitHub
```

### Convenciones

- **Commit Messages:** Usa [Conventional Commits](https://www.conventionalcommits.org/)
  - `feat:` para nuevas funcionalidades
  - `fix:` para correcciones de bugs
  - `docs:` para actualizaciones de documentación
  - `refactor:` para cambios de código sin cambiar funcionalidad

- **Rama principal:** `main` (producción)
- **Rama de desarrollo:** `develop` (desarrollo)

---

## 🧪 Pruebas y Validación

### Validar Instalación

```bash
# Verificar Python
python --version

# Verificar UV
uv --version

# Verificar Git
git status

# Verificar Makefile
make help
```

### Ejecutar Pruebas de Pipeline

```bash
# Ejecutar un paso individual para validar
make crawl

# Revisar logs de ejecución
# Los logs se guardan en la carpeta logs/
```

### Debugging

- Revisa los archivos de log en `logs/`
- Verifica que `.env` está correctamente configurado
- Asegúrate de tener conexión a internet (requerido para scraping y APIs)

---

## 📚 Documentación Adicional

- **Contexto y Módulos:** Ver [contexto/contexto.md](contexto/contexto.md)
- **Configuración de LLM:** Ver `01_codigos/config.py`
- **Prompts del Sistema:** Ver `01_codigos/llm_chains.py`
- **Herramientas del Agente:** Ver `01_codigos/tools.py`

---

## ✨ Evolución del Proyecto

### Línea de Tiempo

| Fase | Objetivo | Estado |
|------|----------|--------|
| **Módulo 1** | Construcción de Base de Conocimiento + Sistema Q&A | ✅ Completado |
| **Módulo 2** | Agente Conversacional con Memoria y Enrutamiento | ✅ Completado |

### Lecciones Aprendidas

- ✅ La precisión mejora significativamente con embeddings semánticos vs. TF-IDF
- ✅ El enrutamiento dinámico (Router) es más eficiente que un sistema monolítico
- ✅ La memoria conversacional es crítica para UX
- ✅ La separación de herramientas estructuradas vs. RAG maximiza precisión
- 🔄 La actualización periódica del corpus es necesaria
- 🔄 Se requiere persistencia de memoria entre sesiones (futuro)

---

## 📞 Soporte y Contacto

Si encuentras problemas o tienes preguntas:

1. **Revisa los logs:** `logs/` o salida de terminal
2. **Verifica .env:** Asegúrate de tener claves API válidas
3. **Consulta la documentación:** [contexto/contexto.md](contexto/contexto.md)
4. **Contacta al equipo:** 
   - Juan Manuel García Ortíz
   - Ricardo Muñoz Bocanegra
   - Deybar Andres Mora Segura
   - Luisa María Candelo Angulo

---

## 📄 Licencia

Este proyecto es académico y se desarrolló para la Universidad Autónoma de Occidente.

**Información del Banco:** Todos los datos extraídos provienen de fuentes públicas del **Banco de Occidente**.

---

**Última actualización:** Mayo de 2026  
**Versión:** 2.0.0 (Módulo 2 Completado)
