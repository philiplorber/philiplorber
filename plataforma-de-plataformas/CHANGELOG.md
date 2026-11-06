# Andamio · Registro de cambios

Andamio es la plataforma que arma y gestiona la presencia digital de una organización. A partir de una conversación crea su plataforma (el sitio para clientes) y un panel del negocio que junta todos sus canales: WhatsApp, Instagram, Facebook, correo, llamadas, reseñas de Google, TikTok, chat web y delivery.

- **Prototipo publicado:** https://claude.ai/artifact/DgaHj6yxcL9Whbe2F8Gtug (es privado: se comparte desde el menú Compartir)
- **Código:** `plataforma-de-plataformas/index.html`
- **Control de versiones:** cada versión corresponde a un commit en la rama `claude/dreamy-heisenberg-ki0d5j` y está anotada abajo con su código. Se usa versionado semántico: el número del medio sube con cada funcionalidad nueva y el último con cada corrección. Las etiquetas de git (`v0.1.0`…) se pueden crear desde GitHub en "Releases", con esos commits.
- **Análisis comparativo:** `ANALISIS-AMBORAS.md` · **Mercado regional:** `INVESTIGACION-LATAM.md`
- **Cómo se trabaja (roles, decisiones, metacognición):** `BITACORA.md` · **Seguridad:** `SEGURIDAD.md`

---

## v0.5.0 · 6 de noviembre de 2026, 12:50 (hora de Chile)
**Entrada en un solo paso, seguridad y pruebas automáticas**

- **Nueva pantalla de entrada:** una pregunta ("¿Qué organización quieres llevar a lo digital?"), una caja de texto y un botón ("Crear mi plataforma"). Los ejemplos solo rellenan la caja. Debajo se ven los 3 pasos (Describe, Revisa, Conecta) y una nota de confianza sobre dónde quedan tus datos. El resto de la herramienta aparece recién después del primer envío.
- Si el texto es muy corto, aparece un aviso que dice qué falta.
- Cada pregunta del flujo muestra en qué paso y pregunta vas.
- **Seguridad:** se limpia y limita todo texto escrito; el texto de la persona va separado de las instrucciones para la IA; nuevo `SEGURIDAD.md` con lo aplicado y lo que falta para el producto real.
- **DevOps:** prueba de humo automática (`tests/smoke.cjs`, 9 revisiones, incluido un intento de inyectar código) y flujo de GitHub Actions que la corre en cada cambio.
- **Documentos nuevos:** `INVESTIGACION-LATAM.md` (competidores en Chile y Latinoamérica), `BITACORA.md` (registro de trabajo y metacognición) y la skill `.claude/skills/andamio-equipo` (roles para futuras sesiones).

## v0.4.0 · 6 de noviembre de 2026 · commit `e5d3437`
**Herramientas para vender más (inspiradas en la revisión de Amboras)**

- Nuevo grupo **Crecer** en el menú del panel:
  - **Pruebas A/B:** la IA prueba dos versiones de un botón, una foto, un precio o el asunto de un mensaje, y aplica la ganadora cuando tiene al menos 95% de certeza. Cada prueba se puede pausar.
  - **Ventas cruzadas:** ofertas según lo que hace el cliente (al reservar cancha se ofrece un tubo de pelotas; al pedir ceviche, un pisco sour), con lo que aceptan y las ventas extra del mes en pesos.
  - **Mensajes automáticos:** confirmación, recordatorio, cuota por vencer, pedir reseña, pago fallido, cumpleaños… Salen primero por WhatsApp y el correo queda de respaldo.
- El **Resumen** suma el embudo del mes: visitas, interesados, inicios y confirmaciones.
- Se agregó el documento `ANALISIS-AMBORAS.md`, con el inventario de Amboras, cómo lo aplica Andamio, precios, diferencias para Latinoamérica y cómo abordarlos.

## v0.3.0 · 6 de noviembre de 2026 · commit `5a06cc0`
**Control de versiones y foco en la presencia digital**

- Cada pedido que haces en la conversación guarda una **versión nueva de la plataforma**, con fecha y hora, lo que dijiste y lo que se construyó.
- La pestaña **Plano** muestra el **Historial de versiones**. Con **Restaurar** vuelves a cualquier versión anterior, y la restauración queda registrada como una versión más (no se pierde nada).
- El botón **Copiar registro** copia el historial como texto, listo para pegar en un documento o correo.
- Se cambió el enfoque del producto: "toda la presencia digital de tu organización, en un solo lugar".
- Se muestra la versión de Andamio al pie del Plano.

## v0.2.0 · 6 de noviembre de 2026 · commit `5372bc7`
**Panel del negocio: integración de todos los canales**

- La plataforma generada tiene dos caras: el **Sitio para clientes** y el **Panel del negocio**, con menú a la izquierda.
- El panel tiene:
  - un **Resumen** con mensajes de hoy, cuántos faltan por responder, el tiempo de respuesta y la nota en Google, más mensajes por canal;
  - una **Bandeja unificada** con todos los canales en una lista, que se filtra por canal. Al responder, el mensaje sale por el canal original;
  - una **pestaña por cada canal** conectado, con sus propias cifras;
  - **Lo que preguntan**, con las preguntas repetidas agrupadas por tema. Cada respuesta automática se puede encender o apagar;
  - **Conexiones**, para conectar o desconectar cada canal (simulado en el prototipo).
- Se agregaron dos preguntas a la conversación: "¿Por dónde te contacta la gente?" y "¿Qué hago con las preguntas repetidas?" (responder con IA, sugerir y aprobar, o solo agrupar).
- Con la IA activa, el botón **Redactar con IA** escribe la respuesta a cada mensaje.
- En "Podrías estar olvidando" se sumaron temas de integración: reglas de WhatsApp Business, cuentas profesionales de Meta, aviso de grabación de llamadas y la Ley 21.719 de datos personales.

## v0.1.0 · 6 de noviembre de 2026 · commit `01bdf0b`
**Primer prototipo: constructor conversacional**

- La conversación hace una pregunta a la vez, con opciones que aceptas o rechazas: objetivo, perfiles de usuario, secciones, números del negocio (canchas, mesas, horarios), colores, ubicación del menú, portada y nombre.
- La **vista previa en vivo** se puede navegar y verse en modo escritorio o móvil. Incluye reservas por bloque, escalerilla, torneos, clases, cuotas, noticias, tienda y perfil.
- Hay dos motores: **IA (Claude)**, cuando la página tiene permiso, y **modo guiado**, que no necesita IA.
- El modo guiado tiene rubros preparados para club deportivo, restaurante, colegio y negocio general.
- Al terminar aparece la lista **"Podrías estar olvidando"** con los puntos ciegos de cada rubro.
- Se pueden pedir cambios directos en cualquier momento ("menú lateral", "agrega galería", "colores verde y blanco"), y hay botón **Deshacer**.

---

## Pendiente (próximas versiones)
- Conectar canales de verdad con las APIs oficiales (Meta para WhatsApp, Instagram y Facebook; Google; Gmail u Outlook; telefonía).
- Backend con usuarios, roles y base de datos para guardar las plataformas creadas.
- Pagos locales (Webpay, Mercado Pago) y boletas del SII.
- Publicar la plataforma generada en su propio dominio.
