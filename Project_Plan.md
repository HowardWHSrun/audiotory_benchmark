# Project plan

Updated October 7, 2026 (Houston). Sources: [Lan's initial request](sources/Lan_Message_2026-10-01.md), [team clarifications received October 7](sources/Team_Clarifications_2026-10-07.md), and [SONIC bioRxiv v1](Paper_Notes.md).

## Primary purpose and evidence status

The primary Rice target is **measuring auditory-cortex responses to sound in sedated sheep**. Lan clarified that a soundproof box and a behavioral rig are not required. Howard and Jiaao's immediate work is to define sound generation, identify a suitable speaker and sound-measurement chain, and establish reproducible electrical/acoustic timing.

SONIC tested **awake, alert sheep**. Sedated sheep are a Rice adaptation. The paper does not provide a sedated result, so its response windows, decoding accuracy and information transfer rate (ITR) cannot be treated as expected Rice performance. Establish the actual recorded response and timing under the intended Rice conditions before assessing decoding and ITR.

Use these labels throughout the project:

- **Confirmed team direction:** supplied team statements, with source context.
- **Paper fact:** settings and results checked against the pinned manuscript.
- **Proposed design:** a Rice choice that still needs evaluation.
- **Unknown:** an unanswered requirement, unverified equipment item or missing measurement.

## Confirmed responsibilities

| Person | Responsibility | Source |
|---|---|---|
| Howard Wang and Jiaao Zhang | Investigate auditory stimulus setup, now focused on the sheep target. | Initial assignment; clarified target in October 7 source record. |
| Xiaorong Zhang and Jiaao Zhang | Discuss visual-system adaptation for Xiaorong's current animal. | Initial assignment; secondary workstream, species unspecified. |
| Xiaorong Zhang | Evaluate rodent auditory-cortex implantation feasibility. | Initial assignment; secondary workstream, no procedure specified. |
| Team | Read the paper, discuss findings and arrange a mutually workable group discussion. | Initial assignment; time remains unconfirmed. |

## Current work and next deliverables

| Workstream | Concrete output | Completion evidence |
|---|---|---|
| Paper review | Verified method ledger and explanation of the sound-to-neural-decoding experiment. | [Paper notes](Paper_Notes.md) with page citations and explicit gaps. |
| Experiment website | Main page explains our planned sedated-sheep setup, sound/calibration paths, recording alignment, and open equipment choices. SONIC explanation and results stay within a separate Paper reference section. | Working setup diagram with component details; paper illustrations labeled and distinct from hardware playback or real-recording analysis. |
| Local inventory | Models, interfaces, calibration resources and practical gaps. | [Inventory](Equipment_Software_Inventory.md) supported by inspection, manuals or direct team input. |
| Sound generation | Waveform/sequence specification, delivery path and run manifest. | Exact parameters recorded; missing paper details resolved or declared as Rice adaptations. |
| Speaker and measurement | Suitable speaker/amplifier proposal and microphone/calibration method. | Frequency coverage, placement, level convention and measurement capability documented. |
| Electrical/acoustic timing | Event-channel map and clock-alignment plan. | Markers and acoustics can be compared with the acquisition clock using defined event rules. |
| Bench validation | Animal-free delivery/timing test. | Evidence meets agreed criteria in the [bench plan](Bench_Validation_Plan.md); no bench evidence is claimed yet. |
| Sheep response pilot | Documented sound-evoked recordings in the intended sedated condition. | Recorded response, quality and timing; any decoding uses a declared evaluation protocol. This stage is not complete. |
| Visual/rodent feasibility | Focused notes on stimulus delivery, response timing and access requirements. | Intended-setup evidence and relevant lab expertise; no informal impression becomes a surgical procedure. |

The website supports planning our experiment, with the paper as a reference. It does not establish that bench stimulus code, calibrated hardware or animal recordings exist.

## Focused McGinley follow-up

McGinley students shared their rodent rig and calibration approach. Use this as practical input rather than copying an entire parts list. Prepare focused questions about speaker model and usable frequency range, microphone/calibration equipment, reference geometry, frequency-by-frequency level measurements and event-to-acoustic timing. These questions are prepared here; no external messages have been sent.

Their impression of rodent surgery feasibility is informal. A possible craniotomy observation could help the feasibility work, but its date is not confirmed and it does not establish an approved procedure.

## Discussion preparation

The initial request preferred Thursday afternoon and allowed two or four weeks. Later supplied messages show clock times without dates; **“this Thursday” remains unresolved**. No date is inferred and no meeting or observation is booked.

Suggested topics:

1. Sedated sheep as the main target and the evidence needed before claiming a SONIC-like score.
2. Waveform generation, speaker bandwidth and measured output at sheep-ear geometry.
3. Microphone/calibration resources and existing lab methods worth reusing.
4. Recording event inputs, clock mapping and acoustic onset evidence.
5. Equipment gaps, next bench check and secondary visual/rodent questions.

## Decisions still open

- Which recording interface and acquisition software will Rice use?
- Which DAC, speaker/amplifier and microphone/calibration chain are available?
- What initial tone alphabet, duration and exposure settings will the sheep experiment use?
- What ramp shape, sequence-balancing rule and seed handling will Rice document?
- How will markers, sound arrival and recorded neural response be aligned?
- What response window and evaluation protocol fit the actual sedated recordings?
- When can a group discussion or possible craniotomy observation occur?
