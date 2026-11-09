// Construye docs/Guia_y_Registro_DCF.docx: guía paso a paso + registro de decisiones.
// Uso: node src/construir_word.js   (después de python src/construir_excel.py)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType,
  ShadingType, HeadingLevel, AlignmentType, LevelFormat, BorderStyle,
  Footer, PageNumber,
} = require("docx");

const RAIZ = path.resolve(__dirname, "..");
const R = JSON.parse(fs.readFileSync(path.join(RAIZ, "outputs", "resultados.json"), "utf8"));
const FECHA = "9 de noviembre de 2026";
const ANCHO = 9026; // A4 con márgenes de 1 pulgada (DXA)

// ------------------------------------------------------------ helpers
const pct = (x, d = 1) => (x * 100).toFixed(d).replace(".", ",") + "%";
const mm = (x) => Math.round(x).toLocaleString("es-CL");
const t = (text, o = {}) => new TextRun({ text, ...o });
const P = (...runs) => new Paragraph({ spacing: { after: 120 }, children: runs.map((r) => (typeof r === "string" ? t(r) : r)) });
const H1 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [t(s)] });
const H2 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [t(s)] });
const H3 = (s) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [t(s)] });
const B = (...runs) => new Paragraph({ numbering: { reference: "vinetas", level: 0 }, spacing: { after: 60 },
  children: runs.map((r) => (typeof r === "string" ? t(r) : r)) });
const N = (ref, s) => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 60 }, children: [t(s)] });
const etiqueta = (e, s) => P(t(e + " ", { bold: true }), s);
const aviso = (s) => new Paragraph({
  spacing: { before: 120, after: 160 },
  border: { left: { style: BorderStyle.SINGLE, size: 18, color: "C00000", space: 8 } },
  children: [t(s, { italics: true, color: "C00000" })],
});

