# DCF de Falabella: ejercicio de aprendizaje (datos SIMULADOS)

> ⚠️ Todos los números son **simulados**. No describen a Falabella S.A. real y no son recomendación de inversión.

Valoración por **suma de partes**:

- **Negocio no bancario** (retail e inmobiliario): flujo de caja libre para la firma (FCFF) descontado al WACC, más un valor terminal de Gordon.
- **Negocio financiero** (Banco Falabella y CMR): valorizado por su patrimonio, con un P/VL justificado = (ROE − g) / (Ke − g).

## Estructura

```
config/supuestos.yaml          ← TODOS los supuestos, con su justificación
data/simulado/                 ← EEFF históricos 2021-2025 simulados
data/mapa_fuentes.csv          ← dónde buscar cada dato real (CMF, BCCh, Damodaran…)
src/simular_datos.py           ← genera los datos simulados (semilla fija)
src/modelo_dcf.py              ← el DCF en Python (sirve para reconciliar el Excel)
src/construir_excel.py         ← arma el Excel con fórmulas vivas
src/construir_word.js          ← arma la guía y el registro en Word
outputs/DCF_Falabella_simulado.xlsx
docs/Guia_y_Registro_DCF.docx  ← los 12 pasos, buenas prácticas, registro de decisiones y plan de práctica
```

## Cómo correrlo

```bash
pip install -r requirements.txt
python src/simular_datos.py        # 1. datos
python src/modelo_dcf.py           # 2. resultado en consola
python src/construir_excel.py      # 3. Excel
node src/construir_word.js         # 4. Word (requiere: npm install docx)
```

Para hacer un análisis de sensibilidad propio, cambia `config/supuestos.yaml` y vuelve a correr los pasos 3 y 4.

## Resultado del caso base (simulado)

| | |
|---|---|
| WACC | 9,71% |
| Valor empresa no bancario | 7,94 billones de CLP (MM CLP 7.943.480) |
| Valor del negocio financiero | MM CLP 2.239.477 (P/VL 1,41x) |
| Valor por acción | 2.433 CLP frente a un precio simulado de 2.800 CLP (−13%) |
| Valor terminal / EV | 75% |

La hoja **Sensibilidad** del Excel muestra el valor por acción para WACC entre ±1 pp y g entre ±1 pp. La hoja **Checks** contiene los controles de razonabilidad y la reconciliación Excel vs. Python.
