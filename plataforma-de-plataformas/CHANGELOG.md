# Andamio · Registro de cambios

Andamio es la plataforma que arma y gestiona la presencia digital de una organización. A partir de una conversación crea su plataforma (el sitio para clientes) y un panel del negocio que junta todos sus canales: WhatsApp, Instagram, Facebook, correo, llamadas, reseñas de Google, TikTok, chat web y delivery.

- **Prototipo publicado:** https://claude.ai/artifact/DgaHj6yxcL9Whbe2F8Gtug (es privado: se comparte desde el menú Compartir)
- **Código:** `plataforma-de-plataformas/index.html`
- **Control de versiones:** cada versión tiene su etiqueta en git (`v0.1.0`, `v0.2.0`, `v0.3.0`). Se usa versionado semántico: el número del medio sube con cada funcionalidad nueva y el último con cada corrección.

---

## v0.3.0 · 6 de noviembre de 2026
**Control de versiones y foco en la presencia digital**

- Cada pedido que haces en la conversación guarda una **versión nueva de la plataforma**, con fecha y hora, lo que dijiste y lo que se construyó.
- La pestaña **Plano** muestra el **Historial de versiones**. Con **Restaurar** vuelves a cualquier versión anterior, y la restauración queda registrada como una versión más (no se pierde nada).
- El botón **Copiar registro** copia el historial como texto, listo para pegar en un documento o correo.
- Se cambió el enfoque del producto: "toda la presencia digital de tu organización, en un solo lugar".
- Se muestra la versión de Andamio al pie del Plano.

## v0.2.0 · 6 de noviembre de 2026
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

## v0.1.0 · 6 de noviembre de 2026
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
