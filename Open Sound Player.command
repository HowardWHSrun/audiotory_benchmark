#!/bin/zsh
cd "$(dirname "$0")" || exit 1
exec /usr/bin/python3 scripts/start_sound_player.py --configure --open
