"""Generación de resultados: CSV, bitácora y resúmenes."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable, Sequence

import pandas as pd
from loguru import logger

from taller_rpa.config import INPUT_PATH, LOGS_PATH, OUTPUT_PATH
from taller_rpa.models import Solicitud
from taller_rpa.utils import asegurar_carpeta, output_filename

FORMATO_LOG = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
    "{module}:{function}:{line} - {message}"
)
SEPARADOR = "=" * 50

COLUMNAS_RESULTADO = [
    "first_name",
    "last_name",
    "email",
    "tipo_solicitud",
    "fecha",
    "prioridad",
    "identificador",
    "estado",
    "resultado",
    "error",
]


@dataclass(frozen=True, slots=True)
class ResumenArchivo:
    """Conteos de un archivo procesado."""

    archivo: str
    filas_leidas: int = 0
    validas: int = 0
    duplicados: int = 0
    errores_validacion: int = 0
    envios_ok: int = 0
    envios_fallidos: int = 0
    omitido: str = ""

    @property
    def fue_omitido(self) -> bool:
        return bool(self.omitido)


def setup_logging(logs_dir: Path = LOGS_PATH, nivel: str = "INFO") -> Path:
    """Configura loguru: consola más un archivo por ejecución."""
    asegurar_carpeta(logs_dir)
    archivo = logs_dir / f"bot_{datetime.now():%Y%m%d_%H%M%S}.log"

    logger.remove()
    logger.add(sys.stderr, format=FORMATO_LOG, level=nivel)
    logger.add(archivo, format=FORMATO_LOG, level="DEBUG", encoding="utf-8")
    return archivo


def guardar_resultados(
    input_path: Path,
    solicitudes: Sequence[Solicitud],
    envios: Sequence[dict],
    errores: Iterable[dict] = (),
    input_dir: Path = INPUT_PATH,
    output_dir: Path = OUTPUT_PATH,
) -> Path:
    """Escribe el CSV de resultados en la ruta espejo de `input_path` bajo `output_dir`."""
    destino = output_filename(input_path, input_dir, output_dir)
    asegurar_carpeta(destino.parent)

    envio_por_id = {envio["identificador"]: envio for envio in envios}
    filas = [_fila_enviada(s, envio_por_id.get(s.identificador, {})) for s in solicitudes]
    filas.extend(_fila_rechazada(error) for error in errores)

    pd.DataFrame(filas, columns=COLUMNAS_RESULTADO).to_csv(
        destino, index=False, encoding="utf-8-sig"
    )
    logger.info("Resultados guardados en: {}", destino)
    return destino


def _fila_enviada(solicitud: Solicitud, envio: dict) -> dict:
    return {
        "first_name": solicitud.persona.first_name,
        "last_name": solicitud.persona.last_name,
        "email": solicitud.persona.email,
        "tipo_solicitud": solicitud.tipo_solicitud,
        "fecha": solicitud.fecha.isoformat(),
        "prioridad": solicitud.prioridad,
        "identificador": solicitud.identificador,
        "estado": solicitud.estado,
        "resultado": envio.get("resultado", ""),
        "error": envio.get("error", ""),
    }


def _fila_rechazada(error: dict) -> dict:
    """Fila que no llegó al formulario: error de validación o duplicado."""
    motivo = error.get("motivo", "validacion")
    detalle = f"{error.get('campo', '')}: {error.get('error', '')}".strip(": ")
    if "fila" in error:
        detalle = f"fila {error['fila']} - {detalle}"
    return {
        "first_name": "",
        "last_name": "",
        "email": error.get("email", ""),
        "tipo_solicitud": "",
        "fecha": "",
        "prioridad": "",
        "identificador": error.get("identificador", ""),
        "estado": "",
        "resultado": motivo if motivo == "duplicado" else f"error_{motivo}",
        "error": detalle,
    }


def resumen_archivo(resumen: ResumenArchivo) -> None:
    """Imprime el resumen de un archivo."""
    logger.info(SEPARADOR)
    logger.info("RESUMEN: {}", resumen.archivo)
    if resumen.fue_omitido:
        logger.warning("  Omitido: {}", resumen.omitido)
    logger.info("  Total filas leídas:    {}", resumen.filas_leidas)
    logger.info("  Válidas:               {}", resumen.validas)
    logger.info("  Duplicados:            {}", resumen.duplicados)
    logger.info("  Errores validación:    {}", resumen.errores_validacion)
    logger.info("  Envíos exitosos:       {}", resumen.envios_ok)
    logger.info("  Envíos fallidos:       {}", resumen.envios_fallidos)
    logger.info(SEPARADOR)


def resumen_global(resumenes: Sequence[ResumenArchivo]) -> None:
    """Imprime el resumen de toda la ejecución."""
    omitidos = [resumen for resumen in resumenes if resumen.fue_omitido]

    logger.info(SEPARADOR)
    logger.info("RESUMEN GLOBAL DE EJECUCIÓN")
    logger.info("  Archivos totales:      {}", len(resumenes))
    logger.info("  Archivos procesados:   {}", len(resumenes) - len(omitidos))
    logger.info("  Archivos omitidos:     {}", len(omitidos))
    logger.info(SEPARADOR)
