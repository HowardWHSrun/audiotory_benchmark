# Equipment and software inventory

Updated October 8, 2026. **Primary target: sedated-sheep sound-evoked auditory-cortex responses.** Howard Wang and Jiaao Zhang jointly own the auditory investigation. Lan does not require a soundproof box or behavioral rig. McGinley students shared rodent-rig/calibration experience; this does not verify particular equipment for sheep. See [team source record](sources/Team_Clarifications_2026-10-07.md).

## Auditory delivery and timing

Complete availability/model fields from inspection, specifications, records or direct team confirmation.

| Item/role | Availability | Model/version | Compatibility to verify | Evidence/next action |
|---|---|---|---|---|
| Stimulus computer/OS | Unknown | Unknown | Playback support, load and saved configuration | Inventory |
| Experimental generation/playback | Unknown | Unknown | Exact waveforms, sequences, event logs and errors | Identify lab tools; educational frontend is separate |
| DAC/audio output | Unknown | Unknown | Frequency range, sample rate, limits, drivers and buffering | Inspect models/manuals |
| Speaker | Unknown | Unknown | Measured bandwidth/level, distortion and sheep-ear geometry | Focused McGinley question; local verification |
| Amplifier if needed | Unknown | Unknown | Bandwidth, gain, clipping and electrical compatibility | Identify/document |
| Reference microphone | Unknown | Unknown | Frequency coverage, sensitivity/calibration and placement | Identify measurement capability |
| Microphone preamplifier/input | Unknown | Unknown | Bandwidth, gain, limits and sampling | Establish measurement chain |
| Calibration reference/records | Unknown | Unknown | Traceability, level convention and geometry applicability | Obtain relevant method, not wholesale parts list |
| Trigger/event output | Unknown | Unknown | Coding, voltage limits, polarity and timing | Confirm recorder compatibility |
| Electrical/acoustic acquisition | Unknown | Unknown | Shared-clock capture, sampling and timestamp export | Identify channels/clocks |
| Neural recording interface | Unknown | Unknown | Event input, clock origin/drift and data export | Establish intended Rice system |
| Cables/adapters/channel map | Unknown | Unknown | Pinouts, levels, grounding and routing | Produce connection map |
| Speaker/microphone fixture | Unknown | Unknown | Repeatable distance/orientation | Document sheep geometry |
| Soundproof box/behavioral rig | Not required by team direction | Not applicable | Background conditions still documented | Lan clarification, not an acoustic result |
| Experimental storage/versioning | Unknown | Unknown | Raw captures, manifests, configuration/access | Establish lab records convention |
| Existing software/SOPs | Unknown | Unknown | Applicability, versions and validation evidence | Review available resources |

For confirmed items, record owner/custodian, calibration status and constraints. State whether each satisfies a **paper fact** or **proposed Rice choice**. An unknown item does not imply a purchase.

## Mouse setup: provision from scratch

Howard asked us to assume the mouse setup must be assembled. Each function below is **not yet secured for planning purposes**; this is an assumption, not a completed physical inventory. The [BCM email](sources/BCM_Acoustic_Equipment_Email_2026-10-08.md) suggests candidates without confirming Rice access. See the [equipment plan](Mouse_Setup_Equipment_Plan.md) for dependencies and official sources.

| Function | Candidate or unresolved choice | Provision to confirm |
|---|---|---|
| Stimulus computer/software | Unselected | OS, waveform generation, timed playback, saved configuration |
| Analog playback output | Hardware-timed DAC/DAQ, model open | Frequency coverage, output range, event generation |
| Free-field speaker path | ES1 + ED1 candidate | Intended tones at or above 4 kHz; zBus/ZB1PS power, matching speaker cable, calibration |
| Other speaker paths | EC1, Peerless XT25TG30-04, Scan-Speak R2004/602200 | Coupling for EC1; suitable conventional amplifier for either tweeter; usable band |
| Acoustic recording | 116Hm complete CM16/CMPA kit or 4939 measurement chain | Exact microphone, preamplifier/conditioning, ADC, gain and calibration |
| Neural recording | Recorder/headstage/electrode chain unselected | Intended implant, event inputs, clock and file export |
| Timing connections | Shared markers; clock strategy open | Voltage/connector compatibility, onset and drift verification |
| Calibration/support | Reference, mounts, cables, power, storage | Traceable level measurement, stable geometry, data records |
| Behavior camera/enclosure | Optional | Include only if needed; verify camera frame timing if used |

Pricing is recorded separately in the [expanded equipment list](Mouse_Equipment_Pricing_2026-10-08.md). Public price listings do not change the availability status above.

## Educational software

The project includes a visual experiment walkthrough. Illustrative sounds, figures and calculations should be labeled as examples. A frontend does not confirm an experimental playback program, calibrated output, acquisition synchronization or a neural-data decoder. Keep these statuses distinct.

## Secondary visual and rodent work

For Xiaorong and Jiaao's visual assessment, establish the current animal/setup before listing display/stimulus software, refresh timing, photodiode/onset measurement and synchronization. These details remain unknown.

Lan also states that rodent sound isolation is unnecessary because comparable isolation is unavailable for sheep. Document background conditions in either case. McGinley students' informal surgery-feasibility impression is not a procedure or documented surgical plan. A possible craniotomy observation remains undated and unbooked.
