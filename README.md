# Sistema Q&A Banco de Occidente

Este proyecto forma parte de la **Maestría en IA y Ciencia de Datos** de la **Universidad Autónoma de Occidente**.

## Contexto Académico
- **Materia:** Técnicas Avanzadas de IA
- **Módulo:** 1
- **Institución:** Universidad Autónoma de Occidente (UAO)

## Estructura de Datos y Entregables
De acuerdo con la rúbrica del proyecto, se ha definido la siguiente estrategia de gestión de archivos:

### ✅ Archivos Versionados (Entregables)
Estos archivos son fundamentales para la evaluación y **SÍ** se encuentran en el repositorio:
- `data/corpus_master.md`: Base de conocimiento generada para el sistema Q&A.
- `data/urls.txt`: Evidencia de las fuentes procesadas mediante scraping.

### ❌ Archivos Ignorados (Regenerables)
Para mantener el repositorio limpio, los siguientes datos intermedios no se suben, ya que pueden ser regenerados ejecutando el pipeline completo:
- Documentos en crudo (`data/raw_docs/`)
- Documentos limpios (`data/clean_docs/`)
- Conversiones a Markdown (`data/markdown_docs/`)
- Fragmentos de texto (`data/chunks.json`)

## Seguridad
- Las credenciales y secretos (archivos `.env`) están estrictamente excluidos del repositorio.
- Se proporciona un archivo `.env.example` como plantilla para configurar las variables de entorno necesarias.
