"""Native playback-to-microphone waveform roundtrip on a full-duplex sample grid.

Run ``python -m latency.roundtrip --generate-only`` without audio hardware, or
``--analyze-run PATH`` to analyze an existing capture without playing sound.
The default command deliberately plays twenty probes and captures room audio.
This is distinct from analysis.py's simultaneous electrical-reference method.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .analysis import analyze_trials
from .music_check import write_pcm24
from .stimulus import make_probe_plan
from .transport import assess_timestamps

FS = 96000
ROOT = Path(__file__).resolve().parents[1]
INTERPRETATION = (
    "Generated output-buffer waveform to microphone input-buffer waveform alignment "
    "on this native full-duplex application's sample grid. Includes output/input "
    "buffering, interface conversion, loudspeaker, acoustic travel and microphone path. "
    "It is not UI-click/Play-to-sound latency, physical DAC-to-ADC-only latency, "
    "independently established acoustic onset, or neural latency. Sample interval "
    "is the search increment, not calibrated measurement accuracy."
)


def analyze_roundtrip(source, microphone, samplerate, windows, transport):
    """Analyze source/microphone vectors with explicit transport qualification.

    The source is the exact array submitted by the same duplex callback that
    stored the microphone samples. It is not a recorded electrical channel.
    Saved-stream integrity must be supplied; absent/failed metadata suppresses
    accepted delays, while retaining waveform candidates for diagnosis.
    """
    source = np.asarray(source)
    microphone = np.asarray(microphone)
    if source.ndim != 1 or microphone.ndim != 1 or not len(source) or len(source) != len(microphone):
        raise ValueError("source and microphone must be nonempty, equal-length mono vectors")
    if not np.isfinite(source).all() or not np.isfinite(microphone).all():
        raise ValueError("source and microphone must contain finite samples")
    result = analyze_trials(np.column_stack((microphone, source)), samplerate, windows)
    # Reuse signal-quality checks without inheriting electrical-reference claims.
    result["method"] = "native_full_duplex_source_to_microphone_waveform_roundtrip"
    result["reference_signal"] = "exact_generated_output_buffer_array; not an electrical recording"
    result["response_signal"] = "Audient microphone input 1"
    result["sample_index_origin"] = "input and output array positions advanced together in each full-duplex callback"
    result["interpretation"] = INTERPRETATION
    result["electrical_reference_required"] = False
    result["reported_driver_latency_added_or_subtracted"] = False
    result["raw_audio_publication_authorized"] = False
    for trial in result["trials"]:
        trial["source_rms_fs"] = trial.pop("reference_rms_fs")
        trial["source_clipped_samples"] = trial.pop("reference_clipped_samples")
        trial["reasons"] = [reason.replace("reference_", "source_") for reason in trial["reasons"]]
    transport_valid = (isinstance(transport, dict) and transport.get("valid_transport") is True
                       and transport.get("transport_errors") == [])
    result["transport"] = dict(transport) if isinstance(transport, dict) else None
    if isinstance(transport, dict) and isinstance(transport.get("clock_diagnostics"), dict):
        clock = dict(transport["clock_diagnostics"])
        clock["interpretation"] = (
            "Host ADC/DAC timestamps are uncalibrated diagnostics. Primary source/microphone "
            "roundtrip uses paired full-duplex callback sample coordinates; timestamps "
            "and reported driver latencies are not added or subtracted."
        )
        result["transport"]["clock_diagnostics"] = clock
    result["minimum_accepted_trials_for_screening"] = 3
    result["waveform_quality_accepted_trials_before_transport_screen"] = result["summary"]["accepted_trials"]
    if not transport_valid:
        for trial in result["trials"]:
            trial["accepted"] = False
            trial["delay_samples"] = trial["delay_ms"] = None
            trial["reasons"].append("transport_invalid_or_unverified")
        for key in result["summary"]:
            if key == "accepted_trials":
                result["summary"][key] = 0
            elif key == "rejected_trials":
                result["summary"][key] = result["summary"]["total_trials"]
            elif key != "total_trials":
                result["summary"][key] = None
    result["usable_measurement"] = transport_valid and result["summary"]["accepted_trials"] >= 3
    result["status"] = ("screening_pass" if result["usable_measurement"] else
                        "invalid_transport" if not transport_valid else "insufficient_accepted_trials")
    return result


def _probe_windows(manifest):
    stimulus = manifest.get("stimulus", {})
    if stimulus.get("kind") != "timing_probe" or not stimulus.get("trials"):
        raise ValueError("Roundtrip analysis requires a saved nonperiodic timing-probe plan")
    return [(trial["output_start"], trial["output_stop"]) for trial in stimulus["trials"]]


def analyze_saved_run(folder):
    """Analyze a private native run, preserving its original analysis/manifest."""
    folder = Path(folder)
    manifest = json.loads((folder / "manifest.json").read_text())
    source = np.load(folder / "output_float32.npy", allow_pickle=False)
    expected_hash = manifest.get("output_sha256")
    if not expected_hash or hashlib.sha256(source.tobytes()).hexdigest() != expected_hash:
        raise ValueError("Saved source hash is absent or does not match its manifest")
    with np.load(folder / "capture.npz", allow_pickle=False) as saved:
        recording = saved["recording"]
        samplerate = float(saved["samplerate"].item())
        timestamps = saved["callback_timestamps"] if "callback_timestamps" in saved else None
    if samplerate != FS or manifest.get("sample_rate_hz") != FS:
        raise ValueError("This native roundtrip workflow requires matching saved 96000 Hz metadata")
    if recording.ndim != 2 or recording.shape[1] != 2:
        raise ValueError("Saved capture must contain Audient inputs 1 and 2")
    transport = dict(manifest.get("transport") or {})
    errors = list(transport.get("transport_errors") or [])
    if transport.get("valid_transport") is not True or "transport_errors" not in transport:
        errors.append("saved_transport_invalid_or_unverified")
    if transport.get("captured_frames") != len(recording):
        errors.append("saved_capture_frame_count_mismatch")
    if manifest.get("native_playback_and_capture_performed") is not True:
        errors.append("native_duplex_acquisition_unverified")
    check = assess_timestamps(timestamps if timestamps is not None else [], samplerate)
    errors.extend(check["errors"])
    transport.update(valid_transport=not errors, transport_errors=sorted(set(errors)),
                     clock_diagnostics=check["clock_diagnostics"])
    result = analyze_roundtrip(source, recording[:, 0], samplerate, _probe_windows(manifest), transport)
    result["source_sha256"] = expected_hash
    result["sample_rate_hz"] = samplerate
    result["distance_m"] = manifest.get("distance_m")
    result["geometry_role"] = "recorded metadata; not subtracted from measured waveform roundtrip"
    result["source_wav"] = "played-probes.wav"
    result["microphone_wav"] = "microphone-input-1.wav"
    write_pcm24(folder / result["source_wav"], source)
    write_pcm24(folder / result["microphone_wav"], recording[:, 0])
    (folder / "roundtrip-analysis.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--generate-only", action="store_true", help="Prepare probes without accessing audio hardware")
    mode.add_argument("--analyze-run", type=Path, help="Analyze an existing native timing-probe run; no playback/capture")
    parser.add_argument("--peak-dbfs", type=float, default=-24)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--distance-m", type=float, help="Optional measured geometry metadata; never subtracted")
    parser.add_argument("--output", type=Path, help="New acquisition/generation folder; default ignored .work/latency/runs/")
    args = parser.parse_args()
    try:
        if args.analyze_run:
            if args.output:
                raise ValueError("--analyze-run writes derived results beside the saved capture; omit --output")
            result = analyze_saved_run(args.analyze_run)
            print(json.dumps(result, indent=2, allow_nan=False))
            return
        if args.distance_m is not None and (not np.isfinite(args.distance_m) or args.distance_m <= 0):
            raise ValueError("--distance-m must be positive when supplied")
        source, plan = make_probe_plan(FS, args.repetitions, args.peak_dbfs)
        folder = args.output or ROOT / ".work/latency/runs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-roundtrip")
        folder.mkdir(parents=True, exist_ok=False)
        np.save(folder / "output_float32.npy", source)
        write_pcm24(folder / "played-probes.wav", source)
        manifest = {"date_utc": datetime.now(timezone.utc).isoformat(),
                    "purpose": "native full-duplex source-to-microphone waveform roundtrip",
                    "sample_rate_hz": FS, "distance_m": args.distance_m, "stimulus": plan,
                    "native_playback_and_capture_performed": False,
                    "output_sha256": hashlib.sha256(source.tobytes()).hexdigest(),
                    "raw_audio_publication_authorized": False}
        manifest_path = folder / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
        if not args.generate_only:
            # Keep offline analysis/generation independent of audio-backend imports.
            from .run import audient, capture, sd

            try:
                index, device = audient()
                if float(device["default_samplerate"]) != FS:
                    raise RuntimeError("Set the Audient's current sample rate to 96000 Hz before measuring")
                print(f"Playing {args.repetitions} timing probes at {args.peak_dbfs:g} dBFS; recording microphone input 1. Keep input monitoring disabled.", flush=True)
                recording, timestamps, transport = capture(source, index)
            except sd.PortAudioError as error:
                raise RuntimeError(f"Audient audio error: {error}") from error
            np.savez_compressed(folder / "capture.npz", recording=recording, samplerate=FS,
                                callback_timestamps=timestamps)
            manifest.update(device=device, native_playback_and_capture_performed=True, transport=transport)
            manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
            print(json.dumps(analyze_saved_run(folder), indent=2, allow_nan=False))
        print(f"Saved privately in {folder.resolve()}")
    except (RuntimeError, ValueError, OSError, KeyError, ImportError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
