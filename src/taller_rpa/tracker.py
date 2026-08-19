"""Detección de archivos ya procesados.

Cada archivo rastreado (de entrada o de salida) es un Value Object inmutable
anclado a su fecha y ruta relativa (`ProcessableFile` y sus dos subclases).
Dos archivos son "el mismo" si comparten esa ruta relativa, sin importar si
uno es de entrada y el otro de salida; eso permite calcular los pendientes
con una simple diferencia de conjuntos: `entradas - salidas`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Self

from taller_rpa.config import INPUT_PATH, OUTPUT_PATH

EXTENSIONES_RASTREADAS: frozenset[str] = frozenset({".csv", ".xlsx"})


@dataclass(frozen=True, eq=False)
class ProcessableFile:
    """Archivo ubicado en `<base>/<year>/<month>/<day>/<nombre>`.

    `eq=False` porque la igualdad no la genera `dataclass` (que compararía
    también el tipo concreto): la definimos a mano en base a `path_dir`, para
    que un `ProcessableInputFile` y su `ProcessableOutputFile` correspondiente
    cuenten como el mismo elemento dentro de un `set`.
    """

    year: int
    month: int
    day: int
    date: date
    path_dir: str
    full_path: Path

    @classmethod
    def desde_ruta(cls, base_dir: Path, full_path: Path) -> Self:
        """Construye el objeto a partir de la ruta de `full_path` relativa a `base_dir`."""
        relativa = full_path.resolve().relative_to(base_dir.resolve())
        year, month, day = (int(parte) for parte in relativa.parts[:3])
        return cls(
            year=year,
            month=month,
            day=day,
            date=date(year, month, day),
            path_dir=relativa.as_posix(),
            full_path=full_path.resolve(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ProcessableFile):
            return NotImplemented
        return self.path_dir == other.path_dir

    def __hash__(self) -> int:
        return hash(self.path_dir)


@dataclass(frozen=True, eq=False)
class ProcessableInputFile(ProcessableFile):
    """Archivo pendiente de envío, del lado `data/input/`."""


@dataclass(frozen=True, eq=False)
class ProcessableOutputFile(ProcessableFile):
    """Archivo ya generado, del lado `data/output/`."""


def get_unprocessed_files(
    input_dir: Path = INPUT_PATH, output_dir: Path = OUTPUT_PATH
) -> list[Path]:
    """Archivos de entrada cuya ruta relativa no tiene aún su espejo en `output_dir`."""
    entradas = _indexar(input_dir, ProcessableInputFile)
    if not entradas:
        return []

    salidas = _indexar(output_dir, ProcessableOutputFile)
    pendientes = entradas - salidas
    return [archivo.full_path for archivo in sorted(pendientes, key=lambda a: a.path_dir)]


def _indexar(base_dir: Path, cls: type[ProcessableFile]) -> set[ProcessableFile]:
    """Recorre `base_dir` recursivamente y construye el `set` de archivos rastreables."""
    if not base_dir.is_dir():
        return set()
    return {
        cls.desde_ruta(base_dir, archivo)
        for archivo in base_dir.rglob("*")
        if _es_rastreable(archivo)
    }


def _es_rastreable(archivo: Path) -> bool:
    """Solo cuentan archivos reales, de extensión soportada y no temporales de Excel."""
    return (
        archivo.is_file()
        and archivo.suffix.lower() in EXTENSIONES_RASTREADAS
        and not archivo.name.startswith("~$")
    )
