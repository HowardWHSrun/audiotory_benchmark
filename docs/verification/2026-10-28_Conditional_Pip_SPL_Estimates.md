# Conditional 10 ms pip level estimates — October 28, 2026

## Scope and reference

Howard confirmed that the acoustic calibrator is a REED R8090, selected at 114 dB, that the M50 was fitted with its adapter for the earlier reference, and that microphone gain and routing remained unchanged. At this stage Howard reported the microphone about 10 cm from the speaker and the same position and settings as the prior corrected-pip test; exact location and microphone orientation were not independently measured. The reference recording was made at 15:59:50, not during these checks. Its dominant frequency was approximately 992 Hz, and its median matched-frequency fundamental peak was −14.0274 dBFS. The maximum recorded sample was 0.2015 FS; the capture has no callback status record or independent on/off check. The calibrator's actual output, calibration date, adapter seal, preamp analog linearity and unchanged settings were not independently verified. See [the reference record](2026-10-28_Acoustic_Calibrator_Reference.md).

The M50's individual printed chart looks approximately flat, but numerical unit-specific frequency corrections and the coupler-to-free-field response relationship were not measured or applied. Estimates assume exactly 114 dB SPL delivered in the coupler, unchanged linear electronics, and zero microphone sensitivity change relative to 1 kHz across 2–27 kHz. Under these assumptions, matched peak amplitudes from a steady sinusoidal reference and a central-window sinusoidal component can be compared without an extra RMS/peak offset:

`conditional equivalent-sine level = 114 dB + pip-component peak (dBFS) − reference-component peak (dBFS)`.

These are **conditional central-component equivalent-sine estimates** only. They are not independently verified dB SPL, 10 ms whole-pip broadband RMS SPL, a standardized peak-equivalent SPL measurement, or equal perceived loudness. The 6 ms Hann window and microphone response may reject other sound energy; noise, frequency-dependent arrival time, signal leakage and harmonics can bias a result. The 96 kHz recording does not independently qualify ultrasonic harmonics above 48 kHz. The 10 ms whole-pip broadband RMS checked in an earlier capture was often dominated by local background; a valid SNR and metric must be established before reporting total pip SPL. No uncertainty budget or animal-use qualification was established.

An exploratory check of the current 16:44:20 isolated capture also compared the unfiltered, aligned 10 ms microphone-window RMS with the RMS of the 10 ms window immediately before each source event. The three-trial median contrasts were approximately −9.7 dB at 6 kHz and −6.3 dB at 17 kHz, with substantial variation between individual windows. The pre-source samples are a separate, non-simultaneous background estimate; these exploratory contrasts depend on alignment and noise variation and do not imply that the pip was absent. They show that broadband background can dominate some current measurement windows, so this capture does not establish reliable unweighted total-pip SPL by simple window RMS.

## Captures and measurement

The 16:42:59 consecutive-pip capture contained a dominant near-992 Hz signal across the recording and is excluded from pip level conclusions. Howard subsequently reported the calibrator off and removed; its actual physical state during that earlier capture and the source of the tone were not established. A subsequent microphone-only check was reported quiet but was not saved; it cannot be independently audited. The later isolated and continuous runs had valid transport and no detected digital clipping. Raw microphone recordings stay under ignored `.work/latency/runs/` and are not published.

Each 16:43:50 and 16:44:20 isolated sequence used 42 reconstructed 10 ms pips with 2 ms raised-cosine ramps, three per frequency at 300 ms onset spacing. The 16:43:50 run used the earlier profile; the 16:44:20 run used a newly derived additional attenuation-only profile. All frequencies in both runs passed the three-trial local narrowband background screens and common 2 kHz alignment screen. Their frequency-group medians span 3.06 dB and 1.60 dB respectively. This is not a bound on every pip.

The 16:44:49 and 16:45:26 previews used that new diagnostic profile in a 7 s, 700-pip, balanced back-to-back reconstruction. All 14 groups passed the local screens in each run. Their clean-neighbor group median components spanned 1.13 and 0.77 dB respectively. Each group had 10–43 clean pips; the 24 kHz group had 10. At 2 kHz, median levels were 14.6 and 15.7 dB above the pre-block narrowband background; this is not a metrological uncertainty. Analysis used a fixed 37.2 ms array alignment from the isolated checks with ±1 ms sensitivity checks, not independent consecutive-pip timing or a calibrated latency.

| Frequency | Prior-profile isolated estimate | New-profile isolated estimate | Continuous run 1 | Continuous run 2 |
| ---: | ---: | ---: | ---: | ---: |
| 2 kHz | 44.8 | 40.3 | 41.0 | 41.3 |
| 4 kHz | 43.3 | 41.8 | 42.1 | 42.1 |
| 6 kHz | 44.0 | 41.4 | 41.3 | 41.6 |
| 8 kHz | 43.3 | 41.5 | 41.8 | 41.6 |
| 9 kHz | 43.6 | 41.6 | 41.7 | 41.7 |
| 10.5 kHz | 43.5 | 41.7 | 41.7 | 41.9 |
| 17 kHz | 43.8 | 41.6 | 41.6 | 41.6 |
| 18.2 kHz | 44.1 | 41.7 | 41.6 | 41.6 |
| 19.5 kHz | 43.4 | 41.8 | 41.8 | 41.8 |
| 20.9 kHz | 43.7 | 41.7 | 41.7 | 41.6 |
| 22.4 kHz | 44.3 | 41.7 | 41.7 | 41.7 |
| 24 kHz | 41.7 | 41.9 | 41.9 | 41.7 |
| 25.8 kHz | 44.0 | 41.7 | 41.8 | 41.7 |
| 27 kHz | 44.5 | 41.7 | 41.7 | 41.9 |

