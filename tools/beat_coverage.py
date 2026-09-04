#!/usr/bin/env python3
"""Beat coverage and grain, counted from the prose rather than from the outline.

The first version of this counted beats out of `OUTLINE.md` and compared the total against a
chapter's paragraph count. That has a blind spot a reader found twice: counting from the contract
cannot tell a split beat from a missing one (K59), and it cannot tell that a chapter's sections have
been reordered away from the contract at all (K74). It reported 43/43 through both defects.

So it reads the `<!-- beat <slug>.<n> -->` marker under each `##` heading and checks the prose
against the outline in both directions.

**The ids are chapter-scoped (2026-09-04, issue #77).** A beat used to be numbered across the whole
book, so inserting one moved every later marker, every later outline line and everything anybody had
written down; it happened three times in two weeks. A beat's id is now its chapter's slug and its
place inside that chapter, counted from 1 — `make-it-move.3` — and the chapters' order lives in
`chapters/SUMMARY.md` and `OUTLINE.md`'s headings, never inside an id. So this file's contract is
per chapter, and it is exactly this:

  * every beat line under a chapter's heading in `OUTLINE.md` is claimed by a marker in that
    chapter's file, and no marker claims a beat the outline has not got;
  * a chapter's beat lines run 1, 2, 3 … from 1, with no hole;
  * every marker in a chapter's file carries **that chapter's own slug** — a marker naming another
    chapter is refused here rather than counted somewhere else;
  * the ids the markers claim, in the order they appear, ascend from 1 with no gap;
  * **at most twelve beats in a chapter** — today's largest, *Make it move*, and the ceiling the
    1,800-word grain already implies. A chapter that wants a thirteenth splits instead.

**A split is contiguous or it is a defect.** A beat carried by more than one section is legitimate
and is named below as a split — but its sections are adjacent. The same id claimed again after a
later one has appeared is a section that was moved or relabelled, and that is refused.

**What it cannot see, stated plainly, because an earlier docstring overclaimed it (K77).** The
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

**And no global beat number survives anywhere.** A number that used to be a beat's name is now
nobody's name, so `OUTLINE.md`, `CONTINUUM.md`, `demos/DEMOS.md` and the chapters are scanned for
the old form — `beat 35`, `beats 12 and 41` — and it is refused. Prose names a beat by what it is;
tooling and review notes name it `slug.n`.

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

# Twelve beats in a chapter, and not a thirteenth. See the docstring.
CAP = 12

# A marker on its own line. The trailing run is `[ \t]*`, never `\s*`: `\s` matches a newline, and a
# pattern that ate the blank line after the marker would report a different file from the one on
# disk.
MARKER = re.compile(r"^<!--[ \t]*beat[ \t]+([a-z0-9][a-z0-9-]*)\.(\d+)[ \t]*-->[ \t]*$", re.M)

# Anything still calling a beat by a book-wide number. `beat 35`, `Beats 12`, `beats 44–49`.
GLOBAL_FORM = re.compile(r"\b[Bb]eats?\s+\d+")

# What the scan reads. The chapters are added to it at run time; these are the contract files.
SCANNED = ("OUTLINE.md", "CONTINUUM.md", "demos/DEMOS.md")


def outline_chapters() -> list[tuple[int, str, list[int]]]:
    out: list[tuple[int, str, list[int]]] = []
    for line in OUTLINE.read_text(encoding="utf-8").splitlines():
        head = re.match(r"^##\s+(\d+)\s+·\s+(.*)$", line.strip())
        if head:
            out.append((int(head.group(1)), head.group(2).strip(), []))
        elif (beat := re.match(r"^(\d+)\.\s", line.strip())) and out:
            out[-1][2].append(int(beat.group(1)))
    return out


def numbering_problems(beats: list[int], where: str) -> list[str]:
    """One chapter's outline beats must run 1, 2, 3 … to at most twelve. **Pure.**

    This is the check that was missing when the numbering was book-wide, and the gap it left was
    found by a proofreader (2026-09-02): `tools/renumber_beats.py` run twice shifted the outline's
    beats AND every chapter's markers together, so every beat was still claimed by a section and the
    audit below passed — while the outline had an eleven-beat hole in it. The claims agreeing with
    the contract means nothing if the contract itself has a hole. Scoped to a chapter now, and with
    the cap, which is the other thing a contract can get wrong.
    """
    if not beats:
        return [f"{where}: the outline lists no beats under this chapter's heading"]
    problems = []
    if beats[0] != 1:
        problems.append(f"{where}: the outline's beats start at {beats[0]}, not 1")
    holes = [(a, b) for a, b in zip(beats, beats[1:]) if b != a + 1]
    if holes:
        problems.append(
            f"{where}: the outline's beat numbering has {len(holes)} hole(s): "
            + ", ".join(f"{a} → {b}" for a, b in holes)
            + " — a renumbering is half applied, or a beat was deleted"
        )
    if len(beats) > CAP:
        problems.append(
            f"{where}: {len(beats)} beats, and a chapter is capped at {CAP}. Split the chapter — "
            f"that is the scope rule, mechanically"
        )
    return problems


def reading_order() -> list[str]:
    text = SUMMARY.read_text(encoding="utf-8")
    return [m.group(1)[:-3] for m in re.finditer(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", text, re.M)]


def global_form_problems() -> list[str]:
    """Nothing reader-facing, and nothing in the contract, still calls a beat by a number.

    Refusing rather than checking (EDITION_STANDARD rule 4): the question is not whether the right
    id is present somewhere, it is whether the wrong form is absent everywhere.
    """
    problems = []
    paths = [ROOT / name for name in SCANNED]
    paths += sorted((ROOT / "chapters").glob("*.md"))
    for path in paths:
        if not path.exists():
            problems.append(f"{path.name}: missing, and it is one of the files scanned for stale "
                            f"beat numbers")
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            found = GLOBAL_FORM.search(line)
            if found:
                problems.append(
                    f"{path.relative_to(ROOT)}:{number}: writes {found.group(0).strip()!r} — a "
                    f"book-wide beat number, which is nobody's name any more. A beat is "
                    f"`slug.n` (make-it-move.3); prose names it by what it is"
                )
    return problems


def sections(markdown: str) -> list[tuple[str, str | None, int, bool]]:
    """(heading, claimed beat id or None, prose words, is_preamble) in document order.

    The preamble — everything above the first `##`, which is the H1, the scope block, the figure and
    any opening prose — is returned as a section so that a marker declared there is visible. The
    first version split it off and threw it away, which is what made the excusal in `main`
    impossible to declare and therefore necessary to infer. It is flagged rather than silently
    included, because its word count is not comparable with a beat's: it carries the scope block and
    the figure, so the grain check skips it.
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
                    f"{claimed.group(1)}.{claimed.group(2)}" if claimed else None,
                    len(ce.words(ce.cleaned_prose(body))),
                    preamble))
    return out


