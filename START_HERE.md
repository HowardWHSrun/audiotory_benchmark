# Start here

## Current sound setup

- [Basic speaker playback and microphone recording](latency/README.md#basic-speaker-playback-and-microphone-recording): verified together on October 23; repeat with `.work/latency-venv/bin/python -m latency.music_check`.
- [Concise playback-to-microphone delay report](output/pdf/2026-10-23/Audient_Delay_Report/main.pdf) · [LaTeX source](output/pdf/2026-10-23/Audient_Delay_Report/main.tex): approximately **38.3 ms** in two native 96 kHz runs (40 sweeps); includes playback/recording buffering and the acoustic chain. Repeat with [Measure Sound Delay.command](Measure%20Sound%20Delay.command).
- [SONIC tone reconstruction and timing methods](latency/README.md): play the 84-second reconstructed E14 block with [Play SONIC Tones.command](Play%20SONIC%20Tones.command), or review the separate electrical-reference method.
- [Audient / MK3 sound player](playback/README.md): run `python3 scripts/start_sound_player.py --configure`, then open <http://127.0.0.1:8765/>. Playback starts only when you click a button.
- [Read Final Part List V1](output/pdf/2026-10-16/M50_Sound_Setup_Guide/Final%20Part%20List%20V1.pdf)
- [Edit the LaTeX source](output/pdf/2026-10-16/M50_Sound_Setup_Guide/main.tex)
- [Review the sound-chain qualification audit](sources/Sound_Chain_Qualification_Audit_2026-10-16.json)

The PDF and LaTeX are together in `output/pdf/2026-10-16/M50_Sound_Setup_Guide/`.

## Understand the paper

- [SONIC study guide](output/pdf/SONIC_Professor_Meeting_Review_Notes.pdf)
- [Detailed paper notes](docs/paper/Paper_Notes.md)
- [Original SONIC paper](sources/SONIC_2025_bioRxiv_v1.pdf)

## Find other files

[Plans and notes](docs/README.md) · [Other PDFs and spreadsheets](output/README.md) · [Website](https://howardwhsrun.github.io/audiotory_benchmark/web/)

Earlier proposals are in `docs/history/`. The superseded Word guide is in `output/archive/`. Your local `Papers/` folder is unchanged.
