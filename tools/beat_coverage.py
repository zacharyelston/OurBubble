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

**And no book-wide beat number survives in any file this scans.** A number that used to be a beat's
name is now nobody's name, so the old form — `beat 35`, `beats 12 and 41`, and the schema `beat N`
a drafter would copy — is refused in every file listed in `SCANNED` below. That list is what the
pass line claims and all it claims: three files quote the old form deliberately and are left out
for that reason, and every other file outside the list is unscanned rather than clean. Prose names a beat by what it is; tooling and review notes name it `slug.n`.

**And an id that names nothing is refused too.** `make-it-move.99` and `no-such-chapter.3` were
possible in the first draft of this: `renumber_beats.py` is chapter-local by design and never edits
the sixteen cross-references the migration wrote, so a later insertion would strand them exactly the
way the book-wide numbering stranded everything. Every `slug.n` in a scanned file is resolved
against the outline.

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
# The number carries no leading zero, so `the-shape-between.03` is refused rather than read as 3.
MARKER = re.compile(
    r"^<!--[ \t]*beat[ \t]+([a-z0-9][a-z0-9-]*)\.([1-9]\d*)[ \t]*-->[ \t]*$", re.M)

# Anything still calling a beat by a book-wide number: `beat 35`, `Beats 12`, `beats 44–49`, and the
# schema `beat N` a drafter would copy out of a docstring. Matched over the WHOLE file, never line by
# line — a reviewer wrapped one sentence so that `…is beat` ended a line and `35` began the next, and
# a line-by-line scan passed it green in four files at once. This repository hard-wraps prose, so
# that is the likely shape rather than an exotic one.
#
# **The shape of the denylist, because a denylist's limit is only a limit if it is written down.**
# What it catches: any case of `beat`/`beats`, any run of spaces, a newline between the word and the
# number, and the literal `N`. What it does **not** catch, and a reader is the only guard on:
# `BEAT 35` in full capitals, `beat #35`, `beat number 35`, and a number written in words.
# Whitespace **or a hyphen**: `#beat-31` is a book-wide beat number wearing a deep link's clothes,
# and one sat in demos/DEMOS.md — the file whose own section is called *Nothing here knows a beat
# number* — through a whole renumber, because this looked for a space. A reader found it.
GLOBAL_FORM = re.compile(r"\b[Bb]eats?[\s-]+(?:\d+|N\b)")

# A beat id written in prose or in a comment. The hyphen is what tells it from a version string:
# every chapter slug has one, `python3.11` does not — and `slugs_are_hyphenated()` asserts that the
# first half of that stays true, because the day a chapter's slug has no hyphen every reference to
# it becomes invisible to this while the pass line still says it resolved.
#
# The lookbehind stops a match starting inside a longer id, where `make-it-move.3` would otherwise
# also read as `it-move.3`. An id hard-wrapped across a line break is joined before the scan runs
# (`unwrapped()`), the way the stale-form scan reads its whole file.
#
# **What it does not see, stated because a heuristic's limit is only a limit when it is written
# down:** an id whose slug is a single word; `Make-It-Move.9` in capitals; and `make-it-move.099`,
# which resolves as 99 — where `MARKER` refuses a leading zero outright.
ID_IN_PROSE = re.compile(r"(?<![\w-])([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\.(\d+)\b")

