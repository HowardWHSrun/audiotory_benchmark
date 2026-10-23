import { SAMPLE_RATE, E_FREQUENCIES, AUDIBLE_FREQUENCIES, sinePip, buildSequence, stereoSamples, logarithmicSweep } from './waveform.mjs';

const $ = (id) => document.getElementById(id);
let context;
let source;
let poll;
let operation = 0;
let micStream;
let micNodes = [];
let micFrame;
let micOperation = 0;
let micMeasurement;
const status = (message) => { $('status').textContent = message; };

function stop(message = 'Stopped.') {
  finishMeasurement('Playback stopped');
  operation++;
  clearInterval(poll);
  poll = undefined;
  if (source) {
    const old = source;
    source = undefined;
    old.onended = null;
    try { old.stop(); } catch {}
    old.disconnect();
  }
  $('test').disabled = false;
  $('sequence').disabled = false;
  $('sweep').disabled = false;
  status(message);
}

async function outputReady() {
  const response = await fetch('/api/output', { cache: 'no-store', signal: AbortSignal.timeout(1800) });
  if (!response.ok) throw new Error('Cannot read Mac output. Restart the local launcher.');
  const output = await response.json();
  $('output').textContent = output.name ? `${output.name} · ${Number(output.sample_rate).toLocaleString()} Hz` : 'Mac output unavailable';
  if (output.ready !== true || !/audient/i.test(output.name ?? '') || Math.abs(Number(output.sample_rate) - SAMPLE_RATE) >= 1) {
    throw new Error('Playback blocked: select Audient as Mac output at 96 kHz using the launcher.');
  }
  return output;
}

async function initialize() {
  // Called only from an explicit click; an empty context produces no signal.
  if (!context || context.state === 'closed') {
    context = new AudioContext({ sampleRate: SAMPLE_RATE, latencyHint: 'interactive' });
    context.addEventListener('statechange', () => {
      if (source && context.state !== 'running') stop('Playback stopped: browser audio was interrupted.');
    });
  }
  await context.resume();
  $('context').textContent = `Browser audio: ${context.sampleRate.toLocaleString()} Hz · ${context.state}. Physical mixer route is unverified.`;
  if (context.sampleRate !== SAMPLE_RATE) throw new Error('Playback blocked: browser audio is not running at 96 kHz. Close this page and reopen after configuring Audient.');
  if (context.state !== 'running') throw new Error('Browser audio could not start. Click Check output again.');
}

async function play(kind) {
  stop('Checking output…');
  const token = operation;
  $('test').disabled = true;
  $('sequence').disabled = true;
  $('sweep').disabled = true;
  try {
    // Start/resume within the click gesture, then verify the OS route before scheduling sound.
    await Promise.all([initialize(), outputReady()]);
    if (operation !== token) return;
    const dbfs = Number($('level').value);
    const channel = $('channel').value;
    const frequencies = $('alphabet').value === 'full' ? E_FREQUENCIES : AUDIBLE_FREQUENCIES;
    const mono = kind === 'test' ? sinePip(1000, 0.5, dbfs) : kind === 'sweep' ? logarithmicSweep(dbfs) : buildSequence(frequencies, Number($('duration').value), dbfs);
    const buffer = context.createBuffer(2, mono.length, SAMPLE_RATE);
    stereoSamples(mono, channel).forEach((samples, index) => buffer.copyToChannel(samples, index));
    // Recheck immediately before start, after waveform construction.
    await outputReady();
    if (operation !== token) return;
    source = context.createBufferSource();
    source.buffer = buffer;
    source.channelCount = 2;
    source.channelCountMode = 'explicit';
    source.connect(context.destination);
    source.onended = () => { if (operation === token) { finishMeasurement('Playback finished'); stop('Finished.'); } };
    source.start();
    if (micStream) micMeasurement = { started: performance.now(), kind, peak: [0, 0], energy: [0, 0], maxRms: [0, 0], frequencyAtMax: [null, null], count: 0, frames: 0 };
    status(`Playing ${kind === 'test' ? '1 kHz test' : kind === 'sweep' ? '100 Hz–20 kHz sweep' : 'synthetic pips'} · ${channel} · ${dbfs} dBFS · ${(mono.length / SAMPLE_RATE).toFixed(1)} s`);
    let checking = false;
    poll = setInterval(async () => {
      if (checking || operation !== token) return;
      checking = true;
      try { await outputReady(); } catch (error) { if (operation === token) stop(error.message); }
      finally { checking = false; }
    }, 500);
  } catch (error) {
    if (operation === token) stop(error.message || 'Audio could not start.');
  }
}

