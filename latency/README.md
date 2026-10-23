# Audient sound-delivery delay check

This package prepares SONIC-derived sounds and measures native playback-to-microphone waveform delay. On October 23, 2026, two native full-duplex runs established approximately **38.3 ms** of application roundtrip delay for the working wired setup at 96 kHz. The browser player's button timestamps are not used for this measurement.

## Measured playback-to-microphone roundtrip

Forty nonperiodic sweeps were detected across two separately opened streams, with no rejected trials, clipping, or transport warnings. Run medians were 38.250 and 38.375 ms; all detected delays were between 38.240 and 38.375 ms. This establishes short-run repeatability for this program and configuration. The observed spread is not a calibrated accuracy bound. See the [concise one-page report](../output/pdf/2026-10-23/Audient_Delay_Report/main.pdf), [LaTeX source](../output/pdf/2026-10-23/Audient_Delay_Report/main.tex), and [measurement record](../docs/verification/2026-10-23_Audient_Playback_Microphone_Delay.json).

To repeat without changing the working cables or controls, pause other audio and double-click [Measure Sound Delay.command](../Measure%20Sound%20Delay.command), or run:

```sh
.work/latency-venv/bin/python -m latency.roundtrip
```

The command plays twenty 100 ms sweeps at -24 dBFS peak and records the microphone on input 1 in one Audient full-duplex stream. The exact generated output array is compared with the microphone input array; input 2 is not used as a reference. The result includes application/device playback and recording buffers, conversion, loudspeaker, air travel, and microphone path. It does not establish UI-click latency, isolated speaker delay, exact acoustic onset, another application's latency, or SONIC's neural/intrinsic delay. The operator previously reported 10 cm geometry; it was not remeasured for these runs or subtracted from the result.

`--generate-only` prepares probes without opening audio hardware. `--analyze-run .work/latency/runs/RUN_FOLDER` checks a saved source hash, native acquisition metadata, raw callback log, and signal quality without playing sound. Invalid transport suppresses accepted delay values. Source and microphone WAVs, raw capture, timestamps, manifest, and `roundtrip-analysis.json` stay in ignored `.work/`. The old electrical-reference analysis is a separate measurement and retains its own validity requirements below.

## Basic speaker playback and microphone recording

Simultaneous playback through the Audient and Earthworks recording on input 1 were verified on October 23, 2026. Howard heard the locally synthesized melody, and three sections of the microphone recording matched it with 0.948–0.954 normalized waveform correlation after a 200–1600 Hz bandpass. The capture had no transport warnings or clipping. This verifies the basic sound path; it does not establish a delay, calibrated level, or full frequency response. See the [verification record](../docs/verification/2026-10-23_Audient_Basic_Playback_Recording.json).

To repeat the basic check, pause other computer audio and keep the working speaker volume, microphone gain, and phantom-power switches unchanged. Inputs 1/2 must remain excluded from speaker monitoring to prevent feedback. This check requires the microphone on input 1 and a speaker on output 1; it does not require an electrical-return cable. Double-click [Play and Record Music.command](../Play%20and%20Record%20Music.command), or run:

```sh
.work/latency-venv/bin/python -m latency.music_check
```

The command plays a new synthesized recording of the public-domain *Twinkle, Twinkle, Little Star* melody at -24 dBFS peak through outputs 1/2 while recording inputs 1/2. The melody lasts 19.2 seconds, with two seconds of silence before it and one after it. It saves the source waveform, microphone WAV, raw capture, and metadata locally under ignored `.work/latency/runs/`. `--generate-only` prepares the source without opening audio hardware. This is a basic connection check, separate from the SONIC reconstruction and timing probe.

## Optional electrical timing reference

The application roundtrip measurement above needs only the working speaker and microphone connections. The wiring below is for measuring the microphone **relative to an electrical return**, which cancels shared playback buffering. A reliable electrical reference was not present in the successful roundtrip runs.

Turn speaker volume down while changing cables. Disable input monitoring in the Audient iD Mixer so inputs 1/2 do not feed the monitor outputs. Keep gain low initially.

