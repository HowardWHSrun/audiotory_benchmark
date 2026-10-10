# Item-purpose verification

The two-page faculty parts list now uses **Item | Description | Count | Source | Cost**. All 42 individual part rows and both added-kit rows have a brief description. This revision checks component roles; it does not refresh prices, establish assembled-system performance or change the existing cost scope.

## Paper and slide attribution

- The unchanged [pinned SONIC v1](SONIC_2025_bioRxiv_v1.pdf), Methods 6.1–6.2, page 11, names USB-6361 assembly 152805A-03L, SA1, free-field MF1 and TM2500C. It describes precomputed waveform output, analog/reference input recording, and satellite/network/10-megahertz timing. It does not identify the proposed microphone kit, the exact accessory ordering numbers or ZB1PS enclosure. These remain reproduction additions. The clock reference alone does not synchronize an arbitrary recorder.
- The McGinley [diagram](hardware_slides_2026-10-09/01_system_diagram.png) and [parts slide](hardware_slides_2026-10-09/02_equipment_links.png) show the two computer/chassis connection cards and their cable, the signal board connected to the BNC panel, and the audio module connected to ED1 and ES1. The added microphone kit is our proposal. Neuropixels and SONIC's Connexus recorder remain excluded because Howard has his own recorder.
- Basic and Compact are proposed alternatives. The descriptions do not imply that either has been assembled, calibrated or measured.

## McGinley connections

