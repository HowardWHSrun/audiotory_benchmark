"""Separate audio-buffer integrity from uncalibrated host-clock timestamps."""
import numpy as np


def assess_timestamps(log, samplerate):
    log = np.asarray(log, dtype=float)
    errors, diagnostics = [], {}
    if log.ndim != 2 or log.shape[1] != 5 or len(log) < 2:
        return {"errors": ["missing_callback_timestamps"], "clock_diagnostics": diagnostics}
    if not np.isfinite(log).all():
        return {"errors": ["non_finite_callback_log"], "clock_diagnostics": diagnostics}
    if np.any(log[:, 3] <= 0) or np.any(np.diff(log[:, 0]) != log[:-1, 3]):
        errors.append("noncontiguous_callback_array_positions")
    if np.any(log[:, 4] != 0):
        errors.append("portaudio_callback_status_flag")
    sample_seconds = (log[:, 0] - log[0, 0]) / samplerate
    centered = sample_seconds - sample_seconds.mean()
    for column, name in ((1, "input"), (2, "output")):
        times = log[:, column]
        if np.any(times <= 0) or np.any(np.diff(times) <= 0):
            errors.append(f"invalid_{name}_timestamps")
            continue
        elapsed = times - times[0]
        slope = float(np.dot(centered, elapsed - elapsed.mean()) / np.dot(centered, centered))
        fitted = elapsed.mean() + slope * centered
        residual_samples = (elapsed - fitted) * samplerate
        diagnostics[name] = {"host_time_vs_nominal_sample_time_ppm": (slope - 1) * 1e6,
            "affine_residual_min_samples": float(residual_samples.min()),
            "affine_residual_max_samples": float(residual_samples.max()),
            "max_increment_residual_samples": float(np.max(np.abs(np.diff(times) * samplerate - log[:-1, 3])))}
        # PortAudio CoreAudio ADC/DAC stamps share a host-clock conversion.
        # Small common corrections are not evidence of missing audio samples.
        # Large unexplained jumps still fail this provisional transport screen.
        if np.max(np.abs(residual_samples)) > samplerate * 0.001:
            errors.append(f"large_unexplained_{name}_timestamp_jump")
    diagnostics["adc_dac_offset_range_samples"] = float(np.ptp((log[:, 2] - log[:, 1]) * samplerate))
    diagnostics["host_clock_independently_calibrated"] = False
    diagnostics["interpretation"] = "Timestamp affine fits diagnose host-time mapping; they do not qualify its accuracy. Primary microphone/reference alignment uses simultaneous input sample positions."
    return {"errors": errors, "clock_diagnostics": diagnostics}
