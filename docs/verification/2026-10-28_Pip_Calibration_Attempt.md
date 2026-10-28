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

## Lateral-position check

At 16:22:24 Howard reported moving the microphone approximately 5 mm sideways and restoring speaker output after the muted control; exact displacement and orientation were not independently measured. The same uncorrected digital pip waveform at a −36 dBFS nominal peak was used. Both captures passed transport, digital-clipping, common-alignment and all stated narrowband trial screens. The relative frequency-specific values below use the 2 kHz reference within each respective capture.

| Frequency (kHz) | Before move relative dB | After move relative dB | Change dB |
| ---: | ---: | ---: | ---: |
| 2 | +0.0 | +0.0 | +0.0 |
| 8 | -27.2 | -27.1 | +0.1 |
| 20.9 | -33.8 | -33.2 | +0.6 |
| 22.4 | -54.2 | -50.2 | +4.1 |
| 24 | -28.0 | -28.4 | -0.3 |
| 25.8 | -30.4 | -30.3 | +0.1 |
| 27 | -58.0 | -52.5 | +5.5 |

The three post-move central-window 22.4 kHz levels were −93.9, −95.9 and −94.6 dBFS, a 2.0 dB span. The corresponding 27 kHz levels were −100.9, −95.7 and −97.0 dBFS, a 5.2 dB span. Improvement with the reported position change is consistent with a position-dependent acoustic field, but the small set of observations does not exclude other path variation. These values remain uncorrected relative microphone fundamental measurements, not verified free-field SPL or equal loudness. The 27 kHz component remains more than 50 dB below the 2 kHz component in this capture; the prior attenuation-to-weakest approach failed its noise and alignment screens and is not yet a qualified 14-frequency solution.

## Second lateral-position and pip-specific correction checks

Howard reported a second approximately 5 mm sideways microphone movement in the same direction, for approximately 10 mm total from the 16:18 baseline; displacement and orientation were not independently measured. The reported setup remained about 10 cm from the speaker. At 16:24:00 an uncorrected −36 dBFS nominal digital peak pip baseline was recorded; compared with the 16:22:24 pip capture, the 27 kHz microphone component increased approximately 12.7 dB and the 2 kHz component increased approximately 1.0 dB. These observations are consistent with position sensitivity but do not isolate the cause.

The 16:24:24 and 16:24:48 tests used the same per-frequency pip-specific attenuation derived from the 16:24:00 baseline. No frequency was boosted above the base −36 dBFS digital peak. All three runs passed transport, input digital clipping and common 2 kHz alignment screens. In the first corrected run, 9 kHz had only two of three trials passing the background screen; the remaining 13 frequencies had a 1.54 dB total median-component spread relative to 2 kHz. In the second corrected run, all 14 frequencies had three passing trials, with a **1.70 dB total spread** in the central 6 ms microphone component. The 27 kHz central component varied by about 0.3 dB across the three second-run trials; its prior position dependence remains unresolved. Three trials and these screening rules do not establish an uncertainty bound or long-term repeatability.

| Frequency kHz | Digital attenuation from −36 dBFS peak | Corrected run 1 relative dB | Corrected run 2 relative dB |
| ---: | ---: | ---: | ---: |
| 2 | -40.84 dB | +0.00 | +0.00 |
| 4 | -31.48 dB | -1.40 | -1.30 |
| 6 | -29.30 dB | -1.05 | -0.81 |
| 8 | -10.76 dB | -1.54 | -1.07 |
| 9 | -24.03 dB | Not qualified (2/3) | -0.97 |
| 10.5 | -25.91 dB | -0.92 | -1.04 |
| 17 | -23.15 dB | -1.09 | -0.85 |
| 18.2 | -20.86 dB | -0.87 | -0.64 |
| 19.5 | -23.48 dB | -1.08 | -0.80 |
| 20.9 | -20.17 dB | -0.94 | -0.80 |
| 22.4 | -17.47 dB | -0.68 | -0.46 |
| 24 | -1.03 dB | -1.21 | -1.70 |
| 25.8 | -0.07 dB | -1.03 | -0.57 |
| 27 | +0.00 dB | -0.85 | -0.60 |

The final row set is a preliminary **isolated-pip** result at a single reported geometry; the electronic microphone frequency correction, independently verified SPL and uncertainty, acoustic distortion and harmonic rejection, short-pip level convention, intended sheep-ear geometry, and SONIC-style consecutive sequences were not validated. The table has not been integrated into the normal SONIC player. The two corrected runs share one source waveform and are not independent calibration derivations. Further position and time repeats and verification with actual back-to-back stimuli are needed before using a gain table experimentally.

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

### 20261028-162224-697932-isolated-corrected-pips

- `manifest.json` SHA-256 `2eef12c7da8ca461f83db45c5469f12bcf2c9da1329f35b0175d2b3816460536`
- `output_float32.npy` SHA-256 `c7f40a0cbbe4dca02d937f37d704148fb2e6fd498dfa49f1b06d028047beb91a`
- `capture.npz` SHA-256 `ea90696c02349abb49933fb5dbb7986d0524ed4b72d7d31e0ca4d204712a9c27`
- `analysis.json` SHA-256 `9bc71d1ae724d148ccbd028a7c9685e7e2961b66c6b1b25b8f8221fc2cc086d8`

### 20261028-162400-420775-isolated-corrected-pips

- `manifest.json` SHA-256 `5aab0dec1586d0f3951f2cdd56bd1bd27209109bbb52b357bd9b0b2af98d6125`
- `output_float32.npy` SHA-256 `c7f40a0cbbe4dca02d937f37d704148fb2e6fd498dfa49f1b06d028047beb91a`
- `capture.npz` SHA-256 `84b737ad9404049fb008ed97496b86b0a2d1e612a1873832bd145e137f08c789`
- `analysis.json` SHA-256 `5bc60c7e0a7fd9e0e52de87f2623d8c5def52b8069f3e0f6ca8ebd2985244c05`

### 20261028-162424-160589-isolated-corrected-pips

- `manifest.json` SHA-256 `077c3c0a8e8fdcb8a17e939eaca380f507a9253e4e0e87df176b7bcbfe5c5e23`
- `output_float32.npy` SHA-256 `e2d00509966350d18ffbe97a0d7152d303eff65601b670cdef5d4eb0a11874b5`
- `capture.npz` SHA-256 `46ffb05afb59456a8dbba4ea865014825dd641682fec632c43f4c6e87610134c`
- `analysis.json` SHA-256 `d574c8d9d0c178923caa37d8e4799358453090a8ba34e92ade89044d6438eea0`

### 20261028-162448-897345-isolated-corrected-pips

- `manifest.json` SHA-256 `fcc6228b5300032281212dde2ebcaf86b843c3ec9b5907e2a4b471611e4b4988`
- `output_float32.npy` SHA-256 `e2d00509966350d18ffbe97a0d7152d303eff65601b670cdef5d4eb0a11874b5`
- `capture.npz` SHA-256 `bc364460db4031c4ee893f9c7e0944689c82dc21bc139418d0676afd46c515f7`
- `analysis.json` SHA-256 `6c202e50c624eeb7ad036ee34d0b6419099cbc6b1d7aa3d29b8ff1f62e3067e4`