# What the scan reads, beside every `chapters/*.md`: the contract, the ledger, the standard, the
# canon, the art direction, the reader-facing README, the demos' own document and modules, the
# working note, the reviewer's skill, and the modules whose comments name a beat. No count of it is
# written down here — the pass line prints the length, and a count in a comment is one more number
# nothing guards.
#
# **Three files quote the book-wide form deliberately** and are left out for that reason:
# `beat_coverage.py` itself, `tools/attacks_beats.py` and `tools/migrate_beat_ids.py` all have to
# write the form down in order to refuse it or to migrate it. Every *other* file outside this list
# is simply unscanned — `record/`, which is a frozen copy of the engine and is derived rather than
# edited, most of all. The pass line says "no file scanned", not "no file", and that is the whole
# of what it claims.
SCANNED = (
    "OUTLINE.md",
    "CONTINUUM.md",
    "EDITION_STANDARD.md",
    "README.md",
    "CANON.md",
    "ART_DIRECTION.md",
    "demos/DEMOS.md",
    "demos/core.mjs",
    "demos/steps.mjs",
    "tools/canon.py",
    "notes/octahedron-crossing.md",
    ".claude/skills/proof-reader/SKILL.md",
    "gen_appendix.py",
    "preprocessor.py",
    "check_edition.py",
    "tools/octahedron.py",
    "tools/oracle.py",
    "tools/napkin_export.py",
    "tools/demo_steps.py",
    "tools/renumber_beats.py",
    "tools/reader_note.py",
)


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


def scanned_paths() -> list:
    return [ROOT / name for name in SCANNED] + sorted((ROOT / "chapters").glob("*.md"))


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def stale_form_problems(text: str, where: str) -> list[str]:
    """The book-wide form, anywhere in one file's text. **Pure.**

    Over the whole text rather than line by line, and that is the point: a space pattern matches a
    newline too, so
    a sentence hard-wrapped between the word and its number reads as `beat 35` to any human and read
    as nothing at all to the first version of this. Refusing rather than checking (EDITION_STANDARD
    rule 4): the question is not whether the right id is present somewhere, it is whether the wrong
    form is absent.
    """
    return [
        f"{where}:{line_of(text, found.start())}: writes "
        f"{' '.join(found.group(0).split())!r} — a book-wide beat number, which is nobody's name "
        f"any more. A beat is `slug.n` (make-it-move.3); prose names it by what it is"
        for found in GLOBAL_FORM.finditer(text)
    ]


def unwrapped(text: str) -> str:
    """A hyphen at the end of a line joined to the next, so a wrapped id reads as one id.

    The line numbers below are derived from this string, which is the source text with a `-\n` (or
    `-\r\n`) closed up — every other character is where it was, so a number counted from an offset
    is still the source's own line.
    """
    return re.sub(r"-\r?\n[ \t]*", "-", text)


def slugs_are_hyphenated(order: list[str]) -> list[str]:
    """`ID_IN_PROSE` finds an id by its slug's hyphen. This is that assumption, asserted."""
    bare = [slug for slug in order if "-" not in slug]
    return [f"chapters/SUMMARY.md lists {bare}, whose slug(s) carry no hyphen — every reference to "
            f"them in prose would be invisible to the id scan, which finds an id by exactly that "
            f"hyphen. Rename the chapter, or widen ID_IN_PROSE and its stated limits"] if bare else []


def unresolved_id_problems(text: str, where: str, sizes: dict[str, int]) -> list[str]:
    """Every `slug.n` in one file's text names a chapter the book has, and a beat that chapter has.

    The migration wrote sixteen cross-references into files `renumber_beats.py` is designed never to
    touch, so without this an insertion in *Make it move* would strand `make-it-move.9` in a comment
    silently — the failure #77 exists to end, moved from every file to sixteen. **Pure.**
    """
    problems = []
    text = unwrapped(text)
    for found in ID_IN_PROSE.finditer(text):
        slug, number = found.group(1), int(found.group(2))
        if slug not in sizes:
            problems.append(
                f"{where}:{line_of(text, found.start())}: names {found.group(0)}, and "
                f"chapters/SUMMARY.md has no chapter {slug}"
            )
        elif not 1 <= number <= sizes[slug]:
            problems.append(
                f"{where}:{line_of(text, found.start())}: names {found.group(0)}, and {slug} has "
                f"{sizes[slug]} beat(s)"
            )
    return problems


