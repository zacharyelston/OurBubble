#!/usr/bin/env python3
"""One-shot, idempotent migration: book-wide beat numbers become chapter-scoped ids.

A beat used to be numbered across the whole book — `<!-- beat 35 -->` — so inserting one moved every
later marker, every line of `OUTLINE.md` after it, `demos/steps.json`, `DEMOS.md`'s ranges and every
reference anybody had written down. It happened three times in two weeks (a chapter added, a chapter
added again, then the preface moving all 119 by four), and each time something holding a number in
its own source went stale in silence.

A beat's id is now **`<chapter-slug>.<n>`**, `n` counted from 1 inside its own chapter:

    <!-- beat make-it-move.3 -->

`OUTLINE.md` numbers each chapter's beats from 1 under that chapter's heading. The chapters' order
lives in `chapters/SUMMARY.md` and in `OUTLINE.md`'s headings — never inside a beat's id — so moving
a chapter renumbers nothing at all, and inserting a beat renumbers only that chapter's later beats.

What this script rewrites, in one pass, from the numbering the tree currently carries:

  1. every `<!-- beat N -->` marker in `chapters/*.md`, to the id its own chapter gives it;
  2. `OUTLINE.md`'s beat lines, so each chapter's run starts again at 1;
  3. the cross-references that name a beat by its number in prose or in a comment — the appendix
     generator's two notes, the outline's drafter's notes, three tool comments and the octahedron
     working note — each one mapped through the same table as the markers;
  4. four sentences in `CONTINUUM.md` whose numbers are **history** rather than references: they
     name ranges in a numbering that no longer exists, so they are replaced by what they were
     recording (a count of beats), not by a translated range. A mapped rewrite of those would be a
     lie with a new syntax.

**Deterministic and idempotent.** The map is computed from the file the migration is being read out
of, `OUTLINE.md`, and a tree that has already been migrated is detected and left alone: each
chapter's beats already start at 1, which cannot be true of a book-wide numbering with more than one
chapter in it. Run it twice and the second run writes nothing.

**A run that writes nothing says only that.** The first version printed "every beat already carries
a chapter-scoped id" whenever its plan came out empty — which a reviewer showed is a different
statement: revert one chapter's markers to the book-wide form and the outline still reads as
migrated, so the plan is empty and sixteen book-wide markers are left standing. The surviving
markers are now counted before anything is claimed, and a mixed tree is an error rather than a
reassuring line.

    tools/migrate_beat_ids.py --dry-run     # print the unified diff and write nothing
    tools/migrate_beat_ids.py --apply       # write the files

FIREWALL: this is tooling for a book about a toy DEC lattice; nothing here is a claim about nature.
"""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"
SUMMARY = ROOT / "chapters" / "SUMMARY.md"
CHAPTERS = ROOT / "chapters"

OUTLINE_CHAPTER = re.compile(r"^##\s+(\d+)\s+·\s+(.*)$")
OUTLINE_BEAT = re.compile(r"^(\d+)\.\s")
# A marker on its own line. The trailing run is `[ \t]*`, never `\s*`: `\s` matches a newline,
# so a `\s*$` here would eat the blank line after the marker and glue the comment to the prose.
MARKER = re.compile(r"^<!--[ \t]*beat[ \t]+(\d+)[ \t]*-->[ \t]*$", re.M)

# `beat 22`, `Beat 4`, `beat 22's`, `beats 109-110`, `beats 35 and 47`. The number is what is
# replaced; the word, the possessive and the joiner are kept exactly as they were written.
REFERENCE = re.compile(
    r"\b(?P<word>[Bb]eats?)\s+(?P<first>\d+)"
    r"(?:(?P<joiner>\s*[–—-]\s*|\s+and\s+)(?P<second>\d+))?"
)

# The files whose beat numbers are **references to beats that still exist**, and are therefore
# mapped. Everything else in the repository that names a beat names it by what it is.
REFERRING = (
    "OUTLINE.md",
    "gen_appendix.py",
    "tools/octahedron.py",
    "tools/oracle.py",
    "tools/napkin_export.py",
    "notes/octahedron-crossing.md",
)

