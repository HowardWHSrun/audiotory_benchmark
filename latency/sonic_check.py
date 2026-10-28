"""Play reconstructed SONIC Sheep E tones while recording the Audient microphone.

This is a stimulus and pickup check, not a calibrated sound-level or delay test.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .music_check import FS, ROOT, _input_summary, write_pcm24
from .stimulus import make_sonic_e_block


def make_stimulus(preview=False, peak_dbfs=-24, pip_gains=None):
    """Return padded reconstructed pips with optional experimental attenuation."""
    block, plan = make_sonic_e_block(
        samplerate=FS, tones_per_frequency=50 if preview else 600,
        peak_dbfs=peak_dbfs,
    )
    if pip_gains is not None:
        from .pip_level_check import FREQUENCIES_HZ
        if peak_dbfs != -36 or set(pip_gains) != set(FREQUENCIES_HZ):
            raise ValueError('An experimental pip profile requires the -36 dBFS base and all frequencies.')
        for event in plan['events']:
            gain=float(pip_gains[event['frequency_hz']])
            if not np.isfinite(gain) or gain > 0:
                raise ValueError('All pip profile gains must be finite and non-positive.')
            block[event['output_start']:event['output_stop']] *= 10**(gain/20)
            event['attenuation_db']=gain
        plan['observed_digital_peak']=float(np.max(np.abs(block)))
        plan['experimental_pip_attenuation_db_by_frequency_hz']={str(f):float(pip_gains[f]) for f in FREQUENCIES_HZ}
        plan['local_choices'].append('Experimental measured isolated-pip attenuation applied by frequency; consecutive playback unqualified.')
        plan['limitations'].append('Isolated-pip correction does not establish equal levels in the consecutive sequence or an animal protocol.')
    waveform = np.concatenate((np.zeros(FS, dtype=np.float32), block,
                               np.zeros(FS, dtype=np.float32)))
    return waveform, plan


def _write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generate-only", action="store_true",
                        help="Write the source and plan without importing sounddevice or accessing audio devices")
    parser.add_argument("--preview", action="store_true",
                        help="Play a short 700-pip, 7-second preview instead of the full 8,400-pip, 84-second block")
    parser.add_argument("--peak-dbfs", type=float, default=-24,
                        help="Digital peak, -60 to -18 dBFS (default -24); acoustic SPL is uncalibrated")
    parser.add_argument("--output", type=Path,
                        help="New output folder; default ignored .work/latency/runs/timestamp-sonic-e14-full or preview")
    parser.add_argument("--pip-correction-from", type=Path,
                        help="Experimentally apply the validated profile of a prior isolated-pip run; requires --peak-dbfs -36")
    args = parser.parse_args()
    try:
        gains=None
        profile=None
        if args.pip_correction_from:
            if args.peak_dbfs != -36:
                raise ValueError('Experimental pip correction requires --peak-dbfs -36.')
            from .pip_level_check import derive_pip_corrections
            gains,profile=derive_pip_corrections(args.pip_correction_from,reuse_profile=True)
        waveform, plan = make_stimulus(args.preview, args.peak_dbfs, gains)
        scope = "preview" if args.preview else "full"
        folder = args.output or ROOT / ".work/latency/runs" / (
            datetime.now().strftime("%Y%m%d-%H%M%S") + f"-sonic-e14-{scope}")
        folder.mkdir(parents=True, exist_ok=False)
        source_name = f"sonic-e14-{scope}-reconstruction.wav"
        np.save(folder / "output_float32.npy", waveform)
        write_pcm24(folder / source_name, waveform)
        _write_json(folder / "stimulus-plan.json", plan)
        manifest = {
            "date_utc": datetime.now(timezone.utc).isoformat(),
            "purpose": "SONIC Sheep E reconstruction playback and simultaneous microphone recording; no delay estimate",
            "stimulus_scope": "short preview; below the paper's block-size range" if args.preview else "one full reconstructed E14 block; not a full paper session",
            "exact_original_waveform": False,
            "sample_rate_hz": FS,
            "digital_peak_limit_dbfs": args.peak_dbfs,
            "observed_digital_peak_fs": float(np.max(np.abs(waveform))),
            "acoustic_spl_calibrated": False,
            "frequency_response_qualified": False,
            "experimental_pip_profile": profile,
            "stimulus_plan_file": "stimulus-plan.json",
            "stimulus_plan_describes": "unpadded generated block; sound_played in that plan describes generation only",
            "block_duration_seconds": plan["duration_seconds"],
            "tone_count": plan["tone_count"],
            "tones_per_frequency": plan["tones_per_frequency"],
            "source_wav_file": source_name,
            "source_float32_file": "output_float32.npy",
            "output_sample_count": len(waveform),
            "output_duration_seconds": len(waveform) / FS,
            "leading_silence_samples": FS,
            "trailing_silence_samples": FS,
            "plan_event_to_output_offset_samples": FS,
            "event_position_rule": "add 96000 to stimulus-plan output_start/output_stop for padded source positions",
            "output_channel_routing": "same mono waveform to Audient host output channels 1 and 2",
            "native_playback_and_capture_performed": False,
            "raw_audio_publication_authorized": False,
            "measured_delay_ms": None,
            "output_float32_sha256": hashlib.sha256(waveform.tobytes()).hexdigest(),
            "source_wav_sha256": hashlib.sha256((folder / source_name).read_bytes()).hexdigest(),
            "limitations": [
                "Original recording/order, exact ramp shape and digital amplitude were not supplied; see the reconstruction plan.",
                "High-frequency pips may be inaudible; audibility does not establish speaker bandwidth.",
                "Digital peak does not establish acoustic SPL. Keep the established hardware volume and microphone gain.",
                "Repeated pure tones are not analyzed here for timing; no latency result is inferred.",
                "Any experimental pip correction applies only the isolated-pip profile; consecutive playback is not qualified.",
            ],
        }
        _write_json(folder / "manifest.json", manifest)
        if not args.generate_only:
            # Offline generation deliberately does not import the audio backend.
            from .run import audient, capture, sd

            try:
                index, device = audient()
                if float(device["default_samplerate"]) != FS:
                    raise RuntimeError("Set the Audient's current sample rate to 96000 Hz before this check.")
                print(f"Playing {scope} reconstructed SONIC E14: {plan['tone_count']} pips, "
                      f"{plan['duration_seconds']:.1f} seconds plus 1-second silence at each end, "
                      f"{args.peak_dbfs} dBFS peak. Recording Audient inputs 1 and 2.", flush=True)
                print("Keep the working hardware volume and mic gain. Inputs 1/2 must stay excluded from speaker monitoring. "
                      "Acoustic level and high-frequency response are uncalibrated.", flush=True)
                recording, timestamps, transport = capture(waveform, index)
            except sd.PortAudioError as error:
                raise RuntimeError(f"Audient audio error: {error}") from error
            np.savez_compressed(folder / "capture.npz", recording=recording, samplerate=FS,
                                callback_timestamps=timestamps)
            write_pcm24(folder / "microphone-input-1.wav", recording[:, 0])
            report = {
                "purpose": "SONIC E14 reconstruction playback and simultaneous recording check",
                "stimulus_scope": scope,
                "transport": transport,
                "inputs": _input_summary(recording),
                "electrical_reference_required": False,
                "sound_pickup_requires_review": True,
                "acoustic_spl_calibrated": False,
                "frequency_response_qualified": False,
                "measured_delay_ms": None,
            }
            manifest.update(device=device, native_playback_and_capture_performed=True,
                            transport=transport)
            _write_json(folder / "manifest.json", manifest)
            _write_json(folder / "pickup-check.json", report)
            print(json.dumps(report, indent=2, allow_nan=False))
        print(f"Saved in {folder.resolve()}. Raw room audio is private; keep capture files outside Git.")
    except (RuntimeError, ValueError, OSError, ImportError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
