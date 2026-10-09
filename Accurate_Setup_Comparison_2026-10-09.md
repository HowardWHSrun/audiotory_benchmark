# Auditory setup comparison: three specialized options

Checked October 9, 2026. One sound output channel, reusing our computer and neural recorder. These are public USD item asking prices; delivery, tax, added tariffs, labor, quote-only TDT parts and unresolved connections are excluded. No price is a delivered quotation or a reservation. The [four-page PDF](output/pdf/Auditory_Hardware_Options_2026-10-09.pdf) keeps the basic option on page 1 and gives each specialized option its own page, prepared for discussion with Dr. Luan. [Editable LaTeX](output/pdf/Auditory_Hardware_Options_2026-10-09.tex). [Detailed source/price record](sources/Accurate_Setup_Prices_2026-10-09.json).

| Version | Known-priced subtotal | With proposed measurement kit | What remains unpriced |
|---|---:|---:|---|
| SONIC paper sound chain | $4,840.36 | $7,357.58, new preamp | MF1-M, SA1/power quotes; mic/recorder/Ethernet connections |
| McGinley supplied-slide sound chain | $7,551.75 | $10,068.97, new preamp | ES1/cable quote; mic/recorder connections; any missing rack cord |
| Recommended sound + measurement chain | $5,636.47, new preamp | Included | MF2-M, SA1/ZB1PS quotes; recorder interface |

