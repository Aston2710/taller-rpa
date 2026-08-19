"""Constantes de configuración del bot."""

from __future__ import annotations

from pathlib import Path

RAIZ_PROYECTO = Path(__file__).resolve().parents[2]

# Perfil persistente del navegador (cookies + localStorage + IndexedDB).
# Se ignora en git (ver .gitignore): contiene la sesión activa de WhatsApp.
SESSION_DIR = RAIZ_PROYECTO / ".session"

# Tiempo máximo de espera para que la persona escanee el QR.
LOGIN_TIMEOUT_MS = 120_000

KEYRING_SERVICE = "whatsapp-bot-rpa"
KEYRING_USERNAME = "numero_destino"

# Capturas de pantalla y trazas de diagnóstico del envío. Contiene el número
# destino y el mensaje: se ignora en git.
DEBUG_DIR = RAIZ_PROYECTO / "debug"
