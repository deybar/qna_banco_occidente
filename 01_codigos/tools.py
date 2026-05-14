import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import BANCO_INFO_JSON

from langchain_core.tools import tool
from llm_chains import ask_question


def _load_banco_info() -> dict:
    if not os.path.exists(BANCO_INFO_JSON):
        raise FileNotFoundError(
            f"Archivo de datos estructurados no encontrado: {BANCO_INFO_JSON}"
        )
    with open(BANCO_INFO_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


_BANCO_INFO = _load_banco_info()


def _format_dict_section(seccion: dict, titulo: str) -> str:
    lines = [f"**{titulo}**"]
    for k, v in seccion.items():
        if isinstance(v, bool):
            v = "Sí" if v else "No"
        label = k.replace("_", " ").capitalize()
        lines.append(f"- {label}: {v}")
    return "\n".join(lines)


def _format_sucursales(sucursales: list, ciudad_filtro: str = None) -> str:
    if ciudad_filtro:
        ciudad_filtro = ciudad_filtro.lower().strip()
        filtradas = [s for s in sucursales if ciudad_filtro in s["ciudad"].lower()]
    else:
        filtradas = sucursales

    if not filtradas:
        return f"No se encontraron sucursales para '{ciudad_filtro}' en el registro."

    lines = [f"**Sucursales{' en ' + ciudad_filtro.title() if ciudad_filtro else ''}**"]
    for s in filtradas:
        lines.append(
            f"- {s['tipo']} ({s['ciudad']}): {s['direccion']} | Tel: {s['telefono']}"
        )
    return "\n".join(lines)


@tool
def consultar_corpus_documental(consulta: str) -> str:
    """
    Útil para responder preguntas ABIERTAS sobre el Banco de Occidente que requieren
    explicaciones, descripciones o información detallada extraída de la base de
    conocimiento documental del banco. Úsala para preguntas como:
    - ¿Qué tarjetas de crédito ofrece el banco?
    - ¿Cuáles son los requisitos del crédito hipotecario?
    - ¿Qué beneficios tiene la cuenta de ahorros?
    - ¿Cómo funciona la banca empresarial?
    - ¿Qué es el Banco de Occidente? ¿Cuál es su misión?
    - Cualquier pregunta sobre productos, servicios, procesos o información
      corporativa que requiera contexto narrativo.

    El argumento 'consulta' debe ser la pregunta original del usuario, en español.
    Esta herramienta NO sirve para datos puntuales como teléfonos u horarios.
    """
    return ask_question(consulta)


@tool
def consultar_datos_estructurados(tipo: str, ciudad: str = "") -> str:
    """
    Útil para datos PRECISOS Y FIJOS del Banco de Occidente: teléfonos, horarios
    de atención, NIT, sedes, direcciones, redes sociales, información corporativa
    básica. Úsala para preguntas como:
    - ¿Cuál es el teléfono de servicio al cliente?
    - ¿En qué horario atienden las sucursales?
    - ¿Cuál es el NIT del banco?
    - ¿En qué ciudades hay sucursales?
    - Listar las sucursales en Cali (o Bogotá, Medellín, etc.)
    - ¿Cuáles son las redes sociales del banco?
    - ¿Cómo bloqueo mi tarjeta?
    - ¿Cómo recupero mi clave?

    Argumentos válidos para 'tipo':
    - 'telefono'        → Líneas de atención telefónica
    - 'horario'         → Horarios de sucursales y canales
    - 'corporativo'     → NIT, razón social, fundación, sede principal
    - 'sucursales'      → Listado de sucursales (opcional: filtrar por ciudad)
    - 'redes_sociales'  → URLs de redes sociales oficiales
    - 'canales_digitales' → App, portal web, banca empresarial
    - 'normativo'       → Vigilancia, Fogafín, defensor del consumidor
    - 'preguntas_directas' → Tutoriales rápidos (bloqueo de tarjeta, claves, etc.)

    El argumento 'ciudad' solo aplica para tipo='sucursales' y es opcional.
    """
    tipo = tipo.lower().strip()

    mapeo = {
        "telefono":          ("lineas_atencion",       "Líneas de atención"),
        "telefonos":         ("lineas_atencion",       "Líneas de atención"),
        "horario":           ("horarios_atencion",     "Horarios de atención"),
        "horarios":          ("horarios_atencion",     "Horarios de atención"),
        "corporativo":       ("informacion_corporativa", "Información corporativa"),
        "corporativa":       ("informacion_corporativa", "Información corporativa"),
        "redes_sociales":    ("redes_sociales",        "Redes sociales oficiales"),
        "redes":             ("redes_sociales",        "Redes sociales oficiales"),
        "canales_digitales": ("canales_digitales",     "Canales digitales"),
        "canales":           ("canales_digitales",     "Canales digitales"),
        "normativo":         ("datos_normativos",      "Información normativa"),
        "normativa":         ("datos_normativos",      "Información normativa"),
        "preguntas_directas": ("preguntas_frecuentes_directas", "Procesos directos"),
    }

    if tipo == "sucursales":
        return _format_sucursales(_BANCO_INFO["sucursales_principales"], ciudad)

    if tipo not in mapeo:
        return (
            f"Tipo de consulta '{tipo}' no reconocido. Tipos válidos: "
            "telefono, horario, corporativo, sucursales, redes_sociales, "
            "canales_digitales, normativo, preguntas_directas."
        )

    key, titulo = mapeo[tipo]
    seccion = _BANCO_INFO.get(key, {})

    if not seccion:
        return f"No hay datos disponibles en la sección '{titulo}'."

    return _format_dict_section(seccion, titulo)


TOOLS = [consultar_corpus_documental, consultar_datos_estructurados]
