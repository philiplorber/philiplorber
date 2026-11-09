"""Construye outputs/DCF_Falabella_simulado.xlsx con FÓRMULAS vivas.

El Excel no trae resultados pegados: cada número calculado es una fórmula
que puedes seguir con "Rastrear precedentes" (Fórmulas > Auditoría).
Los insumos vienen de config/supuestos.yaml y data/simulado/eeff_historicos.csv.

Uso:  python src/construir_excel.py
"""
import json
from pathlib import Path

import pandas as pd
import yaml
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from modelo_dcf import cargar, costo_capital, proyectar, valorizar

RAIZ = Path(__file__).resolve().parents[1]
SALIDA = RAIZ / "outputs" / "DCF_Falabella_simulado.xlsx"

# ----------------------------------------------------------------- estilos
FUENTE = "Arial"
AZUL = Font(name=FUENTE, color="0000FF")             # insumo escrito a mano
NEGRO = Font(name=FUENTE, color="000000")            # fórmula
VERDE = Font(name=FUENTE, color="008000")            # vínculo a otra hoja
NEGRITA = Font(name=FUENTE, bold=True)
TITULO = Font(name=FUENTE, bold=True, size=14)
SUBT = Font(name=FUENTE, bold=True, color="FFFFFF")
AMARILLO = PatternFill("solid", fgColor="FFFF00")    # supuesto clave
GRIS = PatternFill("solid", fgColor="D9D9D9")
AZUL_OSC = PatternFill("solid", fgColor="1F3864")
BORDE_SUP = Border(top=Side(style="thin"))
MM = '#,##0;(#,##0);"-"'
PCT = '0.0%;(0.0%);"-"'
PCT2 = '0.00%;(0.00%);"-"'
MULT = '0.00"x"'
CLP = '#,##0" CLP";(#,##0" CLP")'


def celda(ws, ref, valor, fuente=NEGRO, fmt=None, relleno=None, negrita=False):
    c = ws[ref]
    c.value = valor
    c.font = Font(name=FUENTE, color=fuente.color, bold=negrita or fuente.bold, size=fuente.size)
    if fmt:
        c.number_format = fmt
    if relleno:
        c.fill = relleno
    return c


def encabezado(ws, fila, textos, desde_col=1):
    for i, t in enumerate(textos):
        c = ws.cell(row=fila, column=desde_col + i, value=t)
        c.font = SUBT
        c.fill = AZUL_OSC
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)


def anchos(ws, dic):
    for col, w in dic.items():
        ws.column_dimensions[col].width = w


def titulo(ws, texto, sub):
    celda(ws, "A1", texto, TITULO)
    celda(ws, "A2", sub, Font(name=FUENTE, italic=True, color="C00000"))


# ----------------------------------------------------------------- hojas
def hoja_leeme(wb):
    ws = wb.active
    ws.title = "Leeme"
    titulo(ws, "DCF Falabella — ejercicio de aprendizaje", "DATOS SIMULADOS. No describe a Falabella S.A. real. No es recomendación de inversión.")
    lineas = [
        ("Qué es", "Valoración por suma de partes: negocio NO bancario por flujos de caja descontados (FCFF a WACC) + negocio financiero (Banco + CMR) por patrimonio (P/VL justificado a Ke)."),
        ("Cómo se edita", "Cambia SOLO celdas azules con fondo amarillo de la hoja Supuestos (o mejor: config/supuestos.yaml y vuelve a correr src/construir_excel.py). Todo lo demás se recalcula."),
        ("", ""),
        ("Código de colores", ""),
        ("Azul", "Insumo escrito a mano (dato histórico o supuesto)."),
        ("Negro", "Fórmula calculada en la misma hoja."),
        ("Verde", "Fórmula que trae un valor desde otra hoja."),
        ("Fondo amarillo", "Supuesto clave: aquí se discute la valoración."),
        ("", ""),
        ("Recorrido (= pasos del proceso)", ""),
        ("1. Fuentes", "De dónde saldría cada dato real (aquí: simulado)."),
        ("2. Historico", "Estados financieros históricos 2021-2025 y sus ratios (márgenes, capex, capital de trabajo, ROE banco)."),
        ("3. Supuestos", "Todos los supuestos en un solo lugar, con justificación."),
        ("4. Proyeccion", "Ingresos → EBITDA → EBIT → NOPAT → FCFF, 2026-2030."),
        ("5. WACC", "Costo del patrimonio (CAPM), costo de la deuda y WACC; Ke del banco."),
        ("6. Valoracion", "Valor terminal (Gordon), valor empresa, banco, puente a valor por acción vs precio."),
        ("7. Sensibilidad", "Valor por acción para distintos WACC y g."),
        ("8. Checks", "Controles de razonabilidad y reconciliación con Python."),
        ("", ""),
        ("Unidades", "MM CLP = millones de pesos chilenos nominales. Valor por acción en CLP. Fecha de valoración: 31-dic-2025 (convención de fin de año)."),
    ]
    for i, (a, b) in enumerate(lineas, start=4):
        celda(ws, f"A{i}", a, NEGRITA if b == "" or a in ("Qué es", "Cómo se edita", "Unidades") else NEGRO)
        celda(ws, f"B{i}", b)
        ws[f"B{i}"].alignment = Alignment(wrap_text=True, vertical="top")
    ws["A8"].font = Font(name=FUENTE, color="0000FF")
    ws["A10"].font = Font(name=FUENTE, color="008000")
    ws["A11"].fill = AMARILLO
    anchos(ws, {"A": 30, "B": 110})


