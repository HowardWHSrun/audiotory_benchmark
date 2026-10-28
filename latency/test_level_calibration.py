import unittest
import numpy as np
from latency.level_calibration import FS, FREQUENCIES_HZ, make_probe, analyze, derive_attenuations


class SeparatedToneChecks(unittest.TestCase):
    def test_gain_recovery_and_clipping_rejection(self):
        wave, events = make_probe(-48)
        self.assertEqual(len(events), 14)
        self.assertLessEqual(np.max(np.abs(wave)), 10**(-48/20) + 1e-8)
        # Simulated input delayed 50 ms, with known frequency-dependent losses.
        recording = np.zeros((len(wave), 2), np.float32)
        delay = int(.05 * FS)
        for i, event in enumerate(events):
            a, b = event['start_sample'], event['stop_sample']
            recording[a+delay:b+delay, 0] = wave[a:b] * (0.1 if i else 1)
        result = analyze(recording, events, {'valid_transport': True})
        self.assertTrue(all(r['passes_background_screen'] for r in result['rows']))
        self.assertAlmostEqual(result['rows'][1]['relative_to_2khz_db'], -20, places=2)
        recording[0, 0] = 1.
        result = analyze(recording, events, {'valid_transport': True})
        self.assertTrue(result['microphone_clipping_screen_failed'])
        self.assertIsNone(result['rows'][1]['relative_to_2khz_db'])
        result = analyze(recording * .1, events, {'valid_transport': False})
        self.assertIsNone(result['rows'][1]['relative_to_2khz_db'])

    def test_silence_and_validation(self):
        wave, events = make_probe()
        result = analyze(np.zeros((len(wave), 2)), events, {'valid_transport': True})
        self.assertEqual([r['frequency_hz'] for r in result['rows']], list(FREQUENCIES_HZ))
        self.assertTrue(all(not r['passes_background_screen'] and r['relative_to_2khz_db'] is None
                            for r in result['rows']))
        with self.assertRaises(ValueError):
            make_probe(-20)

    def test_attenuation_only_recovers_equal_levels(self):
        wave, events = make_probe(-36)
        base = np.zeros((len(wave), 2), np.float32)
        gains = np.linspace(1.0, .05, len(events))
        for i, event in enumerate(events):
            a, b = event['start_sample'], event['stop_sample']
            base[a:b, 0] = wave[a:b] * gains[i]
        baseline = analyze(base, events, {'valid_transport': True})
        manifest = {'native_playback_and_capture_performed': True, 'sample_rate_hz': FS,
                    'digital_peak_dbfs': -36, 'events': events}
        correction = derive_attenuations(baseline, manifest, -36)
        self.assertTrue(all(x <= 0 for x in correction.values()))
        corrected_wave, corrected_events = make_probe(-36, correction)
        self.assertLessEqual(np.max(np.abs(corrected_wave)), np.max(np.abs(wave)) + 1e-8)
        corrected = np.zeros_like(base)
        for i, event in enumerate(corrected_events):
            a, b = event['start_sample'], event['stop_sample']
            corrected[a:b, 0] = corrected_wave[a:b] * gains[i]
        result = analyze(corrected, corrected_events, {'valid_transport': True})
        for row in result['rows']:
            self.assertAlmostEqual(row['relative_to_2khz_db'], 0, places=3)
        # A subsequent measured drift receives only additional attenuation.
        event = corrected_events[4]
        corrected[event['start_sample']:event['stop_sample'], 0] *= .8
        second_analysis = analyze(corrected, corrected_events, {'valid_transport': True})
        corrected_manifest = dict(manifest, events=corrected_events,
                                  correction_source={'method': 'previous attenuation'})
        second = derive_attenuations(second_analysis, corrected_manifest, -36)
        self.assertTrue(all(second[f] <= correction[f] + 1e-12 for f in FREQUENCIES_HZ))
        second_wave, second_events = make_probe(-36, second)
        final = np.zeros_like(base)
        for i, event in enumerate(second_events):
            a, b = event['start_sample'], event['stop_sample']
            final[a:b, 0] = second_wave[a:b] * gains[i] * (.8 if i == 4 else 1)
        final_result = analyze(final, second_events, {'valid_transport': True})
        for row in final_result['rows']:
            self.assertAlmostEqual(row['relative_to_2khz_db'], 0, places=3)
        with self.assertRaises(ValueError):
            derive_attenuations(baseline, manifest, -35)
        bad = dict(baseline, microphone_clipping_screen_failed=True)
        with self.assertRaises(ValueError):
            derive_attenuations(bad, manifest, -36)
        bad = dict(baseline, rows=baseline['rows'][:-1])
        with self.assertRaises(ValueError):
            derive_attenuations(bad, manifest, -36)
        with self.assertRaises(ValueError):
            make_probe(-36, {freq: 1 for freq in FREQUENCIES_HZ})


if __name__ == '__main__':
    unittest.main()
