"""Native Audient full-duplex acquisition; raw captures stay in ignored .work/."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import threading

import numpy as np
import sounddevice as sd

from .analysis import analyze_trials, _normalized_correlations
from .stimulus import make_probe_plan, make_sonic_e_block
from .transport import assess_timestamps

ROOT = Path(__file__).resolve().parents[1]
FS = 96000


def audient():
    matches = [(i, dict(d)) for i, d in enumerate(sd.query_devices())
               if "audient" in d["name"].lower() and d["max_input_channels"] >= 2 and d["max_output_channels"] >= 2]
    if len(matches) != 1:
        raise RuntimeError("Connect exactly one Audient with at least two input/output channels.")
    index, device = matches[0]
    if "core audio" not in sd.query_hostapis(device["hostapi"])["name"].lower():
        raise RuntimeError("This setup requires the macOS Core Audio backend.")
    sd.check_input_settings(device=index, channels=2, dtype="float32", samplerate=FS)
    sd.check_output_settings(device=index, channels=2, dtype="float32", samplerate=FS)
    return index, device


def capture(waveform, device_index):
    """Single duplex stream; input columns are first two Audient host channels.

    Callback array positions for output and input are NOT assumed simultaneous.
    The primary analysis compares two channels of the same captured input array.
    """
    total = len(waveform)
    recording = np.zeros((total, 2), dtype=np.float32)
    log = np.zeros((total // 16 + 256, 5), dtype=np.float64)
    complete = threading.Event()
    position = 0
    log_position = 0

    def callback(indata, outdata, frames, timing, flags):
        nonlocal position, log_position
        outdata.fill(0)
        count = min(frames, total - position)
        if log_position >= len(log) or count < 0:
            raise sd.CallbackAbort
        # Preallocated audio and timestamp storage, no disk I/O in callback.
        recording[position:position + count] = indata[:count, :2]
        outdata[:count, 0] = waveform[position:position + count]
        outdata[:count, 1] = waveform[position:position + count]
        bits = (int(flags.input_underflow) | int(flags.input_overflow) << 1 |
                int(flags.output_underflow) << 2 | int(flags.output_overflow) << 3 |
                int(flags.priming_output) << 4)
        log[log_position] = (position, timing.inputBufferAdcTime, timing.outputBufferDacTime, frames, bits)
        log_position += 1
        position += count
        if position >= total:
            raise sd.CallbackStop

    with sd.Stream(device=(device_index, device_index), samplerate=FS, channels=(2, 2),
                   dtype="float32", blocksize=0, latency="low", callback=callback,
                   finished_callback=complete.set) as stream:
        reported_latency = tuple(float(v) for v in stream.latency)
        if not complete.wait(total / FS + 8):
            stream.abort()
            raise RuntimeError("Capture did not finish within its expected duration.")
    timestamps = log[:log_position].copy()
    errors = []
    if position != total:
        errors.append("incomplete_capture")
    if not np.isfinite(recording).all():
        errors.append("non_finite_audio")
    timestamp_check = assess_timestamps(timestamps, FS)
    errors.extend(timestamp_check["errors"])
    return recording, timestamps, {"valid_transport": not errors, "transport_errors": errors,
        "reported_input_output_latency_seconds": reported_latency,
        "reported_latency_is_measured_delay": False, "captured_frames": position,
        "clock_diagnostics": timestamp_check["clock_diagnostics"],
        "callback_log_columns": ["capture_array_start", "input_buffer_adc_time_s", "output_buffer_dac_time_s", "frames", "status_bits"],
        "status_bits": {"input_underflow": 1, "input_overflow": 2, "output_underflow": 4, "output_overflow": 8, "priming_output": 16}}


def reference_windows(recording, waveform, plan):
    """Locate actual electrical return; do not align input/output by callback index."""
    if plan.get("trials"):
        trials = plan["trials"]
        first = trials[0]
        start, stop = first["output_start"], first["output_stop"]
    else:
        start = FS  # SONIC playback is prefixed with one second of silence.
        stop = start + FS // 2
        trials = [{"output_start": point, "output_stop": point + FS // 4}
                  for point in range(start, len(waveform) - FS - FS // 4, FS)]
    radius = FS // 5
    left, right = max(0, start - radius), min(len(recording), stop + radius)
    template = waveform[start:stop]
    correlations = _normalized_correlations(template, recording[left:right, 1])
    peak = int(np.argmax(np.abs(correlations)))
    score = float(abs(correlations[peak]))
    reference_rms = float(np.sqrt(np.mean(recording[left + peak:left + peak + len(template), 1] ** 2)))
    if score < 0.6 or reference_rms < 1e-6:
        raise RuntimeError("Electrical reference not detected reliably. Check output 2 → rear line input 2, its gain and 48 V OFF. No delay result is valid.")
    offset = left + peak - start
    windows, matches = [], []
    for trial in trials:
        a, b = trial["output_start"], trial["output_stop"]
        local_radius = FS // 200
        local_left = max(0, a + offset - local_radius)
        local_right = min(len(recording), b + offset + local_radius)
        local = _normalized_correlations(waveform[a:b], recording[local_left:local_right, 1])
        local_peak = int(np.argmax(np.abs(local)))
        local_score = float(abs(local[local_peak]))
        if local_score < .6 or local_peak in (0, len(local) - 1):
            raise RuntimeError("An electrical probe could not be aligned uniquely within its local search; recording requires review.")
        actual_start = local_left + local_peak
        windows.append({"start_sample": actual_start, "stop_sample": actual_start + b - a})
        matches.append({"capture_minus_output_array_offset_samples": int(actual_start - a),
                        "electrical_template_correlation": local_score})
    if any(w["start_sample"] < 0 or w["stop_sample"] + FS // 10 > len(recording) for w in windows):
        raise RuntimeError("Reference alignment exceeds capture bounds; no valid delay result.")
    return windows, {"capture_minus_output_array_offset_samples": offset,
                     "electrical_template_correlation": score,
                     "per_window_reference_matches": matches,
                     "reference_offset_range_samples": int(np.ptp([m["capture_minus_output_array_offset_samples"] for m in matches])),
                     "array_offset_is_absolute_hardware_latency": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Inspect device/format only; no capture or playback")
    wiring = sub.add_parser("wiring-check", help="Play three very quiet probes and verify electrical return; geometry is unmeasured")
    wiring.set_defaults(stimulus="probe", repetitions=3, peak_dbfs=-48, distance_m=None, output=None)
    wiring.add_argument("--peak-dbfs", type=float, default=-48)
    wiring.add_argument("--repetitions", type=int, default=3)
    record = sub.add_parser("record", help="Play quietly and record microphone+electrical return")
    record.add_argument("--stimulus", choices=["probe", "sonic-e"], default="probe")
    record.add_argument("--repetitions", type=int, default=20)
    record.add_argument("--peak-dbfs", type=float, default=-36)
    record.add_argument("--distance-m", type=float, required=True, help="Measured speaker-to-microphone distance; geometry metadata only")
    record.add_argument("--output", type=Path, help="Local run folder, default ignored .work/latency/runs/timestamp")
    args = parser.parse_args()
    try:
        index, device = audient()
        if args.command == "check":
            print(json.dumps({"device_index_this_process": index, "device": device,
                              "sample_rate_hz": FS, "native_duplex_format_supported": True,
                              "playback_or_capture_started": False}, indent=2))
            return
        if args.command == "record" and (not np.isfinite(args.distance_m) or args.distance_m <= 0):
            parser.error("--distance-m must be a positive measured distance")
        if args.stimulus == "probe":
            waveform, plan = make_probe_plan(samplerate=FS, repetitions=args.repetitions, peak_dbfs=args.peak_dbfs)
        else:
            block, plan = make_sonic_e_block(samplerate=FS, peak_dbfs=args.peak_dbfs)
            waveform = np.concatenate((np.zeros(FS, dtype=np.float32), block, np.zeros(FS, dtype=np.float32)))
        folder = args.output or ROOT / ".work/latency/runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
        folder.mkdir(parents=True, exist_ok=False)
        print("Wiring: mic → input 1 (phantom as required); output 1 → one speaker; output 2 → rear line input 2 (48 V OFF).", flush=True)
        print(f"Playing {args.stimulus} at {args.peak_dbfs} dBFS for {len(waveform)/FS:.2f} s, capturing Audient channels 1 and 2.", flush=True)
        recording, timestamps, transport = capture(waveform, index)
        np.savez_compressed(folder / "capture.npz", recording=recording, samplerate=FS, callback_timestamps=timestamps)
        np.save(folder / "output_float32.npy", waveform)
        manifest = {"date_utc": datetime.now(timezone.utc).isoformat(), "device": device,
                    "native_playback_and_capture_performed": True,
                    "sample_rate_hz": FS, "distance_m": args.distance_m,
                    "platform": platform.platform(), "numpy_version": np.__version__, "sounddevice_version": sd.__version__,
                    "stimulus": plan, "transport": transport,
                    "output_sha256": hashlib.sha256(waveform.tobytes()).hexdigest(),
                    "raw_audio_publication_authorized": False}
        result = {"status": "invalid", "measured_delay_ms": None}
        try:
            windows, alignment = reference_windows(recording, waveform, plan)
            manifest.update(windows=windows, alignment=alignment)
            result = analyze_trials(recording, FS, windows)
            result["transport"] = transport
            result["minimum_accepted_trials_for_screening"] = 3
            result["usable_measurement"] = transport["valid_transport"] and result["summary"]["accepted_trials"] >= 3
            if args.command == "wiring-check":
                result["purpose"] = "wiring_check_only; geometry unmeasured and level intentionally low"
                result["usable_measurement"] = False
            if not transport["valid_transport"]:
                result["status"] = "invalid_transport; correlation candidates are diagnostic only"
        except (RuntimeError, ValueError) as error:
            result["error"] = str(error)
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2))
        (folder / "analysis.json").write_text(json.dumps(result, indent=2))
        print(json.dumps(result, indent=2))
        print(f"Local capture and analysis saved in {folder}. Raw room audio stays outside Git.")
    except (RuntimeError, sd.PortAudioError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
