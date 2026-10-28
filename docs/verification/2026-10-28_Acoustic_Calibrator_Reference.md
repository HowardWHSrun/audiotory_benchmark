# Acoustic calibrator reference: preliminary bench estimate

On October 28, 2026, six seconds of input 1 were recorded at 96 kHz with the Audient iD14 and Earthworks M50. The user subsequently reported that the calibrator was set to **114 dB**, was snugly fitted to the microphone using its adapter, and that the microphone gain and routing had not changed since the earlier tone test. The calibrator model, its stated frequency and calibration status, the adapter identity and fit, and the unchanged settings were not independently verified. The original analysis JSON marks fit and level unknown because it was produced before that user clarification.

The reference analysis reports an estimated 992 Hz tone, a maximum sample magnitude of 0.2015 of digital full scale, and a mean one-second fundamental peak of -14.027 dBFS. The six one-second fundamental values span -14.029 to -14.024 dBFS. The recorded sample maximum is below digital full scale; this screen does not rule out analog clipping. The reference capture does not contain a transport status log or an independent on/off source check.

## Provisional calculation and scope

The earlier playback test used 14 separated 0.6 s steady tones with 20 ms ramps. The microphone was reported approximately 10 cm from the speaker. Its input fundamental was measured in a central 250 ms Hann-weighted window, not from the SONIC 10 ms pips. Its transport and digital-clipping screens passed, and all tones passed the per-frequency narrowband background screen. The calibrator was recorded subsequently, not simultaneously.

For a rough comparison only, assume the reference delivered exactly 114 dB SPL, the microphone and input chain were unchanged and linear, and the frequency response has zero difference from the reference frequency. Then use matching peak-fundamental amplitudes:

`provisional level (dB SPL) = 114 + tone fundamental (dBFS peak) − reference fundamental (dBFS peak)`

The reference calibrator’s RMS-defined SPL is compared to two sinusoid peak amplitudes; their peak-to-RMS factors cancel under those assumptions. These levels are **uncorrected conditional estimates**, not calibrated frequency-specific SPL: no M50 serial-specific response, free-field correction, independently verified 114 dB output or measurement uncertainty is available. The reference is near 1 kHz, while the tested tones span 2–27 kHz. They do not establish equal perceived loudness, ultrasonic fidelity, distortion, the sound at a sheep’s ear, or levels of the 10 ms pips.

| Frequency (kHz) | Relative mic fundamental to 2 kHz (dB) | Provisional uncorrected steady-tone level (dB SPL) |
| ---: | ---: | ---: |
| 2 | +0.0 | 47.6 |
| 4 | -0.3 | 47.3 |
| 6 | +0.4 | 48.0 |
| 8 | +0.1 | 47.8 |
| 9 | -0.1 | 47.6 |
| 10.5 | +0.2 | 47.9 |
| 17 | +0.1 | 47.8 |
| 18.2 | -0.1 | 47.5 |
| 19.5 | -0.1 | 47.5 |
| 20.9 | +0.8 | 48.4 |
| 22.4 | -0.3 | 47.3 |
| 24 | -0.0 | 47.6 |
| 25.8 | -0.5 | 47.2 |
| 27 | +0.4 | 48.0 |

Do not apply these as accepted experimental settings. Confirm calibrator model and adapter, verify the reference and gain stability, obtain the individual M50 frequency-response data, and repeat calibrated measurements at the intended ear geometry, including the actual pips and distortion checks.

## Evidence and privacy

The following hashes identify local private captures and their analysis records. The audio remains in ignored `.work/latency/runs/`; raw room audio is not included in Git.

- Reference audio capture: SHA-256 `36b4ead35f832997ec75cca295f3953a2b45fb074ff0008f3419c435f2188a44`
- Reference analysis: SHA-256 `b393baa3e2ca34dc4982e3c7058586057a035f999dd376c5498db4030f275991`
- Separated-tone audio capture: SHA-256 `7f02371637edb88cfbb9c0fc1b1d587a831851776ce4c23a8ee6be11d1c2388f`
- Separated-tone analysis: SHA-256 `527e0979c6a0d914adf15d2b180d7af87da8eaa25f144e6ecc57a8460f915735`
- Separated-tone manifest: SHA-256 `c3a4ed31409c4460b2676b2d31e027293aa6df10bd3d0d06bff136bd30dd379b`

The source waveform SHA-256 recorded in the separated-tone manifest is `7bae79a0445506d6817c9b03461cda00b0e2f8f53706c618e2edf2e1c24bca8e` (hash of the float32 sample bytes).