```text
Audient OUT 1/L -> powered speaker -> air -> Earthworks -> MIC/LINE input 1 (XLR)
Audient OUT 2/R -------------------------------> MIC/LINE input 2 (centre TRS hole)
```

The same return cable has BOTH ends in the Audient: OUT 2/R and input 2. Input 2 phantom power stays OFF; input 1 phantom power supplies the M50. Output 1 remains connected to the speaker. Leave the passive speaker's red/black cable attached. With one analogue input to the powered MR3, only the corresponding side may reproduce the test; position the microphone in front of the speaker that actually plays.

Record the microphone tip's distance, orientation and height. Avoid the bass port for the reference position; fix the geometry and background conditions across runs. Distance is metadata, not automatically subtracted from the result. Physical monitoring/phantom settings cannot be verified by this program.

## Prepared sounds and provenance

The [pinned SONIC v1 manuscript](../sources/SONIC_2025_bioRxiv_v1.pdf), sections 6.1-6.2, printed page 11, specifies zero-phase 10 ms sine pips with 2 ms end ramps. Sheep E's 14 frequencies are 2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8 and 27 kHz. Tones are consecutive, uniformly selected and balanced within blocks. Reported blocks have 8,000-15,000 pips, 1 second between blocks, and at least 12 blocks/session. The paper used precomputed waveforms through an NI USB-6361 at 192 kHz, TDT SA1/MF1 delivery and an approximately 80 dB SPL ear-position level. Those hardware/level settings have not been reproduced here.

Original stimulus files/code were not located in a focused DOI/title and official Paradromics repository search on October 23, 2026. The exact C37 list, ramp shape, seed/order, balancing algorithm, digital amplitude convention and detailed calibration/geometry remain unresolved. Our E14 files are a declared reconstruction: raised-cosine ramps, PCG64 seed 20261023, and a shuffled block containing 600 of each tone (8,400 pips, 84 seconds). The Audient version uses 96 kHz; a 192 kHz archive is also generated, but the Audient is not asked to play that rate. Full E14 includes frequencies above the speakers' verified operating range; generated samples do not establish acoustic coverage.

The separate timing probe is a local calibration signal: twenty 100 ms logarithmic sweeps from 100 Hz to 20 kHz, 20 ms end ramps, 500 ms onset spacing, and 1 second padding before and after (11.6 seconds total). It is not a published SONIC stimulus. A nonperiodic probe avoids the cycle ambiguity of a single pure tone. The legacy electrical-reference command defaults to -36 dBFS; `roundtrip` and `sonic_check` default to the working -24 dBFS peak. Neither digital level establishes calibrated SPL.

To play the reconstructed E14 sounds through the working route while recording the microphone, double-click [Play SONIC Tones.command](../Play%20SONIC%20Tones.command), or run:

```sh
.work/latency-venv/bin/python -m latency.sonic_check
```

This plays one 84-second reconstructed block at -24 dBFS peak, with one second of capture silence at either end. `--preview` selects a 7-second, 700-pip preview; `--generate-only` saves files without accessing audio hardware. The padded source WAV, unpadded stimulus plan, microphone WAV, and transport metadata stay local. No delay is inferred from the repeated pure tones. The original sound order is unavailable, acoustic SPL is uncalibrated, and playback does not establish the speaker's high-frequency response.

One full block was played and recorded on October 23 without clipping or callback warnings. Sequence matching and spectral checks substantiated microphone pickup of the 2-10.5 kHz tones; higher-frequency acoustic coverage remains unqualified. A separate direct delay check of five four-second SONIC sequence windows accepted only one; four had ambiguous carrier-correlation peaks. No SONIC-specific delay is qualified: approximately 38.3 ms is the separate sweep result. See the [SONIC playback verification record](../docs/verification/2026-10-23_SONIC_E14_Playback.json).

## Run the separate electrical-reference method

The isolated environment is prepared locally at `.work/latency-venv/`. To recreate it using a Python installation with venv support:

