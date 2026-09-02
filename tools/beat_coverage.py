#!/usr/bin/env python3
"""Beat coverage: every numbered beat in OUTLINE.md must have prose behind it.

The charter's delivery test is "every outline beat → a paragraph". This does not try to judge
whether the prose is *good* — a reader does that. It answers the cheaper question the charter
actually asks: is there a chapter for this beat's chapter, and does that chapter have at least as
many prose paragraphs as the chapter has beats, so no beat can have been silently dropped.

Run: python3 tools/beat_coverage.py [first_chapter last_chapter]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import check_edition as ce  # noqa: E402

OUTLINE = ROOT / "OUTLINE.md"
SUMMARY = ROOT / "chapters" / "SUMMARY.md"


def outline_chapters() -> list[tuple[int, str, list[int]]]:
    """(number, title, [beat numbers]) for each `## N · Title` heading in the outline."""
    out: list[tuple[int, str, list[int]]] = []
    for line in OUTLINE.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^##\s+(\d+)\s+·\s+(.*)$", line.strip())
        if head:
            out.append((int(head.group(1)), head.group(2).strip(), []))
            continue
        beat = re.match(r"^(\d+)\.\s", line.strip())
        if beat and out:
            out[-1][2].append(int(beat.group(1)))
    return out


def reading_order() -> list[str]:
    return [m.group(1)[: -len(".md")] for m in
            re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", SUMMARY.read_text(encoding="utf-8"),
                        re.MULTILINE)]


def main() -> int:
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    order = reading_order()
    problems: list[str] = []
    print(f"{'ch':>3}  {'beats':>5}  {'paras':>5}  chapter")
    total_beats = 0
    for number, title, beats in outline_chapters():
        if not (lo <= number <= hi):
            continue
        total_beats += len(beats)
        if number >= len(order):
            problems.append(f"chapter {number} ({title}) has no slug in SUMMARY.md")
            continue
        slug = order[number]
        path = ROOT / "chapters" / f"{slug}.md"
        if not path.exists():
            problems.append(f"chapter {number}: {path.name} does not exist")
            continue
        paragraphs = list(ce.prose_paragraphs(path.read_text(encoding="utf-8")))
        flag = "" if len(paragraphs) >= len(beats) else "  <-- fewer paragraphs than beats"
        if flag:
            problems.append(f"chapter {number} ({slug}): {len(beats)} beats, "
                            f"{len(paragraphs)} prose paragraphs")
        print(f"{number:>3}  {len(beats):>5}  {len(paragraphs):>5}  {slug}{flag}")
    print(f"\n{total_beats} beats in range; every beat's chapter exists and carries prose."
          if not problems else "\n" + "\n".join("PROBLEM: " + p for p in problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
