#!/usr/bin/env python3
"""Beat coverage and grain, counted from the prose rather than from the outline.

The first version of this counted beats out of `OUTLINE.md` and compared the total against a
chapter's paragraph count. That has a blind spot a reader found twice: counting from the contract
cannot tell a split beat from a missing one (K59), and it cannot tell that a chapter's sections have
been reordered away from the contract at all (K74). It reported 43/43 through both defects.

So it now reads the `<!-- beat N -->` marker under each `##` heading and checks the prose against the
outline in both directions:

  * every beat in range has at least one section claiming it, and none is claimed that does not exist
  * the sections' beat numbers run in the outline's own order, so a reorder is reported, not silent
  * a beat carried by more than one section is named as a split rather than passed over

It also prints the grain, because the word counts had been argued over with two counters two or three
words apart (K75). There is one counter now and it is the edition checker's own, so the number here
and the number `check_edition.py` would get are the same number.

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
BAND, CEILING = (100, 200), 220
MARKER = re.compile(r"^<!--\s*beat\s+(\d+)\s*-->\s*$", re.M)


def outline_chapters() -> list[tuple[int, str, list[int]]]:
    out: list[tuple[int, str, list[int]]] = []
    for line in OUTLINE.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^##\s+(\d+)\s+·\s+(.*)$", line.strip())
        if head:
            out.append((int(head.group(1)), head.group(2).strip(), []))
        elif (beat := re.match(r"^(\d+)\.\s", line.strip())) and out:
            out[-1][2].append(int(beat.group(1)))
    return out


def reading_order() -> list[str]:
    text = SUMMARY.read_text(encoding="utf-8")
    return [m.group(1)[:-3] for m in re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", text, re.M)]


def sections(markdown: str) -> list[tuple[str, int | None, int]]:
    """(heading, claimed beat or None, prose words) for each `##` section."""
    out = []
    for part in re.split(r"^## ", markdown, flags=re.M)[1:]:
        lines = part.splitlines()
        body = "\n".join(lines[1:])
        claimed = MARKER.search(body)
        out.append((lines[0].strip(),
                    int(claimed.group(1)) if claimed else None,
                    len(ce.words(ce.cleaned_prose(body)))))
    return out


def main() -> int:
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    order, problems, grain, n_beats = reading_order(), [], [], 0

    for number, title, beats in outline_chapters():
        if not (lo <= number <= hi):
            continue
        n_beats += len(beats)
        if number >= len(order):
            problems.append(f"chapter {number} ({title}) has no slug in chapters/SUMMARY.md")
            continue
        slug = order[number]
        path = ROOT / "chapters" / f"{slug}.md"
        if not path.exists():
            problems.append(f"chapter {number}: {path.name} does not exist")
            continue

        secs = sections(path.read_text(encoding="utf-8"))
        claimed = [b for _, b, _ in secs if b is not None]
        unmarked = [h for h, b, _ in secs if b is None]
        # the chapter's opening prose carries the chapter's first beat, before any heading
        expected = beats[1:] if len(beats) == len(secs) + 1 else beats

        missing = [b for b in expected if b not in claimed]
        stray = sorted({b for b in claimed if b not in beats})
        splits = sorted({b for b in claimed if claimed.count(b) > 1})
        reordered = claimed != sorted(claimed)

        for h, b, n in secs:
            if n > CEILING or not (BAND[0] <= n <= BAND[1]):
                grain.append((n, slug, h, b))

        note = []
        if unmarked:
            problems.append(f"chapter {number} ({slug}): {len(unmarked)} section(s) carry no "
                            f"`<!-- beat N -->` marker: {unmarked}")
        if missing:
            problems.append(f"chapter {number} ({slug}): no section claims beat(s) {missing}")
        if stray:
            problems.append(f"chapter {number} ({slug}): section claims beat(s) {stray}, "
                            f"which are not this chapter's")
        if reordered:
            problems.append(f"chapter {number} ({slug}): sections claim beats {claimed}, "
                            f"which is not the outline's order")
        if splits:
            note.append(f"split: {splits}")
        print(f"{number:>3}  {len(beats):>2} beats  {len(secs):>2} sections  {slug}"
              + (f"   ({'; '.join(note)})" if note else ""))

    over = [g for g in grain if g[0] > CEILING]
    print(f"\ngrain — band {BAND[0]}-{BAND[1]} words, hard ceiling {CEILING}")
    if not grain:
        print("  every section inside the band")
    for n, slug, h, b in sorted(grain, reverse=True):
        mark = "  OVER THE CEILING" if n > CEILING else ""
        print(f"  {n:>4}  beat {b}  {slug} §{h}{mark}")
    if over:
        problems.append(f"{len(over)} section(s) over the {CEILING}-word hard ceiling")

    if problems:
        print("\n" + "\n".join("PROBLEM: " + p for p in problems))
        return 1
    print(f"\n{n_beats} beats in range; every one claimed by a section, in the outline's order.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
