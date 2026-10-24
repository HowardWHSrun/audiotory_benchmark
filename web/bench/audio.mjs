/** Pure-browser SONIC reconstruction and conservative waveform-delay screening.
 * Importing this module never requests permission, opens audio, or plays sound.
 * The waveform specification follows latency/stimulus.py. Browser PRNG/order is
 * deliberately declared separately from its NumPy PCG64 reconstruction. */
export const E14_FREQUENCIES = Object.freeze([2000, 4000, 6000, 8000, 9000, 10500, 17000, 18200, 19500, 20900, 22400, 24000, 25800, 27000]);
export const PAPER_SOURCE = Object.freeze({title: 'SONIC: A Benchmarking Paradigm for Brain-Computer Interfaces', version: 'bioRxiv v1, posted 2025-10-02', url: 'https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1', methods: 'Sections 6.1–6.2, printed page 11'});
export const LIMITATIONS = Object.freeze([
  'Browser screening estimate only; physical audio timing and hardware performance are unverified.',
  'Generated sample coordinates are not physical DAC/ADC timestamps or Play-button timing.',
  'The browser may buffer, resample or hide hardware overruns; worklet/chunk checks cannot detect all driver or hardware xruns.',
  'Selecting devices does not prove a shared hardware clock. Use the same wired interface and keep input monitoring off.',
  'Digital dBFS is not acoustic SPL. This app does not calibrate sound level or establish an animal-ready protocol.',
  'No original SONIC waveform/order was available; the E14 stimulus is a documented local reconstruction.',
]);
const own = (obj, key) => Object.prototype.hasOwnProperty.call(obj, key);
const finite = (value) => typeof value === 'number' && Number.isFinite(value);
function integer(value, name, lo, hi) { if (!Number.isInteger(value) || value < lo || value > hi) throw new Error(`${name} must be an integer from ${lo} to ${hi}.`); return value; }
function amplitude(peakDbfs) { if (!finite(peakDbfs) || peakDbfs < -60 || peakDbfs > -18) throw new Error('Digital peak must be between −60 and −18 dBFS.'); return 10 ** (peakDbfs / 20); }
function rateCheck(sampleRate, e14 = false) { if (!finite(sampleRate) || sampleRate < 44100 || sampleRate > 192000) throw new Error('Unsupported browser sample rate.'); if (e14 && sampleRate < 96000) throw new Error('The full E14 list reaches 27 kHz and requires an actual browser audio rate of at least 96 kHz. This browser is running at ' + sampleRate.toLocaleString() + ' Hz; E14 playback is blocked.'); }
export function raisedCosineEnvelope(samples, rampSamples) {
  integer(samples, 'Samples', 4, 192000); integer(rampSamples, 'Ramp samples', 2, Math.floor(samples / 2));
  const envelope = new Float32Array(samples); envelope.fill(1);
  for (let i = 0; i < rampSamples; i++) { const v = .5 * (1 - Math.cos(Math.PI * i / (rampSamples - 1))); envelope[i] = v; envelope[samples - 1 - i] = v; }
  return envelope;
}
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export function makeSonicBlock({sampleRate = 96000, tonesPerFrequency = 600, seed = 20261023, peakDbfs = -36} = {}) {
  rateCheck(sampleRate, true); integer(tonesPerFrequency, 'Pips per frequency', 1, 1000); integer(seed, 'Seed', 0, 4294967295);
  // Rates that cannot represent exact 10-ms/2-ms sample lengths are refused.
  if (sampleRate % 500 !== 0) throw new Error('This context rate cannot represent exact 10 ms pips and 2 ms ramps.');
  const peak = amplitude(peakDbfs), pipSamples = sampleRate / 100, rampSamples = sampleRate / 500;
  const envelope = raisedCosineEnvelope(pipSamples, rampSamples);
  const sequence = E14_FREQUENCIES.flatMap((frequency) => Array(tonesPerFrequency).fill(frequency));
  const random = mulberry32(seed);
  for (let i = sequence.length - 1; i > 0; i--) { const j = Math.floor(random() * (i + 1)); [sequence[i], sequence[j]] = [sequence[j], sequence[i]]; }
  const padding = sampleRate;
  const waveform = new Float32Array(sequence.length * pipSamples + 2 * padding);
  const bank = new Map(E14_FREQUENCIES.map((frequency) => {
    const pip = new Float32Array(pipSamples);
    for (let n = 0; n < pipSamples; n++) pip[n] = peak * Math.sin(2 * Math.PI * frequency * n / sampleRate) * envelope[n];
    return [frequency, pip];
  }));
  const events = sequence.map((frequency, trial) => { const start = padding + trial * pipSamples; waveform.set(bank.get(frequency), start); return {trial, frequency_hz: frequency, output_start: start, output_stop: start + pipSamples}; });
  return {waveform, metadata: {
    schema_version: 1, kind: 'sonic_e14_reconstruction', exact_original_waveform: false,
    paper_source: PAPER_SOURCE, sample_rate_hz: sampleRate, sample_count: waveform.length,
    duration_seconds: waveform.length / sampleRate, active_duration_seconds: sequence.length / 100,
    published_frequency_list_hz: [...E14_FREQUENCIES], tone_count: sequence.length,
    tones_per_frequency: tonesPerFrequency, seed, digital_peak_limit_dbfs: peakDbfs,
    tone_duration_seconds: .01, tone_duration_samples: pipSamples, ramp_seconds_each_end: .002,
    ramp_samples_each_end: rampSamples, ramp_shape: 'raised cosine, endpoints inclusive; local choice',
    phase_convention: 'zero-phase sine independently for every pip', inter_tone_silence_samples: 0,
    leading_silence_samples: padding, trailing_silence_samples: padding,
    sequence_rule: 'exactly equal frequency counts, Mulberry32(seed) and descending Fisher–Yates shuffle',
    random_bit_generator: 'Mulberry32; differs from native NumPy PCG64 and from unavailable original SONIC order',
    within_published_block_tone_count_range: sequence.length >= 8000 && sequence.length <= 15000,
    original_details_unknown: ['original waveform/order/seed', 'digital level and normalization', 'ramp shape', 'exact per-block counts'],
    local_choices: ['balanced seeded sequence', 'declared digital peak', 'raised-cosine ramps', 'one second of silence before and after one block'],
    sample_index_convention: 'zero-based generated output_start inclusive/output_stop exclusive; not physical onset',
    events, limitations: [...LIMITATIONS],
  }};
}
export function makeProbePlan({sampleRate = 96000, repetitions = 10, peakDbfs = -36} = {}) {
  rateCheck(sampleRate); integer(repetitions, 'Repetitions', 3, 20);
  const peak = amplitude(peakDbfs), probeSamples = Math.round(sampleRate * .1), rampSamples = Math.round(sampleRate * .02), spacingSamples = Math.round(sampleRate * .5), padSamples = Math.round(sampleRate);
  const envelope = raisedCosineEnvelope(probeSamples, rampSamples), probe = new Float32Array(probeSamples);
  const sweepRate = Math.log(20000 / 100) / (probeSamples / sampleRate);
  for (let n = 0; n < probeSamples; n++) probe[n] = peak * Math.sin(2 * Math.PI * 100 * Math.expm1(sweepRate * n / sampleRate) / sweepRate) * envelope[n];
  const waveform = new Float32Array(2 * padSamples + (repetitions - 1) * spacingSamples + probeSamples);
  const trials = Array.from({length: repetitions}, (_, trial) => { const start = padSamples + trial * spacingSamples; waveform.set(probe, start); return {trial, output_start: start, output_stop: start + probeSamples}; });
  return {waveform, metadata: {schema_version: 1, kind: 'timing_probe', sonic_stimulus: false,
    purpose: 'Locally specified timing probe, distinct from SONIC pips', sample_rate_hz: sampleRate,
    sample_count: waveform.length, duration_seconds: waveform.length / sampleRate,
    repetitions, digital_peak_limit_dbfs: peakDbfs, probe_duration_seconds: .1,
    ramp_seconds_each_end: .02, ramp_shape: 'raised cosine with inclusive zero endpoints',
    frequency_start_hz: 100, frequency_end_hz: 20000, sweep: 'logarithmic, zero-phase sine',
    onset_spacing_seconds: .5, leading_silence_samples: padSamples, trailing_silence_samples: padSamples,
    trials, limitations: [...LIMITATIONS],
  }};
}

