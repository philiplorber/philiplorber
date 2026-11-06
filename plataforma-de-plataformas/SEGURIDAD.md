# Seguridad y buenas prácticas en Andamio (explicado en simple)

## Lo que ya está aplicado en el prototipo

| Práctica | Qué es, en simple | Dónde está |
|---|---|---|
| **Escapar todo lo que se muestra** | Si alguien escribe código (por ejemplo `<img onerror=…>`), se muestra como texto y no se ejecuta. Es la defensa contra el ataque más común en páginas web (XSS) | Función `esc()` en `index.html`, y la prueba automática lo verifica |
| **Limpiar y limitar lo que se escribe** | Se quitan caracteres invisibles o de control y se limita el largo (300 en la entrada, 500 en el chat), para que nadie meta texto gigante o caracteres trampa | Función `cleanText()` y `maxlength` |
| **Validar lo que devuelve la IA** | La IA puede equivocarse. Antes de usar su respuesta se revisa todo: los colores deben ser códigos válidos, las secciones de tipos conocidos y los textos de largo máximo | Función `sanitize()` |
| **Separar instrucciones de datos al hablar con la IA** | El texto de la persona va entre marcas `<<< >>>`, y se le dice a la IA que es información, no órdenes. Así es más difícil "convencer" a la IA de saltarse sus reglas (inyección de instrucciones) | `aiPrompt()` y `draftAI()` |
| **Sin claves ni secretos en la página** | La página no tiene contraseñas ni claves de API. La IA se usa con la cuenta de Claude de quien mira, con su permiso | Diseño del prototipo |
| **Guardar solo lo necesario, y en el navegador** | Lo que escribes queda en tu navegador, no en un servidor. Si el navegador bloquea el guardado, la página igual funciona | `save()` con `try/catch` |
| **Pruebas automáticas (CI)** | Cada cambio que se sube a GitHub abre la página en un navegador y prueba el flujo, incluido el intento de inyectar código | `tests/smoke.cjs` y `.github/workflows/andamio-ci.yml` |
| **Permisos mínimos en la automatización** | La revisión automática de GitHub solo puede leer el código, no modificarlo | `permissions: contents: read` |

## Lo que hay que hacer cuando exista el producto real (con servidor)

1. **Inicio de sesión sin contraseñas propias:** entrar con Google, con un enlace al correo o con llaves de acceso (passkeys). Guardar contraseñas propias es un riesgo innecesario.
2. **Cada organización ve solo lo suyo:** cada dato lleva el identificador de su organización, y la base de datos impide leer los de otra (seguridad por fila). Es lo más importante en una plataforma con muchos clientes.
3. **Roles:** dueño, administrador, quien atiende y quien solo ve. Quien responde WhatsApp no necesita ver los pagos.
4. **Secretos en una bóveda:** las claves de Meta, Google y los pagos van en un gestor de secretos, nunca en el código ni en GitHub. Se renuevan periódicamente.
5. **Verificar a quien nos escribe:** los avisos que mandan Meta o Webpay vienen firmados, y hay que comprobar la firma antes de creerles.
6. **Datos personales (Ley 21.719, rige desde diciembre de 2026):** pedir consentimiento, guardar solo lo necesario, cifrar los datos sensibles, permitir que una persona pida borrar sus datos y tener un registro de quién vio qué.
7. **Límites de uso:** frenar a quien hace demasiadas peticiones (robots, ataques) y poner tope de gasto en la IA.
8. **Respaldos y monitoreo:** copias diarias de la base de datos, alertas si algo falla y un plan escrito para incidentes.
9. **Revisión de dependencias:** que GitHub avise si una librería usada tiene una falla conocida (Dependabot).
