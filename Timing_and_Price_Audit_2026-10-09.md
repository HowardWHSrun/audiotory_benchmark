# Timing and price audit - October 9, 2026

Howard correctly identified the paper's reported **56-millisecond delay**. The earlier reading PDF's sentence, “the paper gives no measured timing error,” was too broad and omitted this result. The corrected PDF separates neural-processing delay from sound-to-neural recording alignment and accumulating clock mismatch.

## What the paper actually reports

Primary source: the unchanged [saved SONIC version 1 paper](sources/SONIC_2025_bioRxiv_v1.pdf), [original DOI](https://doi.org/10.1101/2025.09.30.679683). Page numbers below are PDF pages, starting at the title page.

| Figure | Meaning and evidence | What it does not establish |
|---|---|---|
| **56 milliseconds** | Main benchmark's reported intrinsic delay. Page 7: neural measurement below one, filtering five, feature binning five, decoder context 45 milliseconds. Pages 4-5 define the terms. | It is not ±56 milliseconds of synchronization error. Sensory physiology and computer calculation time are excluded. |
| **11 milliseconds** | Separate single-session window analysis, Figure 5, page 8. Methods page 12 limits it to the first 40% of Sheep E, Session 2, with a changed decoder and a single five-millisecond bin. | It is not the main multi-session result or demonstrated Rice performance. |
| **Below 100 milliseconds** | Page 9 reports separate online evaluation of the neural interface plus computation, depending on hardware/software. | It is not a quantified tone-onset-to-decoded-output delay including sensory physiology. |
| **Remaining sound-to-neural timestamp error** | Methods page 11 describes recorded analog output, trial-start edges and the time reference. | The paper does not quantify residual acoustic alignment error, trial-to-trial timing variation or long-session drift. |

- The components listed for 56 milliseconds add to **less than 56**, because neural measurement is less than one. Retain the paper's reported 56; do not turn the rounded/reporting convention into an exact equality.
- “Sensory physiology” is the time from sound to the neural response. It is separate from collecting and decoding neural data.
- “Timing error” is uncertainty assigning an event to the recording timeline. A known fixed delay can be corrected without being an equally large uncertainty.
- “Drift” is a growing clock mismatch over time. One simultaneous start signal does not establish equal running speeds.
- The shopping list reproduces the **sound chain** and excludes the paper's Connexus neural recorder. Buying those sound parts cannot establish 56-millisecond processing delay for our own recorder and analysis.
- Our proposed corrected alignment goal of one millisecond describes timestamp matching. It cannot be ranked directly against the paper's 56-millisecond processing delay.
- Paper methods pages 11 and 13 confirm precomputed nominal 192,000-sample-per-second waveforms, USB-6361 to SA1 to MF1, and awake, alert sheep. Rice's sedated-sheep response and decoding performance remain unverified.

## Hardware corrections and limits

- **USB-6361:** the [manufacturer specifications](https://download.ni.com/support/manuals/374650c.pdf) give 50 parts per million under default typical conditions at 25 degrees Celsius. Multiplying by one hour gives 180 milliseconds versus ideal time. This is a specification-scale calculation, not a guaranteed maximum or measured mismatch versus our recorder. Removed “up to” from the current evidence record.
- **PXI-4461:** the [manufacturer specifications](https://docs-be.ni.com/bundle/ni-4461-4462-specs/raw/resource/enus/373770k.pdf), pages 1 and 24, make accuracy conditional on calibration. The internal 20-parts-per-million figure corresponds to 72 milliseconds per hour versus ideal time; used-board calibration and aging remain unknown. The configured clock determines which figure applies.
- **Output filter and bandwidth:** the same board's 32-sample output-filter delay is 0.15625 milliseconds at 204,800 samples per second. Its flat output through 92.1 kilohertz is also conditional on that rate. Neither establishes sound-to-neural alignment.
- **Common reference:** [National Instruments synchronization guidance](https://www.ni.com/en/support/documentation/supplemental/10/synchronization-explained.html) describes trigger skew, filter offsets and small rate-rounding effects. Replaced the claim that sharing a reference removes all clock drift with conditional language about suppressing independent oscillator drift and measuring residual alignment.
- **Time reference:** [TimeMachines' brochure](https://timemachinescorp.com/wp-content/uploads/TM2500-Brochure.pdf) gives network synchronization precision below one microsecond plus network variation. That is a reference-device specification, not demonstrated sound-arrival accuracy. Its physical reference must be connected and configured for the chosen hardware.
- **Speaker range:** ES1 is specified from four kilohertz, so it misses the paper's lowest tones. MF1's raw ±13-decibel response is sourced specifically to the [2019 speaker guide](https://www.tdt.com/wp-content/uploads/2019/04/SpeakerGuide.pdf). Raw response variation is not calibrated accuracy.
- **Measurement chain:** M50 and MM-1 nominal bandwidths do not establish their assembled response at 32 kilohertz. MM-1 response uses a 150-ohm test source; M50's balanced output is specified at 600 ohms. Check the combined chain. The calibrator's ±0.5-decibel specification applies to its one-kilohertz reference, not all tones.

## Purchasing audit

Main prices, quantities and basket arithmetic were independently checked against current retrievable manufacturer, distributor and marketplace pages. Reopening a listing does not reserve stock; cached pages and seller claims do not prove function or calibration. No checkout, vendor contact or purchase occurred.

- Replaced the inaccessible $122.39 Reverb speaker with the same-model [new single JBL 305P MkII for $99 at Sweetwater](https://www.sweetwater.com/store/detail/LSR305MK2--jbl-305p-mkii-5-inch-powered-studio-monitor). It is a limited-time sale.
- Replaced the unrecoverable $0.59 battery offer with [two Panasonic cells at $0.62 each from DigiKey](https://www.digikey.com/en/products/detail/panasonic-energy/LR6XWA-2SB/2043739), minimum two.
- The earlier $325 used/no-returns MM-1 could not be retrieved. Keep it only as conditional savings; this does not establish that it is sold out. Main baskets now use the retrievable $945 new amplifier.
- The earlier $3,498.95 eBay sound-device lead is cached and remains unconfirmed. It is excluded from the main basket.
- Other main priced parts were reopened without a price change. Quote-only speaker/amplifier items, recorder-specific connections, shipping, tax, added tariffs and labor remain outside accurate-version subtotals.

| Current basket | Known-priced subtotal | Limit |
|---|---:|---|
| Basic, borrowed calibrator | $346.79 | $426.79 with estimated shipping/tax reserve |
| Basic, purchased calibrator | $565.79 | $665.79 with estimated shipping/tax reserve |
| SONIC sound parts only | $4,840.36 | Speaker/amplifier quotes and measurement extra |
| SONIC with proposed new-amplifier measurement kit | $7,357.58 | Still incomplete |
| Supplied-slide sound parts only | $7,551.75 | Speaker quote and measurement extra |
| Supplied-slide parts with proposed new-amplifier measurement kit | $10,068.97 | Still incomplete |
| Recommendation with new microphone amplifier | $5,636.47 | Speaker/amplifier/enclosure quotes and recorder interface extra |
| Recommendation with earlier used amplifier | $5,016.47 | Conditional availability; still incomplete |

Exact item records and buying links are in the [current price provenance](sources/Accurate_Setup_Prices_2026-10-09.json) and [itemized comparison](Accurate_Setup_Comparison_2026-10-09.md). Older budget files and earlier research-log entries are historical snapshots, not the current shopping basket. No complete upper budget or achieved Rice precision is established.
