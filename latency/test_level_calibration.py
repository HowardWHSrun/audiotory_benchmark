import unittest
import numpy as np
from latency.level_calibration import FS, FREQUENCIES_HZ, make_probe, analyze


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


if __name__ == '__main__':
    unittest.main()
