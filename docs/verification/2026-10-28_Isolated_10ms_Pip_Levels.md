# Isolated 10 ms pip levels: preliminary bench check

On October 28, 2026, Howard reported that the M50 was back about 10 cm from the speaker with the calibrator off and removed, and that microphone and speaker gains were unchanged from the previous separated-tone correction. Exact geometry, orientation and gain values were not independently verified. Using the previously recorded attenuation-only settings, the Audient output base was −36 dBFS and no frequency was boosted above it. The probe used the same locally reconstructed 10 ms, 2 ms raised-cosine end-ramp pips as the SONIC E14 generator; the original paper waveform is unavailable. Unlike SONIC, these pips were separated by 300 ms onset-to-onset to support independent measurement. Each of the 14 frequencies was presented three times in each of two runs. This did not apply corrections to the normal SONIC player.

The microphone was captured at 96 kHz. For each run, a common output-array-to-input alignment was estimated from the three 2 kHz acoustic pip envelopes. A Hann-weighted projection at the nominal frequency measured its fundamental component over a 6 ms window (2–8 ms within the pip), with a same-length silence window as a background screen. The value is a matched-frequency peak amplitude, relative to 2 kHz in the same run. It is not whole-pip RMS, broadband dB SPL, or perceived loudness. Three trials per frequency had to pass a 10 dB narrowband background screen; no values are reported for an incomplete frequency group. These screens do not establish accuracy or acoustic isolation. Frequency-specific delay may bias the common-window result.

| Frequency (kHz) | Run 1 relative to 2 kHz (dB) | Run 2 relative to 2 kHz (dB) | Qualifying trials run 1 / run 2 |
| ---: | ---: | ---: | ---: |
| 2 | +0.0 | +0.0 | 3/3; 3/3 |
| 4 | -5.6 | -5.8 | 3/3; 3/3 |
| 6 | +0.3 | -0.3 | 3/3; 3/3 |
| 8 | -10.8 | -11.1 | 3/3; 3/3 |
| 9 | -10.3 | -11.1 | 3/3; 3/3 |
| 10.5 | -5.2 | -5.8 | 3/3; 3/3 |
| 17 | -8.3 | -9.0 | 3/3; 3/3 |
| 18.2 | -10.5 | -11.2 | 3/3; 3/3 |
| 19.5 | -6.2 | -6.7 | 3/3; 3/3 |
| 20.9 | -12.2 | -13.0 | 3/3; 3/3 |
| 22.4 | -18.6 | -16.1 | 3/3; 3/3 |
| 24 | -1.0 | -1.9 | 3/3; 3/3 |
| 25.8 | -7.0 | -7.7 | 3/3; 3/3 |
| 27 | Not qualified | Not qualified | 2/3; 2/3 |

Both runs passed transport and digital input-clipping screens. Current-run 2 kHz alignment was approximately 37.26 ms and 37.16 ms respectively; these are array-alignment quantities, not calibrated sound latency. Thirteen groups passed the stated three-trial screen in both runs; the 27 kHz group had only two qualifying trials in each and therefore has no reported level. Among qualified groups, the range relative to 2 kHz was approximately −18.6 to +0.3 dB in the first run and −16.1 to 0 dB in the second. These preliminary observations do not establish why pips differ from the near-flat steady tones; possible frequency-dependent speaker transient response, position, common-lag error, and other path variation require investigation. The chart for M50 serial 38520AA visually shows a near-flat on-axis response, but the electronic frequency calibration and measurement uncertainty were not applied.


A secondary exploratory timing check used Hann-weighted 6 ms projections at the stimulus frequency, sliding the window start from 25 ms to under 85 ms after the output event in 0.5 ms steps and selecting the highest across-trial median. In each run, 12 of the 13 otherwise qualifying frequencies had maxima within 0.4 dB of the fixed central-window result. At 22.4 kHz the exploratory maxima were approximately 3.3 dB and 2.7 dB higher than the primary results, respectively, indicating window sensitivity; positions were not consistent across trials. The search itself can favor noise and was not a pre-specified or independently qualified timing method. At 27 kHz the maxima and timing were unstable, so no 27 kHz level is inferred. This exploratory check is not a correction or measurement uncertainty.

The 114 dB coupler reference reported earlier is not a validated pip SPL calibration. This check does not establish equal sound pressure, equal sheep loudness, speaker distortion, ultrasound fidelity, intended ear geometry, consecutive-pip behavior or animal-use suitability. The microphone/geometry and reference should be revalidated before any change in attenuation and checked at the intended ear position.

## Provenance and privacy

Generated waveform, manifest, raw input capture and analyses stay in ignored `.work/latency/runs/`. No raw room audio is included here. The following SHA-256 hashes identify the local evidence used for this report.

- Run `20261028-160701-472436-isolated-corrected-pips`:
  - `manifest.json`: `a559d12b2855ab7ed16d911438b3112d0782c840c7231950dd2b97ffde3f7fd5`
  - `output_float32.npy`: `243b47d51ee0aa7e4e0b919838ce3326ff1d84ae95b4175d183ad1c9300c2281`
  - `capture.npz`: `737cc0cf3641f9d95946b35bc9bf545637a42611c3559b299d52b5a16b246052`
  - `analysis.json`: `3044fc962b59dfe6f0006bf9f5c8571cf79f78d4a5d809711cd485057a3e6a68`
- Run `20261028-160727-801048-isolated-corrected-pips`:
  - `manifest.json`: `7ac7132baf66209a1d1fe1401cedfd5e75c24254d27b18264e63b2c11648e517`
  - `output_float32.npy`: `243b47d51ee0aa7e4e0b919838ce3326ff1d84ae95b4175d183ad1c9300c2281`
  - `capture.npz`: `be98dd60a1a80d9b2ec008d7054c10d0f32c229e78e60b98619dfb8825c5398d`
  - `analysis.json`: `5a426c2774b18c95fd6cd3b223b34e0eb8e8f02681c12834a3f8e42d379f5cdc`
