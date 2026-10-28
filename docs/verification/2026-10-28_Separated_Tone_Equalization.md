# Separated-tone equalization: preliminary bench check

On October 28, 2026, the Audient iD14 was operated in a 96 kHz duplex stream, with the connected speaker and M50 microphone. Howard reported a microphone-to-speaker distance of approximately 10 cm. Exact speaker model, angle, placement reproducibility, microphone gain and whether this is the intended sheep-ear geometry were not established. A user-provided acoustic calibrator was available but its model, fit and use were not confirmed. The M50 serial-specific frequency correction and an absolute SPL calibration were not applied.

The 14-tone diagnostic uses separate 0.6 s steady sinusoids with 20 ms ramps and 0.5 s gaps. The measured level is the 250 ms, Hann-weighted microphone fundamental beginning 200 ms after each output-array event, with the previous silent interval as a narrowband background reference. Output-to-input array offset is assumed below 150 ms; this is not a qualified timing measurement. Relative pickup is referenced to the 2 kHz tone within each run. A 10 dB narrowband margin is a screening rule, not a measurement uncertainty or proof of acoustic isolation. Raw audio and run-specific source files remain under ignored `.work/latency/runs/` and must not be committed.

| Run (local time) | Probe | Relative microphone pickup to 2 kHz | Screening and notes |
| --- | --- | --- | --- |
| 15:49:49 | Uncorrected, −36 dBFS digital peak | 8 kHz −27.6 dB; 22.4 kHz −33.5 dB; full range −33.5 to 0 dB | All 14 passed the background screen; transport valid; no input clipping detected. |
| 15:53:05 | First attenuation-only correction from baseline | 8 kHz +10.6 dB; full range −3.0 to +10.6 dB | All 14 passed the screen; transport valid; no input clipping detected. Most tones were closer, but 8 kHz did not match. |
| 15:53:55 | Second cumulative attenuation-only correction from first corrected capture | 8 kHz −0.2 dB; full range −1.4 to +0.6 dB, a 2.0 dB spread | All 14 passed the screen; transport valid; no input clipping detected. |
| 15:54:17 | Repeat with the same second correction | 8 kHz +0.1 dB; full range −0.5 to +0.8 dB, a 1.3 dB spread | All 14 passed the screen; transport valid; no input clipping detected. |

An independent review found the 8 kHz microphone fundamental increased by approximately 5.1 dB from baseline to the first corrected run even though its digital tone was attenuated by approximately 5.9 dB. Its four central 80 ms windows were stable to around 1 dB within each capture. The apparent full-chain response changed by approximately 11 dB between runs. A change in acoustic geometry near a null, level-dependent speaker behavior, or other chain variation could explain this; the available recordings do not identify the cause.

In the two consecutive captures with the same second correction, the frequency-specific levels relative to 2 kHz differed by up to approximately 1.2 dB, at 22.4 kHz. These two runs show short-term agreement only, not a general repeatability bound.

The second-correction table below is transcribed from the `15:53:55` run manifest; the `15:54:17` repeat used the same table. Attenuations are cumulative relative to the common **−36 dBFS digital peak**. Values are rounded to 0.01 dB; the actual files retain full precision. These are playback settings for the separated-tone diagnostic, not measured SPL values.

| Frequency (kHz) | Attenuation (dB) | Resulting digital peak (dBFS) |
| ---: | ---: | ---: |
| 2 | -36.49 | -72.49 |
| 4 | -30.85 | -66.85 |
| 6 | -24.96 | -60.96 |
| 8 | -19.49 | -55.49 |
| 9 | -27.73 | -63.73 |
| 10.5 | -28.74 | -64.74 |
| 17 | -28.84 | -64.84 |
| 18.2 | -25.35 | -61.35 |
| 19.5 | -20.70 | -56.70 |
| 20.9 | -15.81 | -51.81 |
| 22.4 | -3.41 | -39.41 |
| 24 | -9.23 | -45.23 |
| 25.8 | -13.30 | -49.30 |
| 27 | -13.50 | -49.50 |

These are preliminary, uncorrected whole-chain relative measurements at one reported position, not calibrated sound pressure, sheep loudness, or proof of clean ultrasound. No microphone frequency-response correction, absolute level calibration, distortion qualification, acoustic-isolation control, or verification with actual 10 ms pips was performed. The measured spreads do not establish long-term repeatability, safety, or suitability for animal use. Equalization has not been applied to the SONIC player. Record geometry and settings and repeat measurements before relying on a gain table; the weakest frequency controls the attainable level in this attenuation-only approach.
