"""Rolling waveform-delay estimates for explicitly started live audio.

``push`` only copies callback data into a bounded ring. ``snapshot`` performs
correlation on the calling (non-audio) thread. Playback and capture sample zero
must refer to the same duplex callback, and ``start_frame`` uses that stream's
sample coordinates. This mode includes the interface/host buffering offset;
it is not calibrated acoustic onset or neural-response timing.
"""
from __future__ import annotations

from collections import deque
from copy import deepcopy
import math
import threading

import numpy as np

from latency.analysis import analyze_trials, _normalized_correlations


SONIC_MATCH_CENTERS_HZ = (2000, 4000, 6000, 8000, 9000, 10500)


def _envelope_step(samplerate):
    return max(1, 2 ** int(math.floor(math.log2(max(1.0, samplerate / 2000.0)))))


def _sonic_envelope_delay(source, microphone, samplerate, max_lag_ms):
    """Match the random pip sequence through multiple amplitude envelopes.

    Carrier phase is not an onset marker after loudspeaker/room filtering.
    Each narrow band's analytic amplitude is independently normalized, so a
    few loud frequencies cannot overwhelm the sequence's other useful bands.
    At least three bands must support the same envelope delay. Distinct, nearly
    equal delay alternatives remain rejected. Delays closer than 5 ms are not
    resolved as separate paths by this method.
    """
    reasons = []
    if np.sqrt(np.mean(np.asarray(source, dtype=np.float64) ** 2)) < 1e-6:
        reasons.append("reference_missing_or_too_quiet")
    if np.sqrt(np.mean(np.asarray(microphone, dtype=np.float64) ** 2)) < 1e-6:
        reasons.append("microphone_missing_or_too_quiet")
    step = _envelope_step(samplerate)
    envelope_rate = samplerate / step
    max_lag = int(math.floor(samplerate * max_lag_ms / 1000)) // step
    measured = {"accepted": False, "delay_ms": None, "reasons": reasons,
                "method": "multiband_amplitude_envelope", "search_step_ms": 1000 / envelope_rate,
                "useful_bands_hz": [], "peak_correlation": None, "secondary_peak_ratio": None}
    if reasons:
        return measured
    size = 1 << (len(microphone) - 1).bit_length()
    reference = np.zeros(len(microphone), dtype=np.float64)
    reference[:len(source)] = source
    spectra = np.fft.fft(np.stack((reference, microphone)), n=size, axis=1)
    frequency = np.fft.fftfreq(size, 1 / samplerate)
    smooth_samples = max(1, int(round(envelope_rate * 0.002)))
    smooth = np.ones(smooth_samples) / smooth_samples
    trim = max(1, int(round(envelope_rate * 0.010)))
    reference_stop = len(source[::step]) - trim
    if reference_stop - trim < 32:
        reasons.append("sequence_window_too_short")
        return measured
    correlations = []
    centers = []
    for center in SONIC_MATCH_CENTERS_HZ:
        if center + 450 >= samplerate / 2:
            continue
        distance = np.abs(frequency - center)
        mask = np.where(distance < 450, 1 + np.cos(np.pi * np.minimum(distance / 450, 1)), 0)
        # A positive-frequency-only analytic band, identically applied to both
        # paths. Zero padding and the 10 ms trim suppress boundary transients.
        envelopes = np.abs(np.fft.ifft(spectra * mask, axis=1))[:, ::step]
        ref_env = np.convolve(envelopes[0], smooth, mode="same")[trim:reference_stop]
        mic_env = np.convolve(envelopes[1], smooth, mode="same")[trim:reference_stop + max_lag]
        ref_rms = float(np.sqrt(np.mean(ref_env ** 2)))
        if ref_rms < 1e-6 or np.std(ref_env) < max(1e-6, 0.15 * ref_rms) or np.std(mic_env) < 1e-6:
            continue
        correlation = _normalized_correlations(ref_env, mic_env)
        # Eligibility must not depend on the best matching lag: selecting only
        # correlated bands can cherry-pick accidental matches to a wrong order.
        # Compare burst amplitude with the band's quiet envelope floor instead,
        # and retain every eligible band, including negative evidence.
        if float(np.percentile(mic_env, 99)) < 4 * max(1e-6, float(np.median(mic_env))):
            continue
        correlations.append(correlation)
        centers.append(center)
    measured["useful_bands_hz"] = centers
    if len(correlations) < 3:
        reasons.append("insufficient_reliable_frequency_bands")
        return measured
    combined = np.mean(correlations, axis=0)
    peak_index = int(np.argmax(combined))
    peak = float(combined[peak_index])
    guard = max(1, int(math.ceil(envelope_rate * 0.005)))
    outside = np.ones(len(combined), dtype=bool)
    outside[max(0, peak_index - guard):peak_index + guard + 1] = False
    secondary = float(np.max(combined[outside])) if np.any(outside) else 0.0
    ratio = max(0.0, secondary) / peak if peak > 0 else 1.0
    measured.update(peak_correlation=peak, secondary_peak_ratio=ratio)
    if peak < 0.55:
        reasons.append("weak_envelope_correlation")
    if sum(float(correlation[peak_index]) >= 0.45 for correlation in correlations) < 3:
        reasons.append("frequency_bands_disagree")
    if ratio >= 0.85:
        reasons.append("ambiguous_envelope_delay_paths")
    if peak_index in (0, len(combined) - 1):
        reasons.append("boundary_peak_unresolved")
    if not reasons:
        measured.update(accepted=True, delay_ms=peak_index * 1000 / envelope_rate)
    return measured


