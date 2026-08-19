"""Lectores (Strategy + Factory)."""

from __future__ import annotations

import pandas as pd
import pytest

from taller_rpa.exceptions import FileReadError
from taller_rpa.readers import CsvReader, XlsxReader, leer_archivo, reader_factory
from tests.conftest import hacer_df


@pytest.mark.parametrize(
    "extension, esperado",
    [(".csv", CsvReader), (".CSV", CsvReader), (".xlsx", XlsxReader), (".xls", XlsxReader)],
)
def test_factory_elige_el_lector(extension, esperado):
    assert isinstance(reader_factory(extension), esperado)


def test_factory_rechaza_extension_no_soportada():
    with pytest.raises(FileReadError):
        reader_factory(".pdf")


def test_archivo_inexistente_lanza_error(tmp_path):
    with pytest.raises(FileReadError):
        leer_archivo(tmp_path / "no_existe.csv")


@pytest.mark.parametrize("extension", [".csv", ".xlsx"])
def test_lee_csv_y_xlsx_recortando_espacios(tmp_path, fila, extension):
    df = hacer_df(dict(fila, **{"First Name": "  Ana  "}))
    destino = tmp_path / f"entrada{extension}"
    if extension == ".csv":
        df.to_csv(destino, index=False, encoding="utf-8-sig")
    else:
        df.to_excel(destino, index=False)

    leido = leer_archivo(destino)

    assert list(leido.columns)[:2] == ["First Name", "Last Name"]
    assert leido.loc[0, "First Name"] == "Ana"


def test_ignora_filas_completamente_vacias(tmp_path, fila):
    destino = tmp_path / "entrada.csv"
    hacer_df(fila).to_csv(destino, index=False)
    with destino.open("a", encoding="utf-8") as archivo:
        archivo.write(",,,,,,,,,,,,\n")

    assert len(leer_archivo(destino)) == 1
