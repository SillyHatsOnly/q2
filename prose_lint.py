#!/usr/bin/env python3
"""Quick Russian prose hygiene check for index.html body text.

Counts common mechanical markers and editor-asides. Not a style judge —
use before/after a rewrite pass to see if the numbers moved the right way.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HTML = ROOT / "index.html"

# Phrases that often signal "editor talking about the textbook"
ASIDES = [
    r"здесь «[^»]+» — про",
    r"не про тон учебника",
    r"этот учебник",
    r"не этот учебник",
    r"второй сезон",
    r"не «купите весь магазин»",
]

# Overused mechanical / bureaucratic tokens (case-insensitive where useful)
TOKENS = [
    (r"\bданный\b", "данный"),
    (r"\bявляется\b", "является"),
    (r"осуществл\w+", "осуществлять*"),
    (r"в современном мире", "в современном мире"),
    (r"играет ключевую роль", "играет ключевую роль"),
    (r"на сегодняшний день", "на сегодняшний день"),
    (r"подводя итог", "подводя итог"),
    (r"широкий спектр", "широкий спектр"),
    (r"слева направо", "слева направо"),
    (r"сверху вниз", "сверху вниз"),
]


def body_text(html: str) -> str:
    """Strip script/style and tags; keep readable text roughly."""
    html = re.sub(r"(?is)<script[^>]*>.*?</script>", " ", html)
    html = re.sub(r"(?is)<style[^>]*>.*?</style>", " ", html)
    html = re.sub(r"(?s)<!--.*?-->", " ", html)
    html = re.sub(r"<[^>]+>", " ", html)
    html = re.sub(r"&nbsp;|&#160;", " ", html)
    html = re.sub(r"&[a-z]+;|&#\d+;", " ", html, flags=re.I)
    return re.sub(r"\s+", " ", html).strip()


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HTML
    text = body_text(path.read_text(encoding="utf-8"))
    words = len(text.split())
    print(f"file: {path}")
    print(f"words≈ {words}")
    print()

    print("asides / meta-voice:")
    for pat in ASIDES:
        n = len(re.findall(pat, text, flags=re.I))
        if n:
            print(f"  {n:4d}  {pat}")
    if not any(re.search(p, text, flags=re.I) for p in ASIDES):
        print("  (none of the listed patterns)")

    print()
    print("token hits:")
    hits = Counter()
    for pat, label in TOKENS:
        hits[label] = len(re.findall(pat, text, flags=re.I))
    for label, n in hits.most_common():
        if n:
            print(f"  {n:4d}  {label}")
    if not any(hits.values()):
        print("  (clean)")

    # Rough "можно дальше" / checkpoint density — good when present, not noise
    cp = len(re.findall(r"Можно дальше, если", text))
    print()
    print(f"checkpoints: {cp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
