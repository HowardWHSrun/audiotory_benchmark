"""Measure separated-tone microphone pickup; this does not establish acoustic SPL.

No gain corrections are applied. Recordings stay in the ignored .work directory.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

FS = 96000
FREQUENCIES_HZ = (2000, 4000, 6000, 8000, 9000, 10500, 17000,
                  18200, 19500, 20900, 22400, 24000, 25800, 27000)
ROOT = Path(__file__).resolve().parents[1]


def make_probe(peak_dbfs=-48.0):
    """14 separated 0.6 s tones, with 0.5 s gaps and 20 ms ramps."""
    if not np.isfinite(peak_dbfs) or not -80 <= peak_dbfs <= -36:
        raise ValueError('Digital peak must be between -80 and -36 dBFS.')
    duration = round(.6 * FS)
    gap = round(.5 * FS)
    ramp_len = round(.02 * FS)
    envelope = np.ones(duration)
    ramp = .5 - .5 * np.cos(np.linspace(0, np.pi, ramp_len))
    envelope[:ramp_len] = ramp
    envelope[-ramp_len:] = ramp[::-1]
    amplitude = 10 ** (peak_dbfs / 20)
    parts = [np.zeros(FS, dtype=np.float32)]
    events = []
    cursor = FS
    for freq in FREQUENCIES_HZ:
        t = np.arange(duration) / FS
        parts.append((amplitude * envelope * np.sin(2 * np.pi * freq * t)).astype(np.float32))
        events.append({'frequency_hz': freq, 'start_sample': cursor, 'stop_sample': cursor + duration})
        parts.append(np.zeros(gap, dtype=np.float32))
        cursor += duration + gap
    parts.append(np.zeros(FS, dtype=np.float32))
    return np.concatenate(parts), events


def sinusoid_amplitude(samples, frequency):
    """Magnitude of a Hann-weighted single-frequency component, peak units."""
    if len(samples) < 2:
        raise ValueError('Analysis window is empty.')
    samples = np.asarray(samples, dtype=np.float64)
    weights = np.hanning(len(samples))
    oscillator = np.exp(-2j * np.pi * frequency * np.arange(len(samples)) / FS)
    return float(2 * abs(np.dot(samples * weights, oscillator)) / weights.sum())


def analyze(recording, events, transport):
    """Compare a stationary central tone window against an earlier silent window.

    Array alignment assumes the total playback/capture offset is below 150 ms;
    the steady-state window is deliberately inside each tone. No timing measurement.
    """
    audio = np.asarray(recording)
    if audio.ndim != 2 or audio.shape[1] < 1 or not np.isfinite(audio).all():
        raise ValueError('Recording must be finite and contain input channel 1.')
    mic = audio[:, 0]
    peak = float(np.max(np.abs(mic)))
    clipped = peak >= .99
    records = []
    for event in events:
        start = event['start_sample']
        n = round(.25 * FS)
        a = start + round(.20 * FS)
        b = start - round(.35 * FS)
        if b < 0 or a + n > len(mic):
            raise ValueError('Audio capture too short for analysis windows.')
        freq = event['frequency_hz']
        tone_amp = sinusoid_amplitude(mic[a:a+n], freq)
        background_amp = sinusoid_amplitude(mic[b:b+n], freq)
        pickup_dbfs = 20 * np.log10(max(tone_amp, 1e-15))
        noise_dbfs = 20 * np.log10(max(background_amp, 1e-15))
        above_background_db = float(pickup_dbfs - noise_dbfs)
        records.append({'frequency_hz': freq, 'microphone_fundamental_peak_dbfs': float(pickup_dbfs),
                        'background_component_peak_dbfs': float(noise_dbfs),
                        'tone_minus_background_db': above_background_db,
                        'passes_background_screen': bool(tone_amp > 1e-8 and above_background_db >= 10)})
    reference = records[0]['microphone_fundamental_peak_dbfs']
    for row in records:
        row['relative_to_2khz_db'] = (row['microphone_fundamental_peak_dbfs'] - reference
                                       if records[0]['passes_background_screen'] and row['passes_background_screen']
                                       and not clipped and transport.get('valid_transport', False) else None)
    return {'purpose': 'separated tone relative microphone pickup, not absolute sound-pressure calibration',
            'microphone_input_peak_fs': peak, 'microphone_clipping_screen_failed': clipped,
            'transport': transport, 'reference_hz': 2000, 'rows': records,
            'limitations': ['Uncorrected microphone and whole playback/room/input chain; not calibrated dB SPL.',
                            'Assumes playback-to-capture offset below 150 ms, with stable gain and geometry.',
                            'At least 10 dB above the narrowband background is a screening criterion, not proof of accuracy.',
                            'Steady tones are not the actual 10 ms pips; no distortion, equal loudness, safe exposure or ultrasonic fidelity is established.',
                            'No gain corrections have been applied.']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--peak-dbfs', type=float, default=-48.)
    parser.add_argument('--generate-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        waveform, events = make_probe(args.peak_dbfs)
        folder = args.output or ROOT / '.work/latency/runs' / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '-separated-levels')
        folder.mkdir(parents=True, exist_ok=False)
        np.save(folder / 'output_float32.npy', waveform)
        manifest = {'utc': datetime.now(timezone.utc).isoformat(), 'sample_rate_hz': FS,
                    'digital_peak_dbfs': args.peak_dbfs, 'events': events,
                    'output_sha256': hashlib.sha256(waveform.tobytes()).hexdigest(),
                    'native_playback_and_capture_performed': False,
                    'position_and_gain': 'not recorded; obtain from operator', 'raw_audio_publication_authorized': False}
        (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        if not args.generate_only:
            from .run import audient, capture
            index, device = audient()
            if float(device['default_samplerate']) != FS:
                raise RuntimeError('Set the Audient sample rate to 96000 Hz before acquisition.')
            print(f'Playing 14 separated tones over {len(waveform)/FS:.1f} seconds at {args.peak_dbfs:g} dBFS peak; recording Audient input 1.', flush=True)
            print('Keep monitoring off, hardware levels and geometry unchanged. Stop if any sound is unexpectedly loud.', flush=True)
            recording, timestamps, transport = capture(waveform, index)
            np.savez_compressed(folder / 'capture.npz', recording=recording, samplerate=FS, callback_timestamps=timestamps)
            manifest.update(device=device, native_playback_and_capture_performed=True, transport=transport)
            (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n')
            result = analyze(recording, events, transport)
            (folder / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
            print(json.dumps(result, indent=2, allow_nan=False))
        print(f'Local data: {folder.resolve()}. Keep raw room audio outside Git.')
    except (RuntimeError, ValueError, OSError, ImportError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