```sh
python3 -m venv .work/latency-venv
.work/latency-venv/bin/python -m pip install -r latency/requirements.txt
.work/latency-venv/bin/python -m latency.run check
.work/latency-venv/bin/python -m latency.run wiring-check
.work/latency-venv/bin/python -m latency.stimulus bank
```

`check` inspects the Audient and verifies 96 kHz stereo input/output format support without starting sound or capture. `wiring-check` plays three very quiet probes at -48 dBFS and captures both inputs; it does not qualify a geometry-specific delay. `bank` creates 96/192 kHz PCM24 WAVs, sequence/event manifests and SHA256 files under ignored `.work/latency/stimuli/`; no audio plays.

Once the return cable, monitoring and gains are configured, run the timing probe with your measured distance in metres. Replace the example distance with the actual value:

```sh
.work/latency-venv/bin/python -m latency.run record --stimulus probe --distance-m 0.30
```

For the declared E14 reconstruction, use `--stimulus sonic-e` instead. It plays one 84-second balanced block with 1-second capture padding on either side; this is not the paper's full session. Both commands deliberately open the audio device and capture room sound. Use Ctrl+C to abort. Local run folders contain `capture.npz`, `output_float32.npy`, `manifest.json` and `analysis.json`. Raw room recordings stay under ignored `.work/` and are not published.

## Meaning of the electrical-reference result

One full-duplex Core Audio stream binds the named Audient at 96 kHz. Its first two input channels are recorded together: input 1 microphone, input 2 electrical return. Actual reference windows are found in the captured electrical channel; output/input array positions in a callback are not assumed simultaneous. Per-buffer ADC/DAC timestamps and PortAudio status flags are saved.

The primary result is normalized waveform alignment of the microphone relative to the simultaneous electrical return. It includes speaker processing, propagation and microphone path **relative to** the electrical-return channel. Shared computer buffering and DAC latency cancel from this comparison. Inter-output and inter-input analogue path skew remain uncalibrated. The estimate is not absolute click-to-sound latency, an independently verified acoustic onset, neural latency, or SONIC's 56/11 ms intrinsic delay.

The program reports candidate delays, median, 5th/95th percentiles, jitter range, and a linear delay trend. Weak, clipped, ambiguous or search-boundary matches are rejected; the width of the primary correlation lobe is reported. At least three accepted trials are required for the provisional screening flag. Transport flags, incomplete capture, nonmonotonic timestamps and large unexplained clock jumps invalidate a run. Small common host-clock corrections are diagnosed separately and do not establish missing input samples. Host-time accuracy remains uncalibrated; the primary comparison uses the shared ADC sample clock. The 10.4 microsecond sample spacing is the search increment, not claimed measurement accuracy. Echoes, frequency-dependent phase, noise, threshold selection and transducer/channel delays can move a waveform peak. Review raw traces and repeat stable-geometry runs before relying on a number. Software-trigger and neural-clock alignment need additional independently verified timing references. See [PortAudio's timing guidance](https://github.com/PortAudio/portaudio/wiki/BufferingLatencyAndTimingImplementationGuidelines) and its [CoreAudio backend](https://github.com/PortAudio/portaudio/blob/master/src/hostapi/coreaudio/pa_mac_core.c).

## Verification

```sh
.work/latency-venv/bin/python -m unittest discover -s latency -p 'test_*.py'
```

Offline tests recover imposed delays in synthetic signals and reject missing channels, clipping, pure-tone ambiguity, competing echoes, boundary peaks, source-hash mismatches, and invalid transport. These are algorithm checks, separate from the measured two-run result above.

Earlier electrical-reference checks did not establish a delay. A three-probe check at -48 dBFS detected the electrical return with approximately 0.995 correlation, but all microphone estimates were rejected. After USB reconnect, a 20-probe run at -36 dBFS had no detectable reference. These failed checks remain recorded in the [preparation record](../docs/verification/2026-10-23_Audient_Delay_Preparation.json). Later speaker/microphone pickup and application roundtrip were verified separately; a reliable electrical return remains pending. Raw recordings remain local.
