# Source register

## Current parts and budget comparison

The [two-page parts list](../output/pdf/Auditory_Hardware_Options_2026-10-09.pdf) now orders McGinley, SONIC, basic and compact. Every item now has a brief purpose description; [role verification](Item_Purpose_Audit_2026-10-10.md) checks the paper, supplied slides and primary equipment documentation. The October 10 revision removes visible dates, footnotes and borrowed-calibrator alternatives, and includes explicitly marked planning estimates for required TDT parts. [Planning estimate record](Planning_Estimates_2026-10-10.json) stores amounts, basis and limitations; [observed price evidence](Accurate_Setup_Prices_2026-10-09.json) retains October 9 seller observations unchanged. The [detailed comparison](../Accurate_Setup_Comparison_2026-10-09.md) separates planning totals from exact observed-price baskets and preserves timing/calibration evidence. Estimated amounts are author-set allowances, not supplier quotations, delivered totals or hard upper bounds.

Fresh methods review identifies SONIC's exact BNC USB-6361 assembly; the recommendation uses the cheaper screw-terminal variant with its different included PSU/cable. PXI-4461 hybrid compatibility, internal 20 ppm clock, 32-sample DAC delay and ES1's 4 kHz cutoff come from NI/TDT primary documentation. SONIC reported 56/11-millisecond processing delays, GPS/PTP source precision, converter sample spacing, raw speaker response and at-ear/neural uncertainty remain distinct. Component clock calculations are conditional; common references do not establish zero residual error. The original paper/slides do not identify the proposed M50/MM-1/R8090 measurement kit. Supplier stock and used condition are observations, not verified hardware performance. No vendor was contacted or part ordered.

## Earlier cost, precision and DIY comparison (superseded reading versions)

Checked October 9, 2026 for the revised [two-page decision PDF](../output/pdf/Auditory_Hardware_Options_2026-10-09.pdf). [Current price inputs](Sound_Decision_Prices_2026-10-09.json) preserve direct eBay, Reverb, DigiKey, Sweetwater, Arduino and Adafruit purchase URLs, conditions, unit prices and budget calculations. TDT MF2-M/SA1/ZB1PS remain quote-only. Excluded leads include sold-out SA1/power stock, conflicting-model NI listings and unavailable speaker boards; incomplete used NI units are identified rather than treated as ready replacements.

The saved SONIC v1 was re-read at Methods 6.1–6.2 (p.11) and 6.6 (p.13). Primary technical checks cover NI clock/sample-rate behavior, JBL/Dayton bands, REED reference accuracy, MF2/M50/MM-1 bandwidth/power and Arduino buffered analog I/O. The PDF keeps clock accuracy, sample spacing and one-frequency calibration separate from unmeasured acoustic/neural accuracy. Complete URLs are retained in the price input file and PDF.

The Arduino/FPGA plans are candidate engineering paths, not tested hardware or executable animal protocols. An uncalibrated demo and a proposed sound-research assembly have different prices and purposes. Firmware, connections, recorder compatibility and physical validation remain open; no program was built or run, vendor contacted or part ordered.

