# Research log

## 2026-10-09 America/Chicago - slide hardware and economical sound alternatives

- Howard supplied two NI/TDT hardware slides and requested a parts list, eBay prices, and lowest versus upper budgets, including whether a computer/speaker/microphone route is possible.
- Preserved the slides and added the [hardware comparison](Auditory_Hardware_Options_2026-10-09.md), [editable parts budget](outputs/01a11dcd-7193-7620-9381-3678488ff8ee/Sound_Setup_Budget_2026-10-09.xlsx) and [dated price inputs](sources/Sound_Hardware_Prices_2026-10-09.json). Kept the lab's own probes outside new purchases; the exact recorder and stimulus range remain open.
- Found a $264.90 three-part audible basket. The conditional minimum including accessories/reserve is $424.90; practical audible scenarios total $1,114.90–1,596.87. USB higher-frequency scenarios total $11,004.90–20,251.98; full slide-rack scenarios total $15,800.49–29,469.33. Prices/estimates, borrowed equipment and band limitations are explicit; these are not guaranteed supplier bounds.
- Identified ES1's 4 kHz lower limit and external electrostatic-drive/power requirement, uncertain PXI-4461 hybrid-slot compatibility, the slide source's bandwidth limit, microphone omissions and the opportunity to remove the rack with a USB DAQ. Audible components do not reproduce the full SONIC frequency alphabet.
- [Verification record](Verification_2026-10-09_Hardware_Budget.md) covers arithmetic, an input-change recalculation test, workbook visual checks, manufacturer/source review, existing model/static checks and unchanged manuscript bytes. No hardware or animal validation is claimed.


## 2026-10-02 UTC - project starter

- Located the existing research home at `/Users/howardwang/Desktop/Rice Research` through read-only folder inspection. Its descriptive project folders and Markdown navigation were used as the convention for this new project.
- Established `SONIC Auditory Benchmarking` as a separate project. Existing research files and repositories are outside the change scope.
- Recorded Lan's supplied message, joint auditory assignment, visual adaptation assignment and rodent feasibility assignment separately from proposed work.
- Interpreted October 15/29 Thursday afternoons in Houston as tentative discussion windows from the October 1 message; nothing was scheduled.
- Pinned the paper to bioRxiv v1 (`2025.09.30.679683v1`). Manuscript method verification is pending parent research findings.
- Used the author organization's public overview for the preliminary study explanation; no exact stimulus parameters were inferred.
- Ordinary direct bioRxiv PDF retrieval returned HTTP 429; web fetches also failed. No PDF or failed download was included as a valid paper copy.
- Created requirements, inventory and bench-validation planning documents. All lab availability remains unknown, and all bench checks remain proposed.
- Writing-style retrieval was unavailable in this conversation. Documents use plain research-note prose and the local project's navigation convention without claiming a personal style match.
- No contacts, bookings, orders, experiments, surgical protocol, packages, implementation code or changes to existing repositories were made for this starter.

## 2026-10-02 UTC - verified manuscript update

- Received the parent researcher's full v1 findings and checked the source manuscript, including printed pp.5-14 and the methods on pp.11-12.
- Successfully materialized the supplied private Library paper into `sources/SONIC_2025_bioRxiv_v1.pdf`; confirmed 18 readable pages, title, DOI/version and methods. Preserved Library identity and version attributes. Recorded checksum and provenance in the source register.
- Added a public bioRxiv metadata snapshot and reusable BibTeX citation. The API lists v1 date 2025-10-02 and no linked published article at retrieval.
- Updated paper notes with session-level results, exact sheep auditory settings, electrical synchronization, preprocessing, decoder evaluation and information-rate definition.
- Kept 56/11 ms intrinsic delay separate from physiology, computation and delivery-to-output timing. Recorded the narrower single-session scope of the 11 ms analysis and offline status of the main analysis.
- Logged the exploratory-duration grouping discrepancy and missing frequency-array/ramp/calibration details rather than selecting a guessed protocol.
- Updated proposed Rice requirements and the project plan. No animal-ready stimulus files, code, testing or experimental protocol were generated.

## 2026-10-07 America/Chicago - shared repository and visual design

