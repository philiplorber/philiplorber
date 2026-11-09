"""Modelo DCF en Python puro (suma de partes: retail por FCFF + banco por patrimonio).

Este archivo es la "segunda opinión" del Excel: calcula lo mismo de forma
independiente. Si el Excel y Python no dan lo mismo, hay un error en alguno.
(Buena práctica: reconciliar dos implementaciones.)

Uso:  python src/modelo_dcf.py
"""
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]


def cargar():
    cfg = yaml.safe_load((RAIZ / "config" / "supuestos.yaml").read_text(encoding="utf-8"))
    hist = pd.read_csv(RAIZ / "data" / "simulado" / "eeff_historicos.csv", index_col="partida")
    return cfg, hist


def v(cfg, seccion, clave):
    """Lee el `valor` de un supuesto."""
    return cfg[seccion][clave]["valor"]


# ---------------------------------------------------------------- Paso 2: histórico
def analisis_historico(hist: pd.DataFrame) -> pd.DataFrame:
    h = hist.copy()
    h.loc["ebitda"] = h.loc["ingresos"] - h.loc["costo_ventas"] - h.loc["gav"]
    h.loc["capital_trabajo"] = h.loc["inventarios"] + h.loc["cxc_comerciales"] - h.loc["proveedores"]
    ratios = pd.DataFrame({
        "crecimiento_ingresos": h.loc["ingresos"].pct_change(),
        "margen_ebitda": h.loc["ebitda"] / h.loc["ingresos"],
        "depreciacion_pct": h.loc["depreciacion"] / h.loc["ingresos"],
        "capex_pct": h.loc["capex"] / h.loc["ingresos"],
        "capital_trabajo_pct": h.loc["capital_trabajo"] / h.loc["ingresos"],
        "roe_banco": h.loc["utilidad_banco"] / h.loc["patrimonio_banco"],
    }).T
    return pd.concat([h, ratios])


# ---------------------------------------------------------------- Paso 3-4: proyección y FCFF
def proyectar(cfg, hist: pd.DataFrame) -> pd.DataFrame:
    base = str(cfg["general"]["anio_base"])
    n = cfg["general"]["anios_proyeccion"]
    anios = [str(int(base) + i) for i in range(1, n + 1)]
    t = v(cfg, "operacion", "tasa_impuesto")

    ingresos_prev = hist.loc["ingresos", base]
    ct_prev = hist.loc["inventarios", base] + hist.loc["cxc_comerciales", base] - hist.loc["proveedores", base]
    filas = []
    for i, anio in enumerate(anios):
        ingresos = ingresos_prev * (1 + v(cfg, "operacion", "crecimiento_ingresos")[i])
        ebitda = ingresos * v(cfg, "operacion", "margen_ebitda")[i]
        dep = ingresos * v(cfg, "operacion", "depreciacion_pct_ingresos")[i]
        ebit = ebitda - dep
        nopat = ebit * (1 - t)
        capex = ingresos * v(cfg, "operacion", "capex_pct_ingresos")[i]
        ct = ingresos * v(cfg, "operacion", "capital_trabajo_pct_ingresos")[i]
        delta_ct = ct - ct_prev
        fcff = nopat + dep - capex - delta_ct
        filas.append(dict(anio=anio, periodo=i + 1, ingresos=ingresos, ebitda=ebitda, depreciacion=dep,
                          ebit=ebit, nopat=nopat, capex=capex, capital_trabajo=ct,
                          delta_capital_trabajo=delta_ct, fcff=fcff))
        ingresos_prev, ct_prev = ingresos, ct
    return pd.DataFrame(filas).set_index("anio").T