// Radix-2 FFT for exact full-band correlation. No decimation aliases 20-kHz probes.
function fft(real, imag, inverse = false) {
  const n = real.length;
  for (let i = 1, j = 0; i < n; i++) { let bit = n >> 1; for (; j & bit; bit >>= 1) j ^= bit; j ^= bit; if (i < j) { [real[i], real[j]] = [real[j], real[i]]; [imag[i], imag[j]] = [imag[j], imag[i]]; } }
  for (let length = 2; length <= n; length *= 2) {
    const angle = (inverse ? 2 : -2) * Math.PI / length, wr = Math.cos(angle), wi = Math.sin(angle);
    for (let start = 0; start < n; start += length) { let r = 1, im = 0;
      for (let j = 0; j < length / 2; j++) { const a = start + j, b = a + length / 2;
        const br = real[b] * r - imag[b] * im, bi = real[b] * im + imag[b] * r;
        real[b] = real[a] - br; imag[b] = imag[a] - bi; real[a] += br; imag[a] += bi;
        const next = r * wr - im * wi; im = r * wi + im * wr; r = next;
      }
    }
  }
  if (inverse) for (let i = 0; i < n; i++) { real[i] /= n; imag[i] /= n; }
}
export function normalizedCorrelations(reference, signal) {
  if (reference.length < 16 || signal.length < reference.length) throw new Error('Correlation windows are too short.');
  const n = reference.length, count = signal.length - n + 1;
  let size = 1; while (size < n + signal.length - 1) size *= 2;
  const a = new Float64Array(size), ai = new Float64Array(size), b = new Float64Array(size), bi = new Float64Array(size);
  let mean = 0; for (const x of reference) { if (!finite(x)) throw new Error('Non-finite reference.'); mean += x; } mean /= n;
  let referenceEnergy = 0;
  for (let i = 0; i < n; i++) { const centered = reference[i] - mean; b[n - 1 - i] = centered; referenceEnergy += centered * centered; }
  for (let i = 0; i < signal.length; i++) { if (!finite(signal[i])) throw new Error('Non-finite recording.'); a[i] = signal[i]; }
  fft(a, ai); fft(b, bi);
  for (let i = 0; i < size; i++) { const re = a[i] * b[i] - ai[i] * bi[i]; ai[i] = a[i] * bi[i] + ai[i] * b[i]; a[i] = re; }
  fft(a, ai, true);
  let sum = 0, squares = 0;
  for (let i = 0; i < n; i++) { sum += signal[i]; squares += signal[i] ** 2; }
  const result = new Float64Array(count);
  for (let lag = 0; lag < count; lag++) {
    const energy = Math.max(0, squares - sum * sum / n), denominator = Math.sqrt(energy * referenceEnergy);
    result[lag] = denominator > 1e-20 ? Math.max(-1, Math.min(1, a[n - 1 + lag] / denominator)) : 0;
    if (lag + n < signal.length) { const old = signal[lag], next = signal[lag + n]; sum += next - old; squares += next * next - old * old; }
  }
  return result;
}
function rms(values) { if (!values.length) return 0; let sum = 0, squares = 0; for (const x of values) { sum += x; squares += x*x; } return Math.sqrt(Math.max(0, squares / values.length - (sum / values.length) ** 2)); }
function clipped(values) { let count = 0; for (const x of values) if (Math.abs(x) >= .999) count++; return count; }
export function analyzeLag(reference, signal, sampleRate, {maxLagMs = 250, minRms = 1e-6, minCorrelation = .35, ambiguityRatio = .95} = {}) {
  if (!finite(sampleRate) || sampleRate <= 0 || !finite(maxLagMs) || maxLagMs <= 0 || maxLagMs > 1000) throw new Error('Invalid correlation sample rate or lag bound.');
  const maxLag = Math.floor(sampleRate * maxLagMs / 1000), reasons = [];
  const used = signal.subarray(0, reference.length + maxLag);
  const result = {accepted: false, delay_samples: null, delay_ms: null, candidate_delay_samples: null, candidate_delay_ms: null, peak_correlation: null, peak_correlation_abs: null, secondary_peak_ratio: null, reasons,
    reference_rms_fs: rms(reference), microphone_rms_fs: rms(used), reference_clipped_samples: clipped(reference), microphone_clipped_samples: clipped(used)};
  if (reference.length < 16 || used.length < reference.length + maxLag) reasons.push('incomplete_search_window');
  if (result.reference_rms_fs < minRms) reasons.push('reference_missing_or_too_quiet');
  if (result.microphone_rms_fs < minRms) reasons.push('microphone_missing_or_too_quiet');
  if (result.reference_clipped_samples) reasons.push('reference_clipping');
  if (result.microphone_clipped_samples) reasons.push('microphone_clipping');
  if (result.reference_rms_fs < minRms || result.microphone_rms_fs < minRms || reference.length < 16 || used.length < reference.length) return result;
  const correlations = normalizedCorrelations(reference, used);
  let peak = 0; for (let i = 1; i < correlations.length; i++) if (Math.abs(correlations[i]) > Math.abs(correlations[peak])) peak = i;
  const sign = Math.sign(correlations[peak]); let left = peak, right = peak + 1;
  while (left > 0 && correlations[left - 1] * sign > 0) left--;
  while (right < correlations.length && correlations[right] * sign > 0) right++;
  const exclusionStart = Math.min(left, Math.max(0, peak - 3)), exclusionStop = Math.max(right, Math.min(correlations.length, peak + 4));
  let secondary = 0; for (let i = 0; i < correlations.length; i++) if (i < exclusionStart || i >= exclusionStop) secondary = Math.max(secondary, Math.abs(correlations[i]));
  const magnitude = Math.abs(correlations[peak]), ratio = magnitude ? secondary / magnitude : 1;
  Object.assign(result, {candidate_delay_samples: peak, candidate_delay_ms: peak * 1000 / sampleRate, peak_correlation: correlations[peak], peak_correlation_abs: magnitude, secondary_peak_ratio: ratio,
    primary_lobe_start_lag_samples: left, primary_lobe_stop_lag_samples_exclusive: right,
    primary_lobe_width_samples: right - left, primary_lobe_bounded_by_zero_crossings: left > 0 && right < correlations.length,
    peak_at_search_boundary: peak === 0 || peak === correlations.length - 1});
  if (magnitude < minCorrelation) reasons.push('weak_correlation');
  if (ratio >= ambiguityRatio) reasons.push('ambiguous_peak');
  if (left === 0 || right === correlations.length) reasons.push('primary_lobe_unresolved_at_search_boundary');
  if (result.peak_at_search_boundary) reasons.push('boundary_peak_unresolved');
  if (!reasons.length) Object.assign(result, {accepted: true, delay_samples: peak, delay_ms: result.candidate_delay_ms});
  return result;
}
function quantile(sorted, q) { const position = (sorted.length - 1) * q, left = Math.floor(position), right = Math.ceil(position); return sorted[left] + (sorted[right] - sorted[left]) * (position - left); }
function summarize(trials) {
  const values = trials.filter(t => t.accepted).map(t => t.delay_ms).sort((a,b) => a-b);
  const result = {total_trials: trials.length, accepted_trials: values.length, rejected_trials: trials.length - values.length, median_delay_ms: null, p05_delay_ms: null, p95_delay_ms: null, jitter_p95_minus_p05_ms: null, min_delay_ms: null, max_delay_ms: null};
  if (values.length) Object.assign(result, {median_delay_ms: quantile(values, .5), p05_delay_ms: quantile(values, .05), p95_delay_ms: quantile(values, .95), jitter_p95_minus_p05_ms: quantile(values, .95) - quantile(values, .05), min_delay_ms: values[0], max_delay_ms: values.at(-1)});
  return result;
}
export function assessCaptureChunks(chunks, expectedFrames, firstFrame, done = {}) {
  const errors = [];
  if (!Number.isInteger(firstFrame) || firstFrame < 0) errors.push('worklet_first_frame_invalid');
  const channels = {microphone: new Float32Array(expectedFrames), reference: null};
  let offset = 0, referenceChunks = 0;
  chunks.forEach((chunk, index) => {
    if (chunk.index !== index) errors.push('capture_chunk_sequence_mismatch');
    if (chunk.start !== offset || chunk.frame !== firstFrame + offset) errors.push('capture_frame_gap_or_overlap');
    if (!Number.isInteger(chunk.count) || chunk.count < 1 || chunk.count > 4096 || chunk.start < 0 || chunk.start + chunk.count > expectedFrames) { errors.push('capture_chunk_bounds_invalid'); return; }
    const microphone = new Float32Array(chunk.microphone);
    if (microphone.length !== chunk.count) errors.push('capture_chunk_length_mismatch');
    else channels.microphone.set(microphone, chunk.start);
    if (chunk.reference !== null && chunk.reference !== undefined) {
      referenceChunks++;
      if (!channels.reference) channels.reference = new Float32Array(expectedFrames);
      const reference = new Float32Array(chunk.reference);
      if (reference.length !== chunk.count) errors.push('reference_chunk_length_mismatch'); else channels.reference.set(reference, chunk.start);
    }
    offset = chunk.start + chunk.count;
  });
  if (referenceChunks && referenceChunks !== chunks.length) errors.push('reference_chunk_missing');
  if (offset !== expectedFrames || done.frames !== expectedFrames) errors.push('capture_incomplete');
  if (done.chunks !== chunks.length) errors.push('capture_chunk_count_mismatch');
  if (done.processGaps) errors.push('worklet_process_frame_gap');
  if (done.inputMissingFrames) errors.push('input_channels_missing');
  if (done.endFrame !== firstFrame + expectedFrames) errors.push('worklet_end_frame_mismatch');
  return {...channels, valid: errors.length === 0, errors: [...new Set(errors)], captured_frames: offset,
    worklet_first_frame: firstFrame, worklet_end_frame: done.endFrame, input_channel_minimum: done.inputChannelMin,
    limitation: 'No observed worklet/chunk gaps does not prove absence of hidden browser, hardware or driver xruns.'};
}
export function analyzeCapture({source, microphone, reference = null, sampleRate, stimulus, transport, processingVerified = false, inputChannels = 0, requireReference = false}) {
  if (!(source instanceof Float32Array) || !(microphone instanceof Float32Array) || source.length !== microphone.length) throw new Error('Capture and source arrays must have matching lengths.');
  if (reference && reference.length !== source.length) throw new Error('Electrical reference length differs from source.');
  const transportErrors = [...(transport?.errors || [])];
  if (transport?.valid !== true) transportErrors.push('capture_integrity_invalid_or_unverified');
  if (!processingVerified) transportErrors.push('browser_input_processing_not_verified_off');
  if (requireReference && (!reference || inputChannels < 2 || transport?.input_channel_minimum < 2)) transportErrors.push('two_distinct_input_channels_not_exposed');
  const trials = stimulus.trials.map((trial) => {
    const start = trial.output_start, stop = trial.output_stop, probe = source.subarray(start, stop);
    if (!requireReference) return {...trial, ...analyzeLag(probe, microphone.subarray(start, Math.min(microphone.length, stop + Math.floor(sampleRate * .25))), sampleRate)};
    // Source coordinates alone are not ADC coordinates. Locate the actual input-2
    // probe first, then compare that recorded reference to the microphone.
    if (!reference) return {...trial, accepted: false, delay_ms: null, delay_samples: null, candidate_delay_ms: null, reasons: ['electrical_reference_unavailable']};
    const located = analyzeLag(probe, reference.subarray(start, Math.min(reference.length, stop + Math.floor(sampleRate * .25))), sampleRate);
    if (!located.accepted) return {...trial, accepted: false, delay_ms: null, delay_samples: null, candidate_delay_ms: null, reasons: ['electrical_reference_probe_not_located', ...located.reasons], reference_alignment: located};
    const adcStart = start + located.delay_samples, adcStop = adcStart + probe.length;
    return {...trial, ...analyzeLag(reference.subarray(adcStart, adcStop), microphone.subarray(adcStart, Math.min(microphone.length, adcStop + Math.floor(sampleRate * .25))), sampleRate), reference_alignment: located, recorded_reference_start_sample: adcStart};
  });
  const candidateSummary = summarize(trials), minimumAccepted = Math.max(3, Math.ceil(trials.length * .8));
  const transportValid = transportErrors.length === 0;
  // Fixed 500-ms repeats could alias an out-of-range delay onto a later
  // trial. The first trial has no preceding probe: require it as an anchor.
  const firstProbeAccepted = trials[0]?.accepted === true;
  const signalEnough = candidateSummary.accepted_trials >= minimumAccepted && firstProbeAccepted;
  const usable = transportValid && signalEnough;
  // A rejected run must not leave a normal-looking qualified delay on screen.
  if (!usable) for (const trial of trials) { trial.waveform_quality_accepted = trial.accepted; trial.accepted = false; trial.delay_ms = trial.delay_samples = null; if (!transportValid) trial.reasons.push('transport_or_processing_unverified'); }
  return {schema_version: 1, kind: 'browser_delay_screen', method: requireReference ? 'recorded_input_2_to_microphone_waveform_alignment' : 'browser_worklet_generated_source_to_microphone_roundtrip',
    status: usable ? 'screening_pass' : (signalEnough ? 'diagnostic_only' : 'insufficient_signal'), usable_measurement: usable, usable,
    sample_rate_hz: sampleRate, sample_interval_ms: 1000 / sampleRate, search_lag_ms: [0,250],
    minimum_accepted_trials: minimumAccepted, minimum_accepted_fraction: .8, first_probe_anchor_required:true, first_probe_anchor_accepted:firstProbeAccepted, screen_rejection_reasons: firstProbeAccepted ? [] : ['first_probe_not_accepted_out_of_range_repeat_alias_cannot_be_excluded'], trials,
    summary: summarize(trials), diagnostic_candidate_summary: candidateSummary,
    transport: {...transport, valid: transportValid, errors: [...new Set(transportErrors)]},
    interpretation: requireReference ? 'Waveform alignment from a recorded electrical reference to microphone on browser-exposed input channels. Includes loudspeaker/acoustic/microphone path relative to the reference. A shared ADC clock must be established separately; host output latency is common and excluded.' : 'Browser generated-output sample grid to microphone waveform roundtrip. Includes browser output/input buffering, conversion, loudspeaker, acoustic travel and microphone path; not isolated speaker-to-microphone acoustic latency.',
    limitations: [...LIMITATIONS, 'Integer-sample correlation increments do not establish measurement accuracy or physical acoustic onset.', 'Signal thresholds are local screening choices, not hardware qualification.'],
    thresholds: {minimum_rms_fs: 1e-6, minimum_peak_correlation: .35, maximum_secondary_peak_ratio: .95, clipping_level_fs: .999, ambiguity_exclusion: 'same-sign primary lobe between zero crossings, minimum ±3 samples'},
  };
}
export function wavBlob(channels, sampleRate) {
  if (!Array.isArray(channels) || !channels.length || channels.some(c => c.length !== channels[0].length)) throw new Error('WAV channels must be equal length.');
  const frames = channels[0].length, bytes = frames * channels.length * 4, buffer = new ArrayBuffer(44 + bytes), view = new DataView(buffer);
  const write = (offset, text) => [...text].forEach((ch, i) => view.setUint8(offset + i, ch.charCodeAt(0)));
  write(0, 'RIFF'); view.setUint32(4, 36 + bytes, true); write(8, 'WAVE'); write(12, 'fmt '); view.setUint32(16,16,true); view.setUint16(20,3,true); view.setUint16(22,channels.length,true); view.setUint32(24,sampleRate,true); view.setUint32(28,sampleRate * channels.length * 4,true); view.setUint16(32,channels.length * 4,true); view.setUint16(34,32,true); write(36,'data'); view.setUint32(40,bytes,true);
  for (let n = 0, offset = 44; n < frames; n++) for (const channel of channels) { view.setFloat32(offset,channel[n],true); offset += 4; }
  return new Blob([buffer], {type:'audio/wav'});
}
async function sha256(samples) { if (!globalThis.crypto?.subtle) return null; const digest = await crypto.subtle.digest('SHA-256', samples); return [...new Uint8Array(digest)].map(v => v.toString(16).padStart(2,'0')).join(''); }
function aborted() { const error = new Error('Stopped. Audio devices released.'); error.name = 'AbortError'; return error; }

