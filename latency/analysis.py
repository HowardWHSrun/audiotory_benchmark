"""Same-clock electrical-reference / microphone waveform delay estimation.

``recording[:, 0]`` is microphone input 1 and ``recording[:, 1]`` is an
electrical loopback on input 2. Each (start, stop) window selects the active
reference probe, in capture sample coordinates; stop is exclusive. A window
must contain a nonperiodic probe and leave ``max_lag_ms`` of captured tail.
SONIC pure tones alone generally cannot identify an unambiguous delay.

The integer-sample correlation delay is a waveform alignment estimate. It
does not establish absolute host/DAC latency, physiological latency, acoustic
onset, or calibrated SPL. One sample is the search increment, not a statement
of measurement accuracy. The microphone and reference must share an ADC clock.

Run offline with:
    python3 latency/analysis.py capture.npz manifest.json --output result.json
NPZ keys are ``recording`` (N x 2) and ``samplerate`` (scalar Hz). The manifest
has ``windows`` entries of [start, stop] or {start_sample, stop_sample}.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable

import numpy as np


def _normalized_correlations(reference: np.ndarray, microphone: np.ndarray) -> np.ndarray:
    """Pearson correlation of reference with each valid microphone window."""
    reference = reference.astype(np.float64, copy=False)
    microphone = microphone.astype(np.float64, copy=False)
    centered = reference - reference.mean()
    n = len(centered)
    size = 1 << (n + len(microphone) - 2).bit_length()
    convolution = np.fft.irfft(
        np.fft.rfft(microphone, size) * np.fft.rfft(centered[::-1], size),
        size,
    )
    numerator = convolution[n - 1 : len(microphone)]
    sums = np.concatenate(([0.0], np.cumsum(microphone)))
    squares = np.concatenate(([0.0], np.cumsum(microphone * microphone)))
    window_sums = sums[n:] - sums[:-n]
    energy = np.maximum(squares[n:] - squares[:-n] - window_sums**2 / n, 0.0)
    denominator = np.sqrt(np.dot(centered, centered) * energy)
    return np.clip(
        np.divide(numerator, denominator, out=np.zeros_like(numerator), where=denominator > 0),
        -1.0,
        1.0,
    )


def _rms(values: np.ndarray) -> float:
    centered = values - values.mean()
    return float(np.sqrt(np.mean(centered * centered)))


def _window_bounds(window: Any) -> tuple[int, int]:
    if isinstance(window, dict):
        values = (window["start_sample"], window["stop_sample"])
    else:
        values = tuple(window)
        if len(values) != 2:
            raise ValueError("Each trial window must contain exactly start and stop samples")
    if any(isinstance(v, (bool, np.bool_)) or not isinstance(v, (int, np.integer)) for v in values):
        raise ValueError("Trial window coordinates must be integer sample indices")
    return int(values[0]), int(values[1])


def _primary_lobe_bounds(correlations: np.ndarray, peak_index: int) -> tuple[int, int, bool]:
    """Bounds of the peak's contiguous same-sign lobe; stop is exclusive.

    Acoustic filtering can broaden a nonperiodic probe's correlation peak.
    Adjacent samples on that lobe are not independent delay alternatives.
    A lobe that reaches a search edge cannot be fully assessed here.
    """
    signed = correlations * np.sign(correlations[peak_index])
    left = np.flatnonzero(signed[:peak_index] <= 0)
    right = np.flatnonzero(signed[peak_index + 1 :] <= 0)
    start = int(left[-1] + 1) if len(left) else 0
    stop = int(peak_index + 1 + right[0]) if len(right) else len(correlations)
    return start, stop, bool(len(left) and len(right))


def analyze_trials(
    recording: np.ndarray,
    samplerate: float,
    windows: Iterable[Any],
    *,
    max_lag_ms: float = 100.0,
    min_rms: float = 1e-6,
    min_peak_correlation: float = 0.35,
    ambiguity_ratio: float = 0.95,
    peak_guard_samples: int = 3,
    clipping_level: float = 0.999,
) -> dict[str, Any]:
    """Estimate causal microphone delay relative to an electrical loopback.

    Correlation uses absolute magnitude so inverted microphone polarity is
    allowed. A second correlation lobe that reaches ``ambiguity_ratio`` of
    the primary rejects the trial. The primary's contiguous same-sign lobe
    between zero crossings is excluded, with +/- ``peak_guard_samples`` as
    a minimum exclusion. This avoids treating a broadened peak's shoulder as
    a separate alternative. Lobe width is diagnostic, not delay uncertainty;
    overlapping paths within a lobe are not resolved by this method. Rejected trials keep
    candidate diagnostics but have null delay values and do not enter summary
    statistics. A peak at either search boundary is unresolved and rejected:
    the true maximum may lie outside the search interval. Normalized
    floating-point full scale is +/-1. No SPL or latency qualification follows
    from these signal-quality thresholds.
    """
    samples = np.asarray(recording, dtype=np.float64)
    if samples.ndim != 2 or samples.shape[1] != 2 or not len(samples):
        raise ValueError("recording must be a nonempty N x 2 array (microphone, electrical reference)")
    if not np.isfinite(samples).all():
        raise ValueError("recording contains non-finite samples")
    if not np.isfinite(samplerate) or samplerate <= 0:
        raise ValueError("samplerate must be finite and positive")
    if not np.isfinite(max_lag_ms) or max_lag_ms <= 0:
        raise ValueError("max_lag_ms must be finite and positive")
    if not np.isfinite(min_rms) or min_rms <= 0:
        raise ValueError("min_rms must be finite and positive")
    if not 0 < min_peak_correlation <= 1 or not 0 < ambiguity_ratio <= 1:
        raise ValueError("Correlation and ambiguity thresholds must be within (0, 1]")
    if isinstance(peak_guard_samples, bool) or not isinstance(peak_guard_samples, int) or peak_guard_samples < 0:
        raise ValueError("peak_guard_samples must be a nonnegative integer")
    if not np.isfinite(clipping_level) or not 0 < clipping_level <= 1:
        raise ValueError("clipping_level must be within (0, 1]")
    bounds = [_window_bounds(window) for window in windows]
    if not bounds:
        raise ValueError("At least one reference probe window is required")
    max_lag = int(np.floor(float(samplerate) * max_lag_ms / 1000.0))
    if max_lag < 1:
        raise ValueError("max_lag_ms must span at least one sample")
    trials: list[dict[str, Any]] = []
    for trial_index, (start, stop) in enumerate(bounds):
        if start < 0 or stop > len(samples) or stop - start < 16:
            raise ValueError("Each reference window must contain at least 16 samples within the recording")
        reference = samples[start:stop, 1]
        microphone = samples[start : min(stop + max_lag, len(samples)), 0]
        reasons: list[str] = []
        reference_rms = _rms(reference)
        microphone_rms = _rms(microphone)
        reference_clipped = int(np.count_nonzero(np.abs(reference) >= clipping_level))
        microphone_clipped = int(np.count_nonzero(np.abs(microphone) >= clipping_level))
        if reference_rms < min_rms:
            reasons.append("reference_missing_or_too_quiet")
        if microphone_rms < min_rms:
            reasons.append("microphone_missing_or_too_quiet")
        if reference_clipped:
            reasons.append("reference_clipping")
        if microphone_clipped:
            reasons.append("microphone_clipping")
        if stop + max_lag > len(samples):
            reasons.append("incomplete_search_window")

        trial: dict[str, Any] = {
            "trial_index": trial_index,
            "start_sample": start,
            "stop_sample": stop,
            "reference_rms_fs": reference_rms,
            "microphone_rms_fs": microphone_rms,
            "reference_clipped_samples": reference_clipped,
            "microphone_clipped_samples": microphone_clipped,
            "accepted": False,
            "reasons": reasons,
            "delay_samples": None,
            "delay_ms": None,
            "candidate_delay_samples": None,
            "candidate_delay_ms": None,
            "peak_correlation": None,
            "peak_correlation_abs": None,
            "secondary_peak_ratio": None,
            "primary_lobe_start_lag_samples": None,
            "primary_lobe_stop_lag_samples_exclusive": None,
            "primary_lobe_width_samples": None,
            "primary_lobe_width_ms": None,
            "primary_lobe_bounded_by_zero_crossings": None,
            "peak_at_search_boundary": None,
        }
        # Do not manufacture a correlation estimate from absent/constant inputs.
        if reference_rms >= min_rms and microphone_rms >= min_rms:
            correlations = _normalized_correlations(reference, microphone)
            magnitudes = np.abs(correlations)
            peak_index = int(np.argmax(magnitudes))
            peak = float(magnitudes[peak_index])
            lobe_start, lobe_stop, lobe_bounded = _primary_lobe_bounds(correlations, peak_index)
            outside = np.ones(len(magnitudes), dtype=bool)
            exclusion_start = min(lobe_start, max(0, peak_index - peak_guard_samples))
            exclusion_stop = max(lobe_stop, min(len(magnitudes), peak_index + peak_guard_samples + 1))
            outside[exclusion_start:exclusion_stop] = False
            secondary = float(np.max(magnitudes[outside])) if outside.any() else 0.0
            ratio = secondary / peak if peak > 0 else 1.0
            trial.update(
                candidate_delay_samples=peak_index,
                candidate_delay_ms=peak_index * 1000.0 / samplerate,
                peak_correlation=float(correlations[peak_index]),
                peak_correlation_abs=peak,
                secondary_peak_ratio=ratio,
                primary_lobe_start_lag_samples=lobe_start,
                primary_lobe_stop_lag_samples_exclusive=lobe_stop,
                primary_lobe_width_samples=lobe_stop - lobe_start,
                primary_lobe_width_ms=(lobe_stop - lobe_start) * 1000.0 / samplerate,
                primary_lobe_bounded_by_zero_crossings=lobe_bounded,
                peak_at_search_boundary=peak_index in (0, len(magnitudes) - 1),
            )
            if peak < min_peak_correlation:
                reasons.append("weak_correlation")
            if ratio >= ambiguity_ratio:
                reasons.append("ambiguous_peak_use_nonperiodic_probe")
            if not lobe_bounded:
                reasons.append("primary_lobe_unresolved_at_search_boundary")
            if trial["peak_at_search_boundary"]:
                reasons.append("boundary_peak_unresolved")
            if not reasons:
                trial.update(accepted=True, delay_samples=peak_index, delay_ms=trial["candidate_delay_ms"])
        trials.append(trial)

    accepted = [trial for trial in trials if trial["accepted"]]
    summary: dict[str, Any] = {
        "total_trials": len(trials),
        "accepted_trials": len(accepted),
        "rejected_trials": len(trials) - len(accepted),
        "median_delay_ms": None,
        "p05_delay_ms": None,
        "p95_delay_ms": None,
        "jitter_p95_minus_p05_ms": None,
        "min_delay_ms": None,
        "max_delay_ms": None,
        "std_delay_ms": None,
        "delay_trend_ms_per_minute": None,
    }
    if accepted:
        delays = np.asarray([trial["delay_ms"] for trial in accepted])
        p05, p95 = np.percentile(delays, [5, 95])
        summary.update(
            median_delay_ms=float(np.median(delays)),
            p05_delay_ms=float(p05),
            p95_delay_ms=float(p95),
            jitter_p95_minus_p05_ms=float(p95 - p05),
            min_delay_ms=float(delays.min()),
            max_delay_ms=float(delays.max()),
            std_delay_ms=float(delays.std()),
        )
        times = np.asarray([trial["start_sample"] / samplerate / 60.0 for trial in accepted])
        if len(accepted) >= 3 and np.ptp(times) > 0:
            centered_times = times - times.mean()
            summary["delay_trend_ms_per_minute"] = float(
                np.dot(centered_times, delays - delays.mean()) / np.dot(centered_times, centered_times)
            )
    return {
        "method": "same_adc_clock_normalized_waveform_cross_correlation",
        "samplerate_hz": float(samplerate),
        "sample_interval_ms": 1000.0 / samplerate,
        "search_lag_samples": [0, max_lag],
        "max_lag_ms": max_lag * 1000.0 / samplerate,
        "thresholds": {
            "min_rms_fs": min_rms,
            "min_peak_correlation": min_peak_correlation,
            "ambiguity_ratio": ambiguity_ratio,
            "peak_guard_samples": peak_guard_samples,
            "ambiguity_exclusion": "primary_same_sign_lobe_between_zero_crossings_with_minimum_sample_guard",
            "clipping_level_fs": clipping_level,
        },
        "interpretation": (
            "Waveform delay from electrical reference input 2 to microphone input 1. "
            "Includes loudspeaker, acoustic travel and microphone path relative to the reference path; "
            "does not measure common host/DAC latency or establish acoustic onset. "
            "Sample interval is the search increment, not calibrated measurement accuracy."
        ),
        "summary": summary,
        "trials": trials,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("capture", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-lag-ms", type=float, default=100.0)
    args = parser.parse_args()
    with np.load(args.capture, allow_pickle=False) as capture:
        recording = capture["recording"]
        samplerate = float(capture["samplerate"].item())
    manifest = json.loads(args.manifest.read_text())
    result = analyze_trials(recording, samplerate, manifest["windows"], max_lag_ms=args.max_lag_ms)
    rendered = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.write_text(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
