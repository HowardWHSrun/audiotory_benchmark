import unittest

import numpy as np

from latency.level_calibration import FREQUENCIES_HZ, FS
from latency.pip_spl_estimate import estimate, reference_peak


class PipSplEstimateTests(unittest.TestCase):
    def test_reference_and_peak_conversion(self):
        t = np.arange(3 * FS) / FS
        a = np.zeros((3 * FS, 2), dtype=np.float32)
        a[:, 0] = .2 * np.sin(2 * np.pi * 1000 * t)
        reference, segments = reference_peak(a, 1000)
        self.assertAlmostEqual(reference, 20 * np.log10(.2), places=5)
        self.assertEqual(len(segments), 3)
        rows = [{'frequency_hz': f, 'pip_trials': [
            {'central_fundamental_peak_dbfs': reference - 20,
             'passes_background_screen': True} for _ in range(3)]} for f in FREQUENCIES_HZ]
        analysis = {'transport': {'valid_transport': True},
                    'microphone_clipping_screen_failed': False,
                    'timing_reference': {'valid': True}, 'rows': rows}
        output = estimate(reference, 94, analysis)
        self.assertAlmostEqual(output[0]['conditional_central_component_median_spl_db'], 74)
        correction = {f: 2.0 for f in FREQUENCIES_HZ}
        output = estimate(reference, 94, analysis, correction)
        self.assertAlmostEqual(output[0]['conditional_central_component_median_spl_db'], 72)
        rows[1]['pip_trials'][0]['passes_background_screen'] = False
        self.assertIsNone(estimate(reference, 94, analysis)[1]['conditional_central_component_median_spl_db'])
        analysis['timing_reference']['valid'] = False
        with self.assertRaises(ValueError):
            estimate(reference, 94, analysis)

    def test_clipped_reference_and_missing_response(self):
        a = np.ones((3 * FS, 1), dtype=np.float32)
        with self.assertRaises(ValueError):
            reference_peak(a, 1000)
        good = {'transport': {'valid_transport': True}, 'microphone_clipping_screen_failed': False,
                'timing_reference': {'valid': True},
                'rows': [{'frequency_hz': f, 'pip_trials': []} for f in FREQUENCIES_HZ]}
        with self.assertRaises(ValueError):
            estimate(-14, 114, good, {2000: 0})


if __name__ == '__main__':
    unittest.main()
