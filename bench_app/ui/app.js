"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { token: null, devices: [], running: false, starting: false, stopping: false, quitting: false, closed: false, online: false, lastStatus: null, lastRecord: null, lastResultKey: null, runPath: "", polling: false, pollTimer: null };
  const routeInputs = Array.from(document.querySelectorAll("[data-route]"));
  const panelNames = new Set(["setup", "delay", "stimulus"]);
  let toastTimer;

  function showPanel(name, updateHash = true) {
    if (!panelNames.has(name)) name = "setup";
    document.querySelectorAll(".panel").forEach((panel) => { panel.hidden = panel.id !== `panel-${name}`; });
    document.querySelectorAll(".nav-item").forEach((item) => {
      const selected = item.dataset.panel === name;
      item.classList.toggle("selected", selected);
      if (selected) item.setAttribute("aria-current", "step"); else item.removeAttribute("aria-current");
    });
    if (updateHash && location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
    document.title = `${{ setup: "Setup", delay: "Measure delay", stimulus: "Play SONIC" }[name]} · SONIC Sound Bench`;
  }

  function showError(message) {
    $("globalError").textContent = message || "";
    $("globalError").hidden = !message;
  }

  function setConnection(online, text) {
    state.online = online;
    $("connectionState").classList.toggle("connected", online);
    $("connectionState").classList.toggle("offline", !online);
    $("connectionText").textContent = text;
  }

  async function api(path, options = {}) {
    const headers = { ...(options.headers || {}) };
    if (options.method === "POST") {
      if (!state.token) throw new Error("The local session is not connected. Refresh this page and try again.");
      headers["X-SONIC-Token"] = state.token;
      headers["Content-Type"] = "application/json";
    }
    const response = await fetch(path, { ...options, headers, cache: "no-store" });
    let data;
    try { data = await response.json(); } catch (_) { throw new Error("The local audio app returned an unreadable response. Check the launcher window."); }
    if (!response.ok) throw new Error(typeof data.error === "string" ? data.error : data.message || `Request failed (${response.status}).`);
    return data;
  }

  const currentDevice = () => state.devices.find((device) => String(device.index) === $("device").value);
  const isReferenceMode = () => document.querySelector("input[name='referenceMode']:checked").value === "electrical";
  const busy = () => state.running || state.starting || state.stopping || state.quitting || state.closed;

  function populateChannels(select, count, prefix, preferred) {
    select.replaceChildren();
    for (let channel = 1; channel <= count; channel += 1) {
      const option = document.createElement("option");
      option.value = String(channel);
      option.textContent = `${prefix} ${channel}`;
      select.append(option);
    }
    if (!count) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = `No ${prefix.toLowerCase()} channels`;
      select.append(option);
    } else select.value = String(Math.min(preferred || 1, count));
  }

  function onDeviceChange() {
    clearCalibration();
    const device = currentDevice();
    const outputs = Number(device?.max_output_channels || 0);
    const inputs = Number(device?.max_input_channels || 0);
    populateChannels($("outputChannel"), outputs, "Output", 1);
    populateChannels($("inputChannel"), inputs, "Input", 1);
    populateChannels($("referenceOutputChannel"), outputs, "Output", 2);
    populateChannels($("referenceChannel"), inputs, "Input", 2);
    $("deviceHelp").textContent = device ? `${device.host_api || "Audio interface"} · ${inputs} input${inputs === 1 ? "" : "s"} · ${outputs} output${outputs === 1 ? "" : "s"}. A run checks sample-rate support before playback.` : "Connect an interface with microphone input and speaker output, then refresh devices.";
    updateRouting();
    updateAvailability();
  }

  async function loadDevices() {
    $("refreshDevices").disabled = true;
    try {
      const data = await api("/api/devices");
      state.devices = (Array.isArray(data) ? data : data.devices || []).filter((device) => Number(device.max_input_channels) > 0 && Number(device.max_output_channels) > 0);
      const previous = $("device").value;
      $("device").replaceChildren();
      if (!state.devices.length) {
        const option = document.createElement("option");
        option.value = "";
        option.textContent = "No input + output interface found";
        $("device").append(option);
        if (data.backend_available === false || data.errors?.length) showError((data.errors || []).join(" ") || "Audio support is unavailable. Check the local launcher for installation details.");
      } else {
        state.devices.forEach((device) => {
          const option = document.createElement("option");
          option.value = String(device.index);
          option.textContent = `${device.name}${device.host_api ? ` · ${device.host_api}` : ""}`;
          $("device").append(option);
        });
        const selected = state.devices.find((device) => String(device.index) === previous)
          || state.devices.find((device) => device.index === data.default_output)
          || state.devices.find((device) => device.is_default_output)
          || state.devices[0];
        $("device").value = String(selected.index);
      }
      onDeviceChange();
      setConnection(true, state.devices.length ? "Local engine ready" : "Connect an interface");
    } catch (error) {
      showError(error.message);
      setConnection(false, "Engine disconnected");
    } finally { $("refreshDevices").disabled = busy(); }
  }

  function updateRouting() {
    const device = currentDevice();
    const output = $("outputChannel").value || "—";
    const input = $("inputChannel").value || "—";
    const rate = Number($("sampleRate").value) / 1000;
    $("diagramOutput").textContent = `Speaker output ${output}`;
    $("diagramInput").textContent = `Microphone input ${input}`;
    document.querySelectorAll(".route-summary-text").forEach((label) => { label.textContent = device ? `${device.name} · ${rate} kHz · speaker ${output} → mic ${input}` : "Choose your interface in setup"; });
    document.querySelectorAll(".route-summary").forEach((item) => item.classList.toggle("ready", !!device));
    const reference = isReferenceMode();
    $("referenceRouting").hidden = !reference;
    document.querySelectorAll(".method-option").forEach((label) => label.classList.toggle("selected", label.querySelector("input").checked));
    $("methodDescription").textContent = reference
      ? "Compares the microphone arrival with the output recorded through a cable on the same interface. Includes speaker/mic response, sound travel, and analog-path differences."
      : "Measures playback-to-microphone round-trip delay. Includes computer and interface buffering, the speaker, microphone, and sound travel.";
    $("referenceWiring").textContent = `Connect output ${$("referenceOutputChannel").value || "—"} to input ${$("referenceChannel").value || "—"} with a balanced TRS cable. Keep phantom power off on the reference input and input monitoring off. Use channels separate from the speaker and microphone.`;
    $("stimulusAdaptation").textContent = `${rate === 96 ? "96 kHz is an interface adaptation; the paper used 192 kHz." : "192 kHz matches the paper’s sample rate."} Original tone order, exact ramp shape, and acoustic level were not available.`;
  }

  function updatePlan() {
    const count = Number($("tonesPerFrequency").value);
    const valid = Number.isInteger(count) && count >= 1 && count <= 600;
    $("toneCountDisplay").textContent = valid ? (count * 14).toLocaleString() : "—";
    const duration = valid ? (count * 14 * 0.01).toLocaleString(undefined, { maximumFractionDigits: 2 }) : "—";
    $("durationDisplay").replaceChildren(document.createTextNode(duration), Object.assign(document.createElement("span"), { textContent: " s" }));
  }

  function updateAvailability() {
    const locked = busy();
    routeInputs.forEach((input) => { input.disabled = locked; });
    document.querySelectorAll("[data-start]").forEach((button) => { button.disabled = locked || !state.online || !currentDevice() || !state.token; });
    $("refreshDevices").disabled = locked;
    $("stopRun").disabled = state.stopping || !state.running;
    $("stopRun").textContent = state.stopping ? "Stopping…" : "■ Stop";
    $("quitApp").disabled = state.quitting || state.closed || !state.token;
    $("quitApp").textContent = state.quitting ? "Closing…" : state.closed ? "App closed" : "Quit app";
    document.body.classList.toggle("is-running", locked && !state.closed);
  }

  function readConfig(action) {
    const device = currentDevice();
    if (!device) throw new Error("Choose an audio interface in setup first.");
    const numeric = (id, min, max, integer = false) => {
      const input = $(id);
      const value = input.value.trim() === "" ? NaN : Number(input.value);
      if (!Number.isFinite(value) || value < min || value > max || (integer && !Number.isInteger(value))) {
        input.focus();
        throw new Error(`${input.closest("label").childNodes[0].textContent.trim()} must be ${integer ? "a whole number " : ""}between ${min} and ${max}.`);
      }
      return value;
    };
    const config = {
      action,
      device: Number(device.index),
      sample_rate: numeric("sampleRate", 96000, 192000, true),
      output_channel: numeric("outputChannel", 1, Number(device.max_output_channels), true),
      input_channel: numeric("inputChannel", 1, Number(device.max_input_channels), true),
      reference_channel: null,
      reference_output_channel: null,
      peak_dbfs: numeric("peakDbfs", -60, -18),
      repetitions: action === "calibrate" ? numeric("repetitions", 3, 40, true) : 10,
      tones_per_frequency: action === "stimulus" ? numeric("tonesPerFrequency", 1, 600, true) : 600,
      seed: action === "stimulus" ? numeric("seed", 0, 4294967295, true) : 20261023,
      distance_m: $("distanceM").value.trim() ? numeric("distanceM", 0, 100) : null,
    };
    if (action === "calibrate" && isReferenceMode()) {
      config.reference_channel = numeric("referenceChannel", 1, Number(device.max_input_channels), true);
      config.reference_output_channel = numeric("referenceOutputChannel", 1, Number(device.max_output_channels), true);
      if (config.reference_channel === config.input_channel || config.reference_output_channel === config.output_channel) throw new Error("Electrical reference needs a separate input and output. Choose different reference channels, or use the simple timing method.");
    }
    return config;
  }

  async function startRun(action) {
    if (busy()) return;
    showError("");
    let config;
    try { config = readConfig(action); } catch (error) { showError(error.message); return; }
    if (action === "calibrate") clearCalibration();
    else $("stimulusResult").hidden = true;
    state.starting = true;
    updateAvailability();
    try {
      const status = await api("/api/start", { method: "POST", body: JSON.stringify(config) });
      state.starting = false;
      if (status.state) applyStatus(status); else await pollStatus();
    } catch (error) { state.starting = false; showError(error.message); }
    updateAvailability();
  }

  async function stopRun() {
    if (!state.running || state.stopping) return;
    state.stopping = true;
    updateAvailability();
    try {
      const status = await api("/api/stop", { method: "POST", body: "{}" });
      if (status.state) applyStatus(status); else await pollStatus();
    } catch (error) { state.stopping = false; showError(`Could not confirm Stop: ${error.message} Check the launcher window if audio continues.`); }
    updateAvailability();
  }

  async function quitApp() {
    if (state.quitting || state.closed) return;
    state.quitting = true;
    updateAvailability();
    try {
      await api("/api/quit", { method: "POST", body: "{}" });
      state.closed = true;
      state.quitting = false;
      state.running = false;
      state.stopping = false;
      clearInterval(state.pollTimer);
      $("runDock").hidden = true;
      $("appClosed").hidden = false;
      showError("");
      setConnection(false, "App closed");
    } catch (error) {
      state.quitting = false;
      showError(`Could not confirm that the app closed. ${error.message} Check the launcher window.`);
    }
    updateAvailability();
  }

  function clearCalibration() {
    $("delayEmpty").hidden = false;
    $("delayResult").hidden = true;
    $("delayResult").replaceChildren();
    $("delayResultTag").textContent = "NOT MEASURED";
    $("delayResultTag").className = "result-tag";
  }

  function textElement(tag, text, className) {
    const node = document.createElement(tag);
    node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function addResultDetails(container, result) {
    const details = document.createElement("details");
    details.className = "result-details";
    details.append(textElement("summary", "Analysis & run details"), textElement("pre", JSON.stringify(result, null, 2)));
    container.append(details);
  }

  const formatMs = (value, digits = 2) => Number.isFinite(value) ? Number(value).toLocaleString(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits }) : "—";

  function renderCalibration(result) {
    const target = $("delayResult");
    target.replaceChildren();
    $("delayEmpty").hidden = true;
    target.hidden = false;
    const usable = result.usable_measurement === true && Number.isFinite(result.measured_delay_ms);
    $("delayResultTag").textContent = usable ? "MEASURED" : "CHECK SIGNAL";
    $("delayResultTag").className = `result-tag ${usable ? "success" : "warning"}`;
    if (usable) {
      const number = textElement("div", formatMs(result.measured_delay_ms), "result-number");
      number.append(textElement("span", "ms"));
      target.append(number, textElement("p", result.mode === "electrical_reference" ? "Microphone arrival relative to electrical reference" : "Playback → microphone round-trip", "result-label"));
      const summary = result.summary || {};
      const stats = document.createElement("dl");
      stats.className = "result-stats";
      const items = [
        ["Accepted chirps", `${summary.accepted_trials ?? "—"} / ${summary.total_trials ?? "—"}`],
        ["5th–95th percentile", `${formatMs(summary.p05_delay_ms)}–${formatMs(summary.p95_delay_ms)} ms`],
      ];
      items.forEach(([label, value]) => { const item = document.createElement("div"); item.append(textElement("dt", label), textElement("dd", value)); stats.append(item); });
      target.append(stats);
    } else target.append(textElement("p", "No usable delay estimate. Check speaker/microphone channels, recording gain, background noise, and clipping, then measure again.", "result-warning"));
    const interpretation = result.interpretation;
    if (interpretation) target.append(textElement("p", typeof interpretation === "string" ? interpretation : JSON.stringify(interpretation), "result-interpretation"));
    if (usable) {
      const sampleRate = Number(state.lastStatus?.config?.sample_rate || result.transport?.sample_rate);
      const interval = sampleRate > 0 ? ` Sample interval: ${formatMs(1e6 / sampleRate, 2)} µs.` : "";
      target.append(textElement("p", `Waveform alignment on the recording grid.${interval} This is not independently calibrated timing accuracy or button-to-sound latency.`, "result-interpretation"));
    }
    const config = state.lastStatus?.config;
    if (config) {
      const capturedDevice = state.devices.find((device) => Number(device.index) === Number(config.device));
      const deviceName = capturedDevice?.name || `Device ${config.device}`;
      const rate = Number(config.sample_rate) / 1000;
      const reference = config.reference_channel == null ? "simple method" : `reference out ${config.reference_output_channel} → in ${config.reference_channel}`;
      target.append(textElement("p", `Measured setup: ${deviceName} · ${rate} kHz · speaker out ${config.output_channel} → mic in ${config.input_channel} · ${reference}.`, "result-interpretation"));
    }
    addResultDetails(target, result);
  }

  function renderStimulus(result) {
    const target = $("stimulusResult");
    target.replaceChildren();
    target.append(textElement("h3", "SONIC playback saved."));
    const duration = Number.isFinite(result.duration_seconds) ? ` · ${result.duration_seconds.toLocaleString(undefined, { maximumFractionDigits: 2 })} seconds` : "";
    target.append(textElement("p", `${Number.isFinite(result.tone_count) ? result.tone_count.toLocaleString() : "Generated"} tone pips${duration}. Playback does not record the microphone or establish a calibrated delay or acoustic level.`));
    addResultDetails(target, result);
    target.hidden = false;
  }

  function applyStatus(status) {
    if (state.closed) return;
    state.lastStatus = status;
    state.running = status.state === "running" || status.state === "stopping";
    if (status.state === "stopping") state.stopping = true;
    if (!state.running) state.stopping = false;
    $("runDock").hidden = !state.running;
    $("runTitle").textContent = status.action === "stimulus" ? "Playing the SONIC sequence" : "Measuring acoustic timing";
    $("runMessage").textContent = status.message || "Audio run in progress…";
    const progress = Math.max(0, Math.min(1, Number(status.progress) || 0));
    $("runProgress").style.width = `${progress * 100}%`;
    $("runPercent").textContent = `${Math.round(progress * 100)}%`;
    if (status.run_path) {
      state.runPath = status.run_path;
      state.lastRecord = status;
      $("runPath").textContent = status.run_path;
      $("runRecord").hidden = false;
    }
    const resultKey = `${status.run_path || ""}|${status.state}|${JSON.stringify(status.result || null)}`;
    if (status.state === "completed" && status.result && resultKey !== state.lastResultKey) {
      state.lastResultKey = resultKey;
      if (status.action === "stimulus" || status.result.kind === "sonic_e14_reconstruction") renderStimulus(status.result);
      else if (status.action === "calibrate" || "measured_delay_ms" in status.result) renderCalibration(status.result);
    }
    if (status.state === "failed" && resultKey !== state.lastResultKey) {
      if (status.action === "calibrate") clearCalibration();
      state.lastResultKey = resultKey;
      showError(status.message || (status.errors || []).join(" ") || "The run failed. Check the interface connection and launcher window.");
    }
    if (status.state === "cancelled" && resultKey !== state.lastResultKey) {
      if (status.action === "calibrate") clearCalibration();
      state.lastResultKey = resultKey;
      toast("Run stopped. Partial files may be saved; this is not a completed measurement.");
    }
    updateAvailability();
  }

  async function pollStatus() {
    if (state.polling || state.closed) return;
    state.polling = true;
    try {
      const status = await api("/api/status");
      if (state.closed) return;
      setConnection(true, state.devices.length ? "Local engine ready" : "Connect an interface");
      applyStatus(status);
    } catch (error) {
      setConnection(false, "Engine disconnected");
      if (state.running) {
        $("runMessage").textContent = "Connection lost. Check the launcher window to stop or confirm audio.";
        showError("Connection to the local engine was lost during a run. Check the launcher window to confirm audio has stopped.");
      }
      updateAvailability();
    } finally { state.polling = false; }
  }

  function toast(message) {
    clearTimeout(toastTimer);
    $("toast").textContent = message;
    $("toast").hidden = false;
    toastTimer = setTimeout(() => { $("toast").hidden = true; }, 4500);
  }

  document.querySelectorAll("[data-panel]").forEach((button) => button.addEventListener("click", () => showPanel(button.dataset.panel)));
  document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => { showPanel(button.dataset.go); window.scrollTo({ top: 0, behavior: "instant" }); }));
  window.addEventListener("hashchange", () => showPanel(location.hash.slice(1), false));
  $("device").addEventListener("change", onDeviceChange);
  $("refreshDevices").addEventListener("click", () => { showError(""); loadDevices(); });
  routeInputs.filter((input) => input.id !== "device").forEach((input) => input.addEventListener("change", () => { clearCalibration(); updateRouting(); }));
  $("tonesPerFrequency").addEventListener("input", updatePlan);
  $("startCalibration").addEventListener("click", () => startRun("calibrate"));
  $("startStimulus").addEventListener("click", () => startRun("stimulus"));
  $("stopRun").addEventListener("click", stopRun);
  $("quitApp").addEventListener("click", quitApp);
  $("downloadResult").addEventListener("click", () => {
    if (!state.lastRecord) return;
    const url = URL.createObjectURL(new Blob([JSON.stringify(state.lastRecord, null, 2)], { type: "application/json" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "sonic-run-result.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  $("copyRunPath").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(state.runPath); toast("Run path copied."); }
    catch (_) { toast("Select and copy the path shown beside this button."); }
  });
  window.addEventListener("keydown", (event) => { if (event.key === "Escape" && state.running && !state.stopping) stopRun(); });

  async function init() {
    showPanel(location.hash.slice(1), false);
    updatePlan();
    updateAvailability();
    try {
      const session = await api("/api/session");
      if (!session.token) throw new Error("The local engine did not provide a session token. Restart the app and refresh this page.");
      state.token = session.token;
      await loadDevices();
      await pollStatus();
    } catch (error) { setConnection(false, "Engine disconnected"); showError(error.message); }
    updateAvailability();
    state.pollTimer = window.setInterval(pollStatus, 1000);
  }
  init();
})();
