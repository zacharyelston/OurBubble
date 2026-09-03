#!/usr/bin/env python3
"""The napkin: the book's chapters 1–5 numbers, **rendered** from the engine while the page is built.

Chapters 1–4 live on one triangle, one tetrahedron, and the two shapes that tetrahedron is made of,
and every number in them is finger-countable — four dots, six lines, three differences, ten ticks,
and then a crossing that takes two of those ticks. Quoting such numbers from a record would be
theatre: the reader can check them on a napkin, so the book should do the same thing in front of her
rather than cite itself. Each `{{napkin:NAME}}` token in a chapter is replaced at build time by the
block this file renders, and every rendered block says so.

**This file computes nothing.** That changed on 2026-09-02, and it is the whole point of the change.
The arithmetic is UniForge's `napkin` crate — registered as `lab/napkin/0001`, 23 computations —
vendored under [`engine/`](../engine/PROVENANCE.md) and pinned by [`engine.lock`](../engine.lock)
the way `record/` is pinned. `tools/engine.py` reads it; this file turns it into tables. Before that
there were three implementations of one arithmetic — here, in `demos/core.mjs`, and in the crate —
and three implementations are three places a book can disagree with itself.

The Python that used to do the work is still in the repository, in `tools/oracle.py` and
`tools/octahedron.py`, and it has exactly one job left: `tools/engine_check.py` runs it on every
`make check` and requires its output to be **byte-identical** to what is vendored. The oracle became
the guard. The reader sees one engine.

**Everything is exact.** `fractions.Fraction` throughout, and each value is rendered by `number()`,
which refuses anything it cannot write down exactly and briefly. There is no floating point anywhere
in this file.

Chapter 4 is where the napkin runs out, on purpose, and that is its finding: the last of the shapes
bigger than one tetrahedron cannot be run at the chapters' own tick size at all. `number()` refusing
to print it is not a formatting problem — it is the chapter's point, arriving in the one place it
cannot be argued with.

**Every token asserts its own claim before it renders.** The loop sums are zero, the inside sum is
zero, the total is conserved — those are the *claims* the chapters make, so a token that cannot
demonstrate its claim raises and takes the build down with it. Those assertions read the vendored
data rather than a fresh computation, which makes them the last line of the engine's integrity
layer: an edited `engine/napkin.json` fails the hashes in `check_edition.py`, and if it somehow
reached a page it would fail here too, by name.

FIREWALL: the engine computes a toy DEC lattice. *Dot, line, face, inside, tick, slosh, poke,
crossing, stella, world* name features of that lattice, never claims about nature. See
`../FIREWALL.md`.
"""

from __future__ import annotations

import os
import re
import sys
from fractions import Fraction
from typing import Dict, List, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine  # noqa: E402  (needs the path above)

# ── the book's names ──────────────────────────────────────────────────────────────────────────────
#
# The one thing this file owns outright. Names are presentation: the engine calls the dots 0, 1, 2, 3
# and the book calls them A, B, C, D, and which is which is the book's decision, made once, here.

NAMES = ("A", "B", "C", "D")
VERTICES: Tuple[int, ...] = (0, 1, 2, 3)

# ── rendering ─────────────────────────────────────────────────────────────────────────────────────


def number(value: Fraction) -> str:
    """An exact, short decimal for `value`, or a refusal.

    The refusal is the point. Every number on these pages is meant to be checkable in the reader's
    head, so a value that needs more than a couple of decimal places is not a formatting problem —
    it means the arithmetic upstream drifted away from the napkin, and the build should stop and say
    so rather than print `2.9990234375` in a table about counting on your fingers.
    """
    # A real minus sign, everywhere, including inside table cells: these are reader-facing pages,
    # and a stray ASCII hyphen among typeset minus signs is exactly the kind of seam a proofreader
    # catches and a checker does not.
    sign = "−" if value < 0 else ""
    magnitude = abs(value)
    if magnitude.denominator == 1:
        return f"{sign}{magnitude.numerator}"
    if magnitude.denominator in (2, 4, 5, 10, 20, 100):
        text = f"{float(magnitude):.2f}".rstrip("0").rstrip(".")
        assert Fraction(text) == magnitude, f"{value} does not round-trip through {text!r}"
        return f"{sign}{text}"
    raise AssertionError(
        f"{value} is not finger-countable (denominator {value.denominator}). The napkin tables must "
        f"stay exact and short; change the tick size rather than the formatting."
    )


def signed(value: Fraction) -> str:
    """`+3` / `−4` — the difference from `number()` is only the explicit `+` on positives."""
    return f"+{number(value)}" if value >= 0 else number(value)


def edge_name(edge: Tuple[int, ...]) -> str:
    return "".join(NAMES[v] for v in edge)


def walk_terms(row: Sequence[int], values: Sequence[Fraction]) -> str:
    """The terms of one oriented loop, as a reader would write them down.

    Each term is the **product** of the incidence sign and the number on that piece — which is the
    bug this function exists to prevent. Printing the incidence sign next to the unsigned value gave
    `+3 −1 +4` for a loop that sums to zero: three terms that visibly do not, under a column headed
    with the right answer. A napkin whose arithmetic does not add up in front of the reader is worse
    than no napkin, so the signs are multiplied out here, once.
    """
    parts = []
    for index, sign in enumerate(row):
        if not sign:
            continue
        term = sign * values[index]
        parts.append(signed(term))
    return " ".join(parts)


def footnote(what: str) -> str:
    return f"\n*computed while this page was built — {what}.*\n"


CAPTION_CEILING = 70


def block(name: str, body: str, what: str) -> str:
    """One rendered token, fenced by comments that mark exactly where the computed span begins.

    The fence is load-bearing, not decoration: `check_edition.py` uses it to bound the
    computed-on-build exemption to this span and nothing else, so a bold number the *narrative*
    emphasises is still governed by the appendix-anchoring rule.
    """
    # A caption is a caption. It was the one surface with no ceiling on it — the grain band counts a
    # chapter's prose and sees `{{napkin:NAME}}` as one word — and a caption grew to 118 words and
    # spent the following section's whole reveal in small italics before anyone measured it (a
    # proofreader, 2026-09-02). The cap is above every caption in the book, so it costs nothing
    # except the next one that tries to do a section's work.
    length = len(what.split())
    assert length <= CAPTION_CEILING, (
        f"{name}: the caption is {length} words, over the {CAPTION_CEILING}-word ceiling — a "
        f"caption states what was computed; it does not carry the section's argument"
    )
    return (
        f"<!-- napkin:{name} -->\n\n{body.strip()}\n{footnote(what)}\n<!-- /napkin:{name} -->"
    )
def fraction_text(value: Fraction) -> str:
    """An exact fraction as a fraction — `2/3`, `2/5` — for the values `number()` rightly refuses.

    `number()` writes a short decimal or nothing, which is the correct rule for a table of a run: a
    value it cannot write is a sign the arithmetic left the napkin. A *tick size* is different. Two
    thirds is exactly as checkable as a half and it has no short decimal, so refusing it would push
    the chapter into rounding a number the reader is meant to be able to verify. The round-trip is
    asserted, so this cannot quietly print something else.
    """
    text = (f"{value.numerator}/{value.denominator}" if value.denominator != 1
            else str(value.numerator))
    assert Fraction(text) == value, f"{value} does not round-trip through {text!r}"
    return text


