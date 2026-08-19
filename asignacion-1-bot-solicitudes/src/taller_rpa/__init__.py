"""Bot RPA de validación y registro de solicitudes."""

from taller_rpa.models import COLUMNAS_ARCHIVO, Persona, Solicitud
from taller_rpa.orchestrator import Orchestrator

__all__ = ["COLUMNAS_ARCHIVO", "Orchestrator", "Persona", "Solicitud"]
