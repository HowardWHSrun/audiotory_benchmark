#!/bin/zsh
set -eu
cd -- "${0:A:h}"
if [[ -x .work/latency-venv/bin/python ]]; then
  exec .work/latency-venv/bin/python scripts/launch_bench_app.py "$@"
fi
if [[ -x .work/bench_app/venv/bin/python ]]; then
  exec .work/bench_app/venv/bin/python scripts/launch_bench_app.py "$@"
fi
exec python3 scripts/launch_bench_app.py "$@"
