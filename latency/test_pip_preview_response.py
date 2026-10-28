import unittest

import numpy as np

from latency.pip_preview_response import analyze_arrays
from latency.stimulus import E_FREQUENCIES_HZ, make_sonic_e_block


class ContinuousPreviewChecks(unittest.TestCase):
    def test_clean_delayed_tones_and_failed_transport(self):
        fs = 96000
        signal, plan = make_sonic_e_block(samplerate=fs, tones_per_frequency=50,
                                         peak_dbfs=-36)
        source = np.concatenate([np.zeros(fs), signal, np.zeros(fs)]).astype(np.float32)
        # Impose a known, shared delay and realistic small background.
        lag = round(.0372 * fs)
        rng = np.random.default_rng(123)
        recorded = (rng.normal(0, 1e-7, len(source))).astype(np.float32)
        recorded[lag:] += source[:-lag] * .1
        audio = np.column_stack((recorded, np.zeros_like(recorded)))
        manifest = {'plan_event_to_output_offset_samples': fs,
                    'transport': {'valid_transport': True}}
        result = analyze_arrays(source, audio, plan, manifest)
        checked = [r for r in result['rows'] if r['relative_to_2khz_db'] is not None]
        self.assertGreaterEqual(len(checked), 10)
        self.assertLess(max(abs(r['relative_to_2khz_db']) for r in checked), .1)
        manifest['transport']['valid_transport'] = False
        rejected = analyze_arrays(source, audio, plan, manifest)
        self.assertTrue(all(r['relative_to_2khz_db'] is None for r in rejected['rows']))

    def test_silence_suppresses_all_results(self):
        fs = 96000
        signal, plan = make_sonic_e_block(samplerate=fs, tones_per_frequency=50,
                                         peak_dbfs=-36)
        source = np.concatenate([np.zeros(fs), signal, np.zeros(fs)]).astype(np.float32)
        audio = np.zeros((len(source), 2), dtype=np.float32)
        result = analyze_arrays(source, audio, plan,
                                {'plan_event_to_output_offset_samples': fs,
                                 'transport': {'valid_transport': True}})
        self.assertTrue(all(r['relative_to_2khz_db'] is None for r in result['rows']))


if __name__ == '__main__':
    unittest.main()