Table entries are rounded conditional median equivalent-sine levels in dB relative to 20 µPa under the assumptions above. Displayed decimal places are not an accuracy claim. The attenuations were derived from microphone components; the resulting similarity does not establish equal individual-pip SPL or a correct absolute acoustic level.

The experimental `Play Corrected SONIC Pips.command` now uses the new profile from the 16:44:20 isolated run for its seven-second preview and requires that saved local run. Do not transfer the profile to a different setup or the sheep experiment without verification. Before use, recheck the physical reference and microphone response and repeat measurements at actual ear geometry, establish the desired 10 ms metric, verify broadband background, acoustic isolation, per-pip repeatability and distortion, and determine an acceptable level with the research team.

## Private evidence and hashes

Raw recordings and waveform arrays remain private in ignored local `.work`; hashes identify the exact material examined. The 15:59:50 reference-capture SHA-256 is `36b4ead35f832997ec75cca295f3953a2b45fb074ff0008f3419c435f2188a44` and its analysis SHA-256 is `b393baa3e2ca34dc4982e3c7058586057a035f999dd376c5498db4030f275991`.

### `20261028-164259-sonic-e14-preview`

- `manifest.json`: `186aad519f88aadaab07d11c7f9162d6139b67fd2674827bad1e449d8c3bf080`
- `pickup-check.json`: `7b9ee7b6c60eba290b396eceead4b32104bc28f0419efbfdfb3d594fa775f199`
- `capture.npz`: `9ae99e404c523bdfe879ca8b4881fb535fb5f10f56eedd9ce1a229d9122c6ddd`
- `output_float32.npy`: `b3246df69b662728e46ca0e853a6146814fe3cddcea865f3160dcfc27dc19dff`
- `stimulus-plan.json`: `71ce4e262cdd1dc393a2d89068a13f35cbf126ea9aaa992f399326c6166eb7a1`

### `20261028-164350-517037-isolated-corrected-pips`

- `manifest.json`: `5127e06920b70fa0e314fdf0529fbc6e0db57cbb5c1925d5172236087ca5a7ef`
- `analysis.json`: `47e9609e9dc288588ad412d338d97ea41a65315cb9eb5c8a962380a89cdbb86c`
- `conditional-pip-spl-estimate.json`: `dc9c0ad082ac3c5287cc0950115aa1e27113cf36c144c973fb6799fe91ebc3cf`
- `capture.npz`: `6245a98f9f572c5b8aa0bb292d7911f357e8316bcdb85e8c8488eca09b8b324a`
- `output_float32.npy`: `e2d00509966350d18ffbe97a0d7152d303eff65601b670cdef5d4eb0a11874b5`

### `20261028-164420-221594-isolated-corrected-pips`

- `manifest.json`: `b3866f059b84bb1f83fdab97df789842565d68816ccabf420539673ff4517d3d`
- `analysis.json`: `f72c0a1b055266dc7095e54f72c8b6cbb66550cbe0e753654d7c3b49eee08367`
- `conditional-pip-spl-estimate.json`: `b7952266321624a58533ead5f5ff9c0b20bf4d978e41280afd63959d92ef607c`
- `capture.npz`: `74d1b83ac793a20f12ba94d7c8c0db4b8d076a5e003f365f047c7f89cb056ae3`
- `output_float32.npy`: `846bfb44c27a38508002e21dbd794c2fd9c485b152d0c470fe4aff3032c99d09`

### `20261028-164449-sonic-e14-preview`

- `manifest.json`: `ded11d1a193fadafc58df31b1261d386bdc4725e91459aff7771f25949aa5913`
- `continuous-pip-analysis.json`: `4b2175233d4d41d520f923577d7610a40211cebd1c9c8c89cc4774ae22fa775f`
- `pickup-check.json`: `5a7a971ea19e549db2d6b023577b34230c96eda4a587c1ad4e9692049ad03f9b`
- `capture.npz`: `6f6f5af7093956b6551da05da8ac5d76181f581d0b1c18688e19467007613efc`
- `output_float32.npy`: `ceedbfcc69bbefbbfe3807567b74cfcf747a51afb0cd5a38a83b29d311d5ef1d`
- `stimulus-plan.json`: `5f2d5c9a37073034ddb292dd775acc91b9878a7433072282e6c0f1f3f5c7569e`

### `20261028-164526-sonic-e14-preview`

- `manifest.json`: `058b212393da8e5b932993792c24add179508d821fb48166bf0bb358b06b6889`
- `continuous-pip-analysis.json`: `9063a0433d85df6c8facecd59cfa2669efa9c6596bac5786e8159653963731d2`
- `pickup-check.json`: `f75ec3bde1e63bb4180e88113653e3fbf0afdd576d7bb2b56c22cd1a0ce897ec`
- `capture.npz`: `a29ce57603b57581f599c7ecbb8f022af199a1a97482c1533e179a8027c047ef`
- `output_float32.npy`: `ceedbfcc69bbefbbfe3807567b74cfcf747a51afb0cd5a38a83b29d311d5ef1d`
- `stimulus-plan.json`: `5f2d5c9a37073034ddb292dd775acc91b9878a7433072282e6c0f1f3f5c7569e`

