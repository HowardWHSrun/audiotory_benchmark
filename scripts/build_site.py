"""Build a small, portable Pages bundle from the tracked project materials."""

from pathlib import Path
import json
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / ".work/site"


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    ignored = shutil.ignore_patterns(".DS_Store", "__pycache__", "*.pyc", "*.aux", "*.log", "*.out", "*.synctex.gz")
    for directory in ("web", "sources", "docs", "output", "scripts", "tests", "playback"):
        shutil.copytree(ROOT / directory, OUT / directory, ignore=ignored)
    for path in ROOT.glob("*.md"):
        shutil.copy2(path, OUT / path.name)
    # Keep old published document URLs working without cluttering the workspace.
    manifest = json.loads((ROOT / "docs/organization/2026-10-16_path_moves.json").read_text())
    aliases = 0
    for move in manifest["moves"]:
        for old in (move["from"], move.get("observed_user_source")):
            if not old or Path(old).suffix == ".py":
                continue
            source, destination = OUT / move["to"], OUT / old
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.suffix == ".md":
                link = os.path.relpath(source, destination.parent)
                destination.write_text(f"# Document moved\n\n[Open the document]({link})\n")
            else:
                shutil.copy2(source, destination)
            aliases += 1
    (OUT / ".nojekyll").touch()
    (OUT / "index.html").write_text(
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<meta http-equiv="refresh" content="0;url=web/">'
        '<title>SONIC Auditory Benchmarking</title></head>'
        '<body><a href="web/">Open the SONIC visual walkthrough</a></body></html>\n',
        encoding="utf-8",
    )
    count = sum(path.is_file() for path in OUT.rglob("*"))
    print(f"Built {count} files in .work/site/ with {aliases} legacy document URLs.")


if __name__ == "__main__":
    build()
