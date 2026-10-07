(function (root, factory) {
  'use strict';
  const model = factory();
  if (typeof module === 'object' && module.exports) {
    module.exports = model;
  } else {
    root.SONICModel = model;
  }
}(typeof globalThis !== 'undefined' ? globalThis : this, function () {
  'use strict';

  // Published SONIC v1 Table 1. Accuracy and SD are percentage points.
  // These reported results stay fixed when a teaching control changes.
  const results = Object.freeze({
    C: Object.freeze({
      sessions: Object.freeze([174.6, 204.0, 201.6, 227.2]),
      mean: 201.9,
      accuracy: 45.4,
      sd: 3.1,
      classes: 37,
    }),
    E: Object.freeze({
      sessions: Object.freeze([228.2, 231.6, 225.1, 235.4]),
      mean: 230.1,
      accuracy: 75.9,
      sd: 0.7,
      classes: 14,
    }),
  });

  function requireFiniteNumber(value, name) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new TypeError(name + ' must be a finite number.');
    }
  }

  function requirePositiveNumber(value, name) {
    requireFiniteNumber(value, name);
    if (value <= 0) {
      throw new RangeError(name + ' must be greater than zero.');
    }
  }

  // Ideal input entropy rate for equally likely classes and perfect decoding.
  // It is not a prediction of achieved neural decoding or device capacity.
  function ceilingBps(classes, durationMs) {
    requirePositiveNumber(classes, 'classes');
    if (!Number.isSafeInteger(classes)) {
      throw new RangeError('classes must be a positive safe integer.');
    }
    requirePositiveNumber(durationMs, 'durationMs');
    const rate = Math.log2(classes) * 1000 / durationMs;
    if (!Number.isFinite(rate)) {
      throw new RangeError('The supplied duration produces an unrepresentable rate.');
    }
    return rate;
  }

  // Rounded teaching approximation: <1 ms measurement, 5 ms filtering,
  // plus the observation-window length. The 1 ms term is an approximation.
  // Physiology and computation are excluded, as in the paper's definition.
  function intrinsicDelayMs(windowMs) {
    requirePositiveNumber(windowMs, 'windowMs');
    return 6 + windowMs;
  }

  return Object.freeze({ results, ceilingBps, intrinsicDelayMs });
}));