def hoja_supuestos(wb, cfg):
    ws = wb.create_sheet("Supuestos")
    titulo(ws, "Supuestos (espejo de config/supuestos.yaml)", "DATOS SIMULADOS — cada supuesto con su justificación")
    base = cfg["general"]["anio_base"]
    n = cfg["general"]["anios_proyeccion"]
    anios = [str(base + i) for i in range(1, n + 1)]
    encabezado(ws, 4, ["Supuesto", "Unidad"] + anios + ["Justificación / fuente"])
    ref = {}
    fila = 5

    def seccion(nombre):
        nonlocal fila
        fila += 1
        celda(ws, f"A{fila}", nombre, NEGRITA, relleno=GRIS)
        for col in range(2, 4 + n):
            ws.cell(row=fila, column=col).fill = GRIS
        fila += 1

    def fila_supuesto(clave, seccion_cfg, etiqueta, unidad, fmt):
        nonlocal fila
        s = cfg[seccion_cfg][clave]
        celda(ws, f"A{fila}", etiqueta)
        celda(ws, f"B{fila}", unidad)
        valores = s["valor"] if isinstance(s["valor"], list) else [s["valor"]]
        for i, x in enumerate(valores):
            celda(ws, f"{get_column_letter(3 + i)}{fila}", x, AZUL, fmt, AMARILLO)
        j = ws.cell(row=fila, column=3 + n, value=" ".join(str(s["justificacion"]).split()))
        j.font = Font(name=FUENTE, size=9)
        j.alignment = Alignment(wrap_text=True, vertical="top")
        ref[f"{seccion_cfg}.{clave}"] = fila
        fila += 1

    seccion("1. Operación — negocio NO bancario (un valor por año)")
    fila_supuesto("crecimiento_ingresos", "operacion", "Crecimiento de ingresos", "%", PCT)
    fila_supuesto("margen_ebitda", "operacion", "Margen EBITDA (post arriendos)", "% ingresos", PCT)
    fila_supuesto("depreciacion_pct_ingresos", "operacion", "Depreciación", "% ingresos", PCT)
    fila_supuesto("capex_pct_ingresos", "operacion", "Capex", "% ingresos", PCT)
    fila_supuesto("capital_trabajo_pct_ingresos", "operacion", "Capital de trabajo neto", "% ingresos", PCT)
    fila_supuesto("tasa_impuesto", "operacion", "Tasa de impuesto", "%", PCT)
    seccion("2. Tasa de descuento (WACC)")
    fila_supuesto("tasa_libre_riesgo", "wacc", "Tasa libre de riesgo (rf)", "%", PCT2)
    fila_supuesto("beta_desapalancada", "wacc", "Beta desapalancada (βu)", "x", "0.00")
    fila_supuesto("premio_riesgo_mercado", "wacc", "Premio por riesgo de mercado (ERP)", "%", PCT2)
    fila_supuesto("riesgo_pais", "wacc", "Riesgo país (CRP)", "%", PCT2)
    fila_supuesto("costo_deuda_antes_impuesto", "wacc", "Costo de la deuda antes de impuesto (Kd)", "%", PCT2)
    fila_supuesto("deuda_sobre_capital_total", "wacc", "Deuda / (Deuda + Patrimonio) objetivo", "%", PCT)
    fila_supuesto("tasa_impuesto_escudo", "wacc", "Tasa de impuesto (escudo tributario)", "%", PCT)
    seccion("3. Valor terminal")
    fila_supuesto("crecimiento_perpetuo", "terminal", "Crecimiento perpetuo (g)", "%", PCT2)
    fila_supuesto("multiplo_salida_referencia", "terminal", "EV/EBITDA de referencia (contraste)", "x", MULT)
    seccion("4. Negocio financiero (Banco + CMR)")
    fila_supuesto("roe_sostenible", "banco", "ROE sostenible", "%", PCT)
    fila_supuesto("beta_banco", "banco", "Beta del banco (apalancada)", "x", "0.00")
    fila_supuesto("crecimiento_perpetuo", "banco", "Crecimiento perpetuo banco", "%", PCT2)
    seccion("5. Puente a valor por acción")
    fila_supuesto("deuda_financiera_no_bancaria", "puente", "Deuda financiera no bancaria", "MM CLP", MM)
    fila_supuesto("caja_no_bancaria", "puente", "Caja no bancaria", "MM CLP", MM)
    fila_supuesto("participaciones_no_controladoras", "puente", "Participaciones no controladoras", "MM CLP", MM)
    fila_supuesto("inversiones_asociadas", "puente", "Inversiones en asociadas", "MM CLP", MM)
    fila_supuesto("acciones_en_circulacion_mm", "puente", "Acciones en circulación", "millones", "#,##0")
    fila_supuesto("precio_mercado", "puente", "Precio de mercado por acción", "CLP", "#,##0")

    anchos(ws, {"A": 40, "B": 12, **{get_column_letter(3 + i): 10 for i in range(n)}, get_column_letter(3 + n): 90})
    ws.freeze_panes = "C5"
    # Devuelve referencias absolutas: escalares en columna C; anuales por columna.
    return {k: f"Supuestos!$C${r}" for k, r in ref.items()}, {k: r for k, r in ref.items()}


