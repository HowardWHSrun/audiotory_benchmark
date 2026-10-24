import { BrowserBench } from './audio.mjs';

const $ = (id) => document.getElementById(id);
const inputs = { inputDevice: $('inputDevice'), outputDevice: $('outputDevice'), sampleRate: $('sampleRate'), inputChannel: $('inputChannel'), outputChannel: $('outputChannel'), referenceChannel: $('referenceChannel'), referenceOutputChannel: $('referenceOutputChannel'), peakDbfs: $('peakDbfs'), repetitions: $('repetitions'), seed: $('seed'), distanceM: $('distanceM') };
const state = { connected: false, busy: false, phase: 'idle', connection: null, tab: 'stimulus', calibration: null, playback: null, lastAction: null, generation: 0, devices: [] };
const outputSelection = Boolean((globalThis.AudioContext || globalThis.webkitAudioContext)?.prototype?.setSinkId);
let currentStatus = {};
const engine = new BrowserBench({ onStatus: onEngineStatus });

function make(tag, className, content) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (content !== undefined) element.textContent = content;
  return element;
}

function notice(message = '', error = false) {
  $('globalNotice').textContent = message;
  $('globalNotice').classList.toggle('error', error);
  $('globalNotice').hidden = !message;
}

function selectedMethod() { return document.querySelector('input[name="referenceMode"]:checked').value; }
function selectedCount() { return Number(document.querySelector('input[name="sequenceLength"]:checked').value); }
function actualRate() { return Number(state.connection?.sampleRate || state.connection?.contextRate || 0); }
function hasUsableCalibration() { return state.calibration?.usable_measurement === true && Number.isFinite(state.calibration?.summary?.median_delay_ms); }
function inputLabel() {
  const id = inputs.inputDevice.value || state.connection?.inputDeviceId;
  return state.devices.find((item) => item.kind === 'audioinput' && item.deviceId === id)?.label
    || state.devices.find((item) => item.kind === 'audioinput' && item.deviceId === 'default')?.label || 'System default input';
}
function outputLabel() {
  const id = outputSelection && inputs.outputDevice.value ? inputs.outputDevice.value : 'default';
  return state.devices.find((item) => item.kind === 'audiooutput' && item.deviceId === id)?.label || 'System default output';
}
function number(value, min, max, name, integer = false) {
  if (typeof value === 'string' && value.trim() === '') throw new Error(`${name} is required.`);
  const parsed = Number(value);
  if (!Number.isFinite(parsed) || parsed < min || parsed > max || (integer && !Number.isInteger(parsed))) throw new Error(`${name} must be ${integer ? 'a whole number ' : ''}between ${min} and ${max}.`);
  return parsed;
}
function settings() {
  return { inputDeviceId: inputs.inputDevice.value, outputDeviceId: outputSelection ? inputs.outputDevice.value : '', sampleRate: Number(inputs.sampleRate.value), inputChannel: Number(inputs.inputChannel.value), outputChannel: Number(inputs.outputChannel.value), referenceChannel: Number(inputs.referenceChannel.value), referenceOutputChannel: Number(inputs.referenceOutputChannel.value) };
}

