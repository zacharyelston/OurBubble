#!/usr/bin/env python3
"""Shift beat numbers — and chapter numbers — through `OUTLINE.md` and every chapter, in one pass.

Inserting a beat in the middle of the outline moves every beat after it, and every beat is written
down twice: once in `OUTLINE.md`, which is the contract, and once as a `<!-- beat N -->` marker in
the prose that answers it, which is what `tools/beat_coverage.py` checks the contract against. Doing
that by hand is how the two come apart, and when they come apart the coverage tool reports a
chapter's prose against the wrong questions while exiting 0.

So it is done here, by rule, and the rule is deliberately narrow:

  * in `OUTLINE.md`, a line beginning `N. ` is a beat; a line beginning `## N · ` is a chapter;
  * in `chapters/*.md`, a line that is exactly `<!-- beat N -->` is a marker;
  * nothing else in either file is touched — no prose, no table, no link.

Every substitution is computed against the ORIGINAL text and written once, so a shift can never be
applied twice to the same number (renumbering in place, low to high, is the classic way to turn
36→47 and then 47→58).

Usage:

    tools/renumber_beats.py --beats-from 36 --by 11 --chapters-from 4 --expect-last 105 --apply
    tools/renumber_beats.py --beats-from 36 --by 11                       # a dry run: prints only

`--expect-last` is the outline's highest beat number *before* the shift, and it is required to
write: the operator states what they believe the file contains, and a stale belief is refused. The
refusal deliberately does not print the number that would unblock it.

**The insertion window, because it is not obvious and it breaks the repository's own rule.** A
first shift opens a hole on purpose — this tool prints it — and `tools/beat_coverage.py`, which runs
in tier 0, refuses any hole in the numbering. So **from the shift until the new beat lines are typed
into `OUTLINE.md`, tier 0 is red**, by design: an outline with a hole in it is a half-finished
insertion. Do the two together, in one commit. And the way back out of a shift is `git checkout`,
not this tool: it refuses to run on a tree that already has a hole, so it cannot undo its own shift.

**What --expect-last does and does not buy, stated plainly.** It stops the realistic accident — the
documented command re-run verbatim. It cannot distinguish a re-run from a *deliberate* second
insertion at the same beat, because nothing in the file distinguishes them: both open a hole and
move everything after it. Two things cover that instead. A tree with a hole already in it is
refused here (finish the insertion first), and `tools/beat_coverage.py` — which runs in tier 0 —
refuses an outline whose beat numbering has a hole in it at all. That second one is the guard that
matters, and it was added for exactly this: a double shift moves the outline and every marker
together, so every beat is still claimed by a section and the coverage audit passed while the
numbering had an eleven-beat hole in it (a proofreader, 2026-09-02). Tier 0 now goes red on it.

It prints a self-check afterwards and refuses to write if it fails: the outline's beats must still
run consecutively — apart from the one hole a positive shift opens on purpose, which it names — and
every marker must claim a beat the outline has.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"
CHAPTERS = ROOT / "chapters"

BEAT_LINE = re.compile(r"^(\d+)\.\s", re.M)
CHAPTER_HEAD = re.compile(r"^##\s+(\d+)\s+·\s", re.M)
MARKER = re.compile(r"^<!--\s*beat\s+(\d+)\s*-->\s*$", re.M)


def shifted(text: str, pattern: re.Pattern, first: int, by: int) -> tuple[str, int]:
    """Every number `pattern` captures that is ≥ `first`, moved by `by`. One pass, no re-entry."""
    moves = 0

    def replace(match: re.Match) -> str:
        number = int(match.group(1))
        if number < first:
            return match.group(0)
        nonlocal moves
        moves += 1
        return match.group(0).replace(match.group(1), str(number + by), 1)

    return pattern.sub(replace, text), moves


def breaks_in(text: str) -> list[tuple[int, int]]:
    """Where the outline's beat run is already broken — i.e. an insertion is half finished."""
    beats = outline_beats(text)
    return [(a, b) for a, b in zip(beats, beats[1:]) if b != a + 1]


def outline_beats(text: str) -> list[int]:
    return [int(m.group(1)) for m in BEAT_LINE.finditer(text)]


def markers(text: str) -> list[int]:
    return [int(m.group(1)) for m in MARKER.finditer(text)]