def hoja_historico(wb, hist):
    ws = wb.create_sheet("Historico")
    titulo(ws, "Estados financieros históricos — MM CLP", "DATOS SIMULADOS (src/simular_datos.py). Ver hoja Fuentes para el dato real equivalente.")
    anios = list(hist.columns)
    encabezado(ws, 4, ["Partida"] + anios + ["Origen"])
    etiquetas = {
        "ingresos": "Ingresos (no bancario)", "costo_ventas": "Costo de ventas", "gav": "Gastos de adm. y ventas (incl. arriendos, sin D&A)",
        "depreciacion": "Depreciación y amortización", "capex": "Capex (flujo de inversión)", "inventarios": "Inventarios",
        "cxc_comerciales": "Cuentas por cobrar comerciales", "proveedores": "Proveedores",
        "patrimonio_banco": "Patrimonio negocio financiero", "utilidad_banco": "Utilidad negocio financiero",
    }
    filas = {}
    r = 5
    for clave, etiqueta in etiquetas.items():
        celda(ws, f"A{r}", etiqueta)
        for j, a in enumerate(anios):
            celda(ws, f"{get_column_letter(2 + j)}{r}", float(hist.loc[clave, a]), AZUL, MM)
        celda(ws, f"{get_column_letter(2 + len(anios))}{r}", "SIMULADO", Font(name=FUENTE, size=9, color="C00000"))
        filas[clave] = r
        r += 1
    r += 1
    celda(ws, f"A{r}", "Cálculos", NEGRITA, relleno=GRIS)
    r += 1
    calc = [
        ("ebitda", "EBITDA (post arriendos)", "={c}{ingresos}-{c}{costo_ventas}-{c}{gav}", MM, False),
        ("capital_trabajo", "Capital de trabajo neto operativo", "={c}{inventarios}+{c}{cxc_comerciales}-{c}{proveedores}", MM, False),
        ("crec", "Crecimiento de ingresos", "={c}{ingresos}/{p}{ingresos}-1", PCT, True),
        ("mg", "Margen EBITDA", "={c}{ebitda}/{c}{ingresos}", PCT, False),
        ("dep", "Depreciación % ingresos", "={c}{depreciacion}/{c}{ingresos}", PCT, False),
        ("capex_pct", "Capex % ingresos", "={c}{capex}/{c}{ingresos}", PCT, False),
        ("capex_dep", "Capex / Depreciación", "={c}{capex}/{c}{depreciacion}", MULT, False),
        ("ct_pct", "Capital de trabajo % ingresos", "={c}{capital_trabajo}/{c}{ingresos}", PCT, False),
        ("roe", "ROE negocio financiero", "={c}{utilidad_banco}/{c}{patrimonio_banco}", PCT, False),
    ]
    for clave, etiqueta, plantilla, fmt, salta_primero in calc:
        celda(ws, f"A{r}", etiqueta)
        filas[clave] = r
        for j in range(len(anios)):
            if salta_primero and j == 0:
                continue
            col, prev = get_column_letter(2 + j), get_column_letter(1 + j)
            celda(ws, f"{col}{r}", plantilla.format(c=col, p=prev, **filas), NEGRO, fmt)
        r += 1
    # Promedios: la referencia natural para proponer supuestos.
    col_prom = get_column_letter(2 + len(anios))
    celda(ws, f"{col_prom}{filas['crec']-1}", "Promedio", NEGRITA)
    for clave in ["crec", "mg", "dep", "capex_pct", "capex_dep", "ct_pct", "roe"]:
        fmt = MULT if clave == "capex_dep" else PCT
        celda(ws, f"{col_prom}{filas[clave]}", f"=AVERAGE(B{filas[clave]}:{get_column_letter(1 + len(anios))}{filas[clave]})", NEGRO, fmt, negrita=True)
    anchos(ws, {"A": 48, **{get_column_letter(2 + j): 13 for j in range(len(anios))}, col_prom: 12})
    ws.freeze_panes = "B5"
    return filas, get_column_letter(1 + len(anios))  # columna del año base


