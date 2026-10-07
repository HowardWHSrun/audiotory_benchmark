# Bench-validation plan

Updated October 7, 2026. **Proposed animal-free check; no bench-test evidence is recorded here.** The primary destination is a sedated-sheep auditory experiment. The bench check establishes sound delivery and timing, not a neural response or information transfer rate.

Lan does not require a soundproof box or behavioral rig. Validate the free-field arrangement and document background conditions and reference geometry. See [team clarifications](sources/Team_Clarifications_2026-10-07.md) and [setup requirements](Auditory_Setup_Requirements.md).

## Inputs to settle

- Exact waveform/sequence specification and declared SONIC differences.
- Hardware/software configuration, input/output limits and connection map.
- Speaker and microphone placement at the intended reference geometry.
- Microphone/calibration method, frequency coverage and level convention.
- Event definitions, clock mapping, run length and predeclared acceptance criteria.

Resolve missing paper details and exploratory grouping, or treat them as explicit Rice choices. The walkthrough provides illustrative examples; it is not evidence of implemented experimental playback or timing capture.

## Proposed sequence

| Step | Check | Evidence to retain |
|---|---|---|
| 1. Waveform review | File properties, scaling, ramps, routing, IDs, balancing and clipping. | Manifest, hashes and inspection. |
| 2. Electrical routing | Input/output limits, marker polarity/encoding, grounding and channels. | Specifications and connection map. |
| 3. Calibration capability | Microphone/measurement bandwidth, reference and level convention. | Models, calibration records and method. |
| 4. Acoustic delivery | Output per selected frequency at reference geometry; level, spectrum, distortion and background. | Raw captures, geometry, gains and results. |
| 5. Timing capture | Markers/electrical loopback and acoustics on a common clock if possible; validated mapping otherwise. | Raw channels, clocks and timestamps. |
| 6. Timing analysis | Defined onset/offset rule; latency, variability, pip duration, spacing and completeness. | Analysis, statistics and flagged events. |
| 7. Stability | Drift, buffering failures and event completeness during representative load/run length. | Full-run logs, errors and drift analysis. |
| 8. Reproduction | Another member reproduces the setup; relevant restart/change checks. | Independent setup record and comparison. |
| 9. Acceptance | Compare measurements with criteria and record gaps. | Pass/fail/conditional decision and version. |

Ask McGinley students about relevant speaker/calibration methods; copying an entire rodent rig is not the goal. No external message is sent by this plan.

## Acceptance criteria to define

| Criterion | Value/rule | Basis | Status |
|---|---|---|---|
| Waveform/sequence fidelity | To be defined | Rice stimulus specification | Unknown |
| Acoustic level/spectral fidelity | To be defined | Intended exposure, frequencies and measurement convention | Unknown |
| Geometry/background | To be defined | Intended sheep arrangement | Unknown |
| Onset/offset alignment | To be defined | Acquisition and analysis needs | Unknown |
| Latency variability/drift | To be defined | Run duration and temporal resolution | Unknown |
| Event completeness/errors | To be defined | Run-quality rule | Unknown |
| Reproducibility | To be defined | Agreed reproduction evidence | Unknown |

Use measured acoustics to assess delivery. Approximately 80 dB SPL, 192 kHz playback and 10 ms pips are paper settings, not automatically local acceptance limits.

## After bench validation

The next separate stage is the team's sheep response experiment under the intended animal-use protocol. Record actual animal state and delivery; establish response latency, quality and a usable window before selecting decoding. The source sheep were awake/alert, so no sedated neural performance follows from a passing audio bench test.

If ITR is later evaluated, preserve stimulus IDs, timing evidence and contiguous block boundaries; keep test data out of fitting and declare window selection/preprocessing. Main SONIC analysis and the reduced Figure 5 sweep are different protocols; see [paper notes](Paper_Notes.md).

## Validation record

Retain run ID; local date/time/timezone; operator/reviewer; purpose; configuration; waveform manifest; geometry; calibration; event/clocks; raw captures; analysis version; deviations; criterion decisions; and next action. Store raw evidence before summaries.