The latest reading version focuses on two setups and distinguishes delay, trial variation and accumulating clock mismatch. Timing derivations are added to the same price-input record: [NI 6361 specifications](https://download.ni.com/support/manuals/374650c.pdf) label defaults typical at 25°C and list 50 ppm / USB PFI 10 MHz reference; [NI synchronization concepts](https://www.ni.com/en/support/documentation/supplemental/10/synchronization-explained.html) explain independent clocks versus a shared trigger. [PortAudio](https://portaudio.com/docs/latency.html) supports buffer-duration calculations, while [stream information](https://portaudio.com/docs/v19-doxydocs/structPaStreamInfo.html) describes latency estimates. [NTi delay measurement](https://www.nti-audio.com/wp-content/uploads/download-manager-files/NTi_Audio_AppNote_Delay_Measurement.pdf) supports approximately 3 ms/metre acoustic travel. These calculations are not measured Rice latency, jitter or drift. The recorder clock and input compatibility remain unknown; ≤1 ms corrected residual alignment is a proposed acceptance goal.

## Shared hardware slides and used equipment comparison

Received October 9, 2026: [system diagram](hardware_slides_2026-10-09/01_system_diagram.png) and [equipment links](hardware_slides_2026-10-09/02_equipment_links.png), copied unchanged from Howard's attachments. The slides describe an NI PXIe rack, ES1/ED1 sound chain and separate Neuropixels system. Their component suggestions are reference material, not instructions or confirmed Rice inventory.

[Hardware comparison](../Auditory_Hardware_Options_2026-10-09.md) and [price inputs](Sound_Hardware_Prices_2026-10-09.json) record eBay asking-price leads, seller conditions, manufacturer specifications and clearly separated planning allowances. EBay destination defaults/cached dates vary; Houston checkout, stock, actual model identity and functional/calibration performance are unverified. No source manuscript bytes were changed.

The key manufacturer checks cover ES1/ED1 frequency and power limits, NI PXI-4461 hybrid-slot variants, waveform bandwidth, USB DAQ alternatives, filtered Avisoft 40026 acquisition, audible measurement/speaker limits, and neural synchronization. A cheap audible chain does not cover the complete SONIC frequency alphabet. See the comparison for direct sources and exclusions.

## Equipment pricing snapshot

[Expanded pricing record](../Mouse_Equipment_Pricing_2026-10-08.md), checked October 8, 2026. Each numeric price is linked to its manufacturer or direct seller. Avisoft prices are USD; Intan figures are manufacturer list prices with distributor confirmation required; Dell is an exact-configuration offer; the new B&K 4231 seller listing is EUR excluding VAT. No exchange-rate conversion, used-equipment substitution, or complete-system price is inferred.

The record also uses official NI package information, Avisoft microphone-variant documentation, ART amplifier specifications, Intan recording specifications, and Basler trigger specifications to identify dependencies. Search-index and directly refreshed NI prices differed; the record uses the refreshed exact SKU price. Stock for the Scan-Speak listing is unconfirmed; Samsung's listed SSD showed delivery unavailable. No quote requests, vendor contacts, or orders were sent.

## BCM equipment suggestions and manufacturer checks

Consulted October 8, 2026 for the [mouse equipment plan](../Mouse_Setup_Equipment_Plan.md) and the added equipment page in the [simple PDF](../output/pdf/Mouse_Auditory_Experiment.pdf).

- [Forwarded BCM equipment email record](BCM_Acoustic_Equipment_Email_2026-10-08.md): user-supplied suggestions from Tinghan via Xiaorong. BCM inventory does not establish Rice access. Only relevant provenance and clean equipment links are retained.
- TDT: [ES1/EC1 documentation](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/), [ED1](https://www.tdt.com/docs/hardware/ed1-electrostatic-speaker-driver/), and [ZB1PS](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/). Field/coupler roles, operating band, matched driver, and power dependencies.
- Peerless/Tymphany: [XT25TG30-04 manufacturer listing](https://products.peerless-audio.com/transducer/535). Exact model, nominal impedance, and stated frequency range.
- Scan-Speak: [R2004/602200 manufacturer page](https://www.scan-speak.dk/product/r2004-602200/) and [exact-model datasheet](https://www.scan-speak.dk/datasheet/pdf/r2004-602200.pdf). Do not substitute R2004/602000.
- Avisoft: [116Hm base interface and complete kit](https://avisoft.com/ultrasoundgate/116hm/), [manual](https://www.avisoft.com/usgmanual_116Hm.pdf), [40017 mic power module](https://avisoft.com/ultrasound-microphones/1-4-mic-power-module/), [calibration settings](https://www.avisoft.com/Help/RECORDER/trigger_level_calibration.htm), and [external-clock settings](https://www.avisoft.com/Help/RECORDER/advanced_usgh_device_settings.htm). Interface/microphone distinction, conditioning, calibration, and timing dependencies.
- Brüel & Kjær/HBK: [Type 4939 datasheet BP 1851–13](https://www.bksv.com/-/media/literature/Product-Data/bp1851.ashx), dated 2021-10. Cartridge, external polarization, classical preamplifiers, and individual calibration data. The English product-page retrieval was unavailable; the official datasheet was readable.

Manufacturer specifications describe candidate components. No local chain compatibility, calibrated output, timestamp accuracy, or experimental result has been measured.

## Mouse adaptation sources

Consulted October 8, 2026 for the [mouse setup proposal](../Mouse_Stimulus_Setup_Proposal.md). These primary studies and official technical documents support design questions; their experimental settings do not establish Rice equipment compatibility or a validated mouse protocol.

- Bowen, Winkowski and Kanold (2020), [Functional organization of mouse primary auditory cortex in adult C57BL/6 and F1 (CBAxC57) mice](https://www.nature.com/articles/s41598-020-67819-4). Strain comparison, frequency representation, and sound-level sensitivity in awake adult mice.
- Guo et al. (2012), [Robustness of cortical topography across fields, laminae, anesthetic states, and neurophysiological signal types](https://www.cmu.edu/dietrich/psychology/shinn/publications/pdfs/2012/2012jneurosci_guo.pdf). DOI 10.1523/JNEUROSCI.0065-12.2012. Frequency-map and response-property comparisons across tested states.
- Phillips, Schreiner and Hasenstaub (2017), [Diverse effects of stimulus history in waking mouse auditory cortex](https://pubmed.ncbi.nlm.nih.gov/28566458/). DOI 10.1152/jn.00094.2017. Dependence of subsequent-tone responses on stimulus history.
- NI, [Acquiring an Analog Signal: Bandwidth, Nyquist Sampling Theorem, and Aliasing](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/acquiring-an-analog-signal--bandwidth--nyquist-sampling-theorem-.html). Sampling and analog-bandwidth requirements.
- TDT, [MF1 Multi-Field Magnetic Speakers](https://www.tdt.com/product/mf1-multi-field-magnetic-speakers/). Manufacturer-stated ultrasonic and field-configuration capabilities.
- TDT, [ABR guide with acoustic calibration guidance](https://www.tdt.com/files/manuals/ABRGuideRA4PA.pdf). Microphone and delivery-geometry considerations; not a cortical stimulus prescription.
- TDT, [Input and Output Delays](https://www.tdt.com/files/fastfacts/IODelays.pdf). Hardware-specific digital and analog-converter delays; exact values are not transferred to Rice hardware.

## Paper - pinned version

- Title: *SONIC: A Benchmarking Paradigm for Brain-Computer Interfaces*.
- Citation: Perkins, S. M., et al. (2025). bioRxiv preprint. DOI: `10.1101/2025.09.30.679683`.
- Version: **v1**, content identifier `2025.09.30.679683v1`. A later version must be registered separately.
- [Versioned abstract](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1.abstract).
- [Versioned manuscript page](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1).
- [Normal PDF route](https://www.biorxiv.org/content/10.1101/2025.09.30.679683v1.full.pdf).
- Posted date: **2025-10-02**, verified in the manuscript and bioRxiv API.
- Local copy: [SONIC_2025_bioRxiv_v1.pdf](SONIC_2025_bioRxiv_v1.pdf), materialized on 2026-10-02 UTC from the private Library reference supplied by the parent researcher. The parent obtained it through the normal public manuscript browser/PDF route. Library identity/version attributes are preserved.
- Verified **18 readable pages**, correct title, DOI/version and methods on printed pp.11-12.
- Size: **1,465,185 bytes**.
- SHA256: `3c8de5dc6bad53a043f7b6181603cf5af223979c92cfc5eb486f1fa7842a0731`.
- License stated on the source: CC BY-NC-ND 4.0. The PDF is retained unchanged.
- Retrieval history: direct command-line PDF/XML requests returned HTTP 429 and web fetches failed; ordinary browser access subsequently succeeded. No access controls were bypassed.
- [Public API metadata snapshot](bioRxiv_v1_Metadata_2026-10-02.json), retrieved from [bioRxiv details API](https://api.biorxiv.org/details/biorxiv/10.1101/2025.09.30.679683) on 2026-10-02 UTC.
- [BibTeX citation](SONIC_v1.bib).

## Author organization overview

- Paradromics, ["Setting New Standards and New Records for Brain-Computer Interfaces"](https://paradromics.com/blog/bci-benchmarking/), dated October 3, 2025; consulted 2026-10-02 UTC.
- Used for the initial overview before manuscript access; the current paper notes are grounded in the manuscript. Treat company commentary as the author organization's account, not independent validation.

## Assignment source

- [Lan message record](Lan_Message_2026-10-01.md): supplied through the parent research task from Howard's shared message. Contains the confirmed team assignments and discussion preference.
- No Slack retrieval, external communication or calendar action was performed.

## Follow-up team direction

- [Team clarifications received October 7, 2026](Team_Clarifications_2026-10-07.md): follow-up Slack information supplied by Howard in this conversation.
- Primary target: sedated-sheep auditory-cortex responses to sound. A soundproof box and behavioral rig are not required. Visual adaptation and rodent feasibility are secondary.
- McGinley students shared rodent-rig/calibration input. Focused speaker and measurement questions remain useful; their surgery-feasibility impression is informal. A possible craniotomy observation is unconfirmed.
- Follow-up messages show clock times without dates. October 7 is the received/recorded date, not an inferred message/meeting date; “this Thursday” remains unresolved.
- This is supplied team context, not a manuscript fact or completed test. SONIC tested awake, alert sheep; no sedated result is established.
- No private Slack identifiers/URLs, external messages or calendar actions are retained or performed.

## Verified findings register

Parent research findings were received on 2026-10-02 UTC and checked against the local v1 PDF. [Paper notes](../Paper_Notes.md) identify the manuscript sections/pages supporting settings and results, distinguish main benchmarking from the Figure 5 sweep, and preserve unresolved method questions. Proposed Rice decisions remain separate.

No public code, data or supplement was located by the parent researcher. No linked publication was returned by the bioRxiv API at retrieval. These are bounded review outcomes, not absolute absence claims.
