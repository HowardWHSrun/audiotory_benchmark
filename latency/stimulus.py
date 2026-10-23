"""Precompute documented timing probes and a SONIC Sheep E reconstruction.

This module generates arrays/files only. It never opens an audio device or plays
sound. Run ``python latency/stimulus.py --help`` for the optional file generator.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import wave

import numpy as np


E_FREQUENCIES_HZ = (2000, 4000, 6000, 8000, 9000, 10500, 17000,
                    18200, 19500, 20900, 22400, 24000, 25800, 27000)
SUPPORTED_SAMPLE_RATES = (96000, 192000)
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / ".work/latency/stimuli"
PAPER_SOURCE = {
    "title": "SONIC: A Benchmarking Paradigm for Brain-Computer Interfaces",
    "version": "bioRxiv v1, posted 2025-10-02",
    "doi": "10.1101/2025.09.30.679683",
    "url": "https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1",
    "methods": "Sections 6.1–6.2, printed page 11",
    "local_pdf": "sources/SONIC_2025_bioRxiv_v1.pdf",
}


def _parameters(samplerate, peak_dbfs):
    if isinstance(samplerate, bool) or samplerate not in SUPPORTED_SAMPLE_RATES:
        raise ValueError("samplerate must be 96000 or 192000 Hz")
    if not isinstance(peak_dbfs, (int, float)) or not math.isfinite(peak_dbfs):
        raise ValueError("peak_dbfs must be finite")
    if not -60 <= peak_dbfs <= -18:
        raise ValueError("peak_dbfs must be between -60 and -18 dBFS")
    return int(samplerate), float(peak_dbfs), 10.0 ** (peak_dbfs / 20.0)


def _positive_integer(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(value)


def _envelope(samples, ramp_samples):
    """Inclusive zero-to-one half-cosine samples at each end of a flat envelope."""
    if not 2 <= ramp_samples <= samples // 2:
        raise ValueError("ramp must contain at least two samples and fit at both ends")
    result = np.ones(samples, dtype=np.float64)
    edge = 0.5 * (1.0 - np.cos(np.linspace(0.0, np.pi, ramp_samples)))
    result[:ramp_samples] = edge
    result[-ramp_samples:] = edge[::-1]
    return result


def _common_metadata(kind, samplerate, peak_dbfs, waveform):
    return {
        "schema_version": 1,
        "kind": kind,
        "sample_rate_hz": samplerate,
        "channels": 1,
        "array_dtype": "float32",
        "sample_count": len(waveform),
        "duration_seconds": len(waveform) / samplerate,
        "digital_peak_limit_dbfs": peak_dbfs,
        "observed_digital_peak": float(np.max(np.abs(waveform))),
        "amplitude_convention": "sine/chirp peak multiplier = 10**(dBFS/20); not RMS or acoustic SPL",
        "ramp_shape": "raised cosine (local choice); endpoints inclusive, first/last samples zero",
        "sample_index_convention": "zero-based output_start inclusive, output_stop exclusive",
        "sound_played": False,
        "measurement_status": "generated reference only; no recorded timing or acoustic measurement",
        "limitations": [
            "Digital amplitude does not establish acoustic sound pressure or exposure.",
            "Sample indices describe the generated output array, not physical output timestamps.",
            "Speaker bandwidth, distortion, acoustic onset and timing jitter remain unmeasured.",
        ],
    }


def make_probe_plan(samplerate=96000, repetitions=20, peak_dbfs=-36):
    """Return a mono float32 chirp train and a sample-accurate trial plan.

    Every probe is a 100 ms logarithmic 100 Hz–20 kHz chirp with 20 ms
    raised-cosine end ramps. Starts are separated by 500 ms. Exact 1 second
    silence pads precede the first probe and follow the final probe's stop.
    This timing signal is deliberately distinct from the SONIC experiment.
    """
    samplerate, peak_dbfs, peak = _parameters(samplerate, peak_dbfs)
    repetitions = _positive_integer(repetitions, "repetitions")
    probe_samples = samplerate // 10
    ramp_samples = samplerate // 50
    spacing_samples = samplerate // 2
    pad_samples = samplerate
    t = np.arange(probe_samples, dtype=np.float64) / samplerate
    duration = probe_samples / samplerate
    sweep_rate = math.log(20000.0 / 100.0) / duration
    phase = 2.0 * np.pi * 100.0 * np.expm1(sweep_rate * t) / sweep_rate
    probe = (peak * np.sin(phase) * _envelope(probe_samples, ramp_samples)).astype(np.float32)
    waveform = np.zeros(2 * pad_samples + (repetitions - 1) * spacing_samples + probe_samples,
                        dtype=np.float32)
    trials = []
    for trial in range(repetitions):
        start = pad_samples + trial * spacing_samples
        stop = start + probe_samples
        waveform[start:stop] = probe
        trials.append({"trial": trial, "output_start": start, "output_stop": stop})
    metadata = _common_metadata("timing_probe", samplerate, peak_dbfs, waveform)
    metadata.update({
        "purpose": "electrical/acoustic timing reference; distinct from SONIC experimental stimuli",
        "sonic_stimulus": False,
        "sweep": "logarithmic frequency; sine phase starts at zero",
        "frequency_start_hz": 100,
        "frequency_end_hz": 20000,
        "frequency_endpoint_convention": "20 kHz instantaneous frequency at t=100 ms, just after the last sampled point",
        "probe_duration_seconds": 0.1,
        "probe_duration_samples": probe_samples,
        "ramp_seconds_each_end": 0.02,
        "ramp_samples_each_end": ramp_samples,
        "onset_spacing_seconds": 0.5,
        "onset_spacing_samples": spacing_samples,
        "leading_silence_samples": pad_samples,
        "trailing_silence_samples": pad_samples,
        "repetitions": repetitions,
        "trials": trials,
        "provenance": "Locally specified timing probe; no claim that SONIC used this signal.",
    })
    return waveform, metadata


def make_sonic_e_block(samplerate=96000, tones_per_frequency=600,
                       seed=20261023, peak_dbfs=-36):
    """Return one balanced, seeded reconstruction using the published E14 list.

    The default block has 8,400 consecutive 10 ms pips (84 seconds). The exact
    historical order, seed, ramp shape and digital levels are unavailable; this
    array must not be called an original or exact SONIC recording waveform.
    """
    samplerate, peak_dbfs, peak = _parameters(samplerate, peak_dbfs)
    tones_per_frequency = _positive_integer(tones_per_frequency, "tones_per_frequency")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed must be a nonnegative integer")
    seed = int(seed)
    pip_samples = samplerate // 100
    ramp_samples = samplerate // 500
    sequence = np.repeat(np.asarray(E_FREQUENCIES_HZ, dtype=np.int32), tones_per_frequency)
    generator = np.random.Generator(np.random.PCG64(seed))
    generator.shuffle(sequence)
    tone_count = len(sequence)
    waveform = np.empty(tone_count * pip_samples, dtype=np.float32)
    time = np.arange(pip_samples, dtype=np.float64) / samplerate
    envelope = _envelope(pip_samples, ramp_samples)
    bank = {frequency: (peak * np.sin(2.0 * np.pi * frequency * time) * envelope).astype(np.float32)
            for frequency in E_FREQUENCIES_HZ}
    events = []
    for trial, value in enumerate(sequence):
        frequency = int(value)
        start = trial * pip_samples
        stop = start + pip_samples
        waveform[start:stop] = bank[frequency]
        events.append({"trial": trial, "frequency_hz": frequency,
                       "output_start": start, "output_stop": stop})
    metadata = _common_metadata("sonic_e14_reconstruction", samplerate, peak_dbfs, waveform)
    metadata.update({
        "purpose": "Locally generated reconstruction of the published Sheep E stimulus specification",
        "exact_original_waveform": False,
        "paper_source": dict(PAPER_SOURCE),
        "published_frequency_list_hz": list(E_FREQUENCIES_HZ),
        "frequency_precision": "uses the numeric frequency values listed in SONIC v1; no original waveform file available",
        "tone_count": tone_count,
        "tones_per_frequency": tones_per_frequency,
        "marginal_probability_each_frequency": 1 / len(E_FREQUENCIES_HZ),
        "sequence_rule": "repeat each frequency equally, then numpy Generator(PCG64(seed)).shuffle once",
        "seed": seed,
        "numpy_version": np.__version__,
        "random_bit_generator": "PCG64",
        "tone_duration_seconds": 0.01,
        "tone_duration_samples": pip_samples,
        "ramp_seconds_each_end": 0.002,
        "ramp_samples_each_end": ramp_samples,
        "phase_convention": "sine starts at zero phase independently for every pip",
        "inter_tone_silence_samples": 0,
        "leading_silence_samples": 0,
        "trailing_silence_samples": 0,
        "within_published_block_tone_count_range": 8000 <= tone_count <= 15000,
        "block_scope": "one block only; no 1-second inter-block silence or >=12-block session included",
        "paper_dac_sample_rate_hz": 192000,
        "sample_rate_role": "Audient 96-kHz adaptation" if samplerate == 96000 else "192-kHz archival reconstruction matching the paper DAC rate",
        "sequence_hz": [int(value) for value in sequence],
        "events": events,
        "unresolved_original_details": [
            "Original sound files and stimulus-generation code were not located; availability remains unresolved.",
            "The original random order, seed, balancing algorithm and exact per-block counts are unspecified.",
            "The paper specifies 2-ms ramps but not their shape; raised cosine is a local choice.",
            "Digital amplitude, normalization and acoustic level convention are unspecified.",
            "Speaker position, frequency-specific calibration, acoustic latency and jitter are unspecified.",
            "The exact initial Sheep C 37-frequency array is absent; it is not reconstructed here.",
        ],
        "local_choices": [
            "Declared PCG64 seeded shuffle of exactly equal frequency counts.",
            "Raised-cosine ramps and declared digital peak level.",
            f"One block with {tones_per_frequency} instances of each frequency.",
            "Mono output array; playback channel and physical route are separate choices.",
        ],
    })
    return waveform, metadata


def write_stimulus(waveform, metadata, output_dir=DEFAULT_OUTPUT_DIR):
    """Write PCM24 WAV, JSON manifest and hashes without opening audio devices."""
    waveform = np.asarray(waveform)
    if waveform.ndim != 1 or not np.all(np.isfinite(waveform)):
        raise ValueError("waveform must be a finite mono array")
    if len(waveform) != metadata["sample_count"] or np.max(np.abs(waveform)) >= 1:
        raise ValueError("waveform size/peak does not match a valid generated reference")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    level = f"{abs(metadata['digital_peak_limit_dbfs']):g}".replace(".", "p")
    suffix = (f"{metadata['repetitions']}trials" if metadata["kind"] == "timing_probe" else
              f"{metadata['tones_per_frequency']}per-tone_seed{metadata['seed']}")
    stem = f"{metadata['kind']}_{metadata['sample_rate_hz']}Hz_{suffix}_m{level}dBFS"
    wav_path = output_dir / f"{stem}.wav"
    with wave.open(str(wav_path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(3)
        stream.setframerate(metadata["sample_rate_hz"])
        for start in range(0, len(waveform), 65536):
            integers = np.rint(waveform[start:start + 65536].astype(np.float64) * (2 ** 23)).astype("<i4")
            packed = integers.view(np.uint8).reshape(-1, 4)[:, :3].tobytes()
            stream.writeframesraw(packed)
    digest = hashlib.sha256()
    with wav_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    waveform_hash = digest.hexdigest()
    manifest = dict(metadata)
    manifest.update({
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "wav_file": wav_path.name,
        "wav_encoding": "mono signed little-endian PCM24; round(float32 * 2**23)",
        "wav_sha256": waveform_hash,
    })
    manifest_path = output_dir / f"{stem}.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    hash_path = output_dir / f"{stem}.sha256"
    hash_path.write_text(f"{waveform_hash}  {wav_path.name}\n{manifest_hash}  {manifest_path.name}\n", encoding="ascii")
    return {"wav": str(wav_path.resolve()), "manifest": str(manifest_path.resolve()), "sha256": str(hash_path.resolve())}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=("probe", "sonic-e", "bank"),
                        help="bank writes both signal types at both 96 and 192 kHz")
    parser.add_argument("--samplerate", type=int, choices=SUPPORTED_SAMPLE_RATES, default=96000)
    parser.add_argument("--repetitions", type=int, default=20)
    parser.add_argument("--tones-per-frequency", type=int, default=600)
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--peak-dbfs", type=float, default=-36)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()
    outputs = []
    try:
        for rate in SUPPORTED_SAMPLE_RATES if args.kind == "bank" else (args.samplerate,):
            if args.kind in ("probe", "bank"):
                signal, plan = make_probe_plan(rate, args.repetitions, args.peak_dbfs)
                outputs.append(write_stimulus(signal, plan, args.output_dir))
            if args.kind in ("sonic-e", "bank"):
                signal, plan = make_sonic_e_block(rate, args.tones_per_frequency, args.seed, args.peak_dbfs)
                outputs.append(write_stimulus(signal, plan, args.output_dir))
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps({"sound_played": False, "outputs": outputs}, indent=2))


if __name__ == "__main__":
    main()
