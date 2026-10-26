"""Offline fake-backend checks. No test accesses audio hardware or plays sound."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import wave

import numpy as np

from bench_app.engine import AudioEngine, source_provenance


class _CallbackStop(Exception):
    pass


class _CallbackAbort(Exception):
    pass


class FakeBackend:
    """Sample-index fake: declared delays are synthetic, never measurements."""
    CallbackStop = _CallbackStop
    CallbackAbort = _CallbackAbort
    __version__ = "synthetic-test-backend"

    def __init__(self, *, fail_rate=False, rate_offset=0, flags=False, clip=False,
                 nonfinite=False, silent=False, ambiguous=False, truncate=False,
                 slow=False, bad_timestamps=False):
        self.default = SimpleNamespace(device=(0, 0))
        self.fail_rate = fail_rate
        self.rate_offset = rate_offset
        self.flags = flags
        self.clip = clip
        self.nonfinite = nonfinite
        self.silent = silent
        self.ambiguous = ambiguous
        self.truncate = truncate
        self.slow = slow
        self.bad_timestamps = bad_timestamps
        self.opened = []
        self.checked = []
        self.started = threading.Event()

    def query_devices(self):
        return [dict(name="Synthetic interface", hostapi=0, max_input_channels=4,
                     max_output_channels=4, default_samplerate=96000)]

    def query_hostapis(self, index):
        return {"name": "Synthetic host"}

    def check_input_settings(self, **settings):
        self.checked.append(("input", settings))
        if self.fail_rate:
            raise RuntimeError("rate unsupported")

    def check_output_settings(self, **settings):
        self.checked.append(("output", settings))
        if self.fail_rate:
            raise RuntimeError("rate unsupported")

    def Stream(self, **settings):
        return FakeStream(self, settings, duplex=True)

    def OutputStream(self, **settings):
        return FakeStream(self, settings, duplex=False)


class FakeStream:
    def __init__(self, backend, settings, duplex):
        self.backend = backend
        self.settings = settings
        self.duplex = duplex
        self.samplerate = settings["samplerate"] + backend.rate_offset
        self.latency = (0.01, 0.02) if duplex else 0.02
        self.aborted = threading.Event()
        self.finished = threading.Event()
        self.worker = None
        self.output = []
        backend.opened.append(self)

    def __enter__(self):
        self.backend.started.set()
        self.worker = threading.Thread(target=self._run, daemon=True)
        self.worker.start()
        return self

    def __exit__(self, *_):
        self.abort()
        self.close()

    def abort(self):
        self.aborted.set()

    def close(self):
        if self.worker and self.worker is not threading.current_thread():
            self.worker.join(2)

    def _run(self):
        rate = self.settings["samplerate"]
        block = 1024
        channels = self.settings["channels"]
        inputs, outputs = channels if self.duplex else (0, channels)
        history = np.zeros((rate * 30, outputs), dtype=np.float32)
        position = 0
        mic_delay = int(rate * 0.030)
        reference_delay = int(rate * 0.024)
        flags = SimpleNamespace(input_underflow=False, input_overflow=self.backend.flags,
                                output_underflow=False, output_overflow=False, priming_output=False)
        try:
            while not self.aborted.is_set():
                output = np.zeros((block, outputs), dtype=np.float32)
                timing = SimpleNamespace(inputBufferAdcTime=1.0 + position / rate,
                                         outputBufferDacTime=1.02 + position / rate)
                if self.backend.bad_timestamps:
                    timing.inputBufferAdcTime = 0
                if self.duplex:
                    data = np.zeros((block, inputs), dtype=np.float32)
                    for channel, delay in ((0, mic_delay), (1, reference_delay)):
                        if channel >= inputs:
                            continue
                        start = position - delay
                        a, b = max(0, start), max(0, start + block)
                        if b > a:
                            source_channel = min(channel, outputs - 1)
                            data[max(0, -start):max(0, -start) + b - a, channel] = history[a:b, source_channel]
                    if self.backend.ambiguous and position > rate:
                        # Equal-energy echoes separated by 20 ms reject ambiguity.
                        start = position - mic_delay - rate // 50
                        a, b = max(0, start), max(0, start + block)
                        if b > a:
                            data[max(0, -start):max(0, -start) + b - a, 0] += history[a:b, 0]
                    if self.backend.silent:
                        data.fill(0)
                    if self.backend.clip:
                        data[0, 0] = 1.0
                    if self.backend.nonfinite:
                        data[0, 0] = np.nan
                try:
                    if self.duplex:
                        self.settings["callback"](data, output, block, timing, flags)
                    else:
                        self.settings["callback"](output, block, timing, flags)
                finally:
                    self.output.append(output.copy())
                    history[position:position + block] = output
                position += block
                if self.backend.truncate and position > rate:
                    break
                if self.backend.slow:
                    self.aborted.wait(0.01)
        except (_CallbackStop, _CallbackAbort):
            pass
        finally:
            self.finished.set()
            self.settings["finished_callback"]()


class EngineTests(unittest.TestCase):
    def test_windows_enables_asio_before_lazy_import(self):
        backend = FakeBackend()
        with patch.dict(os.environ, {}, clear=True), \
                patch("bench_app.engine.platform.system", return_value="Windows"), \
                patch("bench_app.engine.importlib.import_module", return_value=backend) as load:
            engine = AudioEngine(backend=None)
            self.assertIs(engine._audio(), backend)
            load.assert_called_once_with("sounddevice")
            self.assertEqual(os.environ["SD_ENABLE_ASIO"], "1")
            self.assertEqual(backend.opened, [])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.backend = FakeBackend()
        self.engine = AudioEngine(Path(self.directory.name) / "runs", backend=self.backend)

    def tearDown(self):
        self.engine.stop()
        if self.engine._thread:
            self.engine._thread.join(5)
        self.directory.cleanup()

    def finish(self):
        self.engine._thread.join(15)
        self.assertFalse(self.engine._thread.is_alive(), "synthetic worker did not finish")
        status = self.engine.status()
        json.dumps(status, allow_nan=False)
        return status

    def config(self, **overrides):
        return dict({"action": "calibrate", "device": 0, "repetitions": 3}, **overrides)

    def test_import_and_construction_are_silent_and_lazy(self):
        with patch("bench_app.engine.importlib.import_module", side_effect=AssertionError("backend import")):
            import bench_app.engine as module
            importlib.reload(module)
            engine = module.AudioEngine(Path(self.directory.name) / "unused")
            self.assertEqual(engine.status()["state"], "idle")
        self.assertEqual(self.backend.opened, [])

    def test_readonly_devices_never_opens_stream(self):
        result = self.engine.devices()
        self.assertEqual(result["devices"][0]["host_api"], "Synthetic host")
        self.assertEqual(result["devices"][0]["index"], 0)
        self.assertEqual(self.backend.opened, [])
        json.dumps(result, allow_nan=False)

    def test_provenance_is_available_without_audio(self):
        provenance = source_provenance()
        self.assertEqual(len(provenance), 6)
        self.assertTrue(all(len(digest) == 64 for digest in provenance.values()))
        self.assertEqual(self.backend.opened, [])

    def test_bad_configs_never_open_stream(self):
        for change in ({"device": 10}, {"device": True}, {"sample_rate": 44100},
                       {"output_channel": 5}, {"input_channel": 5}, {"peak_dbfs": -10},
                       {"peak_dbfs": float("nan")}, {"peak_dbfs": True}, {"repetitions": 2},
                       {"tones_per_frequency": 601}, {"seed": -1}, {"distance_m": 0},
                       {"reference_channel": 1}, {"reference_channel": 2, "reference_output_channel": 1},
                       {"mystery": "no"}):
            config = self.config()
            config.update(change)
            with self.subTest(change=change), self.assertRaises((ValueError, RuntimeError)):
                self.engine.start(config)
        self.assertEqual(self.backend.opened, [])
        self.assertFalse((Path(self.directory.name) / "runs").exists())

    def test_unsupported_rate_rejected_before_worker(self):
        self.backend.fail_rate = True
        with self.assertRaisesRegex(RuntimeError, "does not accept"):
            self.engine.start(self.config(sample_rate=192000))
        self.assertEqual(self.backend.opened, [])

    def test_reported_rate_mismatch_never_starts_stream(self):
        self.backend.rate_offset = 1
        self.engine.start(self.config())
        status = self.finish()
        self.assertEqual(status["state"], "failed")
        self.assertIn("instead of requested", status["message"])
        self.assertFalse(self.backend.started.is_set())
        self.assertFalse(status["result"]["usable_measurement"])
        manifest = json.loads((Path(status["run_path"]) / "manifest.json").read_text())
        self.assertTrue(manifest["native_audio_attempted"])
        self.assertFalse(manifest["native_audio_started"])

    def test_synthetic_roundtrip_lifecycle_and_private_provenance(self):
        self.engine.start(self.config())
        status = self.finish()
        self.assertEqual(status["state"], "completed", status)
        result = status["result"]
        self.assertTrue(result["usable_measurement"])
        self.assertEqual(result["mode"], "output_to_microphone_roundtrip")
        self.assertEqual(result["measured_delay_ms"], 30.0)
        self.assertEqual(result["summary"]["accepted_trials"], 3)
        self.assertIn("buffering", result["interpretation"])
        self.assertNotIn("reference_rms_fs", result["trials"][0])
        folder = Path(status["run_path"])
        manifest = json.loads((folder / "manifest.json").read_text())
        self.assertEqual(manifest["state"], "completed")
        self.assertTrue(manifest["source_sha256"]["latency/stimulus.py"])
        self.assertEqual(len(manifest["stimulus"]["trials"]), 3)
        self.assertIn("capture_float32.npy", manifest["artifacts_sha256"])
        self.assertFalse(manifest["raw_audio_publication_authorized"])
        self.assertTrue(manifest["native_audio_started"])
        self.assertTrue((folder / "microphone.wav").exists())
        # Windows uses inherited ACLs; st_mode cannot verify a POSIX mode there.
        if os.name == "posix":
            self.assertEqual(folder.stat().st_mode & 0o777, 0o700)
            self.assertEqual((folder / "capture_float32.npy").stat().st_mode & 0o777, 0o600)

    def test_synthetic_electrical_reference_at_both_sample_rates(self):
        for rate in (96000, 192000):
            with self.subTest(rate=rate):
                self.engine.start(self.config(sample_rate=rate, reference_channel=2))
                status = self.finish()
                self.assertEqual(status["state"], "completed", status)
                result = status["result"]
                self.assertEqual(result["mode"], "electrical_reference")
                self.assertEqual(result["measured_delay_ms"], 6.0)
                self.assertEqual(result["summary"]["accepted_trials"], 3)
                self.assertIn("input 2", result["interpretation"])
                with wave.open(str(Path(status["run_path"]) / "microphone.wav")) as exported:
                    self.assertEqual(exported.getframerate(), rate)
                np.testing.assert_array_equal(self.backend.opened[-1].output[100][:, 0],
                                              self.backend.opened[-1].output[100][:, 1])

    def test_stimulus_only_selected_output_and_exact_events(self):
        self.engine.start({"action": "stimulus", "device": 0, "tones_per_frequency": 1,
                           "output_channel": 2, "reference_channel": 2,
                           "reference_output_channel": 1})
        status = self.finish()
        self.assertEqual(status["state"], "completed", status)
        self.assertFalse(self.backend.opened[-1].duplex)
        output = np.concatenate(self.backend.opened[-1].output)
        self.assertTrue(np.all(output[:, 0] == 0))
        self.assertGreater(np.max(np.abs(output[:, 1])), 0)
        result = status["result"]
        self.assertEqual(result["tone_count"], 14)
        self.assertFalse(result["usable_measurement"])
        self.assertIsNone(result["measured_delay_ms"])
        folder = Path(status["run_path"])
        self.assertFalse((folder / "capture_float32.npy").exists())
        plan = json.loads((folder / "manifest.json").read_text())["stimulus"]
        self.assertEqual(plan["events"][0]["output_start"], 96000)
        self.assertEqual(len(plan["events"]), 14)

    def test_cancel_is_prompt_idempotent_and_never_valid(self):
        self.backend.slow = True
        self.engine.start(self.config(repetitions=10))
        self.assertTrue(self.backend.started.wait(2))
        with self.assertRaisesRegex(RuntimeError, "already active"):
            self.engine.start(self.config())
        begin = time.monotonic()
        self.engine.stop()
        self.engine.stop()
        status = self.finish()
        self.assertLess(time.monotonic() - begin, 2)
        self.assertEqual(status["state"], "cancelled")
        self.assertFalse(status["result"]["usable_measurement"])
        self.assertIsNone(status["result"]["measured_delay_ms"])
        manifest = json.loads((Path(status["run_path"]) / "manifest.json").read_text())
        self.assertFalse(manifest["usable_measurement"])
        self.assertEqual(self.engine.stop()["state"], "cancelled")

    def test_transport_rejects_overflow_clipping_nonfinite_short_and_bad_time(self):
        for attribute, expected in (("flags", "portaudio_callback_status_flag"), ("clip", "input_clipping"),
                                    ("nonfinite", "non_finite_audio"), ("truncate", "incomplete_capture"),
                                    ("bad_timestamps", "invalid_input_timestamps")):
            with self.subTest(attribute=attribute):
                setattr(self.backend, attribute, True)
                self.engine.start(self.config())
                status = self.finish()
                self.assertEqual(status["state"], "failed", status)
                self.assertFalse(status["result"]["usable_measurement"])
                self.assertIsNone(status["result"]["measured_delay_ms"])
                self.assertIn(expected, status["result"]["transport"]["transport_errors"])
                setattr(self.backend, attribute, False)

    def test_silence_and_ambiguous_echoes_reject_timing(self):
        for attribute in ("silent", "ambiguous"):
            with self.subTest(attribute=attribute):
                setattr(self.backend, attribute, True)
                self.engine.start(self.config())
                status = self.finish()
                self.assertEqual(status["state"], "failed", status)
                self.assertFalse(status["result"]["usable_measurement"])
                self.assertIsNone(status["result"]["measured_delay_ms"])
                self.assertEqual(status["result"]["summary"]["accepted_trials"], 0)
                setattr(self.backend, attribute, False)

    def test_missing_electrical_reference_fails_without_delay(self):
        self.backend.silent = True
        self.engine.start(self.config(reference_channel=2))
        status = self.finish()
        self.assertEqual(status["state"], "failed")
        self.assertIsNone(status["result"]["measured_delay_ms"])
        self.assertIn("Electrical reference", status["message"])


if __name__ == "__main__":
    unittest.main()