$('test').addEventListener('click', () => play('test'));
$('sequence').addEventListener('click', () => play('sequence'));
$('sweep').addEventListener('click', () => play('sweep'));
$('stop').addEventListener('click', () => { finishMeasurement('Stopped early'); stop(); stopMicrophone(); });
$('check').addEventListener('click', async () => {
  stop('Checking output without a signal…');
  const token = operation;
  try {
    await Promise.all([initialize(), outputReady()]);
    if (operation === token) status('Output check passed. Start with the 1 kHz test at a low hardware volume.');
  } catch (error) { if (operation === token) status(error.message); }
});
$('level').addEventListener('input', () => { $('level-text').textContent = `${$('level').value.replace('-', '−')} dBFS`; });
for (const id of ['level', 'channel', 'alphabet', 'duration']) $(id).addEventListener('change', () => { if (source) stop('Stopped after a control changed. Press Play to use the new settings.'); });
$('alphabet').addEventListener('change', () => {
  const list = $('alphabet').value === 'full' ? E_FREQUENCIES : AUDIBLE_FREQUENCIES;
  $('frequencies').textContent = `${list.map((f) => f / 1000).join(', ')} kHz · ascending, repeating · 10 ms per pip`;
});
function db(value) { return value > 0 ? `${Math.max(-120, 20 * Math.log10(value)).toFixed(1)} dBFS` : '−∞ dBFS'; }

function finishMeasurement(label) {
  if (!micMeasurement) return;
  const m = micMeasurement;
  micMeasurement = undefined;
  if (!m.count) { $('mic-summary').textContent = `${label}: no input samples observed.`; return; }
  const elapsed = (performance.now() - m.started) / 1000;
  $('mic-summary').textContent = `${label} (${m.kind}) · ${elapsed.toFixed(2)} s · ${m.frames} observed analyser frames. ${m.peak.map((peak, i) => `Input ${i + 1}: peak ${db(peak)}, observed RMS ${db(Math.sqrt(m.energy[i] / m.count))}, max RMS ${db(m.maxRms[i])}, dominant frequency at max ${m.frequencyAtMax[i] ? `${Math.round(m.frequencyAtMax[i])} Hz` : 'unavailable'}${peak >= 0.99 ? ' · possible clipping' : ''}`).join(' | ')}. Uncalibrated digital levels; FFT peaks can include ambient sound and harmonics. No SPL or frequency-response inference.`;
}

function stopMicrophone() {
  micOperation++;
  cancelAnimationFrame(micFrame);
  finishMeasurement('Microphone stopped');
  micStream?.getTracks().forEach((track) => track.stop());
  micStream = undefined;
  micNodes.forEach((node) => { try { node.disconnect(); } catch {} });
  micNodes = [];
  $('mic-start').disabled = false;
  $('mic-status').textContent = 'Microphone off; input tracks released.';
}

