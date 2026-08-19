"""Configuración del bot desde `.env`.

Único módulo que lee variables de entorno; el resto importa estas constantes.
Los defaults son rutas relativas, ancladas a la raíz del proyecto para que el
bot funcione igual sin importar desde qué carpeta se lance.
"""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

load_dotenv(RAIZ_PROYECTO / ".env")

_VALORES_VERDADEROS = frozenset({"1", "true", "yes", "y", "on", "si", "sí"})


def _ruta(clave: str, default: str) -> Path:
    ruta = Path(os.getenv(clave) or default).expanduser()
    return ruta if ruta.is_absolute() else RAIZ_PROYECTO / ruta


def _booleano(clave: str, default: str) -> bool:
    return (os.getenv(clave) or default).strip().lower() in _VALORES_VERDADEROS


INPUT_PATH: Path = _ruta("INPUT_PATH", "data/input")
OUTPUT_PATH: Path = _ruta("OUTPUT_PATH", "data/output")
WEB_FORM_URL: str = os.getenv("WEB_FORM_URL") or "https://example.com/form"
HEADLESS: bool = _booleano("HEADLESS", "true")

LOGS_PATH: Path = OUTPUT_PATH / "logs"


def leer_config() -> dict[str, object]:
    """Devuelve la configuración vigente (útil para diagnóstico y logs)."""
    return {
        "INPUT_PATH": INPUT_PATH,
        "OUTPUT_PATH": OUTPUT_PATH,
        "WEB_FORM_URL": WEB_FORM_URL,
        "HEADLESS": HEADLESS,
    }
