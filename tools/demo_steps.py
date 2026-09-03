#!/usr/bin/env python3
"""Generate `demos/steps.json` — the demos' step scaffolding — from the contract, not by hand.

FIREWALL: this writes the scaffolding for pages that compute a toy DEC lattice. Nothing here is a
claim about nature. See ../FIREWALL.md.

**No beat number is ever typed into a demo.** The preface being drafted will insert beats at the
front of `OUTLINE.md` and shift every number in the book again, and it has happened twice already:
tranche C added a chapter and moved every beat from 36 on, tranche D moved every beat from 36 on by
three more. Each time, anything holding a beat number in its own source went stale silently.

So the demos hold **no** numbers. A demo step declares which of its chapter's `##` sections it
covers, by that section's **anchor** — a string a renumber cannot touch — and this script reads the
beat number off the `<!-- beat N -->` marker in the chapter, and the beat's question off
`OUTLINE.md`. The pages then render titles and beat labels from what it writes. A renumber changes
`OUTLINE.md` and the chapters, this file's output follows, and no demo source is edited at all.

Run it:

    python3 tools/demo_steps.py            # rewrite demos/steps.json
    python3 tools/demo_steps.py --check    # fail if the committed file is not what this derives

`check_edition.py` runs the second form, so a stale `demos/steps.json` is a red check rather than a
page showing last week's numbering.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"
CHAPTERS = ROOT / "chapters"
STEPS_JSON = ROOT / "demos" / "steps.json"

# The chapters the demos cover, in the book's order, by slug. Listed rather than discovered: a demo
# page appearing or disappearing is a decision, and it should be made here and reviewed, not
# inferred from what happens to be on disk.
DEMO_CHAPTERS = (
    "two-dots-and-a-line",
    "one-tetrahedron-is-a-whole-world",
    "make-it-move",
    "the-shape-between",
    "two-worlds-threaded",
)

BEAT_MARKER = re.compile(r"<!--\s*beat\s+(\d+)\s*-->")
HEADING = re.compile(r"^##\s+(.+?)\s*$")
OUTLINE_BEAT = re.compile(r"^(\d+)\.\s+(.+?)\s*$")


def strip_emphasis(text: str) -> str:
    """Markdown emphasis out of a line that is about to become a page's heading text.

    The outline writes *change* and *not* for a reader of the outline. A demo's title is rendered as
    text, so the asterisks would be printed. Nothing else is touched — the words are the outline's.
    """
    return re.sub(r"[*_]", "", text)


def anchor_for(heading: str) -> str:
    """The anchor mdBook gives a heading: lowercase, punctuation dropped, spaces hyphenated.

    Used only as a **key** — the demos do not deep-link into a chapter's sections, so a divergence
    from mdBook's slugifier in some exotic heading could not break a reader's link. What it must be
    is stable under a renumber, and a heading's words are exactly that.
    """
    slug = strip_emphasis(heading).lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def outline_beats() -> Dict[int, str]:
    """Every beat's question, by number, with the drafters' bracketed note cut off.

    The parenthetical italics in the outline say what the reader is supposed to *see*, and the whole
    point of this pass is that a demo shows it rather than telling her. So the answer is dropped
    here, at the boundary, where it cannot be reintroduced by an editing hand.
    """
    text = OUTLINE.read_text(encoding="utf-8")
    beats: Dict[int, str] = {}
    for line in text.splitlines():
        found = OUTLINE_BEAT.match(line)
        if not found:
            continue
        number = int(found.group(1))
        question = found.group(2)
        question = re.split(r"\s*\*\(", question)[0]
        question = re.sub(r"\s*\[[^\]]*\]\s*$", "", question)
        beats[number] = strip_emphasis(question).strip()
    if not beats:
        raise SystemExit("demo steps: OUTLINE.md has no numbered beats — has its format changed?")
    return beats


def chapter_title(markdown: str, slug: str) -> str:
    for line in markdown.splitlines():
        if line.startswith("# "):
            return strip_emphasis(line[2:].strip())
    raise SystemExit(f"demo steps: chapters/{slug}.md has no `# ` title")


def chapter_sections(slug: str) -> List[dict]:
    """The chapter's `##` sections that carry a beat marker, in the order they appear.

    A marker is paired with the nearest heading above it. A marker with no heading above it is the
    chapter's opening prose answering a beat — `tools/beat_coverage.py` reads that as a declared
    excusal — and there is nothing on a demo page for it to key against, so it is refused here by
    name rather than silently skipped.
    """
    path = CHAPTERS / f"{slug}.md"
    if not path.exists():
        raise SystemExit(f"demo steps: chapters/{slug}.md is missing")
    lines = path.read_text(encoding="utf-8").splitlines()
    sections: List[dict] = []
    heading = None
    for number, line in enumerate(lines, start=1):
        found_heading = HEADING.match(line)
        if found_heading:
            heading = found_heading.group(1)
            continue
        found_beat = BEAT_MARKER.search(line)
        if not found_beat:
            continue
        if heading is None:
            raise SystemExit(
                f"demo steps: chapters/{slug}.md:{number} carries a beat marker with no `## ` "
                f"heading above it. The demos key their steps on a section anchor, so a beat "
                f"answered by a chapter's opening prose has nothing for a step to hold on to."
            )
        sections.append({
            "anchor": anchor_for(heading),
            "heading": strip_emphasis(heading),
            "beat": int(found_beat.group(1)),
        })
        heading = None
    if not sections:
        raise SystemExit(f"demo steps: chapters/{slug}.md carries no beat markers")
    return sections


def derive() -> dict:
    beats = outline_beats()
    chapters = {}
    for slug in DEMO_CHAPTERS:
        markdown = (CHAPTERS / f"{slug}.md").read_text(encoding="utf-8")
        sections = chapter_sections(slug)
        for section in sections:
            number = section["beat"]
            if number not in beats:
                raise SystemExit(
                    f"demo steps: chapters/{slug}.md claims beat {number}, which OUTLINE.md does "
                    f"not have. One of the two was renumbered without the other."
                )
            section["question"] = beats[number]
        numbers = [section["beat"] for section in sections]
        if numbers != sorted(numbers):
            raise SystemExit(
                f"demo steps: chapters/{slug}.md's beats are out of order: {numbers}"
            )
        if len(set(numbers)) != len(numbers):
            raise SystemExit(f"demo steps: chapters/{slug}.md claims a beat twice: {numbers}")
        chapters[slug] = {
            "title": chapter_title(markdown, slug),
            "first": numbers[0],
            "last": numbers[-1],
            "sections": sections,
        }
    return {
        "note": (
            "Generated by tools/demo_steps.py from OUTLINE.md and the chapters' beat markers. "
            "Do not edit: a renumber regenerates it, and check_edition.py fails if the committed "
            "file is not what the contract now derives."
        ),
        "chapters": chapters,
    }


def text() -> str:
    return json.dumps(derive(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main(argv: List[str]) -> int:
    derived = text()
    if "--check" in argv:
        if not STEPS_JSON.exists():
            print("demo steps: demos/steps.json is missing — run tools/demo_steps.py", file=sys.stderr)
            return 1
        committed = STEPS_JSON.read_text(encoding="utf-8")
        if committed != derived:
            print(
                "demo steps: demos/steps.json is not what OUTLINE.md and the chapters now derive — "
                "run `python3 tools/demo_steps.py` and commit it",
                file=sys.stderr,
            )
            return 1
        print(f"demo steps: demos/steps.json is in step ({len(committed)} bytes)")
        return 0
    STEPS_JSON.write_text(derived, encoding="utf-8")
    total = sum(len(chapter["sections"]) for chapter in derive()["chapters"].values())
    print(f"demo steps: wrote demos/steps.json — {len(DEMO_CHAPTERS)} chapters, {total} sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
