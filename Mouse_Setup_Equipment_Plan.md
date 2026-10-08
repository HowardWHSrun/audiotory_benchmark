# Mouse setup: equipment to assemble

October 8, 2026. Howard clarified that we will use the lab's own probes and mainly need to assemble the sound setup. Treat sound functions as needing provision until access is confirmed. Neural-hardware and animal-preparation purchases are outside this budget. The [forwarded BCM list](sources/BCM_Acoustic_Equipment_Email_2026-10-08.md) gives candidates, not confirmed Rice equipment. The [short PDF](output/pdf/Mouse_Auditory_Experiment.pdf) is the reading version; this note keeps the supporting details.

Mouse state and tone settings remain open. Rice's confirmed primary project remains sedated-sheep auditory measurements. Howard wants the mouse sound setup designed with later sheep reuse in mind; transfer is an engineering aim, not a validated result.

## Sound delivery

The simplified reading budget uses one MF2-M mono kit, SA1, ZB1PS, and NI USB-6361. SONIC used MF1; TDT lists MF2 as its current generation. This is a proposed budgeting choice, pending the frequency band and hardware checks. [MF2 product](https://www.tdt.com/product/mf2-multi-field-magnetic-speakers/), [kit and SA1 support](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/).

Provisional free-field budgeting path:

**Computer and saved waveforms → NI timed analog output → SA1 → MF2 → mouse-ear position**, with ZB1PS power for SA1. The earlier ES1/ED1 candidates remain alternatives in the reference table below.

### Why this proposed speaker group?

- **MF2-M:** one through-air speaker kit, with a stand/accessories and a stated 1–80 kHz band. That includes SONIC's 1.4–32 kHz band and is a useful design basis for a shared mouse/sheep sound system. Manufacturer reference conditions do not establish output in our geometry. [MF2 range and package](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/).
- **SA1:** TDT supports this amplifier with MF2. It supplies speaker-driving power from the NI waveform; SONIC also used SA1. [MF2 support](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/), [SA1](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/).
- **ZB1PS:** SA1 requires System 3 zBus power; this powered chassis supplies it and houses the module. It is a hardware dependency in our proposed chain. [SA1 power](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/), [ZB1PS](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/).

### What SONIC actually used

The manuscript's Methods 6.2 (printed p.11) names NI USB-6361 output at 192 kHz, SA1 at 0 dB attenuation, MF1 in free-field use at about 80 dB SPL at sheep-ear distance, and a TimeMachines TM2500C providing PTP/10 MHz clock references. It records electrical sound-output/trial-start loopback for alignment. **MF2-M, ZB1PS, and our Avisoft measurement kit are proposed Rice choices:** the exact power unit and measurement microphone are not named in the paper. Its 80 dB level is a published condition, not a selected mouse or sedated-sheep exposure. [Saved SONIC v1](sources/SONIC_2025_bioRxiv_v1.pdf), [paper notes](Paper_Notes.md).

| Candidate | What the manufacturer establishes | What it means for our plan |
|---|---|---|
| TDT ES1 | Free-field electrostatic model; stated response ±11 dB over 4–110 kHz. TDT advises operation from 4 kHz upward and reports distortion/degradation below that range. [Speaker documentation](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/) | A candidate for ultrasonic tones through the air. It cannot be assumed to reproduce SONIC's full explored 1.4–32 kHz range. Measure output at each selected frequency and geometry. |
| TDT EC1 | Coupler/tubing model; response depends on coupling, tube length, and the ear. [Speaker documentation](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/) | A separate delivery choice if we want tubing to the ear. Its reference curve cannot be transferred to a different coupling arrangement. |
| TDT ED1 | Analog-input driver for ES1/EC1 only, powered by System 3 zBus through a chassis such as ZB1PS. [ED1 documentation](https://www.tdt.com/docs/hardware/ed1-electrostatic-speaker-driver/) | Include power/chassis and matching speaker cable. A DAC is still needed to generate the analog waveform; ED1 is not the amplifier for the conventional tweeters below. |
| Peerless XT25TG30-04 | Manufacturer lists 4 Ω and a frequency range of 800–20,000 Hz. [Exact-model listing](https://products.peerless-audio.com/transducer/535) | Needs a suitable conventional amplifier. The listing does not establish calibrated 32 kHz output. |
| Scan-Speak R2004/602200 | Exact-model 4 Ω ring radiator. [Manufacturer page](https://www.scan-speak.dk/product/r2004-602200/), [datasheet](https://www.scan-speak.dk/datasheet/pdf/r2004-602200.pdf) | Needs a suitable conventional amplifier and measurement over our chosen band. Do not substitute the different R2004/602000 model's data. |

Choose the usable frequency band before committing to the speaker/output combination. A speaker's upper-frequency specification does not establish the DAC's bandwidth: at 192 kSa/s, the theoretical Nyquist boundary is 96 kHz, with practical filter margin also required. SONIC used 192 kSa/s with NI USB-6361, SA1, and MF1; that is a separate published chain, not the BCM ES1/ED1 path. See [paper notes](Paper_Notes.md).

## Acoustic measurement

The [simple shopping budget](Mouse_Equipment_Pricing_2026-10-08.md) uses **one complete 116Hm kit**. Other routes below are alternatives retained for reference, not extra purchases. The kit's microphone specification starts at 2 kHz; lower required tones would change this choice.

- **Avisoft complete kit:** UltraSoundGate 116Hm plus CM16/CMPA microphone/preamplifier, cable, stand, and RECORDER USGH software. The base 116Hm is a one-channel USB acquisition interface; its kit must be specified explicitly. The manufacturer's listed computer support is Windows. [116Hm product and kit details](https://avisoft.com/ultrasoundgate/116hm/).
- **B&K measurement chain:** 4939 cartridge → compatible classical preamplifier → external polarization/conditioning → acoustic ADC/recorder. The cartridge requires 200 V external polarization; 4939-A-011 includes a 2670 preamplifier. [4939 datasheet](https://www.bksv.com/-/media/literature/Product-Data/bp1851.ashx).
- **Possible hybrid:** Avisoft's 40017 mic power module lists B&K 2670 compatibility with UltraSoundGate. Confirm exact connector, power, gain, and bandwidth before assembling it. Its optional 15 kHz high-pass filter would attenuate lower candidate frequencies. [Power-module documentation](https://avisoft.com/ultrasound-microphones/1-4-mic-power-module/).
- **Calibration:** obtain microphone sensitivity/frequency-response records and a compatible sound-level reference. Record the measurement gain and ear-position geometry. A waveform capture, or a reference at only one frequency, does not establish absolute SPL across the whole band. [Avisoft calibration guidance](https://www.avisoft.com/Help/RECORDER/trigger_level_calibration.htm), [4939 individual calibration data](https://www.bksv.com/-/media/literature/Product-Data/bp1851.ashx).

One 116Hm analog channel cannot independently capture both the microphone and an electrical playback monitor simultaneously. Plan additional channels if both are needed. Its acoustic listening output is not the stimulus playback DAC. [116Hm manual](https://www.avisoft.com/usgmanual_116Hm.pdf).

## Timing and the remaining equipment

| Function to provide | Choice still needed |
|---|---|
| Tone generation and playback | Computer/OS, software, timed DAC/DAQ, output bandwidth, and saved sequence/configuration |
| Connection to lab neural recording | Use the lab's own probes; confirm recorder/headstage interfaces, event inputs, clock, and export format. Their models and accessory availability remain unverified. |
| Alignment | Compatible event outputs/inputs; clock-sharing or repeated-marker alignment; validated acoustic onset and drift |
| Sound-level measurement | One complete microphone/conditioning/acquisition chain plus calibration records and reference |
| Repeatable geometry | Speaker/microphone mounts, distance/orientation record, cables, power, and background-sound record |
| Data storage | Raw neural/acoustic recordings, event/sample mappings, sequence, and configuration |
| Optional behavior | Camera and verified frame timing if behavior is part of the experiment |

Schedule tone markers with playback hardware and record them in the neural and acoustic streams. A computer command timestamp does not establish actual sound arrival. Shared event markers also do not automatically unify two sampling clocks; check offset, drift, converter delay, and microphone onset on the bench.

For 116Hm, the DIN marker is embedded in 16-bit recorded samples and is unavailable in 8-bit mode. Current Avisoft settings also support an external sample clock at 16 times the desired WAV sampling rate, with a separate ADC-start input. This is a possible synchronization route, not a confirmed match to our unknown neural recorder. [116Hm manual](https://www.avisoft.com/usgmanual_116Hm.pdf), [external-clock documentation](https://www.avisoft.com/Help/RECORDER/advanced_usgh_device_settings.htm).

A soundproof box, sound isolation, and behavioral rig are not required by [current team direction](sources/Team_Clarifications_2026-10-07.md). Any enclosure remains a placement option; background sound and geometry still need documenting. Animal preparation follows the later awake/sedated decision and is outside this sound-shopping budget.

## Reusing the mouse sound setup for sheep

- Intend to reuse speaker, amplifier, powered chassis, NI, computer, and acoustic recorder, with the lab's probes for neural recordings. This does not confirm recorder/headstage interfaces or transfer performance.
- Adapt the mounts, distance, angle, and measurement position. Calibrate every selected tone at the sheep-ear position, verify clean output there, and recheck acoustic onset and alignment to the sheep recording timeline. A mouse calibration cannot be copied to the sheep geometry. [TDT configuration-specific calibration](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/).
- Resolve the lowest tone before buying the measurement kit: MF2's stated band begins at 1 kHz, but CM16/CMPA begins at 2 kHz. SONIC's 1.4 kHz tones and other tones below 2 kHz need another suitably calibrated microphone. Reusing the 116Hm recorder with that microphone may be possible, but its configuration/cost needs confirmation. [Microphone specification](https://avisoft.com/ultrasound-microphones/cm16-cmpa/).
- Select animal-specific stimulus levels and response windows with the team. The mouse preparation is undecided; Rice's sheep will be sedated, while SONIC's were awake. Hardware reuse does not establish equal neural responses, decoder performance, or achieved ITR. See the [team direction](sources/Team_Clarifications_2026-10-07.md) and SONIC Methods 6.6 (p.13).

See the [equipment budget and detailed reference prices](Mouse_Equipment_Pricing_2026-10-08.md) for one proposed shopping list, numerical estimates for quote-only/model-open items, bundled contents, and alternative subtotals. Estimates are our planning reserves, not vendor quotations.

All listed chains are proposals. Public price research does not establish access commitments, a supplier quotation, or a selected final configuration. We have not connected hardware or measured performance. Manufacturer documents were checked October 8, 2026.