- Howard requested that project work be kept in `HowardWHSrun/audiotory_benchmark` on GitHub from now on, and requested a visual design showing how the experiment is performed.
- Inspected the repository: it was empty and public. Initialized this existing project folder as its local checkout, preserving the source PDF and existing research records.
- Recorded the additional supplied team-message context in `sources/Team_Clarifications_2026-10-07.md`. Follow-up dates were not supplied; October 7 is the receipt date, not an inferred date for the messages, discussion, or surgery.
- Updated the primary target to sedated sheep, with paper-derived sound delivery, calibration, and recording/event timing. Sound isolation and a behavioral rig are not required by Lan. Visual and rodent feasibility work remain secondary.
- Preserved the awake/alert state of the published SONIC sheep as a paper fact. No sedated-sheep response, timing window, or information rate is established by that study.
- Created an educational browser walkthrough with illustrative activity, adjustable timing, a proposed sheep setup, and the published session results. The walkthrough does not produce audible stimuli, connect to hardware, or claim measured Rice data.
- Added repository working instructions, scientific model checks, local link/source validation, and a static GitHub Pages publishing workflow. Verification and publication evidence are recorded in `Verification_2026-10-07.md` when complete.
- No external messages, calendar bookings, orders, animal experiments, or bench tests were performed. The image filename in the supplied conversation was not accompanied by an image; no claim about its contents is made.

## 2026-10-07 America/Chicago - setup-first website revision

- Howard requested a cleaner website with our planned experiment as the main section and the paper explanation confined to one separate section.
- Reorganized the site around Our experiment and Paper reference. The main page presents the planned sedated-sheep sound, calibration, recording, and timing paths; published settings and results remain in Paper reference.
- Retained unknown local equipment choices and the distinction between awake source animals and the planned sedated preparation. No hardware or neural-performance assumption was added.
- Legacy `#experiment` links now lead to our experiment setup; the paper material remains separately accessible. Updated the repository overview and preview to match this focus.

## 2026-10-07 America/Chicago - minimal website revision

- Howard asked to reduce the amount of information further. The homepage now centers on a short goal and the setup diagram, with component details shown only when selected.
- Removed the always-visible workflow and decision summaries from the website; the detailed planning documents remain in the repository. Paper methods, illustration, and results are collapsed by default.
- Kept the planned-sedated-sheep status, unknown equipment, microphone acoustic checks, and paper/Rice distinction accessible without repeating long explanations on the homepage.

## 2026-10-08 America/Chicago - mouse stimulus setup proposal

- Howard requested initial thinking about adapting the sound setup to mice while reviewing SONIC methods. Retained sedated sheep as the confirmed primary Rice target and kept mouse state, strain/age, and recorder open.
- Howard confirmed in response to a setup question that awake versus anesthetized/sedated mouse state is still undecided. The proposal keeps sound-chain bench work independent of that later choice.
- Rechecked complete SONIC v1 methods pages 11-13 in the unchanged local manuscript, including tone generation, synchronization, evaluation, and awake/alert source animals.
- Added a mouse proposal with a functional sound/measurement/timing diagram, comparison with the paper, mouse-specific design questions, and staged bench, response, sequence, and decoding work.
- Registered primary mouse studies and official hardware/calibration sources. Kept numerical paper settings, illustrative bandwidth examples, and proposed local choices distinct.
- Verification passed: six existing scientific-model checks, validation of 84 references and the unchanged SONIC v1 PDF checksum, and whitespace/diff checks. Scientific and hardware review identified a useful recorder-artifact bench check, now included in the proposal.
- No hardware connection, sound playback, calibration measurement, animal experiment, external message, order, or website change was performed.

## 2026-10-08 America/Chicago - simple LaTeX experiment draft

- Howard requested a very simple LaTeX file and PDF describing the proposed mouse experiment after checking SONIC's methods. Created an editable standalone source and a one-page PDF under `output/pdf/`.
- Rechecked SONIC v1 Sections 6.1-6.2 in the unchanged source manuscript. The five-control table labels sheep reference values separately from open mouse choices. MF1/SA1 remain candidate equipment; acoustic onset checks and the separated-tone progression are proposed Rice additions.
- Included sound delivery, clock-aligned hardware markers and microphone timing, three starting steps, and a short list of open decisions. Mouse state, equipment, behavior, and enclosure choices remain open.
- The desktop LaTeX compiler confirmed success. Exported the PDF from the same source with the official Tectonic 0.17.0 compiler, downloaded into a temporary folder and verified against the release asset's SHA256 digest.
- Checked the final PDF visually and programmatically: one page, all sections present, three correct embedded source-link targets, and no overfull content. Repository validation passed for 86 references and the unchanged SONIC checksum; all six existing model checks passed. Kept compiler logs, downloads, and preview images outside the repository.
- No equipment purchase, hardware connection, bench/animal experiment, external message, or website content change was performed.

## 2026-10-08 America/Chicago - plain language PDF revision