const borde = { style: BorderStyle.SINGLE, size: 4, color: "BFBFBF" };
const bordes = { top: borde, bottom: borde, left: borde, right: borde };
function tabla(cabecera, filas, anchos) {
  const total = anchos.reduce((a, b) => a + b, 0);
  const celdaT = (txt, i, head) => new TableCell({
    borders: bordes, width: { size: anchos[i], type: WidthType.DXA },
    shading: head ? { fill: "1F3864", type: ShadingType.CLEAR, color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 100, right: 100 },
    children: [new Paragraph({ children: [t(String(txt), head ? { bold: true, color: "FFFFFF", size: 18 } : { size: 18 })] })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: anchos,
    rows: [
      new TableRow({ tableHeader: true, children: cabecera.map((c, i) => celdaT(c, i, true)) }),
      ...filas.map((f) => new TableRow({ children: f.map((c, i) => celdaT(c, i, false)) })),
    ],
  });
}
const espacio = () => new Paragraph({ spacing: { after: 120 }, children: [] });

// ------------------------------------------------------------ contenido
const pasos = [
  {
    t: "Paso 1 — Entender el negocio y definir el alcance",
    obj: "Saber QUÉ estás valorizando antes de abrir el Excel.",
    hacer: ["Lee la memoria anual y la presentación de resultados: segmentos, países, de dónde viene la utilidad.",
      "Identifica negocios que NO se valorizan con FCFF: bancos, aseguradoras (su deuda es materia prima).",
      "Decide el método: DCF consolidado, suma de partes (SOTP) o excluir partes. Escríbelo en el registro."],
    concepto: "Suma de partes (SOTP, sum-of-the-parts): valorizar cada negocio con el método que le corresponde y sumar.",
    excel: "Hoja Leeme.",
    ojo: "Error típico: meter el banco dentro del FCFF y restar sus depósitos como deuda. Destruye el valor dos veces.",
    ej: "Elige otra empresa chilena (Cencosud, Ripley, Parque Arauco) y escribe en 5 líneas qué segmentos tiene y cuál requiere otro método.",
  },
  {
    t: "Paso 2 — Reunir datos y registrar fuentes",
    obj: "Que cada número del modelo tenga un origen verificable.",
    hacer: ["Descarga 3-5 años de estados financieros auditados (CMF) y la nota de segmentos.",
      "Anota en mapa_fuentes.csv: partida, documento, nota y página.",
      "Separa insumos (azul) de cálculos (negro) desde el primer minuto."],
    concepto: "Trazabilidad (audit trail): cualquiera debe poder ir del resultado a la fuente.",
    excel: "Hojas Fuentes e Historico. Archivo data/mapa_fuentes.csv.",
    ojo: "Error típico: mezclar cifras de prensa con EEFF; usar unidades distintas (MM$ vs miles de $).",
    ej: "Sin mirar la hoja Fuentes, escribe de qué estado financiero sale el capex y de cuál el capital de trabajo.",
  },
  {
    t: "Paso 3 — Analizar el histórico",
    obj: "Entender los motores de valor (value drivers) antes de proyectarlos.",
    hacer: ["Calcula crecimiento, margen EBITDA, depreciación, capex y capital de trabajo como % de ingresos.",
      "Busca años atípicos (pandemia, cierre de tiendas, deterioros) y normalízalos (no extrapoles un año raro).",
      "Calcula promedios: son el ancla para tus supuestos."],
    concepto: "EBITDA: resultado operacional antes de depreciación y amortización; aproxima la caja que genera la operación.",
    excel: "Hoja Historico, bloque Cálculos y columna Promedio.",
    ojo: "Con IFRS 16 (norma de arriendos) el EBITDA reportado EXCLUYE los arriendos. Aquí usamos EBITDA DESPUÉS de arriendos: hay que ser consistente en todo el modelo.",
    ej: "Calcula a mano el margen EBITDA 2025 y compáralo con el Excel.",
  },
  {
    t: "Paso 4 — Proyectar la operación",
    obj: "Traducir una historia del negocio en números.",
    hacer: ["Propón crecimiento de ingresos año a año. Ancla: inflación + crecimiento real + iniciativas.",
      "Propón margen EBITDA, capex y capital de trabajo como % de ingresos.",
      "Converge al final del horizonte hacia un estado estable (steady state)."],
    concepto: "Horizonte explícito: años con supuestos detallados (aquí 5). Después, el valor terminal.",
    excel: "Hoja Supuestos (amarillo) → Proyeccion.",
    ojo: "Error típico: el palo de hockey (hockey stick): márgenes que suben sin explicación. Pregúntate: ¿qué tiene que pasar en el negocio para lograrlo?",
    ej: "ANTES de mirar Supuestos, escribe tu crecimiento y margen para 2026-2030 y justifícalos en 1 línea cada uno. Luego compara.",
  },
  {
    t: "Paso 5 — Calcular el flujo de caja libre (FCFF)",
    obj: "Pasar de utilidad contable a caja disponible para accionistas y acreedores.",
    hacer: ["EBIT = EBITDA − depreciación.",
      "NOPAT = EBIT × (1 − t). Impuesto sobre el EBIT, NO sobre la utilidad (los intereses van en el WACC).",
      "FCFF = NOPAT + depreciación − capex − aumento del capital de trabajo."],
    concepto: "FCFF (free cash flow to the firm): caja después de impuestos e inversiones, antes de pagar a los financistas.",
    excel: "Hoja Proyeccion, filas NOPAT a FCFF.",
    ojo: "Error típico: restar intereses en el FCFF y además descontar con WACC (doble conteo del escudo tributario).",
    ej: "Recalcula el FCFF 2026 en una hoja en blanco con solo 4 números: ingresos, margen, capex %, CT %.",
  },
  {
    t: "Paso 6 — Costo del patrimonio (Ke) con CAPM",
    obj: "Estimar el retorno que exige el accionista.",
    hacer: ["Ke = rf + βL × ERP (+ riesgo país si rf no es local).",
      "Toma una beta desapalancada (βu) de comparables y reapaláncala con tu estructura objetivo (fórmula de Hamada).",
      "Usa rf y ERP de la MISMA moneda que los flujos (aquí pesos)."],
    concepto: "Beta: sensibilidad de la acción al mercado. Desapalancar = quitar el efecto de la deuda para comparar empresas.",
    excel: "Hoja WACC, filas 5-13.",
    ojo: "Error típico: sumar riesgo país con una rf chilena (doble conteo), o mezclar rf en dólares con flujos en pesos.",
    ej: "Con βu = 0,8, D/E = 0,54 y t = 27%, calcula βL a mano. (Respuesta en la hoja WACC.)",
  },
  {
    t: "Paso 7 — WACC",
    obj: "Una tasa que refleje a TODOS los financistas, en proporción a su peso.",
    hacer: ["Kd = rendimiento de mercado de la deuda (no la tasa contable).",
      "Pesos a valor de MERCADO y estructura OBJETIVO de largo plazo.",
      "WACC = E/V × Ke + D/V × Kd × (1 − t)."],
    concepto: "Escudo tributario: los intereses reducen impuestos; por eso Kd va multiplicado por (1 − t).",
    excel: "Hoja WACC, fila 18.",
    ojo: "Error típico: usar valor libro del patrimonio para los pesos. Y olvidar que más deuda sube βL: el WACC no baja tanto como parece.",
    ej: "Cambia D/V de 35% a 50% en Supuestos y explica por qué el WACC casi no se mueve.",
  },
  {
    t: "Paso 8 — Valor terminal",
    obj: "Valorizar todo lo que pasa después del año 5 (normalmente 60-80% del valor).",
    hacer: ["Gordon: VT = FCFF(n) × (1 + g) / (WACC − g).",
      "g nominal ≤ crecimiento de largo plazo de la economía (inflación ~3% + algo real).",
      "Contrasta con el EV/EBITDA implícito vs comparables."],
    concepto: "Perpetuidad creciente: un flujo que crece a g para siempre vale flujo/(tasa − g).",
    excel: "Hoja Valoracion, filas 9-14.",
    ojo: "Error típico: g muy alto o año terminal no estable (capex < depreciación con g > 0 es incoherente).",
    ej: `Con WACC ${pct(R.wacc, 2)} y g 3%, ¿cuánto cambia el valor por acción si g sube 0,5 pp? Búscalo en Sensibilidad.`,
  },
  {
    t: "Paso 9 — Negocio financiero por patrimonio",
    obj: "Valorizar el banco como banco.",
    hacer: ["Ke banco con beta APALANCADA de bancos comparables.",
      "P/VL justificado = (ROE − g) / (Ke − g).",
      "Valor = P/VL × patrimonio contable."],
    concepto: "P/VL (precio/valor libro): si el banco rinde más que lo que exige el accionista (ROE > Ke), vale más que su libro.",
    excel: "Hoja Valoracion, bloque B.",
    ojo: "Error típico: usar el WACC para el banco, o un ROE de un año excepcional (normalizar por ciclo de riesgo de crédito).",
    ej: "¿Qué ROE hace que P/VL = 1? (Pista: ROE = Ke.)",
  },
  {
    t: "Paso 10 — Puente a valor por acción",
    obj: "Pasar del valor del negocio al valor de UNA acción.",
    hacer: ["EV − deuda financiera neta − minoritarios + asociadas + valor banco = patrimonio.",
      "Patrimonio / acciones en circulación = valor por acción.",
      "Compara con el precio de mercado a la MISMA fecha."],
    concepto: "Valor empresa (EV) vs valor patrimonio: el EV pertenece a accionistas y acreedores; el patrimonio solo a accionistas.",
    excel: "Hoja Valoracion, bloque C.",
    ojo: "Error típico: olvidar los minoritarios (participaciones no controladoras) o restar la deuda del banco.",
    ej: "Explica en voz alta, en 60 segundos, cada línea del puente.",
  },
  {
    t: "Paso 11 — Sensibilidad y escenarios",
    obj: "Mostrar un rango, no un número mágico.",
    hacer: ["Tabla WACC × g.", "Escenarios (pesimista/base/optimista) moviendo crecimiento y margen juntos.",
      "Identifica qué supuesto mueve más el valor."],
    concepto: "Análisis de sensibilidad: cuánto cambia el resultado ante cambios en un supuesto.",
    excel: "Hoja Sensibilidad.",
    ojo: "Error típico: presentar un precio objetivo con decimales como si fuera preciso.",
    ej: "¿Qué combinaciones de WACC y g justifican el precio de mercado? Márcalas en la tabla.",
  },
  {
    t: "Paso 12 — Controles y comunicación",
    obj: "Que el modelo sea confiable y que la conclusión se entienda en 30 segundos.",
    hacer: ["Revisa la hoja Checks: todo en OK o explicado.", "Reconcilia Excel vs Python.",
      "Escribe la conclusión: valor, rango, 2-3 supuestos que la mueven, riesgos."],
    concepto: "Sanity check (control de razonabilidad): ¿el resultado tiene sentido frente a múltiplos, historia y mercado?",
    excel: "Hoja Checks.",
    ojo: "Error típico: confiar en el número porque 'el Excel no tiene errores'. Sin #REF! no significa correcto.",
    ej: "Escribe la conclusión del caso en 3 líneas, como para un comité de inversión.",
  },
];

const buenasPracticas = [
  ["Un solo lugar para supuestos", "config/supuestos.yaml y hoja Supuestos. Nunca un número escrito dentro de una fórmula."],
  ["Colores estándar", "Azul = insumo, negro = fórmula, verde = vínculo a otra hoja, amarillo = supuesto clave."],
  ["Consistencia de moneda e inflación", "Flujos nominales en CLP → tasas nominales en CLP. Reales con reales."],
  ["Consistencia flujo-tasa", "FCFF con WACC; flujo al accionista (FCFE) o dividendos con Ke."],
  ["Consistencia IFRS 16", "Si el EBITDA es post arriendos, no restes pasivos por arriendo. Si es pre, réstalos y ajusta el WACC."],
  ["Estado estable en el año terminal", "Crecimiento ≈ g, capex ≥ depreciación, margen sostenible."],
  ["Pesos de mercado y estructura objetiva", "En el WACC, no los valores contables."],
  ["Normalizar el histórico", "Quitar efectos no recurrentes antes de promediar."],
  ["Fechas consistentes", "Fecha de valoración = fecha de deuda, caja, acciones y precio."],
  ["Mostrar rangos", "Sensibilidad y escenarios; nunca un único número."],
  ["Reconciliar", "Dos cálculos independientes (Excel y Python) deben coincidir."],
  ["Registrar decisiones", "Qué se decidió, alternativas y por qué (este documento)."],
];

const errores = [
  ["Banco dentro del FCFF", "Valor muy bajo o negativo", "Suma de partes; banco por patrimonio"],
  ["Doble conteo del escudo tributario", "Valor inflado", "NOPAT sin intereses; escudo solo en el WACC"],
  ["g ≥ WACC o g muy alto", "Valor terminal explosivo", "g ≤ crecimiento nominal de LP; check g < WACC"],
  ["Riesgo país sumado dos veces", "WACC muy alto", "Si rf es BCP en pesos, CRP = 0"],
  ["Monedas mezcladas", "Resultados sin sentido", "Flujos y tasas en la misma moneda"],
  ["Olvidar minoritarios", "Valor por acción inflado", "Restar participaciones no controladoras"],
  ["Capex < depreciación con crecimiento", "Valor terminal inflado", "Capex/Dep ≥ 1 en el año terminal"],
  ["Billón vs billion", "Error de escala ×1.000", "Billón (ES) = 10¹²; billion (EN) = 10⁹"],
];

const decisiones = [
  ["08-oct-2026", "Alcance: suma de partes", "DCF consolidado; excluir banco", "Un banco no se valoriza con FCFF/WACC: su deuda es operativa."],
  ["09-nov-2026", "Usar datos SIMULADOS", "Esperar datos reales de la CMF", "El objetivo es aprender el proceso; el mapa de fuentes permite reemplazarlos después."],
  ["09-nov-2026", "EBITDA después de arriendos (pre-IFRS 16)", "EBITDA IFRS 16 + pasivos por arriendo como deuda", "Más simple y consistente; evita proyectar derechos de uso."],
  ["09-nov-2026", "Convención de fin de año", "Mitad de año (mid-year)", "Más simple para aprender; mid-year sube el valor empresa en (1+WACC)^0,5 − 1 ≈ 4-5%."],
  ["09-nov-2026", "rf en pesos (BCP) y riesgo país = 0", "rf EE.UU. + riesgo país + diferencial de inflación", "Flujos en CLP nominales: la tasa debe estar en la misma moneda."],
  ["09-nov-2026", "Minoritarios a valor libro", "Valor de mercado de la parte no controladora", "Simplificación; anotada como mejora pendiente."],
  ["09-nov-2026", "Banco por P/VL justificado", "Residual income / FCFE", "Conecta ROE y Ke en una fórmula; mejora futura: residual income."],
];

const supuestosTabla = [
  ["Crecimiento de ingresos 2026-30", "6,0% → 4,0%", "Converge a g; histórico simulado ~5,7%"],
  ["Margen EBITDA", "9,5% → 10,0%", "Recupera hacia promedio histórico ~10,2%"],
  ["Capex % ingresos", "4,0% → 3,5%", "Histórico ~4,0%; capex/dep > 1"],
  ["Capital de trabajo % ingresos", "8,0%", "Histórico ~8,1%"],
  ["Tasa de impuesto", "27%", "Primera categoría Chile"],
  ["Tasa libre de riesgo", "5,5%", "SIMULADO (real: BCP 10 años)"],
  ["Beta desapalancada", "0,80", "SIMULADO (real: comparables)"],
  ["Premio por riesgo de mercado", "6,0%", "SIMULADO (real: Damodaran)"],
  ["Kd antes de impuesto", "7,0%", "SIMULADO (real: bonos de mercado)"],
  ["D/(D+E) objetivo", "35%", "SIMULADO"],
  ["Crecimiento perpetuo g", "3,0%", "Meta de inflación BCCh + ~0% real"],
  ["ROE sostenible banco", "15%", "Histórico simulado ~14,8%"],
];

const practica = [
  ["Día 1", "Recorre el Excel hoja por hoja con 'Rastrear precedentes'. Lee este documento.", "60 min", "Puedes explicar cada hoja en 1 frase."],
  ["Día 2", "Rehaz el FCFF y el WACC en una hoja EN BLANCO usando solo la hoja Supuestos.", "45 min", "Tu FCFF y WACC coinciden con el modelo."],
  ["Día 4", "Cambia 3 supuestos (margen, WACC, g) y anota el impacto en el valor por acción.", "30 min", "Sabes cuál mueve más el valor y por qué."],
  ["Día 7", "DCF completo en blanco con datos simulados nuevos (cambia la semilla en el YAML).", "45 min", "Terminas con valor por acción + 1 check."],
  ["Día 14", "Repite con otra empresa (simulada o real).", "45 min", "Lo haces sin mirar la guía."],
  ["Día 30", "Explica el DCF en voz alta en 3 minutos, como en entrevista. Grábate.", "15 min", "Cubres alcance, FCFF, WACC, VT, puente y sensibilidad."],
];

const entrevista = [
  ["¿Por qué no valorizas el banco con el WACC?", "Porque para un banco la deuda es materia prima, no financiamiento. Se valoriza el patrimonio con Ke."],
  ["¿Qué pesa más en tu valor?", `El valor terminal (${pct(R.vp_terminal / R.ev, 0)} del EV), por eso muestro sensibilidad a WACC y g.`],
  ["¿Por qué el impuesto se calcula sobre el EBIT?", "Porque el beneficio tributario de la deuda ya está en el WACC; ponerlo en el flujo sería contarlo dos veces."],
  ["¿Cómo elegiste g?", "Nominal en pesos ≈ meta de inflación; no puede superar el crecimiento de la economía en el largo plazo."],
  ["¿Cómo trataste IFRS 16?", "EBITDA después de arriendos, sin restar pasivos por arriendo: consistente entre flujo y deuda."],
  ["¿Qué harías con más tiempo?", "Datos reales de la CMF, residual income para el banco, escenarios por país y convención de mitad de año."],
];

const glosario = [
  ["DCF", "Discounted cash flow: valor = flujos futuros traídos a hoy con una tasa que refleja su riesgo."],
  ["FCFF", "Flujo de caja libre para la firma (accionistas + acreedores)."],
  ["NOPAT", "Utilidad operacional después de impuestos, como si la empresa no tuviera deuda."],
  ["WACC", "Costo promedio ponderado de capital."],
  ["Ke / Kd", "Costo del patrimonio / costo de la deuda."],
  ["CAPM", "Modelo que relaciona el retorno exigido con el riesgo de mercado (beta)."],
  ["Beta (β)", "Sensibilidad de la acción a los movimientos del mercado."],
  ["ERP", "Equity risk premium: premio por riesgo de mercado."],
  ["Valor terminal", "Valor de todos los flujos después del horizonte explícito."],
  ["EV", "Enterprise value: valor de la empresa para todos los financistas."],
  ["P/VL", "Precio sobre valor libro del patrimonio."],
  ["ROE", "Utilidad / patrimonio."],
  ["IFRS 16", "Norma contable que lleva los arriendos al balance como deuda."],
  ["Minoritarios", "Participaciones no controladoras: parte de filiales que pertenece a otros."],
  ["SOTP", "Sum-of-the-parts: suma de partes."],
];

// ------------------------------------------------------------ documento
const hijos = [
  new Paragraph({ heading: HeadingLevel.TITLE, children: [t("Guía y registro: DCF de Falabella")] }),
  P(t("Ejercicio de aprendizaje con datos SIMULADOS · Philip Lorber · " + FECHA, { color: "595959" })),
  aviso("Todos los números de este documento y del Excel son SIMULADOS. No describen a Falabella S.A. real y no constituyen recomendación de inversión."),

  H1("1. Cómo usar este documento"),
  P("Este documento acompaña al Excel outputs/DCF_Falabella_simulado.xlsx. Tiene dos usos:"),
  B(t("Guía: ", { bold: true }), "los 12 pasos para armar un DCF, con el concepto, dónde está en el Excel, en qué fijarse y un ejercicio de repetición."),
  B(t("Registro: ", { bold: true }), "las decisiones tomadas y los supuestos, con espacio para que escribas tu propuesta antes de mirar la del modelo."),
  P("Recomendación: haz los ejercicios ANTES de mirar la respuesta. Escribir tu propio supuesto y luego corregirlo es lo que fija el aprendizaje."),

  H1("2. El DCF en una página"),
  P("Una empresa vale lo que va a generar en caja en el futuro, traído a hoy. La tasa con que se trae a hoy (tasa de descuento) refleja el riesgo: más riesgo, más tasa, menos valor."),
  P(t("Valor empresa = Σ FCFF(t) / (1 + WACC)^t + Valor terminal / (1 + WACC)^n", { bold: true, font: "Consolas" })),
  P("Luego se pasa del valor empresa al valor por acción restando lo que se le debe a otros (deuda, minoritarios) y dividiendo por el número de acciones."),
  P("Las tres preguntas que resume cualquier DCF: ¿cuánta caja genera? (proyección), ¿cuánto riesgo tiene? (tasa) y ¿cuánto dura? (valor terminal)."),

  H1("3. Por qué suma de partes en Falabella"),
  P("Falabella consolida retail, negocio inmobiliario y un negocio financiero (Banco Falabella y CMR). Para un banco, los depósitos y la deuda son su materia prima, no su forma de financiarse. Si se mete en el FCFF y se resta su deuda, se castiga el valor dos veces y el WACC deja de tener sentido."),
  P("Solución usada: el negocio no bancario se valoriza por FCFF descontado al WACC; el negocio financiero por su patrimonio, con un P/VL justificado descontado al Ke. Al final se suman."),

  H1("4. El proceso en 12 pasos"),
];
pasos.forEach((p) => {
  hijos.push(H2(p.t));
  hijos.push(etiqueta("Objetivo:", p.obj));
  hijos.push(P(t("Qué hacer:", { bold: true })));
  p.hacer.forEach((h) => hijos.push(B(h)));
  hijos.push(etiqueta("Concepto:", p.concepto));
  hijos.push(etiqueta("En el Excel:", p.excel));
  hijos.push(etiqueta("Fíjate en:", p.ojo));
  hijos.push(etiqueta("Ejercicio:", p.ej));
});

hijos.push(
  H1("5. Buenas prácticas de finanzas"),
  tabla(["Práctica", "En concreto"], buenasPracticas, [2800, 6226]),
  espacio(),
  H1("6. Errores frecuentes"),
  tabla(["Error", "Síntoma", "Solución"], errores, [3000, 2600, 3426]),
  espacio(),
  H1("7. Registro de decisiones"),
  P("Cada decisión de método queda escrita con su alternativa y su razón. En una entrevista, este registro es tu guion."),
  tabla(["Fecha", "Decisión", "Alternativa descartada", "Por qué"], decisiones, [1200, 2300, 2400, 3126]),
  espacio(),
  H1("8. Registro de supuestos"),
  P("Completa las dos columnas de la derecha ANTES de leer el valor base. Luego compara y anota qué aprendiste."),
  tabla(["Supuesto", "Base del modelo", "Justificación", "Tu propuesta", "Tu justificación"],
    supuestosTabla.map((f) => [...f, "", ""]), [2200, 1400, 2426, 1300, 1700]),
  espacio(),
  H1("9. Resultados del caso base (simulado)"),
  tabla(["Concepto", "Valor"], [
    ["Beta apalancada", R.beta_apalancada.toFixed(2).replace(".", ",")],
    ["Ke (costo del patrimonio)", pct(R.ke, 2)],
    ["WACC", pct(R.wacc, 2)],
    ["VP de FCFF 2026-2030 (MM CLP)", mm(R.vp_flujos)],
    ["VP del valor terminal (MM CLP)", mm(R.vp_terminal)],
    ["Valor empresa no bancario (MM CLP)", mm(R.ev)],
    ["% del EV en valor terminal", pct(R.vp_terminal / R.ev)],
    ["P/VL justificado del banco", R.pvl_banco.toFixed(2).replace(".", ",") + "x"],
    ["Valor negocio financiero (MM CLP)", mm(R.valor_banco)],
    ["Valor del patrimonio (MM CLP)", mm(R.patrimonio)],
    ["Valor por acción (CLP)", mm(R.valor_por_accion)],
    ["Precio de mercado simulado (CLP)", mm(R.precio_mercado)],
    ["Potencial", pct(R.potencial)],
  ], [5000, 4026]),
  espacio(),
  P(`Lectura: con estos supuestos simulados el valor por acción (${mm(R.valor_por_accion)} CLP) queda bajo el precio simulado (${mm(R.precio_mercado)} CLP). La hoja Sensibilidad muestra que un WACC ~0,5 pp menor y g ~0,5 pp mayor bastan para justificar el precio: la conclusión depende mucho de la tasa.`),

  H1("10. Plan de práctica por repetición"),
  P("La memoria se fija por repetición espaciada (repasar justo antes de olvidar). Este plan alterna rehacer, modificar y explicar."),
  tabla(["Cuándo", "Qué hacer", "Tiempo", "Criterio de éxito"], practica, [1000, 4200, 900, 2926]),
  espacio(),
  H1("11. Preguntas típicas de entrevista"),
  tabla(["Pregunta", "Respuesta corta"], entrevista, [3400, 5626]),
  espacio(),
  H1("12. Glosario"),
  tabla(["Término", "Significado"], glosario, [2000, 7026]),
  espacio(),
  H1("13. Pendientes"),
  B("Verificar el titular de prensa del 'un billón': ¿utilidad, ingresos o EBITDA? En español, billón = 10¹² (un millón de millones); en inglés, billion = 10⁹. Falta el link de la nota."),
  B("Reemplazar datos simulados por EEFF reales de la CMF usando data/mapa_fuentes.csv."),
  B("Mover el proyecto a su propio repositorio (por ejemplo, falabella-dcf) y enlazarlo desde el README del perfil."),
  B("Mejoras de método: convención de mitad de año, residual income para el banco, minoritarios a valor de mercado, escenarios."),
);

const doc = new Document({
  creator: "Philip Lorber",
  title: "Guía y registro: DCF de Falabella (datos simulados)",
  styles: {
    default: { document: { run: { font: "Arial", size: 21 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: "Arial", size: 40, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 0, after: 120 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 30, bold: true, color: "1F3864" }, paragraph: { spacing: { before: 360, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 25, bold: true, color: "2E5597" }, paragraph: { spacing: { before: 240, after: 100 }, keepNext: true, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: "Arial", size: 22, bold: true }, paragraph: { spacing: { before: 160, after: 80 }, keepNext: true, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "vinetas", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [t("Datos simulados · página ", { size: 16, color: "808080" }), new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "808080" })] })] }) },
    children: hijos,
  }],
});

const salida = path.join(RAIZ, "docs", "Guia_y_Registro_DCF.docx");
Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(salida, buf); console.log("Word escrito en docs/Guia_y_Registro_DCF.docx"); });
