import unittest
import numpy as np
from transport import assess_timestamps


class TransportTests(unittest.TestCase):
    def fixture(self):
        positions = np.arange(100) * 512
        adc = 100 + positions / 96000
        return np.column_stack((positions, adc, adc + .03, np.full(100, 512), np.zeros(100)))

    def test_common_clock_drift_is_diagnostic(self):
        log = self.fixture()
        log[:, 1:3] += log[:, :1] / 96000 * -130e-6
        result = assess_timestamps(log, 96000)
        self.assertEqual(result["errors"], [])
        self.assertAlmostEqual(result["clock_diagnostics"]["input"]["host_time_vs_nominal_sample_time_ppm"], -130, places=4)
        self.assertFalse(result["clock_diagnostics"]["host_clock_independently_calibrated"])

    def test_audio_status_flags_and_array_gap_fail(self):
        log = self.fixture(); log[5, 4] = 2
        self.assertIn("portaudio_callback_status_flag", assess_timestamps(log, 96000)["errors"])
        log = self.fixture(); log[10:, 0] += 512
        self.assertIn("noncontiguous_callback_array_positions", assess_timestamps(log, 96000)["errors"])

    def test_large_jump_and_nonmonotonic_timestamp_fail(self):
        log = self.fixture(); log[50:, 1:3] += .01
        self.assertIn("large_unexplained_input_timestamp_jump", assess_timestamps(log, 96000)["errors"])
        log = self.fixture(); log[50, 1] = log[49, 1]
        self.assertIn("invalid_input_timestamps", assess_timestamps(log, 96000)["errors"])


if __name__ == "__main__":
    unittest.main()
