# SONIC Bench

A local Mac/Windows control panel for preparing and playing the published SONIC Sheep E tone specification and checking playback-to-microphone delay. The browser provides the controls; a native Python audio stream performs playback and capture. Browser timing is not used as a measured audio clock.

## Start the app

Standalone downloads are available from the [verified Mac/Windows build](https://github.com/HowardWHSrun/audiotory_benchmark/actions/runs/40110935554). Unzip the download, then open **SONIC Bench.app** on an Apple Silicon Mac or **SONIC Bench.exe** inside its folder on Windows x64. These bundles include Python. The locally built Mac app is also placed in the project root; build output stays outside Git.

For the source launchers below:

Keep the complete repository folder together. Install Python **3.10 or newer** with `venv` and `pip` if Python is not already available ([macOS instructions](https://docs.python.org/3/using/mac.html), [Windows instructions](https://docs.python.org/3/using/windows.html)).

- **Mac:** double-click [`Launch SONIC Bench.command`](../Launch%20SONIC%20Bench.command).
- **Windows:** double-click [`Launch SONIC Bench.cmd`](../Launch%20SONIC%20Bench.cmd).

The launcher reuses the project's prepared audio environment when available; otherwise it creates an isolated environment under ignored `.work/bench_app/venv` and installs the dependencies. An initial installation needs internet access. It opens the local control panel. Keep the launcher's terminal open while using the app; Ctrl+C stops its server. The browser connects to the computer's loopback address; this is not a hosted website or remote equipment service.

Use **Stop** (or Escape) to cancel a run, and **Quit app** to stop audio and close the local server. Closing a browser tab stops an active run after the 12-second heartbeat timeout; it does not quit the server. Completed runs offer a JSON download and a local folder path containing manifests, source WAVs and calibration recordings.

Manual launch from the repository root, using an environment with `latency/requirements.txt` installed:

```sh
python -m bench_app
```

The source launch helpers require Python. The optional [PyInstaller recipe](SONIC_Bench.spec) and manually triggered [build workflow](../.github/workflows/bench-app.yml) produce standalone Mac/Windows bundles containing a Python runtime. These are not signed or notarized installers. Build success and offline checks do not verify a machine's audio hardware or driver. Windows driver, launch and audio behavior still require a Windows bench check. The [verification record](../docs/verification/2026-10-24_Bench_App.json) states the checks actually performed.

## Connect and select the audio interface

Use one wired full-duplex audio interface for both output and microphone capture, then select that interface in the app. Its driver and chosen sample rate must support the required inputs and outputs. Start with the working Audient setup at **96 kHz**; 192 kHz is offered for interfaces that actually support it. The existing Audient iD14 setup was verified at 96 kHz, not 192 kHz. An available format or generated file does not establish acoustic bandwidth.

For the current equipment:

```text
Computer USB <-> Audient iD14
Audient output 1/L -> powered speaker -> air -> Earthworks M50 -> input 1 XLR
```

Keep microphone/input monitoring disabled in the interface mixer so captured sound is not fed back to the speaker. The M50 requires its microphone phantom power on input 1. Start with low speaker volume and input gain, and document microphone distance, orientation, speaker/output level and gain. The app cannot inspect physical phantom switches, cables or mixer routes. Grant the operating system microphone permission to the process running Python when requested; restarting the app may be necessary after changing permission.

On macOS, audio uses Core Audio through PortAudio. On Windows, install the interface manufacturer's ASIO driver and select its corresponding device/host API. The app enables the bundled ASIO-capable PortAudio library for its own process before importing `sounddevice`; this changes no system setting and does not install a hardware driver. A single device with both input and output channels is required; separate Windows WASAPI input/output endpoints are not combined by this app. Windows drivers and ASIO streams still need their own bench verification. See the [sounddevice installation documentation](https://python-sounddevice.readthedocs.io/en/0.5.6/installation.html) and [host API settings](https://python-sounddevice.readthedocs.io/en/0.5.6/api/platform-specific-settings.html).

## Check the delay first

The delay action plays a separate, nonperiodic timing probe while recording the microphone in the same native full-duplex stream. Each probe is a 100 ms logarithmic chirp from 100 Hz toward 20 kHz with 20 ms ramps. Probe onsets are 500 ms apart, with one second of silence at each end of the train; select the number of repeats in the app. This probe is a local calibration choice, separate from SONIC's repeated tone pips. Repeated pure tones can produce ambiguous correlation peaks and are not used as the delay probe.

**Source-to-microphone mode** needs only the speaker and microphone connections above. It matches the exact generated output array to the microphone recording on the application's duplex sample grid. The reported roundtrip includes application/input/output buffering, DA/AD conversion, speaker response, air travel, microphone and preamplifier. It is not a measurement of the Play button's latency, isolated speaker delay or an independently established acoustic onset. Do not subtract it blindly from neural recordings or another application's timestamps.

**Electrical-reference mode** adds a simultaneous electrical return to cancel shared output buffering in a microphone-versus-reference comparison:

```text
Output 1/L -> speaker -> air -> microphone -> input 1 XLR
Output 2/R --------------------------------> input 2 TRS
```

Both ends of the return cable connect to the interface. **Input 2 phantom power must remain off**, and input monitoring must remain off. Turn the speaker down before changing wiring. The result is microphone delay relative to recorded input 2, including speaker, propagation and microphone path differences; input/output channel skew is uncalibrated. A working electrical return must be present for this mode to produce a useful result. It is not the same estimand as source-to-microphone roundtrip.

The app saves the source, capture, callback/timestamp integrity information, settings and analysis for review. Missing/invalid transport evidence, clipping, weak or ambiguous matches and insufficient accepted trials must not be treated as a successful calibration. Sample spacing is the correlation search increment, not a calibrated timing accuracy. Repeat a stable geometry/configuration before relying on a result; changing driver, rate, buffering, interface, speaker or microphone can change the delay.

## Prepare and send the SONIC stimulus

Select the reconstructed **Sheep E 14-frequency** block. The generator reuses [`latency/stimulus.py`](../latency/stimulus.py) and the pinned [SONIC bioRxiv v1 manuscript](../sources/SONIC_2025_bioRxiv_v1.pdf), Methods 6.1–6.2, printed page 11 ([paper source](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1)).

- Published frequencies: **2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8 and 27 kHz**.
- Published pip structure: **10 ms**, zero starting sine phase, **2 ms end ramps**, consecutive pips without inter-tone silence, uniformly selected and balanced at the block level.
- Local default: **600 pips per frequency**, 8,400 pips / **84 seconds** of tone content, PCG64 seed `20261023`, equal counts shuffled once, raised-cosine ramps and a declared digital peak level. Capture padding is separate from tone content.

The explicit stimulus action opens the output device and plays sound; it does not simultaneously record the microphone. The calibration action performs playback and capture together. For generation without hardware, the existing `python -m latency.stimulus sonic-e` command writes the reconstructed plan and WAV without playing sound. Digital dBFS is an output-array peak convention, not dB SPL. The original waveform files, random order/seed, exact balancing algorithm, ramp shape and digital amplitude convention remain unavailable. This app reproduces the documented E14 timing/frequency specification with disclosed local choices; it cannot promise the identical original SONIC waveform or acoustic field.

Each action opens a new stream. Output-only stimulus playback may have different buffering from duplex calibration, so the roundtrip estimate is not a validated correction for SONIC playback timestamps. The app logs the delay; it does not automatically shift stimuli or neural data.

The paper used precomputed 192 kHz NI USB-6361 output, TDT SA1/MF1 hardware and approximately 80 dB SPL at the sheep's ears. Its sessions had at least 12 blocks of 8,000–15,000 tones separated by one second. One reconstructed block is not that full session or a reproduction of those hardware, level, calibration or synchronization conditions. The Sheep C 37-frequency stimulus is not reconstructed here.

## Saved results and scientific limits

Source-launch records stay under ignored **`.work/bench_app/runs/`**; standalone bundles use **`SONIC Bench/runs` in your home folder**. Calibration records include raw room audio. These are local files, not uploaded to GitHub. Keep useful sanitized verification summaries separate from raw recordings and review an exported file before sharing it. Do not commit `.work/` or include identifiable room audio in a public issue.

The existing command-line workflow measured approximately **38.3 ms** of source-to-microphone roundtrip on October 23, 2026, across two 96 kHz Mac/Audient streams and 40 accepted probes. That is historical evidence for the documented configuration, **not a new measurement made by this app**. See the [measured delay record](../docs/verification/2026-10-23_Audient_Playback_Microphone_Delay.json). Existing recordings also support pickup of all E14 frequency groups above their controls, with uneven recorded levels and unqualified high-frequency fidelity ([frequency review](../docs/verification/2026-10-23_SONIC_E14_Pip_Frequency_Pickup.json)).

Delay checking does not calibrate microphone sensitivity, absolute SPL, frequency response, distortion, speaker bandwidth or exposure. Frequency-specific acoustic delivery remains unqualified; a 27 kHz digital tone does not establish a 27 kHz acoustic stimulus at the subject. The M50's serial-specific calibration, documented geometry, level calibration and independent acoustic controls remain separate work.

This is a bench tool and planning aid. It does not control neural acquisition, provide trial TTL/PTP synchronization or establish neural-clock alignment. SONIC's reported 56/11 ms intrinsic delays are separate quantities and exclude auditory physiology and computation; the 11 ms finding is from a narrower one-session window sweep. Rice's planned sedated-sheep measurements are an adaptation of the paper's awake/alert-sheep work; their responses, windows and achieved ITR are unverified. App verification uses offline/synthetic checks unless a record explicitly identifies an authorized real capture.

## Developer checks

Run `python -m unittest discover -s bench_app -p 'test_*.py'` and `python -m bench_app --smoke-test` for offline checks. Optional browser checks use `node bench_app/test_ui.cjs` with Playwright and Chromium installed; `PLAYWRIGHT_MODULE_PATH` and `PLAYWRIGHT_BROWSER_EXECUTABLE` can select existing installations. The browser suite uses a mock API, opens no audio hardware, and saves ignored screenshots under `.work/bench_app/`.
