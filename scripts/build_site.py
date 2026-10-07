"""Build a small, portable Pages bundle from the tracked project materials."""

from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "_site"


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for directory in ("web", "sources"):
        shutil.copytree(ROOT / directory, OUT / directory)
    if (ROOT / "docs").exists():
        shutil.copytree(ROOT / "docs", OUT / "docs")
    for path in ROOT.glob("*.md"):
        shutil.copy2(path, OUT / path.name)
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
    print(f"Built {count} files in _site/")


if __name__ == "__main__":
    build()