def global_form_problems(sizes: dict[str, int]) -> list[str]:
    """Both scans, over every file in `SCANNED` and every chapter. See the docstring on the three
    files that are not in it."""
    problems = []
    for path in scanned_paths():
        where = str(path.relative_to(ROOT))
        if not path.exists():
            problems.append(f"{where}: missing, and it is one of the files scanned for stale beat "
                            f"numbers and unresolvable ids")
            continue
        text = path.read_text(encoding="utf-8")
        problems += stale_form_problems(text, where)
        problems += unresolved_id_problems(text, where, sizes)
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

    # the stale-number scan: the old form refused, the new one accepted. The wrapped case is the
    # reviewer's (2026-09-04): the first version scanned line by line and passed it green.
    for stale in ("Beats 12 and 41 print counts", "the outline moved beats 44–49", "beat 35",
                  "a `<!-- beat N -->` marker", "the sentence ends in beat\n35 of the book",
                  "beat  35"):
        if not stale_form_problems(stale, "x"):
            failures.append(f"self-test: the scan accepts the book-wide form {stale!r}")
    for fine in ("<!-- beat make-it-move.3 -->", "beat make-it-move.3 is the poke step",
                 "the poke step", "beats named by what they are", "beats, and steps.json derives"):
        if stale_form_problems(fine, "x"):
            failures.append(f"self-test: the scan refuses {fine!r}, which is the form it wants")

    # the id resolver, on a book of one chapter with four beats
    sizes = {"make-it-move": 4}
    if unresolved_id_problems("see make-it-move.3 and make-it-move.4", "x", sizes):
        failures.append("self-test: the resolver refuses an id the chapter has")
    for bad in ("make-it-move.9", "no-such-chapter.1"):
        if not unresolved_id_problems(f"see {bad}", "x", sizes):
            failures.append(f"self-test: the resolver accepts {bad!r}, which names nothing")
    for fine in ("python3.11", "mdbook 0.4.35", "make-it-move.md"):
        if unresolved_id_problems(fine, "x", sizes):
            failures.append(f"self-test: the resolver reads {fine!r} as a beat id")
    # and it does not start a match inside a longer id
    found = unresolved_id_problems("beat%20make-it-move.3", "x", sizes)
    if found:
        failures.append(f"self-test: the resolver split an encoded id: {found}")

    return failures


def main() -> int:
    lo, hi = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv) > 2 else (0, 99)
    order, grain, n_beats = reading_order(), [], 0
    # The guard is tested before it is trusted, on every run.
    problems = self_test()

    # The contract's own numbering, over the WHOLE outline whatever range was asked for: a chapter
    # with a hole or a thirteenth beat is a broken contract wherever it sits.
    chapters = outline_chapters()
    for number, title, beats in chapters:
        problems += numbering_problems(beats, f"chapter {number} ({title})")

    # How many beats each chapter has, by slug — what an id in prose is resolved against.
    sizes = {order[number]: len(beats) for number, _, beats in chapters if number < len(order)}
    problems += slugs_are_hyphenated(order)
    problems += global_form_problems(sizes)

    # A chapter listed in the reading order with no block in the outline is never audited below,
    # and that is exactly the half-finished state of adding one: the file and the SUMMARY line
    # first, the outline block second. A reviewer walked a whole extra chapter, markers and all,
    # past the first version of this.
    numbered = {number for number, _, _ in chapters}
    for index, slug in enumerate(order):
        if slug == Path(ce.APPENDIX_FILE).stem:
            continue
        if index not in numbered:
            problems.append(f"chapters/{slug}.md is chapter {index} in chapters/SUMMARY.md and "
                            f"OUTLINE.md has no `## {index} · ` block for it, so its beats are "
                            f"checked by nothing")

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
          f"split above and its sections are adjacent; every chapter in chapters/SUMMARY.md has an "
          f"outline block; every chapter slug carries the hyphen the id scan finds an id by; and "
          f"across the {len(scanned_paths())} file(s) scanned — every chapter, plus the files "
          f"named at SCANNED, which also names the three it leaves out and why, and says that "
          f"every other file in the repository is unscanned rather than clean — no beat is called "
          f"by a book-wide number and every `slug.n` resolves to a beat the outline has. A "
          f"section moved and relabelled together still ascends, so this is not a statement about "
          f"order — see the docstring.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
