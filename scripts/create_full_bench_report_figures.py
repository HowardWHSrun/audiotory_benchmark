#!/usr/bin/env python3
"""Recreate scientific report figures from saved captures; never access audio hardware.

Raw room audio stays in ignored .work/. Figures display explicitly identified
measured excerpts and derived metrics, with source hashes in a JSON manifest.
Run with .work/latency-venv/bin/python scripts/create_full_bench_report_figures.py.
The LaTeX project directory must already exist; this script creates only images/.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from latency.analysis import _normalized_correlations, _primary_lobe_bounds

FS = 96000
RUN_IDS = ("20261023-155401", "20261023-155500-roundtrip-repeat")
SONIC_ID = "20261023-155615-sonic-e14-full"
DEFAULT_OUTPUT = ROOT / "output/pdf/2026-10-23/Full_Bench_Analysis_Report/images"
COLORS = ("#24608A", "#B65B2F")


def digest(path):
    checksum = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def source_record(path):
    return {"path": relative(path), "sha256": digest(path)}


def save_figure(fig, output, name):
    fig.savefig(output / f"{name}.png", dpi=300, facecolor="white")
    fig.savefig(output / f"{name}.pdf", facecolor="white",
                metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def timing_summary(output, verification):
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.8), sharex=True,
                             gridspec_kw={"height_ratios": [1.7, 1]}, layout="constrained")
    metadata, all_delays = [], []
    for index, run_id in enumerate(RUN_IDS):
        folder = ROOT / ".work/latency/runs" / run_id
        analysis_path = folder / "roundtrip-analysis.json"
        result = json.loads(analysis_path.read_text())
        published = next(run for run in verification["runs"] if run["run_id"] == run_id)
        trials = result["trials"]
        if len(trials) != 20 or not result["usable_measurement"] or not all(t["accepted"] for t in trials):
            raise ValueError(f"Expected twenty accepted measured trials: {run_id}")
        delays = np.array([t["delay_samples"] for t in trials], dtype=int)
        if delays.tolist() != [t["delay_samples"] for t in published["trials"]]:
            raise ValueError(f"Canonical and sanitized timing records disagree: {run_id}")
        x = np.arange(1, 21) + index * 20
        delay_ms = delays * 1000 / FS
        label = f"Run {index + 1}: median {np.median(delay_ms):.3f} ms"
        axes[0].plot(x, delay_ms, "o-", color=COLORS[index], lw=1, ms=4, label=label)
        axes[0].hlines(np.median(delay_ms), x[0], x[-1], color=COLORS[index], ls="--", lw=1)
        axes[1].plot(x, [t["peak_correlation_abs"] for t in trials], "o-",
                     color=COLORS[index], lw=1, ms=3.5)
        all_delays.extend(delays.tolist())
        metadata.append({"run_id": run_id, "analysis": source_record(analysis_path),
                         "capture": source_record(folder / "capture.npz"),
                         "source": source_record(folder / "output_float32.npy"),
                         "delay_samples": delays.tolist(), "display_trial_numbers": x.tolist()})
    for axis in axes:
        axis.axvline(20.5, color="0.65", lw=1)
        axis.grid(axis="y", alpha=.23)
        axis.set_xlim(.3, 40.7)
    axes[0].set_ylim(38.20, 38.425)
    axes[0].set_ylabel("Waveform roundtrip (ms)")
    axes[0].legend(loc="lower right", frameon=False, fontsize=9)
    axes[0].set_title("Forty timing probes across two separately started streams", loc="left", weight="bold")
    axes[1].axhline(.35, color="0.35", ls="--", lw=1, label="Strength threshold 0.35")
    axes[1].set_ylim(.32, .49)
    axes[1].set_ylabel("Absolute peak\ncorrelation")
    axes[1].set_xlabel("Probe number: 1–20 in run 1; 21–40 in run 2")
    axes[1].legend(loc="lower right", frameon=False, fontsize=8)
    axes[1].xaxis.set_major_locator(MaxNLocator(integer=True, nbins=9))
    fig.get_layout_engine().set(rect=(0, .075, 1, .925))
    fig.text(.013, .018, "One sample = 10.4 µs search step; neither sample repeatability nor axis precision establishes absolute timing accuracy.", fontsize=8)
    save_figure(fig, output, "TimingSummary")
    return {"name": "TimingSummary", "runs": metadata,
            "method": "Unmodified accepted integer-sample lags; milliseconds = samples / 96000 × 1000.",
            "not_established": "Absolute accuracy, calibrated jitter, or a UI-click/physical-only delay."}


def probe_example(output):
    folder = ROOT / ".work/latency/runs" / RUN_IDS[0]
    with np.load(folder / "capture.npz", allow_pickle=False) as capture:
        recording = capture["recording"]
        if int(capture["samplerate"]) != FS:
            raise ValueError("Unexpected probe sample rate")
    source = np.load(folder / "output_float32.npy", allow_pickle=False)
    result = json.loads((folder / "roundtrip-analysis.json").read_text())
    trial = result["trials"][0]
    start, stop = trial["start_sample"], trial["stop_sample"]
    first, last = start - FS // 20, start + 9 * FS // 20
    time_ms = (np.arange(first, last) - start) * 1000 / FS
    correlation = _normalized_correlations(source[start:stop], recording[start:stop + FS // 10, 0])
    peak = int(np.argmax(abs(correlation)))
    if peak != trial["delay_samples"]:
        raise ValueError("Representative raw correlation disagrees with its canonical trial")
    lobe_start, lobe_stop, bounded = _primary_lobe_bounds(correlation, peak)
    scales = [float(np.max(abs(source[first:last]))), float(np.max(abs(recording[first:last, 0])))]
    fig, axes = plt.subplots(3, 1, figsize=(7.4, 6.0),
                             gridspec_kw={"height_ratios": [1, 1, 1.25]}, layout="constrained")
    for axis, samples, color, label, scale in zip(axes[:2],
            (source[first:last], recording[first:last, 0]), (COLORS[0], COLORS[1]),
            ("Generated source", "Recorded microphone input 1"), scales):
        axis.plot(time_ms, samples / scale, color=color, lw=.45)
        axis.set_xlim(-50, 450)
        axis.set_ylim(-1.08, 1.08)
        axis.set_ylabel("Own peak = 1")
        axis.text(.99, .92, label, ha="right", va="top", transform=axis.transAxes, fontsize=9,
                  bbox={"facecolor": "white", "edgecolor": "none", "alpha": .85})
        axis.grid(alpha=.18)
    axes[0].set_title("Representative measured timing probe: run 1, probe 1", loc="left", weight="bold")
    axes[0].axvline(0, color="0.3", ls="--", lw=.9)
    axes[1].axvline(peak * 1000 / FS, color="0.3", ls="--", lw=.9)
    axes[1].set_xlabel("Shared callback sample-grid position relative to source probe start (ms)")
    axes[0].tick_params(labelbottom=False)
    lag_ms = np.arange(len(correlation)) * 1000 / FS
    axes[2].plot(lag_ms, abs(correlation), color="#393E46", lw=1.2)
    axes[2].axvspan(lobe_start * 1000 / FS, lobe_stop * 1000 / FS, color=COLORS[0], alpha=.14,
                    label=f"Primary same-sign lobe: {(lobe_stop - lobe_start) * 1000 / FS:.3f} ms")
    axes[2].axvline(peak * 1000 / FS, color=COLORS[1], ls="--", lw=1,
                    label=f"Waveform-match lag: {peak * 1000 / FS:.3f} ms")
    axes[2].set_xlim(33, 44)
    axes[2].set_ylim(0, .52)
    axes[2].set_ylabel("Absolute normalized\ncorrelation")
    axes[2].set_xlabel("Source-to-microphone waveform lag (ms)")
    axes[2].legend(loc="upper right", frameon=False, fontsize=8)
    axes[2].grid(alpha=.18)
    fig.get_layout_engine().set(rect=(0, .075, 1, .925))
    fig.text(.013, .018, "Waveforms use independent peak normalization; levels are not comparable or SPL-calibrated. Lobe width is not delay uncertainty.", fontsize=8)
    save_figure(fig, output, "ProbeWaveformCorrelation")
    return {"name": "ProbeWaveformCorrelation", "run_id": RUN_IDS[0], "trial_index": 0,
            "source": source_record(folder / "output_float32.npy"), "capture": source_record(folder / "capture.npz"),
            "analysis": source_record(folder / "roundtrip-analysis.json"),
            "display_window_samples_inclusive_exclusive": [first, last],
            "source_reference_window_samples_inclusive_exclusive": [start, stop],
            "microphone_correlation_window_samples_inclusive_exclusive": [start, stop + FS // 10],
            "independent_display_peak_normalizers_fs": {"source": scales[0], "microphone": scales[1]},
            "peak_lag_samples": peak, "peak_correlation_signed": float(correlation[peak]),
            "primary_lobe_lag_samples_inclusive_exclusive": [lobe_start, lobe_stop],
            "primary_lobe_bounded": bounded,
            "method": "Pearson normalized correlation; largest absolute peak. No driver latency or timestamp correction.",
            "not_established": "Independent acoustic onset, amplitude calibration, or a lobe-width uncertainty interval."}


def spectrogram(values, window=384, hop=96, nfft=2048):
    windows = np.lib.stride_tricks.sliding_window_view(values, window)[::hop]
    weights = np.hanning(window)
    spectrum = np.fft.rfft(windows * weights, n=nfft, axis=1)
    power = abs(spectrum) ** 2
    return power.T, np.fft.rfftfreq(nfft, 1 / FS), (np.arange(len(windows)) * hop + window / 2) / FS


def sonic_example(output):
    folder = ROOT / ".work/latency/runs" / SONIC_ID
    manifest = json.loads((folder / "manifest.json").read_text())
    plan_path = folder / manifest["stimulus_plan_file"]
    plan = json.loads(plan_path.read_text())
    source = np.load(folder / manifest["source_float32_file"], allow_pickle=False)
    if hashlib.sha256(source.tobytes()).hexdigest() != manifest["output_float32_sha256"]:
        raise ValueError("SONIC source hash mismatch")
    with np.load(folder / "capture.npz", allow_pickle=False) as capture:
        microphone = capture["recording"][:, 0]
    source_start, source_stop = 2 * FS, 2 * FS + FS // 5
    display_shift = int(.038 * FS)
    arrays = (source[source_start:source_stop], microphone[source_start + display_shift:source_stop + display_shift])
    fig, axes = plt.subplots(2, 1, figsize=(7.4, 4.8), sharex=True, sharey=True, layout="constrained")
    power_refs = []
    for axis, samples, label in zip(axes, arrays, ("Commanded source", "Recorded microphone; shifted 38 ms for illustration")):
        power, frequency, centers = spectrogram(samples)
        selected = frequency <= 30000
        power = power[selected]
        reference = float(power.max())
        power_refs.append(reference)
        display_db = 10 * np.log10(np.maximum(power / reference, 1e-12))
        artist = axis.pcolormesh(centers * 1000, frequency[selected] / 1000, display_db,
                                 vmin=-60, vmax=0, cmap="magma", shading="auto", rasterized=True)
        axis.set_title(label, loc="left", fontsize=10, weight="bold")
        axis.set_ylabel("Frequency (kHz)")
    offset = manifest["plan_event_to_output_offset_samples"]
    shown_events = []
    for event in plan["events"]:
        a, b = event["output_start"] + offset, event["output_stop"] + offset
        if b <= source_start or a >= source_stop:
            continue
        frequency = event["frequency_hz"]
        x0, x1 = (a - source_start) * 1000 / FS, (b - source_start) * 1000 / FS
        shown_events.append({"source_start_sample": a, "source_stop_sample": b, "frequency_hz": frequency})
        for axis in axes:
            axis.hlines(frequency / 1000, x0, x1, color="white", lw=1.1, alpha=.85)
    for axis in axes:
        axis.set_xlim(0, 200)
        axis.set_ylim(0, 30)
    axes[1].set_xlabel("Commanded sequence position within the example (ms)")
    colorbar = fig.colorbar(artist, ax=axes, shrink=.88, pad=.025)
    colorbar.set_label("Relative power (dB; each panel's own maximum)")
    fig.get_layout_engine().set(rect=(0, .10, 1, .90))
    fig.text(.013, .042, "White segments: commanded frequencies. Microphone display alignment is illustrative; no SONIC-specific delay is inferred.", fontsize=7.8)
    fig.text(.013, .014, "4 ms Hann window; 1 ms hop; ≈250 Hz window scale (zero-padded FFT). This view does not qualify individual 10 ms pip envelopes.", fontsize=7.8)
    save_figure(fig, output, "SONICExample")
    return {"name": "SONICExample", "run_id": SONIC_ID,
            "source": source_record(folder / manifest["source_float32_file"]),
            "capture": source_record(folder / "capture.npz"), "plan": source_record(plan_path),
            "manifest": source_record(folder / "manifest.json"),
            "source_window_samples_inclusive_exclusive": [source_start, source_stop],
            "microphone_window_samples_inclusive_exclusive": [source_start + display_shift, source_stop + display_shift],
            "illustrative_microphone_display_shift_samples": display_shift,
            "alignment_is_qualified_sonic_delay": False, "shown_command_events": shown_events,
            "stft": {"window_samples": 384, "hop_samples": 96, "nfft": 2048, "window": "Hann",
                     "window_time_ms": 4, "window_frequency_scale_hz": 250, "zero_padded_bin_spacing_hz": FS / 2048,
                     "display_db_range": [-60, 0], "independent_panel_power_normalizers": power_refs},
            "not_established": "Cross-panel amplitude calibration, ultrasonic qualification, pip-envelope fidelity, or measured SONIC latency."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--skip-sonic", action="store_true")
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.parent.is_dir():
        parser.error("Create/select the LaTeX project first; the output directory's parent must already exist")
    output.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titlesize": 11, "pdf.fonttype": 42, "ps.fonttype": 42})
    record_path = ROOT / "docs/verification/2026-10-23_Audient_Playback_Microphone_Delay.json"
    verification = json.loads(record_path.read_text())
    figures = [timing_summary(output, verification), probe_example(output)]
    if not args.skip_sonic:
        figures.append(sonic_example(output))
    metadata = {"schema_version": 1, "generated_utc": datetime.now(timezone.utc).isoformat(),
                "purpose": "Scientific figures from saved bench data; no hardware access or audio acquisition",
                "script": source_record(__file__), "verification_record": source_record(record_path),
                "software": {"numpy": np.__version__, "matplotlib": matplotlib.__version__},
                "figures": figures,
                "raw_audio_files_included": False,
                "figure_waveforms_are_actual_measured_excerpts": True}
    for figure in metadata["figures"]:
        figure["outputs"] = [{"filename": f"{figure['name']}.{extension}",
                               "sha256": digest(output / f"{figure['name']}.{extension}")}
                              for extension in ("png", "pdf")]
    (output / "figures-manifest.json").write_text(json.dumps(metadata, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"output_directory": str(output), "figure_names": [f["name"] for f in figures]}, indent=2))


if __name__ == "__main__":
    main()
