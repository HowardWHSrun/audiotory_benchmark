#!/usr/bin/env node
"use strict";

/*
 * Optional browser checks: node bench_app/test_ui.cjs
 * Requires Playwright and its Chromium browser, or set:
 *   PLAYWRIGHT_MODULE_PATH  path to an installed Playwright package
 *   PLAYWRIGHT_BROWSER_EXECUTABLE  path to a compatible Chrome/Chromium binary
 * All API responses are test fixtures. No audio backend or hardware is opened.
 * Screenshots go to the ignored .work/bench_app directory.
 */
const http = require("node:http");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const assert = require("node:assert/strict");

const UI_ROOT = path.join(__dirname, "ui");
const OUTPUT = path.resolve(__dirname, "../.work/bench_app");
const TOKEN = "mock-ui-test-token";
const MOCK_PATH = path.join(os.tmpdir(), "MOCK-UI-TEST");
const idle = () => ({ state: "idle", action: null, progress: 0, message: "Ready", result: null, run_path: null });
let status = idle();
const starts = [];
let stops = 0;
let quits = 0;
let browser;

const server = http.createServer((request, response) => {
  response.setHeader("Cache-Control", "no-store");
  if (request.url.startsWith("/api/")) {
    response.setHeader("Content-Type", "application/json");
    if (request.url === "/api/session") return response.end(JSON.stringify({ token: TOKEN }));
    if (request.url === "/api/devices") return response.end(JSON.stringify({
      devices: [{ index: 7, name: "MOCK TEST Interface", host_api: "Test backend", max_input_channels: 2, max_output_channels: 2, default_sample_rate: 48000, is_default_output: true }],
      default_output: 7, backend_available: true, errors: [],
    }));
    if (request.url === "/api/status") return response.end(JSON.stringify(status));
    if (request.method !== "POST" || request.headers["x-sonic-token"] !== TOKEN) {
      response.statusCode = 403;
      return response.end(JSON.stringify({ error: "Mock API requires the session token." }));
    }
    let body = "";
    request.on("data", (chunk) => { body += chunk; });
    request.on("end", () => {
      if (request.url === "/api/start") {
        const config = JSON.parse(body);
        starts.push(config);
        status = { state: "running", action: config.action, progress: 0.1, message: "MOCK UI TEST: no audio opened", config, result: null, run_path: MOCK_PATH };
      } else if (request.url === "/api/stop") {
        stops += 1;
        status = { ...status, state: "cancelled", progress: 0, message: "Mock cancelled" };
      } else if (request.url === "/api/quit") {
        quits += 1;
        status = { ...status, state: "closed" };
      } else {
        response.statusCode = 404;
        return response.end(JSON.stringify({ error: "Unknown mock endpoint." }));
      }
      response.end(JSON.stringify(status));
    });
    return;
  }
  const file = path.join(UI_ROOT, request.url === "/" ? "index.html" : request.url.slice(1));
  response.setHeader("Content-Type", file.endsWith(".css") ? "text/css" : file.endsWith(".js") ? "application/javascript" : "text/html");
  try { response.end(fs.readFileSync(file)); }
  catch (_) { response.statusCode = 404; response.end(); }
});

