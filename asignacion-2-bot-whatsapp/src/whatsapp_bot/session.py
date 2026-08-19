"""Sesión persistente de WhatsApp Web.

Usamos `launch_persistent_context` (perfil completo en disco) en vez de
`storage_state` + `new_context`: `storage_state` solo guarda cookies y
localStorage, y WhatsApp Web guarda parte de sus claves de sesión en
IndexedDB, que `storage_state` no captura. El perfil persistente sí
conserva cookies, localStorage e IndexedDB entre ejecuciones, que es lo
que evita tener que volver a escanear el QR.

Preferimos el canal "msedge" para reutilizar el Edge que Windows ya trae
instalado, en vez de descargar un motor de navegador aparte. Si esa máquina
no tiene Edge, instalamos Chromium bajo demanda (una sola vez) y lo usamos
como respaldo.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from playwright.sync_api import BrowserContext, Error as PlaywrightError, Playwright

from whatsapp_bot.config import SESSION_DIR


class SessionManager:
    """Abre (o crea) el contexto de navegador con perfil persistente."""

    def __init__(self, session_dir: Path = SESSION_DIR) -> None:
        self._session_dir = session_dir

    def ya_existe(self) -> bool:
        return self._session_dir.exists() and any(self._session_dir.iterdir())

    def iniciar_contexto(self, playwright: Playwright) -> BrowserContext:
        self._session_dir.mkdir(parents=True, exist_ok=True)
        try:
            return self._lanzar(playwright, channel="msedge")
        except PlaywrightError:
            print("Edge no está disponible en esta máquina, se instalará/usará Chromium.")
            self._instalar_chromium()
            return self._lanzar(playwright, channel=None)

    def _lanzar(self, playwright: Playwright, channel: str | None) -> BrowserContext:
        return playwright.chromium.launch_persistent_context(
            user_data_dir=str(self._session_dir),
            headless=False,
            channel=channel,
        )

    @staticmethod
    def _instalar_chromium() -> None:
        subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            check=True,
        )
