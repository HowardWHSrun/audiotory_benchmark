# Project tools

For the local Audient / MK3 speaker player:

```sh
python3 scripts/start_sound_player.py --configure
```

Open <http://127.0.0.1:8765/>. `--configure` selects the connected Audient as macOS application playback output at 96 kHz; it does not change gain or microphone input and does not start sound. Omit it to preserve the current device settings. Read-only output check: `python3 scripts/sound_output.py`. See [playback instructions](../playback/README.md).

Run from the project root:

```sh
node --test tests/*.test.cjs playback/waveform.test.mjs
python3 scripts/validate_site.py
python3 scripts/build_site.py
python3 scripts/validate_site.py --root .work/site
```

The static build is written to ignored `.work/site/`, including downloadable outputs and legacy document URLs. Local `Papers/` and temporary working files are excluded.

The active guide is edited in [LaTeX](../output/pdf/2026-10-16/M50_Sound_Setup_Guide/main.tex). `archive/build_m50_word_guide.py` is the historical Word builder; it writes only into the Word archive and does not overwrite the active LaTeX manifest.
