"""Contrato del campo Email: dato del formulario y clave de deduplicación."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from taller_rpa import services
from taller_rpa.models import Persona
from tests.conftest import FILA_BASE, hacer_df

PERSONA_BASE = {
    "first_name": "Ana",
    "last_name": "Rodriguez",
    "company_name": "TechCorp",
    "role_in_company": "Analyst",
    "address": "Calle 63, Ciudad",
    "phone_number": "+1-555-4657",
}


def persona_con(email) -> Persona:
    return Persona(**PERSONA_BASE, email=email)


@pytest.mark.parametrize(
    "email",
    [
        "ana@example.com",
        "ana+taller@example.com",
        "ana_rodriguez@example.com",
        "ana@mail.example.com",
        "ana.rodríguez0@example.com",  # así vienen los datos del taller
    ],
)
def test_correos_aceptados(email):
    assert persona_con(email).email == email


@pytest.mark.parametrize(
    "email",
    [
        "",
        "   ",
        "ana.example.com",  # sin @
        "ana@",
        "@example.com",
        "ana@@example.com",
        "ana.@example.com",
        "a..b@example.com",
        "ana@localhost",  # sin TLD
        "ana@[192.168.0.1]",
        "ana rodriguez@example.com",
        '"ana rodriguez"@example.com',
        "ana@example.com,otra@example.com",
        "mailto:ana@example.com",
        "a" * 300 + "@example.com",
        None,
        12345,
    ],
)
def test_correos_rechazados(email):
    with pytest.raises(ValidationError):
        persona_con(email)


def test_deduplicate_usa_el_correo_como_clave(fila):
    otra = dict(fila, identificador="SOL-2024001")
    validos, errores = services.validate(hacer_df(fila, otra))
    assert not errores

    unicos, duplicados = services.deduplicate(validos, key="email")

    assert [s.identificador for s in unicos] == ["SOL-2024000"]
    assert duplicados[0]["campo"] == "email"
    assert duplicados[0]["email"] == fila["Email"]


def test_el_correo_del_archivo_base_es_valido():
    assert persona_con(FILA_BASE["Email"]).email == FILA_BASE["Email"]