- Howard asked for a simpler document written more naturally. Replaced the control table and detailed checklist with three short sections using direct "we" wording. Kept speaker choice provisional, mouse state open, and sheep reference values separate from mouse choices.
- Recompiled the same LaTeX source and replaced the one-page PDF. Increased the body text to 12 pt and added more space. Desktop compilation and PDF export succeeded; visual review and content checks confirmed a readable page with no overflow.

## 2026-10-08 America/Chicago - bullet point PDF revision

- Howard requested more bullet points. Converted the three setup sections and starting steps to 15 short, single-level bullets, preserving the simple wording and open mouse choices.
- Desktop LaTeX compilation and PDF export succeeded. Checked the updated page visually and confirmed all bullets fit on one page without overflow. Temporary font/download resources and preview images remain outside the repository.

## 2026-10-08 America/Chicago - SONIC choices beside the setup bullets

- Howard requested references showing what SONIC chose to do. Added concise published choices beside the sound, equipment, and synchronization bullets, with six method-section/printed-page citations and a linked paper reference.
- Included the explored frequency range, benchmark tone duration/fades, random balanced blocks without inter-tone silence, precomputed playback, NI/SA1/MF1 sound chain, reported sheep level, and electrical synchronization. Kept mouse settings open and labeled microphone arrival checks and optional video alignment as local additions.
- Rechecked against SONIC v1 methods. Desktop compilation and PDF export succeeded; visual/content checks confirmed one readable page, the expected references, and no overflow. The original manuscript remains unchanged.

## 2026-10-08 America/Chicago - remove the starting steps

- Howard approved the remaining draft and asked to remove "Start here." Deleted only that heading and its three bullets, then regenerated the PDF. Desktop compilation and visual review passed; the other content and SONIC references are unchanged.

## 2026-10-08 America/Chicago - mouse equipment extension from scratch

- Howard confirmed the short plan with a labmate and asked us to extend it assuming the lab needs to assemble the setup. Recorded the relevant equipment and provenance from Xiaorong's forward of Tinghan's BCM list, without private contact addresses, RSVP links, or tracking parameters.
- Checked official TDT, Avisoft, Peerless/Tymphany, Scan-Speak, and B&K specifications. Distinguished ES1 free-field delivery from EC1 coupling; ED1 from the waveform DAC; and 116Hm acquisition from the 4939 microphone cartridge. Recorded driver power, microphone conditioning, calibration, and timing dependencies.
- Added one equipment page to the simple PDF and updated two speaker bullets to reflect the from-scratch assumption. Preserved SONIC references, undecided mouse state/settings, and the removal of "Start here." Kept detailed compatibility notes in the repository equipment plan.
- Verification passed: desktop LaTeX compilation, export of the same source, visual review of both pages, five correct PDF source-link targets, no overfull content, repository validation of 129 references and the unchanged SONIC checksum, and diff checks. A separate content review checked the paper/BCM/Rice distinction and clarified the ES1 range wording. Temporary compiler/render files remain outside the repository.
- No equipment access, purchase, hardware connection, acoustic measurement, animal procedure, external message, or website content change was performed.

## 2026-10-08 America/Chicago - expanded equipment list and pricing

- Howard requested a more extensive equipment list with prices. Researched new-item public listings and manufacturer list prices for sound delivery, acoustic measurement/calibration, timing connections, neural recording comparisons, computer/storage, optional video, software, and setup support.
- Added a dated pricing record with exact SKUs, unit/package basis, original currency, links, bundled contents, stock limits, and quote/model-open labels. Excluded used listings and avoided counting alternatives or bundled accessories twice.
- Included partial subtotals rather than an unsupported complete budget. TDT and most B&K items require quotes; the Rice neural system, implant, mouse preparation, and final frequency band remain open.
- Kept the two-page outline and added four pricing pages. Desktop LaTeX compilation and PDF export succeeded; visual review covered all six pages with no overflow. Programmatic checks confirmed the four pricing sections, six correct subtotals, 38 HTTPS PDF links, and continued removal of "Start here." Repository validation passed for 182 references and the unchanged SONIC checksum; diff checks passed. Independent acoustic and supporting-equipment reviews found no material corrections. Temporary renders and compiler files remain outside the repository.
- No vendor contact, quote request, purchase, hardware connection, or experiment was performed.

## 2026-10-08 America/Chicago - clarify complete equipment choices

