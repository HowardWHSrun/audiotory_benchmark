#!/bin/zsh
set -eu
cd -- "${0:A:h}"
if [[ ! -x .work/latency-venv/bin/python ]]; then
  print -u2 'The local audio environment is missing. Follow latency/README.md to prepare it.'
  exit 1
fi
exec .work/latency-venv/bin/python -m latency.sonic_check "$@"
