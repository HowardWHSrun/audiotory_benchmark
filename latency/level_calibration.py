"""Measure separated-tone microphone pickup; this does not establish acoustic SPL.

Optional experimental corrections only attenuate individual output tones.
Recordings stay in the ignored .work directory.
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


def make_probe(peak_dbfs=-48.0, corrections=None):
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
    if corrections is not None and set(corrections) != set(FREQUENCIES_HZ):
        raise ValueError('Corrections must specify every test frequency exactly once.')
    for freq in FREQUENCIES_HZ:
        correction = 0.0 if corrections is None else float(corrections[freq])
        if not np.isfinite(correction) or correction > 0:
            raise ValueError('Corrections must be finite, non-positive attenuation values.')
        t = np.arange(duration) / FS
        parts.append((amplitude * 10 ** (correction / 20) * envelope * np.sin(2 * np.pi * freq * t)).astype(np.float32))
        events.append({'frequency_hz': freq, 'start_sample': cursor, 'stop_sample': cursor + duration,
                       'attenuation_db': correction})
        parts.append(np.zeros(gap, dtype=np.float32))
        cursor += duration + gap
    parts.append(np.zeros(FS, dtype=np.float32))
    return np.concatenate(parts), events


def derive_attenuations(analysis, manifest, peak_dbfs):
    """Attenuate stronger tones to the weakest measured pickup; never boost output.

    Accept a screened baseline or earlier corrected run. For an earlier corrected
    run, add further attenuation to each recorded prior setting. This does not
    correct microphone response or establish SPL at the animal's ears.
    """
    if manifest.get('native_playback_and_capture_performed') is not True:
        raise ValueError('Baseline must be an actual completed playback and capture.')
    if manifest.get('sample_rate_hz') != FS:
        raise ValueError('Baseline must use 96 kHz.')
    base_peak = manifest.get('digital_peak_dbfs')
    if isinstance(base_peak, bool) or not isinstance(base_peak, (int, float)) or not np.isfinite(base_peak) or peak_dbfs != base_peak:
        raise ValueError('Corrected digital peak must equal the baseline digital peak.')
    baseline_events = manifest.get('events', [])
    if len(baseline_events) != len(FREQUENCIES_HZ) or [e.get('frequency_hz') for e in baseline_events] != list(FREQUENCIES_HZ):
        raise ValueError('Baseline must contain the exact ordered set of frequencies.')
    previous = {}
    for e in baseline_events:
        attenuation = e.get('attenuation_db', 0)
        if (isinstance(attenuation, bool) or not isinstance(attenuation, (int, float))
                or not np.isfinite(attenuation) or attenuation > 0):
            raise ValueError('Prior attenuation must be a finite, non-positive value.')
        previous[e['frequency_hz']] = float(attenuation)
    if manifest.get('correction_source') is None and any(previous.values()):
        raise ValueError('Uncorrected baseline cannot contain previous attenuation.')
    if analysis.get('reference_hz') != 2000 or analysis.get('microphone_clipping_screen_failed') is not False or analysis.get('transport', {}).get('valid_transport') is not True:
        raise ValueError('Baseline transport, clipping and 2 kHz reference must pass.')
    rows = analysis.get('rows', [])
    if len(rows) != len(FREQUENCIES_HZ):
        raise ValueError('Baseline must have exactly one row for every test frequency.')
    levels = {}
    for row in rows:
        freq = row.get('frequency_hz')
        value = row.get('relative_to_2khz_db')
        if freq not in FREQUENCIES_HZ or freq in levels or row.get('passes_background_screen') is not True or isinstance(value, bool) or not isinstance(value, (float, int)) or not np.isfinite(value):
            raise ValueError('Every frequency needs one finite, screened baseline measurement.')
        levels[freq] = float(value)
    if set(levels) != set(FREQUENCIES_HZ) or abs(levels[2000]) > 1e-6:
        raise ValueError('The baseline reference or frequency list is invalid.')
    target = min(levels.values())
    return {freq: float(previous[freq] + target - levels[freq]) for freq in FREQUENCIES_HZ}


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
    parser.add_argument('--correction-analysis', type=Path,
                        help='Apply attenuation-only corrections from a screened previous run analysis.json')
    args = parser.parse_args()
    try:
        corrections = None
        correction_source = None
        if args.correction_analysis:
            analysis_path = args.correction_analysis.resolve()
            analysis = json.loads(analysis_path.read_text(encoding='utf-8'))
            manifest_path = analysis_path.parent / 'manifest.json'
            baseline_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            corrections = derive_attenuations(analysis, baseline_manifest, args.peak_dbfs)
            baseline_waveform = np.load(analysis_path.parent / 'output_float32.npy', allow_pickle=False)
            previous_attenuations = {e['frequency_hz']: float(e.get('attenuation_db', 0))
                                     for e in baseline_manifest['events']}
            expected_waveform, _ = make_probe(args.peak_dbfs, previous_attenuations)
            if (hashlib.sha256(baseline_waveform.tobytes()).hexdigest() != baseline_manifest.get('output_sha256')
                    or not np.array_equal(baseline_waveform, expected_waveform)):
                raise ValueError('Baseline waveform hash or per-tone source levels do not match its manifest.')
            correction_source = {'analysis_sha256': hashlib.sha256(analysis_path.read_bytes()).hexdigest(),
                                 'manifest_sha256': hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                                 'baseline_output_sha256': baseline_manifest['output_sha256'],
                                 'baseline_digital_peak_dbfs': baseline_manifest['digital_peak_dbfs'],
                                 'method': 'cumulatively attenuate all frequencies to weakest measured relative pickup',
                                 'attenuation_db_by_frequency_hz': {str(k): v for k, v in corrections.items()}}
        waveform, events = make_probe(args.peak_dbfs, corrections)
        folder = args.output or ROOT / '.work/latency/runs' / (datetime.now().strftime('%Y%m%d-%H%M%S-%f') + '-separated-levels')
        folder.mkdir(parents=True, exist_ok=False)
        np.save(folder / 'output_float32.npy', waveform)
        manifest = {'utc': datetime.now(timezone.utc).isoformat(), 'sample_rate_hz': FS,
                    'digital_peak_dbfs': args.peak_dbfs, 'events': events,
                    'correction_source': correction_source,
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
            if corrections is not None:
                result['limitations'][-1] = 'Experimental attenuation was applied; response remains uncorrected for microphone calibration.'
                result['correction_source'] = correction_source
            (folder / 'analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
            print(json.dumps(result, indent=2, allow_nan=False))
        print(f'Local data: {folder.resolve()}. Keep raw room audio outside Git.')
    except (RuntimeError, ValueError, OSError, ImportError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
