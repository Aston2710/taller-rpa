"""Value Objects de archivos rastreados y diferencia de conjuntos de pendientes."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from datetime import date

import pytest

from taller_rpa.tracker import (
    ProcessableInputFile,
    ProcessableOutputFile,
    get_unprocessed_files,
)


def _crear(base_dir, ruta_relativa):
    """Crea `base_dir/ruta_relativa` (y sus carpetas) y devuelve la ruta absoluta."""
    destino = base_dir / ruta_relativa
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.touch()
    return destino


def test_desde_ruta_extrae_year_month_day_y_construye_date(tmp_path):
    archivo = _crear(tmp_path, "2028/01/15/solicitudes_a.csv")

    objeto = ProcessableInputFile.desde_ruta(tmp_path, archivo)

    assert (objeto.year, objeto.month, objeto.day) == (2028, 1, 15)
    assert objeto.date == date(2028, 1, 15)
    assert objeto.path_dir == "2028/01/15/solicitudes_a.csv"
    assert objeto.full_path == archivo.resolve()


def test_igualdad_es_cruzada_entre_input_y_output_por_path_dir(tmp_path):
    entrada = _crear(tmp_path / "in", "2028/01/15/solicitudes_a.csv")
    salida = _crear(tmp_path / "out", "2028/01/15/solicitudes_a.csv")

    input_file = ProcessableInputFile.desde_ruta(tmp_path / "in", entrada)
    output_file = ProcessableOutputFile.desde_ruta(tmp_path / "out", salida)

    assert input_file == output_file
    assert output_file == input_file


def test_igualdad_distingue_por_ruta_no_por_contenido(tmp_path):
    a = _crear(tmp_path, "2028/01/15/solicitudes_a.csv")
    b = _crear(tmp_path, "2028/01/16/solicitudes_a.csv")

    assert ProcessableInputFile.desde_ruta(tmp_path, a) != ProcessableInputFile.desde_ruta(
        tmp_path, b
    )


def test_hash_es_consistente_con_la_igualdad(tmp_path):
    """Precondición de cualquier Value Object usado en un `set`/`dict`."""
    entrada = _crear(tmp_path / "in", "2028/01/15/solicitudes_a.csv")
    salida = _crear(tmp_path / "out", "2028/01/15/solicitudes_a.csv")

    input_file = ProcessableInputFile.desde_ruta(tmp_path / "in", entrada)
    output_file = ProcessableOutputFile.desde_ruta(tmp_path / "out", salida)

    assert hash(input_file) == hash(output_file)
    assert {input_file} == {output_file}
    assert {input_file, output_file} == {input_file}


def test_processable_file_es_inmutable(tmp_path):
    archivo = _crear(tmp_path, "2028/01/15/solicitudes_a.csv")
    objeto = ProcessableInputFile.desde_ruta(tmp_path, archivo)

    with pytest.raises(FrozenInstanceError):
        objeto.year = 2029


def test_get_unprocessed_files_recorre_subcarpetas_por_fecha(tmp_path):
    entrada, salida = tmp_path / "in", tmp_path / "out"
    _crear(entrada, "2028/01/15/solicitudes_a.csv")
    _crear(entrada, "2028/01/15/pedidos_b.xlsx")
    _crear(entrada, "2028/01/16/reclamos_c.csv")
    _crear(salida, "2028/01/15/solicitudes_a.csv")
    _crear(salida, "2028/01/15/pedidos_b.xlsx")

    pendientes = get_unprocessed_files(entrada, salida)

    assert [p.relative_to(entrada).as_posix() for p in pendientes] == [
        "2028/01/16/reclamos_c.csv"
    ]


def test_get_unprocessed_files_ignora_extensiones_no_rastreadas_y_temporales(tmp_path):
    entrada, salida = tmp_path / "in", tmp_path / "out"
    _crear(entrada, "2028/01/15/notas.txt")
    _crear(entrada, "2028/01/15/~$pedidos_b.xlsx")
    salida.mkdir()

    assert get_unprocessed_files(entrada, salida) == []


def test_get_unprocessed_files_sin_carpeta_de_entrada(tmp_path):
    assert get_unprocessed_files(tmp_path / "no_existe", tmp_path / "out") == []


def test_get_unprocessed_files_sin_carpeta_de_salida_trata_todo_como_pendiente(tmp_path):
    entrada = tmp_path / "in"
    _crear(entrada, "2028/01/15/solicitudes_a.csv")

    pendientes = get_unprocessed_files(entrada, tmp_path / "out_inexistente")

    assert len(pendientes) == 1
