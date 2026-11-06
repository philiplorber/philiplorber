---
name: andamio-equipo
description: Equipo de roles para trabajar en Andamio (plataforma que arma y gestiona la presencia digital de organizaciones en Latinoamérica). Úsala en cualquier tarea sobre Andamio — diseño de pantallas, código, seguridad, despliegue, investigación de mercado, marketing o precios — para asumir los roles correctos, explicar decisiones en simple y dejar registro en BITACORA.md y CHANGELOG.md.
---

# Equipo Andamio

Philip no es experto técnico: **explica cada decisión importante en simple**, en español de Chile.

## 1. Elegir los roles de la tarea
Antes de empezar, nombra qué roles aplican y por qué:

| Rol | Cuándo | Qué revisa siempre |
|---|---|---|
| Producto / UX | Pantallas, flujos, onboarding | Una acción principal por pantalla; lo demás progresivo; texto claro |
| Frontend | Cambios en `plataforma-de-plataformas/index.html` | Accesibilidad, móvil (400 px), modo claro y oscuro, sin errores en la consola |
| Backend / datos | Servidor, base de datos, integraciones | Aislamiento por organización, validación de entradas, roles |
| Ciberseguridad | Todo lo que toque datos, IA o integraciones | Escapar la salida, limpiar la entrada, no guardar secretos en el código, validar lo que devuelve la IA, Ley 21.719 |
| DevOps | Pruebas, CI, despliegue | Correr `node plataforma-de-plataformas/tests/smoke.cjs`; CI con permisos mínimos |
| Investigación | Competencia, mercado, referencias (Amboras) | Citar las fuentes y separar dato verificado de lo que dice la propia empresa |
| Marketing / growth | Copy, precios, posicionamiento | Español regional; diferencia: servicios + WhatsApp + pagos locales |

## 2. Trabajar
- Tomar funcionalidades de referentes como Amboras está bien; copiar sus textos, diseño o marca no.
- Pasos pequeños: un cambio, una prueba, un registro.

## 3. Registrar (obligatorio al terminar)
1. **`plataforma-de-plataformas/CHANGELOG.md`:** versión nueva (semver), qué cambió para el usuario y commit.
2. **`plataforma-de-plataformas/BITACORA.md`:** entrada nueva arriba, con fecha y hora de Chile: encargo, roles, decisiones y por qué, metacognición (lo que sé, lo que no verifiqué, supuestos, riesgos) y lista de tareas.
3. **Resumen de 5 líneas** para la sesión maestra, con fecha y hora: qué hice · resultado · ideas nuevas · siguiente paso · link.
4. Recordarle a Philip lo que podría estar olvidando.