def hoja_proyeccion(wb, cfg, S, Sfila, H, col_base):
    ws = wb.create_sheet("Proyeccion")
    titulo(ws, "Proyección y flujo de caja libre para la firma (FCFF) — MM CLP", "DATOS SIMULADOS. Columna B = año base real (2025); C-G = proyección.")
    base = cfg["general"]["anio_base"]
    n = cfg["general"]["anios_proyeccion"]
    cols = [get_column_letter(3 + i) for i in range(n)]
    encabezado(ws, 3, ["Concepto", f"{base}A"] + [f"{base + i + 1}E" for i in range(n)])
    celda(ws, "A4", "Período de descuento (años desde la valoración)")
    celda(ws, "B4", 0, AZUL)
    for i, c in enumerate(cols):
        celda(ws, f"{c}4", f"={get_column_letter(2 + i)}4+1")

    def anual(clave):  # columna del supuesto anual i -> columna Supuestos C..G
        return Sfila[clave]

    F = {}
    filas_def = [
        ("crec", "Crecimiento de ingresos", PCT),
        ("ingresos", "Ingresos", MM),
        ("mg", "Margen EBITDA", PCT),
        ("ebitda", "EBITDA", MM),
        ("dep_pct", "Depreciación % ingresos", PCT),
        ("dep", "(-) Depreciación", MM),
        ("ebit", "EBIT (resultado operacional)", MM),
        ("t", "Tasa de impuesto", PCT),
        ("imp", "(-) Impuesto sobre EBIT", MM),
        ("nopat", "NOPAT (EBIT después de impuesto)", MM),
        ("dep2", "(+) Depreciación (no es salida de caja)", MM),
        ("capex_pct", "Capex % ingresos", PCT),
        ("capex", "(-) Capex", MM),
        ("ct_pct", "Capital de trabajo % ingresos", PCT),
        ("ct", "Capital de trabajo neto", MM),
        ("dct", "(-) Aumento de capital de trabajo", MM),
        ("fcff", "FCFF = NOPAT + Dep − Capex − ΔCT", MM),
        (None, "", None),
        ("fd", "Factor de descuento = 1/(1+WACC)^período", "0.0000"),
        ("vp", "Valor presente del FCFF", MM),
    ]
    r = 5
    for clave, etiqueta, _ in filas_def:
        if clave:
            F[clave] = r
            celda(ws, f"A{r}", etiqueta, NEGRITA if clave in ("fcff", "ebitda", "nopat") else NEGRO)
        r += 1

    # Año base (histórico, verde = viene de otra hoja)
    b = col_base
    celda(ws, f"B{F['ingresos']}", f"=Historico!{b}{H['ingresos']}", VERDE, MM)
    celda(ws, f"B{F['ebitda']}", f"=Historico!{b}{H['ebitda']}", VERDE, MM)
    celda(ws, f"B{F['mg']}", f"=Historico!{b}{H['mg']}", VERDE, PCT)
    celda(ws, f"B{F['ct']}", f"=Historico!{b}{H['capital_trabajo']}", VERDE, MM)

    for i, c in enumerate(cols):
        p = get_column_letter(2 + i)        # columna anterior
        s = get_column_letter(3 + i)        # columna del supuesto anual en Supuestos
        fx = {
            "crec": (f"=Supuestos!{s}{anual('operacion.crecimiento_ingresos')}", VERDE, PCT),
            "ingresos": (f"={p}{F['ingresos']}*(1+{c}{F['crec']})", NEGRO, MM),
            "mg": (f"=Supuestos!{s}{anual('operacion.margen_ebitda')}", VERDE, PCT),
            "ebitda": (f"={c}{F['ingresos']}*{c}{F['mg']}", NEGRO, MM),
            "dep_pct": (f"=Supuestos!{s}{anual('operacion.depreciacion_pct_ingresos')}", VERDE, PCT),
            "dep": (f"={c}{F['ingresos']}*{c}{F['dep_pct']}", NEGRO, MM),
            "ebit": (f"={c}{F['ebitda']}-{c}{F['dep']}", NEGRO, MM),
            "t": (f"={S['operacion.tasa_impuesto']}", VERDE, PCT),
            "imp": (f"={c}{F['ebit']}*{c}{F['t']}", NEGRO, MM),
            "nopat": (f"={c}{F['ebit']}-{c}{F['imp']}", NEGRO, MM),
            "dep2": (f"={c}{F['dep']}", NEGRO, MM),
            "capex_pct": (f"=Supuestos!{s}{anual('operacion.capex_pct_ingresos')}", VERDE, PCT),
            "capex": (f"={c}{F['ingresos']}*{c}{F['capex_pct']}", NEGRO, MM),
            "ct_pct": (f"=Supuestos!{s}{anual('operacion.capital_trabajo_pct_ingresos')}", VERDE, PCT),
            "ct": (f"={c}{F['ingresos']}*{c}{F['ct_pct']}", NEGRO, MM),
            "dct": (f"={c}{F['ct']}-{p}{F['ct']}", NEGRO, MM),
            "fcff": (f"={c}{F['nopat']}+{c}{F['dep2']}-{c}{F['capex']}-{c}{F['dct']}", NEGRO, MM),
            "fd": (f"=1/(1+WACC!$C$18)^{c}4", VERDE, "0.0000"),
            "vp": (f"={c}{F['fcff']}*{c}{F['fd']}", NEGRO, MM),
        }
        for clave, (f, fuente, fmt) in fx.items():
            celda(ws, f"{c}{F[clave]}", f, fuente, fmt, negrita=clave == "fcff")
    for col in ["A"] + ["B"] + cols:
        ws[f"{col}{F['fcff']}"].border = BORDE_SUP
    anchos(ws, {"A": 46, "B": 13, **{c: 13 for c in cols}})
    ws.freeze_panes = "B4"
    return F, cols


