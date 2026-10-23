"""Synthetic offline checks; no audio device access or experimental data."""
import unittest

import numpy as np

try:
    from .pip_response import (
        FS, WINDOW_SAMPLES, controls_for_frequency, group_metrics,
        neighbour_clean_mask, projection_kernels,
    )
except ImportError:
    from latency.pip_response import (
        FS, WINDOW_SAMPLES, controls_for_frequency, group_metrics,
        neighbour_clean_mask, projection_kernels,
    )


class PipProjectionTests(unittest.TestCase):
    def test_known_sine_rms_across_frequency_and_phase(self):
        time = np.arange(WINDOW_SAMPLES) / FS
        for frequency in (2000, 17000, 24000, 27000):
            for phase in (0, 0.6, 2.1):
                with self.subTest(frequency=frequency, phase=phase):
                    signal = 0.03 * np.sin(2 * np.pi * frequency * time + phase)
                    value = signal @ projection_kernels([frequency])[0]
                    self.assertAlmostEqual(abs(value) / np.sqrt(2), 0.03 / np.sqrt(2), delta=1e-6)

    def test_missing_distant_fundamental_and_silent_group(self):
        time = np.arange(WINDOW_SAMPLES) / FS
        four_khz = 0.03 * np.sin(2 * np.pi * 4000 * time)
        missing = four_khz @ projection_kernels([20900])[0]
        self.assertLess(abs(missing) / np.sqrt(2), 1e-6)
        silent = group_metrics(np.zeros(20, dtype=complex))
        self.assertEqual(silent["complex_phase_coherence"], 0)
        self.assertTrue(np.isfinite(silent["median_fundamental_rms_dbfs"]))

    def test_target_neighbours_and_near_harmonics_are_excluded(self):
        sequence = np.array([
            4000, 4000, 20900, 4000, 4000, 4000, 4000, 20900,
            10500, 4000, 4000, 4000, 20900, 20900, 4000, 4000,
        ])
        clean = neighbour_clean_mask(sequence, 20900)
        self.assertTrue(clean[2])  # Isolated target surrounded by nonharmonic 4-kHz pips.
        self.assertFalse(clean[7])  # 10.5-kHz neighbour has a 21-kHz second harmonic.
        self.assertFalse(clean[12])  # Repeated target neighbour can ring into this event.
        self.assertFalse(clean[13])
        off = controls_for_frequency(sequence, 20900)
        self.assertFalse(off[2])
        self.assertFalse(off[8])  # Current 10.5-kHz control is also excluded.


if __name__ == "__main__":
    unittest.main()
