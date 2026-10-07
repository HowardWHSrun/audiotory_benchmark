'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const model = require('../web/model.js');

function approximately(actual, expected, tolerance = 1e-9) {
  assert.ok(Math.abs(actual - expected) <= tolerance,
    `${actual} differs from ${expected} by more than ${tolerance}`);
}

test('published fixtures preserve Table 1, accuracy, and reported rounded means', () => {
  assert.deepEqual(model.results.C, {
    sessions: [174.6, 204.0, 201.6, 227.2],
    mean: 201.9, accuracy: 45.4, sd: 3.1, classes: 37,
  });
  assert.deepEqual(model.results.E, {
    sessions: [228.2, 231.6, 225.1, 235.4],
    mean: 230.1, accuracy: 75.9, sd: 0.7, classes: 14,
  });

  // Session values and means are rounded in the paper; retain the reported
  // means rather than treating the printed session values as raw data.
  for (const result of Object.values(model.results)) {
    const printedSessionMean = result.sessions.reduce((sum, value) => sum + value, 0) / 4;
    assert.equal(Math.round(printedSessionMean * 10) / 10, result.mean);
  }
  approximately(model.results.C.mean * 0.01, 2.019);
  approximately(model.results.E.mean * 0.01, 2.301);
});

test('uniform stimulus ceilings use seconds and reproduce both published alphabets', () => {
  approximately(model.ceilingBps(37, 10), 520.945336562895);
  approximately(model.ceilingBps(14, 10), 380.7354922057604);
  assert.equal(model.ceilingBps(2, 10), 100);
  assert.equal(model.ceilingBps(1, 10), 0);
});

test('a longer tone halves the theoretical ceiling without predicting a new published score', () => {
  const reportedBefore = JSON.stringify(model.results);
  for (const classes of [14, 37]) {
    approximately(model.ceilingBps(classes, 20), model.ceilingBps(classes, 10) / 2);
  }
  assert.equal(JSON.stringify(model.results), reportedBefore);
  assert.equal(model.results.C.mean, 201.9);
  assert.equal(model.results.E.mean, 230.1);
});

test('rounded intrinsic delay reproduces 56 ms and 11 ms for the paper observation windows', () => {
  assert.equal(model.intrinsicDelayMs(50), 56);
  assert.equal(model.intrinsicDelayMs(5), 11);
  assert.equal(model.intrinsicDelayMs(50) - model.intrinsicDelayMs(5), 45);
  // The API adds only the rounded measurement/filter overhead; it does not
  // add auditory physiology or decoder computation to these paper terms.
  assert.equal(model.intrinsicDelayMs(20), 26);
});

test('formula inputs reject non-finite numbers, non-numbers, and invalid positive parameters', () => {
  for (const invalid of [NaN, Infinity, -Infinity, undefined, null, '10']) {
    assert.throws(() => model.ceilingBps(14, invalid), TypeError);
    assert.throws(() => model.ceilingBps(invalid, 10), TypeError);
    assert.throws(() => model.intrinsicDelayMs(invalid), TypeError);
  }
  for (const invalid of [0, -1]) {
    assert.throws(() => model.ceilingBps(14, invalid), RangeError);
    assert.throws(() => model.ceilingBps(invalid, 10), RangeError);
    assert.throws(() => model.intrinsicDelayMs(invalid), RangeError);
  }
  assert.throws(() => model.ceilingBps(2.5, 10), RangeError);
  assert.throws(() => model.ceilingBps(Number.MAX_SAFE_INTEGER + 1, 10), RangeError);
  assert.throws(() => model.ceilingBps(2, Number.MIN_VALUE), RangeError);
});

test('browser global and CommonJS exports provide the same numerical API', () => {
  const context = vm.createContext({});
  const source = fs.readFileSync(path.join(__dirname, '../web/model.js'), 'utf8');
  vm.runInContext(source, context);
  assert.equal(context.SONICModel.results.C.mean, model.results.C.mean);
  approximately(context.SONICModel.ceilingBps(37, 10), model.ceilingBps(37, 10));
  assert.equal(context.SONICModel.intrinsicDelayMs(5), 11);
});
