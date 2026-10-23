#!/usr/bin/env python3
"""Clean concise-report plots from three public derived-data JSON records only.

No raw recordings, audio-device imports, playback, capture, or new measurements.
Run with .work/latency-venv/bin/python scripts/create_concise_bench_report_figures.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RECORDS = {
    "timing": ROOT / "docs/verification/2026-10-23_Audient_Playback_Microphone_Delay.json",
    "sweep": ROOT / "docs/verification/2026-10-23_Sweep_Relative_Response.json",
    "pip": ROOT / "docs/verification/2026-10-23_SONIC_E14_Pip_Frequency_Pickup.json",
}
OUTPUT = ROOT / "output/pdf/2026-10-23/Concise_Bench_Analysis_Report/images"
COLORS = ("#24608A", "#B65B2F")


def checksum(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(fig, output, name):
    fig.savefig(output / f"{name}.png", dpi=300, facecolor="white")
    fig.savefig(output / f"{name}.pdf", facecolor="white",
                metadata={"CreationDate": None, "ModDate": None})
    plt.close(fig)


def timing_figure(record, output):
    fig, axes = plt.subplots(1, 2, figsize=(7.1, 3.2), sharex=True, sharey=True,
                             layout="constrained")
    plotted = []
    if len(record["runs"]) != 2:
        raise ValueError("Expected two separately started timing runs")
    for index, run in enumerate(record["runs"]):
        trials = run["trials"]
        if len(trials) != 20 or not all(trial["accepted"] for trial in trials):
            raise ValueError("Expected all twenty accepted timing probes per run")
        samples = np.array([trial["delay_samples"] for trial in trials], dtype=int)
        values = np.array([trial["delay_ms"] for trial in trials], dtype=float)
        np.testing.assert_allclose(values, samples * 1000 / run["sample_rate_hz"], rtol=0, atol=1e-12)
        positions = np.arange(1, 21)
        median = float(np.median(samples) * 1000 / run["sample_rate_hz"])
        sample_std_samples = float(np.std(samples - samples[0], ddof=1))
        sample_std_ms = sample_std_samples * 1000 / run["sample_rate_hz"]
        marker = ("o", "s")[index]
        axis = axes[index]
        axis.plot(positions, values, color=COLORS[index], marker=marker, ms=3.8, lw=1.1)
        axis.hlines(median, positions[0], positions[-1], color=COLORS[index], ls="--", lw=.8)
        axis.set_title(f"Run {index + 1}", loc="left", fontsize=10, weight="bold", pad=5)
        axis.text(.98, .94, f"Median {median:.3f} ms", transform=axis.transAxes,
                 ha="right", va="top", color=COLORS[index], fontsize=9)
        axis.set_xlabel("Probe number")
        axis.set_xticks([1, 5, 10, 15, 20])
        plotted.append({"run_id": run["run_id"], "probe_numbers": (positions + 20 * index).tolist(),
                        "within_run_probe_numbers": positions.tolist(),
                        "delay_samples": samples.tolist(), "delay_ms": values.tolist(),
                        "median_delay_ms": median, "n": len(samples), "sample_std_ddof": 1,
                        "sample_std_delay_samples": sample_std_samples,
                        "sample_std_delay_ms": sample_std_ms,
                        "min_delay_ms": float(samples.min() * 1000 / run["sample_rate_hz"]),
                        "max_delay_ms": float(samples.max() * 1000 / run["sample_rate_hz"]),
                        "peak_to_peak_delay_samples": int(np.ptp(samples)),
                        "peak_to_peak_delay_ms": float(np.ptp(samples) * 1000 / run["sample_rate_hz"])})
    for axis in axes.flat:
        axis.grid(axis="y", color="0.90", lw=.6)
        axis.set_xlim(.4, 20.6)
    axes[0].set_ylim(38.20, 38.425)
    axes[0].set_yticks([38.20, 38.25, 38.30, 38.35, 38.40])
    axes[0].set_ylabel("Delay (ms)")
    save(fig, output, "TimingSummary")
    return {"figure": "TimingSummary", "size_inches": [7.1, 3.2], "runs": plotted,
            "sample_sd_definition": "Sample standard deviation (n-1 denominator), computed in sample units then converted to milliseconds.",
            "normalization": "Delay is the unmodified accepted sample-grid lag in milliseconds; no timing correction.",
            "precision_role": "Axis precision and one-sample repeatability do not establish timing accuracy."}


def frequency_figure(sweep, pip, output):
    fig, axes = plt.subplots(2, 1, figsize=(7.1, 4.75),
                             gridspec_kw={"height_ratios": [1.0, 1.15]}, layout="constrained")
    top, bottom = axes
    sweep_arrays = []
    if len(sweep["runs"]) != 2:
        raise ValueError("Expected two sweep recordings")
    for index, run in enumerate(sweep["runs"]):
        frequencies = np.array([band["frequency_hz"] for band in run["bands"]], dtype=float)
        accepted = np.array([bool(band["accepted"]) for band in run["bands"]])
        values = np.array([band["relative_to_2khz_db"] if band["accepted"] else np.nan
                           for band in run["bands"]], dtype=float)
        if int(accepted.sum()) != run["accepted_band_count"]:
            raise ValueError("Sweep accepted-band count differs from the source record")
        top.semilogx(frequencies, values, color=COLORS[index], lw=1.4,
                     ls=("-", "--")[index], label=f"Run {index + 1}")
        sweep_arrays.append({"run_id": run["local_run"], "frequency_hz": frequencies.tolist(),
                             "accepted": accepted.tolist(),
                             "relative_h1_db": [float(value) if np.isfinite(value) else None for value in values],
                             "accepted_band_count": int(accepted.sum())})
    top.set_title("A  Sweep response", loc="left", fontsize=10, weight="bold", pad=5)
    top.set_xlim(100, 27000)
    top.set_ylim(-24, 14)
    top.set_xticks([100, 500, 1000, 2000, 4000, 8000, 20000, 27000],
                  ["100", "500", "1k", "2k", "4k", "8k", "20k", "27k"])
    top.set_xlabel("Frequency (Hz)")
    top.set_ylabel("H1 relative to 2 kHz (dB)")
    top.legend(loc="lower right", bbox_to_anchor=(1, 1.02), borderaxespad=0,
               ncol=2, frameon=False, fontsize=8.8)
    rows = pip["frequency_results"]
    if len(rows) != 14 or any(len(row["captures"]) != 2 for row in rows):
        raise ValueError("Expected fourteen SONIC frequencies and two recordings")
    frequencies = [row["frequency_hz"] for row in rows]
    if frequencies[0] != 2000:
        raise ValueError("The reference SONIC row must be 2 kHz")
    positions = np.arange(len(rows))
    pip_arrays = []
    for index in range(2):
        captures = [row["captures"][index] for row in rows]
        if any(capture["pip_count"] != 600 for capture in captures):
            raise ValueError("Expected 600 pips per frequency and recording")
        median_dbfs = np.array([c["median_fundamental_rms_dbfs"] for c in captures])
        low_dbfs = np.array([c["p05_fundamental_rms_dbfs"] for c in captures])
        high_dbfs = np.array([c["p95_fundamental_rms_dbfs"] for c in captures])
        relative = np.array([c["relative_to_same_run_2khz_db"] for c in captures])
        np.testing.assert_allclose(relative, median_dbfs - median_dbfs[0], rtol=0, atol=1e-10)
        lower_error, upper_error = median_dbfs - low_dbfs, high_dbfs - median_dbfs
        if np.any(lower_error < 0) or np.any(upper_error < 0):
            raise ValueError("Pip percentile bounds do not bracket the median")
        bottom.bar(positions + (index - .5) * .35, relative, width=.33, color=COLORS[index],
                   yerr=np.array([lower_error, upper_error]), capsize=1.8,
                   error_kw={"elinewidth": .65, "capthick": .65}, label=f"Run {index + 1}")
        pip_arrays.append({"run_id": captures[0]["run_id"], "frequency_hz": frequencies,
                           "pip_counts": [c["pip_count"] for c in captures],
                           "median_relative_db": relative.tolist(),
                           "p05_relative_db": (low_dbfs - median_dbfs[0]).tolist(),
                           "p95_relative_db": (high_dbfs - median_dbfs[0]).tolist(),
                           "lower_error_db": lower_error.tolist(), "upper_error_db": upper_error.tolist(),
                           "reference_2khz_median_dbfs": float(median_dbfs[0])})
    bottom.set_title("B  SONIC tone levels", loc="left", fontsize=10, weight="bold", pad=5)
    bottom.set_xlim(-.65, len(rows) - .35)
    bottom.set_ylim(-52, 7)
    bottom.set_xticks(positions, [f"{value / 1000:g}" for value in frequencies], rotation=35, ha="right")
    bottom.tick_params(axis="x", labelsize=8.8)
    bottom.set_xlabel("SONIC frequency (kHz)")
    bottom.set_ylabel("Level relative to 2 kHz (dB)")
    bottom.legend(loc="lower right", bbox_to_anchor=(1, 1.02), borderaxespad=0,
                  ncol=2, frameon=False, fontsize=8.8)
    for axis in axes:
        axis.axhline(0, color="0.66", lw=.7, zorder=0)
        axis.grid(axis="y", color="0.90", lw=.6)
        axis.set_axisbelow(True)
    save(fig, output, "FrequencyResponse")
    return {"figure": "FrequencyResponse", "size_inches": [7.1, 4.75],
            "sweep": {"runs": sweep_arrays,
                      "normalization": "Each saved run's accepted H1 magnitude relative to its 2-kHz band.",
                      "missing_values": "Rejected bands remain NaN while plotting, serialized as null; no interpolation or extrapolation."},
            "pip": {"runs": pip_arrays,
                    "normalization": "All-target pip fundamental medians relative to the same recording's 2-kHz median.",
                    "whiskers": "5th–95th percentiles of pip levels with that same 2-kHz median subtracted; not confidence intervals."}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    if not output.parent.is_dir():
        parser.error("The concise LaTeX project must already exist")
    output.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 9.5, "axes.labelsize": 9.5, "xtick.labelsize": 9,
                         "ytick.labelsize": 9, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.linewidth": .7, "pdf.fonttype": 42, "ps.fonttype": 42})
    data = {name: json.loads(path.read_text()) for name, path in RECORDS.items()}
    figures = [timing_figure(data["timing"], output), frequency_figure(data["sweep"], data["pip"], output)]
    manifest = {"schema_version": 1, "purpose": "Clean concise-report rendering of unchanged saved derived measurements",
                "new_sound_played": False, "new_audio_recorded": False, "raw_recordings_read": False,
                "script": {"path": str(Path(__file__).resolve().relative_to(ROOT)), "sha256": checksum(__file__)},
                "sources": [{"role": name, "path": str(path.relative_to(ROOT)), "sha256": checksum(path)}
                            for name, path in RECORDS.items()],
                "software": {"numpy": np.__version__, "matplotlib": matplotlib.__version__},
                "figures": figures,
                "outputs": [{"filename": f"{name}.{extension}", "sha256": checksum(output / f"{name}.{extension}")}
                            for name in ("TimingSummary", "FrequencyResponse") for extension in ("pdf", "png")]}
    (output / "figures-manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"directory": str(output), "output_files": [row["filename"] for row in manifest["outputs"]],
                      "timing_probes": sum(len(run["delay_samples"]) for run in figures[0]["runs"]),
                      "sonic_frequencies": len(figures[1]["pip"]["runs"][0]["frequency_hz"]),
                      "screened_sweep_bands_per_run": [run["accepted_band_count"] for run in figures[1]["sweep"]["runs"]]}, indent=2))


if __name__ == "__main__":
    main()
