# Experimental corrected continuous-pip preview

On October 28, 2026, two 7 s previews were played and recorded in the current bench configuration after the user reported two successive approximately 5 mm sideways microphone moves. Each preview used the same balanced, shuffled 700-pip local SONIC reconstruction: 50 ten-millisecond pips per frequency, 2 ms raised-cosine ramps, no gaps, at 96 kHz. The original SONIC waveform and the intended sheep-ear geometry remain unverified. The waveform used the experimental attenuation-only settings derived from the isolated-pip baseline; no source frequency exceeded the −36 dBFS digital base. This does not establish acoustic SPL.

The offline analysis in `latency/pip_preview_response.py` validates the saved waveform hash, acquisition transport and callback timestamps, and measures the nominal-frequency component in a 6 ms Hann-windowed section (2–8 ms of each pip). It uses a fixed 37.2 ms array offset informed by the preceding isolated-pip checks, with sensitivity comparisons at 36.2 and 38.2 ms. It does not independently measure latency from the continuous pips. Groups are screened against matched-frequency pre-block background and in-block controls, and against neighboring equal or harmonic-related frequencies. A group requires at least five clean-neighbor events, 20 control events, a 10 dB margin over both controls, no clipping or transport error, and at most 3 dB median variation across the three analysis offsets. These are local screens, not uncertainty bounds or proof of acoustic isolation.

All 14 frequency groups passed these screens in both runs. The table gives clean-neighbor group medians relative to 2 kHz, not full-pip levels or per-pip equality.

| Frequency (kHz) | First run (dB) | Repeat (dB) | Clean pips per run |
| ---: | ---: | ---: | ---: |
| 2 | 0.00 | 0.00 | 38 |
| 4 | -0.56 | -0.48 | 24 |
| 6 | -0.44 | -0.66 | 25 |
| 8 | -0.90 | -1.37 | 14 |
| 9 | -0.53 | -0.57 | 39 |
| 10.5 | -0.79 | -0.87 | 37 |
| 17 | -0.50 | -0.69 | 43 |
| 18.2 | -0.22 | -0.32 | 17 |
| 19.5 | -0.51 | -0.64 | 39 |
| 20.9 | -0.46 | -0.60 | 27 |
| 22.4 | -0.08 | -0.20 | 42 |
| 24 | -1.85 | -1.91 | 10 |
| 25.8 | -0.10 | -0.25 | 33 |
| 27 | -0.33 | -0.35 | 27 |

The first run spanned 1.85 dB and the repeat 1.91 dB across frequency-group medians. This is not a range of all individual pips: for example, among the 10 clean 24 kHz pips, the 5th percentile was about 3.1 dB below its median in the first run and 1.6 dB below in the repeat. The 2 kHz group was approximately 15.2 dB above pre-block matched-frequency background in the first run and 19.3 dB in the repeat. A narrowband margin does not imply a calibrated error bound.

These measurements are uncorrected microphone pickup at one position, not absolute or peak-equivalent SPL, proof of equal sheep loudness, frequency-specific harmonic purity, or qualification of the complete speaker path. Adjacent-pip energy, ringing, leakage, and measurement noise may bias the estimates despite the controls. Capture at 96 kHz does not independently qualify harmonics above 48 kHz. No individual electronic M50 correction was applied. Recheck at the actual ear geometry, validate absolute level and distortion, and reassess repeatability before using a correction profile for an animal experiment.

## Private evidence

Raw audio and waveform files remain under ignored `.work/latency/runs/`, not Git. SHA-256 values below identify the local files.

| File | First run `20261028-162553-sonic-e14-preview` | Repeat `20261028-162618-sonic-e14-preview` |
| --- | --- | --- |
| manifest.json | `04b57807647f294cf03fd9b548597a760f0e9d09bd04fdff3a608fcd1968e22e` | `4ade91b8e9f48a23a9d7b033d2f2e8a641f5d1bd7d9c9f8926110a942ea06156` |
| stimulus-plan.json | `71ce4e262cdd1dc393a2d89068a13f35cbf126ea9aaa992f399326c6166eb7a1` | `71ce4e262cdd1dc393a2d89068a13f35cbf126ea9aaa992f399326c6166eb7a1` |
| output_float32.npy | `b3246df69b662728e46ca0e853a6146814fe3cddcea865f3160dcfc27dc19dff` | `b3246df69b662728e46ca0e853a6146814fe3cddcea865f3160dcfc27dc19dff` |
| capture.npz | `a5e8eb30a6d703cc9dc29c7fc66a8c5b86b12d7718f7ca66cee4d5e95ee369f0` | `26f398a4012c888f4ca5d43a67a1f11d5e3c1c5f3b084bfa48c537f5fcfc56d0` |
| continuous-pip-analysis.json | `dc75213cccada5101da4ece0364dbd46fe488513b98b81921b78bf4470357d01` | `cb9b03308fdd498f16925a3e6969ca83df6f4dfdafbe685eecb3069ef8bb2333` |