# Every worded fraction the captions use, and nothing else. Two rules come with this table, both
# learned the hard way one round apart (a proofreader, 2026-09-02):
#
#   * **it is pinned to literals below**, because a lookup is not a derivation. `fraction_text`
#     round-trips its own output (`Fraction("1/8") == 1/8`); words cannot be parsed back that
#     honestly, so the check is a written-out pin next to the entry. Without it, editing
#     `Fraction(1, 8): "an eighth"` to `"a sixth"` renders "a sixth" over a table saying `1/8` and
#     every check agrees, because `in_caption` compares the caption against the same corrupted
#     lookup — the `stella_in_its_cube` shape, one round later, in the fix for it;
#   * **nothing dead lives here.** It held eight entries of which two were reached, including
#     "half again" for 3/2, which is not a reading of 3/2 on its own. An unused value with an
#     assertion beside it is cover for whatever the next author does with it, which is exactly why
#     `stella_runaway`'s spare denominators were deleted rather than guarded.
#
# A caption that needs a new worded fraction adds the entry AND its pin, in the same commit.
FRACTION_WORDS = {
    Fraction(1, 2): "half",
    Fraction(1, 8): "an eighth",
}

assert FRACTION_WORDS[Fraction(1, 2)] == "half", "a half is not called 'half' any more"
assert FRACTION_WORDS[Fraction(1, 8)] == "an eighth", "an eighth is not called 'an eighth'"
assert len(FRACTION_WORDS) == 2, (
    "FRACTION_WORDS has grown or shrunk: pin every entry to a literal above, and keep no entry no "
    "caption reaches"
)
assert {fraction_text(value) for value in FRACTION_WORDS} == {"1/2", "1/8"}, (
    "the worded fractions and their digit forms have come apart"
)


def fraction_words(value: Fraction) -> str:
    """A small fraction in words — `an eighth`, `half` — for prose that reads better that way.

    `fraction_text` gives `1/8`, which is right in a table cell and wrong in a sentence: making a
    caption fidelity-checked turned "an eighth of it each … exactly half" into "1/8 … 1/2" four
    lines above prose still saying "an eighth" (a proofreader, 2026-09-02). The same fact in two
    registers is a stumble, and a caption is prose. The table keeps the digits; the caption gets the
    words; both come from the same value, and the words are pinned where they are written down.
    """
    assert value in FRACTION_WORDS, (
        f"{value} has no worded form here — add it to FRACTION_WORDS with its pin rather than "
        f"writing it out in a caption, or use fraction_text() and let the sentence carry the digits"
    )
    return FRACTION_WORDS[value]


def _thousands(count: int) -> str:
    return f"{count:,}"


SMALL_WORDS = ("no", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
               "ten", "eleven", "twelve")


def word(count: int) -> str:
    """A small count as a word, for prose that must not carry a typed numeral.

    A sentence like "they fall into four groups of three" is a claim about numbers the token just
    computed, and the first version of it typed both and got one wrong — it said "four and four"
    over a table showing three lines per face (a proofreader, 2026-09-02). Built from the counts
    instead, it cannot disagree with them.
    """
    assert 0 <= count < len(SMALL_WORDS), f"{count} is not a small count"
    return SMALL_WORDS[count]


def shows_each(name: str, fragment: str, pairs: Sequence[Tuple[str, Fraction]]) -> None:
    """Every labelled cell in rendered text carries ITS OWN number, and the text carries no others.

    `shows_exactly` compares a sorted multiset, so a permutation is invisible: swap two arrows
    between lines and the same numbers are all still present (a proofreader, 2026-09-02). The page
    then disagrees with itself between two adjacent tables — under a sentence inviting the reader to
    check exactly that. So each cell is matched against the line it names.
    """
    for label, value in pairs:
        cell = f"{label} **{number(value)}**"
        assert cell in fragment, (
            f"{name}: the rendered text does not carry {cell!r} — a number is against the wrong "
            f"name, or was typed instead of taken from the data"
        )
    found = re.findall(r"\*\*(−?[\d.]+)\*\*", fragment)
    assert len(found) == len(pairs), (
        f"{name}: the rendered text shows {len(found)} emphasised numbers for {len(pairs)} pieces "
        f"of data"
    )


def shows_exactly(name: str, fragment: str, expected: Sequence[Fraction]) -> None:
    """Scrape the emphasised numbers out of rendered text and match them against the data.

    `carries()` compares the page against strings built the same way the page was, so it catches a
    literal typed into the text and misses a rewritten *builder* — retype every arrow in one table
    and the check retypes with it. This closes that by reading the rendered characters back with a
    regular expression and comparing the multiset to the numbers the arithmetic holds. It is the one
    check here that does not trust the code that wrote the line.
    """
    found = sorted(re.findall(r"\*\*(−?[\d.]+)\*\*", fragment))
    want = sorted(number(value) for value in expected)
    assert found == want, (
        f"{name}: the rendered table shows {found} where the arithmetic holds {want} — a number was "
        f"typed into the text instead of being taken from the data"
    )


#: What a token's own caption may not say, whatever else it says. `REFUSED_IN_PROSE` holds a
#: chapter to its tokens' arithmetic; this holds a caption to its own, and it exists because a pin
#: on the caption's *verdict words* is not enough on its own: leave the pinned words in place and
#: append a contradicting clause — "the pair never returns … though it comes home every four after
#: that" — and every check stays green (a proofreader, tranche D round 2). A pin says the right
#: words are present. This says the wrong ones are not.
REFUSED_IN_CAPTION: Dict[str, List[str]] = {}


def refuse_in_caption(name: str, *phrases: str) -> None:
    """Register phrasings this token's caption may not contain, for `checked_block` to enforce.

    Registered from inside the token, because what is refused depends on what the engine returned:
    a run with no period may not say it comes home, and one with a period may not say it never
    does. The refusal is therefore a function of the data rather than a constant.
    """
    REFUSED_IN_CAPTION[name] = list(phrases)


def checked_block(name: str, body: str, what: str,
                  in_caption: Dict[str, str] | None = None, **values: str) -> str:
    """Render a token, and check the block AND the caption each carry the numbers they claim.

    Two scopes, because one was not enough twice over. `values` must appear anywhere in the block —
    that is the table's rule. `in_caption` must appear **in the caption itself**, which is the rule
    the first version missed: a caption saying "a sixth" passed a whole-block check because `1/8`
    was in the table three lines above it, and a caption saying "Only 7 rows" passed because `3` was
    in a cell somewhere (a proofreader, 2026-09-02, twice). A claim is only checked where it is
    made.
    """
    text = block(name, body, what)
    carries(name, text, **values)
    if in_caption:
        carries(f"{name}'s caption", what, **in_caption)
    lowered = what.casefold()
    for phrase in REFUSED_IN_CAPTION.get(name, []):
        assert phrase.casefold() not in lowered, (
            f"{name}'s caption says {phrase!r}, which this token's own arithmetic refuses — see "
            f"napkin.REFUSED_IN_CAPTION"
        )
    return text


def carries(name: str, body: str, **values: str) -> str:
    """Assert the rendered text actually contains the values that were computed. Returns `body`.

    Why this exists, in the words of the attack that found it (a proofreader, 2026-09-02): the
    tokens "assert their *inputs* and render their *outputs*, and nothing checks that the rendered
    characters are the computed values". Editing a literal `11` into a table whose census says 10
    left every check green, because every assertion was about the census and none was about the
    page. A token that says "computed while this page was built" is making a claim about the
    characters on the page, so the characters are what this checks.
    """
    for label, value in values.items():
        assert value in body, (
            f"{name}: the rendered block does not contain the computed {label} ({value!r}) — a "
            f"number was typed into the text instead of being taken from the arithmetic"
        )
    return body


