"""Estrategias para obtener el número de teléfono destino (Strategy pattern).

Todas exponen la misma interfaz (`get_number`), así que `main.py` puede
cambiar de una a otra sin modificar el resto del bot.
"""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

import keyring

from whatsapp_bot.config import KEYRING_SERVICE, KEYRING_USERNAME


class NumberProvider(ABC):
    """Estrategia para obtener el número de teléfono destino."""

    @abstractmethod
    def get_number(self) -> str: ...


class KeyringNumberProvider(NumberProvider):
    """Lee el número guardado en el almacén de credenciales del sistema
    operativo. Si todavía no existe, lo pide una vez por consola y lo
    guarda para que las próximas ejecuciones no vuelvan a preguntarlo.
    """

    def get_number(self) -> str:
        numero = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
        if numero:
            return numero
        numero = input(
            "Número destino, con código de país y sin signos (ej. 50688889999): "
        ).strip()
        keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, numero)
        return numero


class EnvNumberProvider(NumberProvider):
    """Lee el número desde una variable de entorno. Alternativa a keyring
    para pruebas locales o ejecución en CI, donde no hay almacén de
    credenciales interactivo disponible.
    """

    def __init__(self, variable: str = "WHATSAPP_NUMERO") -> None:
        self._variable = variable

    def get_number(self) -> str:
        numero = os.getenv(self._variable)
        if not numero:
            raise RuntimeError(f"Variable de entorno {self._variable} no definida")
        return numero
