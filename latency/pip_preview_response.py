"""Analyze a saved continuous SONIC preview; never access audio hardware.

The matched-frequency projection is a relative pickup screen, not SPL or a
qualified measurement of an individual pip. All analysis stays in .work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from .pip_response import (FS, WINDOW_SAMPLES, controls_for_frequency,
                           neighbour_clean_mask, projection_kernels)
from .stimulus import E_FREQUENCIES_HZ
from .transport import assess_timestamps


def db(value):
    return float(20 * np.log10(max(float(value), 1e-20)))


def analyze_arrays(source, recording, plan, manifest, align_ms=37.2):
    """Analyze 700 balanced contiguous pips at an externally supplied offset.

    A lag sensitivity check is performed, but no unique latency is inferred
    from periodic pips. Require clean neighbours, a minimum count, and a
    sufficient margin over both pre-block and in-block controls.
    """
    source = np.asarray(source)
    recording = np.asarray(recording)
    sequence = np.asarray(plan['sequence_hz'], dtype=int)
    events = plan['events']
    if (plan.get('sample_rate_hz') != FS or len(sequence) != 700
            or len(events) != 700 or plan.get('tone_duration_samples') != FS // 100
            or set(sequence) != set(E_FREQUENCIES_HZ)
            or any(np.count_nonzero(sequence == f) != 50 for f in E_FREQUENCIES_HZ)):
        raise ValueError('Expected a 700-pip balanced 96-kHz E14 preview.')
    if (source.ndim != 1 or recording.ndim != 2 or recording.shape[1] < 1
            or len(source) != len(recording) or not np.isfinite(recording).all()
            or not np.isfinite(source).all()):
        raise ValueError('Invalid source or recording.')
    if any(e['frequency_hz'] != int(sequence[i]) or e['output_start'] != i * 960
           or e['output_stop'] != (i + 1) * 960 for i, e in enumerate(events)):
        raise ValueError('Events do not match the contiguous preview sequence.')
    if not 0 <= align_ms <= 150:
        raise ValueError('Alignment must be in 0–150 ms.')
    starts = np.array([e['output_start'] for e in events], dtype=int)
    starts += int(manifest['plan_event_to_output_offset_samples'])
    kernel = projection_kernels(E_FREQUENCIES_HZ)
    steps = np.arange(WINDOW_SAMPLES)
    mic = recording[:, 0]
    baseline_starts = np.arange(FS // 8, 7 * FS // 8 - WINDOW_SAMPLES, WINDOW_SAMPLES)
    baseline = mic[baseline_starts[:, None] + steps] @ kernel.T
    base = np.sqrt(np.mean(abs(baseline) ** 2, axis=0))
    by_lag = []
    for lag in (align_ms - 1, align_ms, align_ms + 1):
        pos = starts + round(lag * FS / 1000) + round(.002 * FS)
        if pos.min() < 0 or pos.max() + WINDOW_SAMPLES > len(mic):
            raise ValueError('Alignment windows lie outside recording.')
        by_lag.append(mic[pos[:, None] + steps] @ kernel.T)
    src = source[(starts + round(.002 * FS))[:, None] + steps] @ kernel.T
    rows = []
    all_good = manifest.get('transport', {}).get('valid_transport') is True and np.max(abs(mic)) < .99
    for col, f in enumerate(E_FREQUENCIES_HZ):
        own = sequence == f
        clean = own & neighbour_clean_mask(sequence, f)
        control = controls_for_frequency(sequence, f)
        if not clean.any() or not control.any():
            raise ValueError('No usable clean events or in-block controls.')
        medians = [db(np.median(abs(x[clean, col]))) for x in by_lag]
        primary = medians[1]
        inblock = db(np.median(abs(by_lag[1][control, col])))
        preblock = db(base[col])
        above_inblock = primary - inblock
        above_baseline = primary - preblock
        timing_spread = max(medians) - min(medians)
        passes = (all_good and clean.sum() >= 5 and control.sum() >= 20
                  and above_inblock >= 10 and above_baseline >= 10
                  and timing_spread <= 3)
        rows.append({'frequency_hz': int(f), 'pip_count': int(own.sum()),
                     'clean_pip_count': int(clean.sum()), 'control_count': int(control.sum()),
                     'clean_median_fundamental_peak_dbfs': primary,
                     'clean_p05_fundamental_peak_dbfs': db(np.percentile(abs(by_lag[1][clean, col]), 5)),
                     'clean_p95_fundamental_peak_dbfs': db(np.percentile(abs(by_lag[1][clean, col]), 95)),
                     'source_median_fundamental_peak_dbfs': db(np.median(abs(src[own, col]))),
                     'above_preblock_db': above_baseline, 'above_inblock_db': above_inblock,
                     'alignment_window_spread_db': timing_spread,
                     'screen_passed': bool(passes), 'relative_to_2khz_db': None})
    ref = rows[0]
    if ref['screen_passed']:
        for row in rows:
            if row['screen_passed']:
                row['relative_to_2khz_db'] = row['clean_median_fundamental_peak_dbfs'] - ref['clean_median_fundamental_peak_dbfs']
    return {'purpose': 'continuous 700-pip pickup screen', 'alignment_ms': align_ms,
            'valid_transport': bool(manifest.get('transport', {}).get('valid_transport')),
            'input_peak_fs': float(np.max(abs(mic))), 'rows': rows,
            'limitations': ['Fixed lag is based on a separate isolated-pip run and checked at +/-1 ms; no current-run calibrated latency.',
                            'Central-window narrowband fundamental is not full-pip RMS, acoustic SPL, perceived loudness or a purity test.',
                            'Clean-neighbour exclusion and 10 dB control screens reduce but cannot eliminate ringing, leakage or distortion.',
                            'Only 50 pips per frequency before exclusions; screens are not uncertainty estimates.',
                            'M50 individual correction and exact ear geometry are not verified.']}


def analyze_folder(folder, align_ms=37.2):
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    plan = json.loads((folder / 'stimulus-plan.json').read_text())
    source = np.load(folder / 'output_float32.npy', allow_pickle=False)
    with np.load(folder / 'capture.npz', allow_pickle=False) as data:
        recording = data['recording']
        if int(data['samplerate'].item()) != FS:
            raise ValueError('Unexpected capture sample rate.')
        timestamps = data['callback_timestamps']
    if (manifest.get('native_playback_and_capture_performed') is not True
            or manifest.get('sample_rate_hz') != FS
            or hashlib.sha256(source.tobytes()).hexdigest() != manifest.get('output_float32_sha256')
            or assess_timestamps(timestamps, FS)['errors']):
        raise ValueError('Invalid acquisition, source hash, or callback timestamps.')
    return analyze_arrays(source, recording, plan, manifest, align_ms)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('folder', type=Path)
    p.add_argument('--alignment-ms', type=float, default=37.2)
    args = p.parse_args()
    try:
        result = analyze_folder(args.folder, args.alignment_ms)
        (args.folder / 'continuous-pip-analysis.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        print(json.dumps(result, indent=2, allow_nan=False))
    except (ValueError, OSError, KeyError) as e:
        p.exit(1, f'{e}\n')


if __name__ == '__main__':
    main()