# ── the tokens ────────────────────────────────────────────────────────────────────────────────────
#
# Every value below is read from the vendored engine. The constants the chapters carry — the corner
# values 2, 5, 1, 4; the six freely chosen arrows; the tick size 1/2; ten ticks — are the engine's
# choices and arrive with its data, so they are named by where they came from rather than restated
# here. A token that wanted a different tick size would be asking for a different register row.


def tetra_counts() -> str:
    counts = engine.tetrahedron()["counts"]
    census = (counts["dots"], counts["lines"], counts["faces"], counts["insides"])
    assert census == (4, 6, 4, 1), f"the tetrahedron's census came out {census}"
    body = (
        "| dots | lines | faces | solid inside |\n"
        "|---|---|---|---|\n"
        f"| {census[0]} | {census[1]} | {census[2]} | {census[3]} |"
    )
    return block("tetra_counts", body,
                 "the tetrahedron's census, and that walking the boundary comes home to zero twice "
                 "over — round each face, and round the solid inside")


def triangle_loop_example() -> str:
    triangle = engine.triangle()
    values = triangle["values"]
    steps = triangle["steps"]
    assert triangle["sum"] == 0, f"the triangle's loop sum came out {triangle['sum']}"
    assert sum(difference for _, _, difference in steps) == 0, (
        "the three differences do not add to the sum the engine reported"
    )

    rows = "\n".join(
        f"| {a} → {b} | {number(values[NAMES.index(b)])} − {number(values[NAMES.index(a)])} | "
        f"{signed(difference)} |"
        for a, b, difference in steps
    )
    body = (
        f"Corners: **{NAMES[0]} = {number(values[0])}**, **{NAMES[1]} = {number(values[1])}**, "
        f"**{NAMES[2]} = {number(values[2])}**.\n\n"
        "| step | arithmetic | difference |\n|---|---|---|\n"
        f"{rows}\n"
        f"| **all the way round** | {signed(steps[0][2])} {signed(steps[1][2])} "
        f"{signed(steps[2][2])} | **0** |"
    )
    return block("triangle_loop_example", body,
                 "the three differences on one triangle and their sum, from the corner values 2, 5, 1")


def tetra_face_loops() -> str:
    complex4 = engine.complex_on(4)
    tetra = engine.tetrahedron()
    values = tetra["corners"]
    differences = tetra["differences"]
    loops = tetra["face_loops"]
    assert all(loop == 0 for loop in loops), f"a face loop came out non-zero: {loops}"

    corner_text = ", ".join(f"**{name} = {number(values[i])}**" for i, name in enumerate(NAMES))
    line_rows = " | ".join(tetra["line_names"])
    diff_rows = " | ".join(signed(d) for d in differences)
    face_rows = "\n".join(
        f"| {face} | {walk_terms(complex4['d1'][index], differences)} | "
        f"**{number(loops[index])}** |"
        for index, face in enumerate(tetra["face_names"])
    )
    body = (
        f"Corners: {corner_text}.\n\n"
        f"| line | {line_rows} |\n"
        f"|---|{'---|' * len(tetra['line_names'])}\n"
        f"| difference | {diff_rows} |\n\n"
        "| face | its three line-numbers | loop, walked round |\n|---|---|---|\n"
        f"{face_rows}"
    )
    return block("tetra_face_loops", body,
                 "the six differences on one tetrahedron and each face's loop sum, from the corner "
                 "values 2, 5, 1, 4")


def tetra_inside_sum() -> str:
    complex4 = engine.complex_on(4)
    tetra = engine.tetrahedron()
    arrows = tetra["arrows"]
    face_numbers = tetra["face_numbers"]
    outward = tetra["outward_face_numbers"]

    assert all(value != 0 for value in face_numbers), (
        f"a face came out zero ({face_numbers}), so the inside sum would demonstrate less than it "
        f"claims — the six line-numbers must not be differences of corner values"
    )
    assert tetra["inside_sum"] == 0, f"the inside sum came out {tetra['inside_sum']}"

    line_rows = " | ".join(tetra["line_names"])
    arrow_rows = " | ".join(number(a) for a in arrows)

    # K36 (proofread, tranche A round 2): the chapter tells the reader she can do this check with a
    # pencil, and the appendix now promises the arithmetic is shown. So show it. Each face is walked
    # the same way round as seen from OUTSIDE the tetrahedron, which is the orientation that makes
    # every line get walked once in each direction — the reason the grand total is zero. Printing
    # the walk makes both the direction and the sum checkable instead of inferred.
    # Each face is shown walked the way the boundary operator actually takes it — outward. Where the
    # incidence carries a minus, the face is displayed walked the other way round and its number
    # negated, which is the same arithmetic and removes the alternating-sign convention from the
    # reader's side of it: all four displayed numbers then simply add.
    walk_rows = []
    for index, face in enumerate(tetra["face_names"]):
        sign = tetra["inside_incidence"][index]
        row = [sign * value for value in complex4["d1"][index]]
        letters = list(face)
        cycle = letters if sign > 0 else [letters[0], letters[2], letters[1]]
        assert outward[index] == sign * face_numbers[index], (
            f"the engine's outward face-number for {face} is not its face-number walked the way "
            f"the boundary takes it"
        )
        walk_rows.append(
            f"| {' → '.join(cycle + [cycle[0]])} | {walk_terms(row, arrows)} | "
            f"**{number(outward[index])}** |"
        )
    walk_table = "\n".join(walk_rows)
    assert sum(outward) == 0, f"the four outward face-numbers came to {sum(outward)}"
    outward_terms = " ".join(
        (f"+{number(v)}" if v > 0 else f"−{number(-v)}") for v in outward
    ).lstrip("+")

    body = (
        "This time the six line-numbers are given, not worked out from the corners — six arrows in "
        "their own right. So a face's loop need not be zero, and it is not:\n\n"
        f"| line | {line_rows} |\n"
        f"|---|{'---|' * len(tetra['line_names'])}\n"
        f"| arrow | {arrow_rows} |\n\n"
        "Each face below is walked the same way round as seen from outside, which is what makes the "
        "two faces meeting along any line walk that line in opposite directions:\n\n"
        "| walked | its three arrows, signed | how much goes round it |\n"
        "|---|---|---|\n"
        f"{walk_table}\n\n"
        f"Now just add the four up: {outward_terms} = **0**."
    )
    return block("tetra_inside_sum",
                 body,
                 "four non-zero face-numbers from six freely chosen line-numbers, each face's walk "
                 "shown, and their oriented sum around the inside")


def _slosh_body(history: Sequence[Sequence[Fraction]]) -> str:
    head = " | ".join(NAMES)
    rows = []
    for tick, row in enumerate(history):
        cells = " | ".join(number(v) for v in row)
        rows.append(f"| {tick} | {cells} | **{number(sum(row))}** |")
    return (
        f"| tick | {head} | total |\n"
        f"|---|{'---|' * len(NAMES)}---|\n" + "\n".join(rows)
    )


