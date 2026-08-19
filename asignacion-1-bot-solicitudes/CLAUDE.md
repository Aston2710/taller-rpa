# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An RPA (robotic process automation) bot, written as a school/workshop exercise (`taller-rpa`). It reads
"solicitud" (request) records from CSV/Excel files, validates and deduplicates them, groups them by type,
and "submits" each one to a web form (currently a stubbed simulation — see `submitter.py`). Results and a
per-run log are written to `data/output/`.

## Commands

Package management is via **pdm** (Python 3.13+, `src/` layout).

```bash
pdm install               # install dependencies into .venv
pdm run bot               # run the bot (python -m taller_rpa.main)
pdm run test              # run the test suite (pytest -q)
pdm run pytest tests/test_services.py::test_name   # run a single test
```

Config is read from a `.env` file at the project root (see `.env.example`): `INPUT_PATH`, `OUTPUT_PATH`,
`WEB_FORM_URL`, `HEADLESS`. All modules read these constants from `taller_rpa.config` — nothing else reads
`os.environ` directly.

## Architecture

The pipeline is a straight-line orchestration over small, single-purpose modules in `src/taller_rpa/`.
`Orchestrator.run()` (`orchestrator.py`) is the only place that sequences steps; each step's business logic
lives in its own module and is injected/imported rather than inlined, so steps are independently testable:

1. **`tracker.get_unprocessed_files`** — scans `input_dir` for supported files (`.csv`/`.xlsx`/`.xls`) that
   don't already have a matching `resultado_*.csv` in `output_dir` (see `utils.output_filename`). This is
   the resume/idempotency mechanism: re-running the bot skips files already processed.
2. **`readers.leer_archivo`** — Strategy/Factory pattern (`BaseReader` → `CsvReader`/`XlsxReader`, selected
   by extension via `reader_factory`). Reads everything as strings, normalizes headers/cells (strips
   whitespace), and drops fully-empty rows. Adding a new file format means adding one `BaseReader` subclass
   and registering it in `_LECTORES` — nothing downstream changes.
3. **`services`** — pure business-logic functions (no I/O): `columnas_faltantes` (missing required
   columns), `validate` (row → `Solicitud` via Pydantic, collecting per-row errors), `deduplicate` (first
   occurrence wins, keyed by `email` or `identificador`), `classify` (group by field, default
   `tipo_solicitud`).
4. **`models.Solicitud`** — the Pydantic model *is* the validation contract: if a row builds a `Solicitud`
   successfully, it was valid. `Solicitud.desde_fila` maps raw file columns (English headers, e.g.
   `"First Name"`) to internal snake_case fields via `COLUMNAS_PERSONA`/`COLUMNAS_SOLICITUD`. Models are
   frozen, forbid extra fields, and strip string whitespace. Dates accept multiple formats
   (`FORMATOS_FECHA`).
5. **`submitter.WebSubmitter`** — sends each valid `Solicitud` to the web form. Today `_registrar` is a
   stub that only logs; when browser automation (Playwright) is added, only `_registrar` changes — the
   rest of the pipeline is unaffected.
6. **`reporter`** — writes `resultado_{nombre}.csv` (one row per submitted solicitud plus one per
   rejected/duplicate row) and configures loguru (console + a timestamped file under `data/output/logs/`).
   Also prints per-file and global run summaries.

Cross-cutting pieces:
- **`config.py`** is the *only* module that reads environment variables / `.env`; every other module
  imports its resolved constants (`INPUT_PATH`, `OUTPUT_PATH`, `WEB_FORM_URL`, `HEADLESS`). Relative paths
  in `.env` are anchored to the project root (`RAIZ_PROYECTO`), so the bot behaves the same regardless of
  the working directory it's launched from.
- **`exceptions.py`** defines the domain exception hierarchy (`BotException` → `FileReadError`,
  `ValidationFailedError`, `SubmissionError`). `Orchestrator._procesar` catches `BotException` per file and
  skips that file (logging it as `omitido`) rather than aborting the whole run; `main.py` catches
  `BotException` at the top level as the final abort boundary (exit code 1).
- Failure isolation is per-file, not per-row within validation (invalid rows are just reported and
  excluded, not fatal) — a single malformed file never stops the rest of the batch from being processed.

## Tests

`tests/` mirrors the module structure (`test_models.py`, `test_services.py`, `test_readers_tracker.py`,
`test_orchestrator.py`, `test_email.py`). `conftest.py` provides a `fila` fixture (a valid base row that
tests mutate to trigger specific validation errors) and a `hacer_df` helper for building DataFrames with
the correct contract columns/order. `pyproject.toml` sets `pythonpath = ["src"]` and `testpaths = ["tests"]`
for pytest, so tests import `taller_rpa` directly without installing the package.

Sample/template input data referenced by tests lives under `Template/Template/data/`.