# ---------------------------------------------------------------- Paso 5: tasas
def costo_capital(cfg) -> dict:
    rf = v(cfg, "wacc", "tasa_libre_riesgo")
    erp = v(cfg, "wacc", "premio_riesgo_mercado")
    crp = v(cfg, "wacc", "riesgo_pais")
    bu = v(cfg, "wacc", "beta_desapalancada")
    dv = v(cfg, "wacc", "deuda_sobre_capital_total")
    t = v(cfg, "wacc", "tasa_impuesto_escudo")
    de = dv / (1 - dv)
    beta_l = bu * (1 + (1 - t) * de)  # Hamada
    ke = rf + beta_l * erp + crp
    kd_neto = v(cfg, "wacc", "costo_deuda_antes_impuesto") * (1 - t)
    wacc = (1 - dv) * ke + dv * kd_neto
    ke_banco = rf + v(cfg, "banco", "beta_banco") * erp + crp
    return dict(d_e=de, beta_apalancada=beta_l, ke=ke, kd_neto=kd_neto, wacc=wacc, ke_banco=ke_banco)


# ---------------------------------------------------------------- Paso 6-8: valor
def valor_empresa(fcff: pd.Series, wacc: float, g: float) -> dict:
    periodos = range(1, len(fcff) + 1)
    vp_flujos = sum(f / (1 + wacc) ** p for f, p in zip(fcff, periodos))
    vt = fcff.iloc[-1] * (1 + g) / (wacc - g)
    vp_vt = vt / (1 + wacc) ** len(fcff)
    return dict(vp_flujos=vp_flujos, valor_terminal=vt, vp_terminal=vp_vt, ev=vp_flujos + vp_vt)


def valorizar(cfg, hist, proy, tasas, wacc=None, g=None) -> dict:
    wacc = tasas["wacc"] if wacc is None else wacc
    g = v(cfg, "terminal", "crecimiento_perpetuo") if g is None else g
    ev = valor_empresa(proy.loc["fcff"].astype(float), wacc, g)

    base = str(cfg["general"]["anio_base"])
    roe, gb, ke_b = v(cfg, "banco", "roe_sostenible"), v(cfg, "banco", "crecimiento_perpetuo"), tasas["ke_banco"]
    pvl = (roe - gb) / (ke_b - gb)  # P/VL justificado (Gordon sobre patrimonio)
    valor_banco = pvl * hist.loc["patrimonio_banco", base]

    p = cfg["puente"]
    deuda_neta = p["deuda_financiera_no_bancaria"]["valor"] - p["caja_no_bancaria"]["valor"]
    patrimonio = (ev["ev"] - deuda_neta - p["participaciones_no_controladoras"]["valor"]
                  + p["inversiones_asociadas"]["valor"] + valor_banco)
    por_accion = patrimonio / p["acciones_en_circulacion_mm"]["valor"]
    return dict(**ev, pvl_banco=pvl, valor_banco=valor_banco, deuda_neta=deuda_neta,
                patrimonio=patrimonio, valor_por_accion=por_accion,
                potencial=por_accion / p["precio_mercado"]["valor"] - 1)


def sensibilidad(cfg, hist, proy, tasas) -> pd.DataFrame:
    g0 = v(cfg, "terminal", "crecimiento_perpetuo")
    filas = {}
    for dw in cfg["sensibilidad"]["wacc_delta"]:
        w = tasas["wacc"] + dw
        filas[f"{w:.2%}"] = {f"{g0 + dg:.1%}": valorizar(cfg, hist, proy, tasas, w, g0 + dg)["valor_por_accion"]
                             for dg in cfg["sensibilidad"]["g_delta"]}
    return pd.DataFrame(filas).T  # filas = WACC, columnas = g


def main() -> None:
    cfg, hist = cargar()
    proy = proyectar(cfg, hist)
    tasas = costo_capital(cfg)
    res = valorizar(cfg, hist, proy, tasas)
    pd.set_option("display.float_format", lambda x: f"{x:,.3f}")
    print("== Histórico (ratios) ==\n", analisis_historico(hist).tail(6).round(3))
    print("\n== Proyección FCFF (MM CLP) ==\n", proy.round(0))
    print("\n== Tasas ==", {k: round(x, 4) for k, x in tasas.items()})
    print("\n== Valoración ==")
    for k, x in res.items():
        print(f"  {k:>22}: {x:,.4f}")
    print(f"\n  VT / EV: {res['vp_terminal'] / res['ev']:.1%}")
    print("\n== Sensibilidad valor por acción (filas WACC, columnas g) ==\n", sensibilidad(cfg, hist, proy, tasas).round(0))


if __name__ == "__main__":
    main()