def hoja_wacc(wb, S):
    ws = wb.create_sheet("WACC")
    titulo(ws, "Costo de capital", "DATOS SIMULADOS. CAPM + Hamada. El WACC descuenta el FCFF del retail; el Ke del banco descuenta su patrimonio.")
    encabezado(ws, 4, ["Concepto", "Fórmula", "Valor"])
    filas = [
        (5, "Tasa libre de riesgo (rf)", "Supuesto", f"={S['wacc.tasa_libre_riesgo']}", VERDE, PCT2),
        (6, "Beta desapalancada (βu)", "Supuesto", f"={S['wacc.beta_desapalancada']}", VERDE, "0.00"),
        (7, "Premio por riesgo de mercado (ERP)", "Supuesto", f"={S['wacc.premio_riesgo_mercado']}", VERDE, PCT2),
        (8, "Riesgo país (CRP)", "Supuesto", f"={S['wacc.riesgo_pais']}", VERDE, PCT2),
        (9, "Deuda / (Deuda + Patrimonio)", "Supuesto", f"={S['wacc.deuda_sobre_capital_total']}", VERDE, PCT),
        (10, "Tasa de impuesto (t)", "Supuesto", f"={S['wacc.tasa_impuesto_escudo']}", VERDE, PCT),
        (11, "Deuda / Patrimonio (D/E)", "D/V ÷ (1 − D/V)", "=C9/(1-C9)", NEGRO, "0.00"),
        (12, "Beta apalancada (βL)", "βu × (1 + (1−t) × D/E)   [Hamada]", "=C6*(1+(1-C10)*C11)", NEGRO, "0.00"),
        (13, "Costo del patrimonio (Ke)", "rf + βL × ERP + CRP   [CAPM]", "=C5+C12*C7+C8", NEGRO, PCT2),
        (14, "Costo de la deuda antes de impuesto (Kd)", "Supuesto", f"={S['wacc.costo_deuda_antes_impuesto']}", VERDE, PCT2),
        (15, "Costo de la deuda después de impuesto", "Kd × (1 − t)", "=C14*(1-C10)", NEGRO, PCT2),
        (16, "Peso del patrimonio E/V", "1 − D/V", "=1-C9", NEGRO, PCT),
        (17, "Peso de la deuda D/V", "", "=C9", NEGRO, PCT),
        (18, "WACC", "E/V × Ke + D/V × Kd × (1 − t)", "=C16*C13+C17*C15", NEGRO, PCT2),
        (20, "Beta del banco (apalancada)", "Supuesto", f"={S['banco.beta_banco']}", VERDE, "0.00"),
        (21, "Ke del banco", "rf + β banco × ERP + CRP", "=C5+C20*C7+C8", NEGRO, PCT2),
    ]
    for r, a, b, c, f, fmt in filas:
        celda(ws, f"A{r}", a, NEGRITA if r in (13, 18, 21) else NEGRO)
        celda(ws, f"B{r}", b, Font(name=FUENTE, italic=True, color="595959"))
        celda(ws, f"C{r}", c, f, fmt, negrita=r in (13, 18, 21))
    ws["C18"].fill = GRIS
    ws["A18"].comment = Comment("El WACC usa pesos de MERCADO y estructura OBJETIVO, no los valores contables de hoy.", "Guía")
    anchos(ws, {"A": 42, "B": 40, "C": 12})


