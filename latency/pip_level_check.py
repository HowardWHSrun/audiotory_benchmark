"""Measure isolated 10 ms SONIC-like pips using prior attenuation-only settings.

This is an acoustic bench screen, not original SONIC audio or calibrated SPL.
Raw captures are private under .work. No animal protocol is implied.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import numpy as np

from .level_calibration import FS, FREQUENCIES_HZ, make_probe, sinusoid_amplitude
from .stimulus import _envelope

ROOT = Path(__file__).resolve().parents[1]
N = FS // 100
RAMP = FS // 500
SPACING = round(.3 * FS)
SEARCH = round(.15 * FS)
# Local screening choice for three within-run pip levels; not an uncertainty bound.
MAX_TRIAL_SPREAD_DB = 3.0


def load_corrections(folder):
    folder = Path(folder)
    m = json.loads((folder / 'manifest.json').read_text())
    a = json.loads((folder / 'analysis.json').read_text())
    if m.get('native_playback_and_capture_performed') is not True or m.get('sample_rate_hz') != FS or m.get('digital_peak_dbfs') != -36:
        raise ValueError('Expected a completed 96 kHz, -36 dBFS reference run.')
    if a.get('transport', {}).get('valid_transport') is not True or a.get('microphone_clipping_screen_failed') is not False:
        raise ValueError('Reference must pass transport and input clipping screens.')
    if len(a.get('rows', [])) != len(FREQUENCIES_HZ) or not all(row.get('passes_background_screen') is True for row in a['rows']):
        raise ValueError('Reference must pass the per-frequency background screen.')
    events = m.get('events', [])
    if [e.get('frequency_hz') for e in events] != list(FREQUENCIES_HZ):
        raise ValueError('Reference frequencies do not match the expected set.')
    gains = {e['frequency_hz']: float(e['attenuation_db']) for e in events}
    if any(not np.isfinite(v) or v > 0 for v in gains.values()):
        raise ValueError('All reference corrections must be finite and non-positive.')
    wave = np.load(folder / 'output_float32.npy', allow_pickle=False)
    expected, _ = make_probe(-36, gains)
    if not np.array_equal(wave, expected) or hashlib.sha256(wave.tobytes()).hexdigest() != m.get('output_sha256'):
        raise ValueError('Reference waveform differs from its saved attenuation settings.')
    return gains, {'manifest_sha256': hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                   'analysis_sha256': hashlib.sha256((folder/'analysis.json').read_bytes()).hexdigest(),
                   'source_output_sha256': m['output_sha256']}


def make_pips(gains, repeats=3):
    if set(gains) != set(FREQUENCIES_HZ) or repeats < 3:
        raise ValueError('Need all frequencies and at least 3 repeats.')
    env = _envelope(N, RAMP)
    t = np.arange(N) / FS
    wave = np.zeros(FS + repeats * len(FREQUENCIES_HZ) * SPACING + FS, dtype=np.float32)
    # Repeated full-frequency passes preserve a time-separated observation per frequency.
    events = []
    for trial in range(repeats):
        for freq in FREQUENCIES_HZ:
            gain = float(gains[freq])
            if not np.isfinite(gain) or gain > 0:
                raise ValueError('Attenuation must be finite and non-positive.')
            start = FS + len(events) * SPACING
            wave[start:start+N] = (10 ** ((-36 + gain)/20) * np.sin(2*np.pi*freq*t) * env).astype(np.float32)
            events.append({'frequency_hz': freq, 'repeat': trial, 'start_sample': start,
                           'stop_sample': start+N, 'attenuation_db': gain})
    return wave, events


def derive_pip_corrections(folder, reuse_profile=False):
    """Attenuate previously measured isolated pips to the quietest component.

    All frequencies must have passed. Never boost any tone, and verify the saved
    source and capture screens before using it as a correction reference.
    """
    folder = Path(folder)
    manifest = json.loads((folder / 'manifest.json').read_text())
    analysis = json.loads((folder / 'analysis.json').read_text())
    if (manifest.get('native_playback_and_capture_performed') is not True
        or manifest.get('sample_rate_hz') != FS
        or manifest.get('digital_base_peak_dbfs') != -36
        or analysis.get('transport', {}).get('valid_transport') is not True
        or analysis.get('microphone_clipping_screen_failed') is not False
        or analysis.get('timing_reference', {}).get('valid') is not True):
        raise ValueError('Pip reference capture, timing, clipping, transport or sample rate is invalid.')
    events = manifest.get('events', [])
    if len(events) != 3 * len(FREQUENCIES_HZ):
        raise ValueError('Pip reference must contain three pips per frequency.')
    gains = {}
    for e in events:
        frequency=e.get('frequency_hz')
        try:
            gain=float(e['attenuation_db'])
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError('Pip reference has invalid gain.') from error
        if frequency not in FREQUENCIES_HZ or not np.isfinite(gain) or gain > 0:
            raise ValueError('Pip reference has an invalid or positive gain.')
        if frequency in gains and gain != gains[frequency]:
            raise ValueError('Pip reference has inconsistent gains.')
        gains[frequency]=gain
    expected, expected_events = make_pips(gains)
    if events != expected_events:
        raise ValueError('Pip reference event sequence does not match generated pips.')
    wave=np.load(folder / 'output_float32.npy', allow_pickle=False)
    if (not np.array_equal(wave,expected)
        or hashlib.sha256(wave.tobytes()).hexdigest() != manifest.get('output_sha256')):
        raise ValueError('Pip reference waveform does not match the manifest.')
    levels={}
    for row in analysis.get('rows', []):
        frequency=row.get('frequency_hz')
        value=row.get('median_central_fundamental_peak_dbfs')
        if (frequency not in FREQUENCIES_HZ or frequency in levels
            or row.get('passed_trials') != 3
            or isinstance(value,bool) or not isinstance(value,(int,float)) or not np.isfinite(value)
            or row.get('relative_to_2khz_db') is None):
            raise ValueError('Every frequency requires three valid measured pips.')
        trials=row.get('pip_trials', [])
        if len(trials)!=3 or any(t.get('passes_background_screen') is not True for t in trials):
            raise ValueError('Every frequency requires three background-qualified trials.')
        trial_levels=[t.get('central_fundamental_peak_dbfs') for t in trials]
        if any(isinstance(v,bool) or not isinstance(v,(int,float)) or not np.isfinite(v) for v in trial_levels):
            raise ValueError('Every qualifying trial must have a finite measured level.')
        if abs(float(np.median(trial_levels))-float(value)) > 1e-6:
            raise ValueError('The pip median does not agree with its three measured trials.')
        spread=max(trial_levels)-min(trial_levels)
        if spread > MAX_TRIAL_SPREAD_DB:
            raise ValueError(f'{frequency:g} Hz pip levels vary {spread:.2f} dB across trials; '
                             f'local screen allows at most {MAX_TRIAL_SPREAD_DB:g} dB.')
        levels[frequency]=float(value)
    if set(levels)!=set(FREQUENCIES_HZ):
        raise ValueError('Every frequency requires three valid measured pips.')
    target=min(levels.values())
    corrected=({f:float(gains[f]) for f in FREQUENCIES_HZ} if reuse_profile else
               {f:float(gains[f]+target-levels[f]) for f in FREQUENCIES_HZ})
    provenance={'method':('reuse validated isolated-pip attenuation profile' if reuse_profile else
                          'cumulative pip-specific attenuation to weakest measured frequency'),
                'manifest_sha256':hashlib.sha256((folder/'manifest.json').read_bytes()).hexdigest(),
                'analysis_sha256':hashlib.sha256((folder/'analysis.json').read_bytes()).hexdigest(),
                'source_output_sha256':manifest['output_sha256'],
                'target_mic_peak_dbfs':target,
                'maximum_within_frequency_trial_spread_db':MAX_TRIAL_SPREAD_DB,
                'attenuation_db_by_frequency_hz':{str(f):corrected[f] for f in FREQUENCIES_HZ}}
    return corrected, provenance


def _max_matched(segment, freq):
    env = _envelope(N, RAMP)
    t = np.arange(N) / FS
    sc = env * np.sin(2*np.pi*freq*t)
    cc = env * np.cos(2*np.pi*freq*t)
    # Solve the (slightly nonorthogonal) real basis at every lag.
    s = np.correlate(segment, sc, mode='valid')
    c = np.correlate(segment, cc, mode='valid')
    ss, ccv, cs = np.dot(sc,sc), np.dot(cc,cc), np.dot(sc,cc)
    det = ss*ccv-cs*cs
    x = (s*ccv-c*cs)/det
    y = (c*ss-s*cs)/det
    amp = np.hypot(x,y)
    pos = int(np.argmax(amp))
    return float(amp[pos]), pos


def analyze(recording, events, transport):
    a = np.asarray(recording)
    if a.ndim != 2 or a.shape[1] < 1 or not np.isfinite(a).all():
        raise ValueError('Expected finite two-dimensional microphone audio.')
    mic = a[:,0]
    clipped = float(np.max(np.abs(mic))) >= .99
    timing=[]
    for e in events:
        if e['frequency_hz'] != 2000:
            continue
        start=e['start_sample']
        segment=mic[start:start+SEARCH+N]
        if len(segment)!=SEARCH+N:
            raise ValueError('Incomplete capture for acoustic alignment.')
        amp,pos=_max_matched(segment,2000)
        timing.append({'offset_samples':pos,'matched_peak':amp})
    if len(timing)<3:
        raise ValueError('Need three reference pips for acoustic alignment.')
    offsets=np.array([v['offset_samples'] for v in timing])
    common_offset=int(np.median(offsets))
    timing_valid=bool(np.ptp(offsets)<=round(.002*FS) and 0<common_offset<SEARCH and all(v['matched_peak']>1e-8 for v in timing))
    grouped = defaultdict(list)
    n=round(.006*FS)
    for e in events:
        start, f = e['start_sample'], e['frequency_hz']
        pos=start+common_offset+round(.002*FS)
        bgpos=start-round(.01*FS)
        signal=mic[pos:pos+n]
        bg=mic[bgpos:bgpos+n]
        if len(signal)!=n or len(bg)!=n:
            raise ValueError('Insufficient samples to analyze pip and background.')
        amp=sinusoid_amplitude(signal,f)
        noise=sinusoid_amplitude(bg,f)
        snr=20*np.log10(max(amp,1e-15)/max(noise,1e-15))
        grouped[f].append({'central_fundamental_peak_dbfs':float(20*np.log10(max(amp,1e-15))),
                           'background_fundamental_peak_dbfs':float(20*np.log10(max(noise,1e-15))),
                           'tone_minus_background_db':float(snr),
                           'passes_background_screen':bool(amp>1e-8 and snr>=10)})
    rows=[]
    for f in FREQUENCIES_HZ:
        rec=grouped[f]
        valid=[v for v in rec if v['passes_background_screen']]
        rows.append({'frequency_hz': f, 'pip_trials': rec, 'passed_trials':len(valid),
                     'median_central_fundamental_peak_dbfs':float(np.median([v['central_fundamental_peak_dbfs'] for v in valid])) if len(valid)>=3 else None})
    reference=rows[0]['median_central_fundamental_peak_dbfs']
    valid_transport=transport.get('valid_transport',False)
    for row in rows:
        v=row['median_central_fundamental_peak_dbfs']
        row['relative_to_2khz_db'] = v-reference if v is not None and reference is not None and valid_transport and not clipped and timing_valid else None
    return {'purpose':'isolated 10 ms reconstructed pips; central 6 ms fundamental amplitude',
            'microphone_input_peak_fs':float(np.max(np.abs(mic))), 'microphone_clipping_screen_failed':clipped,
            'transport':transport,'timing_reference':{'common_offset_samples':common_offset,
             'common_offset_ms':common_offset/FS*1000,'2khz_offsets_ms':(offsets/FS*1000).tolist(),
             'valid':timing_valid,'interpretation':'Acoustic alignment for analysis only, not calibrated latency.'},'rows':rows,
            'limitations':['Separated 10 ms pips, not consecutive SONIC playback; no claim about original SONIC waveform.',
                           'The central 2–8 ms window uses a common current-run lag found from 2 kHz; frequency-dependent group delay may bias results.',
                           'Relative microphone pickup at the stimulus frequency; no individual microphone correction or verified dB SPL.',
                           'Three clean trials and 10 dB above narrowband background are screening rules, not uncertainty bounds.',
                           'No acoustic isolation, harmonic distortion, equal perceived loudness, actual ear geometry or animal suitability is established.']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    source=parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--reference',type=Path)
    source.add_argument('--flat-output',action='store_true',
                        help='Uncorrected pips: all frequencies at -36 dBFS digital peak')
    source.add_argument('--pip-reference',type=Path,
                        help='Derive attenuation-only correction from a screened prior pip run')
    parser.add_argument('--generate-only',action='store_true')
    args=parser.parse_args()
    try:
        if args.flat_output:
            gains={f:0.0 for f in FREQUENCIES_HZ}
            provenance={'method':'uncorrected flat digital peak output'}
        elif args.pip_reference:
            gains, provenance=derive_pip_corrections(args.pip_reference)
        else:
            gains, provenance=load_corrections(args.reference)
        wave, events=make_pips(gains)
        folder=ROOT/'.work/latency/runs'/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'-isolated-corrected-pips')
        folder.mkdir(parents=True,exist_ok=False)
        np.save(folder/'output_float32.npy',wave)
        manifest={'utc':datetime.now(timezone.utc).isoformat(),'sample_rate_hz':FS,'digital_base_peak_dbfs':-36,
                  'events':events,'provenance':provenance,'output_sha256':hashlib.sha256(wave.tobytes()).hexdigest(),
                  'native_playback_and_capture_performed':False,'raw_audio_publication_authorized':False}
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if not args.generate_only:
            from .run import audient,capture
            idx,dev=audient()
            if float(dev['default_samplerate']) != FS:
                raise RuntimeError('Set Audient current sample rate to 96000 Hz.')
            print(f'Playing {len(events)} separated 10 ms pips over {len(wave)/FS:.1f} seconds, attenuation-only at -36 dBFS base. Recording microphone.',flush=True)
            recording,timestamps,transport=capture(wave,idx)
            np.savez_compressed(folder/'capture.npz',recording=recording,samplerate=FS,callback_timestamps=timestamps)
            manifest.update(device=dev,native_playback_and_capture_performed=True,transport=transport)
            (folder/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
            result=analyze(recording,events,transport)
            (folder/'analysis.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
            print(json.dumps(result,indent=2,allow_nan=False))
        print(f'Local private capture: {folder.resolve()}')
    except (ValueError,RuntimeError,OSError,ImportError,KeyError) as e:
        parser.exit(1,f'{e}\n')

if __name__=='__main__':
    main()
