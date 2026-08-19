"""Reglas de validación a nivel de fila."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from taller_rpa.models import COLUMNAS_ARCHIVO, Solicitud


def test_columnas_del_contrato_son_trece():
    assert len(COLUMNAS_ARCHIVO) == 13
    assert COLUMNAS_ARCHIVO[0] == "First Name"
    assert COLUMNAS_ARCHIVO[-1] == "estado"


def test_fila_valida_se_convierte_en_solicitud(fila):
    solicitud = Solicitud.desde_fila(fila)

    assert solicitud.persona.nombre_completo == "Ana Rodríguez"
    assert solicitud.fecha == date(2024, 1, 1)
    assert solicitud.prioridad == "baja"
    assert solicitud.estado == "pendiente"
    assert solicitud.tipo_solicitud == "consulta"


@pytest.mark.parametrize(
    "texto_fecha, esperada",
    [
        ("2024-03-09", date(2024, 3, 9)),
        ("09/03/2024", date(2024, 3, 9)),
        ("09-03-2024", date(2024, 3, 9)),
        ("2024/03/09", date(2024, 3, 9)),
        ("09.03.2024", date(2024, 3, 9)),
        ("20240309", date(2024, 3, 9)),
    ],
)
def test_fecha_acepta_varios_formatos(fila, texto_fecha, esperada):
    fila["fecha"] = texto_fecha
    assert Solicitud.desde_fila(fila).fecha == esperada


@pytest.mark.parametrize("columna", COLUMNAS_ARCHIVO)
@pytest.mark.parametrize("vacio", ["", "   "])
def test_ningun_campo_puede_ir_vacio(fila, columna, vacio):
    fila[columna] = vacio
    with pytest.raises(ValidationError):
        Solicitud.desde_fila(fila)


@pytest.mark.parametrize("columna", COLUMNAS_ARCHIVO)
def test_ningun_campo_puede_faltar(fila, columna):
    del fila[columna]
    with pytest.raises(ValidationError):
        Solicitud.desde_fila(fila)


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("Email", "no-es-un-correo"),
        ("fecha", "31/02/2024"),
        ("fecha", "ayer"),
        ("prioridad", "urgentísima"),
        ("prioridad", "ALTA"),  # el Literal distingue mayúsculas
        ("estado", "archivada"),
        ("estado", "en proceso"),  # el valor esperado es en_proceso
    ],
)
def test_valores_fuera_del_contrato_son_rechazados(fila, campo, valor):
    fila[campo] = valor
    with pytest.raises(ValidationError):
        Solicitud.desde_fila(fila)


def test_los_espacios_alrededor_se_recortan(fila):
    fila["First Name"] = "  Ana  "
    fila["identificador"] = " SOL-2024000 "

    solicitud = Solicitud.desde_fila(fila)

    assert solicitud.persona.first_name == "Ana"
    assert solicitud.identificador == "SOL-2024000"


def test_columna_extra_es_rechazada_por_el_modelo(fila):
    with pytest.raises(ValidationError):
        Solicitud(persona={}, comentario="hola")
