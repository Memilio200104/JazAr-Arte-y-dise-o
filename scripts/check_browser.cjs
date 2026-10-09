const { chromium } = require("playwright");
const fs = require("fs");
const assert = require("node:assert/strict");
let browser;

(async () => {
  fs.mkdirSync("artifacts", { recursive: true });
  browser = await chromium.launch({ channel: "chrome", headless: true });
  const page = await browser.newPage({
    viewport: { width: 1440, height: 1000 },
  });
  const failures = [];
  page.on("pageerror", (e) => failures.push(e.message));
  page.on("response", (r) => {
    if (r.status() >= 400 && !r.url().includes("favicon"))
      failures.push(`${r.status()} ${r.url()}`);
  });
  await page.goto("http://127.0.0.1:8000/", { waitUntil: "networkidle" });
  await page.screenshot({ path: "artifacts/desktop.png" });
  assert.equal(await page.locator(".product").count(), 6);
  assert.ok(
    await page.locator(".intro").evaluate((el) => el.offsetHeight < 550),
    "Intro must not inherit the source logo height",
  );
  assert.equal(await page.locator(".design-backdrop").count(), 7);
  for (const img of await page
    .locator(".hero-image, .product-visual img, .brand-portrait img")
    .all()) {
    await img.scrollIntoViewIfNeeded();
    await img.evaluate((i) => i.decode());
  }
  for (const src of await page
    .locator("img")
    .evaluateAll((images) => [...new Set(images.map((image) => image.src))])) {
    assert.equal((await page.request.get(src)).status(), 200, src);
  }
  await page.locator(".process-scene").scrollIntoViewIfNeeded();
  for (const step of ["4", "2", "5"]) {
    await page.locator(`[data-goto-step="${step}"]`).click();
    await page.waitForFunction(
      (value) =>
        document.querySelector("#process-number").textContent === `0${value}`,
      step,
    );
    await page
      .locator(`[data-frame="${step}"] img`)
      .evaluate((image) => image.decode());
    await page.waitForFunction(
      (value) =>
        [...document.querySelectorAll(".process-layer")].every(
          (layer) =>
            Number(getComputedStyle(layer).opacity) ===
            (layer.dataset.frame === value ? 1 : 0),
        ),
      step,
    );
  }
  await page.screenshot({ path: "artifacts/process.png" });
  await page.locator('[data-filter="dtf"]').click();
  assert.equal(await page.locator(".product:visible").count(), 2);
  assert.match(page.url(), /tecnica=dtf/);
  await page.locator('[data-filter="dtf"]').evaluate((button) => {
    button.dataset.filter = "empty-test";
  });
  await page.locator('[data-filter="empty-test"]').click();
  assert.equal(await page.locator(".catalog-empty").isVisible(), true);
  await page.locator("[data-reset-filter]").click();
  assert.equal(await page.locator(".product:visible").count(), 6);
  await page.locator('[data-filter="empty-test"]').evaluate((button) => {
    button.dataset.filter = "dtf";
  });
  await page.locator('[data-filter="dtf"]').click();
  await page.locator(".product:visible .text-link").first().click();
  assert.equal(await page.locator("#id_interest").inputValue(), "prendas");
  await page.locator('[data-filter="all"]').click();
  await page.locator("#contacto").scrollIntoViewIfNeeded();
  await page.screenshot({ path: "artifacts/contact.png" });
  for (const width of [320, 390, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 900 });
    await page.evaluate(() => window.scrollTo({ top: 0, behavior: "instant" }));
    await page.waitForTimeout(200);
    assert.equal(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      true,
      `horizontal overflow at ${width}`,
    );
    await page.screenshot({ path: `artifacts/viewport-${width}.png` });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await page.locator(".menu-toggle").click();
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "true",
  );
  await page.keyboard.press("Escape");
  assert.equal(
    await page.locator(".menu-toggle").getAttribute("aria-expanded"),
    "false",
  );
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.waitForFunction(() => window.ScrollTrigger.getAll().length === 0);
  assert.equal(await page.locator(".design-backdrop").count(), 7);
  assert.ok(
    await page
      .locator(".design-backdrop")
      .evaluateAll((items) =>
        items.every((item) => getComputedStyle(item).transform === "none"),
      ),
  );
  await page.screenshot({ path: "artifacts/mobile.png", fullPage: true });
  await page.locator("#id_name").fill("Demo JazAr");
  await page.locator("#id_email").fill("demo@example.com");
  await page.locator("#id_interest").selectOption("regalos");
  await page.locator("#id_quantity").fill("2");
  await page
    .locator("#id_message")
    .fill("Solicitud ficticia para verificar la demo local.");
  await Promise.all([
    page.waitForURL(/contact=/),
    page.locator(".submit-button").click(),
  ]);
  assert.match(
    await page.locator(".form-status").innerText(),
    /Prueba recibida/,
  );
  const noJS = await browser.newPage({
    javaScriptEnabled: false,
    viewport: { width: 390, height: 844 },
  });
  await noJS.goto("http://127.0.0.1:8000/");
  assert.equal(await noJS.locator("h1").isVisible(), true);
  assert.equal(await noJS.locator("#contact-form").isVisible(), true);
  assert.equal(await noJS.locator("#site-nav").isVisible(), true);
  assert.equal(await noJS.locator(".process-selector").isVisible(), false);
  await noJS.close();
  assert.deepEqual(failures, []);
  console.log(
    "PASS: resources, filters, selection, 5 responsive widths, menu, reduced motion, local contact and no-JS content.",
  );
  await browser.close();
})().catch(async (e) => {
  console.error(e);
  await browser?.close();
  process.exit(1);
});
