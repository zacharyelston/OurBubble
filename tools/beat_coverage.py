#!/usr/bin/env python3
"""Beat coverage and grain, counted from the prose rather than from the outline.

The first version of this counted beats out of `OUTLINE.md` and compared the total against a
chapter's paragraph count. That has a blind spot a reader found twice: counting from the contract
cannot tell a split beat from a missing one (K59), and it cannot tell that a chapter's sections have
been reordered away from the contract at all (K74). It reported 43/43 through both defects.

So it now reads the `<!-- beat N -->` marker under each `##` heading and checks the prose against the
outline in both directions:

  * every beat in range has at least one section claiming it, and none is claimed that does not exist
  * the sections' beat numbers ascend in the outline's own order
  * a beat carried by more than one section is named as a split rather than passed over

**What it cannot see, stated plainly, because the previous docstring overclaimed it (K77).** The
markers are self-declarations. A section that is moved *and relabelled* still ascends, so the tool
reports it in order — and relabelling is the natural thing to do when you move a section, which
makes it the likely kind of reorder rather than the unlikely one. A proofreader caught this by
swapping two sections and their markers together: the reader met the ripple bouncing off an edge one
section before there was a ripple, and this tool said "in the outline's order". Only reading catches
that. The order check is worth having against renumbering slips, not against a reorder.

**Why every beat is required unconditionally (K76).** The first version excused a chapter's first
beat when the section count came up one short, on the theory that the opening prose carries it. That
made the check's strictness a function of the thing being checked: deleting the first beat's section
is precisely the edit that drops the count by one, so it flipped the chapter from "all beats
required" to "first beat excused" and went green. The same proofreader deleted §They do not stack
from chapter 4 — 139 words carrying Aristotle, the eighteen centuries and the chapter's only three
record-backed numbers — and this tool printed "every one claimed by a section, in the outline's
order" and exited 0. `check_edition.py` does not compensate: its verbatim test reads the appendix's
body, never the chapter's, so the quotations a chapter exists to earn can leave it with parity
untouched at 35/13 and tier 0 green.

So the excusal is now **declared**: a chapter whose opening prose carries a beat says so with a
marker there, and `expected` is always every beat in range. A count can no longer buy leniency.

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


def sections(markdown: str) -> list[tuple[str, int | None, int, bool]]:
    """(heading, claimed beat or None, prose words, is_preamble) in document order.

    The preamble — everything above the first `##`, which is the H1, the scope block, the figure and
    any opening prose — is returned as a section so that a `<!-- beat N -->` declared there is
    visible. The first version split it off and threw it away, which is what made the excusal in
    `main` impossible to declare and therefore necessary to infer. It is flagged rather than
    silently included, because its word count is not comparable with a beat's: it carries the scope
    block and the figure, so the grain check skips it.
    """
    parts = re.split(r"^## ", markdown, flags=re.M)
    out = []
    for index, part in enumerate(parts):
        lines = part.splitlines()
        preamble = index == 0
        heading = "(opening)" if preamble else lines[0].strip()
        body = part if preamble else "\n".join(lines[1:])
        claimed = MARKER.search(body)
        out.append((heading,
                    int(claimed.group(1)) if claimed else None,
                    len(ce.words(ce.cleaned_prose(body))),
                    preamble))
    return out


def audit(beats: list[int], markdown: str) -> dict:
    """Every finding for one chapter's prose against its beats. **Pure** — reads no files.

    Split out of `main()` so the tool's own rules can be exercised on constructed prose. That is not
    tidiness: on `main` there is not yet a single chapter carrying beat markers, so fixtures are the
    only way to ratify this file at all, and a check that can only be tested by the thing it checks
    is the shape that let K76 through in the first place.
    """
    secs = sections(markdown)
    claimed = [b for _, b, _, _ in secs if b is not None]
    return {
        "secs": secs,
        "claimed": claimed,
        "unmarked": [h for h, b, _, pre in secs if b is None and not pre],
        # EVERY beat, always. No excusal is inferred from any count — see K76 in the docstring.
        "missing": [b for b in beats if b not in claimed],
        "stray": sorted({b for b in claimed if b not in beats}),
        "splits": sorted({b for b in claimed if claimed.count(b) > 1}),
        "reordered": claimed != sorted(claimed),
    }


def _fixture(preamble_beat: int | None, section_beats: list[int], bodies: dict | None = None) -> str:
    """A synthetic chapter: an opening, then one `##` section per beat listed."""
    out = "# T\n\n> **Scope.** A toy.\n\n"
    if preamble_beat is not None:
        out += f"<!-- beat {preamble_beat} -->\n\n"
    out += "Opening prose that carries no beat unless the marker above says so.\n\n"
    for beat in section_beats:
        text = (bodies or {}).get(beat, f"Prose belonging to beat {beat}.")
        out += f"## S{beat}\n\n<!-- beat {beat} -->\n\n{text}\n\n"
    return out


def self_test() -> list[str]:
    """Run the reader's attacks on constructed prose, every time, before trusting the tool.

    K76 was not a logic slip; it was a check whose strictness depended on the thing being checked,
    and it survived because nobody had made it fail on purpose. These are the attacks that found it
    and the ones next door, pinned so they cannot come back — including the one the tool is
    *documented not to catch*, asserted as a pass so the limit stays a stated limit rather than
    quietly becoming a bug.
    """
    beats = [36, 37, 38, 39]
    failures: list[str] = []

    def expect(label: str, markdown: str, missing: list[int], reordered: bool = False):
        found = audit(beats, markdown)
        if found["missing"] != missing:
            failures.append(f"self-test [{label}]: missing {found['missing']}, expected {missing}")
        if found["reordered"] != reordered:
            failures.append(
                f"self-test [{label}]: reordered={found['reordered']}, expected {reordered}")

    # the shape that must hold
    expect("all four sections", _fixture(None, [36, 37, 38, 39]), [])
    # the excusal, DECLARED — the opening prose says it carries the first beat
    expect("first beat declared on the opening", _fixture(36, [37, 38, 39]), [])
    # K76, the reader's exact attack: the first beat's section deleted, so the count comes up one
    # short. The old heuristic read that as "the opening must be carrying it" and went green.
    expect("K76 — first beat's section deleted", _fixture(None, [37, 38, 39]), [36])
    # its neighbours, which the old version did catch — kept so a fix cannot trade one for another
    expect("middle section deleted", _fixture(None, [36, 38, 39]), [37])
    expect("last section deleted", _fixture(None, [36, 37, 38]), [39])
    # every section deleted: the count is now three short, and all four beats are still required
    expect("every section deleted", _fixture(None, []), [36, 37, 38, 39])
    # a reorder that does NOT relabel is caught
    expect("moved without relabelling", _fixture(None, [36, 38, 37, 39]), [], reordered=True)
    # K77, asserted as a PASS: prose swapped and relabelled so the numbers still ascend. The tool
    # cannot see this and says so in its docstring; if this ever starts failing, the docstring is
    # what needs changing, not this line.
    swapped = _fixture(None, [36, 37, 38, 39], bodies={38: "Prose belonging to beat 39.",
                                                      39: "Prose belonging to beat 38."})
    expect("K77 — swapped and relabelled (a stated limit, not a bug)", swapped, [])

    # the opening is flagged as the preamble, so the grain never measures it against a beat's band
    if not audit(beats, _fixture(36, [37]))["secs"][0][3]:
        failures.append("self-test: the opening is not flagged as the preamble")

    return failures


def main() -> int:
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    order, grain, n_beats = reading_order(), [], 0
    # The guard is tested before it is trusted, on every run.
    problems = self_test()

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

        found = audit(beats, path.read_text(encoding="utf-8"))
        secs, claimed = found["secs"], found["claimed"]
        unmarked, missing = found["unmarked"], found["missing"]
        stray, splits, reordered = found["stray"], found["splits"], found["reordered"]

        for h, b, n, pre in secs:
            if pre:
                continue        # the preamble is not a beat's worth of prose; see sections()
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
            problems.append(f"chapter {number} ({slug}): the markers claim beats {claimed}, "
                            f"which does not ascend")
        if splits:
            note.append(f"split: {splits}")
        n_secs = sum(1 for *_, pre in secs if not pre)
        print(f"{number:>3}  {len(beats):>2} beats  {n_secs:>2} sections  {slug}"
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
    print(f"\n{n_beats} beats in range; every one claimed by a marker, and the claims ascend. "
          f"A section moved and relabelled together still ascends, so this is not a statement "
          f"about order — see the docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
