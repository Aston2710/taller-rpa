"""Punto de entrada del bot."""

from __future__ import annotations

from playwright.sync_api import sync_playwright

from whatsapp_bot.config import LOGIN_TIMEOUT_MS
from whatsapp_bot.message import MensajeBuilder
from whatsapp_bot.number_provider import KeyringNumberProvider
from whatsapp_bot.pages.whatsapp_page import WhatsAppWebPage
from whatsapp_bot.session import SessionManager

PATRONES = ["Builder", "Page Object Model", "Strategy"]


def main() -> None:
    numero = KeyringNumberProvider().get_number()
    texto = MensajeBuilder().tarea_finalizada().con_patrones(PATRONES).build()

    with sync_playwright() as playwright:
        contexto = SessionManager().iniciar_contexto(playwright)
        pagina = contexto.pages[0] if contexto.pages else contexto.new_page()
        whatsapp = WhatsAppWebPage(pagina)

        whatsapp.abrir()
        if not whatsapp.esta_logueado():
            whatsapp.esperar_login(LOGIN_TIMEOUT_MS)

        whatsapp.enviar_mensaje(numero, texto)
        contexto.close()


if __name__ == "__main__":
    main()
