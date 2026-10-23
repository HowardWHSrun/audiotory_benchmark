"""Offline SONIC E14 pip-frequency diagnostics; never opens audio hardware.

This is a descriptive pickup check, not an SPL or acoustic-bandwidth calibration.
The exact source and same shuffled sequence were captured in two stream starts.
Run ``python -m latency.pip_response`` from the project, or pass existing folders
with repeated ``--run PATH`` arguments. Results are written beside saved captures.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .transport import assess_timestamps

FS = 96000
ROOT = Path(__file__).resolve().parents[1]
WINDOW_SAMPLES = 576  # Six milliseconds, source-relative 2--8 ms.
ALIGNMENTS_MS = (37, 38, 39)
HARMONIC_EXCLUSION_HZ = 334
DEFAULT_RUNS = (
    ".work/latency/runs/20261023-155615-sonic-e14-full",
    ".work/latency/runs/20261023-160447-sonic-e14-full",
)


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db(value):
    return float(20 * np.log10(max(float(value), 1e-20)))


def interference_mask(sequence, target):
    return np.array([
        any(abs(harmonic * source_frequency - target) < HARMONIC_EXCLUSION_HZ
            for harmonic in range(1, 7))
        for source_frequency in sequence
    ])


def neighbour_clean_mask(sequence, target, *, include_current=False):
    # Exclude the target and nearby first-through-sixth harmonic relationships,
    # at the current event and two neighbours in each direction. This does not
    # remove all possible ringing, nonlinear distortion or electrical leakage.
    interfering = interference_mask(sequence, target)
    controls = np.ones(len(sequence), dtype=bool)
    for shift in range(-2, 3):
        if shift < 0:
            controls[-shift:] &= ~interfering[:shift]
        elif shift > 0:
            controls[:-shift] &= ~interfering[shift:]
        else:
            if include_current:
                controls &= ~interfering
    return controls


def controls_for_frequency(sequence, target):
    return neighbour_clean_mask(sequence, target, include_current=True)


def projection_kernels(frequencies):
    window = np.hanning(WINDOW_SAMPLES)
    time = np.arange(WINDOW_SAMPLES) / FS
    return np.array([
        2 * window * np.exp(-2j * np.pi * frequency * time) / window.sum()
        for frequency in frequencies
    ])


def group_metrics(complex_values):
    amplitude = abs(complex_values) / np.sqrt(2)
    denominator = float(np.sqrt(np.mean(abs(complex_values) ** 2)))
    return {
        "pip_count": len(amplitude),
        "median_fundamental_rms_dbfs": db(np.median(amplitude)),
        "p05_fundamental_rms_dbfs": db(np.percentile(amplitude, 5)),
        "p95_fundamental_rms_dbfs": db(np.percentile(amplitude, 95)),
        "complex_phase_coherence": float(abs(np.mean(complex_values)) / denominator) if denominator else 0.0,
    }


def analyze_run(folder):
    folder = Path(folder).resolve()
    manifest = json.loads((folder / "manifest.json").read_text())
    plan = json.loads((folder / "stimulus-plan.json").read_text())
    source = np.load(folder / "output_float32.npy", allow_pickle=False)
    with np.load(folder / "capture.npz", allow_pickle=False) as capture:
        recording = capture["recording"]
        sample_rate = int(capture["samplerate"].item())
        timestamps = capture["callback_timestamps"]
    if sample_rate != FS or manifest["sample_rate_hz"] != FS:
        raise ValueError("Expected the saved 96-kHz acquisition")
    if recording.ndim != 2 or recording.shape[1] != 2:
        raise ValueError("Expected two recorded Audient input channels")
    if (source.ndim != 1 or len(source) != len(recording) or
            not np.isfinite(recording).all() or not np.isfinite(source).all()):
        raise ValueError("Mismatched source/capture lengths or nonfinite capture")
    if (manifest.get("native_playback_and_capture_performed") is not True or
            manifest["transport"]["valid_transport"] is not True or
            manifest["transport"].get("transport_errors") != [] or
            manifest["transport"].get("captured_frames") != len(recording)):
        raise ValueError("Saved transport screening did not pass")
    transport_check = assess_timestamps(timestamps, FS)
    if transport_check["errors"]:
        raise ValueError("Saved callback timestamps/status failed the offline transport screen")
    if hashlib.sha256(source.tobytes()).hexdigest() != manifest["output_float32_sha256"]:
        raise ValueError("Source sample bytes do not match the manifest")
    if plan["tone_duration_samples"] != 960 or len(plan["events"]) != 8400:
        raise ValueError("Expected the saved 8,400-pip E14 block")

    sequence = np.array(plan["sequence_hz"])
    frequencies = np.array(sorted(set(sequence)))
    if (len(frequencies) != 14 or len(sequence) != 8400 or
            any(np.count_nonzero(sequence == frequency) != 600 for frequency in frequencies) or
            plan["sample_rate_hz"] != FS or
            [event["frequency_hz"] for event in plan["events"]] != sequence.tolist() or
            any(event["output_start"] != index * 960 or event["output_stop"] != (index + 1) * 960
                for index, event in enumerate(plan["events"]))):
        raise ValueError("Saved E14 plan is not a contiguous balanced 600-per-frequency block")
    starts = np.array([event["output_start"] for event in plan["events"]])
    starts += manifest["plan_event_to_output_offset_samples"]
    microphone = recording[:, 0]
    input2 = recording[:, 1]
    sample_offsets = np.arange(WINDOW_SAMPLES)
    kernels = projection_kernels(frequencies)
    # For an isolated sinusoid, abs(complex_peak)/sqrt(2) estimates sine RMS.
    baseline_starts = np.arange(12000, 84000 - WINDOW_SAMPLES, WINDOW_SAMPLES)
    baseline = microphone[baseline_starts[:, None] + sample_offsets]
    baseline_complex = baseline @ kernels.T
    baseline_rms = np.sqrt(np.mean(abs(baseline_complex) ** 2, axis=0) / 2)
    input2_baseline = input2[baseline_starts[:, None] + sample_offsets] @ kernels.T
    input2_baseline_rms = np.sqrt(np.mean(abs(input2_baseline) ** 2, axis=0) / 2)
    source_segments = source[starts[:, None] + 192 + sample_offsets]
    source_complex = source_segments @ kernels.T
    by_alignment = {}
    for alignment_ms in ALIGNMENTS_MS:
        lag = round(alignment_ms * FS / 1000)
        segments = microphone[starts[:, None] + lag + 192 + sample_offsets]
        complex_peak = segments @ kernels.T
        input2_complex = input2[starts[:, None] + lag + 192 + sample_offsets] @ kernels.T
        rows = []
        for column, frequency in enumerate(frequencies):
            own = sequence == frequency
            amplitude = abs(complex_peak[own, column]) / np.sqrt(2)
            source_amplitude = abs(source_complex[own, column]) / np.sqrt(2)
            controls = controls_for_frequency(sequence, frequency)
            off_amplitude = abs(complex_peak[controls, column]) / np.sqrt(2)
            clean = own & neighbour_clean_mask(sequence, frequency)
            if not clean.any() or not controls.any():
                raise ValueError("No neighbour-controlled target/control events remain")
            clean_metrics = group_metrics(complex_peak[clean, column])
            clean_metrics.update(
                median_above_preblock_db=clean_metrics["median_fundamental_rms_dbfs"] - db(baseline_rms[column]),
                median_over_inblock_control_db=clean_metrics["median_fundamental_rms_dbfs"] - db(np.median(off_amplitude)),
            )
            comparator = group_metrics(input2_complex[own, column])
            comparator.update(
                preblock_matched_frequency_rms_dbfs=db(input2_baseline_rms[column]),
                median_above_preblock_db=comparator["median_fundamental_rms_dbfs"] - db(input2_baseline_rms[column]),
                input1_over_input2_median_db=db(np.median(amplitude)) - comparator["median_fundamental_rms_dbfs"],
                neighbour_excluded=group_metrics(input2_complex[clean, column]),
            )
            rows.append({
                "frequency_hz": int(frequency),
                "pip_count": int(own.sum()),
                "median_fundamental_rms_dbfs": db(np.median(amplitude)),
                "p05_fundamental_rms_dbfs": db(np.percentile(amplitude, 5)),
                "p95_fundamental_rms_dbfs": db(np.percentile(amplitude, 95)),
                "median_source_fundamental_rms_dbfs": db(np.median(source_amplitude)),
                "median_mic_over_source_db": db(np.median(amplitude) / np.median(source_amplitude)),
                "preblock_matched_frequency_rms_dbfs": db(baseline_rms[column]),
                "median_above_preblock_db": db(np.median(amplitude) / baseline_rms[column]),
                "inblock_control_count": int(controls.sum()),
                "inblock_control_median_rms_dbfs": db(np.median(off_amplitude)),
                "median_over_inblock_control_db": db(np.median(amplitude) / np.median(off_amplitude)),
                "complex_phase_coherence": group_metrics(complex_peak[own, column])["complex_phase_coherence"],
                "coherently_averaged_fundamental_rms_dbfs": db(
                    abs(np.mean(complex_peak[own, column])) / np.sqrt(2)),
                "neighbour_excluded": clean_metrics,
                "simultaneous_input2_comparator": comparator,
            })
        by_alignment[str(alignment_ms)] = rows
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Private preliminary 10-ms SONIC pip fundamental-pickup diagnostics; not a calibrated response or ultrasonic qualification.",
        "run_id": folder.name,
        "sample_rate_hz": FS,
        "method": {
            "central_window_seconds": [0.002, 0.008],
            "window_samples": WINDOW_SAMPLES,
            "weighting": "Hann; complex single-frequency projection. RMS = abs(2*sum(mic*w*exp(-j*2*pi*f*t))/sum(w))/sqrt(2).",
            "fixed_alignment_ms": 38,
            "sensitivity_alignments_ms": list(ALIGNMENTS_MS),
            "preblock_baseline": "Nonoverlapping 6-ms windows from 0.125 to approximately 0.875 s before the first source pip. Matched-frequency RMS = sqrt(mean(abs(complex_peak)^2)/2).",
            "inblock_control": "Other-pip windows excluding current and +/-2 neighbouring target-frequency events or first-through-sixth harmonic relationships within 334 Hz. This reduces, but does not remove, leakage/distortion contamination.",
            "neighbour_excluded_target_group": "A second target estimate removes target events having +/-1 or +/-2 neighbours at the same frequency or with first-through-sixth harmonic relationships within 334 Hz. This includes excluding 10.5-kHz neighbours for the 20.9-kHz estimate because their second harmonic is 21 kHz. The primary all-target estimate still contains all 600 pips.",
            "input2_comparator": "Same-frequency, same-event-window projection of simultaneously recorded input 2. Its wiring/gain are not independently qualified. This is a feedthrough comparator, not an acoustic-isolation control, electrical timing reference or noise correction for input 1.",
            "statistic_note": "Contrasts above baseline/control are amplitude ratios in dB, not noise-subtracted calibrated SNR. All source frequencies have 600 pips with the same -24-dBFS peak.",
        },
        "transport_valid": manifest["transport"]["valid_transport"],
        "callback_status_bits_observed": np.unique(timestamps[:, 4]).astype(int).tolist(),
        "clipped_samples_at_0_999_fs": int(np.count_nonzero(abs(microphone) >= 0.999)),
        "frequency_results_at_38ms": by_alignment["38"],
        "sensitivity_results": by_alignment,
        "limitations": [
            "Continuous 10-ms pips do not isolate steady tones. Window leakage, transducer filtering/ringing, adjacent pips and harmonics can contribute.",
            "Fixed approximate 37--39-ms alignment is for level sensitivity checks. Periodic-carrier ambiguity prevents using it as a delay measurement.",
            "No serial-specific microphone calibration or SPL/gain calibration was applied. Detection does not establish flatness, fidelity or acoustic high-frequency qualification.",
            "No speaker-disconnected or microphone-blocked isolation control was recorded. Electrical feedthrough was not excluded.",
        ],
        "raw_audio_publication_authorized": False,
        "source_float32_sample_bytes_sha256": manifest["output_float32_sha256"],
        "hashes": {name: file_hash(folder / name) for name in (
            "capture.npz", "output_float32.npy", "manifest.json", "stimulus-plan.json")},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="append", type=Path,
                        help="Existing saved run. Repeat to analyze multiple runs.")
    args = parser.parse_args()
    for folder in args.run or (ROOT / path for path in DEFAULT_RUNS):
        result = analyze_run(folder)
        output = folder / "pip-frequency-preliminary.json"
        output.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        print(output)


if __name__ == "__main__":
    main()