def hoja_valoracion(wb, S, H, col_base, F, cols):
    ws = wb.create_sheet("Valoracion")
    titulo(ws, "Valoración por suma de partes — MM CLP", "DATOS SIMULADOS. No es recomendación de inversión.")
    u = cols[-1]
    encabezado(ws, 4, ["Concepto", "Valor", "Nota"])
    filas = [
        (5, "A. Negocio NO bancario (DCF)", None, None, None, ""),
        (6, "Suma VP de FCFF 2026-2030", f"=SUM(Proyeccion!{cols[0]}{F['vp']}:{u}{F['vp']})", VERDE, MM, ""),
        (7, "FCFF último año proyectado", f"=Proyeccion!{u}{F['fcff']}", VERDE, MM, ""),
        (8, "WACC", "=WACC!C18", VERDE, PCT2, ""),
        (9, "Crecimiento perpetuo (g)", f"={S['terminal.crecimiento_perpetuo']}", VERDE, PCT2, "Debe ser < WACC"),
        (10, "Valor terminal en 2030", "=B7*(1+B9)/(B8-B9)", NEGRO, MM, "Gordon: FCFF(n+1) / (WACC − g)"),
        (11, "VP del valor terminal", f"=B10/(1+B8)^Proyeccion!{u}4", NEGRO, MM, ""),
        (12, "Valor empresa (EV) no bancario", "=B6+B11", NEGRO, MM, ""),
        (13, "% del EV que es valor terminal", "=B11/B12", NEGRO, PCT, "Típico 60-80%; si es >85% el modelo depende demasiado de g"),
        (14, "EV/EBITDA implícito en el terminal", f"=B10/(Proyeccion!{u}{F['ebitda']}*(1+B9))", NEGRO, MULT, "Comparar con múltiplos de comparables"),
        (16, "B. Negocio financiero (por patrimonio)", None, None, None, ""),
        (17, "Patrimonio contable año base", f"=Historico!{col_base}{H['patrimonio_banco']}", VERDE, MM, ""),
        (18, "ROE sostenible", f"={S['banco.roe_sostenible']}", VERDE, PCT, ""),
        (19, "Ke del banco", "=WACC!C21", VERDE, PCT2, ""),
        (20, "g banco", f"={S['banco.crecimiento_perpetuo']}", VERDE, PCT2, ""),
        (21, "P/VL justificado", "=(B18-B20)/(B19-B20)", NEGRO, MULT, "(ROE − g)/(Ke − g): si ROE > Ke, vale más que su libro"),
        (22, "Valor del negocio financiero", "=B17*B21", NEGRO, MM, ""),
        (24, "C. Puente a valor por acción", None, None, None, ""),
        (25, "EV no bancario", "=B12", NEGRO, MM, ""),
        (26, "(−) Deuda financiera no bancaria", f"=-{S['puente.deuda_financiera_no_bancaria']}", VERDE, MM, "Sin deuda del banco ni arriendos (IFRS 16)"),
        (27, "(+) Caja no bancaria", f"={S['puente.caja_no_bancaria']}", VERDE, MM, ""),
        (28, "(−) Participaciones no controladoras", f"=-{S['puente.participaciones_no_controladoras']}", VERDE, MM, "Parte de filiales que no es de Falabella"),
        (29, "(+) Inversiones en asociadas", f"={S['puente.inversiones_asociadas']}", VERDE, MM, "No están en el FCFF"),
        (30, "(+) Valor del negocio financiero", "=B22", NEGRO, MM, ""),
        (31, "Valor del patrimonio (accionistas)", "=SUM(B25:B30)", NEGRO, MM, ""),
        (32, "Acciones en circulación (millones)", f"={S['puente.acciones_en_circulacion_mm']}", VERDE, "#,##0", ""),
        (33, "Valor por acción (CLP)", "=B31/B32", NEGRO, "#,##0", ""),
        (34, "Precio de mercado (CLP)", f"={S['puente.precio_mercado']}", VERDE, "#,##0", "SIMULADO"),
        (35, "Potencial al alza / (a la baja)", "=B33/B34-1", NEGRO, PCT, ""),
    ]
    for r, a, f, fuente, fmt, nota in filas:
        if f is None:
            celda(ws, f"A{r}", a, NEGRITA, relleno=GRIS)
            ws[f"B{r}"].fill = GRIS
            ws[f"C{r}"].fill = GRIS
            continue
        neg = r in (12, 22, 31, 33, 35)
        celda(ws, f"A{r}", a, NEGRITA if neg else NEGRO)
        celda(ws, f"B{r}", f, fuente, fmt, negrita=neg)
        celda(ws, f"C{r}", nota, Font(name=FUENTE, italic=True, size=9, color="595959"))
    ws["B31"].border = BORDE_SUP
    ws["B33"].fill = AMARILLO
    anchos(ws, {"A": 42, "B": 16, "C": 62})