export class BrowserBench {
  constructor({onStatus = () => {}} = {}) {
    this.onStatus = onStatus; this.phase = 'idle'; this.message = 'Connect your audio interface to begin.';
    this.progress = 0; this.connection = null; this.warnings = []; this.context = null;
    this.stream = null; this.node = null; this.sourceNode = null; this._epoch = 0; this._id = 0;
    this._pending = null; this.lastResult = null; this.lastCaptureWav = null; this.lastSourceWav = null;
    this._visibility = () => { if (globalThis.document?.hidden && this.context) this.stop('Page hidden. Audio stopped and devices released.'); };
    globalThis.document?.addEventListener('visibilitychange', this._visibility);
  }
  get capabilities() {
    const Audio = globalThis.AudioContext || globalThis.webkitAudioContext;
    return {secureContext: globalThis.isSecureContext === true, audioWorklet: Boolean(Audio && globalThis.AudioWorkletNode), mediaDevices: Boolean(globalThis.navigator?.mediaDevices?.getUserMedia), outputSelection: Boolean(Audio?.prototype?.setSinkId)};
  }
  status() { return {phase: this.phase, message: this.message, progress: this.progress, connected: Boolean(this.context && this.connection), capabilities: this.capabilities, connection: this.connection, warnings: [...this.warnings]}; }
  _notify(phase, message, progress = this.progress) { this.phase = phase; this.message = message; this.progress = progress; try { this.onStatus(this.status()); } catch (_) { /* UI callbacks cannot interrupt device cleanup. */ } }
  async devices() {
    if (!globalThis.navigator?.mediaDevices?.enumerateDevices) return [];
    return (await navigator.mediaDevices.enumerateDevices()).filter(d => d.kind === 'audioinput' || d.kind === 'audiooutput').map(d => ({deviceId: d.deviceId, groupId: d.groupId, kind: d.kind, label: d.label || (d.kind === 'audioinput' ? 'Microphone (connect to reveal name)' : 'Output (connect to reveal name)')}));
  }
  _dispose() {
    if (this._connectReject) { this._connectReject(aborted()); this._connectReject = null; }
    if (this.node) { try { this.node.port.postMessage({type:'stop'}); this.node.disconnect(); this.node.port.close(); } catch (_) {} }
    if (this.sourceNode) { try { this.sourceNode.disconnect(); } catch (_) {} }
    if (this.stream) for (const track of this.stream.getTracks()) { track.onended = null; track.onmute = null; track.stop(); }
    if (this.context) { this.context.onstatechange = null; if (this.context.state !== 'closed') this.context.close().catch(() => {}); }
    this.node = this.sourceNode = this.stream = this.context = null; this.connection = null;
  }
  async connect({inputDeviceId = '', outputDeviceId = '', sampleRate = 96000, inputChannel = 1, referenceChannel = 2, outputChannel = 1, referenceOutputChannel = 2} = {}) {
    integer(inputChannel, 'Microphone input channel', 1, 2); integer(referenceChannel, 'Electrical reference input channel', 1, 2);
    integer(outputChannel, 'Speaker output channel', 1, 2); integer(referenceOutputChannel, 'Reference output channel', 1, 2);
    if (inputChannel === referenceChannel) throw new Error('Microphone and electrical-reference inputs must be different.');
    const epoch = ++this._epoch;
    if (this._pending) { clearTimeout(this._pending.timer); this._pending.reject(aborted()); this._pending = null; }
    this._dispose(); this.lastResult = null; this.lastCaptureWav = this.lastSourceWav = null;
    this.warnings = []; this._notify('connecting', 'Connecting audio…', 0);
    const capabilities = this.capabilities;
    if (!capabilities.secureContext || !capabilities.mediaDevices || !capabilities.audioWorklet) { this._notify('error', 'This browser needs HTTPS (or localhost), microphone access and AudioWorklet support.'); throw new Error(this.message); }
    const Audio = globalThis.AudioContext || globalThis.webkitAudioContext;
    let ctx, stream;
    try {
      // Construct/resume during the explicit Connect gesture. A rejected requested
      // rate falls back to the browser default, which is always shown to the user.
      try { ctx = new Audio({sampleRate, latencyHint:'interactive'}); }
      catch (_) { ctx = new Audio({latencyHint:'interactive'}); this.warnings.push('The requested processing rate was not accepted; the browser default is shown.'); }
      this.context = ctx;
      const resumed = ctx.resume();
      const audio = {echoCancellation:false, noiseSuppression:false, autoGainControl:false, channelCount:{ideal:2, max:2}, sampleRate:{ideal:sampleRate}};
      if (inputDeviceId) audio.deviceId = {exact:inputDeviceId};
      stream = await navigator.mediaDevices.getUserMedia({audio,video:false});
      await resumed;
      if (epoch !== this._epoch) { stream.getTracks().forEach(track => track.stop()); await ctx.close().catch(() => {}); throw aborted(); }
      this.stream = stream;
      if (outputDeviceId) {
        if (!ctx.setSinkId) throw new Error('This browser cannot choose a playback device. Select the interface as the system output, then reconnect using System output.');
        await ctx.setSinkId(outputDeviceId);
      }
      if (epoch !== this._epoch) throw aborted();
      await ctx.audioWorklet.addModule(new URL('./processor.js?v=20261024-browser3', import.meta.url));
      if (epoch !== this._epoch) throw aborted();
      const track = stream.getAudioTracks()[0];
      if (!track) throw new Error('No microphone track was opened.');
      const settings = track.getSettings ? track.getSettings() : {};
      const processingVerified = ['echoCancellation','noiseSuppression','autoGainControl'].every(flag => own(settings, flag) && settings[flag] === false);
      if (!processingVerified) this.warnings.push('Browser input processing is enabled or unverifiable. Delay can only be a diagnostic candidate.');
      if (ctx.sampleRate < 96000) this.warnings.push('This processing graph is below 96 kHz; E14 playback is blocked. Timing probes can still run.');
      if (settings.sampleRate !== ctx.sampleRate) this.warnings.push('Input track and graph sample rates differ or the input rate is unknown; browser resampling may occur.');
      const outputChannels = Math.min(2, Math.max(1, ctx.destination.maxChannelCount || 2));
      if (outputChannel > outputChannels) throw new Error('The browser exposes only one output channel. Choose output 1.');
      try { ctx.destination.channelCount = outputChannels; ctx.destination.channelInterpretation = 'discrete'; } catch (_) {}
      const node = new AudioWorkletNode(ctx, 'sonic-bench', {numberOfInputs:1, numberOfOutputs:1, outputChannelCount:[outputChannels], channelCountMode:'max', channelInterpretation:'discrete'});
      this.node = node; this.sourceNode = ctx.createMediaStreamSource(stream);
      this.sourceNode.connect(node); node.connect(ctx.destination);
      this.connection = {sampleRate: ctx.sampleRate, contextRate:ctx.sampleRate, requestedSampleRate:sampleRate,
        inputSettings:{...settings}, inputChannels:settings.channelCount || 0, outputChannels, processingVerified,
        outputSelectionSupported:Boolean(ctx.setSinkId), outputDeviceId:outputDeviceId || 'system-default', inputDeviceId:settings.deviceId || inputDeviceId || 'system-default',
        inputChannel, referenceChannel, outputChannel, referenceOutputChannel,
        baseLatency:finite(ctx.baseLatency) ? ctx.baseLatency : null, outputLatency:finite(ctx.outputLatency) ? ctx.outputLatency : null,
        latencyRole:'Browser-reported diagnostic values; never added to or subtracted from waveform alignment.',
        sampleRateRole:'AudioContext processing graph and track format reports; physical ADC/DAC rate and ultrasonic acoustic coverage are not independently verified.',
        inputConstraintsRequested:audio, hardwareClockVerified:false,
      };
      // Wait for a real input-bearing worklet quantum, rather than assuming
      // getUserMedia completion means that capture samples are flowing.
      const inputReady = new Promise((resolve, reject) => {
        const timer = setTimeout(() => { this._connectReject = null; reject(new Error('The browser did not expose microphone samples. Check the selected input and reconnect.')); }, 5000);
        this._connectReject = error => { clearTimeout(timer); reject(error); };
        node.port.onmessage = event => {
          if (event.data.type === 'input-ready') {
            clearTimeout(timer); this._connectReject = null;
            if (this.connection) this.connection.observedInputChannels = event.data.channels;
            resolve();
          } else this._onMessage(event.data);
        };
      });
      node.onprocessorerror = () => this.stop('Audio processing failed. Devices released; no accepted delay.');
      track.onended = () => this.stop('Microphone disconnected. Devices released; no accepted delay.');
      track.onmute = () => { if (this._pending) this._pending.errors.push('microphone_track_muted'); };
      ctx.onstatechange = () => { if (this._pending && ctx.state !== 'running') this.stop('Browser audio was interrupted. Devices released; no accepted delay.'); };
      if (ctx.state !== 'running') { this._connectReject?.(new Error('The browser did not start audio. Click Connect again to resume.')); }
      await inputReady;
      if (epoch !== this._epoch) throw aborted();
      if (ctx.state !== 'running') throw new Error('The browser did not start audio. Click Connect again to resume.');
      this._notify('ready', 'Connected. Check your routing and hardware level before playing.', 0);
      return this.status();
    } catch (error) {
      if (stream && stream !== this.stream) stream.getTracks().forEach(track => track.stop());
      if (epoch === this._epoch) { this._dispose(); this._notify(error.name === 'AbortError' ? 'idle' : 'error', error.message, 0); }
      else if (ctx && ctx !== this.context && ctx.state !== 'closed') ctx.close().catch(() => {});
      throw error;
    }
  }
  _onMessage(message) {
    const run = this._pending;
    if (!run || message.id !== run.id) return;
    if (message.type === 'started') { run.firstFrame = message.frame; return; }
    if (message.type === 'capture') { run.chunks.push(message); return; }
    if (message.type === 'progress') { this._notify(run.capture ? 'calibrating' : 'playing', run.capture ? 'Measuring with timing chirps…' : 'Playing the E14 reconstruction…', message.position / run.source.length); return; }
    if (message.type !== 'done') return;
    clearTimeout(run.timer);
    this._pending = null;
    run.resolve({...message, chunks:run.chunks, errors:run.errors, firstFrame:run.firstFrame});
  }
  async _playPlan(plan, {capture = false, reference = false} = {}) {
    if (!this.context || !this.node || !this.connection || this.context.state !== 'running') throw new Error('Connect audio first.');
    if (this._pending || !['ready'].includes(this.phase)) throw new Error('Audio is busy. Stop the current run first.');
    if (reference && this.connection.inputChannels < 2) throw new Error('Electrical reference needs two separately exposed input channels. This browser has not confirmed two inputs.');
    if (reference && (this.connection.referenceOutputChannel > this.connection.outputChannels || this.connection.referenceOutputChannel === this.connection.outputChannel)) throw new Error('Electrical reference needs a separate exposed output channel. Choose different speaker and reference outputs.');
    const epoch = this._epoch, connection = structuredClone(this.connection);
    this.lastResult = null; this.lastCaptureWav = this.lastSourceWav = null;
    this._notify(capture ? 'calibrating' : 'playing', capture ? 'Preparing timing probes…' : 'Preparing the E14 reconstruction…', 0);
    const hash = await sha256(plan.waveform.buffer);
    if (epoch !== this._epoch || !this.node) throw aborted();
    if (this.context.state !== 'running') { this.stop('Browser audio was suspended. Reconnect before playing.'); throw aborted(); }
    const done = await new Promise((resolve, reject) => {
      const id = ++this._id;
      const timer = setTimeout(() => {
        if (!this._pending || this._pending.id !== id) return;
        this._pending = null;
        reject(new Error('Audio stream timed out. Devices released; no accepted delay.'));
        this.stop('Audio stream timed out. Devices released; no accepted delay.');
      }, (plan.waveform.length / connection.sampleRate + 10) * 1000);
      this._pending = {id, resolve, reject, timer, capture, source:plan.waveform, chunks:[], errors:[], firstFrame:null};
      const source = plan.waveform.slice();
      this.node.port.postMessage({type:'start', id, source:source.buffer, capture,
        inputChannel:connection.inputChannel, referenceChannel:reference ? connection.referenceChannel : null,
        outputChannel:connection.outputChannel, referenceOutputChannel:reference ? connection.referenceOutputChannel : null}, [source.buffer]);
    });
    if (epoch !== this._epoch) throw aborted();
    const environment = {connection, user_agent:globalThis.navigator?.userAgent || '', generated_source_sha256:hash,
      generated_source_hash_encoding:'little-endian float32 sample bytes; source WAV is IEEE float32',
      date_utc:new Date().toISOString(), raw_audio_uploaded:false, sound_played:true, completed:true,
      physical_hardware_verified:false};
    this.lastSourceWav = wavBlob([plan.waveform], connection.sampleRate);
    if (!capture) {
      if (!Number.isInteger(done.firstFrame) || done.firstFrame < 0 ||
          done.frames !== plan.waveform.length || done.processGaps !== 0 ||
          done.endFrame !== done.firstFrame + plan.waveform.length) {
        throw new Error('Playback was interrupted: the browser reported missing or inconsistent audio frames. Reconnect and repeat the block.');
      }
      const result = {...plan.metadata, ...environment, transport:{worklet_first_frame:done.firstFrame, worklet_end_frame:done.endFrame, worklet_process_gaps:done.processGaps, limitation:'Browser-hidden driver/hardware xruns are not exposed.'}};
      this.lastResult = result; this._notify('ready', 'Playback complete. You can download the stimulus and event record.', 1); return result;
    }
    this._notify('analyzing', 'Checking captured probes and timing integrity…', 1);
    // Yield one render frame before CPU analysis; no clock timestamps enter DSP.
    await new Promise(resolve => setTimeout(resolve, 0));
    if (epoch !== this._epoch) throw aborted();
    const captured = assessCaptureChunks(done.chunks, plan.waveform.length, done.firstFrame, done);
    captured.errors.push(...done.errors); captured.valid = captured.valid && !done.errors.length;
    const transport = {valid:captured.valid, errors:captured.errors, captured_frames:captured.captured_frames,
      worklet_first_frame:captured.worklet_first_frame, worklet_end_frame:captured.worklet_end_frame,
      input_channel_minimum:captured.input_channel_minimum, chunks:done.chunks.length,
      observed_process_gaps:done.processGaps, missing_input_frames:done.inputMissingFrames,
      no_observed_gaps:captured.valid, hardware_xruns_verifiable:false, limitations:[captured.limitation]};
    const result = {...analyzeCapture({source:plan.waveform, microphone:captured.microphone, reference:captured.reference,
      sampleRate:connection.sampleRate, stimulus:plan.metadata, transport, processingVerified:connection.processingVerified,
      inputChannels:connection.inputChannels, requireReference:reference}), ...environment, stimulus:plan.metadata,
      capture_wav_channels:reference ? ['microphone','electrical_reference'] : ['microphone'],
      source_wav_channels:['generated_output_reference'],
    };
    if (epoch !== this._epoch) throw aborted();
    this.lastCaptureWav = wavBlob(captured.reference ? [captured.microphone,captured.reference] : [captured.microphone], connection.sampleRate);
    this.lastResult = result;
    this._notify('ready', result.usable_measurement ? 'Timing screening passed. Review the estimate and its scope below.' : 'No accepted delay. Review the signal and browser checks below.', 1);
    return result;
  }
  async play(options = {}) {
    if (!this.connection) throw new Error('Connect audio first.');
    const plan = makeSonicBlock({...options, sampleRate:this.connection.sampleRate});
    try { return await this._playPlan(plan); }
    catch (error) { if (error.name !== 'AbortError' && this.context && this.phase !== 'ready') this.stop(error.message + ' Devices released; no accepted delay.'); throw error; }
  }
  async calibrate(options = {}) {
    if (!this.connection) throw new Error('Connect audio first.');
    const plan = makeProbePlan({...options, sampleRate:this.connection.sampleRate});
    try { return await this._playPlan(plan, {capture:true, reference:Boolean(options.reference)}); }
    catch (error) { if (error.name !== 'AbortError' && this.context && this.phase !== 'ready') this.stop(error.message + ' Devices released; no accepted delay.'); throw error; }
  }
  stop(message = 'Stopped. Audio devices released.') {
    ++this._epoch;
    if (this._pending) { clearTimeout(this._pending.timer); this._pending.reject(aborted()); this._pending = null; }
    this._dispose(); this._notify('idle', message, 0);
  }
  disconnect() { this.stop('Disconnected. Microphone and playback devices released.'); }
}
