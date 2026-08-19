# asignacion-1-bot-solicitudes

Bot RPA que lee solicitudes desde `data/input/` (CSV/Excel, organizadas por fecha), las valida y
deduplica, y las "envía" a un formulario web simulado. Detalle de arquitectura en [`CLAUDE.md`](CLAUDE.md).

## Uso

```bash
pdm install
pdm run bot            # ejecuta el bot
pdm run test           # corre la suite de tests
```

Config vía `.env` (ver `.env.example`): `INPUT_PATH`, `OUTPUT_PATH`, `WEB_FORM_URL`, `HEADLESS`.

Resultados y logs quedan en `data/output/`.
