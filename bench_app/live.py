"""Bounded native-audio telemetry. No recording, playback or device access here."""
from __future__ import annotations

import threading
import time

import numpy as np


class LiveAudioBuffer:
    """Keep half a second of samples; do FFT and display reduction off callback."""

    def __init__(self):
        self._lock = threading.Lock()
        self.reset(96000)

    def reset(self, samplerate, has_input=True):
        with self._lock:
            self._samplerate = int(samplerate)
            self._has_input = bool(has_input)
            self._ring = np.zeros((max(1, int(samplerate) // 2), 2), dtype=np.float32)
            self._frames = 0
            self._updated = None
            self._errors = set()

    def push(self, output, microphone=None, status_bits=0):
        source = np.asarray(output, dtype=np.float32).reshape(-1)
        mic = None if microphone is None else np.asarray(microphone, dtype=np.float32).reshape(-1)
        if mic is not None and len(mic) != len(source):
            raise ValueError("Live input and output must contain the same number of frames")
        if not len(source):
            return
        finite = bool(np.isfinite(source).all() and (mic is None or np.isfinite(mic).all()))
        if not finite:
            source = np.nan_to_num(source, nan=0, posinf=0, neginf=0)
            if mic is not None:
                mic = np.nan_to_num(mic, nan=0, posinf=0, neginf=0)
        with self._lock:
            if not finite:
                self._errors.add("non_finite_audio")
            if status_bits:
                self._errors.add("portaudio_callback_status_flag")
            total = len(source)
            capacity = len(self._ring)
            kept = min(total, capacity)
            start = (self._frames + total - kept) % capacity
            first = min(kept, capacity - start)
            tail = source[-kept:]
            self._ring[start:start + first, 0] = tail[:first]
            self._ring[:kept - first, 0] = tail[first:]
            if mic is not None:
                tail = mic[-kept:]
                self._ring[start:start + first, 1] = tail[:first]
                self._ring[:kept - first, 1] = tail[first:]
            else:
                self._ring[start:start + first, 1] = 0
                self._ring[:kept - first, 1] = 0
            self._frames += total
            self._updated = time.monotonic()

    @staticmethod
    def _levels(samples, samplerate):
        if not len(samples):
            return {"min": [], "max": [], "rms_dbfs": -120.0, "peak_dbfs": -120.0, "clipped": False}
        bins = min(400, len(samples))
        # reduceat preserves transient peaks even when hundreds of samples
        # map onto one display pixel; this is not audio downsampling.
        starts = np.linspace(0, len(samples), bins + 1, dtype=int)[:-1]
        recent = samples[-max(1, samplerate // 20):].astype(np.float64)
        peak = float(np.max(np.abs(recent)))
        rms = float(np.sqrt(np.mean(recent * recent)))
        db = lambda value: float(max(-120.0, 20 * np.log10(max(value, 1e-6))))
        return {"min": np.minimum.reduceat(samples, starts).astype(float).tolist(),
                "max": np.maximum.reduceat(samples, starts).astype(float).tolist(),
                "rms_dbfs": db(rms), "peak_dbfs": db(peak),
                "clipped": bool(np.any(np.abs(samples) >= .999))}

    @staticmethod
    def _spectrum(samples, samplerate):
        if len(samples) < 64:
            return {"frequency_hz": [], "dbfs": []}
        count = min(8192, len(samples))
        window = np.hanning(count)
        values = np.abs(np.fft.rfft(samples[-count:].astype(np.float64) * window)) * 2 / max(1, window.sum())
        frequencies = np.fft.rfftfreq(count, 1 / samplerate)
        high = min(40000, samplerate / 2)
        edges = np.geomspace(20, high, 513)
        frequency, levels = [], []
        for low, upper in zip(edges[:-1], edges[1:]):
            left, right = np.searchsorted(frequencies, (low, upper))
            if right > left:
                frequency.append(float(np.sqrt(low * upper)))
                levels.append(float(max(-120.0, 20 * np.log10(max(float(np.max(values[left:right])), 1e-6)))))
        return {"frequency_hz": frequency, "dbfs": levels}

    def snapshot(self, active=False, probe_playing=False):
        with self._lock:
            frames = self._frames
            size = min(frames, len(self._ring))
            end = frames % len(self._ring)
            start = (end - size) % len(self._ring)
            first = min(size, len(self._ring) - start)
            samples = np.concatenate((self._ring[start:start + first], self._ring[:size - first])).copy()
            fs, has_input = self._samplerate, self._has_input
            age = None if self._updated is None else max(0.0, (time.monotonic() - self._updated) * 1000)
            errors = sorted(self._errors)
        return {"active": bool(active), "has_input": has_input, "sample_rate_hz": fs,
                "frames": frames, "window_ms": size / fs * 1000, "age_ms": age,
                "probe_playing": bool(probe_playing),
                "output": self._levels(samples[:, 0], fs),
                "microphone": self._levels(samples[:, 1], fs) if has_input else None,
                "spectrum": self._spectrum(samples[:, 1], fs) if has_input else {"frequency_hz": [], "dbfs": []},
                "transport_errors": errors}