function updateControls() {
  const supportsRecipe = actualRate() >= 96000;
  const running = ['playing', 'calibrating', 'analyzing'].includes(state.phase);
  const peak = Number(inputs.peakDbfs.value);
  const level = `${Number.isFinite(peak) ? String(peak).replace('-', '−') : '−36'} dBFS digital peak`;
  $('connectionState').classList.toggle('connected', state.connected && !running);
  $('connectionState').classList.toggle('busy', state.busy);
  $('connectionLabel').textContent = state.phase === 'connecting' ? 'Connecting audio…' : running ? 'Audio run in progress' : state.connected ? 'Audio connected' : 'Audio disconnected';
  $('connectAudio').hidden = state.connected || state.phase === 'connecting';
  $('cancelConnect').hidden = state.phase !== 'connecting';
  $('disconnectAudio').hidden = !state.connected;
  $('connectAudio').disabled = state.busy;
  $('connectAudio').firstChild.textContent = state.phase === 'connecting' ? 'Connecting… ' : 'Connect audio ';
  $('disconnectAudio').disabled = state.busy;
  $('refreshDevices').disabled = state.busy;
  for (const field of document.querySelectorAll('[data-connection], [data-level], #repetitions, #seed, #distanceM, input[name="sequenceLength"], input[name="referenceMode"]')) field.disabled = state.busy;
  inputs.outputDevice.disabled = state.busy || !outputSelection;
  $('playStimulus').disabled = state.busy || !state.connected || !supportsRecipe;
  $('measureDelay').disabled = state.busy || !state.connected;
  $('stimulusLevel').textContent = level;
  $('delayLevel').textContent = level;
  $('playLabel').textContent = selectedCount() === 50 ? 'Play quick check' : 'Play full block';
  $('stimulusActionHint').textContent = !state.connected ? 'Connect audio to enable playback.' : !supportsRecipe ? 'A 96 or 192 kHz browser rate is required.' : 'Includes 1 second of silence at each end.';
  $('delayActionHint').textContent = !state.connected ? 'Connect audio to enable the timing check.' : 'Plays chirps while recording the mic.';
  $('formatNotice').hidden = !state.connected || supportsRecipe;
  $('formatNotice').textContent = state.connected && !supportsRecipe ? `This browser opened at ${(actualRate() / 1000).toLocaleString()} kHz. The complete E14 recipe reaches 27 kHz and requires a 96 or 192 kHz browser processing rate here. Set the interface to 96 kHz, reconnect, or use a browser and interface that accept that rate. The recipe has not been truncated.` : '';
  $('stepConnect').classList.toggle('current', !state.connected);
  $('stepConnect').classList.toggle('complete', state.connected);
  $('stepMeasure').classList.toggle('current', state.connected && (!state.calibration || state.tab === 'delay'));
  $('stepMeasure').classList.toggle('complete', hasUsableCalibration());
  $('stepPlay').classList.toggle('current', state.connected && state.tab === 'stimulus' && Boolean(state.calibration));
  $('timingReminder').textContent = hasUsableCalibration() ? 'Timing screening recorded for this setup.' : state.calibration ? 'Timing needs review for this setup.' : 'Timing not checked for this setup.';
  $('runDock').hidden = !running;
  document.body.classList.toggle('running', running);
}

function onEngineStatus(status) {
  if (!status || typeof status !== 'object') return;
  currentStatus = status;
  const wasConnected = state.connected;
  state.phase = status.phase || 'idle';
  state.connected = Boolean(status.connected);
  state.busy = ['connecting', 'playing', 'calibrating', 'analyzing'].includes(state.phase);
  state.connection = status.connection || null;
  $('permissionNote').textContent = state.connected
    ? 'Microphone access is open. Only a delay run retains input; Disconnect releases the microphone.'
    : state.phase === 'connecting'
      ? 'Waiting for microphone access. You can cancel this connection.'
      : 'Connect opens the microphone silently. Only a delay run saves input; sound starts with Play or Measure delay.';
  const connection = state.connection;
  $('rateBadge').hidden = !state.connected;
  $('rateBadge').textContent = connection ? `${(actualRate() / 1000).toLocaleString()} kHz browser` : '';
  $('connectionTitle').textContent = state.connected ? 'Your audio is connected' : 'Connect your audio';
  $('connectionSubtitle').textContent = state.connected ? `${inputLabel()} · ${outputLabel()}` : 'Use one wired interface for the speaker and microphone.';
  const diagnostics = [];
  if (connection) {
    diagnostics.push(`Browser processing graph: ${actualRate()} Hz. Requested: ${connection.requestedSampleRate || inputs.sampleRate.value} Hz.`);
    diagnostics.push(`Input track reported rate: ${connection.inputSettings?.sampleRate || 'unknown'}${connection.inputSettings?.sampleRate ? ' Hz' : ''}. Physical ADC/DAC rates are unverified; resampling may occur.`);
    if (connection.inputChannels) diagnostics.push(`Browser input channels: ${connection.inputChannels}.`);
    if (connection.outputChannels) diagnostics.push(`Browser output channels: ${connection.outputChannels}.`);
    diagnostics.push(connection.processingVerified ? 'Microphone processing reports echo cancellation, noise suppression, and automatic gain control off.' : 'Unprocessed microphone capture has not been verified. Timing may be diagnostic only.');
    if (Number.isFinite(connection.baseLatency)) diagnostics.push(`Reported base latency: ${(connection.baseLatency * 1000).toFixed(2)} ms; this is a browser estimate, not the measured path delay.`);
  }
  if (Array.isArray(status.warnings)) diagnostics.push(...status.warnings);
  $('connectionDiagnostics').textContent = diagnostics.join('\n');
  $('connectionDiagnostics').hidden = !diagnostics.length;
  $('runTitle').textContent = state.phase === 'calibrating' ? 'Measuring playback → microphone' : state.phase === 'analyzing' ? 'Checking the recording' : 'Playing the SONIC reconstruction';
  $('runMessage').textContent = status.message || 'Audio run in progress…';
  const rawProgress = Number(status.progress) || 0;
  const progress = Math.max(0, Math.min(100, rawProgress <= 1 ? rawProgress * 100 : rawProgress));
  $('runProgress').style.width = `${progress}%`;
  $('progressTrack').setAttribute('aria-valuenow', String(Math.round(progress)));
  if (wasConnected && !state.connected && state.calibration) {
    state.calibration = null;
    emptyCalibration('Audio disconnected. Reconnect and run a new timing check.');
  }
  if (state.phase === 'error' && status.message) notice(status.message, true);
  updateControls();
}

