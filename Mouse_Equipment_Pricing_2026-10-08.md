# Mouse equipment list and prices

Prices checked October 8, 2026. This expands the [equipment plan](Mouse_Setup_Equipment_Plan.md) under Howard's assumption that we need to assemble the setup. The [PDF](output/pdf/Mouse_Auditory_Experiment.pdf) contains the experiment outline and grouped price tables.

- Prices are for **one new item/package**, unless stated otherwise. USD is the default; the B&K calibrator listing is explicitly EUR.
- **Quote needed** means no current numerical new price was verified. **Model open** means we have not selected a part to price.
- Prices are public listings or manufacturer list prices, not Rice quotations. Offers and stock can change. Educational eligibility is unconfirmed.
- Shipping, sales/import taxes, and installation are excluded unless the seller explicitly includes them. Newark states its displayed prices include applicable duties/tariffs. The EUR calibrator price excludes VAT; no currency conversion is assumed.
- Choose one sound path and one acoustic measurement path. Do not sum every alternative or buy an extra part already included in a kit.

## What would we actually get?

**Choose one sound-delivery setup and one sound-measurement setup.** A setup may contain several parts that work together. The item tables below are a price reference, not a checklist to buy every row.

### Sound measurement: choose A, B, or C

| Choice | Get these together | Already included / do not add |
|---|---|---|
| **A: complete Avisoft kit — most bundled option** | **1 × 116Hm complete kit**, 51165 ($8,160) or eligible educational 51166 ($7,320) | Includes microphone, preamplifier, acoustic recorder, cable, stand, and software. Do not add another base 116Hm, 40011 microphone, 40017 module, or any B&K parts. |
| **B: microphone connected to NI — alternative to A** | **1 × 40026 filtered microphone package** ($2,580) **plus 1 × compatible NI USB-6361** ($3,030.42) | The 40026 includes microphone, preamplifier, filter, cables, and stand. NI records the sound. Use the same NI device counted for tone output if that configuration is verified; count it once. Do not add the 116Hm kit or the 40011/40013/40014/40017 parts. External power and acquisition configuration still need checking. |
| **C: B&K specialist setup — alternative to A/B** | **1 × 4939-A-011 microphone/preamp set + 1 × matched conditioner + 1 × suitable acoustic ADC** | The set already contains the 4939 cartridge and 2670 preamplifier. Conditioner/ADC models and complete-chain compatibility need defining before a quote. Do not add a separate 4939 or 2670 again. |

For the easiest package to understand and assemble, **A is the starting comparison**. B may reduce equipment cost by using the NI acquisition already planned, but needs more integration work. This is planning guidance, not a selected purchase. A/B's microphone specification starts at 2 kHz; lower intended tones need a different or separately characterized measurement choice.

**Calibration is an additional choice for whichever route we use.** We need a sound-level reference and calibration records appropriate to our selected frequency band. The 60105 reference ($552) is an optional 40 kHz check, not a required part of every kit or proof of calibration at every frequency. The B&K 4231 and its quarter-inch adaptor belong to a separate compatible calibration arrangement; do not automatically buy both reference systems.

### Sound delivery: choose one group

| Choice | Parts to get together | Parts to leave out |
|---|---|---|
| **S1: TDT electrostatic** | 1 × ES1 + 1 × ED1 + 1 × ZB1PS | EC1 replaces ES1 only if tubing/coupled delivery is selected. No SA1, MF1, or ART in this group. |
| **S2: SONIC reference chain** | 1 × MF1 + 1 × SA1 + 1 × ZB1PS | No ES1, EC1, ED1, or ART in this group. |
| **S3: conventional tweeter** | (1 × Peerless **or** 1 × Scan-Speak) **plus** 1 × suitable ART amplifier | Choose one tweeter; do not buy two amplifiers. No ED1/SA1/ZB1PS in this group. |

Each sound group still needs timed waveform output. The candidate is **one NI USB-6361**; if measurement choice B uses that same unit, count it only once. AD3 is a separate optional bench tool, not an automatic extra or verified replacement for the final NI system. Cables, mounts, acoustic output, and timing remain to be checked for the selected group.

## 1. Sound delivery and timed output

