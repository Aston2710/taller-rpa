"""Pipeline completo sobre carpetas temporales."""

from __future__ import annotations

import shutil

import pandas as pd
import pytest

from taller_rpa.orchestrator import Orchestrator
from taller_rpa.submitter import RESULTADO_ERROR, RESULTADO_OK, WebSubmitter
from tests.conftest import ENTRADA_TALLER, hacer_df

FECHA = "2028/01/15"


class SubmitterCaido(WebSubmitter):
    """Doble de prueba: el formulario web falla siempre."""

    def submit(self, solicitudes):
        return [
            {
                "identificador": s.identificador,
                "resultado": RESULTADO_ERROR,
                "error": "timeout",
            }
            for s in solicitudes
        ]


@pytest.fixture
def carpetas(tmp_path):
    entrada, salida = tmp_path / "in", tmp_path / "out"
    entrada.mkdir(), salida.mkdir()
    return entrada, salida


def correr(carpetas, submitter=None):
    entrada, salida = carpetas
    return Orchestrator(
        input_dir=entrada,
        output_dir=salida,
        submitter=submitter,
        configurar_logging=False,
    ).run()


def ruta_entrada(entrada, nombre, fecha=FECHA):
    """Ruta `entrada/fecha/nombre`, creando las carpetas por fecha si hace falta."""
    destino = entrada / fecha / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    return destino


def test_sin_archivos_no_falla(carpetas):
    assert correr(carpetas) == []


def test_procesa_validos_duplicados_y_errores(carpetas, fila):
    entrada, salida = carpetas
    duplicada = dict(fila, identificador="SOL-2024001")
    invalida = dict(fila, Email="rota", identificador="SOL-2024002")
    hacer_df(fila, duplicada, invalida).to_csv(
        ruta_entrada(entrada, "solicitudes.csv"), index=False
    )

    (resumen,) = correr(carpetas)

    assert (resumen.filas_leidas, resumen.validas) == (3, 2)
    assert (resumen.duplicados, resumen.errores_validacion) == (1, 1)
    assert (resumen.envios_ok, resumen.envios_fallidos) == (1, 0)

    csv = pd.read_csv(salida / FECHA / "solicitudes.csv")
    assert list(csv["resultado"]) == [RESULTADO_OK, "error_validacion", "duplicado"]
    assert csv.loc[0, "identificador"] == "SOL-2024000"


def test_el_csv_de_salida_respeta_el_esquema(carpetas, fila):
    entrada, salida = carpetas
    hacer_df(fila).to_csv(ruta_entrada(entrada, "solicitudes.csv"), index=False)

    correr(carpetas)

    csv = pd.read_csv(salida / FECHA / "solicitudes.csv")
    assert list(csv.columns) == [
        "first_name",
        "last_name",
        "email",
        "tipo_solicitud",
        "fecha",
        "prioridad",
        "identificador",
        "estado",
        "resultado",
        "error",
    ]


def test_archivo_sin_columnas_obligatorias_se_omite(carpetas, fila):
    entrada, salida = carpetas
    hacer_df(fila).drop(columns=["Email"]).to_csv(
        ruta_entrada(entrada, "malo.csv"), index=False
    )

    (resumen,) = correr(carpetas)

    assert resumen.fue_omitido
    assert "Email" in resumen.omitido
    assert not list(salida.rglob("*.csv"))


def test_no_reprocesa_archivos_con_resultado(carpetas, fila):
    entrada, _ = carpetas
    hacer_df(fila).to_csv(ruta_entrada(entrada, "solicitudes.csv"), index=False)

    assert len(correr(carpetas)) == 1
    assert correr(carpetas) == []


def test_falla_de_envio_queda_registrada(carpetas, fila):
    entrada, salida = carpetas
    hacer_df(fila).to_csv(ruta_entrada(entrada, "solicitudes.csv"), index=False)

    (resumen,) = correr(carpetas, submitter=SubmitterCaido())

    assert (resumen.envios_ok, resumen.envios_fallidos) == (0, 1)
    csv = pd.read_csv(salida / FECHA / "solicitudes.csv")
    assert csv.loc[0, "resultado"] == RESULTADO_ERROR
    assert csv.loc[0, "error"] == "timeout"


def test_archivos_reales_del_taller(carpetas):
    """`ENTRADA_TALLER` trae `solicitudes_prueba.csv` y `.xlsx`: mismo nombre base,
    distinta extensión. El espejo exacto (misma ruta+extensión que el input) evita
    que uno pise el resultado del otro y permite que ambos queden marcados como
    procesados."""
    entrada, salida = carpetas
    for archivo in ENTRADA_TALLER.iterdir():
        shutil.copy(archivo, ruta_entrada(entrada, archivo.name))

    resumenes = correr(carpetas)

    assert len(resumenes) == 2
    for resumen in resumenes:
        assert (resumen.filas_leidas, resumen.validas) == (20, 20)
        assert (resumen.errores_validacion, resumen.duplicados) == (0, 0)
        assert resumen.envios_ok == 20

    assert (salida / FECHA / "solicitudes_prueba.csv").is_file()
    assert (salida / FECHA / "solicitudes_prueba.xlsx").is_file()
    assert len(pd.read_csv(salida / FECHA / "solicitudes_prueba.xlsx")) == 20

    assert correr(carpetas) == []