def hoja_sensibilidad(wb, cfg, F, cols):
    ws = wb.create_sheet("Sensibilidad")
    titulo(ws, "Sensibilidad del valor por acción (CLP) a WACC y g", "DATOS SIMULADOS. Cada celda recalcula toda la valoración con ese par WACC/g.")
    dw, dg = cfg["sensibilidad"]["wacc_delta"], cfg["sensibilidad"]["g_delta"]
    u = cols[-1]
    celda(ws, "A4", "Δ g →", NEGRITA)
    celda(ws, "A5", "Δ WACC ↓", NEGRITA)
    celda(ws, "B5", "WACC \\ g", NEGRITA)
    for j, d in enumerate(dg):
        c = get_column_letter(3 + j)
        celda(ws, f"{c}4", d, AZUL, PCT2)
        celda(ws, f"{c}5", f"=Valoracion!$B$9+{c}4", NEGRO, PCT2, GRIS, negrita=True)
    for i, d in enumerate(dw):
        r = 6 + i
        celda(ws, f"A{r}", d, AZUL, PCT2)
        celda(ws, f"B{r}", f"=Valoracion!$B$8+A{r}", NEGRO, PCT2, GRIS, negrita=True)
        for j in range(len(dg)):
            c = get_column_letter(3 + j)
            fcff = f"Proyeccion!${cols[0]}${F['fcff']}:${u}${F['fcff']}"
            per = f"Proyeccion!${cols[0]}$4:${u}$4"
            ev = (f"SUMPRODUCT({fcff}/(1+$B{r})^{per})"
                  f"+Proyeccion!${u}${F['fcff']}*(1+{c}$5)/($B{r}-{c}$5)/(1+$B{r})^Proyeccion!${u}$4")
            puente = "+SUM(Valoracion!$B$26:$B$30)"
            celda(ws, f"{c}{r}", f"=({ev}{puente})/Valoracion!$B$32", NEGRO, "#,##0")
    centro = f"{get_column_letter(3 + len(dg) // 2)}{6 + len(dw) // 2}"
    ws[centro].font = Font(name=FUENTE, bold=True)
    ws[centro].border = Border(*(Side(style="medium"),) * 4)
    ultimo = f"{get_column_letter(2 + len(dg))}{5 + len(dw)}"
    ws.conditional_formatting.add(f"C6:{ultimo}", ColorScaleRule(start_type="min", start_color="F8696B",
                                                                 mid_type="percentile", mid_value=50, mid_color="FFEB84",
                                                                 end_type="max", end_color="63BE7B"))
    r = 7 + len(dw)
    celda(ws, f"A{r}", "Precio de mercado (CLP):", NEGRITA)
    celda(ws, f"C{r}", "=Valoracion!B34", VERDE, "#,##0")
    celda(ws, f"A{r+1}", "Lectura: celdas sobre el precio de mercado = la acción estaría barata con ese par de supuestos. Celda con borde = caso base.",
          Font(name=FUENTE, italic=True, size=9))
    anchos(ws, {"A": 12, "B": 12, **{get_column_letter(3 + j): 12 for j in range(len(dg))}})


