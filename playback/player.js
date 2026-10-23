import { SAMPLE_RATE, E_FREQUENCIES, AUDIBLE_FREQUENCIES, sinePip, buildSequence, stereoSamples } from './waveform.mjs';

const $ = (id) => document.getElementById(id);
let context;
let source;
let poll;
let operation = 0;
const status = (message) => { $('status').textContent = message; };

function stop(message = 'Stopped.') {
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
  try {
    // Start/resume within the click gesture, then verify the OS route before scheduling sound.
    await Promise.all([initialize(), outputReady()]);
    if (operation !== token) return;
    const dbfs = Number($('level').value);
    const channel = $('channel').value;
    const frequencies = $('alphabet').value === 'full' ? E_FREQUENCIES : AUDIBLE_FREQUENCIES;
    const mono = kind === 'test' ? sinePip(1000, 0.5, dbfs) : buildSequence(frequencies, Number($('duration').value), dbfs);
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
    source.onended = () => { if (operation === token) stop('Finished.'); };
    source.start();
    status(`Playing ${kind === 'test' ? '1 kHz test' : 'synthetic pips'} · ${channel} · ${dbfs} dBFS · ${(mono.length / SAMPLE_RATE).toFixed(1)} s`);
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
$('stop').addEventListener('click', () => stop());
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
window.addEventListener('pagehide', () => { stop(); context?.close(); });
document.addEventListener('visibilitychange', () => { if (document.hidden) stop('Stopped because this page is hidden.'); });
outputReady().then(() => status('Mac output is ready. Check browser output, then start the 1 kHz test.')).catch((error) => status(error.message));