| Item / exact model | Price for one | Role, package, and availability | Price source |
|---|---:|---|---|
| TDT ES1 | Quote needed | Free-field electrostatic speaker; intended operation from 4 kHz upward. Confirm included matching cable and mount. New availability unconfirmed. | [TDT product](https://www.tdt.com/product/es1-ec1-electrostatic-speakers/), [quotation route](https://www.tdt.com/request-a-quote/) |
| TDT EC1 | Quote needed | Coupler/tubing speaker, alternative to ES1; new availability unconfirmed. | [TDT product](https://www.tdt.com/product/es1-ec1-electrostatic-speakers/), [quotation route](https://www.tdt.com/request-a-quote/) |
| TDT ED1 | Quote needed | Two-channel driver for ES1/EC1; needs analog waveform source and zBus power. | [ED1](https://www.tdt.com/docs/hardware/ed1-electrostatic-speaker-driver/), [quotation route](https://www.tdt.com/request-a-quote/) |
| TDT ZB1PS | Quote needed | Powered zBus chassis for the ED1 or SA1 route; count once in the selected route. | [ZB1PS](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/), [quotation route](https://www.tdt.com/request-a-quote/) |
| TDT MF1 | Quote needed | SONIC speaker reference; specify mono/stereo package. Mono package includes a stand. Exact availability needs confirmation; current page also points to MF2. | [MF1](https://www.tdt.com/product/mf1-multi-field-magnetic-speakers/), [quotation route](https://www.tdt.com/request-a-quote/) |
| TDT SA1 | Quote needed | SONIC amplifier reference; also needs zBus/ZB1PS power. | [SA1](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/), [quotation route](https://www.tdt.com/request-a-quote/) |
| Peerless XT25TG30-04 | $28.47 | Bare tweeter, quantity-one price. DigiKey showed zero stock and 30-week manufacturer lead time. Does not establish calibrated 32 kHz output. | [DigiKey](https://www.digikey.com/en/products/detail/peerless-by-tymphany/XT25TG30-04/6557547) |
| Scan-Speak R2004/602200 | $178.60 | Bare tweeter. Stock unconfirmed: extracted page includes an out-of-stock message. | [Madisound](https://www.madisoundspeakerstore.com/soft-dome-tweeters-scanspeak/scan-speak-r2004/602200-19mm-small-ring-radiator-tweeter/) |
| ART SLA-1 | $279.99 | Two-channel conventional amplifier candidate. Sweetwater showed in stock; excludes DAC and speaker. | [Sweetwater](https://www.sweetwater.com/store/detail/SLA1--art-sla-1-100-watt-power-amplifier) |
| NI USB-6361, 781442-01 | $3,030.42 | Exact Newark SKU, each; one in stock displayed. NI specifies USB cable and desktop power supply; confirm power cord and connection accessories. | [Newark](https://www.newark.com/ni-now-part-of-emerson/781442-01/multifunction-i-o-device-usb-6361/dp/14AJ5341), [NI package](https://www.ni.com/en/shop/hardware/voltage/model-usb-6361) |
| Digilent Analog Discovery 3, 410-415 | $379.00 | Lower-cost bench waveform candidate; long-sequence streaming, output levels, and tone-marker timing still need verification. BNC adapter/accessories extra. | [Digilent](https://digilent.com/shop/analog-discovery-3/) |

Technical boundaries: ED1 drives TDT electrostatics; ART is a candidate for a conventional tweeter and is not an ES1 driver. ART's official specified response is 10 Hz–40 kHz, not the ES1's full ultrasound range. The Peerless manufacturer states 800–20,000 Hz; higher-band suitability remains unverified. AD3 is a bench comparison, not a demonstrated substitute for SONIC's playback system. See [ART specifications](https://artproaudio.com/installation/product/131226/sla1), [Peerless specifications](https://products.peerless-audio.com/transducer/535), and [AD3 datasheet](https://files.digilent.com/datasheets/Analog-Discovery-3-Datasheet.pdf).

## 2. Acoustic components: reference prices only

All numbered Avisoft prices below come from the [official USD price list](https://avisoft.com/price-list-ordering-information/). Kit contents are checked against the [116Hm description](https://avisoft.com/ultrasoundgate/116hm/) and [microphone variants](https://avisoft.com/ultrasound-microphones/cm16-cmpa/). Use the A/B/C groups above to decide which rows belong in a selected setup; do not buy this entire table.

| Item / exact SKU | Price for one | What to count |
|---|---:|---|
| 116Hm interface, 41165 / educational 41166 | $7,200 / $6,360 edu | Without microphone; RECORDER USGH included. |
| 116Hm complete kit, 51165 / educational 51166 | $8,160 / $7,320 edu | Includes CM16/CMPA, preamplifier, cable, stand, and recorder software. |
| CM16/CMPA microphone kit, 40011 | $1,080 | For an UltraSoundGate base; already included in the complete recording kit. |
| Traditional mic power module, 40017 | $1,320 | Possible B&K-preamp-to-USG conditioning; exact connector/configuration must match. |
| CM16/CMPA-5V package, 40013 | $1,800 | Microphone/conditioning for external acquisition; lacks anti-alias filter. |
| CM16/CMPA40-5V package, 40014 | $2,160 | Adds adjustable gain; lacks anti-alias filter. |
| CM16/CMPA48AAF-5V package, 40026 | $2,580 | Adds gain and anti-alias filter; candidate for compatible NI acquisition. |
| Calibrated 40 kHz reference generator, 60105 | $552 | One-frequency reference; not whole-band calibration. |
| B&K 4939 cartridge | Quote needed | Needs compatible preamplifier, polarization/conditioning, and acquisition. [Official datasheet](https://www.bksv.com/-/media/literature/Product-Data/bp1851.ashx). |
| B&K 4939-A-011 set | Quote needed | Includes 4939 and 2670; do not add a second preamplifier. [Manufacturer set](https://www.bksv.com/transducers/acoustic/microphones/microphone-set/4939-a-011). |
| B&K 2670 standalone preamplifier | Quote needed | Needed only when not included in the selected set. [Manufacturer page](https://www.hbkworld.com/ko/products/transducers/acoustic/microphone-preamplifiers/classic-type/2670). |
| B&K NEXUS 2690-A-0F2 | Quote needed | Conditioner option; still needs an ADC. Alternative to other suitable conditioning. [Manufacturer family](https://www.hbkworld.com/en/products/instruments/sound-vibration-daq/nexus/2690-a-0f2-microphone). |
| B&K 4231 sound calibrator | EUR 1,764, excl. VAT | New-sale listing, quotation/availability to confirm. Calibration service is additional. [Leasametric](https://www.leasametric.com/en/product/bruel-kjaer-4231/). |
| DP-0775 quarter-inch calibrator adaptor | Quote needed | Additional for 4939; 4231's included adaptor is half-inch. [4231 datasheet](https://www.bksv.com/doc/bp1311.pdf). |

The 40013/40014/40026 packages are alternatives to a separate UltraSoundGate interface when used with suitable acquisition. For an NI path, the manufacturer recommends anti-alias filtering, such as the 40026 variant. Verify input range, gain, power, sampling, software, and calibration. Do not also add the bare 40011 microphone or separate polarization module to these complete packages.

CM16/CMPA's stated band begins at 2 kHz, so it is not an assumed calibrated reference for SONIC's 1.4 kHz lower end. The 40 kHz reference and B&K's 1 kHz calibrator are different references; neither proves the complete system response across every selected frequency.

## 3. Neural recording, computer, storage, and optional video

Intan is a **cost comparison** while the intended Rice implant/recorder remains open. If selected, the controller, one headstage, its SPI cable, and a compatible electrode go together. Add a shared computer and storage. The camera and its accessories are an optional group. This does not select a replacement for team hardware.

| Item / model | Price for one | Included / remaining dependency | Source |
|---|---:|---|---|
| Intan RHD controller C3004 | $9,950 list | Controller with USB and power cables. Supplier confirmation through White Mountain Systems is required. | [Intan pricing](https://www.intantech.com/pricing.html) |
| Intan RHD 32-channel headstage C3314 | $940 list | Check implant/electrode connector compatibility. | [Intan pricing](https://www.intantech.com/pricing.html) |
| Intan RHD SPI cable C3203, 0.9 m | $215 list | One controller-to-headstage cable. | [Intan pricing](https://www.intantech.com/pricing.html) |
| Electrode/probe and implant adapter | Model open | Separate from controller/headstage; must follow team's recording plan. | Team choice pending |
| Dell Slim ECS1250, offer ecs1250_so_16 | $549.99 offer | Windows 11 Home, i3-14100, 8 GB RAM, 512 GB SSD, keyboard/mouse. Monitor extra; performance/USB load needs matching. | [Dell exact offer](https://www.dell.com/en-us/shop/desktop-computers/spd/dellslimecs1250/ecs1250_so_16) |
| Samsung T7 Shield 2 TB, MU-PE2T0S/AM | $574.99 listed | Reference price; Samsung showed delivery/pickup unavailable. Capacity and a separate backup plan still need deciding. | [Samsung](https://www.samsung.com/us/memory-storage/portable-ssd/portable-ssd-t7-shield-usb-3-2-2tb-black-sku-mu-pe2t0s-am/) |
| Basler acA1300-200um, Edmund 33-978 | $585.00 | Optional camera body only. Needs lens, USB/I/O cables, mounting and illumination; trigger/frame timing needs validation. | [Edmund](https://www.edmundoptics.com/p/basler-ace-aca1300-200um-monochrome-usb-30-camera/3418/), [Basler](https://www.baslerweb.com/en-us/shop/aca1300-200um/) |
| Camera lens, I/O cable, light, mount | Model open | Price after field of view and working distance are chosen. | Not yet selected |
| Monitor and any computer upgrade | Model open | Depends on acquisition requirements; not included in PC price. | Not yet selected |

Intan's analog/digital event inputs are aligned with neural samples, but its sampling rate does not establish ultrasound capture. Use an appropriate acoustic ADC for microphone waveforms and validate alignment with neural markers. [Intan controller specifications](https://www.intantech.com/recording_controller.html).

## 4. Smaller parts, software, and setup support

| Item / model | Unit price / status | How to count it | Source |
|---|---:|---|---|
| Pomona 2249-C-36 BNC cable, 0.9 m | $30.99 each | Final quantity and termination depend on the connection map. | [Newark](https://www.newark.com/pomona/2249-c-36/coaxial-cable-assembly-bnc-male/dp/35F1074) |
| Avisoft 52002 DIN/DOUT screw-terminal adapter | $48 each | USG timing connection option; not proof of electrical compatibility. | [Avisoft price list](https://avisoft.com/price-list-ordering-information/) |
| Avisoft 50021 XLR-5 extension, 2 m | $60 each | Extra only if selected package cable is unsuitable. | [Avisoft price list](https://avisoft.com/price-list-ordering-information/) |
| On-Stage DS7200B desktop stand | $15.95 each | Extra only if kit stand is unsuitable; clamp/thread adapter separate. | [Sweetwater](https://www.sweetwater.com/store/detail/MicStdDesk--on-stage-stands-ds7200b-adjustable-height-desktop-stand) |
| Matching TDT speaker cable | Confirm package | Avoid adding a second charge for a supplied cable. | [TDT speaker docs](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/) |
| Speaker wire / DAC-to-amplifier cable / connectors | Model open | ART and TDT use different connections; choose after chain selection. | Connection map pending |
| NI terminal/connector accessories or AD3 BNC adapter | Model open | Depends on output-device SKU and wiring choice. | Selection pending |
| Clock distribution / level conversion, if required | Model open | Needed only if interfaces require it; verify electrical and timing requirements first. | Recorder interfaces pending |
| Speaker fixture / base / clamps / baffle | Model open | Price after geometry and package contents are known. | Mechanical design pending |
| Animal support, heating, restraint/head-fix equipment if needed | Preparation dependent | Mouse state is undecided; obtain a team-specific equipment list later. | Preparation pending |
| Enclosure or acoustic treatment | Optional / design open | No soundproof box is required by team direction. | [Team record](sources/Team_Clarifications_2026-10-07.md) |
| RECORDER USGH | Included with USG | Do not add a separate license to the 116Hm package. | [Avisoft price list](https://avisoft.com/price-list-ordering-information/) |
| Intan RHX | Free, open-source | Hardware still costs money. | [Intan controller](https://www.intantech.com/recording_controller.html) |
| Digilent WaveForms | Free | For the AD3 bench path; custom timing work remains. | [Digilent software](https://digilent.com/shop/software/digilent-waveforms/) |
| Stimulus/control software and analysis work | Tool choice open | Development labor and any paid license are not priced here. | Workflow pending |

## 5. Subtotals of priced parts

These are **partial subtotals**, not complete experiment budgets. Each includes one of each named item; alternatives are not combined. The 40 kHz reference in the examples is optional and must suit the intended calibration task. Count a shared NI device only once.

| Combination | Arithmetic | Priced subtotal | Excludes |
|---|---|---:|---|
| NI + filtered direct-DAQ microphone + 40 kHz reference | 3,030.42 + 2,580 + 552 | $6,162.42 | Speaker/amplifier, neural system, PC, cables/mounts, tax/shipping; integration and band calibration still unverified |
| NI + 116Hm complete kit + 40 kHz reference | 3,030.42 + 8,160 + 552 | $11,742.42 standard | Same remaining costs |
| Same, with eligible educational kit | 3,030.42 + 7,320 + 552 | $10,902.42 educational | Same remaining costs; discount eligibility unconfirmed |
| Example Intan recording hardware | 9,950 + 940 + 215 | $11,105 list | Electrodes/adapters, PC, storage, and acoustic hardware |
| Peerless + ART conventional sound pair | 28.47 + 279.99 | $308.46 | DAC, wiring/mounting/calibration; Peerless out of stock and high-frequency suitability unverified |
| Scan-Speak + ART conventional sound pair | 178.60 + 279.99 | $458.59 | Same dependencies; speaker availability/band suitability unconfirmed |

No price is assigned to an unselected part, and no quote-only component is counted as zero. TDT and B&K totals remain incomplete until complete-package quotes and recording choices are available. No supplier was contacted and no purchase was made.