class LiveDelayTracker:
    """Bounded live probe history, with no device access or background thread."""

    def __init__(self, *, max_lag_ms=250.0, ring_seconds=2.0, max_points=32, max_pending=64):
        if not math.isfinite(max_lag_ms) or max_lag_ms <= 0:
            raise ValueError("max_lag_ms must be finite and positive")
        if not math.isfinite(ring_seconds) or ring_seconds <= max_lag_ms / 1000:
            raise ValueError("ring_seconds must exceed the maximum lag")
        if isinstance(max_points, bool) or not isinstance(max_points, int) or max_points < 1:
            raise ValueError("max_points must be a positive integer")
        if isinstance(max_pending, bool) or not isinstance(max_pending, int) or max_pending < 1:
            raise ValueError("max_pending must be a positive integer")
        self._max_lag_ms = float(max_lag_ms)
        self._ring_seconds = float(ring_seconds)
        self._max_points = max_points
        self._max_pending = max_pending
        self._lock = threading.RLock()
        self._analysis_lock = threading.Lock()
        self.reset(96000)

    def reset(self, samplerate, has_reference=False, start_frame=0):
        if isinstance(samplerate, bool) or not math.isfinite(samplerate) or samplerate <= 0:
            raise ValueError("samplerate must be finite and positive")
        if isinstance(start_frame, bool) or not isinstance(start_frame, (int, np.integer)) or start_frame < 0:
            raise ValueError("start_frame must be a nonnegative integer")
        rate = float(samplerate)
        lag = int(math.floor(rate * self._max_lag_ms / 1000))
        if lag < 1:
            raise ValueError("maximum lag must span at least one sample")
        capacity = int(math.ceil(rate * self._ring_seconds))
        with self._lock:
            # In-flight analysis cannot publish a result from an earlier stream.
            self._generation = getattr(self, "_generation", 0) + 1
            self._samplerate = rate
            self._max_lag = lag
            self._has_reference = bool(has_reference)
            self._source_kind = "timing_probe"
            self._match_band = [1550.0, 10950.0]
            self._ring = np.empty(capacity, dtype=np.float32)
            self._frame = int(start_frame)
            self._origin_frame = int(start_frame)
            self._next_trial = 0
            self._pending = deque()
            self._points = deque(maxlen=self._max_points)
            self._invalid_reason = None
            self._last_window = None

    def add_probe(self, source_waveform, plan, start_frame):
        """Schedule exact source segments from a generated probe-plan manifest.

        This is a control-thread operation. Call before its first output sample
        is emitted. No waveform is generated or played by the tracker itself.
        """
        if isinstance(start_frame, bool) or not isinstance(start_frame, (int, np.integer)) or start_frame < 0:
            raise ValueError("start_frame must be a nonnegative integer")
        source = np.asarray(source_waveform, dtype=np.float32)
        if source.ndim != 1 or not len(source) or not np.isfinite(source).all():
            raise ValueError("source_waveform must be a finite nonempty mono array")
        if not isinstance(plan, dict) or not isinstance(plan.get("trials"), (list, tuple)):
            raise ValueError("plan must contain a trials list")
        scheduled = []
        for trial in plan["trials"]:
            start, stop = trial["output_start"], trial["output_stop"]
            if any(isinstance(v, bool) or not isinstance(v, (int, np.integer)) for v in (start, stop)):
                raise ValueError("probe coordinates must be integer samples")
            if not 0 <= start < stop <= len(source) or stop - start < 16:
                raise ValueError("probe segments must contain at least 16 source samples")
            scheduled.append((int(start_frame + start), int(start_frame + stop), int(start), int(stop)))
        if any(b[0] < a[0] for a, b in zip(scheduled, scheduled[1:])):
            raise ValueError("probe trials must be ordered by output_start")
        with self._lock:
            plan_rate = plan.get("sample_rate_hz", self._samplerate)
            if plan_rate != self._samplerate:
                raise ValueError("probe plan and capture sample rates must match")
            if self._pending and scheduled and scheduled[0][0] < self._pending[-1]["start"]:
                raise ValueError("probe plans must be scheduled in time order")
            source_kind = plan.get("source_kind", plan.get("kind", "timing_probe"))
            if source_kind == "sonic_e14_reconstruction":
                source_kind = "sonic_sequence"
            if source_kind not in ("timing_probe", "sonic_sequence"):
                raise ValueError("source_kind must be timing_probe or sonic_sequence")
            self._source_kind = source_kind
            for start, stop, source_start, source_stop in scheduled:
                trial = {"trial": self._next_trial, "start": start, "stop": stop,
                         "source_kind": source_kind}
                self._next_trial += 1
                if self._invalid_reason:
                    self._points.append(self._rejected(trial, self._invalid_reason))
                elif not self._has_reference:
                    if stop - start + self._max_lag > len(self._ring):
                        self._points.append(self._rejected(trial, "probe_window_exceeds_ring_capacity"))
                        continue
                    if len(self._pending) >= self._max_pending:
                        self._points.append(self._rejected(self._pending.popleft(), "pending_queue_overflow"))
                    trial["source"] = source[source_start:source_stop].copy()
                    self._pending.append(trial)

    def push(self, microphone, reference=None):
        """Copy one mono input callback; never correlate or inspect its spectrum.

        ``reference`` is accepted for engine integration, but live electrical
        reference analysis is deliberately unavailable in this first version.
        """
        values = np.asarray(microphone, dtype=np.float32)
        if values.ndim != 1:
            raise ValueError("microphone callback must be mono")
        count = len(values)
        if not count:
            return
        with self._lock:
            end = self._frame + count
            capacity = len(self._ring)
            kept = min(count, capacity)
            start = end - kept
            offset = start % capacity
            first = min(kept, capacity - offset)
            self._ring[offset:offset + first] = values[count - kept:count - kept + first]
            if first < kept:
                self._ring[:kept - first] = values[count - kept + first:]
            self._frame = end

    def invalidate(self, reason):
        """Latch a transport failure until reset; no valid-looking delays remain."""
        if isinstance(reason, (list, tuple, set)):
            reason = ", ".join(str(value) for value in reason)
        reason = str(reason).strip() or "invalid_audio_transport"
        with self._lock:
            self._generation += 1
            self._invalid_reason = reason
            for point in self._points:
                point.update(accepted=False, delay_ms=None, reason=reason, reasons=[reason])
            while self._pending:
                self._points.append(self._rejected(self._pending.popleft(), reason))

    def cancel_pending(self):
        """Cancel unmeasured windows when playback stops, preserving its history."""
        with self._lock:
            self._generation += 1
            self._pending.clear()

    def debug_recent_window(self):
        """Opt-in private raw diagnostic copy; never writes or publishes audio."""
        with self._lock:
            if self._last_window is None:
                return None
            return {key: value.copy() if isinstance(value, np.ndarray) else value
                    for key, value in self._last_window.items()}

    @staticmethod
    def _rejected(trial, reason):
        return {"trial": int(trial["trial"]), "start_frame": int(trial["start"]),
                "accepted": False, "delay_ms": None, "reason": reason, "reasons": [reason]}

    def _copy_window(self, start, stop):
        """Copy a currently retained ring range while the state lock is held."""
        size = stop - start
        offset = start % len(self._ring)
        first = min(size, len(self._ring) - offset)
        values = np.empty(size, dtype=np.float32)
        values[:first] = self._ring[offset:offset + first]
        if first < size:
            values[first:] = self._ring[:size - first]
        return values

    def _analyze_ready(self):
        while True:
            with self._lock:
                if self._has_reference or self._invalid_reason or not self._pending:
                    return
                trial = self._pending[0]
                if trial["stop"] + self._max_lag > self._frame:
                    return
                self._pending.popleft()
                if trial["start"] < max(self._origin_frame, self._frame - len(self._ring)):
                    self._points.append(self._rejected(trial, "capture_window_expired"))
                    continue
                generation = self._generation
                samplerate = self._samplerate
                microphone = self._copy_window(trial["start"], trial["stop"] + self._max_lag)
                raw_window = {"microphone": microphone.copy(), "source": trial["source"].copy(),
                              "samplerate": samplerate, "start_frame": trial["start"],
                              "source_kind": trial["source_kind"]}
            # The lock is released before FFT/quality checks. Reset or invalidate
            # may occur while this runs; the generation check guards publication.
            reference = np.zeros(len(microphone), dtype=np.float32)
            reference[:len(trial["source"])] = trial["source"]
            if not np.isfinite(microphone).all():
                point = self._rejected(trial, "non_finite_audio")
            else:
                try:
                    # Inspect raw microphone clipping before filtering could
                    # smooth an over-range sample into a valid-looking value.
                    raw_clipped = bool(np.any(np.abs(microphone) >= 0.999))
                    raw_source_clipped = bool(np.any(np.abs(trial["source"]) >= 0.999))
                    if trial["source_kind"] == "sonic_sequence":
                        measured = _sonic_envelope_delay(trial["source"], microphone, samplerate, self._max_lag_ms)
                    else:
                        result = analyze_trials(np.column_stack((microphone, reference)), samplerate,
                                                [(0, len(trial["source"]))], max_lag_ms=self._max_lag_ms)
                        measured = result["trials"][0]
                    reasons = list(measured["reasons"])
                    if raw_clipped and "microphone_clipping" not in reasons:
                        reasons.append("microphone_clipping")
                    if raw_source_clipped and "reference_clipping" not in reasons:
                        reasons.append("reference_clipping")
                    delay = measured["delay_ms"]
                    accepted = bool(measured["accepted"] and not reasons and delay is not None and math.isfinite(delay))
                    point = {"trial": int(trial["trial"]), "start_frame": int(trial["start"]),
                             "accepted": accepted, "delay_ms": float(delay) if accepted else None,
                             "reason": None if accepted else ", ".join(reasons) or "invalid_delay",
                             "reasons": reasons}
                    if trial["source_kind"] == "sonic_sequence":
                        point["diagnostics"] = {key: measured[key] for key in
                                                ("method", "search_step_ms", "useful_bands_hz",
                                                 "peak_correlation", "secondary_peak_ratio")}
                except (ValueError, FloatingPointError):
                    point = self._rejected(trial, "invalid_audio_window")
            with self._lock:
                if generation == self._generation:
                    self._points.append(point)
                    self._last_window = raw_window

    def snapshot(self):
        """Analyze complete probes off callback, then return finite JSON data."""
        # Multiple HTTP clients may poll. Only one performs analysis at a time;
        # the audio callback never acquires this analysis lock.
        with self._analysis_lock:
            self._analyze_ready()
            with self._lock:
                points = deepcopy(list(self._points))
                reason = self._invalid_reason
                if self._has_reference:
                    reason = "Use Measure delay for electrical-reference analysis"
                return {
                    "mode": "electrical_reference" if self._has_reference else "playback_to_microphone",
                    "source_kind": self._source_kind,
                    "match_band_hz": list(self._match_band) if self._source_kind == "sonic_sequence" else None,
                    "match_band_centers_hz": list(SONIC_MATCH_CENTERS_HZ) if self._source_kind == "sonic_sequence" else [],
                    "method": "multiband_amplitude_envelope" if self._source_kind == "sonic_sequence"
                              else "normalized_waveform_cross_correlation",
                    "search_step_ms": (1000.0 * _envelope_step(self._samplerate) / self._samplerate
                        if self._source_kind == "sonic_sequence" else 1000.0 / self._samplerate),
                    "points": points,
                    "latest_delay_ms": points[-1]["delay_ms"] if points else None,
                    "reference_required": False,
                    "available": not self._has_reference and self._invalid_reason is None,
                    "reason": reason,
                    "pending_trials": len(self._pending),
                    "captured_frames": self._frame,
                    "samplerate_hz": self._samplerate,
                    "interpretation": ("Playback-to-microphone waveform alignment includes host/interface buffering. "
                                       + ("SONIC matching compares independently normalized amplitude envelopes in multiple tone bands. "
                                          "Its coarser envelope search step is not timing accuracy; paths within 5 ms are unresolved. "
                                          if self._source_kind == "sonic_sequence" else "")
                                       + "It is not calibrated acoustic onset or neural timing."),
                }
