"""Validación de columnas, de filas, deduplicación y clasificación."""

from __future__ import annotations

import pytest

from taller_rpa import services
from tests.conftest import hacer_df


def test_detecta_columnas_faltantes(fila):
    df = hacer_df(fila).drop(columns=["Email", "estado"])

    assert services.columnas_faltantes(df) == ["Email", "estado"]


def test_archivo_completo_no_reporta_faltantes(fila):
    assert services.columnas_faltantes(hacer_df(fila)) == []


def test_validate_separa_validos_de_errores(fila):
    mala = dict(fila, Email="rota", identificador="SOL-2024001")

    validos, errores = services.validate(hacer_df(fila, mala))

    assert [s.identificador for s in validos] == ["SOL-2024000"]
    assert len(errores) == 1
    assert errores[0]["fila"] == 3
    assert errores[0]["campo"] == "persona.email"
    assert errores[0]["motivo"] == "validacion"


def test_validate_reporta_campo_vacio(fila):
    validos, errores = services.validate(hacer_df(dict(fila, descripcion="")))

    assert not validos
    assert errores[0]["campo"] == "descripcion"


def test_deduplicate_por_email_conserva_la_primera(fila):
    segunda = dict(fila, identificador="SOL-2024001")
    validos, _ = services.validate(hacer_df(fila, segunda))

    unicos, duplicados = services.deduplicate(validos, key="email")

    assert [s.identificador for s in unicos] == ["SOL-2024000"]
    assert duplicados[0]["identificador"] == "SOL-2024001"
    assert duplicados[0]["motivo"] == "duplicado"


def test_deduplicate_por_identificador(fila):
    segunda = dict(fila, Email="otra@example.com")
    validos, _ = services.validate(hacer_df(fila, segunda))

    unicos, duplicados = services.deduplicate(validos, key="identificador")

    assert len(unicos) == 1
    assert len(duplicados) == 1


def test_deduplicate_rechaza_clave_desconocida():
    with pytest.raises(ValueError):
        services.deduplicate([], key="telefono")


def test_classify_agrupa_por_tipo(fila):
    otra = dict(
        fila,
        tipo_solicitud="soporte",
        identificador="SOL-2024001",
        Email="otra@example.com",
    )
    validos, _ = services.validate(hacer_df(fila, otra))

    grupos = services.classify(validos)

    assert sorted(grupos) == ["consulta", "soporte"]
    assert len(grupos["consulta"]) == 1


def test_classify_por_prioridad(fila):
    validos, _ = services.validate(hacer_df(fila))

    assert list(services.classify(validos, by="prioridad")) == ["baja"]