def audit(slug: str, beats: list[int], markdown: str) -> dict:
    """Every finding for one chapter's prose against its beats. **Pure** — reads no files.

    Split out of `main()` so the tool's own rules can be exercised on constructed prose. That is not
    tidiness: a check that can only be tested by the thing it checks is the shape that let K76
    through in the first place.
    """
    secs = sections(markdown)
    claimed = [beat for _, beat, _, _ in secs if beat is not None]

    foreign = sorted({beat for beat in claimed if not beat.startswith(f"{slug}.")})
    mine = [beat for beat in claimed if beat.startswith(f"{slug}.")]
    numbers = [int(beat.split(".", 1)[1]) for beat in mine]

    # The distinct ids, in the order they were first claimed. A split's sections repeat an id; the
    # run they form is what has to ascend from 1.
    run: list[int] = []
    for number in numbers:
        if number not in run:
            run.append(number)

    # A repeat that is not adjacent to its own first claim: a section moved or relabelled.
    scattered = sorted({number for index, number in enumerate(numbers)
                        if index and number != numbers[index - 1] and number in numbers[:index - 1]})

    return {
        "secs": secs,
        "claimed": claimed,
        "foreign": foreign,
        "run": run,
        "unmarked": [h for h, b, _, pre in secs if b is None and not pre],
        # EVERY beat, always. No excusal is inferred from any count — see K76 in the docstring.
        "missing": [b for b in beats if b not in run],
        "stray": sorted({n for n in run if n not in beats}),
        "over_cap": sorted({n for n in run if n > CAP}),
        "splits": sorted({n for n in numbers if numbers.count(n) > 1}),
        "scattered": scattered,
        "reordered": run != sorted(run),
    }


