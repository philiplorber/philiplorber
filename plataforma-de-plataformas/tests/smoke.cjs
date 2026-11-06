// Prueba de humo de Andamio: abre la página como lo haría una persona y revisa
// que el flujo principal funcione y que el texto escrito no pueda ejecutar código.
// Uso: node plataforma-de-plataformas/tests/smoke.cjs
const path = require("path");
const { chromium } = require("playwright");

const PAGE = "file://" + path.resolve(__dirname, "..", "index.html");
const fails = [];
const check = (ok, msg) => { if (!ok) fails.push(msg); console.log((ok ? "ok   " : "FALLA") + "  " + msg); };

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));

  await page.goto(PAGE);

  // 1. La entrada muestra una sola acción principal.
  check(await page.isVisible("#startForm"), "La pantalla de entrada se ve al abrir");
  check((await page.$$("#start .cta")).length === 1, "La entrada tiene un solo botón principal");

  // 2. Validación: un texto demasiado corto no avanza y explica qué falta.
  await page.fill("#startInput", "hola");
  await page.click("#start .cta");
  check(await page.isVisible("#startErr"), "Un texto muy corto muestra un aviso claro");

  // 3. Seguridad: un texto con HTML malicioso se muestra como texto y no se ejecuta.
  await page.fill("#startInput", 'Mi club <img src=x onerror="window.__xss=1"> de tenis');
  await page.click("#start .cta");
  await page.waitForSelector("#log .msg.me");
  check(await page.evaluate(() => window.__xss === undefined), "El HTML escrito por la persona no se ejecuta");
  check((await page.$$("#log img")).length === 0, "No aparecen etiquetas inyectadas en la conversación");

  // 4. El flujo guiado avanza hasta el final.
  for (let i = 0; i < 16; i++) {
    if (await page.$("#qGo")) await page.click("#qGo");
    else if (await page.$(".q .opt")) await page.click(".q .opt >> nth=0");
    else break;
  }
  check(await page.isVisible(".blind"), "El flujo termina con la lista de lo que podrías estar olvidando");

  // 5. El panel del negocio y sus secciones abren sin errores.
  await page.click("#facePan");
  for (const id of ["a_resumen", "a_bandeja", "a_faq", "g_ab", "g_cross", "g_auto", "a_conexiones"]) {
    await page.click(`[data-apage="${id}"]`);
  }
  check(await page.isVisible(".pv-grid"), "Las páginas del panel se dibujan");

  // 6. El historial de versiones registra cada paso.
  await page.click("#tabPlan");
  check((await page.$$("[data-restore]")).length >= 3, "El historial guarda varias versiones");

  check(errors.length === 0, "Sin errores de JavaScript" + (errors.length ? ": " + errors.join(" | ") : ""));
  await browser.close();
  if (fails.length) { console.error(`\n${fails.length} prueba(s) fallaron.`); process.exit(1); }
  console.log("\nTodas las pruebas pasaron.");
})().catch(e => { console.error(e); process.exit(1); });
