"""Envío de solicitudes al formulario web.

Hoy es un stub que simula el registro. Cuando entre Playwright, solo cambia
`_registrar`: el resto del pipeline no se entera.
"""

from __future__ import annotations

from typing import Iterable

from loguru import logger

from taller_rpa.config import HEADLESS, WEB_FORM_URL
from taller_rpa.exceptions import SubmissionError
from taller_rpa.models import Solicitud

RESULTADO_OK = "registrado"
RESULTADO_ERROR = "error_envio"


class WebSubmitter:
    """Registra solicitudes, una por una, en el formulario web."""

    def __init__(self, form_url: str = WEB_FORM_URL, headless: bool = HEADLESS) -> None:
        self.form_url = form_url
        self.headless = headless

    def submit(self, solicitudes: Iterable[Solicitud]) -> list[dict]:
        """Devuelve un dict por solicitud: identificador, resultado y error."""
        resultados: list[dict] = []
        for solicitud in solicitudes:
            try:
                self._registrar(solicitud)
            except SubmissionError as error:
                logger.error("  Falló {}: {}", solicitud.identificador, error)
                resultado = {"resultado": RESULTADO_ERROR, "error": str(error)}
            else:
                resultado = {"resultado": RESULTADO_OK, "error": ""}
            resultados.append({"identificador": solicitud.identificador, **resultado})
        return resultados

    def _registrar(self, solicitud: Solicitud) -> None:
        """Llena y envía el formulario. Por ahora solo simula el registro."""
        logger.debug(
            "Simulando envío de {} ({}) a {}",
            solicitud.identificador,
            solicitud.persona.email,
            self.form_url,
        )
