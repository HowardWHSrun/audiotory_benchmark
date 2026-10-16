# Project tools

Run from the project root:

```sh
node --test tests/*.test.cjs
python3 scripts/validate_site.py
python3 scripts/build_site.py
python3 scripts/validate_site.py --root .work/site
```

The static build is written to ignored `.work/site/`, including downloadable outputs and legacy document URLs. Local `Papers/` and temporary working files are excluded.

The active guide is edited in [LaTeX](../output/pdf/2026-10-16/M50_Sound_Setup_Guide/main.tex). `archive/build_m50_word_guide.py` is the historical Word builder; it writes only into the Word archive and does not overwrite the active LaTeX manifest.
