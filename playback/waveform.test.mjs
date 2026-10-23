import assert from 'node:assert/strict';
import { sinePip, buildSequence, stereoSamples, E_FREQUENCIES, AUDIBLE_FREQUENCIES, logarithmicSweep } from './waveform.mjs';

assert.deepEqual(E_FREQUENCIES, [2000, 4000, 6000, 8000, 9000, 10500, 17000, 18200, 19500, 20900, 22400, 24000, 25800, 27000]);
assert.equal(AUDIBLE_FREQUENCIES.length, 6);
for (const f of E_FREQUENCIES) {
  const pip = sinePip(f, 0.01, -18);
  assert.equal(pip.length, 960);
  assert.equal(pip[0], 0);
  assert.ok(Math.abs(pip.at(-1)) < 1e-12);
  assert.ok(pip.every(Number.isFinite));
  assert.ok(pip.every((v) => Math.abs(v) <= 10 ** (-18 / 20) + 1e-8));
}
const pip = sinePip(2000, 0.01, -36);
const amplitude = 10 ** (-36 / 20);
const expectedRamp = amplitude * 0.5 * (1 - Math.cos(Math.PI * 101 / 191)) * Math.sin(2 * Math.PI * 2000 * 101 / 96000);
assert.ok(Math.abs(pip[101] - expectedRamp) < 1e-8);
const test = sinePip(1000, 0.5, -36);
assert.equal(test.length, 48000);
// Central 96-sample periods are identical for the 1 kHz test at 96 kHz.
for (let i = 500; i < 596; i++) assert.ok(Math.abs(test[i] - test[i + 96]) < 1e-7);
const sequence = buildSequence(AUDIBLE_FREQUENCIES, 5, -36);
assert.equal(sequence.length, 480000);
assert.deepEqual(sequence.slice(0, 960), pip);
assert.deepEqual(sequence.slice(6 * 960, 7 * 960), pip);
for (const channel of ['left', 'right', 'both']) {
  const [left, right] = stereoSamples(pip, channel);
  assert.deepEqual(channel === 'right' ? right : left, pip);
  if (channel !== 'both') assert.ok((channel === 'left' ? right : left).every((v) => v === 0));
  else assert.deepEqual(right, pip);
}
assert.throws(() => sinePip(48000, 0.01, -36));
assert.throws(() => sinePip(1000, 0.5, -17));
assert.throws(() => buildSequence(AUDIBLE_FREQUENCIES, 5.01, -36));
const sweep = logarithmicSweep(-36);
assert.equal(sweep.length, 480000);
assert.equal(sweep[0], 0);
assert.ok(Math.abs(sweep.at(-1)) < 1e-12);
assert.ok(sweep.every((value) => Number.isFinite(value) && Math.abs(value) <= amplitude + 1e-8));
// Count positive zero crossings in late/early interior windows to verify an increasing sweep.
const crossings = (start, end) => { let count = 0; for (let i = start + 1; i < end; i++) if (sweep[i - 1] <= 0 && sweep[i] > 0) count++; return count; };
assert.ok(crossings(400000, 410000) > 50 * crossings(10000, 20000));
assert.throws(() => logarithmicSweep(-17));
assert.throws(() => logarithmicSweep(-36, 96000, 6));
console.log('Waveform checks passed: frequency list, timing, ramps, peak bounds, sequence bounds, and channel isolation.');
