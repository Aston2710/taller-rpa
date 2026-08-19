"""Fixtures compartidas: filas base y carpetas temporales."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from taller_rpa.models import COLUMNAS_ARCHIVO

RAIZ_PROYECTO = Path(__file__).resolve().parents[1]
ENTRADA_TALLER = RAIZ_PROYECTO / "tests" / "fixtures"

FILA_BASE: dict[str, str] = {
    "First Name": "Ana",
    "Last Name": "Rodríguez",
    "Company Name": "TechCorp",
    "Role in Company": "Analyst",
    "Address": "Calle 63, Ciudad",
    "Email": "ana.rodriguez@example.com",
    "Phone Number": "+1-555-4657",
    "tipo_solicitud": "consulta",
    "fecha": "2024-01-01",
    "prioridad": "baja",
    "identificador": "SOL-2024000",
    "descripcion": "Descripción de la solicitud 1",
    "estado": "pendiente",
}


@pytest.fixture
def fila() -> dict[str, str]:
    """Fila válida; los tests la modifican para provocar cada error."""
    return dict(FILA_BASE)


def hacer_df(*filas: dict[str, str]) -> pd.DataFrame:
    """DataFrame con las columnas del contrato, en el mismo orden del archivo."""
    return pd.DataFrame(list(filas), columns=COLUMNAS_ARCHIVO, dtype=str)
