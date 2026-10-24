# SONIC Bench in your browser

[Open SONIC Bench](https://howardwhsrun.github.io/audiotory_benchmark/web/bench/) on a Mac or Windows computer. There is no app to install and no local server to start. Use a current desktop Chrome or Edge browser for the most complete output-device controls; the page checks the browser's actual capabilities. A hardware interface may still need its manufacturer's existing driver.

The interface is black and white. In the **Audio** panel, choose the microphone and speaker, then select **Connect audio**. The panel collapses after connection. Use the **Play stimulus** and **Measure delay** tabs to choose a task. Playback offers **Quick check** (9 seconds total) and **Full block** (86 seconds total). The timing reference is inside **Timing settings & details**; advanced controls and stimulus provenance stay collapsed until needed. Results appear only after a run produces an outcome.

Nothing plays on page load. Microphone access starts only after an explicit action and browser permission. Use **Stop** or **Escape** to stop a run. Hiding the page also stops audio and releases the devices; reconnect before the next run. Changing the interface, sample rate or physical setup requires another delay check.

## Connect

Use the same wired audio interface for output and input. For the existing equipment:

```text
Computer USB ↔ Audient iD14
Output 1/L → powered speaker → air → Earthworks M50 → input 1 XLR
```

Select that interface as the computer's sound output and microphone input before connecting. Where the browser supports `AudioContext.setSinkId()`, the page can choose an output directly; otherwise it uses the system default. Chrome documents output selection from version 110. MDN's compatibility data currently lists Chrome/Edge support and no Firefox/Safari implementation of this method. This concerns the output selector, not the whole Web Audio API. [Chrome output routing](https://developer.chrome.com/blog/audiocontext-setsinkid/), [MDN method and compatibility](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/setSinkId).

Keep input monitoring off in the interface mixer to prevent microphone feedback. The M50 requires phantom power on input 1. Start with low speaker volume and input gain. The page cannot inspect physical cables, phantom switches, gain or mixer routing. Record microphone distance and orientation, speaker position, gain and output level with any useful result.

The page requests a **96 kHz Web Audio context**, stereo input when needed, and microphone processing disabled. Advanced audio settings also offer a 192 kHz request. Check the displayed actual context rate, input-track settings and observed channels. A request is not evidence that the hardware delivers that format; browsers can ignore unsupported microphone constraints, and can resample between hardware, input track and context. Some combinations will reject a requested rate and the app then displays the browser default. [AudioContext options](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/AudioContext), [sample-rate constraints](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints/sampleRate), [channel-count constraints](https://developer.mozilla.org/en-US/docs/Web/API/MediaTrackConstraints/channelCount), [actual track settings](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/getSettings).

The full E14 reconstruction is enabled only with a context rate of at least 96 kHz. Its highest tone is 27 kHz; generating it at ordinary 44.1/48 kHz would exceed Nyquist. A 96 kHz context alone does **not** prove a 96 kHz physical output path or 27 kHz acoustic delivery. Set the interface's operating-system format accordingly and verify the physical chain separately.

## Check delay

Use the separate chirp probe for delay checking. It is a local timing signal, not a SONIC experimental stimulus. A matched chirp is less ambiguous than the repeated pure tones in the E14 block.

**Speaker + microphone** compares the exact generated source array with microphone samples captured on the AudioWorklet's process-frame grid. Its estimate includes browser input/output buffering, resampling, converters, speaker, air, microphone and preamplifier. It is not isolated speaker-to-microphone propagation time, Play-button latency or a validated correction for neural recordings.

**Electrical reference** adds a simultaneous return:

```text
Output 1/L → speaker → air → microphone → input 1 XLR
Output 2/R ─────────────────────────────→ input 2 TRS
```

Keep **input 2 phantom off** and input monitoring off. Turn the speaker down before changing cables. This mode needs two distinct input channels actually exposed by the browser. It compares microphone and electrical-return arrival in the same captured stream, reducing shared output-buffer timing. Channel mixing, browser resampling, converter/channel skew and physical routing remain unqualified. A stereo setting or a pair of similar waveforms does not establish independent hardware channels; inspect the cables and run separate channel-isolation checks before relying on this mode.

The result is a **browser timing estimate** within the app's 0–250 ms search window. A successful match to the first probe is required so a long delay cannot simply wrap into a later repeated chirp. Clipping, weak or ambiguous matches, missing channels, incomplete capture or insufficient accepted repeats prevent a useful result. Echo cancellation, noise suppression and automatic gain control must be reported off in actual track settings for the app's processing screen to pass; unavailable settings leave a diagnostic result. Passing that screen does not establish metrology-grade accuracy. Worklet frame/chunk continuity can detect some application-level problems; it cannot certify the absence of hardware underruns, overruns, hidden processing or clock drift. Record repeat spread as observed variability, not calibrated timing accuracy.

`baseLatency`, `outputLatency` and `getOutputTimestamp()` are browser diagnostics, not an acoustic delay calibration. The timestamp API relates Web Audio and estimated device rendering time; it does not timestamp the microphone's physical acoustic onset. [MDN output timestamp](https://developer.mozilla.org/en-US/docs/Web/API/AudioContext/getOutputTimestamp), [W3C Web Audio specification](https://www.w3.org/TR/webaudio/).

## Play SONIC

The page reconstructs **Sheep E's 14-frequency specification** from SONIC bioRxiv v1, Methods 6.1–6.2, printed page 11. Frequencies are 2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8 and 27 kHz. Pips last 10 ms with 2 ms end ramps, zero initial sine phase and no inter-tone gap. A full local block has 600 pips per frequency: 8,400 pips and 84 seconds of tone content. [Pinned manuscript](../../sources/SONIC_2025_bioRxiv_v1.pdf), [paper source](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1).

**Quick check** uses 50 pips per frequency: 700 pips and 7 seconds of tone content. Both sequence lengths add one second of silence before and after playback, for 9 or 86 seconds total. These are locally chosen single blocks, not the paper's complete session.

The original waveform files, exact sequence and seed were unavailable. Equal counts, Mulberry32 seeded Fisher–Yates shuffling, raised-cosine ramps and digital peak level are local choices. This shuffle differs from the native app's PCG64 order, even with the same numeric seed. Digital dBFS is not dB SPL. The page does not establish the paper's acoustic field, sound level, frequency response, hardware synchronization or session design.

The paper used awake/alert sheep. Rice's planned sedated-sheep work is an adaptation whose responses, suitable analysis windows and achieved ITR remain unverified. The published 56/11 ms intrinsic delays exclude physiology and computation; the 11 ms result came from a narrower one-session sweep. This app is a bench preparation tool, not an animal-ready protocol or neural-acquisition controller.

## Privacy, compatibility and verification

The page is static content on the project's existing public GitHub Pages site. Audio generation, capture and analysis run in the browser; the app has no recording-upload service. The optional downloads save records on your computer. Raw microphone recordings can contain room conversations, so review them before sharing. GitHub serves the website assets; this does not mean that the site uploads microphone samples.

Microphone capture requires permission and a secure context: use the HTTPS link above. Local development can use localhost, which browsers generally treat as trustworthy; opening files directly or using an ordinary remote HTTP server is unsuitable. [MDN microphone access and security](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia).

AudioWorklet is available in current desktop Chrome, Edge, Firefox and Safari, but that does not guarantee successful 96 kHz input/output, stereo capture or this app's behavior on every device. MDN records initial support in Chrome 66, Firefox 76 and Safari 14.1, with Chromium Edge inheriting support. Feature detection and a physical configuration check remain necessary. [MDN AudioWorklet](https://developer.mozilla.org/en-US/docs/Web/API/AudioWorklet), [Mozilla compatibility data](https://github.com/mdn/browser-compat-data/blob/main/api/AudioWorklet.json).

See the [dated verification record](../verification/2026-10-24_Browser_Bench.json) for checks actually performed. Synthetic tests and browser UI checks are not physical calibration. No new sound playback, room recording, animal experiment or measured Rice performance is implied by publication of this version. The existing [native app](https://github.com/HowardWHSrun/audiotory_benchmark/tree/main/bench_app) remains available for its separate PortAudio workflow; its historical timing results do not validate this browser pipeline.
