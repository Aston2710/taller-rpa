"""Lógica de negocio: validación, deduplicación y clasificación.

Funciones puras (DataFrame/listas dentro, listas fuera): no tocan disco ni red.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Iterable

import pandas as pd
from pydantic import ValidationError

from taller_rpa.models import COLUMNAS_ARCHIVO, Solicitud

PRIMERA_FILA_DATOS = 2  # la fila 1 son los encabezados, como se ve en Excel


def columnas_faltantes(df: pd.DataFrame) -> list[str]:
    """Columnas del contrato que el archivo no trae."""
    return [columna for columna in COLUMNAS_ARCHIVO if columna not in df.columns]


def validate(df: pd.DataFrame) -> tuple[list[Solicitud], list[dict]]:
    """Convierte cada fila en `Solicitud`; las que fallan se reportan como error."""
    validos: list[Solicitud] = []
    errores: list[dict] = []

    for numero_fila, fila in enumerate(
        df.to_dict(orient="records"), start=PRIMERA_FILA_DATOS
    ):
        try:
            validos.append(Solicitud.desde_fila(fila))
        except ValidationError as error:
            errores.extend(_detallar(numero_fila, fila, error))

    return validos, errores


def _detallar(numero_fila: int, fila: dict, error: ValidationError) -> list[dict]:
    """Traduce los errores de Pydantic a diccionarios legibles."""
    return [
        {
            "fila": numero_fila,
            "identificador": str(fila.get("identificador", "")),
            "email": str(fila.get("Email", "")),
            "campo": ".".join(str(parte) for parte in detalle["loc"]) or "fila",
            "error": detalle["msg"],
            "motivo": "validacion",
        }
        for detalle in error.errors()
    ]


CLAVES: dict[str, Callable[[Solicitud], str]] = {
    "email": lambda solicitud: solicitud.persona.email,
    "identificador": lambda solicitud: solicitud.identificador,
}


def deduplicate(
    validos: Iterable[Solicitud], key: str = "email"
) -> tuple[list[Solicitud], list[dict]]:
    """Conserva la primera aparición de cada clave; el resto queda como duplicado."""
    obtener_clave = CLAVES.get(key)
    if obtener_clave is None:
        raise ValueError(f"Clave de deduplicación desconocida: {key!r}")

    vistos: set[str] = set()
    unicos: list[Solicitud] = []
    duplicados: list[dict] = []

    for solicitud in validos:
        clave = obtener_clave(solicitud)
        if clave in vistos:
            duplicados.append(
                {
                    "identificador": solicitud.identificador,
                    "email": solicitud.persona.email,
                    "campo": key,
                    "error": f"duplicado de {clave!r}",
                    "motivo": "duplicado",
                }
            )
            continue
        vistos.add(clave)
        unicos.append(solicitud)

    return unicos, duplicados


def classify(
    unicos: Iterable[Solicitud], by: str = "tipo_solicitud"
) -> dict[str, list[Solicitud]]:
    """Agrupa las solicitudes por el campo indicado."""
    grupos: dict[str, list[Solicitud]] = defaultdict(list)
    for solicitud in unicos:
        valor = getattr(solicitud, by, None)
        if valor is None:
            raise ValueError(f"Campo de clasificación desconocido: {by!r}")
        grupos[str(valor)].append(solicitud)
    return dict(grupos)
