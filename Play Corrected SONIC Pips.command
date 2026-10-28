#!/bin/zsh
set -eu
cd -- "${0:A:h}"

if [[ ! -x .work/latency-venv/bin/python ]]; then
  print -u2 'The local audio environment is missing. Follow latency/README.md to prepare it.'
  exit 1
fi

profile_dir='.work/latency/runs/20261028-162448-897345-isolated-corrected-pips'
for profile_file in manifest.json analysis.json output_float32.npy; do
  if [[ ! -r "$profile_dir/$profile_file" ]]; then
    print -u2 "The measured local correction profile is missing: $profile_dir/$profile_file"
    print -u2 'Restore the original local run or repeat the pip calibration. No sound was played.'
    exit 1
  fi
done

print 'Experimental 7-second corrected SONIC reconstruction plus silence; records the microphone.'
print 'The profile is specific to the measured speaker, microphone position (about 10 cm), orientation and gain settings.'
print 'It is not a calibrated animal stimulus protocol. Keep input monitoring off.'
exec .work/latency-venv/bin/python -m latency.sonic_check --preview --peak-dbfs -36 --pip-correction-from "$profile_dir"
