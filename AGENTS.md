# Project working instructions

## Shared repository

Howard asked on October 7, 2026 for this project's work to be kept on GitHub from now on. The canonical repository is https://github.com/HowardWHSrun/audiotory_benchmark.

- Keep research notes, source provenance, designs, application code, and useful verification records in this project and repository.
- For each completed, verified change, commit and push the authorized project changes to the existing repository. Check the remote state first; preserve others' work and never force-push.
- The visual walkthrough is in `web/`. GitHub Pages publishes checked changes from `main`; verify deployment when changing the walkthrough.
- The homepage should explain **our planned experiment setup**. Keep the SONIC explanation, published results, and illustrative paper controls together in a separate **Paper reference** section.
- The default page is Our experiment. Legacy `#experiment` links should also open our setup, so existing browser tabs do not keep showing the paper walkthrough as the homepage.
- Keep the website sparse: a short goal and setup diagram on the homepage, component explanations shown on selection, and paper details collapsed by default. Detailed planning records belong in the repository documents.
- Keep temporary renders, browser captures, dependency folders, credentials, and local build output out of commits. Do not treat synthetic displays as experimental data.
- Do not change neighboring research projects for this work.

## Scientific scope and evidence

- The primary Rice target is measuring auditory cortical responses in **sedated sheep**, per Lan's clarification supplied by Howard on October 7, 2026. Exact message dates were not supplied.
- SONIC bioRxiv v1 recorded **awake, alert sheep**. Keep sedation as an explicit Rice adaptation; its effects on responses, appropriate windows, and achieved ITR are unverified.
- Lan does not require a soundproof box, behavioral rig, or sound isolation for the planned sheep or rodent measurements. Still document background sound, acoustic calibration, geometry, and timing.
- Preserve the distinction between published paper findings, confirmed team direction, proposed Rice choices, and unknown equipment or experimental results.
- The paper's 56/11 ms intrinsic delays exclude auditory physiology and computation; the 11 ms result is a narrower one-session window sweep.
- The browser walkthrough is an educational simulation and planning aid, not hardware control, measured Rice performance, or an animal-ready stimulus protocol.
- The saved PDF stays unchanged, with its source/version, checksum, attribution, and CC BY-NC-ND 4.0 notice.

## Verification

- Run the applicable model checks and static site validation before publishing changes. Check desktop and narrow layouts and the interactions affected by changes.
- Do not generate fake measured results. Controls may change illustrative timing or theoretical input ceilings; published achieved ITR values stay tied to their original conditions.
- Do not send external messages, schedule meetings, order parts, or perform animal/bench experiments unless the user authorizes those actions. The relative meeting and surgery dates in the supplied messages remain unconfirmed.
