# Pip-specific calibration attempt: October 28, 2026

## Setup and scope

Howard reported the calibrator removed, the microphone approximately 10 cm from the speaker, and unchanged microphone and speaker gains and microphone position since the earlier pip check. This did not establish identical position to the 15:49 long-tone capture, which preceded the microphone being fitted to and removed from the acoustic calibrator. Speaker model and exact coordinates and orientation are not independently confirmed. All sound was generated at 96 kHz and at or below −36 dBFS nominal digital peak, not a measured acoustic exposure. Raw audio remains in ignored `.work/latency/runs/` and is not committed.

The 10 ms probe is the local reconstruction with 2 ms raised-cosine ramps, not an original SONIC waveform. Each frequency was played three times, with 300 ms onset spacing. Per-frequency results use a Hann-weighted 6 ms central-frequency projection in the 2–8 ms portion of the pip after alignment, compared with a preceding silent control. They are **relative microphone fundamental levels, not total-pip SPL or perceived loudness**. Alignment and >=10 dB narrowband background screens, three repetitions, transport and digital clipping checks do not establish accuracy, ultrasonic fidelity, acoustic isolation or animal suitability.

## Results

The 16:18:42 baseline used the same nominal −36 dBFS digital peak at every frequency; its transport and common 2 kHz alignment screens passed, and all groups passed the three-trial background screen. The 16:19:14 test attempted to attenuate all other frequencies to the lowest 27 kHz baseline. It reduced the 2 kHz output by 58.0 dB (to a nominal −94.0 dBFS digital peak) relative to baseline, while not boosting any frequency above −36 dBFS. In that test the 2 kHz pip failed the background screen on all three trials, its alignment screen failed, and all frequency-relative results were suppressed. Thus **the attempt did not establish equal pip levels**.

The 16:19:40 long-tone control used the same uncorrected 0.6 s waveform as the earlier 15:49:49 control. Both used −36 dBFS nominal peak and passed the recorded transport, clipping and per-frequency background screens. Individual values below are normalized to 2 kHz for each run:

| Frequency kHz | 16:18 pips, relative dB | 16:19 long tones, relative dB | 15:49 long tones, relative dB |
| ---: | ---: | ---: | ---: |
| 2 | +0.0 | +0.0 | +0.0 |
| 4 | -11.4 | -10.4 | -5.7 |
| 6 | -11.1 | -11.2 | -11.5 |
| 8 | -27.2 | -25.1 | -27.6 |
| 9 | -19.2 | -23.1 | -7.3 |
| 10.5 | -12.8 | -12.2 | -7.2 |
| 17 | -16.1 | -16.8 | -8.1 |
| 18.2 | -22.0 | -21.4 | -10.3 |
| 19.5 | -22.1 | -21.4 | -14.1 |
| 20.9 | -33.8 | -32.5 | -18.3 |
| 22.4 | -54.2 | -48.3 | -33.5 |
| 24 | -28.0 | -28.0 | -24.3 |
| 25.8 | -30.4 | -30.9 | -23.3 |
| 27 | -58.0 | -53.8 | -22.1 |

The 16:18 27 kHz baseline central-window values were −98.9, −105.0 and −102.5 dBFS; the 22.4 kHz values were −103.6, −97.5 and −98.7 dBFS. These each span approximately 6 dB over three trials despite passing the narrowband screens. An exploratory 6 ms sliding-window search over 20–110 ms after each output onset found the 22.4 kHz highest median at approximately 45 ms, 7.3 dB above the fixed central-window median, and inconsistent individual trial peak times. The 27 kHz peak times also varied. This exploratory search can favor noise and does not establish a valid correction or uncertainty bound.

At 2 kHz, the 16:18 baseline background components were approximately −103.2, −97.4 and −99.3 dBFS. The unadjusted 27 kHz baseline median was −102.5 dBFS. If the chain behaved linearly, reducing 2 kHz to that target would place it around this background level; the attempted correction confirmed the 2 kHz background and alignment screens failed. This is a screening limitation, not a claim that the corresponding acoustic pip was absent.

At 27 kHz, the current and prior long-tone relative levels differ by approximately 31.6 dB. At 22.4 and 20.9 kHz the differences are approximately 14.8 and 14.3 dB respectively, while absolute 2 kHz long-tone pickup changed by about −0.3 dB. The current long-tone and pip checks both show a weak 27 kHz component, so **the recorded change cannot be attributed uniquely to pip duration**. The data cannot isolate speaker response, acoustic geometry and reflections, microphone response or orientation, processing, electronic coupling, or other path changes. Input 2 was lower than input 1 at the tested frequencies, but its different gain and wiring do not constitute an acoustic-isolation control. The photo of the M50 chart suggests a relatively flat on-axis response, but no serial-specific electronic correction or measurement uncertainty is applied.