def _fixture(slug: str, preamble_beat: int | None, section_beats: list[int],
             bodies: dict | None = None, foreign: dict | None = None) -> str:
    """A synthetic chapter: an opening, then one `##` section per beat listed."""
    out = "# T\n\n> **Scope.** A toy.\n\n"
    if preamble_beat is not None:
        out += f"<!-- beat {slug}.{preamble_beat} -->\n\n"
    out += "Opening prose that carries no beat unless the marker above says so.\n\n"
    for index, beat in enumerate(section_beats):
        text = (bodies or {}).get(beat, f"Prose belonging to beat {index}.")
        owner = (foreign or {}).get(index, slug)
        out += f"## S{index}\n\n<!-- beat {owner}.{beat} -->\n\n{text}\n\n"
    return out


def self_test() -> list[str]:
    """Run the reader's attacks on constructed prose, every time, before trusting the tool.

    K76 was not a logic slip; it was a check whose strictness depended on the thing being checked,
    and it survived because nobody had made it fail on purpose. These are the attacks that found it
    and the ones next door, pinned so they cannot come back — including the one the tool is
    *documented not to catch*, asserted as a pass so the limit stays a stated limit rather than
    quietly becoming a bug.
    """
    slug, beats = "make-it-move", [1, 2, 3, 4]
    failures: list[str] = []

    def expect(label: str, markdown: str, **wanted):
        found = audit(slug, beats, markdown)
        for key, value in wanted.items():
            if found[key] != value:
                failures.append(f"self-test [{label}]: {key}={found[key]!r}, expected {value!r}")

    # the shape that must hold
    expect("all four sections", _fixture(slug, None, [1, 2, 3, 4]), missing=[], reordered=False)
    # the excusal, DECLARED — the opening prose says it carries the first beat
    expect("first beat declared on the opening", _fixture(slug, 1, [2, 3, 4]), missing=[])
    # K76, the reader's exact attack: the first beat's section deleted, so the count comes up one
    # short. The old heuristic read that as "the opening must be carrying it" and went green.
    expect("K76 — first beat's section deleted", _fixture(slug, None, [2, 3, 4]), missing=[1])
    # its neighbours, which the old version did catch — kept so a fix cannot trade one for another
    expect("middle section deleted", _fixture(slug, None, [1, 3, 4]), missing=[2])
    expect("last section deleted", _fixture(slug, None, [1, 2, 3]), missing=[4])
    expect("every section deleted", _fixture(slug, None, []), missing=[1, 2, 3, 4])
    # a reorder that does NOT relabel is caught
    expect("moved without relabelling", _fixture(slug, None, [1, 3, 2, 4]), reordered=True)
    # a beat carried by two adjacent sections is a split, and is legitimate
    expect("a declared split", _fixture(slug, None, [1, 2, 2, 3, 4]), missing=[], splits=[2],
           scattered=[], reordered=False)
    # the same id claimed again after a later one: a section moved or relabelled, not a split
    expect("a duplicate that is not a split", _fixture(slug, None, [1, 2, 3, 2, 4]), scattered=[2])
    # a marker naming another chapter, in this chapter's file
    expect("a marker in the wrong chapter's file",
           _fixture(slug, None, [1, 2, 3, 4], foreign={2: "the-shadow"}),
           foreign=["the-shadow.3"], missing=[3])
    # a thirteenth beat's marker, in a chapter the outline caps at four
    expect("a thirteenth beat", _fixture(slug, None, [1, 2, 3, 4, 13]), stray=[13], over_cap=[13])
    # K77, asserted as a PASS: prose swapped and relabelled so the numbers still ascend. The tool
    # cannot see this and says so in its docstring; if this ever starts failing, the docstring is
    # what needs changing, not this line.
    swapped = _fixture(slug, None, [1, 2, 3, 4], bodies={3: "Prose belonging to beat 3.",
                                                        4: "Prose belonging to beat 2."})
    expect("K77 — swapped and relabelled (a stated limit, not a bug)", swapped, missing=[])

    # the opening is flagged as the preamble, so the grain never measures it against a beat's band
    if not audit(slug, beats, _fixture(slug, 1, [2]))["secs"][0][3]:
        failures.append("self-test: the opening is not flagged as the preamble")

    # the contract's own numbering: contiguous from 1 passes, and the shapes a half-applied
    # renumbering or an overgrown chapter leave must not
    if numbering_problems([1, 2, 3, 4], "x"):
        failures.append("self-test: a contiguous run 1..4 was reported as a problem")
    if not numbering_problems([1, 2, 14, 15], "x"):
        failures.append("self-test: an eleven-beat hole in the outline was not reported")
    if not numbering_problems([2, 3, 4], "x"):
        failures.append("self-test: an outline starting at 2 was not reported")
    if numbering_problems(list(range(1, CAP + 1)), "x"):
        failures.append(f"self-test: a chapter of exactly {CAP} beats was reported as over the cap")
    if not numbering_problems(list(range(1, CAP + 2)), "x"):
        failures.append(f"self-test: a chapter of {CAP + 1} beats was not reported as over the cap")

    # the stale-number scan: the old form refused, the new one accepted
    for stale in ("Beats 12 and 41 print counts", "the outline moved beats 44–49", "beat 35"):
        if not GLOBAL_FORM.search(stale):
            failures.append(f"self-test: the scan accepts the book-wide form {stale!r}")
    for fine in ("<!-- beat make-it-move.3 -->", "beat make-it-move.3 is the poke step",
                 "the poke step", "beats named by what they are"):
        if GLOBAL_FORM.search(fine):
            failures.append(f"self-test: the scan refuses {fine!r}, which is the form it wants")

    return failures


