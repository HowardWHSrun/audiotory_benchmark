"""Offline synthetic verification only; these tests are not bench measurements."""

import json
import unittest

import numpy as np

try:
    from .analysis import _normalized_correlations, analyze_trials
    from .stimulus import make_probe_plan
except ImportError:
    from analysis import _normalized_correlations, analyze_trials
    from stimulus import make_probe_plan


FS = 96_000


def synthetic_capture(delays=(1632, 1632, 1632), noise=0.002, inverted=False):
    rng = np.random.default_rng(3741)
    probe_samples = 9600
    windows = [(9600 + index * 30000, 19200 + index * 30000) for index in range(len(delays))]
    recording = np.zeros((windows[-1][1] + FS // 5, 2))
    recording[:, 0] = rng.normal(0, noise, len(recording))
    for (start, stop), delay in zip(windows, delays):
        probe = rng.normal(size=probe_samples)
        spectrum = np.fft.rfft(probe)
        frequency = np.fft.rfftfreq(len(probe), 1 / FS)
        spectrum[(frequency < 100) | (frequency > 20_000)] = 0
        probe = np.fft.irfft(spectrum) * np.hanning(probe_samples)
        probe *= 0.25 / max(np.abs(probe))
        recording[start:stop, 1] = probe
        recording[start + delay : stop + delay, 0] += (-0.4 if inverted else 0.4) * probe
    return recording, windows


def colored_probe_capture(delays=(1632,), noise=0.0005):
    """Synthetic low-pass acoustic path with a declared FIR group delay.

    This deliberately changes the microphone waveform, rather than only
    shifting an otherwise identical reference. It is not a speaker model or
    calibration record.
    """
    waveform, plan = make_probe_plan(repetitions=1, peak_dbfs=-18)
    start, stop = plan["trials"][0]["output_start"], plan["trials"][0]["output_stop"]
    reference = waveform[start:stop].astype(np.float64)
    reference *= 0.25 / np.max(np.abs(reference))
    group_delay = 96
    time = np.arange(-group_delay, group_delay + 1)
    taps = np.sinc(2 * 1600 * time / FS) * np.hanning(len(time))
    taps /= taps.sum()
    filtered = np.convolve(reference, taps)
    recording = np.zeros((len(waveform), 2))
    recording[:, 0] = np.random.default_rng(987).normal(0, noise, len(recording))
    recording[start:stop, 1] = reference
    for delay in delays:
        recording[start + delay : start + delay + len(filtered), 0] += 0.4 * filtered
    return recording, [(start, stop)], group_delay


class CorrelationTests(unittest.TestCase):
    def test_fft_normalization_matches_direct_pearson(self):
        rng = np.random.default_rng(901)
        reference = rng.normal(size=32) + 0.2
        microphone = rng.normal(size=96) - 0.7
        expected = [np.corrcoef(reference, microphone[index : index + 32])[0, 1] for index in range(65)]
        np.testing.assert_allclose(_normalized_correlations(reference, microphone), expected, atol=1e-12)

    def test_known_17_ms_with_noise_and_summary(self):
        recording, windows = synthetic_capture()
        result = analyze_trials(recording.astype(np.float32), FS, windows)
        self.assertEqual(result["summary"]["accepted_trials"], 3)
        self.assertEqual(result["summary"]["median_delay_ms"], 17.0)
        self.assertEqual(result["summary"]["jitter_p95_minus_p05_ms"], 0.0)
        self.assertEqual(result["summary"]["delay_trend_ms_per_minute"], 0.0)
        self.assertAlmostEqual(result["sample_interval_ms"], 1 / 96)
        self.assertTrue(all(trial["delay_samples"] == 1632 for trial in result["trials"]))
        self.assertTrue(all(trial["peak_correlation_abs"] > 0.97 for trial in result["trials"]))
        json.dumps(result, allow_nan=False)

    def test_inverted_polarity(self):
        recording, windows = synthetic_capture(delays=(1632,), inverted=True)
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertTrue(trial["accepted"])
        self.assertEqual(trial["delay_samples"], 1632)
        self.assertLess(trial["peak_correlation"], -0.97)

    def test_jitter_and_trend_use_accepted_trials(self):
        recording, windows = synthetic_capture(delays=(1631, 1632, 1633))
        result = analyze_trials(recording, FS, windows)
        summary = result["summary"]
        self.assertEqual(summary["accepted_trials"], 3)
        self.assertEqual(summary["median_delay_ms"], 17.0)
        self.assertAlmostEqual(summary["jitter_p95_minus_p05_ms"], 1.8 / 96)
        self.assertAlmostEqual(summary["delay_trend_ms_per_minute"], 2.0)

    def test_zero_reference_has_no_estimated_delay(self):
        recording, windows = synthetic_capture(delays=(1632,))
        recording[:, 1] = 0
        result = analyze_trials(recording, FS, windows)
        trial = result["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertIn("reference_missing_or_too_quiet", trial["reasons"])
        self.assertIsNone(trial["candidate_delay_samples"])
        self.assertIsNone(result["summary"]["median_delay_ms"])

    def test_zero_microphone_has_no_estimated_delay(self):
        recording, windows = synthetic_capture(delays=(1632,))
        recording[:, 0] = 0
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertIn("microphone_missing_or_too_quiet", trial["reasons"])
        self.assertIsNone(trial["delay_ms"])

    def test_unrelated_microphone_noise_rejected(self):
        recording, windows = synthetic_capture(delays=(1632,))
        recording[:, 0] = np.random.default_rng(409).normal(0, 0.02, len(recording))
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertIn("weak_correlation", trial["reasons"])

    def test_clipping_in_either_channel_rejected(self):
        for channel, reason in ((0, "microphone_clipping"), (1, "reference_clipping")):
            recording, windows = synthetic_capture(delays=(1632,))
            recording[windows[0][0] + 250, channel] = 1.0
            trial = analyze_trials(recording, FS, windows)["trials"][0]
            self.assertFalse(trial["accepted"])
            self.assertIn(reason, trial["reasons"])
            self.assertIsNone(trial["delay_ms"])

    def test_pure_tone_does_not_claim_unique_delay(self):
        recording = np.zeros((FS // 2, 2))
        start, stop, delay = 9600, 19200, 1632
        tone = 0.2 * np.sin(2 * np.pi * 1000 * np.arange(stop - start) / FS)
        recording[start:stop, 1] = tone
        recording[start + delay : stop + delay, 0] = tone * 0.5
        trial = analyze_trials(recording, FS, [(start, stop)])["trials"][0]
        self.assertGreater(trial["peak_correlation_abs"], 0.99)
        self.assertGreater(trial["secondary_peak_ratio"], 0.95)
        self.assertFalse(trial["accepted"])
        self.assertIn("ambiguous_peak_use_nonperiodic_probe", trial["reasons"])
        self.assertIsNone(trial["delay_ms"])

    def test_equal_echo_ambiguity_rejected(self):
        recording, windows = synthetic_capture(delays=(1632,), noise=0.0001)
        start, stop = windows[0]
        recording[start + 2500 : stop + 2500, 0] += 0.4 * recording[start:stop, 1]
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertIn("ambiguous_peak_use_nonperiodic_probe", trial["reasons"])

    def test_filtered_noisy_probe_does_not_count_peak_shoulder_as_alternative(self):
        recording, windows, group_delay = colored_probe_capture()
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertTrue(trial["accepted"])
        self.assertEqual(trial["delay_samples"], 1632 + group_delay)
        self.assertGreater(trial["peak_correlation_abs"], 0.6)
        self.assertGreater(trial["primary_lobe_width_samples"], 20)
        self.assertTrue(trial["primary_lobe_bounded_by_zero_crossings"])
        self.assertLess(trial["secondary_peak_ratio"], 0.95)
        # A point only four samples away remains on the broad primary lobe:
        # it must not be interpreted as a second independently plausible lag.
        start, stop = windows[0]
        correlation = _normalized_correlations(recording[start:stop, 1], recording[start:stop + FS // 10, 0])
        peak = trial["delay_samples"]
        self.assertGreater(abs(correlation[peak + 4] / correlation[peak]), 0.95)
        self.assertAlmostEqual(trial["primary_lobe_width_ms"],
                               trial["primary_lobe_width_samples"] * 1000 / FS)

    def test_filtered_probe_with_equal_separate_echo_is_still_ambiguous(self):
        # Equal filtered arrivals eight milliseconds apart produce distinct
        # correlation lobes while both signals fit the active probe window.
        recording, windows, _ = colored_probe_capture(delays=(1632, 2400))
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertGreaterEqual(trial["secondary_peak_ratio"], 0.95)
        self.assertIn("ambiguous_peak_use_nonperiodic_probe", trial["reasons"])
        self.assertIsNone(trial["delay_ms"])

    def test_primary_lobe_must_be_bounded_within_search(self):
        # A broad single-signed response with no observable right zero
        # crossing cannot establish a resolved correlation lobe.
        recording = np.zeros((800, 2))
        start, stop = 100, 164
        # A short search cuts through a Gaussian pulse's broad main lobe.
        samples = np.arange(64)
        pulse = 0.2 * np.exp(-((samples - 31.5) / 10) ** 2)
        recording[start:stop, 1] = pulse
        recording[start + 4:stop + 4, 0] = pulse
        trial = analyze_trials(recording, FS, [(start, stop)],
                               max_lag_ms=8 * 1000 / FS)["trials"][0]
        self.assertEqual(trial["candidate_delay_samples"], 4)
        self.assertFalse(trial["peak_at_search_boundary"])
        self.assertFalse(trial["primary_lobe_bounded_by_zero_crossings"])
        self.assertFalse(trial["accepted"])
        self.assertIn("primary_lobe_unresolved_at_search_boundary", trial["reasons"])

    def test_incomplete_microphone_search_rejected(self):
        recording, windows = synthetic_capture(delays=(1632,))
        recording = recording[: windows[0][1] + 5000]
        trial = analyze_trials(recording, FS, windows)["trials"][0]
        self.assertFalse(trial["accepted"])
        self.assertIn("incomplete_search_window", trial["reasons"])

    def test_boundary_peaks_are_unresolved(self):
        for delay in (0, FS // 10):
            recording, windows = synthetic_capture(delays=(delay,), noise=0.0001)
            trial = analyze_trials(recording, FS, windows)["trials"][0]
            with self.subTest(delay_samples=delay):
                self.assertEqual(trial["candidate_delay_samples"], delay)
                self.assertTrue(trial["peak_at_search_boundary"])
                self.assertFalse(trial["accepted"])
                self.assertIn("boundary_peak_unresolved", trial["reasons"])
                self.assertIsNone(trial["delay_ms"])

    def test_manifest_window_objects(self):
        recording, windows = synthetic_capture(delays=(1632,))
        objects = [{"start_sample": start, "stop_sample": stop} for start, stop in windows]
        self.assertTrue(analyze_trials(recording, FS, objects)["trials"][0]["accepted"])

    def test_invalid_recordings_and_windows(self):
        recording, windows = synthetic_capture(delays=(1632,))
        cases = [
            (recording[:, 0], FS, windows),
            (recording, 0, windows),
            (recording, FS, []),
            (recording, FS, [(-1, 100)]),
            (recording, FS, [(1, 2)]),
            (recording, FS, [(0.5, 100)]),
            (recording, FS, [(0, len(recording) + 1)]),
        ]
        for samples, fs, trial_windows in cases:
            with self.subTest(fs=fs, windows=trial_windows):
                with self.assertRaises(ValueError):
                    analyze_trials(samples, fs, trial_windows)
        recording[0, 0] = np.nan
        with self.assertRaises(ValueError):
            analyze_trials(recording, FS, windows)


if __name__ == "__main__":
    unittest.main()
