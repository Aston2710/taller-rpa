"""Modelos de datos con Pydantic.

Los modelos concentran las reglas de validación: si una `Solicitud` se pudo
construir, la fila del archivo era correcta.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Annotated, Any, Literal, Mapping, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

# --- Contrato del archivo de entrada -----------------------------------------

COLUMNAS_PERSONA: dict[str, str] = {
    "First Name": "first_name",
    "Last Name": "last_name",
    "Company Name": "company_name",
    "Role in Company": "role_in_company",
    "Address": "address",
    "Email": "email",
    "Phone Number": "phone_number",
}

COLUMNAS_SOLICITUD: dict[str, str] = {
    "tipo_solicitud": "tipo_solicitud",
    "fecha": "fecha",
    "prioridad": "prioridad",
    "identificador": "identificador",
    "descripcion": "descripcion",
    "estado": "estado",
}

COLUMNAS_ARCHIVO: list[str] = [*COLUMNAS_PERSONA, *COLUMNAS_SOLICITUD]

FORMATOS_FECHA = (
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y/%m/%d",
    "%d.%m.%Y",
    "%Y%m%d",
)

Prioridad = Literal["alta", "media", "baja"]
Estado = Literal["pendiente", "en_proceso", "completada"]

# Campo de texto obligatorio: ni vacío ni solo espacios (se recortan antes).
NoVacio = Annotated[str, Field(min_length=1)]


class _ModeloBase(BaseModel):
    """Base común: inmutable, sin columnas extra y con texto recortado."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
    )


class Persona(_ModeloBase):
    """Datos personales mapeables al formulario web."""

    first_name: NoVacio
    last_name: NoVacio
    company_name: NoVacio
    role_in_company: NoVacio
    address: NoVacio
    email: EmailStr
    phone_number: NoVacio

    @property
    def nombre_completo(self) -> str:
        return f"{self.first_name} {self.last_name}"


class Solicitud(_ModeloBase):
    """Solicitud completa: persona + datos de negocio."""

    persona: Persona
    tipo_solicitud: NoVacio
    fecha: date
    prioridad: Prioridad
    identificador: NoVacio
    descripcion: NoVacio
    estado: Estado

    @field_validator("fecha", mode="before")
    @classmethod
    def _parsear_fecha(cls, valor: Any) -> Any:
        """Acepta la fecha en varios formatos de texto."""
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date) or not isinstance(valor, str):
            return valor

        texto = valor.strip()
        if not texto:
            raise ValueError("la fecha está vacía")
        for formato in FORMATOS_FECHA:
            try:
                return datetime.strptime(texto, formato).date()
            except ValueError:
                continue
        raise ValueError(f"fecha no reconocida: {valor!r}")

    @classmethod
    def desde_fila(cls, fila: Mapping[str, Any]) -> Self:
        """Construye la solicitud a partir de una fila del archivo."""
        persona = {
            campo: fila.get(columna) for columna, campo in COLUMNAS_PERSONA.items()
        }
        solicitud = {
            campo: fila.get(columna) for columna, campo in COLUMNAS_SOLICITUD.items()
        }
        return cls(persona=persona, **solicitud)
