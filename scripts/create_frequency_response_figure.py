"""Plot sanitized, measured frequency-review records; no audio hardware access.

Requires matplotlib and NumPy. The input JSON files contain derived measurements,
not synthetic examples. Raw room audio remains in ignored .work/.
"""
from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PIP_RECORD = ROOT / "docs/verification/2026-10-23_SONIC_E14_Pip_Frequency_Pickup.json"
SWEEP_RECORD = ROOT / "docs/verification/2026-10-23_Sweep_Relative_Response.json"
OUTPUT = ROOT / "output/figures/2026-10-23/Saved_Frequency_Response.png"


def build():
    pip = json.loads(PIP_RECORD.read_text())
    rows = pip["frequency_results"]
    colors = ("#16738d", "#d17a2a")
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                         "axes.spines.right": False, "axes.titleweight": "bold"})
    fig, axes = plt.subplots(2, 1, figsize=(11.2, 9.0),
                             gridspec_kw={"height_ratios": [1.0, 1.15]})
    fig.suptitle("Saved recordings: frequency output is uneven", fontsize=18,
                 fontweight="bold", x=.10, ha="left", y=.98)
    fig.text(.10, .932, "Relative measurements of the full playback / microphone chain | 23 October 2026",
             fontsize=10, color="#52616b")
    top = axes[0]
    top.set_title("A. Timing sweeps: response only where excitation and coherence pass screening", loc="left", pad=12)
    if SWEEP_RECORD.exists():
        sweep = json.loads(SWEEP_RECORD.read_text())
        for run_index, run in enumerate(sweep["runs"]):
            bands = run["bands"]
            frequencies = np.array([band["frequency_hz"] for band in bands])
            values = np.array([band["relative_to_2khz_db"] if band["accepted"] else np.nan
                               for band in bands], dtype=float)
            top.semilogx(frequencies, values, color=colors[run_index], lw=1.7,
                         label=f"Sweep recording {run_index + 1}")
    else:
        raise FileNotFoundError("The reviewed sweep record must exist before plotting")
    top.axhline(0, color="#a9b7bd", lw=.7)
    top.set_xlim(100, 27000)
    top.set_ylim(-24, 14)
    top.set_xticks([100, 200, 500, 1000, 2000, 4000, 8000, 12000, 20000, 27000],
                  ["100", "200", "500", "1k", "2k", "4k", "8k", "12k", "20k", "27k"])
    top.set_xlabel("Frequency (Hz)")
    top.set_ylabel("Transfer relative to 2 kHz (dB)")
    top.grid(axis="y", alpha=.2)
    top.legend(loc="upper right", frameon=False, fontsize=9)
    top.text(.015, .045, "Gaps indicate unsupported measurements; the sweep cannot assess frequencies above 20 kHz.",
             transform=top.transAxes, fontsize=8.6, color="#52616b")
    bottom = axes[1]
    bottom.set_title("B. SONIC tones: high-frequency components are much weaker in the microphone recording", loc="left", pad=12)
    positions = np.arange(len(rows))
    for run_index in range(2):
        level, lower, upper = [], [], []
        for row in rows:
            capture = row["captures"][run_index]
            value = capture["relative_to_same_run_2khz_db"]
            level.append(value)
            lower.append(capture["median_fundamental_rms_dbfs"] - capture["p05_fundamental_rms_dbfs"])
            upper.append(capture["p95_fundamental_rms_dbfs"] - capture["median_fundamental_rms_dbfs"])
        bottom.bar(positions + (run_index - .5) * .35, level, width=.33,
                   yerr=np.array([lower, upper]), capsize=2, color=colors[run_index],
                   alpha=.9, error_kw={"elinewidth": .65}, label=f"SONIC recording {run_index + 1}")
    bottom.axhline(0, color="#52616b", lw=.8)
    bottom.set_ylim(-52, 7)
    bottom.set_xlim(-.65, len(rows) - .35)
    bottom.set_xticks(positions, [f"{row['frequency_hz'] / 1000:g}" for row in rows], rotation=35)
    bottom.set_xlabel("Commanded SONIC frequency (kHz)")
    bottom.set_ylabel("Recorded pip level relative to 2 kHz (dB)")
    bottom.grid(axis="y", alpha=.2)
    bottom.legend(loc="lower left", frameon=False, fontsize=9)
    bottom.text(.99, .04, "600 pips / frequency / recording\nBars: medians; whiskers: 5th-95th percentile of pip levels",
                transform=bottom.transAxes, ha="right", fontsize=8.4, color="#52616b")
    fig.text(.10, .035,
             "Operator-reported separation: 10 cm. Microphone correction and SPL calibration were not applied.\n"
             "Short-pip pickup does not isolate speaker output or establish harmonic distortion or ultrasonic fidelity.",
             fontsize=9.1, color="#52616b")
    fig.subplots_adjust(left=.10, right=.98, top=.865, bottom=.17, hspace=.58)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT, dpi=180, facecolor="white")
    plt.close(fig)
    print(OUTPUT)


if __name__ == "__main__":
    build()