The main comparison uses the $945 new MM-1 amplifier. A freshly listed [B&H used unit for $604.50](https://www.bhphotovideo.com/c/product/803529754-USE/sound_devices_mm_1_single_channel_portable_microphone.html) reduces the compact proposal to $5,295.97, saving $340.50. Its specific-unit page displays moderate wear, in-stock status and a 90-day seller warranty; these are seller observations, not hardware verification. The earlier unretrievable $325 eBay offer is retained only in the historical source record. These are incomplete subtotals, not complete budgets or upper limits. Older $11,000–12,000 and $30,000 planning scenarios used explicitly labeled allowances and are superseded as current price comparisons. A defensible exact final total requires actual TDT quotes and a recorder-interface decision.

## 1. SONIC paper version

The pinned [SONIC v1](https://doi.org/10.1101/2025.09.30.679683), Methods 6.1–6.2, names USB-6361 assembly 152805A-03L (BNC SKU 782255-01), SA1, MF1 and a TM2500C GPS/PTP/10 MHz reference. The paper's Connexus neural system is excluded because we use our own recorder. Exact listed accessory numbers and the powered chassis below are reproduction additions, not claims about what the authors purchased.

| Part | Qty | Unit USD | Condition / source | Notes |
|---|---:|---:|---|---|
| [NI USB-6361 BNC, 782255-01](https://www.newark.com/ni-now-part-of-emerson/782255-01/multifunction-i-o-device-usb-6361/dp/14AJ5490) | 1 | $3,744.42 | new | Paper item |
| [TimeMachines TM2500C](https://timemachinescorp.com/product/gps-ntpptp-network-time-server-10mz-output-tm2500/) | 1 | $799.99 | new | Paper item |
| [NI 781513-01](https://www.newark.com/ni-now-part-of-emerson/781513-01/test-psu-desktop-mini-combicon/dp/14AJ5357) | 1 | $123.42 | new | Reproduction addition |
| [NI 780534-01](https://www.digikey.com/en/products/detail/ni/780534-01/16647424) | 1 | $69.75 | new | Reproduction addition |
| [NI 763830-01](https://www.newark.com/ni-now-part-of-emerson/763830-01/test-cable-assembly-power-cable/dp/13AJ3639) | 1 | $51.00 | new | Reproduction addition |
| [NI 781233-02](https://www.digikey.com/en/products/detail/ni/781233-02/18710754) | 1 | $38.25 | new | Reproduction addition |
| [TDT MF1, free-field mono configuration](https://www.tdt.com/product/mf1-multi-field-magnetic-speakers/) | 1 | Quote required | new quote required | Paper item |
| [TDT SA1 stereo amplifier](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/) | 1 | Quote required | new quote required | Paper item |
| [TDT ZB1PS](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/) | 1 | Quote required | new quote required | Reproduction addition |
| [Hosa BNC-58-103 output lead](https://www.proaudiosolutions.com/Hosa-BNC-58-103-p/bnc-58-103.htm) | 1 | $13.53 | New / Pro Audio Solutions | Our added DAQ-to-amplifier lead |

**Paper-reported processing delay:** 56 milliseconds, consisting of neural measurement below one, filtering five, feature binning five and decoder context 45 milliseconds (paper pages 5 and 7). The paper reports 56 although the components sum to less than 56. It excludes sensory physiology and computer calculation time. A separate one-session analysis reports 11 milliseconds (pages 8 and 12); discussion reports a separate online device-plus-computation evaluation below 100 milliseconds (page 9). None is an acoustic-to-neural synchronization error. Buying the listed sound parts without Connexus does not establish these delays for our recorder. See the [full timing audit](Timing_and_Price_Audit_2026-10-09.md).

**Precision:** paper band 1.4–32 kHz; nominal 192 kSa/s means 5.208 µs spacing, not acoustic-to-neural accuracy. Read back the actual NI sample rate. The [2019 TDT speaker guide](https://www.tdt.com/wp-content/uploads/2019/04/SpeakerGuide.pdf) gives MF1 free-field response as 1–65 kHz, raw ±13 dB; the paper's approximately 80 dB at the ear has no quantified ±dB uncertainty. TM2500C's PTP <1 µs plus network jitter describes the reference, not whole-system alignment. NI's default typical-at-25-degrees-Celsius free-running 50 ppm figure corresponds to 3 ms/min or 180 ms/hour versus ideal time; it is not SONIC's achieved drift after GPS locking. The paper does not give measured acoustic-to-neural jitter or long-session drift. Recorder synchronization remains open.

TM2500C is backordered, and includes PSU, GPS patch antenna and two SMB–BNC cables. Verify current MF1 kit contents and avoid duplicate power/cable accessories. A freshly opened [seller-new eBay BNC unit for $3,498.95](https://www.ebay.com/itm/178144942290) displays two available and 60-day buyer-paid returns. It saves $245.47 relative to the distributor offer: $4,594.89 sound parts, or $7,112.11 with the new-amplifier measurement kit. Confirm the actual SKU, accessories, condition/authenticity and shipping/import costs before substituting it. Do not replace it with a mass-terminated listing without pricing its different connectors and power.

## 2. McGinley supplied-slide version

Sources are the [system diagram](sources/hardware_slides_2026-10-09/01_system_diagram.png) and [part-links slide](sources/hardware_slides_2026-10-09/02_equipment_links.png). This is distinct from the separate BCM equipment email. Neuropixels is excluded because we reuse our own neural recorder. A compatible desktop and free PCIe slot are required; an arbitrary laptop or Mac cannot be assumed compatible.

| Part | Qty | Unit USD | Condition / source | Notes |
|---|---:|---:|---|---|
| [NI PXIe-1082 chassis](https://www.ebay.com/itm/406923647348) | 1 | $2,650.00 | Used; title says tested; China | No acquisition cards counted; confirm power cable and blanking panels. |
| [NI PXIe-6363 DAQ module](https://www.ebay.com/itm/335905594499) | 1 | $2,495.36 | Used; title says tested; South El Monte,CA | Free shipping displayed;60dayreturns. |
| [NI PXI-4461 hybrid slot board, 186900-11L](https://www.ebay.com/itm/198252264097) | 1 | $699.99 | Used; seller tested; Willis,TX | Title explicitly names 186900-11L, which NI certification calls HYBRID SLOT. Actual board/rear connector was not visually inspected; confirm actual item. Displayed shipping19.99USD is for a different ZIP; Houston checkout was not performed. |
| [NI PXIe-8360 MXI chassis controller](https://www.ebay.com/itm/286812339947) | 1 | $493.20 | Used; title says tested; China | Exact PXIe module; do not substitute PXI-8360. |
| [NI PCIe-8361 host card](https://www.ebay.com/itm/187559567628) | 1 | $197.00 | Seller labelsnew; Houston,TX | Existing compatible desktop with a free PCIe slot assumed. |
| [NI MXI-Express 779500-03 / 193355A-03 cable,3m](https://www.ebay.com/itm/307193912690) | 1 | $89.85 | Seller labelsnew | Exact slide cable. |
| [NI SHC68-68-EPM 192061C-02 cable,2m](https://www.ebay.com/itm/277089841525) | 1 | $89.99 | Used;Control Instruments | One bank as pictured; second cable only if channel map requires both. |
| [NI BNC-2090A breakout](https://www.ebay.com/itm/358482820683) | 1 | $613.77 | Used; seller saysworking; China | No returns displayed. |
| [TDT ED1 + zBus chassis + PS25F power bundle](https://www.ebay.com/itm/156873696386) | 1 | $209.06 | Used;NTCTech;RanchoCordova,CA | Seller description includes ED1, HB7, PS25F and zBus; tested,30-day warranty; cosmetic rust/scuffs. No other accessories. Do not double count chassis/power; HB7 is incidental. |
| [TDT ES1 free-field electrostatic speaker with matching high-voltage cable](https://www.tdt.com/product/es1-ec1-electrostatic-speakers/) | 1 | Quote required | Supplierquote | 2018 TDT catalog states a6m connection cable is included, but current kit must be quoted. Prior1500–2500USD numbers were planning estimates, not verified prices. |
| [Hosa BNC-58-103 output lead](https://www.proaudiosolutions.com/Hosa-BNC-58-103-p/bnc-58-103.htm) | 1 | $13.53 | New / Pro Audio Solutions | Our addition |

**Precision:** [ES1](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/) is 4–110 kHz, raw ±11 dB, and is unsuitable below 4 kHz per TDT. It does not reproduce SONIC's 1.4–4 kHz tones. The [PXI-4461](https://docs-be.ni.com/bundle/ni-4461-4462-specs/raw/resource/enus/373770k.pdf) output flatness is specified to 92.1 kHz at 204.8 kSa/s. At that rate sample spacing is 4.8828 µs and DAC filter delay is 32 samples = 156.25 µs; these do not establish at-ear timing. The internal ±20 ppm timebase corresponds to 1.2 ms/min or 72 ms/hour versus ideal time and clock-only ±0.2 Hz at 10 kHz. These accuracy specifications are valid for one year after external calibration. Aging and current calibration of the used board are unverified. No measured acoustic/neural jitter or ±dB appears in the slides.

If configured for the chassis reference rather than internal timing, the selected clock controls the calculation; the chassis ±25 ppm specification corresponds to 90 ms/hour versus ideal time. The PXIe-6363's independent timing specification is 50 ppm. Do not silently assign 4461's 20 ppm to every module or the recorder. Common-rack reference routing and neural synchronization need explicit configuration. A start trigger alone does not prevent rate mismatch. A shared reference suppresses independent oscillator drift, but trigger/filter offsets and small clock-synthesis rounding differences can remain; [NI synchronization guidance](https://www.ni.com/en/support/documentation/supplemental/10/synchronization-explained.html) describes these conditions. Verify the residual alignment.

The 4461 lead names hybrid 186900-11L; confirm the actual rear connector and calibration. ED1 bundle includes zBus/PS25F power and incidental HB7, so no separate ZB1PS is added. One SHC cable follows the diagram; a second bank, if used, needs another cable. Confirm ES1 matching high-voltage cable and any chassis cord. Seller tests are not our verification.

## 3. Recommended version

Proposed full-band chain: PC → USB-6361 screw terminals → SA1 in ZB1PS → MF2-M. Acoustic measurement: M50 → MM-1 → differential NI AI. Hardware markers are recorded with neural data after recorder input review. No program or hardware has been built or validated. Python + NI-DAQmx is a candidate without a paid LabVIEW assumption; host support and implementation remain open.

| Part | Qty | Unit USD | Line USD | Condition / source |
|---|---:|---:|---:|---|
| [NI USB-6361 screw terminal 781442-01](https://www.newark.com/ni-now-part-of-emerson/781442-01/multifunction-i-o-device-usb-6361/dp/14AJ5341) | 1 | $3,030.42 | $3,030.42 | New |
| [Pomona EM4970-36# BNC male to bare wires,36in](https://www.digikey.com/en/products/detail/pomona-electronics/EM4970-36/6125831) | 1 | $23.68 | $23.68 | New |
| [Earthworks M50](https://www.ebay.com/itm/375116964435) | 1 | $1,299.00 | $1,299.00 | New |
| [Sound Devices MM-1](https://www.bhphotovideo.com/c/product/292989-REG/Sound_Devices_MM_1_MM_1_Single_Channel_Portable.html) | 1 | $945.00 | $945.00 | New |
| [REED R8090](https://www.digikey.com/en/products/detail/reed-instruments/R8090/13164951) | 1 | $219.00 | $219.00 | New |
| [Hosa HMIC-010 XLR mic cable10ft](https://www.sweetwater.com/store/detail/HMIC010--hosa-hmic-010-pro-microphone-cable-rean-xlr3f-to-xlr3m-10-ft) | 1 | $17.99 | $17.99 | New |
| [Hosa PHX-106F-BULK XLRfemale adapter6in](https://www.bhphotovideo.com/c/product/488060-REG/Hosa_Technology_PHX_106F_BULK_PNX_106FB_Phoenix_Connector.html) | 1 | $13.95 | $13.95 | New |
| [Gator Rok-It RI-MICTP-FBM mic stand](https://www.sweetwater.com/store/detail/RIMICTPFBM--rok-it-tripod-microphone-stand-with-fixed-boom) | 1 | $34.99 | $34.99 | New |
| [Panasonic LR6XWA/2SB AA battery](https://www.digikey.com/en/products/detail/panasonic-energy/LR6XWA-2SB/2043739) | 2 | $0.62 | $1.24 | New |
| [NI 763830-01 US AC cord](https://www.newark.com/ni-now-part-of-emerson/763830-01/test-cable-assembly-power-cable/dp/13AJ3639) | 1 | $51.00 | $51.00 | New |
| [Yageo MFR-25FBF52-100K bias return resistor](https://www.digikey.com/en/products/detail/yageo/MFR-25FBF52-100K/13473) | 2 | $0.10 | $0.20 | New |
| [TDT MF2-M mono speaker kit](https://www.tdt.com/product/mf2-multi-field-magnetic-speakers/) | 1 | Quote required | Quote required | [TDT order/quote](https://www.tdt.com/contact-tdt/orders/) |
| [TDT SA1 amplifier](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/) | 1 | Quote required | Quote required | [TDT order/quote](https://www.tdt.com/contact-tdt/orders/) |
| [TDT ZB1PS powered chassis](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/) | 1 | Quote required | Quote required | [TDT order/quote](https://www.tdt.com/contact-tdt/orders/) |

The table and main PDF recommendation use the $945 new amplifier. The freshly listed [$604.50 B&H used MM-1](https://www.bhphotovideo.com/c/product/803529754-USE/sound_devices_mm_1_single_channel_portable_microphone.html) saves $340.50, reducing the proposal subtotal to $5,295.97. Moderate wear and a 90-day seller warranty are displayed. Stock is not reserved; the historical $325 offer is not a current buying recommendation. US cord is conservatively included separately; remove only if supplied or a compatible one is owned. NI includes the screw-terminal unit's USB cable and 12 V PSU. MF2 kit includes stand, speaker cable/adapter and calibration files; M50 includes clip and half-inch calibrator adapter; R8090 includes its 9 V battery. MM-1 uses the two AA batteries listed.

**Shared measurement kit:** M50 + MM-1 + R8090 + HMIC cable + stand + two AA cells = $2,176.72 used-preamp or $2,517.22 new-preamp. It is our addition for both source versions; neither paper nor slides identifies this exact kit. DAQ-specific microphone wiring is additional for those two versions. In the recommendation, remove the Phoenix housing from the PHX pigtail and verify XLR pin mapping, differential input, shield/bias returns and gain. Two 100 kΩ bias resistors are a proposal for the MM-1 floating transformer output, not validated wiring. Keep MM-1 high-pass filter and limiter off, gain fixed, and check clipping. NI AI is multiplexed; channel scan timing must be measured/accounted for.

**Precision:** [MF2](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/) free field 1–80 kHz, with THD ≤1% stated for 1–65 kHz under manufacturer conditions. [M50](https://earthworksaudio.com/measurement-microphones/m50/) reaches 50 kHz; [MM-1](https://support.sounddevices.com/hc/en-us/articles/45051602821275-MM-1-User-Guide-and-Technical-Information) is −1 dB at 50 kHz relative to 1 kHz and supplies the M50's 48 V / 10 mA phantom requirement. These nominal bandwidths include 1.4–32 kHz, but do not establish assembled-chain response or calibrated sound-level uncertainty. The MM-1 frequency response uses a 150-ohm test source; M50 output is specified at 600 ohms, so check the actual combined response. [R8090 ±0.5 dB](https://www.reedinstruments.com/pdfs/cache/www.reedinstruments.com/r8090/datasheet/r8090-datasheet.pdf) is a 1 kHz reference specification only. Factory curves do not replace calibration at the ear.

At a proposed actual 200 kSa/s, spacing is 5 µs. NI's default typical-at-25°C 50 ppm figure gives clock-only ±0.5 Hz at 10 kHz / ±1.6 Hz at 32 kHz and 180 ms/hour versus ideal time before correction. Neither is measured Rice accuracy. Actual sound-to-neural jitter, corrected residual drift and at-ear ±dB are unknown. Repeated recorded markers and microphone arrivals can estimate timeline mapping and acoustic delay; a compatible shared clock is another option. Proposed ≤1 ms residual sound-to-neural timestamp alignment is an untested acceptance goal. It measures a different quantity from SONIC's 56-millisecond neural-processing delay; neither value establishes that one setup is faster or more precise than the other. A TM2500C is optional only if the recorder/DAQ clock arrangement benefits from it; its $799.99 backordered price does not buy automatic synchronization.

## Basic setup price refresh

The same JBL305P MkII is freshly listed [new at Sweetwater for $99](https://www.sweetwater.com/store/detail/LSR305MK2--jbl-305p-mkii-5-inch-powered-studio-monitor), replacing the inaccessible $122.39 Reverb offer. Basic parts now total $346.79 with a borrowed calibrator, or $565.79 with the $219 calibrator. Estimated delivery/tax reserves bring working budgets to $426.79 and $665.79; recorder-interface costs remain extra. The sale may change. Battery replacement in the specialized options is [two Panasonic cells at $0.62 each](https://www.digikey.com/en/products/detail/panasonic-energy/LR6XWA-2SB/2043739), minimum two. Earlier documents remain historical snapshots.

## Decision for Dr. Luan and limits

First confirm the required frequency band, our recorder timing inputs, the existing lab inventory and a spending limit for supplier quotes. Use the basic page-1 setup when selected tones below 20 kHz answer the question. The full-band recommendation reduces rack complexity and adds explicit acoustic measurement; it has not demonstrated better neural alignment. Arduino/FPGA can provide prebuffered samples and markers, but needs a suitable DAC/analog output, amplifier, speaker, microphone calibration and physical alignment. Earlier audible DIY budgets remain in the [historical research record](Auditory_Hardware_Options_2026-10-09.md) and [decision inputs](sources/Sound_Decision_Prices_2026-10-09.json); they are not verified lower-cost full-SONIC-band substitutes.

SONIC used awake, alert sheep; Rice's sedated-sheep adaptation has unverified response windows and performance. No purchase, vendor contact, hardware connection, bench/animal experiment or executable animal protocol was performed.
