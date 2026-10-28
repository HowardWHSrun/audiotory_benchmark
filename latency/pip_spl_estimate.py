"""Conditional SPL estimates from saved calibrator and isolated pip recordings.

This offline analysis never opens an audio device. The measured central 6 ms
fundamental is neither the complete 10 ms waveform RMS nor a standardized
peak-equivalent SPL. A 1 kHz reference does not qualify ultrasonic response.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .level_calibration import FS, FREQUENCIES_HZ, sinusoid_amplitude
from .pip_level_check import analyze as analyze_pips
from .transport import assess_timestamps


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reference_peak(capture, frequency_hz):
    """Peak fundamental of each one-second reference segment, central 250 ms."""
    a = np.asarray(capture)
    if a.ndim != 2 or a.shape[1] < 1 or len(a) < FS * 3 or not np.isfinite(a).all():
        raise ValueError('Reference recording must contain at least 3 seconds of finite input 1.')
    if not 800 <= frequency_hz <= 1200:
        raise ValueError('Reference frequency must be a measured near-1 kHz calibrator tone.')
    if np.max(np.abs(a[:, 0])) >= .99:
        raise ValueError('Reference input is digitally clipped.')
    n = FS // 4
    peaks = []
    for second in range(len(a) // FS):
        start = second * FS + FS // 4
        value = sinusoid_amplitude(a[start:start+n, 0], frequency_hz)
        if value <= 1e-8:
            raise ValueError('Reference signal is missing or too weak.')
        peaks.append(float(20 * np.log10(value)))
    if max(peaks) - min(peaks) > 1.0:
        raise ValueError('Reference level varies by more than the 1 dB local screen.')
    return float(np.median(peaks)), peaks


def estimate(reference_dbfs, reference_spl, analysis, correction=None):
    """Convert saved peak fundamental results, screening each event.

    `correction` maps frequency to microphone sensitivity in dB relative to
    the near-1 kHz reference. Subtracting that term corrects mic sensitivity.
    Absence means explicitly assuming zero response difference, not measuring it.
    """
    if not np.isfinite(reference_dbfs) or not np.isfinite(reference_spl) or not 60 <= reference_spl <= 140:
        raise ValueError('Reference levels must be finite; reference SPL must be 60–140 dB.')
    if (analysis.get('transport', {}).get('valid_transport') is not True
            or analysis.get('microphone_clipping_screen_failed') is not False
            or analysis.get('timing_reference', {}).get('valid') is not True):
        raise ValueError('Pip transport, digital clipping and alignment must pass.')
    rows = analysis.get('rows', [])
    if [r.get('frequency_hz') for r in rows] != list(FREQUENCIES_HZ):
        raise ValueError('Pip analysis must contain the expected frequency set in order.')
    if correction is not None and set(correction) != set(FREQUENCIES_HZ):
        raise ValueError('Frequency response must cover all 14 frequencies; no extrapolation.')
    output = []
    for row in rows:
        frequency = row['frequency_hz']
        response_db = 0.0 if correction is None else float(correction[frequency])
        if not np.isfinite(response_db):
            raise ValueError('Frequency response values must be finite.')
        trials = []
        for event in row.get('pip_trials', []):
            value = event.get('central_fundamental_peak_dbfs')
            if event.get('passes_background_screen') is True and isinstance(value, (float, int)) and np.isfinite(value):
                trials.append(float(reference_spl + value - reference_dbfs - response_db))
            else:
                trials.append(None)
        if len(trials) != 3:
            raise ValueError('Expected exactly three trials per frequency.')
        median = float(np.median(trials)) if all(value is not None for value in trials) else None
        output.append({'frequency_hz': frequency,
                       'assumed_mic_response_relative_to_reference_db': response_db,
                       'conditional_central_component_spl_db_by_trial': trials,
                       'conditional_central_component_median_spl_db': median})
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True, help='Local calibrator reference folder')
    parser.add_argument('--pips', type=Path, required=True, help='Local isolated-pip run folder')
    parser.add_argument('--reference-spl', type=float, required=True, help='Operator-confirmed nominal calibrator SPL in dB')
    parser.add_argument('--assume-same-gain', action='store_true')
    parser.add_argument('--assume-calibrator-fit', action='store_true')
    parser.add_argument('--response-json', type=Path, help='Optional JSON mapping frequency Hz to microphone sensitivity relative to the reference, in dB')
    args = parser.parse_args()
    try:
        if not args.assume_same_gain or not args.assume_calibrator_fit:
            raise ValueError('Explicit --assume-same-gain and --assume-calibrator-fit are required.')
        ref_summary = json.loads((args.reference / 'analysis.json').read_text())
        with np.load(args.reference / 'capture.npz', allow_pickle=False) as capture:
            if int(capture['samplerate'].item()) != FS:
                raise ValueError('Unexpected reference sample rate.')
            ref_db, ref_trials = reference_peak(capture['recording'], float(ref_summary['frequency_hz']))
        pip_analysis = json.loads((args.pips / 'analysis.json').read_text())
        pip_manifest = json.loads((args.pips / 'manifest.json').read_text())
        if pip_manifest.get('native_playback_and_capture_performed') is not True or pip_manifest.get('sample_rate_hz') != FS:
            raise ValueError('Expected a completed 96 kHz pip capture.')
        waveform = np.load(args.pips / 'output_float32.npy', allow_pickle=False)
        if hashlib.sha256(waveform.tobytes()).hexdigest() != pip_manifest.get('output_sha256'):
            raise ValueError('Saved pip source waveform hash does not match its manifest.')
        with np.load(args.pips / 'capture.npz', allow_pickle=False) as capture:
            recorded = capture['recording']
            if (int(capture['samplerate'].item()) != FS or len(recorded) != len(waveform)
                    or assess_timestamps(capture['callback_timestamps'], FS)['errors']):
                raise ValueError('Pip capture sample rate, length or transport timestamps failed.')
            checked_analysis = analyze_pips(recorded, pip_manifest['events'], pip_manifest['transport'])
        if checked_analysis != pip_analysis:
            raise ValueError('Saved pip analysis does not match an independent analysis of the capture.')
        correction = None
        if args.response_json:
            raw = json.loads(args.response_json.read_text())
            correction = {int(k): float(v) for k, v in raw.items()}
        rows = estimate(ref_db, args.reference_spl, pip_analysis, correction)
        result = {'purpose': 'conditional, central 6 ms frequency-component SPL estimates for isolated 10 ms pips',
                  'reference_frequency_hz': float(ref_summary['frequency_hz']), 'reference_nominal_spl_db': args.reference_spl,
                  'reference_median_peak_dbfs': ref_db, 'reference_peak_dbfs_by_second': ref_trials,
                  'reference_capture_sha256': sha(args.reference / 'capture.npz'),
                  'reference_analysis_sha256': sha(args.reference / 'analysis.json'),
                  'pip_capture_sha256': sha(args.pips / 'capture.npz'),
                  'pip_manifest_sha256': sha(args.pips / 'manifest.json'), 'pip_analysis_sha256': sha(args.pips / 'analysis.json'),
                  'microphone_response_assumption': 'zero relative sensitivity difference from reference' if correction is None else 'user supplied relative response correction',
                  'response_file_sha256': None if args.response_json is None else sha(args.response_json),
                  'operator_assumptions': ['Calibrator delivers its nominal SPL and is fitted correctly.', 'Microphone gain/routing unchanged; chain is linear.',
                                           'Reference and pip peak sinusoid component amplitudes can be compared; RMS-to-peak cancels.'],
                  'rows': rows,
                  'limitations': ['Conditional estimate only: not validated 10 ms full-pip RMS or standardized peak-equivalent SPL.',
                                  'Calibrator model/output/traceability and acoustic fit are not independently verified.',
                                  'Reference capture has no callback transport log or on/off isolation check.',
                                  'Microphone calibration across frequency and free-field-to-coupler differences remain uncertain.',
                                  'Short central-window projection may be affected by timing, interference, ringing or distortion.',
                                  'Not a statement of equal perceived loudness, animal safety, or experiment readiness.']}
        out = args.pips / 'conditional-pip-spl-estimate.json'
        out.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(json.dumps(result, indent=2, allow_nan=False))
        print(f'Private analysis: {out.resolve()}')
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as error:
        parser.exit(1, f'{error}\n')


if __name__ == '__main__':
    main()