The 114 dB calibrator reference is not a validated full-band or pip SPL measurement. Frequency-dependent level estimates must not be treated as verified animal-experiment settings, and a 96 kHz capture cannot independently qualify all ultrasonic harmonic content. Follow-up requires a controlled acoustic-isolation test and additional stable-geometry measurements, adequate background margin, actual pips and back-to-back sequence verification; do not assume the weakest measurement supplies a usable common target.

## Speaker-muted control

At 16:20:27 the same −36 dBFS uncorrected pip sequence was recorded with the speaker muted as reported by Howard, and the microphone position and gain left unchanged. The transport and digital input-clipping screens passed. Because muting removes the 2 kHz acoustic timing reference, the muted run’s own alignment search failed; for this exploratory comparison both recordings were sampled in the identical central 6 ms window relative to the prior unmuted run’s 37.073 ms array offset. This assumes the offset stayed the same between streams and is not an independent timing measurement.

| Frequency | Unmuted median, dBFS peak | Muted median at same offset, dBFS peak | Difference |
| ---: | ---: | ---: | ---: |
| 2 kHz | −44.5 | −102.5 | −58.0 dB |
| 8 kHz | −71.6 | −110.6 | −39.0 dB |
| 22.4 kHz | −98.7 | −119.3 | −20.6 dB |
| 27 kHz | −102.5 | −130.8 | −28.3 dB |

The muted measurements were at or near local background and were not independently aligned; report them as control amplitudes, not calibrated levels. The reductions support a speaker-output-dependent contribution at 22.4 and 27 kHz, but do not establish purity, distinguish every possible coupling path, or solve the large short-window variability. Muted 27 kHz phase values were similar in three low-level windows, which is compatible with residual coherent coupling but is not evidence enough to identify the source. The muted control does not validate the attempted equalization or restore an adequate 2 kHz signal-to-noise margin.

## Data provenance

The following hashes identify local files; the raw room audio and source arrays remain private in ignored `.work` storage.

### 20261028-161842-441275-isolated-corrected-pips

- `manifest.json` SHA-256 `5aaa3ae6e1779ed0d85ed5fdc23dd3aff647e4a3c79d9c00188df992f462bcb7`
- `output_float32.npy` SHA-256 `c7f40a0cbbe4dca02d937f37d704148fb2e6fd498dfa49f1b06d028047beb91a`
- `capture.npz` SHA-256 `d78c044bf1cb075987d6fb0ce7aa7e811e6311761e14bed1cace3851dd7ef7b3`
- `analysis.json` SHA-256 `e3c04ab237cd3ed4c9af6322c2574ba17796cd1cd5743327a6ba3f0fdd13e41d`

### 20261028-161914-476280-isolated-corrected-pips

- `manifest.json` SHA-256 `8d865f64544acdcdf1445758df4369618fc9ed47cd31d99aa34cb297bb1fcca8`
- `output_float32.npy` SHA-256 `9e34879d13988b7a50135dc8092282476fd945868e94512a7190fe698518ef2e`
- `capture.npz` SHA-256 `1ee98a5c35bdae2a2bd196c40de9db54c976f3e1991954091993f74e14e65071`
- `analysis.json` SHA-256 `f82976a1c5c92cdf8d8cf7191b14e4ba9d3d03dcc1b7a8dc1395ca169cf1869d`

### 20261028-161940-888197-separated-levels

- `manifest.json` SHA-256 `e053747da438388e3c507ad6b24136e71af3ab6070f0a62694b662bf36b4ae8c`
- `output_float32.npy` SHA-256 `6f9d240077315cbfd964cfb8b9d1dc743845b378f07cc723a292cc57feb7b108`
- `capture.npz` SHA-256 `2a20661f21439629fc06459371a76d1c7512bb9d02ef01d913e977349e18af94`
- `analysis.json` SHA-256 `5ed656c25603989e4059943101d178c0779bce98b89ea1582c0442c08f15d811`

### 20261028-154949-365739-separated-levels

- `manifest.json` SHA-256 `72016e122d95d1c24ef673217d86f1be91bab7b87877307eb3107284431460a3`
- `output_float32.npy` SHA-256 `6f9d240077315cbfd964cfb8b9d1dc743845b378f07cc723a292cc57feb7b108`
- `capture.npz` SHA-256 `7f0b0e91bc4fdbe9e1be248070e47f9252fd338c1584a746ad71ba653b242d03`
- `analysis.json` SHA-256 `ba793f12826873f5d370bc5a35738ab1b09e16694029c1dbf57700e5ec1e4252`


### 20261028-162027-597367-isolated-corrected-pips

- `manifest.json` SHA-256 `1ebb513a4765ca9e2d00df09ef877a4f7a8e3b0a8401a3a32596510b6dc63d83`
- `output_float32.npy` SHA-256 `c7f40a0cbbe4dca02d937f37d704148fb2e6fd498dfa49f1b06d028047beb91a`
- `capture.npz` SHA-256 `219152be79a6df8d43c3d2934b9fba3e2421ca49b6bf6761b08f46298fe76fc0`
- `analysis.json` SHA-256 `eace207a155d16d03d384fb0f0f77e3283007c1fc7b20fe49b6be0b6afce7608`