# History, not reference. Each of these sentences records a numbering that was true when it was
# written and is not translatable into the new ids, so it is rewritten to say what it was recording.
LITERAL: Tuple[Tuple[str, str, str], ...] = (
    (
        "CONTINUUM.md",
        "a new chapter 4, *The shape between*, beats 36–46, with the outline and every later "
        "beat renumbered by `tools/renumber_beats.py`",
        "a new chapter 4, *The shape between*, of eleven beats, with the outline and every later "
        "beat renumbered by `tools/renumber_beats.py`",
    ),
    (
        "CONTINUUM.md",
        "a new chapter 5, *Two worlds threaded*, taking beats 44–49 — every later beat +3 and "
        "every later chapter +1, in one `tools/renumber_beats.py` pass",
        "a new chapter 5, *Two worlds threaded*, taking six beats — every later beat +3 and "
        "every later chapter +1, in one `tools/renumber_beats.py` pass",
    ),
    (
        "tools/octahedron.py",
        "it is `tetra_inside_sum` — chapter 2's beat 23 — run four times and",
        "it is `tetra_inside_sum` — the tetrahedron chapter's first beat — run four times and",
    ),
)


def surviving_book_wide_markers() -> List[Tuple[str, int]]:
    """Which chapter files still carry a book-wide marker, and how many. Read, not assumed."""
    out = []
    for path in sorted(CHAPTERS.glob("*.md")):
        count = len(MARKER.findall(path.read_text(encoding="utf-8")))
        if count:
            out.append((f"chapters/{path.name}", count))
    return out


