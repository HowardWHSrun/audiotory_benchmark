# Research log

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

## Next evidence update

Complete the Rice inventory, confirm the sheep recording interface and geometry, and resolve the paper's waveform/calibration questions. Assess sedation as a documented adaptation. Agree on a discussion time from actual availability rather than the undated relative dates in the supplied messages. Keep completed project changes synchronized to GitHub.