def main() -> int:
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    order, grain, n_beats = reading_order(), [], 0
    # The guard is tested before it is trusted, on every run.
    problems = self_test()
    problems += global_form_problems()

    # The contract's own numbering, over the WHOLE outline whatever range was asked for: a chapter
    # with a hole or a thirteenth beat is a broken contract wherever it sits.
    for number, title, beats in outline_chapters():
        problems += numbering_problems(beats, f"chapter {number} ({title})")

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

        found = audit(slug, beats, path.read_text(encoding="utf-8"))
        secs = found["secs"]

        for h, b, n, pre in secs:
            if pre:
                continue        # the preamble is not a beat's worth of prose; see sections()
            if n > CEILING or not (BAND[0] <= n <= BAND[1]):
                grain.append((n, slug, h, b))

        note = []
        where = f"chapter {number} ({slug})"
        if found["unmarked"]:
            problems.append(f"{where}: {len(found['unmarked'])} section(s) carry no "
                            f"`<!-- beat {slug}.n -->` marker: {found['unmarked']}")
        if found["foreign"]:
            problems.append(f"{where}: marker(s) {found['foreign']} name another chapter, in this "
                            f"chapter's file — a beat's id carries the slug of the file it is in")
        if found["missing"]:
            problems.append(f"{where}: no section claims beat(s) "
                            f"{[f'{slug}.{n}' for n in found['missing']]}")
        if found["stray"]:
            problems.append(f"{where}: section claims beat(s) "
                            f"{[f'{slug}.{n}' for n in found['stray']]}, which the outline has not "
                            f"got under this chapter")
        if found["over_cap"]:
            problems.append(f"{where}: marker(s) {found['over_cap']} are past the cap of {CAP} "
                            f"beats in a chapter")
        if found["reordered"]:
            problems.append(f"{where}: the markers claim {found['run']}, which does not ascend")
        if found["scattered"]:
            problems.append(f"{where}: beat(s) {found['scattered']} are claimed again after a later "
                            f"beat — a split's sections are adjacent, so this is a section moved or "
                            f"relabelled")
        if found["splits"]:
            note.append(f"split: {[f'{slug}.{n}' for n in found['splits']]}")
        n_secs = sum(1 for *_, pre in secs if not pre)
        print(f"{number:>3}  {len(beats):>2} beats  {n_secs:>2} sections  {slug}"
              + (f"   ({'; '.join(note)})" if note else ""))

    over = [g for g in grain if g[0] > CEILING]
    print(f"\ngrain — band {BAND[0]}-{BAND[1]} words, hard ceiling {CEILING}")
    if not grain:
        print("  every section inside the band")
    for n, slug, h, b in sorted(grain, reverse=True, key=lambda g: (g[0], g[1], g[2])):
        mark = "  OVER THE CEILING" if n > CEILING else ""
        print(f"  {n:>4}  beat {b}  {slug} §{h}{mark}")
    if over:
        problems.append(f"{len(over)} section(s) over the {CEILING}-word hard ceiling")

    if problems:
        print("\n" + "\n".join("PROBLEM: " + p for p in problems))
        return 1
    print(f"\n{n_beats} beats in range. Every outline beat under a chapter's heading is claimed by "
          f"a marker in that chapter's own file, carrying that chapter's slug; the ids ascend from "
          f"1 with no gap and none is past {CAP}; a beat carried by two sections is named as a "
          f"split above and its sections are adjacent; and no file scanned still calls a beat by a "
          f"book-wide number. A section moved and relabelled together still ascends, so this is not "
          f"a statement about order — see the docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
