"""Play a recognizable melody while recording the Audient microphone, without delay analysis."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import wave

import numpy as np

FS = 96000
ROOT = Path(__file__).resolve().parents[1]
PHRASES = (
    "C C G G A A G", "F F E E D D C", "G G F F E E D",
    "G G F F E E D", "C C G G A A G", "F F E E D D C",
)
FREQUENCIES = {"C": 261.625565, "D": 293.664768, "E": 329.627557,
               "F": 349.228231, "G": 391.995436, "A": 440.0}


def make_melody(peak_dbfs=-24):
    """Return the waveform used in the successful bench check and its note events."""
    if not np.isfinite(peak_dbfs) or not -60 <= peak_dbfs <= -18:
        raise ValueError("peak_dbfs must be between -60 and -18")
    notes, events = [], []
    position = 0
    for phrase in PHRASES:
        tokens = phrase.split()
        for index, note in enumerate(tokens):
            count = int(FS * .4 * (2 if index == len(tokens) - 1 else 1))
            t = np.arange(count) / FS
            frequency = FREQUENCIES[note]
            envelope = (1 - np.exp(-t / .004)) * np.exp(-t / 1.1)
            release = int(FS * .025)
            envelope[-release:] *= np.linspace(1, 0, release)
            signal = (np.sin(2 * np.pi * frequency * t)
                      + .22 * np.sin(2 * np.pi * 2 * frequency * t)
                      + .06 * np.sin(2 * np.pi * 3 * frequency * t)) * envelope
            notes.append(signal.astype(np.float32))
            events.append({"note": note + "4", "frequency_hz": frequency,
                           "start_sample": position, "duration_samples": count})
            position += count
    melody = np.concatenate(notes)
    melody *= np.float32(10 ** (peak_dbfs / 20) / np.abs(melody).max())
    waveform = np.concatenate((np.zeros(2 * FS, dtype=np.float32), melody,
                               np.zeros(FS, dtype=np.float32)))
    return waveform, {"music": "Public-domain Twinkle Twinkle melody; locally synthesized recording",
                      "original_synthesized_recording": True,
                      "sample_rate_hz": FS, "peak_dbfs": peak_dbfs,
                      "duration_seconds": len(waveform) / FS,
                      "preroll_seconds": 2, "postroll_seconds": 1,
                      "events_start_reference": "melody start; add 192000 samples for output waveform positions",
                      "events": events}


def write_pcm24(path, waveform):
    """Write mono PCM24; saturate only at the integer file-format boundaries."""
    waveform = np.asarray(waveform)
    if waveform.ndim != 1 or not np.isfinite(waveform).all():
        raise ValueError("PCM24 export requires a finite mono waveform")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(3)
        stream.setframerate(FS)
        for start in range(0, len(waveform), 65536):
            integers = np.clip(np.rint(waveform[start:start + 65536].astype(np.float64) * 2 ** 23),
                               -2 ** 23, 2 ** 23 - 1).astype("<i4")
            stream.writeframesraw(integers.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())


def _input_summary(recording):
    result = []
    clipping_threshold = .999
    for index in range(recording.shape[1]):
        signal = recording[:, index].astype(np.float64)
        peak = float(np.max(np.abs(signal)))
        rms = float(np.sqrt(np.mean(signal * signal)))
        result.append({"input": index + 1, "peak_fs": peak,
                       "peak_dbfs": float(20 * np.log10(peak)) if peak else None,
                       "rms_dbfs": float(20 * np.log10(rms)) if rms else None,
                       "clipping_threshold_fs": clipping_threshold,
                       "samples_at_or_above_clipping_threshold": int(np.count_nonzero(np.abs(signal) >= clipping_threshold)),
                       "clipped": bool(peak >= clipping_threshold)})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-only", action="store_true", help="Write the stimulus without accessing audio devices")
    parser.add_argument("--peak-dbfs", type=float, default=-24, help="Digital peak, -60 to -18 dBFS (default -24)")
    parser.add_argument("--output", type=Path, help="New output folder; default ignored .work/latency/runs/timestamp-music-check")
    args = parser.parse_args()
    try:
        waveform, metadata = make_melody(args.peak_dbfs)
        folder = args.output or ROOT / ".work/latency/runs" / (datetime.now().strftime("%Y%m%d-%H%M%S") + "-music-check")
        folder.mkdir(parents=True, exist_ok=False)
        np.save(folder / "output_float32.npy", waveform)
        write_pcm24(folder / "played-melody.wav", waveform)
        manifest = {"date_utc": datetime.now(timezone.utc).isoformat(),
                    "purpose": "verify known music playback and simultaneous microphone recording; no delay estimate",
                    **metadata, "native_playback_and_capture_performed": False,
                    "raw_audio_publication_authorized": False, "measured_delay_ms": None,
                    "output_sha256": hashlib.sha256(waveform.tobytes()).hexdigest()}
        (folder / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
        if not args.generate_only:
            # Keep offline generation independent of sounddevice and the audio backend.
            from .run import audient, capture, sd

            try:
                index, device = audient()
                if float(device["default_samplerate"]) != FS:
                    raise RuntimeError("Set the Audient's current sample rate to 96000 Hz before this check.")
                print(f"Playing the melody at {args.peak_dbfs} dBFS for {len(waveform) / FS:.1f} seconds; recording Audient inputs 1 and 2.", flush=True)
                recording, timestamps, transport = capture(waveform, index)
            except sd.PortAudioError as error:
                raise RuntimeError(f"Audient audio error: {error}") from error
            np.savez_compressed(folder / "capture.npz", recording=recording, samplerate=FS,
                                callback_timestamps=timestamps)
            write_pcm24(folder / "microphone-input-1.wav", recording[:, 0])
            report = {"purpose": "basic playback and simultaneous recording check",
                      "transport": transport, "inputs": _input_summary(recording),
                      "electrical_reference_required": False,
                      "measured_delay_ms": None, "sound_pickup_requires_review": True}
            manifest.update(device=device, native_playback_and_capture_performed=True, transport=transport)
            (folder / "manifest.json").write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n")
            (folder / "pickup-check.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
            print(json.dumps(report, indent=2, allow_nan=False))
        print(f"Saved in {folder.resolve()}. Raw room audio is private; keep capture files outside Git.")
    except (RuntimeError, ValueError, OSError, ImportError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
