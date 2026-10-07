# SONIC paper notes

Pinned source: Sean M. Perkins et al. (2025), *SONIC: A Benchmarking Paradigm for Brain-Computer Interfaces*, bioRxiv, DOI [10.1101/2025.09.30.679683](https://doi.org/10.1101/2025.09.30.679683), **v1** (`2025.09.30.679683v1`). [Abstract](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1.abstract) · [PDF route](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1.full.pdf).

Posted October 2, 2025. This is a preprint, not peer reviewed. The [18-page source PDF](sources/SONIC_2025_bioRxiv_v1.pdf) is saved locally. The parent researcher's findings were checked against the materialized v1 PDF on 2026-10-02 UTC; page numbers below are the manuscript's printed pages.

Rice adaptation notes were updated October 7, 2026 from supplied team clarifications. The pinned paper facts and results remain distinct from that new direction.

## What the study does - verified paper facts

SONIC means **Standard for Optimizing Neural Interface Capacity**. The experiment sends a known random sound sequence into the auditory system, records the resulting neural activity, and tests how much of the sound sequence a decoder can recover. Information transfer rate (ITR) combines decoding errors with the presentation rate; a separate delay measure contextualizes the result. This benchmarks sensory decoding rather than voluntary communication or closed-loop stimulation. Source: Section 2, pp.4-5; Section 6.5, p.12.

Two awake male Suffolk Cross sheep, C and E, each had a 421-channel Connexus recording system in left primary auditory cortex. They were selected from a larger cohort for the greatest estimated auditory-cortex coverage. Each had one exploratory session followed by four benchmark sessions. This selected two-animal demonstration does not establish expected performance in another species, brain region or interface. Source: Section 3, p.5; Section 6.6, p.13.

## Results and their scope

| Animal | Session 2 | Session 3 | Session 4 | Session 5 | Mean ITR |
|---|---|---|---|---|---|
| Sheep C | 174.6 | 204.0 | 201.6 | 227.2 | 201.9 bps |
| Sheep E | 228.2 | 231.6 | 225.1 | 235.4 | 230.1 bps |

All session values are in bits/second. Both means exceeded 200 bps; every session did not. Exact-tone accuracy averaged 45.4% +/- 3.1% for C and 75.9% +/- 0.7% for E (mean +/- session standard deviation). C had 37 tone classes; E had 14. Their different error structure and stimulus alphabets explain why accuracy alone is insufficient. Source: Table 1 and surrounding text, p.7.

The reported **56 ms intrinsic delay** includes measurement (<1 ms), filtering (5 ms), binning (5 ms) and context accumulation (45 ms). It excludes computation and auditory physiology. The displayed analyses were offline. The authors separately report an online implementation with BCI delay below 100 ms, dependent on hardware/software choices; this is not the same delay definition as sound-request-to-output. Source: Section 2, p.5; Section 3, p.7; Section 4.1, p.9.

The **>100 bps at 11 ms intrinsic delay** result comes from a narrower window sweep for Sheep E, Session 2, with the first 40% of trials, one 75%/12.5%/12.5% training/validation/test split and a simpler decoder. It maximizes over observation-window alignment. It was not demonstrated across all eight benchmark sessions. Source: Figure 5, p.8; Section 6.4, p.12.

## Published sheep configuration - verified method ledger

**These are the paper's sheep settings, not an approved Rice or rodent protocol.** Tone duration and frequency alphabet are tunable benchmark parameters (Section 2, p.5).

| Topic | Extract from pinned v1 | Paper locator | Verification status |
|---|---|---|---|
| Benchmark definition | Held-out presented/predicted tone confusion matrix; bias-corrected mutual information divided by tone duration. | Section 6.5, p.12 | Verified |
| Subjects and recording | Two selected awake sheep; 421-channel Connexus; left primary auditory cortex. | Sections 3 and 6.6, pp.5,13 | Verified |
| Initial alphabet | 37 frequencies, described as 1/8-octave steps across 1.4-32 kHz. Exact 37-value array is absent from the methods text. | Section 6.1, p.11; p.7 | Verified description; array unresolved |
| Exploration | Durations 4-24 ms in 2 ms increments. Methods and Figure 2 caption differ on grouping; see questions below. | Section 6.1, p.11; Figure 2, p.6 | Verified; discrepancy unresolved |
| Benchmark alphabet | C retained the initial set; E used the 14-frequency set listed below. | Section 6.1, p.11 | Verified |
| Benchmark pips | 10 ms sine-wave pips; zero starting phase; 2 ms amplitude ramps at both ends; ramp shape unspecified. | Sections 6.1-6.2, p.11 | Verified; ramp shape unresolved |
| Sequence | Uniform random frequencies, balanced per block; pips consecutive without inter-tone silence. Blocks contain 8,000-15,000 tones; at least 12 blocks/session, with 1 second silence between blocks. | Section 6.1, p.11 | Verified; seed/balancing algorithm unresolved |
| Audio generation | Entire recording waveform prepared in advance; NI USB-6361 DAC at 192 kHz. Generation software/version not specified. | Section 6.2, p.11 | Verified hardware/rate |
| Sound delivery | TDT SA1 amplifier at 0 dB attenuation and MF1 speaker in free-field use; approximately 80 dB SPL at the sheep's ear distance. Position and frequency-specific calibration are not specified. | Section 6.2, p.11 | Verified reported setup; calibration details unresolved |
| Synchronization | TimeMachines TM2500C GPS server supplies IEEE 1588 PTP and 10 MHz reference. Analog sound output and rising-edge trial-start signal return to NI-DAQ analog inputs; edge timestamps align with broadband recordings from all channels. | Section 6.2, p.11 | Verified electrical scheme; acoustic jitter not reported |
| Neural features | Spike counts and spike-band power in 5 ms bins; main decoder receives ten bins from 10-60 ms after tone onset. | Section 6.3, p.11 | Verified |
| Evaluation | Contiguous blocks kept within folds; 8-16 folds with separate validation/test sets and pooled held-out test predictions. | Section 6.4, p.12 | Verified |
| Reuse assets | No public code, data or supplement was located in the parent review. This is a search outcome, not proof that none exists. | Parent review and manuscript | Access unresolved |

Sheep E's refined frequencies, in kHz: **2, 4, 6, 8, 9, 10.5, 17, 18.2, 19.5, 20.9, 22.4, 24, 25.8, 27** (Section 6.1, p.11). Do not reconstruct Sheep C's array by guessing endpoints or rounding.

### Processing and evaluation details

The paper's analog bandwidth is approximately 10 Hz-2.2 kHz, digitized at 5.2 kHz. Digital processing uses an approximately 300 Hz high-pass filter, zero-phase over a rolling 5 ms buffer, followed by common-average referencing. Spike counts use crossings below -3 times channel RMS, estimated from the first 2 seconds, with a 1 ms minimum event interval. Spike-band power averages squared filtered voltage within each 5 ms bin. Source: Section 6.3, p.11. These are recording-specific choices, not universal Rice requirements.

The main decoder is a two-layer 1D CNN, 400 units/layer, kernel size 5 and stride 1. Training uses cross-entropy, AdamW, batch size 64, initial learning rate 0.001 and stated linear decrement of 10^-7 per batch. Validation ITR is evaluated every 500 batches; early stopping patience is 5. Z-score parameters use a subset of training and validation data, excluding test data. Source: Section 6.4, p.12.

Adjacent tone feature windows overlap, so random trial-level splitting would leak shared data. Preserve complete contiguous blocks within partitions when planning Rice evaluation; document preprocessing/normalization scope and keep test data out of fitting. Source for the paper's block-level partitioning: Section 6.4, p.12. Rice implementation remains a proposal.

For K tone classes and N held-out predictions, the paper subtracts bias **(K-1)^2 / (2 N ln 2)** from confusion-matrix mutual information and divides by tone duration in seconds. The rate therefore uses error structure, not just percent correct. Its denominator does not amortize block silence, calibration or training time; that is an interpretation of the stated equation, not a separate measured session-throughput result. Report wall-clock useful throughput separately if needed. Source: Section 6.5, p.12. Raw device data bandwidth and decoded ITR are different quantities.

Record exact settings together with their experimental context. Do not combine the main eight-session analysis with the simplified Figure 5 sweep as one protocol.

## Rice adaptations - proposals, not paper facts

**Confirmed team direction received October 7, 2026:** the primary Rice task is measuring sound-evoked auditory-cortex responses in **sedated sheep**. Lan does not require a soundproof box or behavioral rig. This updates the project target, not the source paper. SONIC sheep were **awake and alert** (Section 6.6, p.13), and the manuscript supplies no sedated result. See [team clarification record](sources/Team_Clarifications_2026-10-07.md).

Sedated sheep are an adaptation. Establish local recorded response timing and a useful observation window; do not transfer the published windows, accuracy or ITR as expected performance. Sedation may affect evoked responses, so record the condition when interpreting local timing and decoding. No sedated measurement is claimed here.

Immediate engineering work covers sound generation, speaker and microphone/calibration capability, and electrical/acoustic alignment. Preserve stimulus identity and reproducible alignment to recordings. Local hardware choices depend on inventory and measurements. Repeatable geometry and background-condition records remain useful without a required enclosure.

McGinley students shared rodent-rig and calibration input. Prepare focused questions about speaker coverage, microphone/measurement hardware, calibration geometry and timing instead of a wholesale parts list. Their surgery-feasibility impression is informal, and a possible craniotomy observation remains undated. Lan also does not require rodent sound isolation, citing its unavailability for sheep. These are team inputs, not SONIC findings.

A visual adaptation requires its own stimulus-delivery and onset-validation plan. Rodent auditory implementation needs separate feasibility assessment. Both are secondary to sheep auditory work. The educational walkthrough can illustrate these stages, but frontend examples are not experimental playback code, calibration, neural data or a measured benchmark.

Functional equivalents may be suitable for waveform generation, sound delivery and clock/event capture. Rice should validate both electrical timing and measured acoustic onset; an electrical loopback alone does not prove sound timing at the reference position. Before animal use, review hearing range, sound level and exposure duration against the intended animal and approved lab protocol.

For a visual adaptation, Xiaorong and Jiaao should assess the alphabet of visual stimuli, display refresh behavior, photodiode timing, viewing geometry and appropriate neural-response windows. These are proposed questions; no visual result or species-specific configuration is established here.

## Limits and provenance

Only two selected animals were benchmarked. There is no matched-device comparison in this study; the score depends on stimulus selection and decoder choices. Attention was not explicitly controlled. The paper does not establish performance for a visual/rodent adaptation or an uncalibrated decoder carried unchanged across days. Source: Sections 2-4, pp.5-10; subject selection in Section 6.6, p.13.

All authors disclose current or former full-time Paradromics employment and equity (Section 9, p.14). Company explainers are supporting context, not independent validation. The bioRxiv API returned no linked published article when checked on 2026-10-02 UTC; this does not prove no publication exists elsewhere.

## Reproducibility questions to take to the team

- What is the exact initial 37-frequency array, including endpoints and rounding?
- What ramp shape, amplitude convention and balancing/randomization algorithm were used? Are stimuli, seeds or code available?
- Section 6.1 (p.11) says each exploratory block included every duration, with same-duration groups and 1 second silence between groups. Figure 2 (p.6) says durations varied across blocks. Which grouping should a replication use?
- What were speaker position, frequency-specific calibration, level convention and measured acoustic latency/jitter?
- How should normalization, uncertainty estimation and observation-window selection be documented for fair held-out evaluation?
- Which paper choices should Rice preserve, and which changes would make the work an adaptation?
- How will the sedated-sheep condition be recorded, and what local evidence will justify response/decoding windows?
- Which parts of McGinley's speaker and calibration method apply to sheep geometry?
- Which delay and wall-clock throughput definitions should a Rice report include?
