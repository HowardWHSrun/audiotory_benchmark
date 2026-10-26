"""Offline live-display checks; all waveforms and devices here are synthetic."""
from __future__ import annotations

import json
import math
from pathlib import Path
import tempfile
import threading
import time
import unittest

import numpy as np

from bench_app.live import LiveAudioBuffer


class LiveBufferTests(unittest.TestCase):
    def setUp(self):
        self.live = LiveAudioBuffer()
        self.live.reset(96000, has_input=True)

    def snapshot(self, **options):
        result = self.live.snapshot(**options)
        # No NaNs or infinity may reach the HTTP JSON response, including silence.
        json.dumps(result, allow_nan=False)
        return result

    def test_empty_buffer_is_empty_without_example_data(self):
        result = self.snapshot()
        self.assertEqual(result["frames"], 0)
        self.assertFalse(result["active"])
        self.assertEqual(result["output"]["min"], [])
        self.assertEqual(result["output"]["max"], [])
        self.assertIsNone(result["age_ms"])
        self.assertEqual(result["output"]["peak_dbfs"], -120)

    def test_wrapped_history_keeps_recent_samples_in_time_order(self):
        self.live.reset(1000, has_input=True)
        self.live.push(np.full(1000, .1, np.float32), np.full(1000, -.1, np.float32))
        self.live.push(np.full(250, .8, np.float32), np.full(250, -.8, np.float32))
        result = self.snapshot(active=True)
        self.assertEqual(result["frames"], 1250)
        self.assertTrue(result["active"])
        self.assertAlmostEqual(result["window_ms"], 500)
        for name in ("output", "microphone"):
            channel = result[name]
            self.assertGreater(len(channel["min"]), 0)
            self.assertLessEqual(len(channel["min"]), 400)
            self.assertEqual(len(channel["min"]), len(channel["max"]))
            self.assertTrue(np.all(np.asarray(channel["min"]) <= channel["max"]))
        self.assertAlmostEqual(result["output"]["min"][0], .1, places=5)
        self.assertAlmostEqual(result["output"]["max"][-1], .8, places=5)
        self.assertAlmostEqual(result["microphone"]["min"][0], -.1, places=5)
        self.assertAlmostEqual(result["microphone"]["max"][-1], -.8, places=5)
        self.assertAlmostEqual(result["output"]["peak_dbfs"], 20 * math.log10(.8), places=3)
        self.assertFalse(result["output"]["clipped"])

    def test_output_only_stream_never_invents_microphone_data(self):
        self.live.reset(96000, has_input=False)
        self.live.push(np.full(1000, .25, np.float32))
        result = self.snapshot(active=True)
        self.assertFalse(result["has_input"])
        self.assertIsNone(result["microphone"])
        self.assertEqual(result["spectrum"]["frequency_hz"], [])
        self.assertEqual(result["spectrum"]["dbfs"], [])

    def test_spectrum_locates_microphone_frequency_and_is_bounded(self):
        rate, frequency = 96000, 4000
        time_samples = np.arange(rate // 2, dtype=np.float64) / rate
        microphone = (.1 * np.sin(2 * np.pi * frequency * time_samples)).astype(np.float32)
        self.live.push(np.zeros_like(microphone), microphone)
        result = self.snapshot(active=True)
        frequencies = np.asarray(result["spectrum"]["frequency_hz"])
        magnitudes = np.asarray(result["spectrum"]["dbfs"])
        self.assertGreater(len(frequencies), 0)
        self.assertLessEqual(len(frequencies), 512)
        self.assertEqual(len(frequencies), len(magnitudes))
        self.assertTrue(np.all(np.diff(frequencies) > 0))
        self.assertLess(abs(float(frequencies[np.argmax(magnitudes)]) - frequency), 150)
        self.assertLessEqual(float(frequencies[-1]), 48000)

    def test_clipping_and_bad_samples_are_visible_without_invalid_json(self):
        output = np.array([0, .1, 1.0, np.nan, np.inf], dtype=np.float32)
        microphone = np.array([0, -.1, -1.0, -np.inf, np.nan], dtype=np.float32)
        self.live.push(output, microphone, status_bits=2)
        result = self.snapshot(active=True)
        self.assertTrue(result["output"]["clipped"])
        self.assertTrue(result["microphone"]["clipped"])
        self.assertIn("non_finite_audio", result["transport_errors"])
        self.assertTrue(result["transport_errors"])

    def test_reset_drops_old_audio_and_transport_errors(self):
        self.live.push(np.ones(1000, np.float32), np.ones(1000, np.float32), status_bits=2)
        self.live.reset(192000, has_input=False)
        result = self.snapshot()
        self.assertEqual(result["sample_rate_hz"], 192000)
        self.assertEqual(result["frames"], 0)
        self.assertEqual(result["transport_errors"], [])
        self.assertIsNone(result["microphone"])
        self.assertEqual(result["output"]["max"], [])


class LiveMonitorTests(unittest.TestCase):
    def setUp(self):
        from bench_app.engine import AudioEngine
        from bench_app.test_engine import FakeBackend
        self.directory = tempfile.TemporaryDirectory()
        self.output = Path(self.directory.name) / "runs"
        self.backend = FakeBackend(slow=True)
        self.engine = AudioEngine(self.output, backend=self.backend)

    def tearDown(self):
        self.engine.stop()
        if self.engine._thread:
            self.engine._thread.join(5)
        self.directory.cleanup()

    def wait_for(self, condition, timeout=3):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if condition():
                return
            time.sleep(.01)
        self.fail("Synthetic monitor did not reach the expected state")

    def test_monitor_stays_silent_until_explicit_probe_and_saves_no_room_audio(self):
        self.assertFalse(self.engine.live()["active"])
        self.assertEqual(self.backend.opened, [])
        with self.assertRaises(RuntimeError):
            self.engine.play_live_probe()
        self.engine.start({"action": "monitor", "device": 0, "repetitions": 3})
        self.wait_for(lambda: self.engine.live()["frames"] >= 4096)
        self.assertEqual(self.engine.status()["state"], "running")
        self.assertTrue(self.engine.live()["active"])
        self.assertEqual(float(np.max(np.abs(np.concatenate(self.backend.opened[0].output)))), 0)
        self.assertFalse(self.output.exists(), "Live monitoring must not save room audio")
        self.engine.play_live_probe()
        with self.assertRaises(RuntimeError):
            self.engine.play_live_probe()
        self.wait_for(lambda: any(np.any(block) for block in self.backend.opened[0].output))
        stream = self.backend.opened[0]
        native_calls = []
        original_abort, original_close = stream.abort, stream.close

        def audit_abort():
            native_calls.append(("abort", threading.get_ident()))
            return original_abort()

        def audit_close():
            native_calls.append(("close", threading.get_ident()))
            return original_close()

        stream.abort, stream.close = audit_abort, audit_close
        self.engine.stop()
        self.engine._thread.join(3)
        self.assertFalse(self.engine._thread.is_alive())
        self.assertFalse(self.engine.live()["active"])
        self.assertTrue(self.backend.opened[0].aborted.is_set())
        self.assertTrue(native_calls)
        self.assertEqual({thread_id for _, thread_id in native_calls}, {self.engine._thread.ident},
                         "Native stop/close must be serialized on the audio worker")
        self.assertFalse(self.output.exists())
        json.dumps(self.engine.live(), allow_nan=False)

    def test_unexpected_stream_end_marks_live_data_inactive(self):
        self.backend.truncate = True
        self.engine.start({"action": "monitor", "device": 0, "repetitions": 3})
        self.engine._thread.join(4)
        self.assertFalse(self.engine._thread.is_alive())
        self.assertEqual(self.engine.status()["state"], "failed")
        self.assertIn("stopped unexpectedly", self.engine.status()["message"])
        self.assertFalse(self.engine.live()["active"])
        self.assertFalse(self.output.exists())

    def test_monitor_rejects_mismatched_rate_before_playback(self):
        self.backend.rate_offset = 1
        self.engine.start({"action": "monitor", "device": 0, "repetitions": 3})
        self.engine._thread.join(3)
        self.assertFalse(self.engine._thread.is_alive())
        self.assertEqual(self.engine.status()["state"], "failed")
        self.assertFalse(self.backend.started.is_set())
        self.assertFalse(self.engine.live()["active"])
        self.assertFalse(self.output.exists())

    def test_sonic_loop_requires_explicit_enable_and_can_return_to_silence(self):
        with self.assertRaises(RuntimeError):
            self.engine.set_live_sonic(True)
        self.engine.start({"action": "monitor", "device": 0, "repetitions": 3})
        self.wait_for(lambda: self.engine.live()["frames"] >= 4096)
        self.assertFalse(self.engine.live()["sonic_playing"])
        self.assertFalse(any(np.any(block) for block in self.backend.opened[0].output))
        for invalid in (1, "true", None):
            with self.subTest(enabled=invalid), self.assertRaises((TypeError, ValueError)):
                self.engine.set_live_sonic(invalid)
        self.engine.set_live_sonic(True)
        self.wait_for(lambda: any(np.any(block) for block in self.backend.opened[0].output))
        self.assertTrue(self.engine.live()["sonic_playing"])
        with self.assertRaises(RuntimeError):
            self.engine.play_live_probe()
        self.engine.set_live_sonic(False)
        blocks_at_disable = len(self.backend.opened[0].output)
        self.wait_for(lambda: len(self.backend.opened[0].output) > blocks_at_disable + 3)
        self.assertFalse(self.engine.live()["sonic_playing"])
        self.assertTrue(all(not np.any(block) for block in self.backend.opened[0].output[-2:]))
        self.engine.play_live_probe()
        with self.assertRaises(RuntimeError):
            self.engine.set_live_sonic(True)
        self.engine.stop()
        self.engine._thread.join(3)
        self.assertFalse(self.engine._thread.is_alive())
        self.assertFalse(self.engine.live()["active"])
        self.assertFalse(self.engine.live()["sonic_playing"])
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