def slosh_table() -> str:
    motion = engine.motion()
    history = motion["plain"]["history"]
    repeat = motion["plain"]["period"]
    assert repeat, "the run did not repeat within the ticks computed"
    total = sum(history[0])
    for tick, row in enumerate(history):
        assert sum(row) == total, (
            f"the total changed at tick {tick}: {sum(row)} ≠ {total} — this rule conserves it"
        )
    body = _slosh_body(history)
    return block("slosh_table", body,
                 f"the one rule, run {motion['ticks']} ticks from rest on one tetrahedron with "
                 f"every line counting the same; the total is conserved exactly, and with nothing to "
                 f"damp it and no room to spread into the world never settles — at this step size it "
                 f"comes back to its start every {repeat} ticks")


def slosh_table_dialed() -> str:
    motion = engine.motion()
    history = motion["dialed"]["history"]
    plain = motion["plain"]["history"]
    dialed = motion["dialed_line"]

    assert history != plain, "doubling a line changed nothing — the dial is not wired up"
    assert sum(history[0]) == sum(plain[0]), "the two runs must start from the same total"

    # The level the four numbers average to is the one thing the dial must NOT move: it is fixed by
    # the conserved total, not by the weights. Asserted rather than asserted-in-prose.
    average = Fraction(sum(history[0]), len(NAMES))
    for tick, row in enumerate(history):
        assert Fraction(sum(row), len(row)) == average, f"the average moved at tick {tick}"

    body = _slosh_body(history)
    return block("slosh_table_dialed", body,
                 f"the same {motion['ticks']} ticks with line {dialed} counted double and "
                 f"every other line counting one — the dial, on one line. The total is still "
                 f"conserved exactly and the four numbers still average to {number(average)}; what "
                 f"changed is the motion, now faster along {dialed} than the rest")


# ── the triangle, moving: the smallest thing the rule can be run on at all ────────────────────────
#
# Register row R07, added for the owner's pace change of 2026-09-02: the rule runs on THREE numbers
# before four. The row's own finding is why there are two tokens here rather than one. The
# tetrahedron's table comes out in whole numbers because at the book's tick the coefficient the rule
# multiplies by is exactly zero for that shape; the triangle's is not, and at the same tick its
# denominators double every tick until `number()` refuses the third row. The tick that does the same
# thing for the triangle is two thirds. So the tick is a property of the SHAPE, and that is a beat.
#
# Both tokens read `engine/rows.json`'s `triangle_motion` group and compute nothing. The corner
# values 2, 5, 2 are the engine's choice and arrive with its data.

TRIANGLE_NAMES = NAMES[:3]


def _triangle_rows(history: Sequence[Sequence[Fraction]], upto: int | None = None) -> str:
    """The run as a table: one row per tick, with the total that never moves in the last column."""
    rows = []
    for tick, row in enumerate(history if upto is None else history[:upto]):
        cells = " | ".join(number(value) for value in row)
        rows.append(f"| {tick} | {cells} | **{number(sum(row))}** |")
    return (
        f"| tick | {' | '.join(TRIANGLE_NAMES)} | total |\n"
        f"|---|{'---|' * len(TRIANGLE_NAMES)}---|\n" + "\n".join(rows)
    )


def _triangle_conserved(name: str, run: Dict[str, object]) -> Fraction:
    """The total is the same on every tick, and it is the total the engine reported. Returns it."""
    history = run["history"]
    total = sum(history[0])
    for tick, row in enumerate(history):
        assert sum(row) == total, (
            f"{name}: the total changed at tick {tick} ({sum(row)} ≠ {total}) — this rule conserves it"
        )
    assert list(run["totals"]) == [total] * len(history), (
        f"{name}: the engine's own totals column does not match the rows it sits beside"
    )
    return total


def triangle_slosh_table() -> str:
    run = engine.triangle_motion()
    corners = run["corners"]
    good = run["at_two_thirds"]
    history = good["history"]
    total = _triangle_conserved("triangle_slosh_table", good)

    assert good["k"] == Fraction(2, 3), f"the triangle was run at {good['k']}, not two thirds"
    assert good["period"] == 4, f"the run repeats every {good['period']} ticks, not four"
    assert good["printable_rows"] == len(history), (
        f"only {good['printable_rows']} of {len(history)} rows can be written down, so this table "
        f"is not the whole-numbered one the chapter claims"
    )
    assert all(value.denominator == 1 for row in history for value in row), (
        "a value in the triangle's run is not a whole number"
    )
    # The pair, not the row, is what the rule reads — so "back where it started" is a claim about
    # two rows, and it is checked as one: the pair at tick `period` is the pair at tick 0.
    assert history[good["period"]] == history[0] and history[good["period"] - 1] == history[0], (
        "the pair (then, now) at the repeat is not the pair the run started from"
    )
    assert list(corners) == list(history[0]), "the run does not start from the corners it names"

    start = ", ".join(f"{name} = **{number(corners[index])}**"
                      for index, name in enumerate(TRIANGLE_NAMES))
    shows_each("triangle_slosh_table's corners", start,
               [(f"{name} =", corners[index]) for index, name in enumerate(TRIANGLE_NAMES)])
    body = (
        f"Three corners: {start}. Started **at rest**, which means the pair the rule reads is one "
        f"row twice over — *then* and *now* both {' · '.join(number(v) for v in history[0])}.\n\n"
        + _triangle_rows(history)
    )
    return checked_block(
        "triangle_slosh_table", body,
        f"the one rule on a triangle at the triangle's own tick of "
        f"{fraction_text(good['k'])}, from the corners "
        f"{', '.join(number(value) for value in corners)}: {word(len(history))} rows, every value a "
        f"whole number, the total {number(total)} on every tick, and back to the pair it started "
        f"from every {word(good['period'])} ticks",
        corners=start, first=_triangle_rows(history, 1),
        home=f"| {good['period']} | " + " | ".join(number(v) for v in history[good["period"]]),
        in_caption={"tick": f"tick of {fraction_text(good['k'])}",
                    "rows": f"{word(len(history))} rows",
                    "total": f"the total {number(total)}",
                    "period": f"every {word(good['period'])} ticks"})


def no_room() -> str:
    """Register row R10 — every dot of the tetrahedron is one line from every other.

    Added after a proofread (tranche D) found the one beat of chapter 3 with no arithmetic under it,
    in the chapter that had spent eleven beats teaching the reader to expect some. The claim the
    section makes is *there is nowhere further away than anywhere else*, and that is a table.
    """
    room = engine.no_room()
    hops = room["hops"]
    assert room["dots"] == len(NAMES), f"the hop table is on {room['dots']} dots, not four"
    assert room["diameter"] == 1, f"the tetrahedron's diameter came out {room['diameter']}"
    for here, row in enumerate(hops):
        for there, count in enumerate(row):
            assert count == (0 if here == there else 1), (
                f"{NAMES[here]} is {count} hops from {NAMES[there]} — on this object every pair is "
                f"one, which is the whole of what the section claims"
            )
    rows = "\n".join(
        f"| from {NAMES[here]} | " + " | ".join("—" if here == there else str(count)
                                                for there, count in enumerate(row)) + " |"
        for here, row in enumerate(hops)
    )
    body = (
        f"| lines to cross | {' | '.join(NAMES)} |\n"
        f"|---|{'---|' * len(NAMES)}\n{rows}"
    )
    return checked_block(
        "no_room", body,
        f"how many lines you must cross to get from each dot of the tetrahedron to each other dot: "
        f"{word(room['diameter'])}, in every case. The furthest anything is from anything is a "
        f"single line, so there is no further away for a ring to spread into",
        table=rows, diameter=f"{word(room['diameter'])}, in every case",
        in_caption={"diameter": f"{word(room['diameter'])}, in every case",
                    "what": "each other dot"})


