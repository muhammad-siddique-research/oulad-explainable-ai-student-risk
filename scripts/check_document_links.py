"""Fail when a Markdown link points to a missing local repository artifact."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def broken_links() -> list[str]:
    missing = []
    for source in sorted(ROOT.rglob("*.md")):
        if ".git" in source.parts:
            continue
        for raw in LINK.findall(source.read_text(encoding="utf-8")):
            destination = raw.split("#", 1)[0].strip().split(" ", 1)[0]
            if not destination or destination.startswith(
                ("https://", "http://", "mailto:", "data:")
            ):
                continue
            target = (source.parent / destination).resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():
                missing.append(f"{source.relative_to(ROOT)} -> {destination}")
    return missing


if __name__ == "__main__":
    issues = broken_links()
    if issues:
        raise SystemExit("Invalid relative links:\n" + "\n".join(issues))
    print("Verified: all local Markdown links resolve.")
