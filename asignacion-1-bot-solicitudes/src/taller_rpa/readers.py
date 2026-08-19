"""Lectura de archivos de entrada (Strategy + Factory).

Cada formato es una estrategia intercambiable; agregar uno nuevo es registrar
una clase, sin tocar al resto del pipeline (open/closed).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

import pandas as pd

from taller_rpa.exceptions import FileReadError

EXTENSIONES_SOPORTADAS: tuple[str, ...] = (".csv", ".xlsx", ".xls")


class BaseReader(ABC):
    """Estrategia de lectura: convierte un archivo en un DataFrame de texto."""

    def read(self, filepath: Path) -> pd.DataFrame:
        """Lee el archivo y normaliza el DataFrame resultante."""
        if not filepath.is_file():
            raise FileReadError(f"El archivo no existe: {filepath}")
        try:
            df = self._read(filepath)
        except FileReadError:
            raise
        except Exception as error:  # noqa: BLE001 - se traduce a error de dominio
            raise FileReadError(f"No se pudo leer {filepath.name}: {error}") from error
        return _normalizar_dataframe(df)

    @abstractmethod
    def _read(self, filepath: Path) -> pd.DataFrame:
        """Lectura concreta de cada formato."""


class CsvReader(BaseReader):
    """Lee archivos `.csv` (UTF-8 con BOM tolerado)."""

    def _read(self, filepath: Path) -> pd.DataFrame:
        return pd.read_csv(filepath, dtype=str, encoding="utf-8-sig", keep_default_na=False)


class XlsxReader(BaseReader):
    """Lee archivos `.xlsx` / `.xls` con openpyxl."""

    def _read(self, filepath: Path) -> pd.DataFrame:
        return pd.read_excel(filepath, dtype=str, engine="openpyxl", keep_default_na=False)


_LECTORES: dict[str, type[BaseReader]] = {
    ".csv": CsvReader,
    ".xlsx": XlsxReader,
    ".xls": XlsxReader,
}


def reader_factory(extension: str) -> BaseReader:
    """Devuelve el lector adecuado para la extensión indicada."""
    lector = _LECTORES.get(extension.lower())
    if lector is None:
        raise FileReadError(
            f"Extensión no soportada: {extension!r}. "
            f"Soportadas: {', '.join(EXTENSIONES_SOPORTADAS)}"
        )
    return lector()


def leer_archivo(filepath: Path) -> pd.DataFrame:
    """Atajo: elige el lector por extensión y lee el archivo."""
    return reader_factory(filepath.suffix).read(filepath)


def _normalizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Recorta encabezados y celdas, y descarta filas totalmente vacías."""
    df = df.rename(columns=lambda columna: str(columna).strip())
    df = df.apply(lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else v))
    vacias = df.map(lambda v: v == "" or pd.isna(v)).all(axis=1)
    return df.loc[~vacias].reset_index(drop=True)
