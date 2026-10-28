import unittest
import numpy as np
from latency.pip_level_check import FS, FREQUENCIES_HZ, N, make_pips, analyze
from latency.stimulus import _envelope


class PipLevelChecks(unittest.TestCase):
    def test_waveform_and_delayed_gain(self):
        gains={f:0.0 for f in FREQUENCIES_HZ}
        gains[4000]=-6.0
        wave,events=make_pips(gains)
        self.assertEqual(len(events),42)
        t=np.arange(N)/FS
        expected=(10**(-36/20)*np.sin(2*np.pi*2000*t)*_envelope(N,FS//500)).astype(np.float32)
        np.testing.assert_allclose(wave[events[0]['start_sample']:events[0]['stop_sample']],expected,atol=1e-8)
        # A synthetic fixed 38 ms delay and attenuation of microphone gain.
        delay=round(.038*FS)
        recording=np.zeros((len(wave),2),dtype=np.float32)
        recording[delay:,0]=wave[:-delay]*0.1
        result=analyze(recording,events,{'valid_transport':True})
        self.assertTrue(result['timing_reference']['valid'])
        self.assertAlmostEqual(result['timing_reference']['common_offset_ms'],38,delta=.6)
        self.assertAlmostEqual(result['rows'][1]['relative_to_2khz_db'],-6,delta=.1)
        self.assertTrue(all(r['passed_trials']==3 for r in result['rows']))
        recording[0,0]=1
        bad=analyze(recording,events,{'valid_transport':True})
        self.assertTrue(bad['microphone_clipping_screen_failed'])
        self.assertTrue(all(r['relative_to_2khz_db'] is None for r in bad['rows']))

    def test_silence_suppresses_results(self):
        wave,events=make_pips({f:0.0 for f in FREQUENCIES_HZ})
        result=analyze(np.zeros((len(wave),2)),events,{'valid_transport':True})
        self.assertFalse(result['timing_reference']['valid'])
        self.assertTrue(all(r['relative_to_2khz_db'] is None for r in result['rows']))
        with self.assertRaises(ValueError):
            make_pips({f:1.0 for f in FREQUENCIES_HZ})

if __name__=='__main__':
    unittest.main()
