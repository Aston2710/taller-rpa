# whatsapp-bot-rpa

Bot que envía un mensaje por WhatsApp Web usando Playwright, con sesión persistente
(no vuelve a pedir el QR en ejecuciones posteriores).

## Patrones aplicados

- **Builder** (`message.py`): arma el texto del mensaje paso a paso.
- **Strategy** (`number_provider.py`): forma de obtener el número destino
  intercambiable (`KeyringNumberProvider` por defecto, `EnvNumberProvider` como
  alternativa) sin que `main.py` conozca la implementación concreta.
- **Page Object Model** (`pages/whatsapp_page.py`): encapsula los selectores y
  acciones de la UI de WhatsApp Web.

## Instalación y ejecución

Basta con requerir PDM instalado en la máquina; `run_bot.bat` se encarga del resto (`pdm install` es
idempotente: si ya está todo instalado, no vuelve a descargar nada):

```bash
pdm install
pdm run bot
```

o simplemente doble click en `run_bot.bat`, incluso en un clon recién descargado del repo.

El bot usa el **Edge** que Windows ya trae instalado (no descarga un motor de navegador aparte). Si esa
máquina no tiene Edge, instala **Chromium** automáticamente la primera vez (vía Playwright) y lo usa como
respaldo — no hace falta ningún paso manual adicional en ningún caso.

- **Primera ejecución**: no hay número guardado → lo pide por consola y lo
  guarda en el almacén de credenciales del sistema operativo (`keyring`). Se
  abre el navegador y hay que escanear el QR con el teléfono (WhatsApp >
  Dispositivos vinculados > Vincular dispositivo).
- **Siguientes ejecuciones**: reutiliza el número guardado y el perfil de
  navegador en `.session/`, así que no vuelve a pedir QR.

### Cambiar el número destino

```bash
pdm run reset-number
```

Borra el número guardado en keyring; la próxima vez que corras `pdm run bot` (o `run_bot.bat`) lo vuelve a
pedir por consola.

## Sobre la persistencia de sesión

WhatsApp Web guarda parte de sus claves de sesión en IndexedDB, no solo en
cookies/localStorage. Por eso este bot no usa `storage_state` de Playwright
(que no captura IndexedDB), sino `launch_persistent_context`, que persiste el
perfil completo del navegador en `.session/`.

**`.session/` nunca se sube al repositorio** (ver `.gitignore`): esa carpeta
es, en la práctica, la sesión activa de WhatsApp de quien la generó.
