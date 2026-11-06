# Bitácora de trabajo · Andamio

*El CHANGELOG cuenta **qué cambió en el producto**. Esta bitácora cuenta **cómo se trabajó**: qué roles se asumieron, qué se decidió y por qué, qué supuestos hay y qué falta verificar (metacognición). Cada sesión agrega una entrada arriba.*

---

## Sesión 2026-11-06 · 12:30 a 12:50 (hora de Chile) · versión v0.5.0

### Encargo
Cerrar las brechas de la revisión: aplicar prácticas de ingeniería, DevOps y seguridad explicadas en simple; rediseñar la entrada (una sola acción y el resto progresivo); estudiar el flujo de entrada de Amboras; investigar equivalentes en Chile y Latinoamérica; dejar registro y metacognición.

### Roles activados y para qué
| Rol | Para qué se usó en esta sesión |
|---|---|
| Producto / UX | Rediseño de la entrada: una pregunta, un botón, ejemplos opcionales y 3 pasos visibles |
| Desarrollo frontend | Pantalla de entrada, validación con mensaje claro, indicador de pregunta, accesibilidad (etiquetas y avisos leídos por lector de pantalla) |
| Ciberseguridad | Limpieza y límites del texto, separación de instrucciones y datos para la IA, prueba de inyección de código, `SEGURIDAD.md` |
| DevOps | Prueba de humo automática y flujo de GitHub Actions con permisos de solo lectura |
| Investigación de mercado | Flujo de Amboras y competidores regionales (`INVESTIGACION-LATAM.md`) |
| Marketing | Copy de la entrada en español de Chile y mensajes de confianza (gratis, sin cuenta, dónde quedan los datos) |

### Skills y herramientas usadas
- Guía de diseño de artefactos y capacidades de página (IA con permiso del visitante).
- Guía de visualización de datos (barras del Resumen y del embudo).
- Búsqueda web y lectura de páginas (amboras.com, prensa y sitios de competidores).
- Navegador automatizado (Playwright) para probar y revisar la página.
- Nueva skill del proyecto: `.claude/skills/andamio-equipo/SKILL.md`, que carga estos roles en futuras sesiones.

### Decisiones y por qué (en simple)
1. **Primero describir y después crear cuenta** (Amboras hace al revés). Así la persona ve valor antes de entregar datos, y en el prototipo no hay datos que proteger en un servidor.
2. **Una sola caja de texto y un solo botón.** Los ejemplos rellenan la caja pero no envían, para que la acción siga siendo una sola y la persona pueda editarlos.
3. **Pedir mínimo 8 caracteres, con un aviso que dice qué falta** en vez de un error genérico.
4. **Todo texto se limpia y se limita** antes de usarlo, y **todo lo que devuelve la IA se valida**. Nunca se confía en entradas externas.
5. **Prueba automática que intenta inyectar código.** Si un cambio futuro rompe esa protección, GitHub lo avisa.

### Metacognición
- **Lo que sé con certeza:** las 9 pruebas automáticas pasan en este entorno; la entrada y el flujo guiado funcionan sin errores.
- **Lo que no pude verificar:** el modo IA dentro del visor de Claude; el formulario de registro de Amboras, que se dibuja en el navegador y no se pudo leer; los precios de Vambe, AgendaPro, EasyCancha y Justo, que no son públicos.
- **Supuestos:** que conviene partir por servicios (clubes y restaurantes); que los precios en CLP propuestos son razonables. Ambos se validan con entrevistas.
- **Riesgo de sesgo:** casi todas las cifras de competidores vienen de su propia prensa o marketing.
- **Qué haría distinto:** hacer antes las entrevistas con clientes, y después más pantallas.

### Registro de tareas
- [x] Plan corto en pasos.
- [x] Nueva pantalla de entrada (v0.5.0), publicada en el mismo link.
- [x] Limpieza de texto, límites y separación de instrucciones para la IA.
- [x] Prueba de humo `tests/smoke.cjs` (9 de 9 en verde) y flujo de CI.
- [x] Estudio del flujo de entrada de Amboras.
- [x] `INVESTIGACION-LATAM.md`, `SEGURIDAD.md` y esta bitácora.
- [x] Skill del proyecto con los roles.
- [ ] Ver el CI corriendo en GitHub (queda para cuando se abra un PR o se revise la pestaña Actions).

---

## Sesión 2026-11-06 · mañana · versiones v0.1.0 a v0.4.0 (reconstruida)
- **Roles:** producto, diseño, frontend, investigación.
- **Trabajo:** constructor conversacional (v0.1), panel con canales integrados (v0.2), historial de versiones (v0.3) y herramientas para crecer inspiradas en Amboras (v0.4).
- **Aprendizaje:** la diferencia frente a Amboras es servicios + WhatsApp + pagos locales.
- **Pendiente heredado:** etiquetas de versión en GitHub, porque esta sesión no puede subir tags.
