# CLAUDE.md

Standalone PDM project (Python, `src/` layout) — treat this folder as the project root, independent from
`asignacion-1-bot-solicitudes/` elsewhere in this repo.

## What this is

A bot that sends one WhatsApp Web message via Playwright, with a persistent login session so the QR code
is only scanned once (`pdm run bot`, or double-click `run_bot.bat`).

## Architecture

- `config.py` — the only module with path/constant configuration (`SESSION_DIR`, login timeout, keyring
  service/username).
- `number_provider.py` — **Strategy**: `NumberProvider` ABC with `KeyringNumberProvider` (default; reads
  the destination number from the OS credential store, prompting and saving it on first use) and
  `EnvNumberProvider` (reads from an env var, for tests/CI).
- `message.py` — **Builder**: `MensajeBuilder` assembles the message text via chained calls.
- `session.py` — `SessionManager.iniciar_contexto` opens a Playwright `launch_persistent_context` rooted
  at `SESSION_DIR`. Deliberately *not* `storage_state` + `new_context`: WhatsApp Web keeps part of its
  session in IndexedDB, which `storage_state` doesn't capture — the persistent profile directory does.
  Tries `channel="msedge"` first (reuses the Edge that ships with Windows, no extra browser download);
  if that raises a Playwright `Error` (Edge not installed on this machine), it lazily runs
  `playwright install chromium` via subprocess and retries with the default bundled Chromium.
- `pages/whatsapp_page.py` — **Page Object Model**: `WhatsAppWebPage` wraps WhatsApp Web's selectors
  (`abrir`, `esta_logueado`, `esperar_login`, `enviar_mensaje`) so `main.py` never touches DOM details.
- `main.py` — wires the above together; the only orchestration point.

`SESSION_DIR` (`.session/`) holds the live browser profile (cookies/localStorage/IndexedDB) — it's the
actual WhatsApp session and is gitignored at the repo root; never commit it.
