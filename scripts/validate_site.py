"""Check local links and preserve the pinned scientific source before publishing."""

from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "sources/SONIC_2025_bioRxiv_v1.pdf"
PAPER_SHA256 = "3c8de5dc6bad53a043f7b6181603cf5af223979c92cfc5eb486f1fa7842a0731"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        for key in ("href", "src"):
            if attrs.get(key):
                self.refs.append(attrs[key])


def validate():
    errors = []
    if not PAPER.exists() or sha256(PAPER.read_bytes()).hexdigest() != PAPER_SHA256:
        errors.append("Pinned SONIC v1 PDF is missing or its bytes changed.")
    required = ["web/index.html", "web/styles.css", "web/app.js", "web/model.js"]
    for name in required:
        if not (ROOT / name).is_file():
            errors.append(f"Missing application file: {name}")

    refs = []
    for path in (ROOT / "web").glob("*.html"):
        parser = Links()
        parser.feed(path.read_text(encoding="utf-8"))
        refs.extend((path, ref) for ref in parser.refs)
        for ref in parser.refs:
            if ref.startswith("#") and ref[1:] not in parser.ids:
                errors.append(f"Missing HTML anchor in {path.name}: {ref}")

    markdown = list(ROOT.glob("*.md")) + list((ROOT / "sources").glob("*.md"))
    for path in markdown:
        for ref in re.findall(r"\]\(([^\s)]+)\)", path.read_text(encoding="utf-8")):
            refs.append((path, ref))

    for path, ref in refs:
        parts = urlsplit(ref)
        if parts.scheme or parts.netloc or not parts.path:
            continue
        if parts.path.startswith("/"):
            errors.append(f"Nonportable absolute link in {path.name}: {ref}")
            continue
        target = (path.parent / unquote(parts.path)).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"Broken local link in {path.relative_to(ROOT)}: {ref}")

    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(refs)} local/external references and unchanged SONIC v1 PDF.")
    return 0


if __name__ == "__main__":
    sys.exit(validate())