async function startMicrophone() {
  stopMicrophone();
  const token = micOperation;
  $('mic-start').disabled = true;
  $('mic-status').textContent = 'Requesting microphone access…';
  let acquired;
  const constraints = { sampleRate: { ideal: SAMPLE_RATE }, channelCount: { ideal: 2 }, echoCancellation: false, noiseSuppression: false, autoGainControl: false };
  try {
    if (!navigator.mediaDevices?.getUserMedia) throw new Error('Microphone capture requires this localhost page and browser permission.');
    await initialize();
    // Permission reveals device labels. Release the provisional input before selecting Audient exactly.
    acquired = await navigator.mediaDevices.getUserMedia({ audio: constraints });
    const devices = await navigator.mediaDevices.enumerateDevices();
    const audient = devices.find((device) => device.kind === 'audioinput' && !['default', 'communications'].includes(device.deviceId) && /audient/i.test(device.label));
    acquired.getTracks().forEach((track) => track.stop());
    acquired = undefined;
    if (token !== micOperation) return;
    if (!audient) throw new Error('No named Audient input found. Check its USB connection and browser microphone permissions.');
    acquired = await navigator.mediaDevices.getUserMedia({ audio: { ...constraints, deviceId: { exact: audient.deviceId } } });
    if (token !== micOperation) { acquired.getTracks().forEach((track) => track.stop()); return; }
    micStream = acquired;
    const track = micStream.getAudioTracks()[0];
    const settings = track.getSettings();
    if (!/audient/i.test(track.label)) throw new Error('The selected microphone is not labelled Audient; capture stopped.');
    $('mic-settings').textContent = `${track.label} · input ${settings.sampleRate ?? 'unknown'} Hz · ${settings.channelCount ?? 'unknown'} channels · browser analysis ${context.sampleRate} Hz. Echo cancellation ${settings.echoCancellation ?? 'unknown'}, noise suppression ${settings.noiseSuppression ?? 'unknown'}, automatic gain ${settings.autoGainControl ?? 'unknown'}.`;
    const input = context.createMediaStreamSource(micStream);
    const splitter = context.createChannelSplitter(2);
    const mute = context.createGain();
    mute.gain.value = 0;
    input.connect(splitter);
    mute.connect(context.destination);
    const analysers = [context.createAnalyser(), context.createAnalyser()];
    analysers.forEach((analyser, i) => { analyser.fftSize = 8192; analyser.smoothingTimeConstant = 0; splitter.connect(analyser, i); analyser.connect(mute); });
    micNodes = [input, splitter, mute, ...analysers];
    const samples = analysers.map((analyser) => new Float32Array(analyser.fftSize));
    const spectra = analysers.map((analyser) => new Float32Array(analyser.frequencyBinCount));
    const held = [{ peak: 0, rms: 0 }, { peak: 0, rms: 0 }];
    let lastUpdate = 0;
    const update = (now) => {
      if (token !== micOperation) return;
      if (now - lastUpdate >= 50) {
        lastUpdate = now;
        const lines = analysers.map((analyser, i) => {
          analyser.getFloatTimeDomainData(samples[i]);
          let peak = 0; let energy = 0;
          for (const value of samples[i]) { peak = Math.max(peak, Math.abs(value)); energy += value * value; }
          const rms = Math.sqrt(energy / samples[i].length);
          analyser.getFloatFrequencyData(spectra[i]);
          const binHz = context.sampleRate / analyser.fftSize;
          let maxBin = -1; let maxDb = -Infinity;
          for (let bin = Math.ceil(100 / binHz); bin <= Math.floor(20000 / binHz); bin++) if (spectra[i][bin] > maxDb) { maxDb = spectra[i][bin]; maxBin = bin; }
          const dominant = maxDb > -120 ? maxBin * binHz : null;
          held[i].peak = Math.max(held[i].peak, peak); held[i].rms = Math.max(held[i].rms, rms);
          if (micMeasurement) {
            micMeasurement.peak[i] = Math.max(micMeasurement.peak[i], peak); micMeasurement.energy[i] += energy;
            if (rms > micMeasurement.maxRms[i]) { micMeasurement.maxRms[i] = rms; micMeasurement.frequencyAtMax[i] = dominant; }
          }
          return `Input ${i + 1}: peak ${db(peak)} · RMS ${db(rms)}\n  Dominant FFT: ${dominant ? `${Math.round(dominant)} Hz` : '—'} · held peak ${db(held[i].peak)}, RMS ${db(held[i].rms)}${peak >= 0.99 ? ' · possible clipping' : ''}`;
        });
        if (micMeasurement) { micMeasurement.count += samples[0].length; micMeasurement.frames++; }
        $('mic-meter').textContent = lines.join('\n');
      }
      micFrame = requestAnimationFrame(update);
    };
    micFrame = requestAnimationFrame(update);
    track.addEventListener('ended', () => { if (token === micOperation) stopMicrophone(); });
    $('mic-status').textContent = 'Audient input active · silent metering. Play the sweep to collect a level summary.';
  } catch (error) {
    acquired?.getTracks().forEach((track) => track.stop());
    if (token === micOperation) { stopMicrophone(); $('mic-status').textContent = error.message; }
  }
}
$('mic-start').addEventListener('click', startMicrophone);
$('mic-stop').addEventListener('click', stopMicrophone);
window.addEventListener('pagehide', () => { stop(); stopMicrophone(); context?.close(); });
document.addEventListener('visibilitychange', () => { if (document.hidden) { finishMeasurement('Page hidden'); stop('Stopped because this page is hidden.'); stopMicrophone(); } });
outputReady().then(() => status('Mac output is ready. Check browser output, then start the 1 kHz test.')).catch((error) => status(error.message));
