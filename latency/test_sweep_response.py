"""Synthetic LTI and failure checks for the offline sweep-response screen."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from latency.stimulus import make_probe_plan
from latency.sweep_response import analyze_saved_run, analyze_sweeps


class SweepResponseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fs = 96000
        cls.source, cls.plan = make_probe_plan(96000, repetitions=5, peak_dbfs=-24)
        # A real causal one-pole lowpass with known DC gain and sample delay.
        pole = .8
        kernel = (1 - pole) * pole ** np.arange(128)
        filtered = np.convolve(cls.source, kernel) * .3
        cls.microphone = np.concatenate((np.zeros(3500), filtered))[:len(cls.source)]
        cls.transport = {"valid_transport": True, "transport_errors": []}

    def test_recovers_known_causal_gain_and_frequency_rolloff(self):
        result = analyze_sweeps(self.source, self.microphone, self.plan, self.fs,
                                self.transport, centers=[200, 500, 1000, 2000, 4000, 8000])
        rows = {row["frequency_hz"]: row for row in result["bands"]}
        for frequency in [200, 500, 1000, 2000, 4000, 8000]:
            row = rows[frequency]
            self.assertTrue(row["accepted"], row)
            expected_gain = .3 * .2 / abs(1 - .8 * np.exp(-2j * np.pi * frequency / self.fs))
            self.assertLess(abs(20 * np.log10(row["h1_rms_magnitude_diagnostic"] / expected_gain)), .08)
        self.assertLess(rows[8000]["relative_to_2khz_db"], -5)

    def test_invalid_transport_suppresses_all_relative_levels(self):
        result = analyze_sweeps(self.source, self.microphone, self.plan, self.fs,
                                {"valid_transport": False, "transport_errors": ["dropout"]}, centers=[1000, 2000])
        self.assertTrue(all(not row["accepted"] and row["relative_to_2khz_db"] is None for row in result["bands"]))

    def test_missing_source_does_not_become_zero_db_gain(self):
        result = analyze_sweeps(np.zeros_like(self.source), self.microphone, self.plan,
                                self.fs, self.transport, centers=[1000, 2000])
        self.assertTrue(all(row["relative_to_2khz_db"] is None and not row["accepted"] for row in result["bands"]))
        self.assertTrue(all("weak_source_excitation" in row["rejection_reasons"] for row in result["bands"]))

    def test_taper_weakened_upper_endpoint_is_rejected_even_for_perfect_lti(self):
        result = analyze_sweeps(self.source, self.microphone, self.plan, self.fs,
                                self.transport, centers=[200, 2000, 19000, 20000])
        row = next(row for row in result["bands"] if row["frequency_hz"] == 20000)
        self.assertIn("weak_source_excitation", row["rejection_reasons"])
        self.assertIsNone(row["relative_to_2khz_db"])

    def test_one_trial_cannot_artificially_have_perfect_coherence(self):
        plan = dict(self.plan, trials=self.plan["trials"][:1])
        with self.assertRaises(ValueError):
            analyze_sweeps(self.source, self.microphone, plan, self.fs, self.transport)

    def test_saved_run_requires_matching_source_and_raw_transport(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            np.save(folder / "output_float32.npy", self.source)
            times = np.arange(0, len(self.source), 1000, dtype=float)
            log = np.column_stack((times, 100 + times / self.fs, 100.03 + times / self.fs,
                                   np.full(len(times), 1000), np.zeros(len(times))))
            log[1, 4] = 4  # A real saved callback flag must override a stale valid manifest.
            np.savez(folder / "capture.npz", recording=np.column_stack((self.microphone, self.microphone)),
                     samplerate=self.fs, callback_timestamps=log)
            manifest = {"output_sha256": hashlib.sha256(self.source.tobytes()).hexdigest(),
                        "native_playback_and_capture_performed": True, "sample_rate_hz": self.fs,
                        "stimulus": self.plan, "transport": dict(self.transport, captured_frames=len(self.source))}
            (folder / "manifest.json").write_text(json.dumps(manifest))
            result = analyze_saved_run(folder)
            self.assertFalse(result["transport_valid"])
            self.assertIn("portaudio_callback_status_flag", result["transport_errors"])
            self.assertTrue(all(row["relative_to_2khz_db"] is None for row in result["bands"]))
            manifest["output_sha256"] = "wrong"
            (folder / "manifest.json").write_text(json.dumps(manifest))
            with self.assertRaises(ValueError):
                analyze_saved_run(folder)


if __name__ == "__main__":
    unittest.main()
