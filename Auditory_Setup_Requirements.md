# Auditory setup requirements

Updated October 7, 2026. Howard Wang and Jiaao Zhang jointly own the auditory investigation. The **confirmed Rice target is sedated sheep** and measuring auditory-cortex responses to sound. A soundproof box and behavioral rig are not required by Lan's direction. See [team clarifications](sources/Team_Clarifications_2026-10-07.md).

This is a **proposed design**, not an installed or validated setup. SONIC's settings come from awake sheep; [paper notes](Paper_Notes.md) separate that evidence from the Rice adaptation.

## Paper starting point and Rice implications

| Verified SONIC method | Rice requirement to assess |
|---|---|
| Precomputed sine pips, zero starting phase and 2 ms end ramps (Sections 6.1-6.2, p.11). | Record a full waveform specification; resolve or explicitly choose the missing ramp shape. |
| Benchmark pips are 10 ms; initial frequencies extend to 32 kHz; DAC runs at 192 kHz (Sections 6.1-6.2, p.11). | Verify output and measurement coverage for the selected frequencies. Paper values are candidate starting points, not confirmed Rice settings. |
| Uniform random frequencies, balanced blocks, back-to-back tones (Section 6.1, p.11). | Save the sequence, stimulus IDs, seed and balancing rule. |
| TDT SA1 amplifier and MF1 free-field speaker; approximately 80 dB SPL at sheep-ear distance (Section 6.2, p.11). | Identify local speaker/amplifier and measure output at the intended reference geometry. Exact placement and frequency-specific calibration are absent from the paper. |
| PTP/10 MHz reference and electrical sound-output/trial-edge loopback (Section 6.2, p.11). | Validate event/clock mapping and measured acoustic timing with Rice hardware. Matching brands is not itself validation. |
| Awake, alert sheep (Section 6.6, p.13). | Sedated sheep are an adaptation. Establish local response timing and analysis windows; do not promise the paper's ITR. |

## Sound-generation specification

Record the exact frequency array, duration, ramp shape, sample rate, phase convention, amplitude normalization, output channels and bit depth. Record probabilities, balance, order, random seed, repetitions, silence and treatment of aborts. Keep immutable waveform files, versions/hashes and a stimulus-event manifest.

Document generation/playback software, operating system, driver/backend, device configuration, gain and routing. Digital amplitude and acoustic level at the reference position are different measurements. The educational visualization does not generate a validated experimental waveform or control lab hardware.

The initial 37-frequency array is not fully listed; an array reconstructed from rounded endpoints would be a Rice choice. The 14-frequency Sheep E array is explicitly listed in the paper notes. Alphabet and duration may need adjustment when the local sedated response and recording system are known.

## Proposed delivery and measurement paths

`Versioned waveform -> playback software -> DAC/audio output -> amplifier if needed -> speaker -> sound at sheep-ear reference position`

`Reference microphone -> preamplifier/measurement input -> acoustic recording and calibration analysis`

`Trial marker/electrical loopback -> acquisition event/input channel -> clock-aligned event record`

Record actual models, connections and limits once known. Repeatable speaker/microphone geometry remains necessary without an enclosure. Document room/background conditions; the absence of required isolation is not evidence that interference is absent.

## Focused speaker and calibration questions

McGinley students shared a rodent rig and calibration approach. Prepare questions that resolve the sheep sound chain:

- Which speaker, amplifier and playback output are used, and over what measured frequency range?
- Which microphone, preamplifier/interface and calibration reference are used? Do they cover the intended frequencies?
- Where is the reference microphone placed, and how are distance and orientation reproduced?
- Are levels measured per frequency, and how are gain, distortion/clipping and background sound recorded?
- Does calibration apply to short ramped pips, and is the level convention explicit?
- How are electrical markers and acoustic onset captured and aligned?
- Which portions of the method carry over to sheep-ear geometry?

A wholesale rodent parts list is not required. Speaker suitability and calibration carryover remain unknown until specifications and measurements support them. No external message has been sent.

## Timing and synchronization

Distinguish software playback request, electrical marker/waveform, measured acoustic onset/offset, acquisition timestamp and neural response. A marker alone does not establish when sound arrives at the reference position.

Define every event's clock, units, origin and channel. Prefer capturing markers and microphone signal on a shared acquisition clock when supported. Otherwise validate clock mapping, drift and reset behavior. Establish the neural recorder's event inputs and timestamp/export behavior before selecting the connection map.

Measure marker-to-acoustic latency and variability, effective pip duration, spacing, missing/duplicate events and drift across the intended run. Retain raw captures and a documented onset rule. Test representative load and relevant restarts/configuration changes. Tolerances remain open until Rice stimulus and analysis requirements are defined.

Keep delivery timing separate from SONIC intrinsic delay, computation delay and auditory-response time. Published 56 ms and 11 ms values are not sound-arrival-to-output measurements or guarantees for sedated sheep.

## Proposed session record

| Field | Content |
|---|---|
| Run identity | Run ID, operator, local date/time/timezone and purpose. |
| Experimental context | Species, recorded animal state, target and declared SONIC deviations. |
| Stimulus manifest | Waveform version/hash, IDs, sequence, seed and parameters. |
| Configuration | Software/OS/driver versions, models, routes, gains, geometry and clocks. |
| Calibration | Reference position, convention, raw captures, levels and configuration validity. |
| Event record | ID and requested/marker/acoustic/acquisition times, with clock labels and units. |
| Quality record | Underruns, missing events, aborts, clipping, errors and deviations. |
| Evidence | Raw captures, analysis version, acceptance decision and reviewer. |

This is a proposed structure. No calibration, bench delivery or neural result is claimed.