async function main() {
  const { chromium } = require(process.env.PLAYWRIGHT_MODULE_PATH || "playwright");
  fs.mkdirSync(OUTPUT, { recursive: true });
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  const options = { headless: true };
  if (process.env.PLAYWRIGHT_BROWSER_EXECUTABLE) options.executablePath = process.env.PLAYWRIGHT_BROWSER_EXECUTABLE;
  browser = await chromium.launch(options);
  const page = await browser.newPage({ viewport: { width: 1440, height: 1040 }, deviceScaleFactor: 1 });
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));
  const url = `http://127.0.0.1:${server.address().port}`;
  await page.goto(url);
  await page.getByText("Local engine ready").waitFor();
  assert.equal(starts.length, 0, "Page load must never start audio.");
  assert.equal(await page.locator("#device").inputValue(), "7");
  assert.equal(await page.locator("#seed").inputValue(), "20261023");
  await page.screenshot({ path: path.join(OUTPUT, "ui-desktop.png"), fullPage: true });

  await page.locator('[data-go="delay"]').first().click();
  await page.locator("#startCalibration").click();
  await page.locator("#runDock").waitFor({ state: "visible" });
  assert.equal(starts.length, 1);
  assert.equal(starts[0].peak_dbfs, -36);
  assert.equal(starts[0].reference_channel, null);
  assert.equal(await page.locator("#device").isDisabled(), true);
  assert.equal(await page.locator("#startStimulus").isDisabled(), true);
  await page.keyboard.press("Escape");
  await page.locator("#runDock").waitFor({ state: "hidden" });
  assert.equal(stops, 1);

  await page.locator('input[value="electrical"]').check();
  await page.locator("#startCalibration").click();
  await page.locator("#runDock").waitFor({ state: "visible" });
  assert.equal(starts[1].reference_output_channel, 2);
  assert.equal(starts[1].reference_channel, 2);
  status = { ...status, state: "completed", progress: 1, result: {
    usable_measurement: true, mode: "electrical_reference", measured_delay_ms: 12.34,
    summary: { accepted_trials: 10, total_trials: 10, p05_delay_ms: 12.3, p95_delay_ms: 12.4 },
    interpretation: "MOCK UI TEST fixture only",
  } };
  await page.locator("#delayResultTag").filter({ hasText: "MEASURED" }).waitFor();
  assert.equal(await page.locator(".result-number").textContent(), "12.34ms");
  await page.locator("#repetitions").fill("11");
  await page.locator("#repetitions").dispatchEvent("change");
  assert.equal(await page.locator("#delayResult").isHidden(), true, "Configuration changes must clear stale measured results.");
  await page.locator("#referenceOutputChannel").selectOption("1");
  await page.locator("#startCalibration").click();
  assert.match(await page.locator("#globalError").textContent(), /separate input and output/);
  assert.equal(starts.length, 2);
  await page.locator("#referenceOutputChannel").selectOption("2");

  await page.locator('[data-go="stimulus"]').click();
  await page.locator("#tonesPerFrequency").fill("60");
  assert.equal((await page.locator("#durationDisplay").textContent()).trim(), "8.4 s");
  await page.locator("#startStimulus").click();
  await page.locator("#runDock").waitFor({ state: "visible" });
  status = { ...status, state: "completed", progress: 1, result: {
    kind: "sonic_e14_reconstruction", usable_measurement: false, measured_delay_ms: null, tone_count: 840, duration_seconds: 8.4,
  } };
  await page.locator("#stimulusResult").waitFor({ state: "visible" });
  assert.equal(await page.locator("#delayResult").isHidden(), true, "Playback results must not display as calibration.");
  const downloadPromise = page.waitForEvent("download");
  await page.locator("#downloadResult").click();
  assert.equal((await downloadPromise).suggestedFilename(), "sonic-run-result.json");

  status = idle();
  const mobile = await browser.newPage({ viewport: { width: 375, height: 850 }, deviceScaleFactor: 1 });
  mobile.on("pageerror", (error) => errors.push(error.message));
  await mobile.goto(url);
  await mobile.getByText("Local engine ready").waitFor();
  for (const [panel, filename] of [["setup", "ui-mobile.png"], ["delay", "ui-mobile-delay.png"], ["stimulus", "ui-mobile-stimulus.png"]]) {
    await mobile.locator(`[data-panel="${panel}"]`).click();
    await mobile.screenshot({ path: path.join(OUTPUT, filename), fullPage: true });
  }
  await mobile.close();
  for (const width of [320, 375, 768, 1024, 1440]) {
    await page.setViewportSize({ width, height: 850 });
    for (const panel of ["setup", "delay", "stimulus"]) {
      await page.locator(`[data-panel="${panel}"]`).click();
      const sizes = await page.evaluate(() => ({ scroll: document.documentElement.scrollWidth, width: innerWidth }));
      assert(sizes.scroll <= sizes.width, `${panel} overflows at ${width}px: ${JSON.stringify(sizes)}`);
    }
  }
  await page.locator("#quitApp").click();
  await page.locator("#appClosed").waitFor({ state: "visible" });
  assert.equal(quits, 1);
  assert.equal(await page.locator("#startStimulus").isDisabled(), true);
  assert.deepEqual(errors, []);
  console.log("PASS: no automatic audio; token/routing/config; start lock; Stop/Escape; result gates/reset; duplicate-route rejection; stimulus result dispatch; JSON download; Quit; all panels at 320/375/768/1024/1440px. Mock API only; no audio hardware opened.");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
}).finally(async () => {
  if (browser) await browser.close();
  if (server.listening) await new Promise((resolve) => server.close(resolve));
});
