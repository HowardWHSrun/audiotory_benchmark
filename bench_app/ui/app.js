"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const state = { token: null, devices: [], running: false, starting: false, stopping: false, quitting: false, closed: false, online: false, lastStatus: null, lastRecord: null, lastResultKey: null, runPath: "", polling: false, pollTimer: null, panel: "live", live: null, liveReceivedAt: 0, livePolling: false, liveTimer: null, probeStarting: false, sonicStarting: false, sonicTarget: null, liveError: "", spectrumColumns: [], lastLiveFrames: null };
  const routeInputs = Array.from(document.querySelectorAll("[data-route]"));
  const panelNames = new Set(["live", "setup", "delay", "stimulus"]);
  let toastTimer;

  function showPanel(name, updateHash = true) {
    if (!panelNames.has(name)) name = "live";
    state.panel = name;
    document.body.classList.toggle("live-view", name === "live");
    document.querySelectorAll(".panel").forEach((panel) => { panel.hidden = panel.id !== `panel-${name}`; });
    document.querySelectorAll(".nav-item").forEach((item) => {
      const selected = item.dataset.panel === name;
      item.classList.toggle("selected", selected);
      if (selected) item.setAttribute("aria-current", "step"); else item.removeAttribute("aria-current");
    });
    if (updateHash && location.hash !== `#${name}`) history.replaceState(null, "", `#${name}`);
    document.title = `${{ live: "Live sound", setup: "Setup", delay: "Measure delay", stimulus: "Play SONIC" }[name]} · SONIC Sound Bench`;
    if (name === "live") { renderLive(); pollLive(); }
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
    const monitoring = state.running && state.lastStatus?.action === "monitor";
    $("playLiveProbe").disabled = !monitoring || !liveFresh() || !state.online || state.stopping || state.probeStarting || state.sonicStarting || state.live?.probe_playing === true || state.live?.sonic_playing === true;
    $("playLiveProbe").textContent = state.probeStarting || (monitoring && state.live?.probe_playing) ? "Playing chirps…" : "Play chirps";
    const sonicPlaying = monitoring && state.live?.sonic_playing === true;
    $("toggleLiveSonic").disabled = !monitoring || !state.online || state.stopping || state.sonicStarting || (!sonicPlaying && (!liveFresh() || state.probeStarting || state.live?.probe_playing === true));
    $("toggleLiveSonic").textContent = state.sonicStarting ? state.sonicTarget ? "Starting…" : "Stopping…" : sonicPlaying ? "Stop SONIC" : "SONIC loop";
    $("toggleLiveSonic").setAttribute("aria-pressed", String(sonicPlaying));
    $("toggleLiveSonic").classList.toggle("playing", sonicPlaying);
    $("stopLive").disabled = state.stopping || !state.running;
    $("stopLive").textContent = state.stopping ? "Stopping…" : "■ Stop";
    $("startMonitor").textContent = monitoring ? "Mic running" : "Start mic";
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
      repetitions: action === "calibrate" || action === "monitor" ? numeric("repetitions", 3, 40, true) : 10,
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
    else if (action === "stimulus") $("stimulusResult").hidden = true;
    resetLive();
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
      clearInterval(state.liveTimer);
      renderLive();
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
    $("runTitle").textContent = status.action === "monitor" ? "Live microphone" : status.action === "stimulus" ? "Playing the SONIC sequence" : "Measuring acoustic timing";
    $("runDock").classList.toggle("monitor-dock", status.action === "monitor");
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
      toast(status.action === "monitor" ? "Live microphone stopped." : "Run stopped. Partial files may be saved; this is not a completed measurement.");
    }
    updateAvailability();
    renderLive();
    if (state.panel === "live" && state.running) pollLive();
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
      renderLive();
    } finally { state.polling = false; }
  }

  function toast(message) {
    clearTimeout(toastTimer);
    $("toast").textContent = message;
    $("toast").hidden = false;
    toastTimer = setTimeout(() => { $("toast").hidden = true; }, 4500);
  }

  const liveFreshLimitMs = 1000;
  const liveHistorySeconds = 20;

  function resetLive() {
    state.live = null;
    state.liveReceivedAt = 0;
    state.liveError = "";
    state.sonicStarting = false;
    state.sonicTarget = null;
    state.spectrumColumns = [];
    state.lastLiveFrames = null;
    renderLive();
  }

  function liveFresh() {
    const age = state.live?.age_ms == null ? NaN : Number(state.live.age_ms);
    return state.running && state.online && !state.closed && state.live?.active === true
      && Number(state.live?.frames) > 0 && Number.isFinite(age) && age + performance.now() - state.liveReceivedAt < liveFreshLimitMs
      && !state.liveError;
  }

  function canvasFrame(id, horizontalLines = 4, verticalLines = 4) {
    const canvas = $(id);
    const bounds = canvas.getBoundingClientRect();
    const width = Math.max(1, Math.round(bounds.width));
    const height = Math.max(1, Math.round(bounds.height));
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    if (canvas.width !== Math.round(width * ratio) || canvas.height !== Math.round(height * ratio)) {
      canvas.width = Math.round(width * ratio);
      canvas.height = Math.round(height * ratio);
    }
    const context = canvas.getContext("2d");
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);
    context.fillStyle = "#fff";
    context.fillRect(0, 0, width, height);
    context.strokeStyle = "#e9ecee";
    context.lineWidth = 1;
    context.beginPath();
    for (let index = 0; index <= horizontalLines; index += 1) {
      const y = Math.round(index * (height - 1) / horizontalLines) + 0.5;
      context.moveTo(0, y); context.lineTo(width, y);
    }
    for (let index = 0; index <= verticalLines; index += 1) {
      const x = Math.round(index * (width - 1) / verticalLines) + 0.5;
      context.moveTo(x, 0); context.lineTo(x, height);
    }
    context.stroke();
    return { context, width, height };
  }

  const finiteArray = (values) => Array.isArray(values) && values.length > 0 && values.every(Number.isFinite);
  const dbLabel = (value) => Number.isFinite(value) ? `${value <= -120 ? "≤−120" : value.toFixed(1)} dBFS` : "—";

  function drawWaveform(id, signal, prefix, emptyId, emptyText) {
    const { context, width, height } = canvasFrame(id, 2, 4);
    const hasData = signal && finiteArray(signal.min) && finiteArray(signal.max);
    $(emptyId).hidden = !!hasData;
    $(emptyId).textContent = emptyText;
    const meter = $(`${prefix}Meter`);
    $(`${prefix}Rms`).textContent = hasData ? dbLabel(signal.rms_dbfs) : "—";
    $(`${prefix}Peak`).textContent = hasData ? dbLabel(signal.peak_dbfs) : "—";
    const level = hasData && Number.isFinite(signal.rms_dbfs) ? Math.max(-120, Math.min(0, signal.rms_dbfs)) : null;
    meter.style.width = level == null ? "0%" : `${(level + 120) / 120 * 100}%`;
    meter.parentElement.classList.toggle("clipped", hasData && !!signal.clipped);
    if (level == null) meter.parentElement.removeAttribute("aria-valuenow");
    else meter.parentElement.setAttribute("aria-valuenow", String(level));
    if (!hasData) { $(`${prefix}Scale`).textContent = "500 ms"; return; }
    const count = Math.min(signal.min.length, signal.max.length);
    const peak = Math.max(...signal.min.map(Math.abs), ...signal.max.map(Math.abs));
    const scale = Math.min(1, Math.max(0.00001, peak * 1.15));
    const duration = Number(state.live?.window_ms) || 500;
    $(`${prefix}Scale`).textContent = `${duration} ms · ±${scale.toPrecision(2)} FS`;
    context.strokeStyle = signal.clipped ? "#9b2b35" : "#252b30";
    context.lineWidth = Math.max(1, width / count * 0.7);
    context.beginPath();
    for (let index = 0; index < count; index += 1) {
      const x = (index + 0.5) * width / count;
      context.moveTo(x, height * (0.5 - Math.max(-1, Math.min(1, signal.min[index] / scale)) * 0.46));
      context.lineTo(x, height * (0.5 - Math.max(-1, Math.min(1, signal.max[index] / scale)) * 0.46));
    }
    context.stroke();
  }

  function usableSpectrum(spectrum) {
    return spectrum && finiteArray(spectrum.frequency_hz) && finiteArray(spectrum.dbfs)
      && spectrum.frequency_hz.length === spectrum.dbfs.length;
  }

  function drawSpectrum(spectrum) {
    const { context, width, height } = canvasFrame("microphoneSpectrum", 4, 4);
    const available = usableSpectrum(spectrum);
    $("spectrumEmpty").hidden = !!available;
    $("spectrumEmpty").textContent = state.live?.has_input === false ? "Microphone not recorded" : "Start mic";
    if (!available) return;
    const xPosition = (frequency) => Math.log(Math.max(20, frequency) / 20) / Math.log(40000 / 20) * width;
    context.strokeStyle = "#22282d";
    context.lineWidth = 1.4;
    context.beginPath();
    let started = false;
    spectrum.frequency_hz.forEach((frequency, index) => {
      if (frequency < 20 || frequency > 40000) return;
      const x = xPosition(frequency);
      const y = height * (1 - (Math.max(-120, Math.min(0, spectrum.dbfs[index])) + 120) / 120);
      if (!started) { context.moveTo(x, y); started = true; } else context.lineTo(x, y);
    });
    context.stroke();
    context.fillStyle = "#849097";
    context.font = "9px -apple-system, sans-serif";
    context.fillText("0", 5, 11);
    context.fillText("−60", 5, height / 2 - 4);
    context.fillText("−120", 5, height - 5);
  }

  function spectrumRaster(spectrum) {
    const raster = document.createElement("canvas");
    raster.width = 1; raster.height = 256;
    const context = raster.getContext("2d");
    const image = context.createImageData(1, raster.height);
    const frequencies = spectrum.frequency_hz;
    for (let row = 0; row < raster.height; row += 1) {
      const frequency = 20 * Math.pow(40000 / 20, 1 - row / (raster.height - 1));
      let low = 0, high = frequencies.length - 1;
      while (low < high) {
        const middle = Math.floor((low + high) / 2);
        if (frequencies[middle] < frequency) low = middle + 1; else high = middle;
      }
      const index = low > 0 && frequency - frequencies[low - 1] < frequencies[low] - frequency ? low - 1 : low;
      const available = frequency >= frequencies[0] && frequency <= frequencies[frequencies.length - 1];
      const shade = available ? Math.round(255 - Math.max(0, Math.min(1, (spectrum.dbfs[index] + 100) / 80)) * 230) : 255;
      image.data[row * 4] = shade; image.data[row * 4 + 1] = shade; image.data[row * 4 + 2] = shade; image.data[row * 4 + 3] = 255;
    }
    context.putImageData(image, 0, 0);
    return raster;
  }

  function drawSpectrogram() {
    const { context, width, height } = canvasFrame("microphoneSpectrogram", 4, 4);
    const columns = state.spectrumColumns;
    $("spectrogramEmpty").hidden = columns.length > 0;
    $("spectrogramEmpty").textContent = state.live?.has_input === false ? "Microphone not recorded" : "Start mic";
    if (!columns.length) return;
    const latest = columns[columns.length - 1].time;
    const left = latest - liveHistorySeconds;
    const xPosition = (time) => (time - left) / liveHistorySeconds * width;
    const yPosition = (frequency) => height * (1 - Math.log(Math.max(20, Math.min(40000, frequency)) / 20) / Math.log(40000 / 20));
    columns.forEach((column, columnIndex) => {
      const x = xPosition(column.time);
      const nextTime = columns[columnIndex + 1]?.time;
      const duration = nextTime == null ? 0.1 : Math.min(0.2, Math.max(0.01, nextTime - column.time));
      const columnWidth = Math.max(1, duration / liveHistorySeconds * width);
      context.drawImage(column.raster, x, 0, columnWidth + 0.5, height);
    });
    context.fillStyle = "#6f7b82";
    context.font = "9px -apple-system, sans-serif";
    [[40000, "40k"], [1000, "1k"], [20, "20 Hz"]].forEach(([frequency, label]) => {
      const y = Math.max(11, Math.min(height - 4, yPosition(frequency)));
      context.fillStyle = "#ffffffdd"; context.fillRect(2, y - 10, 31, 12);
      context.fillStyle = "#6f7b82"; context.fillText(label, 5, y);
    });
    $("spectrogramHistory").textContent = `${liveHistorySeconds} s · 20 Hz–40 kHz`;
  }

  function friendlyDelayReason(reason) {
    const text = String(reason || "").toLowerCase();
    if (/weak|correlation|quiet|signal/.test(text)) return "Sound too faint to match";
    if (/clip/.test(text)) return "Signal clipped";
    if (/ambig|competing|multiple/.test(text)) return "No clear sound match";
    if (/transport|overflow|underflow|timestamp|clock|discontin/.test(text)) return "Audio interrupted";
    if (/reference/.test(text)) return "Check reference cable";
    if (/bound|window|incomplete/.test(text)) return "Sound outside the timing window";
    return "Chirp could not be matched";
  }

  function drawLiveDelay(delay) {
    const { context, width, height } = canvasFrame("liveDelayPlot", 3, 4);
    const electrical = delay?.mode === "electrical_reference";
    $("liveDelayTitle").textContent = electrical ? "Electrical reference → mic · ms" : "Playback → mic · ms";
    const points = Array.isArray(delay?.points) ? delay.points : [];
    const accepted = points.filter((point) => point.accepted === true && Number.isFinite(point.delay_ms));
    const rejected = points.length - accepted.length;
    const latest = Number.isFinite(delay?.latest_delay_ms) ? delay.latest_delay_ms : null;
    const latestLabel = Number.isFinite(latest) ? `${latest.toFixed(2)} ms` : "—";
    $("liveDelayValue").textContent = latestLabel;
    $("liveDelayNow").textContent = latestLabel;
    $("liveDelaySummaryLabel").textContent = electrical ? "Electrical reference → mic" : "Playback → mic";
    $("liveDelayNowStatus").textContent = !liveFresh() && points.length ? "Last match" : Number.isFinite(latest) ? "Live match" : points.length ? "No reliable match" : "Waiting for sound";
    $("liveDelayCount").textContent = points.length ? `${accepted.length} accepted${rejected ? ` · ${rejected} rejected` : ""}` : "";
    $("liveDelayEmpty").hidden = accepted.length > 0;
    $("liveDelayEmpty").textContent = delay?.reference_required ? "Connect electrical reference" : points.length ? "No reliable match" : "Play chirps or SONIC loop";
    $("liveDelayStatus").textContent = rejected ? friendlyDelayReason(points.filter((point) => !point.accepted).slice(-1)[0]?.reason) : accepted.length ? "Waveform matches" : "No delay measured";
    if (!accepted.length) return;
    const values = accepted.map((point) => point.delay_ms);
    const minimum = Math.min(...values), maximum = Math.max(...values);
    const padding = Math.max(0.25, (maximum - minimum) * 0.2);
    const low = Math.max(0, minimum - padding), high = maximum + padding;
    const chartLeft = 43, chartRight = width - 12, chartTop = 12, chartBottom = height - 18;
    const trials = points.map((point, index) => Number.isFinite(point.trial) ? point.trial : index + 1);
    const firstTrial = Math.min(...trials), lastTrial = Math.max(...trials);
    const xPosition = (point, index) => chartLeft + ((Number.isFinite(point.trial) ? point.trial : index + 1) - firstTrial) / Math.max(1, lastTrial - firstTrial) * (chartRight - chartLeft);
    const yPosition = (value) => chartBottom - (value - low) / Math.max(0.001, high - low) * (chartBottom - chartTop);
    context.fillStyle = "#7b878f"; context.font = "9px -apple-system, sans-serif";
    [low, (high + low) / 2, high].forEach((value) => context.fillText(value.toFixed(2), 3, yPosition(value) + 3));
    points.forEach((point, index) => {
      const x = xPosition(point, index);
      if (point.accepted === true && Number.isFinite(point.delay_ms)) {
        context.beginPath(); context.fillStyle = "#252b30"; context.arc(x, yPosition(point.delay_ms), 3, 0, Math.PI * 2); context.fill();
      } else {
        context.strokeStyle = "#b3bbc0"; context.beginPath(); context.moveTo(x - 3, chartBottom - 3); context.lineTo(x + 3, chartBottom + 3); context.moveTo(x - 3, chartBottom + 3); context.lineTo(x + 3, chartBottom - 3); context.stroke();
      }
    });
  }

  function renderLive() {
    if (state.panel !== "live") return;
    const data = state.live;
    const fresh = liveFresh();
    const hasTrace = Number(data?.frames) > 0;
    const label = fresh ? "LIVE" : state.running && hasTrace ? "STALE" : hasTrace ? "STOPPED · LAST TRACE" : state.running ? "STARTING" : "NOT STARTED";
    $("liveState").textContent = label;
    $("liveState").classList.toggle("fresh", fresh);
    $("panel-live").classList.toggle("live-inactive", !fresh);
    const traceLabel = fresh ? "LIVE" : hasTrace ? "LAST TRACE" : "WAITING";
    $("outputTraceState").textContent = data?.output?.clipped ? "CLIPPED" : traceLabel;
    $("micTraceState").textContent = data?.has_input === false ? "NOT RECORDED" : data?.microphone?.clipped ? "CLIPPED" : traceLabel;
    $("spectrumTraceState").textContent = data?.has_input === false ? "NOT RECORDED" : traceLabel;
    $("spectrogramTraceState").textContent = $("spectrumTraceState").textContent;
    const config = state.running ? state.lastStatus?.config : null;
    const repeats = config?.repetitions || Number($("repetitions").value) || 10;
    const level = config?.peak_dbfs ?? Number($("peakDbfs").value);
    $("liveProbeSettings").textContent = `${repeats} chirps · ${level} dBFS`;
    $("liveCaptureInfo").textContent = state.lastStatus?.action === "monitor" || !state.running ? "Live monitoring does not save room audio." : "This run saves its normal local records. Live plots do not establish neural alignment.";
    const errors = Array.isArray(data?.transport_errors) ? data.transport_errors : [];
    const notice = state.liveError || errors.join(" · ") || (state.running && hasTrace && !fresh ? "Live data paused — showing the last trace." : "");
    $("liveNotice").textContent = notice;
    $("liveNotice").hidden = !notice;
    drawWaveform("outputWaveform", data?.output, "output", "outputEmpty", "No outgoing signal");
    drawWaveform("microphoneWaveform", data?.microphone, "microphone", "microphoneEmpty", data?.has_input === false ? "Microphone not recorded" : "Start mic");
    drawSpectrum(data?.has_input === false ? null : data?.spectrum);
    drawSpectrogram();
    drawLiveDelay(data?.delay);
  }

  async function pollLive() {
    if (state.panel !== "live" || !state.running || state.closed) return;
    renderLive();
    if (state.livePolling || !state.online) return;
    state.livePolling = true;
    try {
      const data = await api("/api/live");
      if (state.closed) return;
      const frames = Number(data.frames);
      if (Number.isFinite(frames) && state.lastLiveFrames != null && frames < state.lastLiveFrames) state.spectrumColumns = [];
      const isNew = Number.isFinite(frames) && frames !== state.lastLiveFrames;
      state.live = data;
      state.liveReceivedAt = performance.now();
      state.liveError = "";
      if (isNew && data.has_input !== false && data.active && Number(data.age_ms) < liveFreshLimitMs && usableSpectrum(data.spectrum) && Number(data.sample_rate_hz) > 0) {
        const time = frames / data.sample_rate_hz;
        state.spectrumColumns.push({ time, raster: spectrumRaster(data.spectrum) });
        state.spectrumColumns = state.spectrumColumns.filter((column) => time - column.time <= liveHistorySeconds).slice(-240);
      }
      state.lastLiveFrames = Number.isFinite(frames) ? frames : state.lastLiveFrames;
      renderLive();
      updateAvailability();
    } catch (error) {
      state.liveError = `Live display unavailable: ${error.message}`;
      renderLive();
    } finally { state.livePolling = false; }
  }

  async function playLiveProbe() {
    if (!state.running || state.lastStatus?.action !== "monitor" || state.probeStarting || state.sonicStarting || state.live?.probe_playing || state.live?.sonic_playing) return;
    state.probeStarting = true;
    showError("");
    updateAvailability();
    try {
      await api("/api/live/probe", { method: "POST", body: "{}" });
      await pollLive();
    } catch (error) { showError(error.message); }
    finally { state.probeStarting = false; updateAvailability(); }
  }

  async function toggleLiveSonic() {
    if (!state.running || state.lastStatus?.action !== "monitor" || state.sonicStarting || state.probeStarting || state.live?.probe_playing) return;
    const enabled = state.live?.sonic_playing !== true;
    state.sonicStarting = true;
    state.sonicTarget = enabled;
    showError("");
    updateAvailability();
    try {
      const result = await api("/api/live/sonic", { method: "POST", body: JSON.stringify({ enabled }) });
      if (typeof result.sonic_playing === "boolean" && state.live) state.live.sonic_playing = result.sonic_playing;
      await pollLive();
    } catch (error) { showError(error.message); }
    finally { state.sonicStarting = false; state.sonicTarget = null; updateAvailability(); }
  }

  window.addEventListener("resize", () => renderLive());
  document.querySelector(".live-waveform-details").addEventListener("toggle", () => renderLive());

  document.querySelectorAll("[data-panel]").forEach((button) => button.addEventListener("click", () => showPanel(button.dataset.panel)));
  document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => { showPanel(button.dataset.go); window.scrollTo({ top: 0, behavior: "instant" }); }));
  window.addEventListener("hashchange", () => showPanel(location.hash.slice(1), false));
  $("device").addEventListener("change", onDeviceChange);
  $("refreshDevices").addEventListener("click", () => { showError(""); loadDevices(); });
  routeInputs.filter((input) => input.id !== "device").forEach((input) => input.addEventListener("change", () => { clearCalibration(); updateRouting(); }));
  $("tonesPerFrequency").addEventListener("input", updatePlan);
  $("startMonitor").addEventListener("click", () => startRun("monitor"));
  $("playLiveProbe").addEventListener("click", playLiveProbe);
  $("toggleLiveSonic").addEventListener("click", toggleLiveSonic);
  $("stopLive").addEventListener("click", stopRun);
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
    state.liveTimer = window.setInterval(pollLive, 100);
  }
  init();
})();
