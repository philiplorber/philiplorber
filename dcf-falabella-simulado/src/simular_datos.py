"""Genera estados financieros históricos SIMULADOS (2021-2025).

Por qué simular: el objetivo es aprender el PROCESO del DCF. Los datos reales
se pueden enchufar después reemplazando `data/simulado/eeff_historicos.csv`
por cifras de la CMF; `data/mapa_fuentes.csv` dice de dónde sale cada línea.

Los números se generan con una semilla fija (config: semilla_simulacion) para
que cualquiera que corra el script obtenga exactamente lo mismo.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
ANIOS = [2021, 2022, 2023, 2024, 2025]


def simular(semilla: int) -> pd.DataFrame:
    rng = np.random.default_rng(semilla)

    # Ingresos: base ilustrativa + crecimiento nominal con ruido.
    crecimiento = rng.normal(0.05, 0.03, len(ANIOS) - 1)
    ingresos = [9_000_000.0]
    for g in crecimiento:
        ingresos.append(ingresos[-1] * (1 + g))
    ingresos = np.array(ingresos)

    # Estructura de costos (% de ingresos) con ruido: margen EBITDA ~ 8-11%.
    costo_ventas = ingresos * rng.normal(0.66, 0.008, len(ANIOS))
    gav = ingresos * rng.normal(0.24, 0.008, len(ANIOS))  # incluye arriendos, excluye D&A
    depreciacion = ingresos * rng.normal(0.030, 0.002, len(ANIOS))
    capex = ingresos * rng.normal(0.040, 0.006, len(ANIOS))

    # Capital de trabajo operativo.
    inventarios = ingresos * rng.normal(0.14, 0.006, len(ANIOS))
    cxc = ingresos * rng.normal(0.06, 0.004, len(ANIOS))
    proveedores = ingresos * rng.normal(0.12, 0.005, len(ANIOS))

    # Negocio financiero (se valoriza aparte, por patrimonio).
    patrimonio_banco = 1_100_000 * np.cumprod(1 + rng.normal(0.07, 0.02, len(ANIOS)))
    utilidad_banco = patrimonio_banco * rng.normal(0.14, 0.02, len(ANIOS))

    filas = {
        "ingresos": ingresos,
        "costo_ventas": costo_ventas,
        "gav": gav,
        "depreciacion": depreciacion,
        "capex": capex,
        "inventarios": inventarios,
        "cxc_comerciales": cxc,
        "proveedores": proveedores,
        "patrimonio_banco": patrimonio_banco,
        "utilidad_banco": utilidad_banco,
    }
    df = pd.DataFrame(filas, index=ANIOS).T.round(0)
    df.index.name = "partida"
    df.columns = [str(a) for a in ANIOS]
    return df


def main() -> None:
    cfg = yaml.safe_load((RAIZ / "config" / "supuestos.yaml").read_text(encoding="utf-8"))
    df = simular(cfg["general"]["semilla_simulacion"])
    salida = RAIZ / "data" / "simulado" / "eeff_historicos.csv"
    df.to_csv(salida)
    print(f"Datos simulados escritos en {salida.relative_to(RAIZ)}")
    print(df.to_string(float_format=lambda x: f"{x:,.0f}"))


if __name__ == "__main__":
    main()
