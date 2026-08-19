"""Helpers de rutas."""

from __future__ import annotations

from pathlib import Path

from taller_rpa.config import INPUT_PATH, OUTPUT_PATH


def output_filename(
    input_path: Path, input_dir: Path = INPUT_PATH, output_dir: Path = OUTPUT_PATH
) -> Path:
    """Ruta del archivo de resultados: espejo exacto (misma ruta y nombre, extensión
    incluida) del archivo de entrada dentro de `output_dir`.

    El contenido que se escribe ahí siempre es CSV (ver `reporter.guardar_resultados`);
    la extensión se mantiene igual a la de entrada aunque no sea `.csv` porque el
    tracker (`tracker.get_unprocessed_files`) reconoce un archivo como procesado
    únicamente cuando su ruta relativa es idéntica en ambos lados.
    """
    relativa = input_path.resolve().relative_to(input_dir.resolve())
    return output_dir / relativa


def asegurar_carpeta(carpeta: Path) -> Path:
    """Crea la carpeta (y sus padres) si no existe y la devuelve."""
    carpeta.mkdir(parents=True, exist_ok=True)
    return carpeta