function setTab(tab, updateHash = true) {
  state.tab = tab === 'delay' ? 'delay' : 'stimulus';
  for (const [name, panel, button] of [['stimulus', 'panelStimulus', 'tabStimulus'], ['delay', 'panelDelay', 'tabDelay']]) {
    const active = state.tab === name;
    $(panel).hidden = !active;
    $(button).classList.toggle('active', active);
    $(button).setAttribute('aria-selected', String(active));
    $(button).tabIndex = active ? 0 : -1;
  }
  if (updateHash && location.hash !== `#${state.tab}`) history.replaceState(null, '', `#${state.tab}`);
  updateControls();
}

async function refreshDevices() {
  try {
    const devices = await engine.devices();
    state.devices = Array.isArray(devices) ? devices : [];
    for (const [select, kind, fallback] of [[inputs.inputDevice, 'audioinput', 'System default input'], [inputs.outputDevice, 'audiooutput', 'System default output']]) {
      const selected = select.value;
      select.replaceChildren(new Option(fallback, ''));
      const visible = state.devices.filter((item) => item.kind === kind && item.deviceId && item.deviceId !== 'default' && item.deviceId !== 'communications');
      visible.forEach((item, index) => select.append(new Option(item.label || `${kind === 'audioinput' ? 'Microphone' : 'Output'} ${index + 1} · connect to reveal name`, item.deviceId)));
      if ([...select.options].some((option) => option.value === selected)) select.value = selected;
    }
    if (state.connected) onEngineStatus(currentStatus);
  } catch (error) { notice(error.message || 'This browser could not list audio devices.', true); }
}

function emptyCalibration(message = 'Your real result will appear here after a run.') {
  const result = $('delayResult');
  result.className = 'result-card empty-measurement';
  result.replaceChildren(make('span', 'empty-result-icon', '∿'));
  result.firstChild.setAttribute('aria-hidden', 'true');
  const copy = make('div');
  copy.append(make('strong', '', 'No measurement yet'), make('p', '', message));
  result.append(copy);
}

async function invalidateConnection() {
  state.generation += 1;
  state.calibration = null;
  state.playback = null;
  $('playbackResult').hidden = true;
  emptyCalibration('Audio settings changed. Run a new timing check.');
  await engine.disconnect();
  $('connectionPanel').open = true;
  notice('Audio settings changed. Connect again before your next run.');
  updateMethod();
  updateControls();
}

function updateMethod() {
  const electrical = selectedMethod() === 'electrical';
  $('methodDescription').textContent = electrical ? 'Compares microphone arrival with a simultaneously recorded electrical return. This is relative to the line path, rather than the browser playback clock.' : 'Measures the whole playback-to-microphone roundtrip: browser buffers, converters, speaker, air travel, and microphone. It does not isolate acoustic travel time.';
  $('referenceWiring').hidden = !electrical;
  $('referenceWiring').textContent = `Connect output ${inputs.referenceOutputChannel.value} → line input ${inputs.referenceChannel.value}. Keep phantom power off on input ${inputs.referenceChannel.value} and all input monitoring off. The speaker stays on output ${inputs.outputChannel.value}; the mic stays on input ${inputs.inputChannel.value}.`;
}

