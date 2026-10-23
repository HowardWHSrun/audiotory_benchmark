"""Offline relative H1 response from saved native microphone/chirp captures.

No audio backend is imported and no sound is played. Results describe the
whole recorded chain at its existing microphone position, not the speaker alone.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .transport import assess_timestamps

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUNS = ("20261023-155401", "20261023-155500-roundtrip-repeat")
THRESHOLDS = {"minimum_coherence": .9, "minimum_source_band_power_relative_db": -30,
              "minimum_coherent_response_above_baseline_db": 10,
              "minimum_repeated_trials": 3, "clipping_level_fs": .999}
ANCHORS = (100, 200, 500, 1000, 2000, 4000, 8000, 12000, 16000, 18000, 20000)


def _sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _db_power(value):
    return float(10 * np.log10(value)) if value > 0 else None


def frequency_centers():
    grid = 100 * 2 ** (np.arange(93) / 12)
    return sorted(set(float(value) for value in grid if value <= 20000) | set(ANCHORS))


def analyze_sweeps(source, microphone, plan, samplerate, transport, centers=None):
    """Estimate one run's H1 and mask unsupported frequency bands.

    H1=sum(Y*conj(X))/sum(abs(X)**2). All spectra use rectangular 0.5-second
    windows from 0.1 seconds before each chirp onset through 0.4 seconds after.
    Source and delayed response occupy the same flat weighting region. A full
    Hann would weight the delayed chirp differently and is deliberately avoided.
    """
    source, microphone = np.asarray(source), np.asarray(microphone)
    if source.ndim != 1 or microphone.ndim != 1 or not len(source) or len(source) != len(microphone):
        raise ValueError("source and microphone must be equal-length nonempty mono arrays")
    if not np.isfinite(source).all() or not np.isfinite(microphone).all():
        raise ValueError("source and microphone must be finite")
    if not np.isfinite(samplerate) or samplerate < 48000:
        raise ValueError("a finite sample rate of at least 48000 Hz is required")
    trials = plan.get("trials", [])
    if len(trials) < THRESHOLDS["minimum_repeated_trials"]:
        raise ValueError("at least three repeated chirps are required for coherence screening")
    size, pre = round(.5 * samplerate), round(.1 * samplerate)
    source_spectra, microphone_spectra = [], []
    for trial in trials:
        onset = trial["output_start"]
        if isinstance(onset, bool) or not isinstance(onset, (int, np.integer)):
            raise ValueError("chirp onset sample positions must be integers")
        a, b = int(onset) - pre, int(onset) - pre + size
        if a < 0 or b > len(source):
            raise ValueError("complete padded 0.5-second chirp windows are required")
        source_spectra.append(np.fft.rfft(source[a:b].astype(np.float64)))
        microphone_spectra.append(np.fft.rfft(microphone[a:b].astype(np.float64)))
    baseline_start, baseline_stop = round(.1 * samplerate), round(.6 * samplerate)
    if baseline_stop > min(trial["output_start"] for trial in trials) or np.max(np.abs(source[baseline_start:baseline_stop])) > 1e-10:
        raise ValueError("the 0.1-0.6-second baseline must be before playback and source-silent")
    baseline = abs(np.fft.rfft(microphone[baseline_start:baseline_stop].astype(np.float64))) ** 2
    X, Y = np.asarray(source_spectra), np.asarray(microphone_spectra)
    xx, yy = np.mean(abs(X) ** 2, axis=0), np.mean(abs(Y) ** 2, axis=0)
    yx = np.mean(Y * X.conj(), axis=0)
    h1 = np.divide(yx, xx, out=np.zeros_like(yx), where=xx > 0)
    coherence = np.clip(np.divide(abs(yx) ** 2, xx * yy, out=np.zeros_like(xx), where=xx * yy > 0), 0, 1)
    coherent_power = np.divide(abs(yx) ** 2, xx, out=np.zeros_like(xx), where=xx > 0)
    frequencies = np.fft.rfftfreq(size, 1 / samplerate)
    requested = frequency_centers() if centers is None else sorted(set(float(f) for f in centers) | {2000.0})
    bands = []
    for center in requested:
        if not 0 < center < samplerate / 2:
            raise ValueError("analysis centers must be positive and below Nyquist")
        lower, upper = center / 2 ** (1 / 24), center * 2 ** (1 / 24)
        mask = (frequencies >= lower) & (frequencies <= upper)
        excitation = float(np.mean(xx[mask])) if np.any(mask) else 0.0
        total_excitation = float(np.sum(xx[mask]))
        gain = float(np.sqrt(np.sum(abs(h1[mask]) ** 2 * xx[mask]) / total_excitation)) if total_excitation else None
        quality_coherence = float(np.sum(coherence[mask] * xx[mask]) / total_excitation) if total_excitation else 0.0
        noise_power = float(np.sum(baseline[mask]))
        response_power = float(np.sum(coherent_power[mask]))
        above_baseline = _db_power(response_power / max(noise_power, 1e-30)) if response_power else None
        bands.append({"frequency_hz": center, "band_edges_hz": [lower, upper],
                      "fft_bins": int(np.count_nonzero(mask)), "source_mean_bin_power": excitation,
                      "source_weighted_coherence": quality_coherence,
                      "coherent_response_above_baseline_db": above_baseline,
                      "h1_rms_magnitude_diagnostic": gain,
                      "source_band_power_relative_db": None,
                      "accepted": False, "rejection_reasons": [],
                      "relative_to_2khz_db": None})
    strongest = max(band["source_mean_bin_power"] for band in bands)
    valid_transport = (isinstance(transport, dict) and transport.get("valid_transport") is True
                       and transport.get("transport_errors") == [])
    microphone_clipped = int(np.count_nonzero(abs(microphone) >= THRESHOLDS["clipping_level_fs"]))
    source_clipped = int(np.count_nonzero(abs(source) >= THRESHOLDS["clipping_level_fs"]))
    for band in bands:
        power = band["source_mean_bin_power"]
        band["source_band_power_relative_db"] = _db_power(power / strongest) if power > 0 and strongest > 0 else None
        reasons = band["rejection_reasons"]
        if not valid_transport:
            reasons.append("transport_invalid_or_unverified")
        if microphone_clipped or source_clipped:
            reasons.append("source_or_microphone_clipping")
        if band["fft_bins"] < 2:
            reasons.append("insufficient_fft_bins")
        if band["source_band_power_relative_db"] is None or band["source_band_power_relative_db"] < THRESHOLDS["minimum_source_band_power_relative_db"]:
            reasons.append("weak_source_excitation")
        if band["source_weighted_coherence"] < THRESHOLDS["minimum_coherence"]:
            reasons.append("low_repeat_coherence")
        if band["coherent_response_above_baseline_db"] is None or band["coherent_response_above_baseline_db"] < THRESHOLDS["minimum_coherent_response_above_baseline_db"]:
            reasons.append("response_not_above_baseline")
        band["accepted"] = not reasons
    reference = next(band for band in bands if band["frequency_hz"] == 2000)
    if not reference["accepted"]:
        for band in bands:
            if band["accepted"]:
                band["rejection_reasons"].append("2khz_reference_unqualified")
                band["accepted"] = False
    for band in bands:
        if band["accepted"]:
            band["relative_to_2khz_db"] = float(20 * np.log10(
                band["h1_rms_magnitude_diagnostic"] / reference["h1_rms_magnitude_diagnostic"]))
    return {"method": "per_run_H1_cross_spectral_relative_magnitude_screen",
            "samplerate_hz": float(samplerate), "chirps_used": len(trials),
            "window_samples": size, "window_seconds": .5,
            "window_relative_to_chirp_onset_seconds": [-.1, .4],
            "window_shape": "rectangular; no full-window Hann or delay-dependent weighting",
            "baseline_interval_seconds": [.1, .6],
            "fft_bin_width_hz": float(samplerate / size),
            "band_definition": "1/12-octave bands; source-power-weighted RMS H1 magnitude and coherence",
            "source_strength_comparison": "mean source FFT-bin power in each band, avoiding bandwidth-dependent integrated-power bias",
            "thresholds": dict(THRESHOLDS),
            "threshold_role": "local analysis screening choices, not loudspeaker acceptance limits",
            "transport_valid": valid_transport,
            "source_clipped_samples": source_clipped,
            "microphone_clipped_samples": microphone_clipped,
            "bands": bands,
            "accepted_band_count": sum(band["accepted"] for band in bands),
            "reference_frequency_hz": 2000,
            "acoustic_spl_calibrated": False, "microphone_frequency_correction_applied": False,
            "isolated_loudspeaker_response": False, "thd_measured": False,
            "measured_delay_ms": None}


def analyze_saved_run(folder):
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    source = np.load(folder / "output_float32.npy", allow_pickle=False)
    expected_hash = manifest.get("output_sha256")
    if not expected_hash or hashlib.sha256(source.tobytes()).hexdigest() != expected_hash:
        raise ValueError("saved source hash is missing or does not match")
    if manifest.get("native_playback_and_capture_performed") is not True:
        raise ValueError("saved native full-duplex acquisition is unverified")
    with np.load(folder / "capture.npz", allow_pickle=False) as stored:
        recording, samplerate = stored["recording"], float(stored["samplerate"].item())
        timestamps = stored["callback_timestamps"] if "callback_timestamps" in stored else []
    if samplerate != manifest.get("sample_rate_hz") or recording.ndim != 2 or recording.shape[1] != 2:
        raise ValueError("saved sample rate or input format does not match its manifest")
    if recording.shape[0] != len(source):
        raise ValueError("saved source and capture lengths differ")
    plan = manifest.get("stimulus", {})
    if plan.get("kind") != "timing_probe" or not plan.get("trials"):
        raise ValueError("saved timing-probe plan is required")
    transport = dict(manifest.get("transport") or {})
    errors = list(transport.get("transport_errors") or [])
    if transport.get("valid_transport") is not True or "transport_errors" not in transport:
        errors.append("saved_transport_invalid_or_unverified")
    if transport.get("captured_frames") != len(source):
        errors.append("saved_capture_frame_count_mismatch")
    raw_transport = assess_timestamps(timestamps, samplerate)
    errors.extend(raw_transport["errors"])
    transport.update(valid_transport=not errors, transport_errors=sorted(set(errors)))
    result = analyze_sweeps(source, recording[:, 0], plan, samplerate, transport)
    result.update(local_run=folder.name, source_float32_array_bytes_sha256=expected_hash,
                  source_npy_file_sha256=_sha(folder / "output_float32.npy"),
                  capture_npz_sha256=_sha(folder / "capture.npz"),
                  manifest_sha256=_sha(folder / "manifest.json"),
                  captured_frames=len(source), native_acquisition_metadata_verified=True,
                  raw_callback_timestamps_rechecked=True,
                  transport_errors=transport["transport_errors"])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=Path, help="Saved chirp run; repeat for independent runs")
    parser.add_argument("--output", type=Path, default=ROOT / "docs/verification/2026-10-23_Sweep_Relative_Response.json")
    args = parser.parse_args()
    try:
        folders = args.run or [ROOT / ".work/latency/runs" / name for name in DEFAULT_RUNS]
        runs = [analyze_saved_run(folder) for folder in folders]
        combined = []
        for index, first in enumerate(runs[0]["bands"]):
            rows = [run["bands"][index] for run in runs]
            supported = all(row["accepted"] for row in rows)
            levels = [row["relative_to_2khz_db"] for row in rows] if supported else []
            combined.append({"frequency_hz": first["frequency_hz"],
                             "accepted_in_all_runs": supported,
                             "median_relative_to_2khz_db": float(np.median(levels)) if levels else None,
                             "run_to_run_range_db": float(np.ptp(levels)) if levels else None})
        report = {"date_local": "2026-10-23", "timezone": "America/Chicago",
                  "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                  "purpose": "offline whole-chain relative response screen from two existing nonperiodic sweep captures",
                  "new_sound_played": False, "new_audio_recorded": False,
                  "scope": "recorded Audient-to-speaker-to-Earthworks path at the saved position; not isolated speaker response",
                  "runs": runs, "combined_magnitude_bands": combined,
                  "combination_rule": "Each run has its own complex H1. Combine qualified relative magnitude levels only; never average complex spectra across streams with different delays.",
                  "acoustic_spl_calibrated": False, "microphone_frequency_correction_applied": False,
                  "thd_measured": False, "raw_room_audio_published": False,
                  "limitations": [
                      "Short log-chirp end ramps severely weaken excitation near 20 kHz. Unsupported endpoint bands remain null; no complete 100 Hz-20 kHz response is claimed.",
                      "No source excitation above 20 kHz is used; these sweeps cannot qualify the high SONIC frequencies.",
                      "Relative magnitudes include interface, speaker, room reflections and uncorrected microphone response at this geometry.",
                      "Coherence and baseline masks are local screening rules. Synchronous room noise, time-varying noise or response outside the window can still bias an estimate.",
                      "The finite window assumes useful response energy decays by 0.4 seconds after onset; long reverberation can be truncated.",
                      "This is a linear-response screen at one digital peak. It does not measure THD, compression, calibrated SPL, acoustic onset or 10 ms pip fidelity.",
                  ],
                  "primary_references": [
                      "https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html",
                      "https://earthworksaudio.com/measurement-microphones/m50/",
                  ]}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(f"Saved offline analysis in {args.output.resolve()}")
        for row in combined:
            if row["frequency_hz"] in ANCHORS:
                print(json.dumps(row))
    except (ValueError, OSError, KeyError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
