"""Synthetic/offline roundtrip checks; never open an audio device."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import wave

import numpy as np

try:
    from .roundtrip import FS, analyze_roundtrip, analyze_saved_run
except ImportError:
    from latency.roundtrip import FS, analyze_roundtrip, analyze_saved_run


def fixture():
    rng = np.random.default_rng(1523)
    windows = [(9600 + i * 30000, 19200 + i * 30000) for i in range(3)]
    source = np.zeros(windows[-1][1] + FS // 5, dtype=np.float32)
    microphone = rng.normal(0, 0.0005, len(source)).astype(np.float32)
    for start, stop in windows:
        probe = rng.normal(0, 0.03, stop - start) * np.hanning(stop - start)
        source[start:stop] = probe
        microphone[start + 3672:stop + 3672] += 0.4 * probe
    transport = {"valid_transport": True, "transport_errors": [], "captured_frames": len(source)}
    return source, microphone, windows, transport


def write_saved(folder, source, microphone, windows, transport):
    recording = np.column_stack((microphone, np.zeros_like(microphone)))
    positions = np.arange(0, len(source), 512)
    adc = 100 + positions / FS
    timestamps = np.column_stack((positions, adc, adc + .03,
                                  np.full(len(positions), 512), np.zeros(len(positions))))
    np.save(folder / "output_float32.npy", source)
    np.savez(folder / "capture.npz", recording=recording, samplerate=FS,
             callback_timestamps=timestamps)
    manifest = {"sample_rate_hz": FS, "native_playback_and_capture_performed": True,
                "transport": transport, "output_sha256": hashlib.sha256(source.tobytes()).hexdigest(),
                "stimulus": {"kind": "timing_probe", "trials": [
                    {"output_start": start, "output_stop": stop} for start, stop in windows]}}
    (folder / "manifest.json").write_text(json.dumps(manifest))
    (folder / "analysis.json").write_text('{"original_electrical_analysis": true}\n')


class RoundtripTests(unittest.TestCase):
    def test_known_source_to_mic_lag_has_distinct_scope(self):
        source, microphone, windows, transport = fixture()
        result = analyze_roundtrip(source, microphone, FS, windows, transport)
        self.assertTrue(result["usable_measurement"])
        self.assertEqual(result["summary"]["accepted_trials"], 3)
        self.assertEqual(result["summary"]["median_delay_ms"], 38.25)
        self.assertIn("source_to_microphone", result["method"])
        self.assertIn("buffering", result["interpretation"])
        self.assertFalse(result["electrical_reference_required"])
        self.assertFalse(result["reported_driver_latency_added_or_subtracted"])
        self.assertIn("source_rms_fs", result["trials"][0])
        self.assertNotIn("reference_rms_fs", result["trials"][0])
        json.dumps(result, allow_nan=False)

    def test_missing_and_unrelated_source_do_not_produce_measurement(self):
        source, microphone, windows, transport = fixture()
        alternatives = (np.zeros_like(source),
                        np.random.default_rng(71).normal(0, .03, len(source)))
        for alternative in alternatives:
            with self.subTest(missing=not np.any(alternative)):
                result = analyze_roundtrip(alternative, microphone, FS, windows, transport)
                self.assertFalse(result["usable_measurement"])
                self.assertEqual(result["summary"]["accepted_trials"], 0)
                self.assertIsNone(result["summary"]["median_delay_ms"])

    def test_invalid_or_absent_transport_suppresses_summary_and_accepted_delays(self):
        source, microphone, windows, _ = fixture()
        cases = (None, {}, {"valid_transport": False, "transport_errors": ["overflow"]},
                 {"valid_transport": True, "transport_errors": ["overflow"]})
        for transport in cases:
            with self.subTest(transport=transport):
                result = analyze_roundtrip(source, microphone, FS, windows, transport)
                self.assertEqual(result["status"], "invalid_transport")
                self.assertEqual(result["summary"]["accepted_trials"], 0)
                self.assertIsNone(result["summary"]["median_delay_ms"])
                for trial in result["trials"]:
                    self.assertFalse(trial["accepted"])
                    self.assertIsNone(trial["delay_ms"])
                    self.assertEqual(trial["candidate_delay_samples"], 3672)

    def test_vector_lengths_dimensions_and_finite_samples_are_validated(self):
        source, microphone, windows, transport = fixture()
        for a, b in ((source[:-1], microphone), (source[:, None], microphone),
                     (source, microphone[:, None]), (source * np.nan, microphone)):
            with self.subTest(source_shape=a.shape, microphone_shape=b.shape):
                with self.assertRaises(ValueError):
                    analyze_roundtrip(a, b, FS, windows, transport)

    def test_saved_analysis_exports_audio_and_preserves_original_electrical_result(self):
        source, microphone, windows, transport = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            write_saved(folder, source, microphone, windows, transport)
            manifest_before = (folder / "manifest.json").read_bytes()
            original_before = (folder / "analysis.json").read_bytes()
            result = analyze_saved_run(folder)
            self.assertEqual(result["summary"]["median_delay_ms"], 38.25)
            self.assertEqual(manifest_before, (folder / "manifest.json").read_bytes())
            self.assertEqual(original_before, (folder / "analysis.json").read_bytes())
            self.assertTrue((folder / "roundtrip-analysis.json").exists())
            for filename in ("played-probes.wav", "microphone-input-1.wav"):
                with wave.open(str(folder / filename), "rb") as audio:
                    self.assertEqual(audio.getparams()[:4], (1, 3, FS, len(source)))

    def test_saved_source_mismatch_fails_and_raw_overflow_cannot_be_hidden_by_manifest(self):
        source, microphone, windows, transport = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            write_saved(folder, source, microphone, windows, transport)
            changed = source.copy(); changed[0] = .1
            np.save(folder / "output_float32.npy", changed)
            with self.assertRaisesRegex(ValueError, "hash"):
                analyze_saved_run(folder)
            np.save(folder / "output_float32.npy", source)
            with np.load(folder / "capture.npz") as saved:
                recording, rate, stamps = saved["recording"], saved["samplerate"], saved["callback_timestamps"]
            stamps[5, 4] = 2
            np.savez(folder / "capture.npz", recording=recording, samplerate=rate, callback_timestamps=stamps)
            result = analyze_saved_run(folder)
            self.assertFalse(result["usable_measurement"])
            self.assertIn("portaudio_callback_status_flag", result["transport"]["transport_errors"])
            self.assertIsNone(result["summary"]["median_delay_ms"])


if __name__ == "__main__":
    unittest.main()