def hoja_checks(wb, S, F, cols, valor_python):
    ws = wb.create_sheet("Checks")
    titulo(ws, "Controles de razonabilidad", "Un modelo sin checks es un modelo en el que no se puede confiar.")
    encabezado(ws, 4, ["Control", "Valor", "¿OK?", "Por qué importa"])
    u = cols[-1]
    checks = [
        ("g < WACC", "=Valoracion!B8-Valoracion!B9", PCT2, "=IF(B5>0,\"OK\",\"ERROR\")", "Si g ≥ WACC la fórmula de Gordon explota (valor infinito o negativo)."),
        ("g ≤ 4% (crecimiento nominal LP razonable en CLP)", "=Valoracion!B9", PCT2, "=IF(B6<=0.04,\"OK\",\"REVISAR\")", "Ninguna empresa crece para siempre más que la economía."),
        ("% del EV en valor terminal", "=Valoracion!B13", PCT, "=IF(B7<=0.85,\"OK\",\"REVISAR\")", "Si es muy alto, la valoración es casi solo un supuesto de g y WACC."),
        ("EV/EBITDA terminal vs referencia", "=Valoracion!B14", MULT, f"=IF(ABS(B8/{S['terminal.multiplo_salida_referencia']}-1)<=0.3,\"OK\",\"REVISAR\")", "El múltiplo implícito debe parecerse a comparables (±30%)."),
        ("Capex / Depreciación último año", f"=Proyeccion!{u}{F['capex']}/Proyeccion!{u}{F['dep']}", MULT, "=IF(B9>=1,\"OK\",\"REVISAR\")", "Para crecer a perpetuidad hay que invertir al menos lo que se deprecia."),
        ("Crecimiento último año vs g", f"=Proyeccion!{u}{F['crec']}-Valoracion!B9", PCT2, "=IF(ABS(B10)<=0.015,\"OK\",\"REVISAR\")", "El último año proyectado debe estar cerca del estado estable."),
        ("FCFF positivos en la proyección", f"=MIN(Proyeccion!{cols[0]}{F['fcff']}:{u}{F['fcff']})", MM, "=IF(B11>0,\"OK\",\"REVISAR\")", "No es error per se, pero exige explicación."),
        ("Valor por acción según Python (src/modelo_dcf.py)", valor_python, "#,##0.00", "=IF(ABS(B12-Valoracion!B33)<0.5,\"OK\",\"ERROR\")", "Reconciliación: dos implementaciones independientes deben dar lo mismo."),
    ]
    for i, (a, f, fmt, ok, why) in enumerate(checks):
        r = 5 + i
        celda(ws, f"A{r}", a)
        celda(ws, f"B{r}", f, AZUL if isinstance(f, float) else VERDE, fmt)
        celda(ws, f"C{r}", ok, NEGRO, negrita=True)
        celda(ws, f"D{r}", why, Font(name=FUENTE, size=9))
    anchos(ws, {"A": 48, "B": 14, "C": 10, "D": 75})


def hoja_fuentes(wb):
    ws = wb.create_sheet("Fuentes")
    titulo(ws, "Mapa de fuentes (data/mapa_fuentes.csv)", "Hoy todo es SIMULADO. Esta tabla dice dónde buscar cada dato real para reemplazarlo.")
    df = pd.read_csv(RAIZ / "data" / "mapa_fuentes.csv").fillna("")
    encabezado(ws, 4, list(df.columns))
    for i, fila in enumerate(df.itertuples(index=False), start=5):
        for j, x in enumerate(fila, start=1):
            c = ws.cell(row=i, column=j, value=x)
            c.font = Font(name=FUENTE, size=9)
            c.alignment = Alignment(wrap_text=True, vertical="top")
    anchos(ws, {"A": 20, "B": 26, "C": 40, "D": 50, "E": 50})


def main() -> None:
    cfg, hist = cargar()
    proy = proyectar(cfg, hist)
    res = valorizar(cfg, hist, proy, costo_capital(cfg))

    wb = Workbook()
    hoja_leeme(wb)
    hoja_fuentes(wb)
    H, col_base = hoja_historico(wb, hist)
    S, Sfila = hoja_supuestos(wb, cfg)
    F, cols = hoja_proyeccion(wb, cfg, S, Sfila, H, col_base)
    hoja_wacc(wb, S)
    hoja_valoracion(wb, S, H, col_base, F, cols)
    hoja_sensibilidad(wb, cfg, F, cols)
    hoja_checks(wb, S, F, cols, round(float(res["valor_por_accion"]), 4))

    # Orden de pestañas = orden del proceso.
    orden = ["Leeme", "Fuentes", "Historico", "Supuestos", "Proyeccion", "WACC", "Valoracion", "Sensibilidad", "Checks"]
    wb._sheets = [wb[n] for n in orden]
    wb.calculation.fullCalcOnLoad = True  # Excel recalcula todo al abrir
    SALIDA.parent.mkdir(exist_ok=True)
    wb.save(SALIDA)
    # Resultados clave para el registro en Word (src/construir_word.js).
    tasas = costo_capital(cfg)
    resumen = {k: float(x) for k, x in {**tasas, **res}.items()}
    resumen["precio_mercado"] = cfg["puente"]["precio_mercado"]["valor"]
    (RAIZ / "outputs" / "resultados.json").write_text(json.dumps(resumen, indent=2), encoding="utf-8")
    print(f"Excel escrito en {SALIDA.relative_to(RAIZ)} (valor por acción Python: {res['valor_por_accion']:,.2f} CLP)")


if __name__ == "__main__":
    main()
