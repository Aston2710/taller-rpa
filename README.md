# taller-rpa

Repositorio con dos asignaciones del taller de RPA. Cada una es un **proyecto PDM independiente**, con su
propio `pyproject.toml`, `pdm.lock` y entorno virtual — no comparten dependencias ni código entre sí. Los
enunciados originales están en [`asignaciones/`](asignaciones/).

```
taller-rpa/
  asignaciones/                     enunciados de ambas asignaciones
  asignacion-1-bot-solicitudes/     bot de procesamiento de solicitudes (CSV/Excel)
  asignacion-2-bot-whatsapp/        bot de WhatsApp Web con Playwright
```

Requisito común: [PDM](https://pdm-project.org/) instalado.

## asignacion-1-bot-solicitudes

Lee solicitudes desde `data/input/`, las valida y deduplica, y las "envía" a un formulario web (simulado).
Detalle de arquitectura en [`asignacion-1-bot-solicitudes/CLAUDE.md`](asignacion-1-bot-solicitudes/CLAUDE.md).

```bash
cd asignacion-1-bot-solicitudes
pdm install
pdm run bot            # ejecuta el bot
pdm run test           # corre la suite de tests
```

Config vía `.env` en esa misma carpeta (ver `.env.example`).

## asignacion-2-bot-whatsapp

Envía un mensaje por WhatsApp Web con Playwright. La sesión persiste entre ejecuciones (no vuelve a pedir
el QR). Detalle en [`asignacion-2-bot-whatsapp/README.md`](asignacion-2-bot-whatsapp/README.md).

```bash
cd asignacion-2-bot-whatsapp
pdm install
pdm run playwright install chromium
pdm run bot             # o doble click en run_bot.bat
```

- **Primera ejecución**: pide el número por consola (se guarda en `keyring`) y hay que escanear el QR con
  el teléfono.
- **Siguientes ejecuciones**: no vuelve a pedir número ni QR.

La carpeta `.session/` que se genera ahí es la sesión activa de WhatsApp — está en `.gitignore` y nunca
debe subirse al repo.
