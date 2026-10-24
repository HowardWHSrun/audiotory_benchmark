"""Prepare the private audio environment and open SONIC Bench on Mac/Windows."""
import os
from pathlib import Path
import subprocess
import sys
import venv

ROOT = Path(__file__).resolve().parents[1]


def main():
    if sys.version_info < (3, 10):
        raise RuntimeError("Install Python 3.10 or newer from python.org, then open this launcher again.")
    target = ROOT / ".work/bench_app/venv"
    python = target / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    # Reuse the project's already prepared environment when it has the native
    # audio dependencies. Import checks do not query devices or open streams.
    existing = ROOT / ".work/latency-venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    for candidate in (python, existing):
        if candidate.exists() and subprocess.run([str(candidate), "-c", "import numpy, sounddevice"],
                                                capture_output=True).returncode == 0:
            python = candidate
            break
    else:
        print("First launch: preparing local audio dependencies. This can take a few minutes.", flush=True)
        venv.create(target, with_pip=True)
        subprocess.run([str(python), "-m", "pip", "install", "-r", str(ROOT / "latency/requirements.txt")], check=True)
    subprocess.run([str(python), "-m", "bench_app", *sys.argv[1:]], cwd=ROOT, check=True)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, OSError, subprocess.CalledProcessError) as error:
        print(f"SONIC Bench could not start: {error}", file=sys.stderr)
        input("Press Enter to close…")
        sys.exit(1)
