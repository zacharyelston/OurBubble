#!/usr/bin/env python3
"""Generate `demos/steps.json` — the demos' step scaffolding — from the contract, not by hand.

FIREWALL: this writes the scaffolding for pages that compute a toy DEC lattice. Nothing here is a
claim about nature. See ../FIREWALL.md.

**No beat number is ever typed into a demo, and there is no book-wide one left to type.** Beats used
to be numbered across the whole book, so inserting one moved every later number; it happened three
times in two weeks, and each time anything holding a number in its own source went stale silently. A
beat's id is now `<chapter-slug>.<n>`, counted from 1 inside its own chapter (issue #77), and an
insertion moves only that chapter's later beats.

So the demos hold **no** numbers. A demo step declares which of its chapter's `##` sections it
covers, by that section's **anchor** — a string a renumber cannot touch — and this script reads the
beat's id off the `<!-- beat slug.n -->` marker in the chapter, and the beat's question off
`OUTLINE.md`, whose beat lines are numbered from 1 under each chapter's heading. The pages render
their titles from what it writes, and label a step **step n of N** on its own page: a reader is
walking this page's steps, and no number she is shown counts anything outside it.

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

BEAT_MARKER = re.compile(r"<!--[ \t]*beat[ \t]+([a-z0-9][a-z0-9-]*)\.(\d+)[ \t]*-->")

# A chapter is capped at twelve beats; `tools/beat_coverage.py` is where that is enforced, and this
# is here so a scaffolding built from a chapter over the cap cannot be written either.
CAP = 12
HEADING = re.compile(r"^##\s+(.+?)\s*$")
OUTLINE_BEAT = re.compile(r"^(\d+)\.\s+(.+?)\s*$")
OUTLINE_CHAPTER = re.compile(r"^##\s+(\d+)\s+·\s+(.*)$")


def reading_order() -> List[str]:
    """The chapters' slugs, in the book's own order — the only place that order is written down."""
    text = (CHAPTERS / "SUMMARY.md").read_text(encoding="utf-8")
    return [m.group(1)[:-3]
            for m in re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", text, re.M)]


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


def outline_beats() -> Dict[str, str]:
    """Every beat's question, by id, with the drafters' bracketed note cut off.

    The parenthetical italics in the outline say what the reader is supposed to *see*, and the whole
    point of this pass is that a demo shows it rather than telling her. So the answer is dropped
    here, at the boundary, where it cannot be reintroduced by an editing hand.
    """
    text = OUTLINE.read_text(encoding="utf-8")
    order = reading_order()
    beats: Dict[str, str] = {}
    slug = None
    for line in text.splitlines():
        chapter = OUTLINE_CHAPTER.match(line)
        if chapter:
            number = int(chapter.group(1))
            if number >= len(order):
                raise SystemExit(f"demo steps: OUTLINE.md chapter {number} has no slug in "
                                 f"chapters/SUMMARY.md")
            slug = order[number]
            continue
        found = OUTLINE_BEAT.match(line)
        if not found or slug is None:
            continue
        question = found.group(2)
        question = re.split(r"\s*\*\(", question)[0]
        question = re.sub(r"\s*\[[^\]]*\]\s*$", "", question)
        beats[f"{slug}.{int(found.group(1))}"] = strip_emphasis(question).strip()
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
        if found_beat.group(1) != slug:
            raise SystemExit(
                f"demo steps: chapters/{slug}.md:{number} carries the marker "
                f"{found_beat.group(0)}, which names another chapter. A beat's id carries the slug "
                f"of the file it is in."
            )
        sections.append({
            "anchor": anchor_for(heading),
            "heading": strip_emphasis(heading),
            "beat": f"{slug}.{int(found_beat.group(2))}",
            "n": int(found_beat.group(2)),
        })
        heading = None
    if not sections:
        raise SystemExit(f"demo steps: chapters/{slug}.md carries no beat markers")
    return sections


def derive() -> dict:
    beats = outline_beats()
    book = reading_order()
    missing = [slug for slug in DEMO_CHAPTERS if slug not in book]
    if missing:
        raise SystemExit(f"demo steps: {missing} are demo chapters and chapters/SUMMARY.md has no "
                         f"such chapter — the reading order is the only place a chapter's place in "
                         f"the book is written down")
    # The pages' order is READ from the reading order, never from the tuple above. A reviewer
    # pointed out that the tuple's own index was being written into steps.json as "the book's
    # order", so reordering chapters/SUMMARY.md — the file this contract makes the sole authority
    # on that — would have left the demo index sorted the old way with nothing objecting.
    listed = sorted(DEMO_CHAPTERS, key=book.index)
    if listed != list(DEMO_CHAPTERS):
        raise SystemExit(f"demo steps: DEMO_CHAPTERS is {list(DEMO_CHAPTERS)} and the reading order "
                         f"puts those chapters {listed}. Adding or moving a demo page is a decision "
                         f"made here and reviewed, so this is a refusal rather than a re-sort")
    chapters = {}
    for order, slug in enumerate(DEMO_CHAPTERS):
        markdown = (CHAPTERS / f"{slug}.md").read_text(encoding="utf-8")
        sections = chapter_sections(slug)
        for section in sections:
            if section["beat"] not in beats:
                raise SystemExit(
                    f"demo steps: chapters/{slug}.md claims beat {section['beat']}, which "
                    f"OUTLINE.md does not have. One of the two was renumbered without the other."
                )
            section["question"] = beats[section["beat"]]
        numbers = [section["n"] for section in sections]
        if numbers != sorted(numbers):
            raise SystemExit(
                f"demo steps: chapters/{slug}.md's beats are out of order: {numbers}"
            )
        if len(set(numbers)) != len(numbers):
            raise SystemExit(f"demo steps: chapters/{slug}.md claims a beat twice: {numbers}")
        if numbers != list(range(1, len(numbers) + 1)):
            raise SystemExit(
                f"demo steps: chapters/{slug}.md's beats do not run from 1 with no gap: {numbers}"
            )
        if len(numbers) > CAP:
            raise SystemExit(
                f"demo steps: chapters/{slug}.md carries {len(numbers)} beats, and a chapter is "
                f"capped at {CAP}"
            )
        chapters[slug] = {
            # This page's place among the demo pages, in the reading order's own sequence —
            # written down because the file is sorted by key, and because a chapter's place is
            # neither alphabetical nor a beat number any more. It is not the chapter's number in
            # the book: the demos cover five of sixteen chapters.
            "order": order,
            "title": chapter_title(markdown, slug),
            "beats": len(numbers),
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
