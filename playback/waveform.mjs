export const SAMPLE_RATE = 96000;
export const E_FREQUENCIES = Object.freeze([2000, 4000, 6000, 8000, 9000, 10500, 17000, 18200, 19500, 20900, 22400, 24000, 25800, 27000]);
export const AUDIBLE_FREQUENCIES = Object.freeze(E_FREQUENCIES.slice(0, 6));

export function sinePip(frequency, duration, dbfs, sampleRate = SAMPLE_RATE, rampSeconds = 0.002) {
  if (!Number.isFinite(frequency) || frequency <= 0 || frequency >= sampleRate / 2) throw new Error('Frequency must be below Nyquist.');
  if (!Number.isFinite(duration) || duration <= 0 || duration > 5) throw new Error('Duration must be between 0 and 5 seconds.');
  if (!Number.isFinite(dbfs) || dbfs < -60 || dbfs > -18) throw new Error('Level must be between −60 and −18 dBFS.');
  const count = Math.round(duration * sampleRate);
  const ramp = Math.min(Math.round(rampSeconds * sampleRate), Math.floor(count / 2));
  if (ramp < 2) throw new Error('Ramp is too short.');
  const result = new Float32Array(count);
  const peak = 10 ** (dbfs / 20);
  for (let i = 0; i < count; i++) {
    const edge = Math.min(i, count - 1 - i);
    const envelope = edge < ramp ? 0.5 * (1 - Math.cos(Math.PI * edge / (ramp - 1))) : 1;
    result[i] = peak * envelope * Math.sin(2 * Math.PI * frequency * i / sampleRate);
  }
  return result;
}

export function buildSequence(frequencies, seconds, dbfs, sampleRate = SAMPLE_RATE) {
  if (!Array.isArray(frequencies) || frequencies.length === 0) throw new Error('Select frequencies.');
  if (!Number.isFinite(seconds) || seconds < 0.01 || seconds > 5) throw new Error('Sequence must be at most 5 seconds.');
  const pipLength = Math.round(0.01 * sampleRate);
  const count = Math.floor(seconds / 0.01);
  const result = new Float32Array(count * pipLength);
  // Cycle in the listed order. This is a connection check, not the paper's random stimulus order.
  const pips = frequencies.map((frequency) => sinePip(frequency, 0.01, dbfs, sampleRate));
  for (let i = 0; i < count; i++) result.set(pips[i % pips.length], i * pipLength);
  return result;
}

export function stereoSamples(mono, channel) {
  if (!['both', 'left', 'right'].includes(channel)) throw new Error('Unknown channel.');
  const silence = new Float32Array(mono.length);
  return [channel === 'right' ? silence : mono, channel === 'left' ? silence : mono];
}
