"""Generate LaTeX tables and provenance for the full saved-data bench report.

Reads verification records and saved capture-quality JSON. No audio devices or
raw room audio are accessed. Compile main.tex separately with LaTeX.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "output/pdf/2026-10-23/Full_Bench_Analysis_Report"
RECORD_NAMES = {
    "delay": "2026-10-23_Audient_Playback_Microphone_Delay.json",
    "sonic": "2026-10-23_SONIC_E14_Playback.json",
    "pip": "2026-10-23_SONIC_E14_Pip_Frequency_Pickup.json",
    "sweep": "2026-10-23_Sweep_Relative_Response.json",
    "basic": "2026-10-23_Audient_Basic_Playback_Recording.json",
    "preparation": "2026-10-23_Audient_Delay_Preparation.json",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def table(path, columns, header, rows):
    lines = [r"\begin{tabular}{@{}" + columns + r"@{}}", r"\toprule",
             " & ".join(header) + r" \\", r"\midrule"]
    lines.extend(" & ".join(row) + r" \\" for row in rows)
    lines.extend([r"\bottomrule", r"\end{tabular}", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    paths = {key: ROOT / "docs/verification" / name for key, name in RECORD_NAMES.items()}
    data = {key: json.loads(path.read_text()) for key, path in paths.items()}
    delay, pip, sweep = data["delay"], data["pip"], data["sweep"]
    output = REPORT / "tables"
    output.mkdir(parents=True, exist_ok=True)
    images = REPORT / "images"
    images.mkdir(exist_ok=True)
    shutil.copy2(ROOT / "output/figures/2026-10-23/Saved_Frequency_Response.png",
                 images / "FrequencyResponse.png")

    rows = []
    for index, run in enumerate(delay["runs"], 1):
        quality = run["quality"]
        # Peak levels are derived directly from captured samples in the source record.
        peak = quality["microphone_input1_peak_dbfs"]
        rows.append([f"D{index}", "Timing sweeps", "20", "11.6", "1,113,600", f"{peak:.2f}"])
    auxiliary_quality = []
    for index, run in enumerate(pip["capture_quality"], 1):
        quality_path = ROOT / ".work/latency/runs" / run["run_id"] / "pickup-check.json"
        peak = json.loads(quality_path.read_text())["inputs"][0]["peak_dbfs"]
        auxiliary_quality.append({"id": f"S{index}", "path": str(quality_path.relative_to(ROOT)),
                                  "sha256": sha(quality_path), "microphone_peak_dbfs": peak})
        rows.append([f"S{index}", "E14 block", "8,400", "86.0", "8,256,000", f"{peak:.2f}"])
    table(output / "Dataset.tex", "llrrrr",
          ["ID", "Stimulus", "Events", "Time (s)", "Frames", "Mic peak (dBFS)"], rows)

    rows = []
    for index, run in enumerate(delay["runs"], 1):
        s = run["summary"]
        correlations = [trial["peak_correlation_abs"] for trial in run["trials"]]
        rows.append([f"D{index}", f"{s['accepted_trials']}/{s['total_trials']}",
                     f"{s['median_delay_ms']:.3f}",
                     f"{s['min_delay_ms']:.3f}--{s['max_delay_ms']:.3f}",
                     f"{min(correlations):.3f}--{max(correlations):.3f}"])
    table(output / "DelayResults.tex", "lrrrr",
          ["Run", "Accepted", "Median (ms)", "Range (ms)", r"$|r|$ range"], rows)

    rows = []
    for row in pip["frequency_results"]:
        first, second = row["captures"]
        a, b = first["relative_to_same_run_2khz_db"], second["relative_to_same_run_2khz_db"]
        control = min(value for cap in row["captures"] for value in
                      (cap["median_above_preblock_db"], cap["median_over_inblock_control_db"]))
        sensitivity = max(cap["alignment_sensitivity_span_db"] for cap in row["captures"])
        rows.append([f"{row['frequency_hz']/1000:g}", f"{a:.2f}", f"{b:.2f}",
                     f"{b-a:+.2f}", f"{control:.1f}", f"{sensitivity:.2f}"])
    table(output / "PipLevels.tex", "rrrrrr",
          [r"\shortstack{Tone\\(kHz)}", r"\shortstack{S1 relative\\(dB)}",
           r"\shortstack{S2 relative\\(dB)}", r"\shortstack{S2--S1\\(dB)}",
           r"\shortstack{Min. contrast\\(dB)}", r"\shortstack{Alignment span\\(dB)}"], rows)

    anchors = (100, 200, 500, 1000, 2000, 4000, 8000, 12000, 16000, 18000, 20000)
    rows = []
    for frequency in anchors:
        bands = [next(b for b in run["bands"] if b["frequency_hz"] == frequency) for run in sweep["runs"]]
        levels = [f"{b['relative_to_2khz_db']:.2f}" if b["accepted"] else "--" for b in bands]
        rows.append([f"{frequency/1000:g}", *levels,
                     f"{bands[0]['source_weighted_coherence']:.3f}",
                     f"{bands[1]['source_weighted_coherence']:.3f}",
                     "Pass" if all(b["accepted"] for b in bands) else "Masked"])
    table(output / "SweepAnchors.tex", "rrrrrl",
          ["kHz", "D1 (dB)", "D2 (dB)", r"$\gamma^2_1$", r"$\gamma^2_2$", "Screen"], rows)

    summary = delay["summary"]
    supported = [row for row in sweep["combined_magnitude_bands"] if row["accepted_in_all_runs"]]
    macros = {
        "DelayMedian": f"{summary['combined_median_delay_ms']:.3f}",
        "DelayMinimum": f"{summary['combined_min_delay_ms']:.3f}",
        "DelayMaximum": f"{summary['combined_max_delay_ms']:.3f}",
        "DelaySpan": f"{summary['combined_range_ms']:.3f}",
        "RunMedianShift": f"{summary['run_median_change_ms']:.3f}",
        "AcceptedSweepBands": str(len(supported)),
        "TotalSweepBands": str(len(sweep['combined_magnitude_bands'])),
        "SupportedLowHz": f"{min(row['frequency_hz'] for row in supported):.2f}",
        "SupportedHighHz": f"{max(row['frequency_hz'] for row in supported):.2f}",
    }
    backslash = chr(92)
    (REPORT / "metrics.tex").write_text("% Generated from measured verification records.\n" +
        "\n".join(backslash + "newcommand{" + backslash + key + "}{" + value + "}"
                  for key, value in macros.items()) + "\n")

    manifest = {
        "date_local": "2026-10-23", "timezone": "America/Chicago",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Full analysis report from existing saved human-bench recordings only",
        "new_playback_performed": False, "new_acquisition_performed": False,
        "raw_room_audio_published": False,
        "analysis_repository_revision": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "input_records": [{"id": key, "path": str(path.relative_to(ROOT)), "sha256": sha(path)}
                          for key, path in paths.items()],
        "additional_capture_quality_records": auxiliary_quality,
        "paper": {"path": "sources/SONIC_2025_bioRxiv_v1.pdf",
                  "sha256": sha(ROOT / "sources/SONIC_2025_bioRxiv_v1.pdf"),
                  "version": "bioRxiv v1, posted 2025-10-02; CC BY-NC-ND 4.0; unchanged"},
        "data_groups": [{"id": f"D{i+1}", "run_id": run["run_id"], "raw_hashes": run["hashes"]}
                        for i, run in enumerate(delay["runs"])],
        "source_code": [{"path": path, "sha256": sha(ROOT / path)} for path in
                        ("latency/run.py", "latency/analysis.py", "latency/roundtrip.py",
                         "latency/transport.py", "latency/pip_response.py", "latency/sweep_response.py",
                         "latency/stimulus.py", "scripts/create_full_bench_report_data.py")],
        "generated_tables": [{"path": str(path.relative_to(REPORT)), "sha256": sha(path)}
                             for path in sorted(output.glob("*.tex"))],
        "metric_macros": macros,
        "pip_data_source": "Two captures of the same PCG64 sequence; 600 pips/frequency/capture, not 1200 independent randomized sessions.",
        "figure_source": "images/figures-manifest.json; FrequencyResponse.png copied from the previously verified relative-response figure.",
        "figure_frequency_response_sha256": sha(images / "FrequencyResponse.png"),
    }
    manifest["data_groups"].extend(
        {"id": f"S{i+1}", "run_id": run["run_id"], "raw_hashes": run["raw_and_manifest_sha256"]}
        for i, run in enumerate(pip["capture_quality"]))
    (REPORT / "data-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Generated four measured tables, metrics, copied figure and provenance in {REPORT}")


if __name__ == "__main__":
    main()