def self_check(outline: str, chapters: dict[Path, str], room: tuple[int, int] | None = None
               ) -> list[str]:
    """The outline is an unbroken run — bar the hole this shift just opened — and no marker strays.

    A shift that makes room for new beats leaves exactly one hole, at exactly the place the beats
    are about to be written. That one is expected and is named; any other break is the sign of a
    half-applied renumbering, which is the failure this file exists to prevent.
    """
    beats = outline_beats(outline)
    problems: list[str] = []
    breaks = [(a, b) for a, b in zip(beats, beats[1:]) if b != a + 1]
    if room is not None:
        first, by = room
        expected = (first - 1, first + by)
        breaks = [pair for pair in breaks if pair != expected]
        if expected[0] in beats and expected[1] in beats:
            print(f"  the hole for the new beats: {expected[0]} → {expected[1]}, "
                  f"room for {by} beat(s)")
    if breaks:
        problems.append(f"the outline's beats are not consecutive: unexpected break(s) {breaks}")
    known = set(beats)
    for path, text in chapters.items():
        stray = sorted(set(markers(text)) - known)
        if stray:
            problems.append(f"{path.name}: marker(s) {stray} claim beats the outline does not have")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--beats-from", type=int, required=True,
                        help="the first beat number to move")
    parser.add_argument("--by", type=int, required=True, help="how far to move it (may be negative)")
    parser.add_argument("--chapters-from", type=int, default=None,
                        help="also move outline chapter headings from this number, by one")
    parser.add_argument("--chapter-by", type=int, default=1)
    parser.add_argument("--expect-last", type=int, default=None,
                        help="the highest beat number the outline has NOW, before the shift; "
                             "required with --apply")
    parser.add_argument("--apply", action="store_true", help="write the files (otherwise dry run)")
    args = parser.parse_args()

    outline = OUTLINE.read_text(encoding="utf-8")
    chapters = {path: path.read_text(encoding="utf-8")
                for path in sorted(CHAPTERS.glob("*.md"))}

    # The re-run guard, and why it is not optional (a proofreader, 2026-09-02): running the same
    # command twice on an already-shifted tree reopens *exactly* the hole the self-check expects,
    # so a fully double-shifted outline came out at exit 0 and only `beat_coverage.py` noticed.
    # Nothing in the file distinguishes the second run from the first — so the operator states what
    # they believe the file contains, and the second run cannot make that statement truthfully.
    last = max(outline_beats(outline))
    if args.apply and args.expect_last is None:
        print("refusing to write without --expect-last: read OUTLINE.md, and pass the highest beat "
              "number it currently carries. The number is not printed here on purpose.")
        return 1
    if args.expect_last is not None and args.expect_last != last:
        print(f"--expect-last {args.expect_last} does not match the outline, so this is not the "
              f"tree you meant to shift — a shift may already have been applied. Read OUTLINE.md. "
              f"Nothing written.")
        return 1
    if breaks_in(outline):
        print(f"the outline already has a gap in its beats {breaks_in(outline)} — an insertion is "
              f"half done. Write the new beats into it before shifting again. Nothing written.")
        return 1

    new_outline, beat_moves = shifted(outline, BEAT_LINE, args.beats_from, args.by)
    chapter_moves = 0
    if args.chapters_from is not None:
        new_outline, chapter_moves = shifted(new_outline, CHAPTER_HEAD, args.chapters_from,
                                             args.chapter_by)
    new_chapters: dict[Path, str] = {}
    marker_moves = 0
    for path, text in chapters.items():
        moved, count = shifted(text, MARKER, args.beats_from, args.by)
        new_chapters[path] = moved
        marker_moves += count
        if count:
            print(f"  {path.name}: {count} marker(s) moved")

    print(f"OUTLINE.md: {beat_moves} beat(s) moved by {args.by:+d}"
          + (f", {chapter_moves} chapter heading(s) moved by {args.chapter_by:+d}"
             if args.chapters_from is not None else ""))
    print(f"chapters/: {marker_moves} marker(s) moved")

    problems = self_check(new_outline, new_chapters,
                          room=(args.beats_from, args.by) if args.by > 0 else None)
    if problems:
        print("\n" + "\n".join("PROBLEM: " + p for p in problems))
        print("nothing written.")
        return 1

    if not args.apply:
        print("dry run — pass --apply to write.")
        return 0

    OUTLINE.write_text(new_outline, encoding="utf-8")
    for path, text in new_chapters.items():
        if text != chapters[path]:
            path.write_text(text, encoding="utf-8")
    print("written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
