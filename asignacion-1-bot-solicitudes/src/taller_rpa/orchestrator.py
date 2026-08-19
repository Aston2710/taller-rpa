"""Orquestador del pipeline.

Solo decide el orden de los pasos y qué hacer ante un fallo; las reglas de
negocio viven en `services`. Los colaboradores se reciben por parámetro para
poder sustituirlos en pruebas.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from taller_rpa import services
from taller_rpa.config import INPUT_PATH, OUTPUT_PATH
from taller_rpa.exceptions import BotException, ValidationFailedError
from taller_rpa.readers import leer_archivo
from taller_rpa.reporter import (
    ResumenArchivo,
    guardar_resultados,
    resumen_archivo,
    resumen_global,
    setup_logging,
)
from taller_rpa.submitter import RESULTADO_OK, WebSubmitter
from taller_rpa.tracker import get_unprocessed_files


class Orchestrator:
    """Coordina el pipeline completo sobre los archivos pendientes."""

    def __init__(
        self,
        input_dir: Path = INPUT_PATH,
        output_dir: Path = OUTPUT_PATH,
        submitter: WebSubmitter | None = None,
        configurar_logging: bool = True,
    ) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.submitter = submitter or WebSubmitter()
        self.configurar_logging = configurar_logging

    def run(self) -> list[ResumenArchivo]:
        """Ejecuta el proceso completo y devuelve un resumen por archivo."""
        if self.configurar_logging:
            setup_logging(self.output_dir / "logs")

        pendientes = get_unprocessed_files(self.input_dir, self.output_dir)
        if not pendientes:
            logger.info("No hay archivos pendientes por procesar.")
            resumen_global([])
            return []

        logger.info("Archivos pendientes: {}", len(pendientes))
        resumenes = [self._procesar(archivo) for archivo in pendientes]

        resumen_global(resumenes)
        return resumenes

    def _procesar(self, archivo: Path) -> ResumenArchivo:
        """Un archivo con problemas se omite; la ejecución continúa."""
        logger.info("Procesando: {}", archivo.name)
        try:
            resumen = self._pipeline(archivo)
        except BotException as error:
            logger.error("  Omitido {}: {}", archivo.name, error)
            resumen = ResumenArchivo(archivo=archivo.name, omitido=str(error))
        resumen_archivo(resumen)
        return resumen

    def _pipeline(self, archivo: Path) -> ResumenArchivo:
        df = leer_archivo(archivo)

        faltantes = services.columnas_faltantes(df)
        if faltantes:
            raise ValidationFailedError(
                f"faltan columnas obligatorias: {', '.join(faltantes)}"
            )

        validos, errores = services.validate(df)
        logger.info("  Validación: {} válidos, {} errores", len(validos), len(errores))

        unicos, duplicados = services.deduplicate(validos)
        if duplicados:
            logger.warning("  Duplicados: {}", len(duplicados))

        grupos = services.classify(unicos)
        logger.info("  Clasificación: {} tipo(s)", len(grupos))
        for tipo, solicitudes in sorted(grupos.items()):
            logger.debug("    {}: {}", tipo, len(solicitudes))

        envios = self.submitter.submit(unicos)
        exitosos = sum(envio["resultado"] == RESULTADO_OK for envio in envios)
        logger.info("  Envíos: {} OK, {} fallidos", exitosos, len(envios) - exitosos)

        guardar_resultados(
            archivo, unicos, envios, [*errores, *duplicados], self.input_dir, self.output_dir
        )

        return ResumenArchivo(
            archivo=archivo.name,
            filas_leidas=len(df),
            validas=len(validos),
            duplicados=len(duplicados),
            errores_validacion=len(errores),
            envios_ok=exitosos,
            envios_fallidos=len(envios) - exitosos,
        )