def tick_belongs_to_shape() -> str:
    run = engine.triangle_motion()
    wrong = run["at_the_book_tick"]
    history = wrong["history"]
    printable = wrong["printable_rows"]
    total = _triangle_conserved("tick_belongs_to_shape", wrong)
    tetra_tick = engine.motion()["k"]
    ceiling = engine.refusal()["ceilings"][0]
    bound = ceiling["bound"]

    assert wrong["k"] == tetra_tick, (
        f"this run is at {wrong['k']}, not the tick the tetrahedron uses ({tetra_tick})"
    )
    assert wrong["period"] == 0, (
        f"the run comes home every {wrong['period']} ticks after all, so the tick is not wrong for "
        f"this shape in the way the section says"
    )
    # K7 (proofread, tranche D): the verdict was written out by hand in both the block and the
    # caption, so a caption claiming the opposite of the period the token had just asserted passed
    # every check. It is built from the period now — and, because building a caption from a variable
    # is not enough on its own (rewrite the builder and the caption and the check move together),
    # the WORDS are pinned to the number, the way FRACTION_WORDS' entries are.
    homing = ("the pair never returns to the pair it started from" if wrong["period"] == 0
              else f"the pair returns every {word(wrong['period'])} ticks")
    assert ("never returns" in homing) == (wrong["period"] == 0), (
        f"this block's verdict is {homing!r} while the engine's period is {wrong['period']} — a run "
        f"that never comes home says 'never returns', and one that does says how often"
    )
    # The refusal is the result, so it is exercised rather than assumed: the row after the last
    # printable one must be a row `number()` will not write.
    refused = False
    try:
        number(history[printable][0])
    except AssertionError:
        refused = True
    assert refused, (
        f"row {printable} writes down after all — the engine says {printable} rows print, and this "
        f"table's whole point is the one that does not"
    )
    assert ceiling["dots"] == 4 and ceiling["holds"], (
        "the first ceiling is no longer the four-dot shape's, or it no longer holds"
    )
    assert bound == Fraction(engine.refusal()["leapfrog_bound"], 1) / ceiling["stiffest"], (
        "the four-dot ceiling is not four over its stiffest mode"
    )
    assert tetra_tick < bound, "the tick the next section uses is not under the ceiling after all"
    # K1 (proofread, tranche D): the block said the next row "cannot be put on a napkin at all", and
    # the reader worked it out — 3.125, 2.75, 3.125 — in the paragraph asking her to stop. The true
    # statement is the one the engine actually enforces (a couple of decimal places) plus the reason
    # it never recovers, and the reason is asserted here rather than asserted in prose.
    for tick, row in enumerate(history):
        widest = max(value.denominator for value in row)
        assert widest == 2 ** tick, (
            f"at tick {tick} the widest denominator is {widest}, not {2 ** tick} — the doubling the "
            f"block tells the reader to expect is not what this run does"
        )
    # "the numbers stay small" is a claim about the whole run and not only the rows shown, so it is
    # measured over every tick the engine computed rather than left to the reader's eye.
    biggest = max(abs(value) for row in history for value in row)
    assert biggest <= total, (
        f"a value reached {biggest}, past the conserved total {total} — this run is not the bounded "
        f"one the section contrasts with the runaway"
    )

    # Whatever else this caption says, it may not say the run comes home: the engine's period is 0.
    refuse_in_caption("tick_belongs_to_shape",
                      *(("comes home", "returns every", "repeats every")
                        if wrong["period"] == 0 else ("never returns", "never comes home")))

    body = (
        f"The same three numbers and the same rule, at {fraction_text(tetra_tick)} — the tick the "
        f"tetrahedron uses in the next section:\n\n"
        + _triangle_rows(history, printable)
        + f"\n\nNothing is running away: the total is still {number(total)} on every tick, and over "
          f"all {word(wrong['ticks'])} ticks the rule was run no number anywhere in it grew bigger "
          f"than that total. What stops is the writing down. These tables only ever print a value "
          f"that fits in a couple of decimal places, and the row after the last one above does not "
          f"— nor does any row after it, because the halves become quarters, the quarters eighths, "
          f"and the denominator doubles every tick from here on. And {homing}.\n\n"
        + f"The shape decides one more thing about the tick: a size it has to stay under. For the "
          f"{word(ceiling['dots'])}-dot tetrahedron that is {fraction_text(bound)}, and the number "
          f"it is worked out from is certified in whole numbers, with no decimal anywhere in it."
    )
    return checked_block(
        "tick_belongs_to_shape", body,
        f"the triangle's three numbers at the tetrahedron's tick of "
        f"{fraction_text(tetra_tick)}: the total {number(total)} still never moves and no number "
        f"grows past it, but only {word(printable)} rows fit in a couple of decimal places, and "
        f"{homing} — and the tick the {word(ceiling['dots'])}-dot shape must stay under is "
        f"{fraction_text(bound)}",
        tick=fraction_text(tetra_tick), rows=_triangle_rows(history, printable),
        bound=fraction_text(bound), verdict=homing,
        in_caption={"tick": f"tick of {fraction_text(tetra_tick)}",
                    "rows": f"only {word(printable)} rows",
                    "total": f"the total {number(total)}",
                    "verdict": homing,
                    "bound": f"must stay under is {fraction_text(bound)}"})


# ── the object one dimension out: how many kinds of place are there? ──────────────────────────────
#
# Chapters 1–3 never leave one tetrahedron. Chapter 4 has to, because she asks for room, and the
# answer to "do tetrahedra fill space?" is no — so the book has to say what was built instead. The
# engine builds it: `mesh_3d_chiral_tetoct_periodic` with `chiral_oct_screw111`, in `core/geom`, and
# `napkin::kinds_of_place` counts the arrangements of line-directions around each dot.
#
# The whole point of the token is the CONTROL. "Three kinds of place" means nothing on its own; it
# means something next to "cut every hole the same way and there is one kind of place". Same
# builder, same lattice, one line different — and both runs are vendored.