def read(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def outline_chapters(text: str) -> List[Tuple[int, str, List[int]]]:
    out: List[Tuple[int, str, List[int]]] = []
    for line in text.splitlines():
        head = OUTLINE_CHAPTER.match(line.strip())
        if head:
            out.append((int(head.group(1)), head.group(2).strip(), []))
        elif (beat := OUTLINE_BEAT.match(line.strip())) and out:
            out[-1][2].append(int(beat.group(1)))
    return out


def reading_order() -> List[str]:
    text = SUMMARY.read_text(encoding="utf-8")
    return [m.group(1)[:-3]
            for m in re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", text, re.M)]


def already_migrated(chapters: List[Tuple[int, str, List[int]]]) -> bool:
    """Every chapter's run starts at 1 — which a book-wide numbering cannot do twice."""
    return len(chapters) > 1 and all(beats and beats[0] == 1 for _, _, beats in chapters)


def build_map(chapters: List[Tuple[int, str, List[int]]], order: List[str]) -> Dict[int, str]:
    ids: Dict[int, str] = {}
    for number, title, beats in chapters:
        if number >= len(order):
            raise SystemExit(f"migrate: chapter {number} ({title}) has no slug in "
                             f"chapters/SUMMARY.md")
        slug = order[number]
        for index, beat in enumerate(beats, start=1):
            if beat in ids:
                raise SystemExit(f"migrate: OUTLINE.md carries beat {beat} twice — the tree is "
                                 f"neither wholly book-wide nor wholly migrated. Nothing written.")
            ids[beat] = f"{slug}.{index}"
    return ids


def rewrite_markers(text: str, slug: str, ids: Dict[int, str], path: str) -> str:
    def replace(found: re.Match) -> str:
        beat = int(found.group(1))
        if beat not in ids:
            raise SystemExit(f"migrate: {path} claims beat {beat}, which OUTLINE.md has not got")
        if not ids[beat].startswith(f"{slug}."):
            raise SystemExit(f"migrate: {path} claims beat {beat}, which OUTLINE.md gives to "
                             f"{ids[beat].rsplit('.', 1)[0]}")
        return f"<!-- beat {ids[beat]} -->"

    return MARKER.sub(replace, text)


def rewrite_outline_numbering(text: str, chapters: List[Tuple[int, str, List[int]]]) -> str:
    """Each chapter's beat lines renumbered from 1, in place, one pass over the lines."""
    local: Dict[int, int] = {}
    for _, _, beats in chapters:
        for index, beat in enumerate(beats, start=1):
            local[beat] = index
    out = []
    for line in text.splitlines(keepends=True):
        found = OUTLINE_BEAT.match(line)
        if found and int(found.group(1)) in local:
            out.append(f"{local[int(found.group(1))]}." + line[found.end(1) + 1:])
        else:
            out.append(line)
    return "".join(out)


def rewrite_references(text: str, ids: Dict[int, str], path: str) -> str:
    def replace(found: re.Match) -> str:
        numbers = [found.group("first")] + ([found.group("second")]
                                            if found.group("second") else [])
        for number in numbers:
            if int(number) not in ids:
                raise SystemExit(f"migrate: {path} names beat {number}, which OUTLINE.md has not "
                                 f"got — say what the beat is instead, or fix the reference")
        out = f"{found.group('word')} {ids[int(numbers[0])]}"
        if len(numbers) == 2:
            out += f"{found.group('joiner')}{ids[int(numbers[1])]}"
        return out

    return REFERENCE.sub(replace, text)


def migrate() -> Dict[str, str]:
    """Every file this changes, as {path: new text}. **Pure** — reads the tree, writes nothing."""
    outline = read("OUTLINE.md")
    chapters = outline_chapters(outline)
    if not chapters:
        raise SystemExit("migrate: OUTLINE.md carries no chapter headings — has its format changed?")
    if already_migrated(chapters):
        return {}
    order = reading_order()
    ids = build_map(chapters, order)

    changed: Dict[str, str] = {}

    for number, _title, _beats in chapters:
        slug = order[number]
        path = f"chapters/{slug}.md"
        before = read(path)
        after = rewrite_markers(before, slug, ids, path)
        if after != before:
            changed[path] = after

    new_outline = rewrite_outline_numbering(outline, chapters)

    for name, old, new in LITERAL:
        before = changed.get(name, read(name))
        if old in before:
            changed[name] = before.replace(old, new)
        elif new not in before:
            raise SystemExit(f"migrate: {name} no longer contains the sentence this migration "
                             f"rewrites: {old[:60]!r}… Nothing written.")

    for name in REFERRING:
        before = changed.get(name, new_outline if name == "OUTLINE.md" else read(name))
        after = rewrite_references(before, ids, name)
        if name == "OUTLINE.md" or after != read(name):
            changed[name] = after

    return {name: text for name, text in changed.items() if text != read(name)}


def main(argv: List[str]) -> int:
    parser = argparse.ArgumentParser(description="beat numbers → chapter-scoped ids")
    parser.add_argument("--dry-run", action="store_true", help="print the diff, write nothing")
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args(argv)
    if args.apply == args.dry_run:
        parser.error("pass exactly one of --dry-run and --apply")

    changed = migrate()
    surviving = surviving_book_wide_markers()
    if not changed:
        if surviving:
            print("migrate: no file changed, and yet "
                  + ", ".join(f"{name} carries {count} `<!-- beat N -->` marker(s)"
                              for name, count in surviving)
                  + ". OUTLINE.md reads as already migrated, so the map this needs no longer "
                  + "exists: restore those markers from git, or write their ids by hand.")
            return 1
        print("migrate: no file changed, and no `<!-- beat N -->` marker survives in chapters/.")
        return 0

    for name in sorted(changed):
        before = read(name).splitlines(keepends=True)
        after = changed[name].splitlines(keepends=True)
        diff = list(difflib.unified_diff(before, after, fromfile=f"a/{name}", tofile=f"b/{name}"))
        sys.stdout.writelines(diff)

    print(f"\nmigrate: {len(changed)} file(s) — "
          + ", ".join(sorted(changed)))
    if args.dry_run:
        print("dry run — pass --apply to write.")
        return 0
    for name, text in changed.items():
        (ROOT / name).write_text(text, encoding="utf-8")
    print("written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
