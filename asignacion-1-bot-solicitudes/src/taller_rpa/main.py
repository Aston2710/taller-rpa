"""Entrypoint del bot."""

from __future__ import annotations

import sys

from loguru import logger

from taller_rpa.exceptions import BotException
from taller_rpa.orchestrator import Orchestrator


def main() -> int:
    """Punto de entrada: 0 si la ejecución terminó, 1 si abortó."""
    try:
        Orchestrator().run()
    except BotException as error:
        logger.error("Ejecución abortada: {}", error)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