- Howard found the component list confusing and asked whether we need one, several, or all the sound-measurement items. Reorganized the reading PDF into explicit complete setups and added a selection guide before the detailed price catalog.
- Measurement choices are alternatives: complete 116Hm kit; filtered 40026 package with compatible NI acquisition; or a specialist B&K set with matched conditioning/acquisition. Identified included microphone/preamp/recorder/cables/stand/software, duplicate parts to omit, and one shared NI device counted once.
- Grouped sound delivery into complete ES1/ED1/power, MF1/SA1/power, and conventional-tweeter/amplifier choices. Kept AD3 optional and calibration as a separate band-appropriate choice, with the 40 kHz reference optional.
- Preserved individual prices in the detailed repository catalog; no hardware purchase or completed compatibility result is implied.
- Verification passed: desktop LaTeX compilation, PDF export, visual review of all six pages, seven subtotal checks, 32 HTTPS PDF links, no overfull or underfull content, repository validation of 183 references and the unchanged SONIC checksum, and diff checks. Temporary renders remain outside the repository; the website is unchanged.

## 2026-10-08 America/Chicago - one simple shopping budget with estimates

- Howard said the grouped alternatives were still too complicated and requested an estimate for every quote-only item. Reduced the reading PDF from six pages to two: the existing experiment outline and one proposed shopping list with quantities, purpose, and budget.
- The proposed budget uses one MF2-M/SA1/ZB1PS sound chain, one NI output unit, one complete 116Hm kit, and an Intan neural-recording comparison. SONIC's actual MF1 choice remains identified; current MF2 kit/SA1 support was checked in TDT's documentation. The equipment subtotal is $32,545.42 (about $33,000); conditional basic animal support and a general reserve bring the working budget to $41,545.42 (about $42,000). Optional video is outside that figure.
- Added numerical planning allowances for all 11 previously quote-only rows and the new MF2 candidate, plus model-open support functions. Clearly labeled these as our low-confidence reserves rather than vendor prices, with broad scenarios and provenance in the detailed catalog. Preserved public/list prices and bundled-content rules; alternatives remain only in the detailed notes.
- Retained undecided mouse state/tone range, the 2 kHz microphone boundary, separate band-calibration work, unknown recorder/interface choices, and the distinction from Rice's sedated-sheep project. The animal allowance excludes full surgery/anesthesia infrastructure, housing, services, and ongoing costs; software/integration labor is outside the equipment subtotal.
- Verification passed: desktop LaTeX compilation, two-page export, visual review of both pages, eight correct HTTPS PDF links, no overfull/underfull layout warnings, checks that all prior quote-only rows contain estimates, and equipment/reserve/video arithmetic. Independent review found no material issues or duplicate bundle charges. Repository validation passed for 195 references and the unchanged SONIC v1 manuscript; diff checks passed. Temporary renders remain outside the repository.
- No vendor contact, quote request, purchase, animal/bench procedure, or website edit was performed.

## 2026-10-08 America/Chicago - sound budget using the lab's probes

- Howard corrected the scope: we will use the lab's own probes, and this work mainly concerns the sound setup. Removed the Intan comparison, new probe/adapter allowance, and animal-support purchases from the current PDF and shopping catalog. Their earlier figures remain only in historical commits/log entries.
- Revised the sound-equipment subtotal to $19,940.42 (about $20,000). A $2,500 reserve gives $22,440.42 (about $22,500). Computer/storage is a conditional $2,000 allowance that can be removed if a suitable lab setup is reused. Optional camera remains outside the core sound budget. All acoustic quote-only estimates are retained.
- Updated the plan, proposal, inventory, and README. Planned use of lab probes is confirmed; exact probe/headstage/recorder models, accessory availability, timing-input compatibility, and physical validation remain unverified. Sound markers still need connecting to the lab recording timeline.
- Verification passed: desktop LaTeX compilation, two-page export, visual review of both pages, seven HTTPS PDF links, no overfull/underfull content, checks for removal of neural purchases and retention of acoustic estimates, sound/reserve/reuse arithmetic, 190-reference repository validation, unchanged SONIC v1 manuscript, and diff checks. Independent scope review found no material issues. Website content is unchanged; temporary renders stay outside the repository.
- No vendor contact, purchase, physical connection, or experiment was performed.

## 2026-10-08 America/Chicago - equipment rationale and intended sheep reuse

