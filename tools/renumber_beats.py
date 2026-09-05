#!/usr/bin/env python3
"""Shift one chapter's beat numbers through `OUTLINE.md` and that chapter's markers, in one pass.

Inserting a beat moves every later beat **in its own chapter and nowhere else**, because a beat's id
is chapter-scoped: `<!-- beat make-it-move.3 -->`, numbered from 1 inside the chapter (issue #77).
The book-wide shift this file used to perform — `--beats-from 36 --by 11`, moving a hundred markers,
the whole outline and every reference anybody had written down — does not exist any more, and
neither does `--chapters-from`: moving a chapter renumbers nothing at all now, so a chapter that
moves is a `chapters/SUMMARY.md` edit and an `OUTLINE.md` heading edit, with no beat touched.

Every beat is still written down twice: once in `OUTLINE.md`, which is the contract, and once as a
marker in the prose that answers it, which is what `tools/beat_coverage.py` checks the contract
against. Doing that by hand is how the two come apart, and when they come apart the coverage tool
reports a chapter's prose against the wrong questions.

So it is done here, by rule, and the rule is deliberately narrow:

  * in `OUTLINE.md`, under **one** chapter's `## N · Title` heading, a line beginning `n. ` is a
    beat; nothing above or below that heading's own block is read or written;
  * in `chapters/<slug>.md`, a line that is exactly `<!-- beat <slug>.n -->` is a marker;
  * nothing else in either file is touched — no prose, no table, no link.

Every substitution is computed against the ORIGINAL text and written once, so a shift can never be
applied twice to the same number (renumbering in place, low to high, is the classic way to turn
3→4 and then 4→5).

Usage:

    tools/renumber_beats.py --chapter make-it-move --from 3 --by 1 --expect-last 12 --apply
    tools/renumber_beats.py --chapter make-it-move --from 3 --by 1          # a dry run: prints only

`--expect-last` is that chapter's highest beat number *before* the shift, and it is required to
write: the operator states what they believe the file contains, and a stale belief is refused. The
refusal deliberately does not print the number that would unblock it.

**The insertion window, because it is not obvious and it breaks the repository's own rule.** A
shift opens a hole on purpose — this tool prints it — and `tools/beat_coverage.py`, which runs in
tier 0, refuses any hole in a chapter's numbering. So **from the shift until the new beat lines are
typed into `OUTLINE.md`, tier 0 is red**, by design: an outline with a hole in it is a half-finished
insertion. Do the two together, in one commit. And the way back out of a shift is `git checkout`,
not this tool: it refuses to run on a chapter that already has a hole, so it cannot undo its own
shift.

**What --expect-last does and does not buy, stated plainly.** It stops the realistic accident — the
documented command re-run verbatim. It cannot distinguish a re-run from a *deliberate* second
insertion at the same beat, because nothing in the file distinguishes them: both open a hole and
move everything after it. Two things cover that instead. A chapter with a hole already in it is
refused here (finish the insertion first), and `tools/beat_coverage.py` refuses a chapter whose beat
numbering has a hole in it at all. That second one is the guard that matters, and it was added for
exactly this: a double shift moved the outline and every marker together, so every beat was still
claimed by a section and the coverage audit passed while the numbering had an eleven-beat hole in it
(a proofreader, 2026-09-02). Tier 0 goes red on it.

It prints a self-check afterwards and refuses to write if it fails: the chapter's beats must still
run consecutively from 1 — apart from the one hole a positive shift opens on purpose, which it
names — no beat may go past the cap of twelve, and every marker must claim a beat the chapter's
outline block has.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTLINE = ROOT / "OUTLINE.md"
CHAPTERS = ROOT / "chapters"
SUMMARY = CHAPTERS / "SUMMARY.md"

CAP = 12

BEAT_LINE = re.compile(r"^(\d+)\.\s", re.M)
CHAPTER_HEAD = re.compile(r"^##\s+(\d+)\s+·\s+(.*)$", re.M)


def marker_pattern(slug: str) -> re.Pattern:
    """That chapter's markers, and only that chapter's. See beat_coverage.py on `[ \t]*`."""
    return re.compile(rf"^<!--[ \t]*beat[ \t]+{re.escape(slug)}\.(\d+)[ \t]*-->[ \t]*$", re.M)


def reading_order() -> list[str]:
    text = SUMMARY.read_text(encoding="utf-8")
    return [m.group(1)[:-3] for m in re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", text, re.M)]


def chapter_block(outline: str, slug: str) -> tuple[int, int]:
    """Where this chapter's beat lines live in `OUTLINE.md`, as a (start, end) slice. **Pure.**

    The block is bounded by the chapter's own heading and the next one, so a shift can touch nothing
    outside it — which is the whole difference between this file and the one it replaced.
    """
    order = reading_order()
    if slug not in order:
        raise SystemExit(f"renumber: {slug} is not a chapter in chapters/SUMMARY.md")
    wanted = order.index(slug)
    heads = list(CHAPTER_HEAD.finditer(outline))
    for index, head in enumerate(heads):
        if int(head.group(1)) == wanted:
            end = heads[index + 1].start() if index + 1 < len(heads) else len(outline)
            return head.end(), end
    raise SystemExit(f"renumber: OUTLINE.md has no `## {wanted} · ` heading for {slug}")


def beats_in(block: str) -> list[int]:
    return [int(m.group(1)) for m in BEAT_LINE.finditer(block)]


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


def breaks_in(beats: list[int]) -> list[tuple[int, int]]:
    """Where the run is already broken — i.e. an insertion is half finished."""
    return [(a, b) for a, b in zip(beats, beats[1:]) if b != a + 1]


def self_check(beats: list[int], markers: list[int], slug: str,
               room: tuple[int, int] | None = None) -> list[str]:
    """The chapter is an unbroken run from 1 — bar the hole this shift just opened — under the cap.

    A shift that makes room for new beats leaves exactly one hole, at exactly the place the beats are
    about to be written. That one is expected and is named; any other break is the sign of a
    half-applied renumbering, which is the failure this file exists to prevent.
    """
    problems: list[str] = []
    breaks = breaks_in(beats)
    if room is not None:
        first, by = room
        expected = (first - 1, first + by)
        breaks = [pair for pair in breaks if pair != expected]
        if expected[0] in beats and expected[1] in beats:
            print(f"  the hole for the new beats: {slug}.{expected[0]} → {slug}.{expected[1]}, "
                  f"room for {by} beat(s)")
    if beats and beats[0] != 1:
        problems.append(f"{slug}: the chapter's beats start at {beats[0]}, not 1")
    if breaks:
        problems.append(f"{slug}: the chapter's beats are not consecutive: unexpected break(s) "
                        f"{breaks}")
    if beats and max(beats) > CAP:
        problems.append(f"{slug}: this shift takes a beat past {slug}.{CAP}, and a chapter is "
                        f"capped at {CAP} beats. Split the chapter instead")
    stray = sorted(set(markers) - set(beats))
    if stray:
        problems.append(f"{slug}.md: marker(s) {[f'{slug}.{n}' for n in stray]} claim beats the "
                        f"outline does not have")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description="shift one chapter's beat numbers")
    parser.add_argument("--chapter", required=True, help="the chapter's slug, e.g. make-it-move")
    parser.add_argument("--from", dest="first", type=int, required=True,
                        help="the first beat number in that chapter to move")
    parser.add_argument("--by", type=int, required=True, help="how far to move it (may be negative)")
    parser.add_argument("--expect-last", type=int, default=None,
                        help="the highest beat number this chapter has NOW, before the shift; "
                             "required with --apply")
    parser.add_argument("--apply", action="store_true", help="write the files (otherwise dry run)")
    args = parser.parse_args()

    slug = args.chapter
    outline = OUTLINE.read_text(encoding="utf-8")
    start, end = chapter_block(outline, slug)
    block = outline[start:end]
    beats = beats_in(block)
    if not beats:
        print(f"renumber: OUTLINE.md lists no beats under {slug}. Nothing written.")
        return 1

    path = CHAPTERS / f"{slug}.md"
    if not path.exists():
        print(f"renumber: chapters/{slug}.md does not exist. Nothing written.")
        return 1
    chapter = path.read_text(encoding="utf-8")
    pattern = marker_pattern(slug)

    # The re-run guard, and why it is not optional (a proofreader, 2026-09-02): running the same
    # command twice on an already-shifted chapter reopens *exactly* the hole the self-check expects,
    # so a fully double-shifted outline came out at exit 0 and only `beat_coverage.py` noticed.
    # Nothing in the file distinguishes the second run from the first — so the operator states what
    # they believe the file contains, and the second run cannot make that statement truthfully.
    last = max(beats)
    if args.apply and args.expect_last is None:
        print("refusing to write without --expect-last: read OUTLINE.md, and pass the highest beat "
              "number this chapter currently carries. The number is not printed here on purpose.")
        return 1
    if args.expect_last is not None and args.expect_last != last:
        print(f"--expect-last {args.expect_last} does not match {slug} in OUTLINE.md, so this is "
              f"not the chapter you meant to shift — a shift may already have been applied. Read "
              f"OUTLINE.md. Nothing written.")
        return 1
    if breaks_in(beats):
        print(f"{slug} already has a gap in its beats {breaks_in(beats)} — an insertion is half "
              f"done. Write the new beats into it before shifting again. Nothing written.")
        return 1

    new_block, beat_moves = shifted(block, BEAT_LINE, args.first, args.by)
    new_outline = outline[:start] + new_block + outline[end:]
    new_chapter, marker_moves = shifted(chapter, pattern, args.first, args.by)

    print(f"OUTLINE.md, under {slug}: {beat_moves} beat(s) moved by {args.by:+d}")
    print(f"chapters/{slug}.md: {marker_moves} marker(s) moved")

    problems = self_check(beats_in(new_block),
                          [int(m.group(1)) for m in pattern.finditer(new_chapter)],
                          slug, room=(args.first, args.by) if args.by > 0 else None)
    if problems:
        print("\n" + "\n".join("PROBLEM: " + p for p in problems))
        print("nothing written.")
        return 1

    if not args.apply:
        print("dry run — pass --apply to write.")
        return 0

    OUTLINE.write_text(new_outline, encoding="utf-8")
    if new_chapter != chapter:
        path.write_text(new_chapter, encoding="utf-8")
    print("written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
