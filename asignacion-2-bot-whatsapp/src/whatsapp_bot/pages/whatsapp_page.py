"""Page Object Model de WhatsApp Web.

Encapsula selectores y acciones de la UI para que el resto del bot no
dependa de detalles de la página (que WhatsApp cambia con frecuencia).
"""

from __future__ import annotations

import re
from urllib.parse import quote

from playwright.sync_api import Page

from whatsapp_bot.config import DEBUG_DIR

_URL_BASE = "https://web.whatsapp.com"
_CHAT_LIST_TESTID = "chat-list"
_COMPOSE_BOX_TESTID = "conversation-compose-box-input"


class WhatsAppWebPage:
    """Acciones disponibles sobre la página de WhatsApp Web."""

    def __init__(self, page: Page) -> None:
        self._page = page

    def abrir(self) -> None:
        self._page.goto(_URL_BASE)

    def esta_logueado(self, timeout_ms: int = 5_000) -> bool:
        try:
            self._page.get_by_test_id(_CHAT_LIST_TESTID).wait_for(timeout=timeout_ms)
            return True
        except Exception:
            return False

    def esperar_login(self, timeout_ms: int) -> None:
        print(
            "Escaneá el QR con tu teléfono: WhatsApp > Dispositivos vinculados "
            "> Vincular dispositivo"
        )
        self._page.get_by_test_id(_CHAT_LIST_TESTID).wait_for(timeout=timeout_ms)

    def enviar_mensaje(self, numero: str, texto: str) -> None:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)

        url = f"{_URL_BASE}/send?phone={numero}&text={quote(texto)}"
        self._page.goto(url)
        self._page.screenshot(path=str(DEBUG_DIR / "1_despues_de_goto.png"))

        salto = self._saltar_pantalla_intermedia()
        print(f"[debug] pantalla intermedia detectada y saltada: {salto}")
        self._page.screenshot(path=str(DEBUG_DIR / "2_despues_de_intermedia.png"))

        cuadro_texto = self._page.get_by_test_id(_COMPOSE_BOX_TESTID)
        cuadro_texto.wait_for(timeout=30_000)
        print(f"[debug] texto en el cuadro antes de Enter: {cuadro_texto.inner_text()!r}")
        self._page.screenshot(path=str(DEBUG_DIR / "3_antes_de_enter.png"))

        cuadro_texto.click()
        self._page.keyboard.press("Enter")
        self._page.wait_for_timeout(1_500)

        print(f"[debug] texto en el cuadro despues de Enter: {cuadro_texto.inner_text()!r}")
        self._page.screenshot(path=str(DEBUG_DIR / "4_despues_de_enter.png"))

    def _saltar_pantalla_intermedia(self) -> bool:
        """Si el número no está en los contactos, WhatsApp muestra una
        pantalla previa con un botón "Continuar para conversar" antes de
        abrir el chat. La saltamos si aparece; si no, seguimos de largo.
        """
        boton_continuar = self._page.get_by_role(
            "button", name=re.compile("continue to chat|continuar para conversar", re.I)
        )
        try:
            boton_continuar.wait_for(timeout=8_000)
            boton_continuar.click()
            return True
        except Exception as error:
            print(f"[debug] sin pantalla intermedia ({type(error).__name__})")
            return False