function exportJson(result, name) {
  download(new Blob([JSON.stringify(result, null, 2)], { type: 'application/json' }), name);
}
function download(blob, name) {
  if (!(blob instanceof Blob)) return;
  const url = URL.createObjectURL(blob);
  const link = make('a');
  link.href = url;
  link.download = name;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function fileStem(kind) { return `sonic-browser-${kind}-${new Date().toISOString().replace(/[:.]/g, '-')}`; }
function exportActions(result, kind, captureBlob, sourceBlob) {
  const actions = make('div', 'download-actions');
  const stem = fileStem(kind);
  const json = make('button', 'text-button', 'Download result JSON ↓');
  json.type = 'button';
  json.addEventListener('click', () => exportJson(result, `${stem}.json`));
  actions.append(json);
  for (const [blob, label, suffix] of [[sourceBlob, 'Source WAV ↓', 'source'], [captureBlob, 'Recorded WAV ↓', 'capture']]) {
    if (!(blob instanceof Blob)) continue;
    const button = make('button', 'text-button', label);
    button.type = 'button';
    button.addEventListener('click', () => download(blob, `${stem}-${suffix}.wav`));
    actions.append(button);
  }
  return actions;
}

function describeResult(result, container, title, badgeText) {
  container.replaceChildren();
  container.className = 'result-card';
  const heading = make('div', 'result-heading');
  const copy = make('div');
  copy.append(make('h3', '', title));
  heading.append(copy, make('span', `result-badge${result.usable_measurement ? ' usable' : ''}`, badgeText));
  container.append(heading);
  return copy;
}

function renderCalibration(result, captureBlob, sourceBlob) {
  const container = $('delayResult');
  const usable = result.usable_measurement === true && Number.isFinite(result.summary?.median_delay_ms);
  const copy = describeResult({ ...result, usable_measurement: usable }, container, usable ? 'Timing screening completed' : 'Timing check needs review', usable ? 'Screening passed' : 'No usable delay');
  copy.append(make('p', '', selectedMethod() === 'electrical' ? 'Microphone relative to recorded electrical return.' : 'Whole browser playback-to-microphone roundtrip.'));
  if (usable) {
    const number = make('div', 'result-number', result.summary.median_delay_ms.toFixed(2));
    number.append(make('small', '', 'ms'));
    container.append(number, make('p', 'result-caption', `${result.summary.accepted_trials} / ${result.summary.total_trials} chirps accepted · median delay`));
    if (Number.isFinite(result.summary.jitter_p95_minus_p05_ms)) container.append(make('p', 'result-detail', `5th–95th percentile spread: ${result.summary.jitter_p95_minus_p05_ms.toFixed(2)} ms. This spread is not calibrated timing accuracy.`));
    container.append(make('p', 'result-detail', 'This result applies to this browser session, routing and geometry. It is not automatically subtracted from playback or neural timestamps.'));
  } else {
    container.append(make('p', 'result-detail', 'No accepted delay is shown. Review the processing, signal, channel and transport checks below, then reconnect or adjust the setup and repeat.'));
    const reason = result.reason || result.message || (Array.isArray(result.warnings) ? result.warnings.join(' ') : '');
    if (reason) container.append(make('p', 'result-detail', reason));
    const checks = resultProblems(result);
    if (checks.length) container.append(make('p', 'result-detail', checks.join(' ')));
  }
  const details = make('details', 'result-details');
  details.append(make('summary', '', 'Diagnostics & run details'));
  const diagnostic = { status: result.status, usable_measurement: usable, summary: result.summary, warnings: result.warnings, diagnostics: result.diagnostics, screen_rejection_reasons: result.screen_rejection_reasons, first_probe_anchor_accepted: result.first_probe_anchor_accepted, diagnostic_candidate_summary: result.diagnostic_candidate_summary, transport: result.transport, trials: result.trials };
  details.append(make('pre', '', JSON.stringify(diagnostic, null, 2)));
  container.append(details, exportActions(result, 'delay', captureBlob, sourceBlob));
}

function resultProblems(result) {
  const reasons = [...(result.screen_rejection_reasons || []), ...(result.transport?.errors || []), ...(result.trials || []).flatMap((trial) => trial.reasons || [])];
  const explanations = {
    browser_input_processing_not_verified_off: 'The browser did not verify that all microphone processing was off.',
    two_distinct_input_channels_not_exposed: 'Two independent input channels were not available to the browser.',
    microphone_missing_or_too_quiet: 'The microphone signal was missing or too quiet.',
    reference_missing_or_too_quiet: 'The reference signal was missing or too quiet.',
    microphone_clipping: 'The microphone clipped; lower its input gain.',
    reference_clipping: 'The reference clipped; lower the line level or gain.',
    weak_correlation: 'The recorded chirp did not match strongly enough; check wiring, gain and background sound.',
    ambiguous_peak: 'Several timing matches were plausible; check reflections and repeat the run.',
    electrical_reference_unavailable: 'The electrical reference input was unavailable.',
    electrical_reference_probe_not_located: 'The electrical return chirp could not be located.',
    capture_integrity_invalid_or_unverified: 'Capture continuity could not be verified.',
    transport_or_processing_unverified: 'The browser transport or input processing checks did not pass.',
    input_channels_missing: 'Input samples were missing during the run.',
    incomplete_search_window: 'The recording did not contain a complete timing search window.',
    boundary_peak_unresolved: 'The timing peak reached the search boundary.',
    primary_lobe_unresolved_at_search_boundary: 'The timing peak could not be resolved within the search window.',
    first_probe_not_accepted_out_of_range_repeat_alias_cannot_be_excluded: 'The first chirp could not be matched. A later repeat may look like a valid delay, so this run was rejected.',
  };
  const unique = [...new Set(reasons)];
  return [...new Set(unique.map((reason) => explanations[reason] || `Capture check: ${reason.replaceAll('_', ' ')}.`))].slice(0, 4);
}

function renderPlayback(result, sourceBlob) {
  const container = $('playbackResult');
  const copy = describeResult(result, container, 'Sequence playback finished', 'Local reconstruction');
  copy.append(make('p', '', `${selectedCount() === 50 ? '700 pips · 7 seconds' : '8,400 pips · 84 seconds'} of tone content. No acoustic level or frequency response was calibrated.`));
  container.append(exportActions(result, 'stimulus', null, sourceBlob));
  container.hidden = false;
}

async function run(kind) {
  if (state.busy || !state.connected) return;
  notice();
  const generation = ++state.generation;
  state.lastAction = kind;
  try {
    const peakDbfs = number(inputs.peakDbfs.value, -60, -18, 'Digital peak level');
    let result;
    if (kind === 'delay') {
      const repetitions = number(inputs.repetitions.value, 3, 20, 'Chirp repeats', true);
      const reference = selectedMethod() === 'electrical';
      if (reference && (inputs.inputChannel.value === inputs.referenceChannel.value || inputs.outputChannel.value === inputs.referenceOutputChannel.value)) throw new Error('The electrical reference needs a different input and output channel from the microphone and speaker. Change the advanced audio settings, then reconnect.');
      const distance = inputs.distanceM.value.trim() === '' ? null : number(inputs.distanceM.value, 0, 100, 'Speaker–mic distance');
      state.calibration = null;
      emptyCalibration('Recording and checking the real signal…');
      result = await engine.calibrate({ repetitions, peakDbfs, reference });
      if (generation !== state.generation) return;
      result = { ...result, user_geometry: { speaker_microphone_distance_m: distance, distance_subtracted: false } };
      state.calibration = result;
      renderCalibration(result, engine.lastCaptureWav, engine.lastSourceWav);
    } else {
      $('playbackResult').hidden = true;
      const seed = number(inputs.seed.value, 0, 4294967295, 'Randomization seed', true);
      result = await engine.play({ tonesPerFrequency: selectedCount(), seed, peakDbfs });
      if (generation !== state.generation) return;
      state.playback = result;
      renderPlayback(result, engine.lastSourceWav);
    }
  } catch (error) {
    if (generation !== state.generation || error.name === 'AbortError') return;
    notice(error.message || 'The audio run could not finish. Review your audio connection and try again.', true);
    if (kind === 'delay') emptyCalibration('The run did not produce a usable measurement.');
  } finally { updateControls(); }
}

async function stopAudio(message = 'Audio stopped. Microphone and output released. Connect again when ready.') {
  state.generation += 1;
  try { await engine.stop(); } finally {
    if (state.lastAction === 'delay' && !state.calibration) emptyCalibration('The timing run was stopped. No measurement was saved.');
    $('connectionPanel').open = true;
    notice(message);
    updateControls();
  }
}

$('connectAudio').addEventListener('click', async () => {
  notice();
  try {
    number(inputs.peakDbfs.value, -60, -18, 'Digital peak level');
    await engine.connect(settings());
    if (state.connected) {
      await refreshDevices();
      $('connectionPanel').open = false;
      $('permissionNote').textContent = 'Microphone access is open. Only a delay run retains input; Disconnect releases the microphone.';
      if (currentStatus.warnings?.length) notice('Audio connected. Review the browser checks in Advanced audio settings before relying on timing.');
    }
  } catch (error) { if (error.name !== 'AbortError') notice(error.message || 'Audio connection failed. Check microphone permission and the selected device.', true); }
  updateControls();
});
$('disconnectAudio').addEventListener('click', async () => { await engine.disconnect(); $('connectionPanel').open = true; notice('Audio disconnected. Microphone and output released.'); });
$('cancelConnect').addEventListener('click', () => stopAudio('Audio connection cancelled. No run started.'));
$('refreshDevices').addEventListener('click', refreshDevices);
$('playStimulus').addEventListener('click', () => run('stimulus'));
$('measureDelay').addEventListener('click', () => run('delay'));
$('stopRun').addEventListener('click', () => stopAudio());
for (const field of document.querySelectorAll('[data-connection]')) field.addEventListener('change', () => {
  if (field === inputs.inputChannel && inputs.inputChannel.value === inputs.referenceChannel.value) inputs.referenceChannel.value = inputs.inputChannel.value === '1' ? '2' : '1';
  if (field === inputs.referenceChannel && inputs.inputChannel.value === inputs.referenceChannel.value) inputs.inputChannel.value = inputs.referenceChannel.value === '1' ? '2' : '1';
  if (field === inputs.outputChannel && inputs.outputChannel.value === inputs.referenceOutputChannel.value) inputs.referenceOutputChannel.value = inputs.outputChannel.value === '1' ? '2' : '1';
  if (field === inputs.referenceOutputChannel && inputs.outputChannel.value === inputs.referenceOutputChannel.value) inputs.outputChannel.value = inputs.referenceOutputChannel.value === '1' ? '2' : '1';
  invalidateConnection();
});
inputs.peakDbfs.addEventListener('change', () => { state.calibration = null; emptyCalibration('Digital level changed. Run a new timing check.'); updateControls(); });
for (const field of document.querySelectorAll('input[name="sequenceLength"]')) field.addEventListener('change', updateControls);
for (const field of document.querySelectorAll('input[name="referenceMode"]')) field.addEventListener('change', () => { state.calibration = null; emptyCalibration('Timing method changed. Run a new timing check.'); updateMethod(); updateControls(); });
for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => setTab(button.dataset.tab));
document.querySelector('.brand').addEventListener('click', (event) => { event.preventDefault(); setTab('stimulus'); });
for (const [id, next] of [['tabStimulus', 'delay'], ['tabDelay', 'stimulus']]) $(id).addEventListener('keydown', (event) => { if (['ArrowLeft', 'ArrowRight'].includes(event.key)) { event.preventDefault(); setTab(next); $(next === 'delay' ? 'tabDelay' : 'tabStimulus').focus(); } });
window.addEventListener('hashchange', () => setTab(location.hash === '#delay' ? 'delay' : 'stimulus', false));
window.addEventListener('keydown', (event) => { if (event.key === 'Escape' && state.busy) { event.preventDefault(); stopAudio(); } });
document.addEventListener('visibilitychange', () => { if (document.hidden && (state.connected || state.busy)) stopAudio('Audio stopped because this tab was hidden. Connect again when ready.'); });
window.addEventListener('pagehide', () => { state.generation += 1; engine.disconnect(); });
navigator.mediaDevices?.addEventListener?.('devicechange', async () => { if (state.connected || state.busy) await invalidateConnection(); await refreshDevices(); });

if (!outputSelection) $('outputHelp').textContent = 'This browser uses the system output. Select your wired interface in macOS Sound or Windows Sound settings, then use the same interface as the microphone input.';
inputs.outputDevice.disabled = !outputSelection;
setTab(location.hash === '#delay' ? 'delay' : 'stimulus', false);
updateMethod();
onEngineStatus(engine.status());
refreshDevices();
if (!globalThis.isSecureContext || !navigator.mediaDevices?.getUserMedia) notice('Audio needs a secure HTTPS page and a browser with microphone access. Open the published HTTPS version in a current desktop browser.', true);