def vertex_classes() -> str:
    kinds = engine.kinds_of_place()
    dots = kinds["dots"]
    screw = kinds["screw"]
    control = kinds["control"]
    bigger = kinds["bigger"]

    assert screw["kinds"] == 3, f"the twisting rule gave {screw['kinds']} kinds of place, not 3"
    assert screw["sizes"] == [dots // 3] * 3, f"the three kinds are not equal thirds: {screw['sizes']}"
    assert sum(screw["sizes"]) == dots, f"{sum(screw['sizes'])} dots classified, expected {dots}"
    assert control["kinds"] == 1, (
        f"cutting every hole the same way gave {control['kinds']} kinds, not 1"
    )
    assert control["sizes"] == [dots], (
        f"the control's single kind does not hold every dot: {control['sizes']}"
    )
    assert control["degree"] == screw["degree"] == 14, (
        "the two cuts do not give every dot the same number of lines, so the comparison is not one"
    )

    # A bigger world must agree, or 6 was too small to see the truth rather than the wrap.
    assert bigger["kinds"] == 3, f"the {bigger['side']}³ world gave {bigger['kinds']} kinds, not 3"
    assert bigger["sizes"] == [kinds["bigger_dots"] // 3] * 3, (
        f"the bigger world is not in thirds: {bigger['sizes']}"
    )

    body = (
        "| how the holes are cut | kinds of place | how the dots divide |\n"
        "|---|---|---|\n"
        f"| all the same way | **{control['kinds']}** | all {dots} alike |\n"
        f"| turning by a third each step | **{screw['kinds']}** | "
        f"{' · '.join(str(size) for size in screw['sizes'])} — exact thirds |"
    )
    return block("vertex_classes", body,
                 f"the object built on a {screw['side']}×{screw['side']}×{screw['side']} wrapped "
                 f"world — every dot has {screw['degree']} lines either way, and the only difference "
                 f"is the cut: cut every hole alike and every dot stands in the same arrangement, "
                 f"turn the cut by a third each step and there are exactly three, in equal thirds "
                 f"(confirmed unchanged on a {bigger['side']}³ world)")



# ── the shape between: cut the one tetrahedron and look at what is left ──────────────────────────
#
# Chapters 1–3 never leave one tetrahedron, and the chapter after them needs room. The cheapest room
# is not more tetrahedra: it is *inside* the one she has. Mark the middle of each of its six lines,
# cut, and four half-size tetrahedra come off the tips leaving one octahedron between them — the
# owner's finding, and the object the record's tiling turns out to be full of.
#
# The `cut`, `poke`, `face_sum`, `stella` and `refusal` groups of `engine/napkin.json` are register
# rows R11–R18. Nothing below computes any of it; each token renders numbers the engine already
# asserted, and re-asserts the handful of them the chapter's sentences actually lean on, so a claim
# cannot survive here after stopping being true over there.


def octa_cut() -> str:
    cut = engine.cut()
    assert (cut["dots"], cut["tips"], cut["octahedra"]) == (10, 4, 1), (
        f"the cut gave {cut['dots']} dots, {cut['tips']} tips and {cut['octahedra']} octahedra"
    )
    assert cut["tip_share"] == Fraction(1, 8) and cut["core_share"] == Fraction(1, 2), (
        "the tips are not eighths, or the shape between them is not half"
    )
    assert cut["tips"] * cut["tip_share"] + cut["core_share"] == 1, (
        "the pieces do not account for the whole tetrahedron"
    )
    body = (
        "| what falls out | how many | how big |\n"
        "|---|---|---|\n"
        f"| dots — the 4 corners and the 6 middles | **{cut['dots']}** | — |\n"
        f"| tetrahedra, one at each tip | **{cut['tips']}** | "
        f"half the side, {fraction_text(cut['tip_share'])} of the whole |\n"
        f"| the shape left between them | **{cut['octahedra']}** | "
        f"{fraction_text(cut['core_share'])} of the whole |\n\n"
        f"Its eight faces divide in two: **{len(cut['faces_at_a_tip'])}** look straight at a tip "
        f"({' · '.join(cut['faces_at_a_tip'])}), and **{len(cut['faces_in_a_face'])}** lie flat in "
        f"a face of the tetrahedron you cut ({' · '.join(cut['faces_in_a_face'])})."
    )
    return checked_block(
        "octa_cut", body,
        f"one tetrahedron cut at the middles of its six lines: the {word(cut['tips'])} tips are "
        f"{fraction_words(cut['tip_share'])} of it each and the shape between them is exactly "
        f"{fraction_words(cut['core_share'])}, so the {word(cut['tips'] + cut['octahedra'])} pieces "
        f"account for all of it",
        in_caption={"tip_share": fraction_words(cut["tip_share"]),
                    "core_share": fraction_words(cut["core_share"]),
                    "tips": f"the {word(cut['tips'])} tips",
                    "pieces": f"the {word(cut['tips'] + cut['octahedra'])} pieces"},
        dots=f"**{cut['dots']}**", tips=f"**{cut['tips']}**",
        octahedra=f"**{cut['octahedra']}**",
        tip_share=fraction_text(cut["tip_share"]), core_share=fraction_text(cut["core_share"]))


def octa_counts() -> str:
    cut = engine.cut()
    tetra = engine.tetrahedron()["counts"]
    counts = (tetra["dots"], tetra["lines"], tetra["faces"], tetra["insides"])
    assert counts == (4, 6, 4, 1), f"the tetrahedron's census came out {counts}"
    assert (cut["oct_dots"], cut["oct_lines"], cut["oct_faces"]) == (6, 12, 8), (
        f"the octahedron came out {(cut['oct_dots'], cut['oct_lines'], cut['oct_faces'])}"
    )
    assert cut["oct_degree"] == 4 and len(cut["opposite_pairs"]) == 3, (
        "the octahedron's dots do not have four lines each, or there are not three opposite pairs"
    )
    pairs = " · ".join("–".join(pair) for pair in cut["opposite_pairs"])
    body = (
        "| | dots | lines | faces | inside |\n"
        "|---|---|---|---|---|\n"
        f"| the tetrahedron, from before | {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |\n"
        f"| the shape between the tips | **{cut['oct_dots']}** | **{cut['oct_lines']}** | "
        f"**{cut['oct_faces']}** | 1 |\n\n"
        f"Its six dots are the middles of the tetrahedron's six lines, so they keep those lines' "
        f"names: {' · '.join(cut['mid_names'])}. Two of them are joined exactly when their "
        f"lines share a corner — which leaves **{len(cut['opposite_pairs'])}** pairs joined by "
        f"nothing at all: {pairs}."
    )
    return checked_block(
        "octa_counts", body,
        f"the census of the shape between the tips: {cut['oct_degree']} lines at every dot, and "
        f"the {word(len(cut['opposite_pairs']))} pairs of dots that no line joins — the first room "
        f"in the book",
        oct_dots=f"**{cut['oct_dots']}**",
        oct_lines=f"**{cut['oct_lines']}**", oct_faces=f"**{cut['oct_faces']}**",
        pairs=pairs, tetra_census=f"| {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |",
        pair_count=f"**{len(cut['opposite_pairs'])}** pairs",
        names=" · ".join(cut["mid_names"]),
        in_caption={"degree": f"{cut['oct_degree']} lines at every dot",
                    "pairs": f"the {word(len(cut['opposite_pairs']))} pairs"})


def octa_poke_table() -> str:
    poke = engine.poke()
    names = engine.cut()["mid_names"]
    history = poke["history"]
    assert poke["crossing_ticks"] == 2 and poke["home_ticks"] == 3 and poke["period"] == 12, (
        f"the crossing came out {poke['crossing_ticks']}, home {poke['home_ticks']}, repeat "
        f"{poke['period']}"
    )
    total = sum(history[0])
    for tick, row in enumerate(history):
        assert sum(row) == total, f"the total changed at tick {tick} — this rule conserves it"
    rows = []
    for tick, row in enumerate(history):
        cells = " | ".join(number(value) for value in row)
        rows.append(f"| {tick} | {cells} | **{number(sum(row))}** |")
    body = (
        f"| tick | {' | '.join(names)} | total |\n"
        f"|---|{'---|' * len(names)}---|\n" + "\n".join(rows)
    )
    # The rows the chapter reads out, and the names it reads them under.
    return checked_block(
        "octa_poke_table", body,
        f"the same rule and the same tick size as the tetrahedron's tables, run on the shape "
        f"between the tips from a poke of 1 on {poke['poked']}: the whole of it is on the opposite "
        f"dot {poke['opposite']} at tick {poke['crossing_ticks']} and home at tick "
        f"{poke['home_ticks']}, the total never moves, and the pair (now, before) does not repeat "
        f"until tick {poke['period']}",
        header=" | ".join(names),
        crossing=rows[poke["crossing_ticks"]], home=rows[poke["home_ticks"]],
        last=rows[poke["period"]],
        in_caption={"poked": f"poke of 1 on {poke['poked']}",
                    "crossing": f"{poke['opposite']} at tick {poke['crossing_ticks']}",
                    "home": f"home at tick {poke['home_ticks']}",
                    "period": f"repeat until tick {poke['period']}"})


def octa_face_sum() -> str:
    surface = engine.face_sum()
    cut = engine.cut()
    names = cut["mid_names"]
    lines = cut["mid_lines"]
    faces = cut["mid_faces"]
    arrows = dict(zip(lines, surface["arrows"]))
    assert surface["sum"] == 0, f"the eight faces summed to {surface['sum']}"
    assert surface["lines_walked_each_way"] == 12, "not every line was walked once each way"
    assert sum(surface["face_numbers"]) == 0, (
        "the eight face-numbers do not add to the sum the engine reported"
    )

    # Group the twelve lines by the face of the original tetrahedron they lie in: a line joins two
    # middles, and the letters of those two middles name a face. Four faces, three lines each.
    grouped: Dict[str, List[str]] = {}
    for line in lines:
        letters = "".join(sorted(set(names[line[0]]) | set(names[line[1]])))
        assert len(letters) == 3, f"the line {line} spans {letters}, which is not a face"
        grouped.setdefault(letters, []).append(
            f"{names[line[0]]}–{names[line[1]]} **{number(arrows[line])}**"
        )
    assert sorted(grouped) == ["ABC", "ABD", "ACD", "BCD"], f"the grouping came out {grouped}"
    assert all(len(items) == 3 for items in grouped.values()), "a face does not hold three lines"
    grouped_table = "\n".join(f"| {face} | {' · '.join(items)} |"
                              for face, items in sorted(grouped.items()))
    shows_each("octa_face_sum's arrows", grouped_table,
               [(f"{names[line[0]]}–{names[line[1]]}", arrows[line]) for line in lines])

    walk_rows = []
    for face, value in zip(faces, surface["face_numbers"]):
        cycle = [names[index] for index in face]
        terms = []
        for step in range(3):
            low, high = face[step], face[(step + 1) % 3]
            sign = 1 if low < high else -1
            terms.append(signed(sign * arrows[(min(low, high), max(low, high))]))
        walk_rows.append(
            f"| {' → '.join(cycle + [cycle[0]])} | {' '.join(terms)} | **{number(value)}** |"
        )
    total_terms = " ".join(signed(value) for value in surface["face_numbers"]).lstrip("+")

    body = (
        f"{word(len(lines)).capitalize()} numbers, one on each line — arrows in their own right, "
        f"not differences of anything. Each line lies in one face of the tetrahedron you cut, so "
        f"they fall into {word(len(grouped))} groups of "
        f"{word(len(next(iter(grouped.values()))))}:\n\n"
        "| the face it lies in | its three lines, with their arrows |\n|---|---|\n"
        + grouped_table
        + f"\n\nNow walk each of the {word(len(faces))} faces the way round it faces from "
          f"outside:\n\n"
        "| walked | its three arrows, signed | how much goes round it |\n|---|---|---|\n"
        + "\n".join(walk_rows)
        + f"\n\nAnd add the {word(len(faces))} up: {total_terms} = **0**."
    )
    shows_exactly("octa_face_sum's face-numbers", "\n".join(walk_rows),
                  list(surface["face_numbers"]))
    return checked_block(
        "octa_face_sum", body,
        f"{word(len(lines))} freely chosen arrows on the shape between the tips, the "
        f"{word(len(faces))} non-zero face-numbers they give, and their sum walked from outside — "
        f"zero, because every one of the {word(len(lines))} lines is walked exactly twice, once "
        f"each way",
        terms=total_terms,
        grouping=f"{word(len(grouped))} groups of "
                 f"{word(len(next(iter(grouped.values()))))}",
        faces_walked=f"each of the {word(len(faces))} faces",
        in_caption={"arrows": f"{word(len(lines))} freely chosen arrows",
                    "faces": f"the {word(len(faces))} non-zero face-numbers",
                    "lines": f"the {word(len(lines))} lines is walked"},
        **{f"face {index}": row for index, row in enumerate(walk_rows)},
        **{f"group {face}": f"| {face} | {' · '.join(items)} |"
           for face, items in grouped.items()})


def stella_counts() -> str:
    both = engine.stella()
    cut = engine.cut()
    tetra = engine.tetrahedron()["counts"]
    assert (both["dots"], both["lines"]) == (14, 36), (
        f"the two together came out {both['dots']} dots and {both['lines']} lines"
    )
    # "No two tips are joined at all" is the sentence below, so it is checked against the engine's
    # own line list rather than inferred from a degree. The first six names are the middles the two
    # tetrahedra share; everything after them is a tip.
    tips = set(range(both["middles"], both["dots"]))
    joined = [edge for edge in both["edges"] if edge[0] in tips and edge[1] in tips]
    assert not joined, f"{len(joined)} line(s) join two tips: {joined[:3]}"
    assert both["middles"] == cut["oct_dots"], (
        "the two tetrahedra do not share the octahedron's six dots, so they are not threaded"
    )
    assert both["in_tetrahedra"] == Fraction(3, 2), (
        f"the pair came out {both['in_tetrahedra']} of the tetrahedron we cut"
    )
    body = (
        "| | dots | lines |\n"
        "|---|---|---|\n"
        f"| the tetrahedron, from before | {tetra['dots']} | {tetra['lines']} |\n"
        f"| the shape between the tips | {cut['oct_dots']} | {cut['oct_lines']} |\n"
        f"| the two tetrahedra, threaded | **{both['dots']}** | **{both['lines']}** |\n\n"
        f"Those are the {both['middles']} middles and {both['tips']} tips — the four "
        f"you started with and the four the second tetrahedron brought "
        f"({' · '.join(both['apex_names'])}). Every middle has {both['middle_degree']} lines and "
        f"every tip has {both['tip_degree']}, and **no two tips are joined at all**, so nothing "
        f"gets from one tip to another without going through the middle. Together they take up "
        f"{fraction_text(both['in_tetrahedra'])} of the tetrahedron you cut, and fill "
        f"{fraction_text(both['in_its_cube'])} of the cube whose eight corners the tips are."
    )
    # Phrases, not bare digits: a "6" on its own is in the table too, so asserting the digit would
    # let a literal into the sentence beside it. The attack that found this typed "The 15 are…"
    # under a table saying 14, and every check stayed green (a proofreader, 2026-09-02).
    return checked_block(
        "stella_counts", body,
        f"the two tetrahedra threaded through one another, counted: the second is the same size as "
        f"the first and its own {word(both['middles'])} middles are the same "
        f"{word(both['middles'])} middles, so they share one octahedron and the "
        f"{word(both['tips'])} tips are the corners of a cube",
        dots=f"**{both['dots']}**", lines=f"**{both['lines']}**",
        middles=f"the {both['middles']} middles", tips=f"{both['tips']} tips",
        middle_degree=f"Every middle has {both['middle_degree']} lines",
        tip_degree=f"every tip has {both['tip_degree']}",
        apexes=" · ".join(both["apex_names"]),
        in_its_cube=fraction_text(both["in_its_cube"]),
        in_tetrahedra=fraction_text(both["in_tetrahedra"]),
        in_caption={"middles": f"its own {word(both['middles'])} middles",
                    "tips": f"the {word(both['tips'])} tips"})


def stella_refusal() -> str:
    refusal = engine.refusal()
    ceilings = refusal["ceilings"]
    runaway = refusal["runaway"]
    tick = refusal["tick"]
    assert runaway["k"] == tick, (
        f"the runaway was run at {runaway['k']}, not the chapters' {tick}"
    )
    assert [row["holds"] for row in ceilings] == [True, True, False], (
        "the verdicts are not hold, hold, fail"
    )
    for row in ceilings:
        assert row["bound"] == Fraction(refusal["leapfrog_bound"], 1) / row["stiffest"], (
            f"the ceiling for {row['dots']} dots is not 4 over its stiffest mode"
        )
        assert row["holds"] == (tick < row["bound"]), (
            f"the verdict for {row['dots']} dots does not follow from its own ceiling"
        )
    assert runaway["printable_rows"] == 3 and runaway["never_returns"], (
        f"{runaway['printable_rows']} rows print, or the run comes home after all"
    )

    # The chapter's own names for the three objects, keyed by how many dots each has, so a row
    # cannot be labelled as the wrong object: the count is what the engine computed.
    called = {4: "the tetrahedron", 6: "the shape between the tips", 14: "the two, threaded"}
    assert sorted(row["dots"] for row in ceilings) == sorted(called), (
        "the three objects are no longer the 4-, 6- and 14-dot ones the chapter met"
    )
    # The column says "must stay under", and it means it: the engine runs each object AT its own
    # bound and asserts the numbers grow there. The first version of this table was headed "the
    # biggest tick it will hold", which a reader disproved on the tetrahedron with a pencil.
    ceiling_rows = "\n".join(
        f"| {called[row['dots']]} | {row['dots']} | {fraction_text(row['bound'])} | "
        f"{'holds' if row['holds'] else '**too big**'} |"
        for row in ceilings
    )
    bounds = runaway["floors"]
    growth = []
    for at, value in runaway["look"]:
        try:
            growth.append((at, number(value)))
        except AssertionError:
            growth.append((at, f"past {_thousands(bounds[at])}"))
    assert any(text.startswith("past") for _, text in growth), (
        "every row wrote down exactly, so the runaway has nothing to show"
    )
    growth_rows = "\n".join(f"| {at} | {text} |" for at, text in growth)

    body = (
        f"| | dots | the tick it must stay under | the book's tick, "
        f"{fraction_text(tick)} |\n|---|---|---|---|\n{ceiling_rows}\n\n"
        "So run it anyway, and watch the biggest number anywhere in the world:\n\n"
        f"| tick | the biggest number in it |\n|---|---|\n{growth_rows}"
    )
    # The caption says only what the two tables above it are: the poke, the tick, the runaway and
    # how much of it can be written down. Everything else it used to carry — the smaller tick, the
    # fifths, the never-coming-home — is the next section's own reveal, and a caption that spends a
    # section's surprise two beats early in small italics was a real defect (a proofreader,
    # 2026-09-02). It also grew the one surface the grain band does not measure.
    most_rows = max(row["printable"] for row in runaway["stable_tried"])
    return checked_block(
        "stella_refusal", body,
        f"the same poke and the same tick on the two tetrahedra threaded together: the tick is "
        f"over what this object will take, so nothing sloshes — it runs away, past "
        f"{_thousands(bounds[max(bounds)])} by tick {max(bounds)}. Only "
        f"{runaway['printable_rows']} rows of the full table can be written down in halves at all, "
        f"and no tick that does stay under the bound prints more than {word(most_rows)} rows",
        column="the tick it must stay under",
        **{f"bound for {row['dots']} dots": fraction_text(row["bound"])
           for row in ceilings},
        book_tick=fraction_text(tick),
        last_bound=_thousands(bounds[max(bounds)]),
        in_caption={"runaway": _thousands(bounds[max(bounds)]),
                    "tick": f"by tick {max(bounds)}",
                    "rows": f"Only {runaway['printable_rows']} rows",
                    "most": f"more than {word(most_rows)} rows"})

# What a token's arithmetic REFUSES, in the prose of any chapter that carries the token.
#
# The defect this exists for (a proofreader, 2026-09-02): `stella_refusal`'s table was corrected to
# "the tick it must stay under" and the prose two paragraphs below it still said "a largest tick it
# will hold, the table says what they are" — pointing at a table that said the opposite. Every
# fidelity check here reads what the *tool* wrote; nothing read what the *author* wrote. So each
# token names the phrasings its own numbers disprove, `check_edition.py` refuses them in the
# chapter's source, and the contradiction cannot be reintroduced by an edit two paragraphs away.
#
# The last group is the readings of the octahedron and time. What has been computed is narrow: a tick is not a trip round the bare octahedron under a time-symmetric rule on 0-forms; the family's claim (screw, 1-forms, chiral mesh) is under review: UniForge lab/napkin/0002.
# They are refused in every chapter's prose, whether or not it carries a token, because neither the
# narrow finding nor the wider claim is a chapter's to make while the wider one is open — and this
# list is a guard rather than a verdict: it keeps a phrasing out and states nothing itself.
REFUSED_IN_PROSE: Dict[str, List[str]] = {
    "triangle_slosh_table": [
        "the triangle settles",
        "the triangle never comes home",
        "the total drifts",
    ],
    "no_room": [
        "further away than",
        "a ring spreads",
    ],
    "tick_belongs_to_shape": [
        "one tick fits every shape",
        "the same tick works on every shape",
        "the tick belongs to the rule",
        "the tick is the rule's",
    ],
    "stella_refusal": [
        "tick it will hold",
        "tick it holds",
        "largest tick that holds",
        "biggest tick that holds",
    ],
    "octa_face_sum": [
        "group four and four",
        "four and four",
    ],
    "octa_poke_table": [
        "one tick to cross",
        "a tick is a trip",
        "trip round the octahedron",
        "trip round the shape",
    ],
    "*": [
        "trip round the octahedron",
        "saves work",
        "cheaper than working",
        "finishes its calculation",
        "before the cube is stable",
    ],
}


TOKENS = {
    "tetra_counts": tetra_counts,
    "triangle_loop_example": triangle_loop_example,
    "tetra_face_loops": tetra_face_loops,
    "tetra_inside_sum": tetra_inside_sum,
    "slosh_table": slosh_table,
    "slosh_table_dialed": slosh_table_dialed,
    "triangle_slosh_table": triangle_slosh_table,
    "tick_belongs_to_shape": tick_belongs_to_shape,
    "no_room": no_room,
    "vertex_classes": vertex_classes,
    "octa_cut": octa_cut,
    "octa_counts": octa_counts,
    "octa_poke_table": octa_poke_table,
    "octa_face_sum": octa_face_sum,
    "stella_counts": stella_counts,
    "stella_refusal": stella_refusal,
}


def render(name: str) -> str:
    if name not in TOKENS:
        raise KeyError(name)
    return TOKENS[name]()


if __name__ == "__main__":
    for token in TOKENS:
        print(f"\n{'=' * 90}\n{token}\n{'=' * 90}")
        print(render(token))
