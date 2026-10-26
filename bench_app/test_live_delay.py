"""Synthetic waveform tests only; no audio device is opened or sound played."""
import json
import unittest
from unittest.mock import patch

import numpy as np

from bench_app.live_delay import LiveDelayTracker, _sonic_envelope_delay
from latency.stimulus import make_probe_plan, make_sonic_e_block


class LiveDelayTests(unittest.TestCase):
    def setUp(self):
        self.rate = 8000
        self.tracker = LiveDelayTracker()
        self.tracker.reset(self.rate)
        rng = np.random.default_rng(426)
        self.probe = (rng.standard_normal(800) * 0.025).astype(np.float32)
        self.source = np.zeros(1200, dtype=np.float32)
        self.source[200:1000] = self.probe
        self.plan = {"sample_rate_hz": self.rate,
                     "trials": [{"output_start": 200, "output_stop": 1000}]}

    def capture(self, *, delay=240, silent=False, clipped=False, echo=False, nonfinite=False,
                start_frame=0):
        data = np.zeros(start_frame + 3200, dtype=np.float32)
        if not silent:
            onset = start_frame + 200 + delay
            data[onset:onset + len(self.probe)] += self.probe
            if echo:
                data[onset + 400:onset + 400 + len(self.probe)] += self.probe
        if clipped:
            data[start_frame + 500] = 1.0
        if nonfinite:
            data[start_frame + 500] = np.nan
        self.tracker.add_probe(self.source, self.plan, start_frame)
        for offset in range(0, len(data), 127):
            self.tracker.push(data[offset:offset + 127])
        return self.tracker.snapshot()

    def test_default_delay_is_waveform_alignment_with_no_fake_initial_value(self):
        empty = self.tracker.snapshot()
        self.assertEqual(empty["points"], [])
        self.assertIsNone(empty["latest_delay_ms"])
        result = self.capture()
        self.assertEqual(result["mode"], "playback_to_microphone")
        self.assertTrue(result["points"][0]["accepted"])
        self.assertAlmostEqual(result["latest_delay_ms"], 30.0)
        self.assertIn("buffering", result["interpretation"])
        json.dumps(result, allow_nan=False)

    def test_generated_chirps_update_repeatedly_during_rolling_capture(self):
        source, plan = make_probe_plan(samplerate=96000, repetitions=3)
        self.tracker.reset(96000)
        self.tracker.add_probe(source, plan, 0)
        microphone = np.zeros(len(source) + 24000, dtype=np.float32)
        microphone[2880:2880 + len(source)] = source
        for start in range(0, len(microphone), 1024):
            self.tracker.push(microphone[start:start + 1024])
            if start % 10240 == 0:
                self.tracker.snapshot()
        points = self.tracker.snapshot()["points"]
        self.assertEqual(len(points), 3)
        self.assertTrue(all(point["accepted"] and point["delay_ms"] == 30.0 for point in points))

    def test_sonic_windows_match_bandlimited_microphone_without_ultrasound(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=100)
        frequency = np.fft.rfftfreq(len(source), 1 / rate)
        # This synthetic loudspeaker model removes every component above12kHz.
        bandlimited = np.fft.irfft(np.fft.rfft(source) * (frequency < 12000), len(source))
        microphone = np.zeros(len(source) + rate // 4, dtype=np.float32)
        microphone[2880:2880 + len(source)] = bandlimited
        microphone += np.random.default_rng(2026).normal(0, 0.0005, len(microphone)).astype(np.float32)
        plan = {"sample_rate_hz": rate, "source_kind": "sonic_sequence",
                "trials": [{"output_start": second * rate, "output_stop": second * rate + rate // 2}
                           for second in range(14)]}
        self.tracker.reset(rate)
        self.tracker.add_probe(source, plan, 0)
        for start in range(0, len(microphone), 1024):
            self.tracker.push(microphone[start:start + 1024])
            if start % 10240 == 0:
                self.tracker.snapshot()
        result = self.tracker.snapshot()
        self.assertEqual(result["source_kind"], "sonic_sequence")
        self.assertEqual(result["match_band_hz"], [1550.0, 10950.0])
        self.assertEqual(result["method"], "multiband_amplitude_envelope")
        self.assertAlmostEqual(result["search_step_ms"], 1 / 3)
        self.assertIn("amplitude envelopes", result["interpretation"])
        self.assertEqual(len(result["points"]), 14)
        self.assertTrue(all(p["accepted"] and p["delay_ms"] == 30 for p in result["points"]))

    def test_sonic_filter_does_not_hide_periodicity_silence_or_raw_clipping(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=10)
        plan = {"source_kind": "sonic_sequence",
                "trials": [{"output_start": 0, "output_stop": rate // 2}]}
        for kind in ("periodic", "silent", "clipped"):
            with self.subTest(kind=kind):
                values = source.copy()
                if kind == "periodic":
                    values = (0.02 * np.sin(2 * np.pi * 2000 * np.arange(len(source)) / rate)).astype(np.float32)
                microphone = np.zeros(rate, dtype=np.float32)
                if kind != "silent":
                    microphone[2880:] = values[:rate - 2880]
                if kind == "clipped":
                    microphone[10000] = 1.0
                self.tracker.reset(rate)
                self.tracker.add_probe(values, plan, 0)
                self.tracker.push(microphone)
                point = self.tracker.snapshot()["points"][0]
                self.assertFalse(point["accepted"])
                self.assertIsNone(point["delay_ms"])
                expected = {"periodic": "insufficient_reliable_frequency_bands", "silent": "microphone_missing_or_too_quiet",
                            "clipped": "microphone_clipping"}[kind]
                self.assertIn(expected, point["reason"])

    def test_sonic_envelopes_allow_uneven_response_and_causal_phase_filtering(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=100)
        raw = source[:3 * rate // 4]
        frequency = np.fft.rfftfreq(len(raw), 1 / rate)
        response = sum(gain * np.exp(-0.5 * ((frequency - center) / 300) ** 2)
                       for center, gain in ((2000, 1.0), (4000, 0.15), (6000, 0.05),
                                            (8000, 0.025), (9000, 0.01), (10500, 0.002)))
        uneven = np.fft.irfft(np.fft.rfft(raw) * response, len(raw))
        # Causal low-pass impulse response changes phase differently in each
        # tone band. The envelope delay includes this filter's small delay.
        kernel = np.exp(-np.arange(256) / 24)
        kernel /= kernel.sum()
        causal = np.convolve(raw, kernel)[:len(raw)]
        for name, signal in (("uneven", uneven), ("causal", causal)):
            with self.subTest(response=name):
                microphone = np.zeros(len(raw))
                microphone[2880:] = signal[:-2880]
                microphone += np.random.default_rng(876).normal(0, 5e-6, len(raw))
                result = _sonic_envelope_delay(source[:rate // 2], microphone, rate, 250)
                self.assertTrue(result["accepted"], result)
                self.assertLessEqual(abs(result["delay_ms"] - 30), result["search_step_ms"])
                self.assertGreaterEqual(len(result["useful_bands_hz"]), 3)

    def test_sonic_envelopes_reject_real_competing_echoes_noise_and_wrong_sequence(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=100)
        different, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=100, seed=123)
        raw = source[:3 * rate // 4]
        echo = np.zeros(len(raw))
        echo[2880:] += raw[:-2880]
        echo[6720:] += raw[:-6720]
        wrong = np.zeros(len(raw))
        wrong[2880:] = different[:len(raw) - 2880]
        noise = np.random.default_rng(876).normal(0, 0.002, len(raw))
        for name, microphone in (("echo", echo), ("noise", noise), ("wrong_sequence", wrong)):
            with self.subTest(signal=name):
                result = _sonic_envelope_delay(source[:rate // 2], microphone, rate, 250)
                self.assertFalse(result["accepted"], result)
                self.assertIsNone(result["delay_ms"])
                if name == "echo":
                    self.assertIn("ambiguous_envelope_delay_paths", result["reasons"])

    def test_wrong_order_screen_cannot_cherry_pick_only_matching_bands(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=10, seed=20261023)
        # This screen includes seed 8002, which previously produced an accidental
        # match when only its two correlated bands were retained. Every strong
        # eligible band must now contribute, including disagreeing evidence.
        for seed in range(8000, 8100):
            with self.subTest(seed=seed):
                other, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=10, seed=seed)
                microphone = np.zeros(rate, dtype=np.float32)
                microphone[2880:] = other[:rate - 2880]
                result = _sonic_envelope_delay(source[:rate // 2], microphone, rate, 250)
                self.assertFalse(result["accepted"], result)
                self.assertIsNone(result["delay_ms"])

    def test_equal_30_and_80_ms_echoes_reject_all_14_windows(self):
        rate = 96000
        source, _ = make_sonic_e_block(samplerate=rate, tones_per_frequency=100, seed=20261023)
        microphone = np.zeros(len(source) + rate // 2)
        microphone[2880:2880 + len(source)] += source
        microphone[7680:7680 + len(source)] += source
        for second in range(14):
            with self.subTest(second=second):
                start = second * rate
                result = _sonic_envelope_delay(source[start:start + rate // 2],
                                               microphone[start:start + 3 * rate // 4], rate, 250)
                self.assertFalse(result["accepted"], result)
                self.assertIsNone(result["delay_ms"])
                self.assertIn("ambiguous_envelope_delay_paths", result["reasons"])

    def test_debug_window_is_opt_in_bounded_and_does_not_expose_mutable_ring(self):
        self.assertIsNone(self.tracker.debug_recent_window())
        self.capture()
        first = self.tracker.debug_recent_window()
        self.assertEqual(len(first["microphone"]), 2800)
        first["microphone"].fill(0)
        self.assertGreater(np.max(np.abs(self.tracker.debug_recent_window()["microphone"])), 0)
        self.tracker.reset(self.rate)
        self.assertIsNone(self.tracker.debug_recent_window())

    def test_waits_for_full_future_search_tail(self):
        self.tracker.add_probe(self.source, self.plan, 0)
        self.tracker.push(np.zeros(2999, dtype=np.float32))
        self.assertEqual(self.tracker.snapshot()["points"], [])
        self.tracker.push(np.zeros(1, dtype=np.float32))
        self.assertEqual(len(self.tracker.snapshot()["points"]), 1)

    def test_silent_clipped_ambiguous_and_nonfinite_are_rejected(self):
        for options, expected in (({"silent": True}, "microphone_missing_or_too_quiet"),
                                  ({"clipped": True}, "microphone_clipping"),
                                  ({"echo": True}, "ambiguous_peak"),
                                  ({"nonfinite": True}, "non_finite_audio")):
            with self.subTest(options=options):
                self.tracker.reset(self.rate)
                result = self.capture(**options)
                self.assertFalse(result["points"][0]["accepted"])
                self.assertIsNone(result["latest_delay_ms"])
                self.assertIn(expected, result["points"][0]["reason"])
                json.dumps(result, allow_nan=False)

    def test_push_does_not_analyze_and_copies_callback_memory(self):
        self.tracker.add_probe(self.source, self.plan, 0)
        data = np.zeros(3200, dtype=np.float32)
        data[440:1240] = self.probe
        with patch("bench_app.live_delay.analyze_trials", side_effect=AssertionError("FFT in callback")):
            self.tracker.push(data)
        data.fill(0)
        self.assertAlmostEqual(self.tracker.snapshot()["latest_delay_ms"], 30.0)

    def test_nonzero_start_and_circular_wrap_preserve_coordinates(self):
        self.tracker.push(np.zeros(15000, dtype=np.float32))
        self.tracker.add_probe(self.source, self.plan, 15000)
        captured = np.zeros(3200, dtype=np.float32)
        captured[440:1240] = self.probe
        self.tracker.push(captured)
        point = self.tracker.snapshot()["points"][0]
        self.assertEqual(point["start_frame"], 15200)
        self.assertAlmostEqual(point["delay_ms"], 30.0)

    def test_nonzero_reset_origin_aligns_callback_samples_and_excludes_uncaptured_prefix(self):
        # Switching continuous playback on after monitoring has already run
        # retains absolute callback coordinates. The reset itself captures no
        # earlier samples, even when their ring slots have allocated memory.
        origin = 127123  # Deliberately wraps the 2-second ring during this input.
        self.tracker.reset(self.rate, start_frame=origin)
        self.assertEqual(self.tracker.snapshot()["captured_frames"], origin)
        self.tracker.add_probe(self.source, self.plan, origin - 400)
        self.tracker.add_probe(self.source, self.plan, origin)
        microphone = np.zeros(3200, dtype=np.float32)
        microphone[440:1240] = self.probe
        for start in range(0, len(microphone), 127):
            self.tracker.push(microphone[start:start + 127])
        result = self.tracker.snapshot()
        self.assertEqual(result["captured_frames"], origin + len(microphone))
        self.assertEqual(result["points"][0]["reason"], "capture_window_expired")
        self.assertIsNone(result["points"][0]["delay_ms"])
        self.assertEqual(result["points"][1]["start_frame"], origin + 200)
        self.assertTrue(result["points"][1]["accepted"])
        self.assertAlmostEqual(result["points"][1]["delay_ms"], 30.0)

    def test_overwritten_windows_reject_instead_of_estimating_wrong_samples(self):
        self.tracker.add_probe(self.source, self.plan, 0)
        self.tracker.push(np.zeros(20000, dtype=np.float32))
        point = self.tracker.snapshot()["points"][0]
        self.assertEqual(point["reason"], "capture_window_expired")
        self.assertIsNone(point["delay_ms"])

    def test_transport_invalidation_removes_accepted_and_pending_delays(self):
        self.assertAlmostEqual(self.capture()["latest_delay_ms"], 30.0)
        self.tracker.add_probe(self.source, self.plan, 8000)
        self.tracker.invalidate(["input_overflow", "input_clipping"])
        result = self.tracker.snapshot()
        self.assertFalse(result["available"])
        self.assertEqual(result["pending_trials"], 0)
        self.assertEqual(len(result["points"]), 2)
        self.assertTrue(all(not point["accepted"] and point["delay_ms"] is None
                            for point in result["points"]))
        self.assertIsNone(result["latest_delay_ms"])
        self.tracker.reset(self.rate)
        self.assertEqual(self.tracker.snapshot()["points"], [])
        self.assertTrue(self.tracker.snapshot()["available"])

    def test_history_is_bounded_and_electrical_mode_explicitly_unavailable(self):
        self.tracker = LiveDelayTracker(max_points=2)
        self.tracker.reset(self.rate)
        self.tracker.invalidate("dropped_audio")
        for start in (0, 1000, 2000):
            self.tracker.add_probe(self.source, self.plan, start)
        self.assertEqual([p["trial"] for p in self.tracker.snapshot()["points"]], [1, 2])
        self.tracker.reset(self.rate, has_reference=True)
        self.tracker.add_probe(self.source, self.plan, 0)
        self.tracker.push(np.zeros(3200, dtype=np.float32))
        result = self.tracker.snapshot()
        self.assertEqual(result["mode"], "electrical_reference")
        self.assertFalse(result["available"])
        self.assertIsNone(result["latest_delay_ms"])
        self.assertIn("Measure delay", result["reason"])

    def test_pending_bound_and_cancel_preserve_measured_history(self):
        self.tracker = LiveDelayTracker(max_pending=2)
        self.tracker.reset(self.rate)
        self.capture()
        for start in (8000, 16000, 24000):
            self.tracker.add_probe(self.source, self.plan, start)
        result = self.tracker.snapshot()
        self.assertEqual(result["pending_trials"], 2)
        self.assertEqual(result["points"][-1]["reason"], "pending_queue_overflow")
        saved = result["points"]
        self.tracker.cancel_pending()
        result = self.tracker.snapshot()
        self.assertEqual(result["pending_trials"], 0)
        self.assertEqual(result["points"], saved)


if __name__ == "__main__":
    unittest.main()
