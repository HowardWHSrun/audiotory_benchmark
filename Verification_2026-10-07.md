# Experiment website verification - October 7, 2026

This record concerns the educational application and project documentation. It is not evidence of an acoustic bench test, hardware operation, or animal experiment.

## Checks performed

- Six numerical model tests passed: published fixtures and reported rounding; uniform-input ceiling units; duration changes without changing measured scores; approximate 56/11 ms intrinsic delays; invalid input handling; and browser/CommonJS compatibility.
- Browser script syntax checks passed.
- A headless Chrome check loaded both views without script errors: Our experiment and Paper reference.
- Verified the homepage and legacy `#experiment` route open Our experiment; `#paper` and legacy `#results` open Paper reference. The skip link focuses main content while preserving the current view.
- Selected all seven equipment components and checked the corresponding role, open choices, and selected state. The homepage contains no paper performance scores or transplanted hardware settings.
- Verified keyboard operation of the duration control and checked alphabet selection, 50/5 ms observation selection, step, play, and pause within the paper illustration.
- Confirmed the paper illustration starts collapsed. Playback pauses when it closes or when leaving Paper reference.
- Confirmed illustrative input changes leave the published achieved ITR values unchanged.
- Confirmed eight session bars and the exact-value table match the manuscript's Table 1.
- Checked Our experiment and Paper reference at 320, 390, 768, and 1440 pixel viewport widths, including the paper illustration both collapsed and expanded: twelve layout cases, with no page-level horizontal overflow.
- Reviewed desktop and mobile captures for text, controls, diagram, and results layout. The long timeline can be scrolled horizontally on narrow screens.
- Confirmed the application runs directly from `web/index.html` with the file protocol, without a server or external network dependencies.
- Confirmed the saved paper is reachable from the served application. Static validation checks its SHA256 remains `3c8de5dc6bad53a043f7b6181603cf5af223979c92cfc5eb486f1fa7842a0731`.
- Checked local application/source/document references and built a static Pages bundle.

## Scientific review

The synthetic sequence and neural raster are labeled as illustrations. The unknown exact 37-frequency array is not reconstructed as a verified paper stimulus. The Sheep E example uses the published 14-frequency list.

Long neural responses and overlapping observation windows are distinct. At the default 50 ms window and 10 ms tone spacing, adjacent windows share 40 ms; 5 ms windows at 10 ms spacing are separate. Neither diagram predicts achieved neural performance.

The 56/11 ms intrinsic delay definitions exclude physiology and computation. The 11 ms result is identified as a reduced, optimized window sweep from Sheep E, Session 2. Published results remain tied to awake sheep and appear only in Paper reference. The homepage explains Rice's planned sedated-sheep setup; local hardware, calibration, response windows, and measured ITR remain unknown. Microphone measurements of acoustic arrival and event-marker clock alignment are shown as distinct checks.

## Publication checks

The GitHub workflow reruns the model, syntax, source, and link checks before publishing. Its execution and deployed version are available in the repository's Actions and Pages deployment records. The live walkthrough is https://howardwhsrun.github.io/audiotory_benchmark/web/.

The temporary browser captures and local site bundle are excluded from Git. A representative screenshot is retained in `docs/images/walkthrough.png` for the repository README.
