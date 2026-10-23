"""Numerical checks only; no audio device access or sound playback."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

try:
    from .stimulus import (E_FREQUENCIES_HZ, _envelope, make_probe_plan,
                           make_sonic_e_block, write_stimulus)
except ImportError:
    from stimulus import (E_FREQUENCIES_HZ, _envelope, make_probe_plan,
                          make_sonic_e_block, write_stimulus)


class ProbeTests(unittest.TestCase):
    def test_default_plan_and_silence(self):
        signal, plan = make_probe_plan()
        self.assertEqual(signal.dtype, np.float32)
        self.assertEqual(len(plan["trials"]), 20)
        self.assertEqual(len(signal), 1113600)
        self.assertEqual(plan["duration_seconds"], 11.6)
        self.assertEqual(plan["trials"][0]["output_start"], 96000)
        self.assertEqual(plan["trials"][-1]["output_stop"], len(signal) - 96000)
        self.assertFalse(np.any(signal[:96000]))
        self.assertFalse(np.any(signal[-96000:]))
        reference = signal[96000:105600]
        for i, trial in enumerate(plan["trials"]):
            start, stop = trial["output_start"], trial["output_stop"]
            self.assertEqual(stop - start, 9600)
            self.assertEqual(start, 96000 + i * 48000)
            np.testing.assert_array_equal(signal[start:stop], reference)
            self.assertEqual(signal[start], 0)
            self.assertEqual(signal[stop - 1], 0)
            if i < 19:
                self.assertFalse(np.any(signal[stop:plan["trials"][i + 1]["output_start"]]))
        self.assertLessEqual(float(np.max(np.abs(signal))), 10 ** (-36 / 20) + 1e-8)
        self.assertFalse(plan["sonic_stimulus"])

    def test_probe_rates_preserve_units_and_chirp(self):
        low, a = make_probe_plan(96000, repetitions=1)
        high, b = make_probe_plan(192000, repetitions=1)
        for key in ("probe_duration_samples", "ramp_samples_each_end", "onset_spacing_samples",
                    "leading_silence_samples", "trailing_silence_samples", "sample_count"):
            self.assertEqual(b[key], 2 * a[key])
        # Away from ramp boundaries, shared sample times have identical phase.
        np.testing.assert_allclose(low[96000 + 2000:96000 + 7000],
                                   high[192000 + 4000:192000 + 14000:2], atol=2e-8)
        self.assertEqual(a["duration_seconds"], b["duration_seconds"])


class SonicTests(unittest.TestCase):
    def test_balance_bounds_and_determinism(self):
        signal, plan = make_sonic_e_block(tones_per_frequency=3)
        second, repeated = make_sonic_e_block(tones_per_frequency=3)
        np.testing.assert_array_equal(signal, second)
        self.assertEqual(plan, repeated)
        values, counts = np.unique(plan["sequence_hz"], return_counts=True)
        self.assertEqual(values.tolist(), list(E_FREQUENCIES_HZ))
        self.assertEqual(counts.tolist(), [3] * 14)
        self.assertEqual(plan["sample_count"], 42 * 960)
        for i, event in enumerate(plan["events"]):
            self.assertEqual(event["output_start"], i * 960)
            self.assertEqual(event["output_stop"], (i + 1) * 960)
            self.assertEqual(event["frequency_hz"], plan["sequence_hz"][i])
            self.assertEqual(signal[i * 960], 0)
            self.assertEqual(signal[(i + 1) * 960 - 1], 0)
        self.assertFalse(plan["exact_original_waveform"])
        self.assertFalse(plan["within_published_block_tone_count_range"])
        _, different = make_sonic_e_block(tones_per_frequency=3, seed=11)
        self.assertNotEqual(plan["sequence_hz"], different["sequence_hz"])

    def test_published_size_and_default_parameters(self):
        # The one default block is only 32 MB; no files are written by this check.
        signal, plan = make_sonic_e_block()
        self.assertEqual(plan["tone_count"], 8400)
        self.assertEqual(len(signal), 8064000)
        self.assertEqual(plan["duration_seconds"], 84)
        self.assertTrue(plan["within_published_block_tone_count_range"])
        self.assertEqual(plan["digital_peak_limit_dbfs"], -36)

    def test_rates_phase_and_ramp_units(self):
        low, a = make_sonic_e_block(96000, tones_per_frequency=1)
        high, b = make_sonic_e_block(192000, tones_per_frequency=1)
        self.assertEqual(a["sequence_hz"], b["sequence_hz"])
        self.assertEqual(b["sample_count"], 2 * a["sample_count"])
        self.assertEqual(a["tone_duration_samples"], 960)
        self.assertEqual(b["tone_duration_samples"], 1920)
        self.assertEqual(a["ramp_samples_each_end"], 192)
        self.assertEqual(b["ramp_samples_each_end"], 384)
        for i, frequency in enumerate(a["sequence_hz"]):
            env = _envelope(960, 192)
            expected = 10 ** (-36 / 20) * np.sin(2 * np.pi * frequency * np.arange(960) / 96000) * env
            np.testing.assert_allclose(low[i * 960:(i + 1) * 960], expected, atol=1e-9)
            np.testing.assert_allclose(low[i * 960 + 200:i * 960 + 700],
                                       high[i * 1920 + 400:i * 1920 + 1400:2], atol=1e-9)
        self.assertEqual(env[0], 0)
        self.assertEqual(env[-1], 0)
        self.assertEqual(env[191], 1)
        self.assertEqual(env[768], 1)
        np.testing.assert_array_equal(env, env[::-1])

    def test_invalid_parameters(self):
        for kwargs in ({"samplerate": 44100}, {"peak_dbfs": -17}, {"peak_dbfs": float("nan")},
                       {"tones_per_frequency": 0}, {"tones_per_frequency": 1.5}, {"seed": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                make_sonic_e_block(**kwargs)
        for kwargs in ({"repetitions": 0}, {"repetitions": True}, {"peak_dbfs": -61}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                make_probe_plan(**kwargs)

    def test_pcm24_and_manifest_hashes(self):
        signal, plan = make_sonic_e_block(tones_per_frequency=1)
        with tempfile.TemporaryDirectory() as temporary:
            paths = write_stimulus(signal, plan, temporary)
            wav_path = Path(paths["wav"])
            with wave.open(str(wav_path), "rb") as stream:
                self.assertEqual(stream.getparams()[:4], (1, 3, 96000, len(signal)))
                raw = np.frombuffer(stream.readframes(len(signal)), dtype=np.uint8).reshape(-1, 3)
            integers = raw[:, 0].astype(np.int32) | raw[:, 1].astype(np.int32) << 8 | raw[:, 2].astype(np.int32) << 16
            integers = np.where(integers & 0x800000, integers - 0x1000000, integers)
            np.testing.assert_allclose(integers / (2 ** 23), signal, atol=0.5 / (2 ** 23) + 1e-12)
            manifest = json.loads(Path(paths["manifest"]).read_text())
            self.assertEqual(manifest["wav_sha256"], hashlib.sha256(wav_path.read_bytes()).hexdigest())
            self.assertFalse(manifest["sound_played"])
            for line in Path(paths["sha256"]).read_text().splitlines():
                expected, filename = line.split("  ", 1)
                self.assertEqual(expected, hashlib.sha256((Path(temporary) / filename).read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()