- Howard requested an appendix explaining the speaker/amplifier/power choices, listing SONIC's actual hardware, and designing the mouse sound setup for later sheep reuse. Added one appendix page; the reading PDF is now three pages and keeps the simple shopping list and existing sound budget.
- Rechecked the saved primary manuscript, Methods 6.2 (p.11) and 6.6 (p.13), plus current official TDT/Avisoft documentation. The appendix distinguishes SONIC's MF1/SA1/NI/TM2500C from our proposed MF2-M, ZB1PS, and Avisoft kit. The exact paper power unit and measurement microphone are unreported; the GPS server is a paper reference, not a new purchase.
- Explained MF2's stated broad band, documented SA1 compatibility, and its zBus power dependency. Intended sheep reuse requires new placement/calibration at the sheep-ear position and fresh timing checks. The 2 kHz microphone limit does not cover SONIC's 1.4 kHz tones; lower-frequency needs must be resolved before purchasing that kit. Hardware reuse does not establish the same physiology or response windows in sedated Rice sheep versus SONIC's awake sheep.
- Updated the supporting plan, proposal, pricing record, and README. Lab probes remain in use; neural/animal purchases remain outside the sound budget. No cross-species performance or equipment compatibility measurement is claimed.
- Verification passed: desktop LaTeX compilation, three-page export, visual review of all pages, 13 HTTPS link annotations to eight correct destinations, appendix attribution/transfer content checks, unchanged budget arithmetic, no overfull/underfull content, independent paper/hardware reviews, 202-reference repository validation, unchanged SONIC v1 source PDF, and diff checks. Temporary renders are outside the repository; the website is unchanged.
- No vendor contact, purchase, hardware connection, or experiment was performed.

## 2026-10-08 America/Chicago - more natural and intuitive sound plan

- Howard asked for wording that feels more human and a plan that is easier to follow. Rewrote the three-page PDF around a simple sound-path diagram and three steps: choose the tones, check what reaches the ear, and match the sound to the brain recording.
- Put each equipment role before its model name, shortened the explanations, and kept the SONIC comparison and sheep adaptations in the appendix. Equipment choices and budget are unchanged. Retained the lab-probe scope, estimate labels, electrical-versus-acoustic timing distinction, microphone's 2 kHz boundary, undecided mouse state, and sedated-sheep versus awake-SONIC distinction.
- Verification passed: desktop LaTeX compilation, export from the same source, visual review of all three pages, content/scope and budget checks, 12 HTTPS link annotations to eight correct destinations, and no overfull/underfull layout warnings. Independent readability review found no material issues. Repository validation passed for 202 references and the unchanged SONIC v1 manuscript; diff checks passed. Temporary renders remain outside the repository.
- No new research, vendor contact, purchase, hardware connection, experiment, or website edit was performed.

## 2026-10-08 America/Chicago - SONIC comparisons in Our sound setup

- Howard requested the published SONIC choices beside the writing in "Our sound setup" so the two setups can be compared while reading. Added four paired "Our plan" and "SONIC" bullets for equipment, tone selection, sound at the ear, and recording alignment, with method-section/page references and a paper link.
- Rechecked complete Methods 6.1-6.2 (p.11) and 6.6 (p.13) in the unchanged manuscript. Preserved the explored-versus-benchmark tone distinction and silence between blocks. Kept SONIC's electrical waveform/trial-marker acquisition and shared clock separate from our proposed microphone acoustic-arrival checks. The paper does not name its measurement microphone or specify direct marker input into its neural recorder.
- Verification passed: native LaTeX compilation, three-page export, visual review of all pages, four comparison-pair and scientific-scope checks, 13 HTTPS annotations to eight destinations, no overfull/underfull warnings, and independent primary-source review. Budget and appendix page text are unchanged. Repository reference/checksum validation and diff checks passed; temporary renders remain outside the repository.
- No vendor contact, purchase, hardware connection, experiment, or website edit was performed.

## 2026-10-09 America/Chicago - complete hardware comparison in PDF and LaTeX

- Howard requested everything from the slide-hardware comparison in PDF and editable LaTeX. Added a standalone seven-page document with the minimum/practical audible baskets, USB and full-rack budgets, all slide parts, eBay/source links, timing/calibration requirements and frequency/compatibility limits.
- Retained the lab neural-chain scope, asking-price versus estimate distinction, conditional minimum, approximately $30,000 upper planning scenario, SONIC band mismatch and awake-versus-sedated-sheep boundary. The PDF links the original slides, full research record, price inputs and editable spreadsheet.
- Verification passed: desktop LaTeX compilation, export of the same source with Tectonic 0.17.0, visual review of all seven pages, expected part/budget/scope content checks, 64 HTTPS annotations to 50 destinations, no overfull/underfull warnings, and independent coverage review. Repository source/link validation, unchanged SONIC manuscript checksum and diff checks passed. Temporary compiler resources and renders are outside the repository; website source is unchanged.
- No vendor contact, purchase, hardware connection or experiment was performed.

## Next evidence update

Complete the Rice inventory, confirm the sheep recording interface and geometry, and resolve the paper's waveform/calibration questions. Assess sedation as a documented adaptation. Agree on a discussion time from actual availability rather than the undated relative dates in the supplied messages. Keep completed project changes synchronized to GitHub.
