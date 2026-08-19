"""Borra el número guardado en keyring para que el bot lo vuelva a pedir."""

from __future__ import annotations

import keyring
import keyring.errors

from whatsapp_bot.config import KEYRING_SERVICE, KEYRING_USERNAME


def main() -> None:
    try:
        keyring.delete_password(KEYRING_SERVICE, KEYRING_USERNAME)
        print("Número borrado de keyring. La próxima ejecución del bot lo va a volver a pedir.")
    except keyring.errors.PasswordDeleteError:
        print("No había ningún número guardado.")


if __name__ == "__main__":
    main()