| Parts | Verified purpose | Primary documentation |
|---|---|---|
| PXIe-1082 | Holds and powers instrument boards | [Chassis manual](https://docs-be.ni.com/bundle/pxie-1082-seri/raw/resource/enus/372752c.pdf) |
| PXIe-6363 | Acquires signals and provides hardware timing/pulses; exact lab channel assignments are not specified in the slides | [Board specifications](https://www.ni.com/docs/en-US/bundle/pxie-6363-specs/page/specs.html) |
| PXI-4461, hybrid 186900-11L | Generates the waveform sent to ED1; also has audio inputs | [Specifications](https://docs-be.ni.com/bundle/ni-4461-4462-specs/raw/resource/enus/373770k.pdf), [hybrid-board certification](https://www.ni.com/en/support/documentation/product-certifications/model.pxi-4461.html) |
| PCIe-8361, PXIe-8360, 779500-03 | Host card, chassis module and connecting cable carry computer communication | [NI connection diagram and ordering guide](https://sine.ni.com/pdf/products/us/cat_pxie836x.pdf) |
| SHC68-68-EPM and BNC-2090A | Connect the signal board to accessible signal sockets | [Cable](https://www.ni.com/en/shop/hardware/cables/model-shc68-68-epm), [panel manual](https://docs-be.ni.com/bundle/bnc-2090a-feature/raw/resource/enus/372101a.pdf) |
| ED1, enclosure and power bundle | Drives the electrostatic speaker; the selected seller bundle includes enclosure/power | [ED1 manual](https://www.tdt.com/docs/hardware/ed1-electrostatic-speaker-driver/), [existing bundle listing](https://www.ebay.com/itm/156873696386) |
| ES1 and matching cable | Produces sound in the specified 4–110 kilohertz range; matching cable carries drive and bias voltages | [ES1 manual](https://www.tdt.com/docs/hardware/ec1-es1-electrostatic-speaker/) |
| Hosa BNC-58-103 | Carries the audio-module output to ED1; carries USB-6361 output to SA1 in SONIC | [Existing cable listing](https://www.proaudiosolutions.com/Hosa-BNC-58-103-p/bnc-58-103.htm) |

ES1's lower limit does not cover the paper's 1.4–4 kilohertz tones. Computer communication cards and cables do not independently establish sound-to-neural synchronization. The used hybrid board's identity, operation and calibration remain unverified physically.

## SONIC and Compact connections

| Parts | Verified purpose | Primary documentation |
|---|---|---|
| USB-6361, BNC and screw-terminal variants | Converts waveforms to voltage and records input signals | [USB-6361 specifications](https://download.ni.com/support/manuals/374650c.pdf), pinned paper above |
| TM2500C | Satellite-referenced time server with network timing and 10-megahertz output | [Manufacturer brochure](https://timemachinescorp.com/wp-content/uploads/TM2500-Brochure.pdf) |
| MF1-M / MF2-M | Magnetic speakers producing sound from SA1 output; specified free-field bands cover the paper's tones | [MF1](https://www.tdt.com/docs/hardware/mf1-multi-field-magnetic-speakers/), [MF2](https://www.tdt.com/docs/hardware/mf2-multi-field-magnetic-speakers/) |
| SA1 / ZB1PS | Speaker amplifier and its powered enclosure | [SA1](https://www.tdt.com/docs/hardware/sa1-stereo-amplifier/), [ZB1PS](https://www.tdt.com/docs/hardware/zb1ps-powered-zbus-device-chassis/) |
| 781513-01, 780534-01, 763830-01 | USB-6361 external power supply, locking computer cable and wall power cord | [NI X Series manual](https://docs-be.ni.com/bundle/pcie-pxie-usb-63xx-features/raw/resource/enus/370784k.pdf), exact supplier links retained in the parts list |
| 781233-02 | Clip-on ferrite on the **power cable**, reducing radiated electrical emissions; not an acoustic filter | NI X Series manual, installation section 1-6 |
| Pomona EM4970-36# | Screw-terminal waveform output to SA1's BNC input | [Exact connector listing](https://www.digikey.com/en/products/detail/pomona-electronics/EM4970-36/6125831), NI/SA1 connection specifications above |
| Hosa PHX-106F-BULK | Proposed modified lead from MM-1 line output to the recording input; Phoenix connector must be removed/replaced and wiring checked | [Connector listing](https://www.bhphotovideo.com/c/product/488060-REG/Hosa_Technology_PHX_106F_BULK_PNX_106FB_Phoenix_Connector.html), [MM-1 manual](https://support.sounddevices.com/hc/en-us/articles/45051602821275-MM-1-User-Guide-and-Technical-Information) |
| Two 100,000-ohm resistors | Proposed ground-reference return paths for the floating microphone-amplifier output | NI X Series floating-source input guidance and MM-1 output specification; proposed connection, not validated hardware |

The short PDF marks custom microphone-input wiring and proposed resistors in their descriptions. Source-version microphone/recorder adapters remain outside the existing budget scope, as documented in the [detailed comparison](../Accurate_Setup_Comparison_2026-10-09.md). No new cost or timing claim is made.

## Basic and measurement parts

| Parts | Verified purpose | Primary documentation |
|---|---|---|
| UMC204HD | Computer sound playback, microphone/line recording and microphone power | [Behringer](https://www.behringer.com/en/products/0805-AAS) |
| JBL 305P MkII | Powered audible speaker with balanced line input | [JBL specifications](https://jblpro.com/fr/site_elements/305p-mkii-sell-sheet) |
| Dayton EMM-6 | Sound measurement; specified 18 hertz–20 kilohertz band and 15–48-volt microphone power | [Dayton product/manual](https://www.daytonaudio.com/product/911/emm-6-electret-measurement-microphone) |
| Hosa HMIC-010 | Microphone to UMC204HD in Basic; microphone to MM-1 in the shared kit | [Hosa catalog](https://hosatech.com/wp-content/uploads/2021/02/Hosa-Product-Catalog-201209.pdf), input documentation above |
| Two Hosa HSS-005 cables | Proposed speaker output and separate electrical reference-loopback connections; software/channel assignment still needs implementation | [Exact connector listing](https://www.sweetwater.com/store/detail/HSS005--hosa-hss-005-pro-balanced-interconnect-rean-1-4-in-trs-to-same-5-foot), UMC204HD/JBL input-output specifications above |
| Earthworks M50 | Sound measurement extending to 50 kilohertz | [Earthworks](https://earthworksaudio.com/measurement-microphones/m50/) |
| Sound Devices MM-1 | Powers the M50 and amplifies its signal; two AA cells power the MM-1 | [MM-1 manual](https://support.sounddevices.com/hc/en-us/articles/45051602821275-MM-1-User-Guide-and-Technical-Information) |
| REED R8090 | Provides a known acoustic level at one kilohertz for checking microphone sensitivity; not full-band calibration | [REED datasheet](https://www.reedinstruments.com/pdfs/cache/www.reedinstruments.com/r8090/datasheet/r8090-datasheet.pdf) |
| Gator RI-MICTP-FBM | Positions the microphone | [Existing stand listing](https://www.sweetwater.com/store/detail/RIMICTPFBM--rok-it-tripod-microphone-stand-with-fixed-boom) |
| Panasonic LR6XWA/2SB cells | Battery power for MM-1 | [Exact cell listing](https://www.digikey.com/en/products/detail/panasonic-energy/LR6XWA-2SB/2043739), MM-1 manual above |

All quantities, buying destinations, source conditions, observed prices, marked estimates and parts totals are preserved. Buying links and past seller-condition observations are not a new stock or price verification. Physical performance and recorder compatibility remain unmeasured.
