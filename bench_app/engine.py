"""Native audio jobs for the local bench app; importing this module is silent.

Hardware is accessed only by devices() (inspection) or an explicit start().
The optional backend has the sounddevice API, allowing offline tests without
opening a real stream. Raw captures and generated audio stay in output_root.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import threading
import time
import uuid
import wave

import numpy as np

from latency.analysis import analyze_trials, _normalized_correlations, _primary_lobe_bounds
from latency.stimulus import make_probe_plan, make_sonic_e_block
from latency.transport import assess_timestamps


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / ".work" / "bench_app" / "runs"


def _json_write(path, value):
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    temporary.chmod(0o600)
    temporary.replace(path)


def _integer(value, name, low, high):
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f"{name} must be an integer between {low} and {high}")
    return value


def _flag_bits(flags):
    return sum(int(bool(getattr(flags, name, False))) << bit for bit, name in enumerate(
        ("input_underflow", "input_overflow", "output_underflow", "output_overflow", "priming_output")))


def _hash_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_provenance():
    """Hash required bundled source files; safe for offline packaging checks."""
    return {path.relative_to(ROOT).as_posix(): _hash_file(path) for path in (
        Path(__file__).resolve(), ROOT / "latency/stimulus.py", ROOT / "latency/analysis.py",
        ROOT / "latency/transport.py")}


def _write_pcm24(path, waveform, samplerate):
    """Human-readable mono export; original float arrays retain raw input values."""
    waveform = np.asarray(waveform)
    if waveform.ndim != 1 or not np.isfinite(waveform).all():
        raise ValueError("PCM24 export requires a finite mono waveform")
    with wave.open(str(path), "wb") as stream:
        stream.setnchannels(1)
        stream.setsampwidth(3)
        stream.setframerate(samplerate)
        for start in range(0, len(waveform), 65536):
            integers = np.clip(np.rint(waveform[start:start + 65536].astype(np.float64) * 2**23),
                               -2**23, 2**23 - 1).astype("<i4")
            stream.writeframesraw(integers.view(np.uint8).reshape(-1, 4)[:, :3].tobytes())
    path.chmod(0o600)


class AudioEngine:
    """One explicitly started job at a time; status() is always JSON serializable."""

    def __init__(self, output_root=DEFAULT_OUTPUT_ROOT, backend=None):
        self.output_root = Path(output_root).resolve()
        self._backend = backend
        self._lock = threading.RLock()
        self._stop = threading.Event()
        self._thread = None
        self._stream = None
        self._status = {"state": "idle", "action": None, "progress": 0.0,
                        "message": "Ready. No audio has started.", "result": None,
                        "run_path": None, "errors": [], "config": None}

    def _audio(self):
        if self._backend is None:
            try:
                self._backend = importlib.import_module("sounddevice")
            except (ImportError, OSError) as error:
                raise RuntimeError("Native audio is unavailable. Install the app's audio dependencies and restart. "
                                   + str(error)) from error
        return self._backend

    def devices(self):
        """Inspect devices without recording or playback; indices are process-local."""
        try:
            backend = self._audio()
            defaults = tuple(backend.default.device)
            devices = []
            for index, raw in enumerate(backend.query_devices()):
                item = dict(raw)
                host = backend.query_hostapis(item["hostapi"])
                devices.append({"index": index, "name": str(item["name"]),
                                "host_api": str(host["name"]),
                                "max_input_channels": int(item["max_input_channels"]),
                                "max_output_channels": int(item["max_output_channels"]),
                                "default_sample_rate": float(item["default_samplerate"]),
                                "is_default_input": index == defaults[0],
                                "is_default_output": index == defaults[1]})
            return {"devices": devices, "default_input": int(defaults[0]),
                    "default_output": int(defaults[1]), "backend_available": True, "errors": []}
        except Exception as error:
            return {"devices": [], "default_input": None, "default_output": None,
                    "backend_available": False, "errors": [str(error)]}

    def status(self):
        with self._lock:
            return deepcopy(self._status)

    def _update(self, **values):
        with self._lock:
            self._status.update(values)

    def _validate(self, raw):
        if not isinstance(raw, dict):
            raise ValueError("Configuration must be a JSON object")
        allowed = {"action", "device", "sample_rate", "output_channel", "input_channel",
                   "reference_channel", "reference_output_channel", "peak_dbfs", "repetitions",
                   "tones_per_frequency", "seed", "distance_m"}
        if set(raw) - allowed:
            raise ValueError("Unknown configuration fields: " + ", ".join(sorted(set(raw) - allowed)))
        config = dict(action="calibrate", sample_rate=96000, output_channel=1, input_channel=1,
                      reference_channel=None, reference_output_channel=2, peak_dbfs=-36,
                      repetitions=10, tones_per_frequency=600, seed=20261023, distance_m=None)
        config.update(raw)
        if config["action"] not in ("stimulus", "calibrate"):
            raise ValueError("action must be stimulus or calibrate")
        if config["action"] == "stimulus":
            # A saved calibration form must not silently drive a second output
            # when the user switches to the separate stimulus playback action.
            config["reference_channel"] = None
            config["reference_output_channel"] = None
        _integer(config.get("device"), "device", 0, 100000)
        if isinstance(config["sample_rate"], bool) or config["sample_rate"] not in (96000, 192000):
            raise ValueError("sample_rate must be 96000 or 192000 Hz")
        config["sample_rate"] = int(config["sample_rate"])
        for name in ("input_channel", "output_channel"):
            _integer(config[name], name, 1, 256)
        if config["action"] == "calibrate" and config["reference_channel"] is not None:
            _integer(config["reference_channel"], "reference_channel", 1, 256)
            _integer(config["reference_output_channel"], "reference_output_channel", 1, 256)
            if config["reference_channel"] == config["input_channel"]:
                raise ValueError("Electrical reference and microphone input channels must be distinct")
            if config["reference_output_channel"] == config["output_channel"]:
                raise ValueError("Speaker and electrical reference output channels must be distinct")
        elif config["reference_output_channel"] is not None:
            _integer(config["reference_output_channel"], "reference_output_channel", 1, 256)
        level = config["peak_dbfs"]
        if isinstance(level, bool) or not isinstance(level, (int, float)) or not math.isfinite(level) or not -60 <= level <= -18:
            raise ValueError("peak_dbfs must be finite and between -60 and -18 dBFS")
        config["peak_dbfs"] = float(level)
        _integer(config["repetitions"], "repetitions", 3, 40)
        _integer(config["tones_per_frequency"], "tones_per_frequency", 1, 600)
        _integer(config["seed"], "seed", 0, 2**63 - 1)
        distance = config["distance_m"]
        if distance is not None:
            if isinstance(distance, bool) or not isinstance(distance, (int, float)) or not math.isfinite(distance) or distance <= 0:
                raise ValueError("distance_m must be a finite positive distance, or null")
            config["distance_m"] = float(distance)
        backend = self._audio()
        devices = list(backend.query_devices())
        if config["device"] >= len(devices):
            raise ValueError("Selected audio device is no longer available; refresh the device list")
        device = dict(devices[config["device"]])
        output_channels = [config["output_channel"]]
        if config["action"] == "calibrate" and config["reference_channel"] is not None:
            output_channels.append(config["reference_output_channel"])
        if max(output_channels) > int(device["max_output_channels"]):
            raise ValueError("Selected output channel exceeds the device's available output channels")
        input_channels = [config["input_channel"]]
        if config["reference_channel"] is not None:
            input_channels.append(config["reference_channel"])
        try:
            backend.check_output_settings(device=config["device"], channels=max(output_channels),
                                          dtype="float32", samplerate=config["sample_rate"])
            if config["action"] == "calibrate":
                if max(input_channels) > int(device["max_input_channels"]):
                    raise ValueError("Selected input channel exceeds the device's available input channels")
                backend.check_input_settings(device=config["device"], channels=max(input_channels),
                                             dtype="float32", samplerate=config["sample_rate"])
        except ValueError:
            raise
        except Exception as error:
            raise RuntimeError(f"Device does not accept the requested {config['sample_rate']} Hz/channel format: {error}") from error
        device["host_api_name"] = str(backend.query_hostapis(device["hostapi"])["name"])
        return config, device

    def start(self, config):
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise RuntimeError("An audio job is already active; stop it before starting another")
            config, device = self._validate(config)
            self._stop = threading.Event()
            self._status = {"state": "running", "action": config["action"], "progress": 0.0,
                            "message": "Preparing the explicitly requested audio job.",
                            "result": None, "run_path": None, "errors": [], "config": config}
            self._thread = threading.Thread(target=self._worker, args=(config, device),
                                            name="sonic-native-audio", daemon=True)
            self._thread.start()
            return deepcopy(self._status)

    def stop(self):
        with self._lock:
            if self._status["state"] in ("running", "stopping"):
                self._stop.set()
                self._status.update(state="stopping", message="Stopping audio; this run will be marked cancelled.")
                stream = self._stream
            else:
                stream = None
        if stream is not None:
            try:
                stream.abort()
            except Exception:
                # The worker also sees the stop event; callback zeroes its output
                # before checking that event, including during a concurrent abort.
                pass
        return self.status()

    def _capture(self, waveform, config, on_started=None):
        backend = self._audio()
        fs = config["sample_rate"]
        duplex = config["action"] == "calibrate"
        total = len(waveform)
        inputs = [config["input_channel"] - 1]
        outputs = [config["output_channel"] - 1]
        if duplex and config["reference_channel"] is not None:
            inputs.append(config["reference_channel"] - 1)
            outputs.append(config["reference_output_channel"] - 1)
        recording = np.empty((total, len(inputs)), dtype=np.float32) if duplex else None
        # At least 16 frames per callback is a conservative capacity bound. An
        # unexpected smaller block is rejected instead of growing in callback.
        log = np.empty((total // 16 + 256, 5), dtype=np.float64)
        position = 0
        log_position = 0
        errors = []
        complete = threading.Event()

        def process(indata, outdata, frames, timing, flags):
            nonlocal position, log_position
            outdata.fill(0)
            if self._stop.is_set():
                raise backend.CallbackAbort
            try:
                count = min(int(frames), total - position)
                if count <= 0 or log_position >= len(log):
                    raise RuntimeError("invalid_callback_size_or_log_capacity")
                if duplex:
                    recording[position:position + count] = indata[:count, inputs]
                for channel in outputs:
                    outdata[:count, channel] = waveform[position:position + count]
                log[log_position] = (position, float(timing.inputBufferAdcTime) if duplex else 0.0,
                                     float(timing.outputBufferDacTime), int(frames), _flag_bits(flags))
                log_position += 1
                position += count
            except Exception as error:
                outdata.fill(0)
                errors.append(f"callback_error: {error}")
                raise backend.CallbackAbort
            if position >= total:
                raise backend.CallbackStop

        def output_callback(outdata, frames, timing, flags):
            return process(None, outdata, frames, timing, flags)

        stream_args = dict(device=(config["device"], config["device"]) if duplex else config["device"],
                           samplerate=fs, channels=(max(inputs) + 1, max(outputs) + 1) if duplex else max(outputs) + 1,
                           dtype="float32", blocksize=0, latency="low",
                           callback=process if duplex else output_callback, finished_callback=complete.set)
        constructor = backend.Stream if duplex else backend.OutputStream
        stream = constructor(**stream_args)
        with self._lock:
            self._stream = stream
        reported_latency = None
        try:
            # Inspect before entering: a mismatched reported rate must never play.
            actual_rate = float(stream.samplerate)
            if not math.isfinite(actual_rate) or abs(actual_rate - fs) > 1e-6:
                raise RuntimeError(f"Stream reported {actual_rate} Hz instead of requested {fs} Hz")
            raw_latency = stream.latency
            reported_latency = [float(v) for v in raw_latency] if isinstance(raw_latency, (tuple, list)) else float(raw_latency)
            if self._stop.is_set():
                return recording[:0] if duplex else None, log[:0], {
                    "valid_transport": False, "transport_errors": ["cancelled"], "captured_frames": 0}
            with stream:
                if on_started is not None:
                    on_started()
                deadline = time.monotonic() + total / fs + 8.0
                while not complete.wait(0.05):
                    self._update(progress=min(0.95, position / total * 0.95),
                                 message="Playing timing probes and recording." if duplex else "Playing the SONIC E14 reconstruction.")
                    if self._stop.is_set():
                        stream.abort()
                        complete.wait(0.25)
                        break
                    if time.monotonic() > deadline:
                        stream.abort()
                        errors.append("stream_timeout")
                        break
        finally:
            try:
                stream.close()
            finally:
                with self._lock:
                    self._stream = None
        timestamps = log[:log_position].copy()
        captured = recording[:position].copy() if duplex else None
        if position != total:
            errors.append("incomplete_capture" if duplex else "incomplete_playback")
        if self._stop.is_set():
            errors.append("cancelled")
        if duplex and not np.isfinite(captured).all():
            errors.append("non_finite_audio")
        if duplex and np.any(np.abs(captured) >= 0.999):
            errors.append("input_clipping")
        if duplex:
            checked = assess_timestamps(timestamps, fs)
            errors.extend(checked["errors"])
            diagnostics = checked["clock_diagnostics"]
        else:
            diagnostics = {}
            if len(timestamps) < 2:
                errors.append("missing_callback_timestamps")
            elif not np.isfinite(timestamps).all() or np.any(np.diff(timestamps[:, 0]) != timestamps[:-1, 3]):
                errors.append("invalid_callback_log")
            elif np.any(timestamps[:, 2] <= 0) or np.any(np.diff(timestamps[:, 2]) <= 0):
                errors.append("invalid_output_timestamps")
            if len(timestamps) and np.any(timestamps[:, 4] != 0):
                errors.append("portaudio_callback_status_flag")
        return captured, timestamps, {
            "valid_transport": not errors, "transport_errors": list(dict.fromkeys(errors)),
            "captured_frames": position if duplex else 0, "played_frames": position,
            "requested_sample_rate_hz": fs, "reported_stream_sample_rate_hz": actual_rate,
            "sample_clock_independently_calibrated": False,
            "reported_input_output_latency_seconds": reported_latency,
            "reported_latency_is_measured_delay": False, "clock_diagnostics": diagnostics,
            "callback_log_columns": ["array_start", "input_buffer_adc_time_s", "output_buffer_dac_time_s", "frames", "status_bits"],
            "status_bits": {"input_underflow": 1, "input_overflow": 2, "output_underflow": 4,
                            "output_overflow": 8, "priming_output": 16}}

    @staticmethod
    def _reference_windows(recording, waveform, plan, fs):
        """Find electrical return in input coordinates, independently of callback offsets."""
        first = plan["trials"][0]
        start, stop = first["output_start"], first["output_stop"]
        radius = fs // 4
        left, right = max(0, start - radius), min(len(recording), stop + radius)

        def locate(a, b, lo, hi):
            template = waveform[a:b]
            if hi - lo < len(template) + 2:
                raise RuntimeError("Electrical reference search is too short")
            correlations = _normalized_correlations(template, recording[lo:hi, 1])
            magnitude = np.abs(correlations)
            peak = int(np.argmax(magnitude))
            score = float(magnitude[peak])
            lobe_a, lobe_b, bounded = _primary_lobe_bounds(correlations, peak)
            outside = np.ones(len(magnitude), dtype=bool)
            outside[min(lobe_a, max(0, peak - 3)):max(lobe_b, min(len(magnitude), peak + 4))] = False
            ratio = float(np.max(magnitude[outside]) / score) if score and outside.any() else 1.0
            if score < 0.6 or ratio >= 0.95 or peak in (0, len(magnitude) - 1) or not bounded:
                raise RuntimeError("Electrical reference is missing, weak, ambiguous or at the search boundary; check its line-level route")
            return lo + peak, score

        actual, score = locate(start, stop, left, right)
        offset = actual - start
        windows, matches = [], []
        for trial in plan["trials"]:
            a, b = trial["output_start"], trial["output_stop"]
            lo = max(0, a + offset - fs // 200)
            hi = min(len(recording), b + offset + fs // 200)
            actual, local_score = locate(a, b, lo, hi)
            window = {"start_sample": actual, "stop_sample": actual + b - a}
            if window["stop_sample"] + fs // 10 > len(recording):
                raise RuntimeError("Electrical reference alignment leaves an incomplete microphone search window")
            windows.append(window)
            matches.append({"capture_minus_output_array_offset_samples": actual - a,
                            "electrical_template_correlation": local_score})
        return windows, {"initial_capture_minus_output_array_offset_samples": offset,
                         "electrical_template_correlation": score, "per_window_reference_matches": matches,
                         "reference_offset_range_samples": int(np.ptp([m["capture_minus_output_array_offset_samples"] for m in matches])),
                         "array_offset_is_absolute_hardware_latency": False}

    def _analyze(self, recording, waveform, plan, config, transport):
        fs = config["sample_rate"]
        electrical = config["reference_channel"] is not None
        if electrical:
            windows, alignment = self._reference_windows(recording, waveform, plan, fs)
            paired = recording
            max_lag = 100.0
            mode = "electrical_reference"
            interpretation = (
                f"Microphone input {config['input_channel']} waveform delay relative to recorded electrical input "
                f"{config['reference_channel']}. Includes speaker, acoustic travel and microphone path relative to "
                "the electrical path. Common output/input buffering is excluded; this is not an acoustic onset or SPL calibration.")
        else:
            windows = [{"start_sample": trial["output_start"], "stop_sample": trial["output_stop"]}
                       for trial in plan["trials"]]
            if len(recording) != len(waveform):
                raise RuntimeError("Capture is too short for output-to-microphone analysis")
            paired = np.column_stack((recording[:, 0], waveform))
            alignment = {"reference": "generated output array; no recorded electrical reference"}
            max_lag = 250.0
            mode = "output_to_microphone_roundtrip"
            interpretation = (
                "Output-array to microphone-input waveform roundtrip delay. Includes output/input buffering, "
                "converters, speaker, acoustic travel and microphone path. It does not isolate speaker-to-microphone "
                "acoustic delay; use a simultaneously recorded electrical reference for that relative estimate.")
        result = analyze_trials(paired, fs, windows, max_lag_ms=max_lag)
        if not electrical:
            for trial in result["trials"]:
                trial["source_rms_fs"] = trial.pop("reference_rms_fs")
                trial["source_clipped_samples"] = trial.pop("reference_clipped_samples")
                trial["reasons"] = [reason.replace("reference_", "source_") for reason in trial["reasons"]]
        result.update(mode=mode, interpretation=interpretation, transport=transport, alignment=alignment)
        if not electrical:
            result["transport"]["clock_diagnostics"]["interpretation"] = (
                "Host ADC/DAC timestamps are uncalibrated diagnostics. Primary output-to-microphone alignment uses "
                "paired full-duplex callback array coordinates; reported driver latencies are not added or subtracted.")
        result["reference_signal"] = ("simultaneously recorded electrical return" if electrical else
                                      "exact generated output callback array; not an electrical recording")
        result["response_signal"] = f"microphone input {config['input_channel']}"
        result["reported_driver_latency_added_or_subtracted"] = False
        result["method"] = ("same_adc_clock_normalized_waveform_cross_correlation" if electrical else
                            "generated_output_array_to_microphone_input_normalized_waveform_cross_correlation")
        minimum = max(3, math.ceil(config["repetitions"] * 0.8))
        usable = transport["valid_transport"] and result["summary"]["accepted_trials"] >= minimum and not self._stop.is_set()
        result.update(usable_measurement=bool(usable), minimum_accepted_trials_for_screening=minimum,
                      measured_delay_ms=result["summary"]["median_delay_ms"] if usable else None,
                      status="screening_passed" if usable else "invalid",
                      distance_m=config["distance_m"],
                      limitations=["Integer sample search increment is not calibrated measurement accuracy.",
                                   "Correlation estimates waveform alignment, not a unique physical acoustic onset.",
                                   "Digital amplitude is not acoustic SPL or an exposure setting.",
                                   "Measured geometry is metadata; distance is not subtracted from the estimate."])
        return result

    def _worker(self, config, device):
        folder = None
        manifest = {"schema_version": 1, "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "config": config, "device": device, "platform": platform.platform(),
                    "python_version": platform.python_version(), "numpy_version": np.__version__,
                    "backend_version": str(getattr(self._audio(), "__version__", "unknown")),
                    "raw_audio_publication_authorized": False, "native_audio_attempted": False,
                    "native_audio_started": False,
                    "sound_pressure_level_calibrated": False, "errors": []}
        result = None
        try:
            self.output_root.mkdir(parents=True, exist_ok=True)
            folder = self.output_root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid.uuid4().hex[:10])
            folder.mkdir(mode=0o700)
            self._update(run_path=str(folder))
            if config["action"] == "calibrate":
                waveform, plan = make_probe_plan(config["sample_rate"], config["repetitions"], config["peak_dbfs"])
            else:
                block, plan = make_sonic_e_block(config["sample_rate"], config["tones_per_frequency"],
                                               config["seed"], config["peak_dbfs"])
                pad = config["sample_rate"]
                waveform = np.concatenate((np.zeros(pad, dtype=np.float32), block, np.zeros(pad, dtype=np.float32)))
                plan = deepcopy(plan)
                plan["events"] = [{**event, "output_start": event["output_start"] + pad,
                                   "output_stop": event["output_stop"] + pad} for event in plan["events"]]
                plan["app_padding_each_end_samples"] = pad
                plan["event_coordinates"] = "zero-based samples in saved padded output_float32.npy"
            if not np.isfinite(waveform).all() or np.any(np.abs(waveform) >= 1):
                raise RuntimeError("Generated waveform is non-finite or clipped")
            manifest.update(stimulus=plan, output_sample_count=len(waveform),
                            output_duration_seconds=len(waveform) / config["sample_rate"],
                            output_float32_sha256=hashlib.sha256(waveform.tobytes()).hexdigest(),
                            source_sha256=source_provenance())
            np.save(folder / "output_float32.npy", waveform, allow_pickle=False)
            (folder / "output_float32.npy").chmod(0o600)
            _write_pcm24(folder / "played-output.wav", waveform, config["sample_rate"])
            manifest["wav_export"] = "mono PCM24 at requested rate; file encoding saturates at integer full-scale boundaries; original float arrays retained"
            _json_write(folder / "manifest.json", manifest)
            if not self._stop.is_set():
                manifest["native_audio_attempted"] = True
                _json_write(folder / "manifest.json", manifest)

                def mark_started():
                    manifest["native_audio_started"] = True
                    _json_write(folder / "manifest.json", manifest)

                recording, timestamps, transport = self._capture(waveform, config, on_started=mark_started)
                np.save(folder / "callback_timestamps.npy", timestamps, allow_pickle=False)
                (folder / "callback_timestamps.npy").chmod(0o600)
                if recording is not None:
                    np.save(folder / "capture_float32.npy", recording, allow_pickle=False)
                    (folder / "capture_float32.npy").chmod(0o600)
                    manifest["capture_columns"] = ([{"role": "microphone", "input_channel": config["input_channel"]}] +
                        ([{"role": "electrical_reference", "input_channel": config["reference_channel"]}] if config["reference_channel"] is not None else []))
                    if np.isfinite(recording).all():
                        _write_pcm24(folder / "microphone.wav", recording[:, 0], config["sample_rate"])
                        if config["reference_channel"] is not None:
                            _write_pcm24(folder / "electrical-reference.wav", recording[:, 1], config["sample_rate"])
                    else:
                        manifest["wav_export_capture_skipped"] = "Non-finite input retained in raw float array for diagnosis; no WAV export"
                manifest["transport"] = transport
                manifest["errors"].extend(transport["transport_errors"])
                if not self._stop.is_set():
                    self._update(progress=0.97, message="Checking capture and waveform alignment.")
                    if not transport["valid_transport"]:
                        result = {"status": "invalid", "usable_measurement": False,
                                  "measured_delay_ms": None, "transport": transport}
                        raise RuntimeError("Audio transport failed: " + ", ".join(transport["transport_errors"]))
                    if config["action"] == "calibrate":
                        result = self._analyze(recording, waveform, plan, config, transport)
                        _json_write(folder / "analysis.json", result)
                        if not result["usable_measurement"]:
                            raise RuntimeError("Too few unambiguous, unclipped trials passed the signal-quality screen")
                    else:
                        result = {"kind": "sonic_e14_reconstruction", "usable_measurement": False,
                                  "measured_delay_ms": None, "tone_count": plan["tone_count"],
                                  "duration_seconds": plan["duration_seconds"],
                                  "total_playback_duration_seconds": len(waveform) / config["sample_rate"],
                                  "exact_original_waveform": False, "transport": transport,
                                  "interpretation": "One locally reconstructed SONIC Sheep E14 block played. No latency or SPL calibration was performed."}
            # Decide final validity under the same lock as stop(): a stop racing
            # with analysis completion cannot be overwritten by a valid result.
            with self._lock:
                if self._stop.is_set():
                    result = {"status": "cancelled", "usable_measurement": False, "measured_delay_ms": None}
                    self._update(state="cancelled", message="Cancelled. This run provides no valid measurement.", result=result)
                else:
                    self._update(state="completed", progress=1.0, result=result,
                                 message="Delay screening completed; review the measurement scope." if config["action"] == "calibrate" else "Stimulus playback completed.")
        except Exception as error:
            manifest["errors"].append(f"{type(error).__name__}: {error}")
            if self._stop.is_set():
                result = {"status": "cancelled", "usable_measurement": False, "measured_delay_ms": None}
                self._update(state="cancelled", result=result, message="Cancelled. This run provides no valid measurement.")
            else:
                if result is None:
                    result = {"status": "invalid", "usable_measurement": False, "measured_delay_ms": None}
                result.update(usable_measurement=False, measured_delay_ms=None)
                self._update(state="failed", message=str(error), result=result)
        finally:
            snapshot = self.status()
            manifest.update(finished_at_utc=datetime.now(timezone.utc).isoformat(), state=snapshot["state"],
                            usable_measurement=bool(result and result.get("usable_measurement")))
            if folder is not None:
                try:
                    _json_write(folder / "analysis.json", result or {"usable_measurement": False})
                    manifest["artifacts_sha256"] = {path.name: _hash_file(path) for path in folder.iterdir()
                        if path.is_file() and path.name != "manifest.json" and not path.name.endswith(".tmp")}
                    _json_write(folder / "manifest.json", manifest)
                except Exception as error:
                    manifest["errors"].append(f"artifact_save_error: {error}")
                    self._update(state="failed", message="Audio stopped, but run artifacts could not be saved.",
                                 result={"status": "invalid", "usable_measurement": False, "measured_delay_ms": None})
            self._update(errors=list(dict.fromkeys(manifest["errors"])))
