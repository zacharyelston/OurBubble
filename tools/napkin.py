#!/usr/bin/env python3
"""The napkin backend: the book's chapters 1–4 numbers, computed while the page is built.

Chapters 1–4 live on one triangle, one tetrahedron, and the two shapes that tetrahedron is made of,
and every number in them is finger-countable — four dots, six lines, three differences, ten ticks,
and then a crossing that takes two of those ticks. Quoting such numbers from a record would be
theatre: the reader can check them on a napkin, so the book should do the same thing in front of her
rather than cite itself. Each `{{napkin:NAME}}` token in a chapter is replaced at build time by the
result of running the arithmetic here, and every rendered block says so.

Chapter 4 is where the napkin runs out, on purpose, and that is its finding: the arithmetic for the
shapes bigger than one tetrahedron lives in `tools/octahedron.py`, and the last of those shapes
cannot be run at the chapters' own tick size at all. `number()` refusing to print it is not a
formatting problem — it is the chapter's point, arriving in the one place it cannot be argued with.

**Everything is exact.** `fractions.Fraction` throughout, and each value is rendered by
`number()`, which refuses anything it cannot write down exactly and briefly. There is no floating
point anywhere in this file, so two builds of the same commit cannot differ.

**Every token asserts its own invariant before it renders.** The loop sums are zero, the inside sum
is zero, the total is conserved — those are the *claims* the chapters make, so a token that cannot
demonstrate its claim raises and takes the build down with it. A napkin that quietly printed a
non-zero loop sum would be worse than no napkin.

The object and the rule are the engine's, replicated faithfully in Python:

* the tetrahedron is the complete simplicial 3-simplex — vertices, and every subset of them —
  with the standard alternating boundary, and `d∘d = 0` is asserted on both rungs rather than
  assumed;
* one tick is `step_scalar_wave` from `core/solve/src/wave_solver.rs`:
  `φ' = 2φ − φ_old − c²dt² Δ₀φ`, with `Δ₀ = ⋆₀⁻¹ d₀ᵀ ⋆₁ d₀` from `core/dec/src/operators.rs`
  (`apply_laplacian_0_metric`). With `⋆₀ = 1` and `⋆₁ = w_e` that is exactly
  `(Δφ)_i = Σ_j w_ij (φ_i − φ_j)`, so **the dial the book turns in chapter 2 is `⋆₁`** — the same
  object that decides isotropy in chapter 5, on six lines you can see.
"""

from __future__ import annotations

import re
from fractions import Fraction
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

# ── the object ────────────────────────────────────────────────────────────────────────────────────

NAMES = ("A", "B", "C", "D")
VERTICES: Tuple[int, ...] = (0, 1, 2, 3)


def simplices(vertices: Sequence[int], k: int) -> List[Tuple[int, ...]]:
    """The k-simplices of the complete complex on `vertices`, each ascending, all in ascending order.

    Ascending vertex order *is* the orientation, which is what makes the alternating signs below the
    only convention in play — the same one the engine's incidence tables are built from.
    """
    return sorted(combinations(sorted(vertices), k + 1))


def coboundary(cells_lo: Sequence[Tuple[int, ...]], cells_hi: Sequence[Tuple[int, ...]]):
    """The matrix of `d` from k-forms on `cells_lo` to (k+1)-forms on `cells_hi`.

    `(d f)(σ) = Σ_i (−1)^i f(σ with its i-th vertex dropped)` — the standard simplicial coboundary.
    """
    index = {cell: i for i, cell in enumerate(cells_lo)}
    rows = []
    for hi in cells_hi:
        row = [0] * len(cells_lo)
        for i in range(len(hi)):
            face = hi[:i] + hi[i + 1:]
            row[index[face]] += (-1) ** i
        rows.append(row)
    return rows


def apply(matrix, values: Sequence[Fraction]) -> List[Fraction]:
    return [sum(coefficient * value for coefficient, value in zip(row, values)) for row in matrix]


def census(vertices: Sequence[int] = VERTICES) -> Dict[str, object]:
    """The counts, and the proof that the object they describe is a complex.

    `d∘d = 0` is checked on both rungs — dots→lines→faces and lines→faces→inside — because it is the
    one fact chapters 1 and 2 are entirely about, and it is combinatorial: it holds because the
    signs cancel, not because a number came out small.
    """
    dots = simplices(vertices, 0)
    lines = simplices(vertices, 1)
    faces = simplices(vertices, 2)
    insides = simplices(vertices, 3)

    d0 = coboundary(dots, lines)
    d1 = coboundary(lines, faces)
    d2 = coboundary(faces, insides)

    for lower, upper, label in ((d0, d1, "d₁∘d₀"), (d1, d2, "d₂∘d₁")):
        for row in [apply(upper, column) for column in _columns(lower)]:
            assert all(entry == 0 for entry in row), f"{label} ≠ 0 — the object is not a complex"

    return {
        "dots": dots, "lines": lines, "faces": faces, "insides": insides,
        "d0": d0, "d1": d1, "d2": d2,
    }


def _columns(matrix) -> List[List[Fraction]]:
    """The columns of `matrix` as vectors, for composing two operators one basis element at a time."""
    if not matrix:
        return []
    return [
        [Fraction(matrix[row][col]) for row in range(len(matrix))]
        for col in range(len(matrix[0]))
    ]


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


def block(name: str, body: str, what: str) -> str:
    """One rendered token, fenced by comments that mark exactly where the computed span begins.

    The fence is load-bearing, not decoration: `check_edition.py` uses it to bound the
    computed-on-build exemption to this span and nothing else, so a bold number the *narrative*
    emphasises is still governed by the appendix-anchoring rule.
    """
    return (
        f"<!-- napkin:{name} -->\n\n{body.strip()}\n{footnote(what)}\n<!-- /napkin:{name} -->"
    )


# ── the tokens ────────────────────────────────────────────────────────────────────────────────────

# Four corner values, used by every tetrahedron token so the chapters can carry one example
# through. Mean 3, chosen so the deviations (−1, +2, −2, +1) are distinct and small.
CORNERS: Tuple[int, int, int, int] = (2, 5, 1, 4)

# Six freely chosen line-numbers for `tetra_inside_sum` — arrows in their own right rather than
# differences of corner values. This is beat 22's move, and it is the whole reason that token is
# worth printing: differences would give four zero faces, and 0+0+0+0 = 0 demonstrates nothing.
ARROWS: Tuple[int, ...] = (3, 1, 1, 2, 1, 1)

# One tick. `k = c²dt²` in the engine's `step_scalar_wave`.
#
# k = 1/2 is the choice that keeps this table on a napkin. The tetrahedron's Laplacian has
# eigenvalues 0 and 4 (three times) with unit weights, and 0, 4, 4, 6 with one line doubled; a mode
# of eigenvalue λ obeys x' = (2 − kλ)x − x_prev, so k = 1/2 makes every coefficient an integer in
# both runs and the tables come out in whole numbers and halves. It is also stable in both: the
# leapfrog needs kλ < 4, and 1/2 · 6 = 3.
TICK_K = Fraction(1, 2)
TICKS = 10


def laplacian(values: Sequence[Fraction], weights: Dict[Tuple[int, ...], Fraction],
              lines: Sequence[Tuple[int, ...]]) -> List[Fraction]:
    """`Δ₀ = ⋆₀⁻¹ d₀ᵀ ⋆₁ d₀` with `⋆₀ = 1`, i.e. `(Δφ)_i = Σ_j w_ij (φ_i − φ_j)`.

    Written as the engine writes it — gradient, apply `⋆₁`, take the codifferential — rather than as
    the graph-Laplacian shortcut, so that the `⋆₁` in the middle is visibly the same dial.
    """
    out = [Fraction(0)] * len(values)
    for line in lines:
        i, j = line
        flux = weights[line] * (values[j] - values[i])   # ⋆₁ d₀ φ on this line
        out[i] -= flux                                    # d₀ᵀ, sign −1 at the low vertex
        out[j] += flux                                    # sign +1 at the high vertex
    return out


def slosh(weights: Dict[Tuple[int, ...], Fraction], lines: Sequence[Tuple[int, ...]],
          ticks: int = TICKS, initial: Sequence[Fraction] | None = None,
          k: Fraction = TICK_K) -> List[List[Fraction]]:
    """The engine's leapfrog scalar wave, started from rest, `ticks` times.

    Started from rest (`φ_old = φ_0`) for a reason that matters to the chapter: the rows of `Δ₀` sum
    to zero, so `Σφ` obeys `S' = 2S − S_prev`, and beginning with `S_prev = S_0` makes the total
    *exactly* constant for ever. The conserved total is not a property of the wave in general — it
    is a property of this rule started this way, and the assertion below is what holds us to it.

    `initial` and `k` default to the chapter's own four corners and tick size, so the tokens above
    are unchanged. They exist so that a *larger* object can be run through this same rule rather
    than through a second copy of it: `tools/octahedron.py` runs the octahedron and the stella
    octangula here, and a second leapfrog written next door would be the one place the book could
    disagree with itself about what one step is.
    """
    current = [Fraction(v) for v in (CORNERS if initial is None else initial)]
    previous = list(current)
    history = [list(current)]
    for _ in range(ticks):
        lap = laplacian(current, weights, lines)
        nxt = [2 * c - p - k * l for c, p, l in zip(current, previous, lap)]
        previous, current = current, nxt
        history.append(list(current))
    total = sum(history[0])
    for tick, row in enumerate(history):
        assert sum(row) == total, (
            f"the total changed at tick {tick}: {sum(row)} ≠ {total} — this rule conserves it, so "
            f"either the step or the Laplacian is wrong"
        )
    return history


def unit_weights(lines: Sequence[Tuple[int, ...]]) -> Dict[Tuple[int, ...], Fraction]:
    return {line: Fraction(1) for line in lines}


def tetra_counts() -> str:
    c = census()
    counts = (len(c["dots"]), len(c["lines"]), len(c["faces"]), len(c["insides"]))
    assert counts == (4, 6, 4, 1), f"the tetrahedron's census came out {counts}"
    body = (
        "| dots | lines | faces | solid inside |\n"
        "|---|---|---|---|\n"
        f"| {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |"
    )
    return block("tetra_counts", body,
                 "the tetrahedron's census, and that walking the boundary comes home to zero twice "
                 "over — round each face, and round the solid inside")


def triangle_loop_example() -> str:
    values = [Fraction(v) for v in (2, 5, 1)]
    walk = [(0, 1), (1, 2), (2, 0)]
    steps = [(a, b, values[b] - values[a]) for a, b in walk]
    total = sum(step[2] for step in steps)
    assert total == 0, f"the triangle's loop sum came out {total}"

    rows = "\n".join(
        f"| {NAMES[a]} → {NAMES[b]} | {number(values[b])} − {number(values[a])} | {signed(d)} |"
        for a, b, d in steps
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
    c = census()
    lines, faces = c["lines"], c["faces"]
    values = [Fraction(v) for v in CORNERS]
    differences = apply(c["d0"], values)
    loops = apply(c["d1"], differences)
    assert all(loop == 0 for loop in loops), f"a face loop came out non-zero: {loops}"

    corner_text = ", ".join(f"**{NAMES[i]} = {number(values[i])}**" for i in VERTICES)
    line_rows = " | ".join(edge_name(line) for line in lines)
    diff_rows = " | ".join(signed(d) for d in differences)
    face_rows = "\n".join(
        f"| {edge_name(face)} | {walk_terms(c['d1'][fi], differences)} | **{number(loops[fi])}** |"
        for fi, face in enumerate(faces)
    )
    body = (
        f"Corners: {corner_text}.\n\n"
        f"| line | {line_rows} |\n"
        f"|---|{'---|' * len(lines)}\n"
        f"| difference | {diff_rows} |\n\n"
        "| face | its three line-numbers | loop, walked round |\n|---|---|---|\n"
        f"{face_rows}"
    )
    return block("tetra_face_loops", body,
                 "the six differences on one tetrahedron and each face's loop sum, from the corner "
                 "values 2, 5, 1, 4")


def tetra_inside_sum() -> str:
    c = census()
    lines, faces = c["lines"], c["faces"]
    arrows = [Fraction(a) for a in ARROWS]
    face_numbers = apply(c["d1"], arrows)
    inside = apply(c["d2"], face_numbers)

    assert all(f != 0 for f in face_numbers), (
        f"a face came out zero ({face_numbers}), so the inside sum would demonstrate less than it "
        f"claims — choose line-numbers that are not differences of corner values"
    )
    assert inside == [Fraction(0)], f"the inside sum came out {inside}"

    line_rows = " | ".join(edge_name(line) for line in lines)
    arrow_rows = " | ".join(number(a) for a in arrows)
    inside_terms = walk_terms(c["d2"][0], face_numbers)

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
    outward = []
    for index, (face, total) in enumerate(zip(faces, face_numbers)):
        sign = c["d2"][0][index]
        row = [sign * value for value in c["d1"][index]]
        letters = list(edge_name(face))
        cycle = letters if sign > 0 else [letters[0], letters[2], letters[1]]
        outward.append(sign * total)
        walk_rows.append(
            f"| {' → '.join(cycle + [cycle[0]])} | {walk_terms(row, arrows)} | "
            f"**{number(sign * total)}** |"
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
        f"|---|{'---|' * len(lines)}\n"
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


def period(history: Sequence[Sequence[Fraction]]) -> int:
    """The repeat length of a run, or 0 if it has not repeated within the ticks computed.

    Stated in the footnote rather than left for the reader to notice. Undamped, on four corners that
    are all each other's neighbours, this rule cannot settle — it returns to where it started — and a
    table with visibly repeating rows invites "is this broken?". Naming the period answers that, and
    computing it means the answer cannot be stale.
    """
    for candidate in range(1, len(history)):
        if all(history[i] == history[i % candidate] for i in range(len(history))):
            return candidate
    return 0


def slosh_table() -> str:
    c = census()
    lines = c["lines"]
    history = slosh(unit_weights(lines), lines)
    repeat = period(history)
    assert repeat, "the run did not repeat within the ticks computed"
    body = _slosh_body(history)
    return block("slosh_table", body,
                 f"the one rule, run {TICKS} ticks from rest on one tetrahedron with every line "
                 f"counting the same; the total is conserved exactly, and with nothing to damp it and "
                 f"no room to spread into the world never settles — at this step size it comes back "
                 f"to its start every {repeat} ticks")


DIALED_LINE: Tuple[int, ...] = (0, 1)


def slosh_table_dialed() -> str:
    c = census()
    lines = c["lines"]
    weights = unit_weights(lines)
    weights[DIALED_LINE] = Fraction(2)
    history = slosh(weights, lines)

    plain = slosh(unit_weights(lines), lines)
    assert history != plain, "doubling a line changed nothing — the dial is not wired up"
    assert sum(history[0]) == sum(plain[0]), "the two runs must start from the same total"

    # The level the four numbers average to is the one thing the dial must NOT move: it is fixed by
    # the conserved total, not by the weights. Asserted rather than asserted-in-prose.
    average = Fraction(sum(history[0]), len(NAMES))
    for tick, row in enumerate(history):
        assert Fraction(sum(row), len(row)) == average, f"the average moved at tick {tick}"

    body = _slosh_body(history)
    return block("slosh_table_dialed", body,
                 f"the same {TICKS} ticks with line {edge_name(DIALED_LINE)} counted double and "
                 f"every other line counting one — the dial, on one line. The total is still "
                 f"conserved exactly and the four numbers still average to {number(average)}; what "
                 f"changed is the motion, now faster along {edge_name(DIALED_LINE)} than the rest")


# ── the object one dimension out: how many kinds of place are there? ──────────────────────────────
#
# Chapters 1–3 never leave one tetrahedron. Chapter 4 has to, because she asks for room, and the
# answer to "do tetrahedra fill space?" is no — so the book has to say what was built instead. This
# token replicates that construction and counts what it produced.
#
# Faithful to `mesh_3d_chiral_tetoct_periodic` in the engine's `core/geom/src/mesh.rs`:
#
#   * dots are the integer points with x+y+z EVEN; the odd points are hole centres and carry
#     nothing at all (asserted below — they must come out with no lines on them);
#   * every unit cube contributes ONE tetrahedron, on its four even corners;
#   * every odd point carries the octahedron of its six axis neighbours, cut into four tetrahedra
#     about ONE long diagonal, and which of the three the cut uses is `(x+y+z) mod 3` —
#     `chiral_oct_screw111`, the rule the engine's own audit picked.
#
# The whole point of the token is the CONTROL. "Three kinds of place" means nothing on its own; it
# means something next to "cut every hole the same way and there is one kind of place". Same
# builder, same lattice, one line different.

TORUS_MIN = 6      # the builder's own minimum: parity (mod 2) and the cut rule (mod 3) must both
TORUS_CHECK = 12   # close under a wrap, and ±2 hops must stay distinct. 12 confirms 6 is enough.


def screw111(x: int, y: int, z: int) -> int:
    """The engine's cut rule: which of the three long diagonals this hole is split about."""
    return (x + y + z) % 3


def uniform_cut(x: int, y: int, z: int) -> int:
    """The control: every hole cut the same way, whatever its position."""
    return 0


def tetoct_stars(n: int, cut) -> Dict[Tuple[int, int, int], frozenset]:
    """Build the complex on an n³ torus and return each dot's set of line-directions.

    A dot's "star" here is the set of directions the lines leaving it point in — the arrangement a
    reader would see standing on that dot and looking around. Directions are taken by shortest way
    round the torus, so a line that wraps is still the short line it geometrically is.
    """
    def wrap(p):
        return (p[0] % n, p[1] % n, p[2] % n)

    def direction(a, b):
        out = []
        for u, v in zip(a, b):
            d = (v - u) % n
            out.append(d - n if d > n // 2 else d)
        return tuple(out)

    tets = []
    # one tetrahedron per cube, on its four even corners
    for i in range(n):
        for j in range(n):
            for k in range(n):
                corners = [
                    (i + a, j + b, k + c)
                    for a in (0, 1) for b in (0, 1) for c in (0, 1)
                    if (i + a + j + b + k + c) % 2 == 0
                ]
                assert len(corners) == 4, "a cube must have four even corners"
                tets.append([wrap(p) for p in corners])

    # one cut-up octahedron per odd point
    for x in range(n):
        for y in range(n):
            for z in range(n):
                if (x + y + z) % 2 == 0:
                    continue
                xp, xm = (x + 1, y, z), (x - 1, y, z)
                yp, ym = (x, y + 1, z), (x, y - 1, z)
                zp, zm = (x, y, z + 1), (x, y, z - 1)
                axis = cut(x, y, z)
                if axis == 0:
                    d0, d1, eq = xm, xp, [yp, zp, ym, zm]
                elif axis == 1:
                    d0, d1, eq = ym, yp, [zp, xp, zm, xm]
                else:
                    d0, d1, eq = zm, zp, [xp, yp, xm, ym]
                for w in range(4):
                    tets.append([wrap(p) for p in (d0, d1, eq[w], eq[(w + 1) % 4])])

    stars: Dict[Tuple[int, int, int], set] = {}
    for x in range(n):
        for y in range(n):
            for z in range(n):
                stars[(x, y, z)] = set()
    for tet in tets:
        for a in tet:
            for b in tet:
                if a != b:
                    stars[a].add(direction(a, b))
    return {point: frozenset(star) for point, star in stars.items()}


def kinds_of_place(n: int, cut) -> Tuple[int, List[int], Dict[Tuple[int, int, int], int]]:
    """The number of distinct arrangements, their sizes, and which arrangement each dot has.

    Only the dots that carry lines are counted. The odd points are not places a number can live —
    they are the holes the octahedra are centred on — and that they come out with no lines at all is
    asserted here rather than assumed, because it is the load-bearing half of "dots are the even
    points".
    """
    stars = tetoct_stars(n, cut)
    arrangements: Dict[frozenset, int] = {}
    labels: Dict[Tuple[int, int, int], int] = {}
    sizes: List[int] = []
    for point in sorted(stars):
        star = stars[point]
        if sum(point) % 2:
            assert not star, f"the hole at {point} carries {len(star)} line(s); it should carry none"
            continue
        assert len(star) == 14, f"the dot at {point} has {len(star)} lines, not 14"
        if star not in arrangements:
            arrangements[star] = len(arrangements)
            sizes.append(0)
        labels[point] = arrangements[star]
        sizes[arrangements[star]] += 1
    return len(arrangements), sizes, labels


def vertex_classes() -> str:
    dots = TORUS_MIN ** 3 // 2

    count, sizes, labels = kinds_of_place(TORUS_MIN, screw111)
    assert count == 3, f"the twisting rule gave {count} kinds of place, not 3"
    assert sizes == [dots // 3] * 3, f"the three kinds are not equal thirds: {sizes}"
    assert sum(sizes) == dots, f"{sum(sizes)} dots classified, expected {dots}"

    # Each kind is exactly one value of (x+y+z) mod 3 — the arrangement a dot has is fixed by where
    # it sits, and by nothing else. This is the claim the chapter will make, so it is the assertion.
    by_kind: Dict[int, set] = {}
    for point, kind in labels.items():
        by_kind.setdefault(kind, set()).add(sum(point) % 3)
    assert all(len(values) == 1 for values in by_kind.values()), (
        f"a kind of place spans more than one position rule: {by_kind}"
    )
    assert {next(iter(v)) for v in by_kind.values()} == {0, 1, 2}, (
        f"the three kinds do not use all three positions: {by_kind}"
    )

    control, control_sizes, _ = kinds_of_place(TORUS_MIN, uniform_cut)
    assert control == 1, f"cutting every hole the same way gave {control} kinds, not 1"
    assert control_sizes == [dots], f"the control's single kind does not hold every dot: {control_sizes}"

    # A bigger world must agree, or 6 was too small to see the truth rather than the wrap.
    bigger, bigger_sizes, _ = kinds_of_place(TORUS_CHECK, screw111)
    big_dots = TORUS_CHECK ** 3 // 2
    assert bigger == 3, f"the {TORUS_CHECK}³ world gave {bigger} kinds, not 3"
    assert bigger_sizes == [big_dots // 3] * 3, f"the bigger world is not in thirds: {bigger_sizes}"

    body = (
        "| how the holes are cut | kinds of place | how the dots divide |\n"
        "|---|---|---|\n"
        f"| all the same way | **{control}** | all {dots} alike |\n"
        f"| turning by a third each step | **{count}** | "
        f"{' · '.join(str(size) for size in sizes)} — exact thirds |"
    )
    return block("vertex_classes", body,
                 f"the object built on a {TORUS_MIN}×{TORUS_MIN}×{TORUS_MIN} wrapped world — every "
                 f"dot has {14} lines either way, and the only difference is the cut: cut every hole "
                 f"alike and every dot stands in the same arrangement, turn the cut by a third each "
                 f"step and there are exactly three, in equal thirds "
                 f"(confirmed unchanged on a {TORUS_CHECK}³ world)")


# ── the shape between: cut the one tetrahedron and look at what is left ──────────────────────────
#
# Chapters 1–3 never leave one tetrahedron, and the chapter after them needs room. The cheapest room
# is not more tetrahedra: it is *inside* the one she has. Mark the middle of each of its six lines,
# cut, and four half-size tetrahedra come off the tips leaving one octahedron between them — the
# owner's finding, and the object the record's tiling turns out to be full of.
#
# **The arithmetic for these six tokens lives in `tools/octahedron.py`, not here**, and the import
# below is deliberately inside each function rather than at the top of the file. `octahedron.py`
# imports *this* module — it runs the chapters' own leapfrog rather than a second copy of it — so a
# top-level import here would be a cycle. The direction of dependence is the honest one: the napkin
# owns the rule and the rendering, the other module owns the object and every assertion about it.
#
# Nothing below computes anything itself. Each token renders numbers another module has already
# asserted, and re-asserts the handful of them the chapter's sentences actually lean on, so a claim
# cannot survive here after stopping being true over there.


def _octahedron():
    import octahedron                        # noqa: PLC0415 — see the note above: a cycle otherwise
    return octahedron


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


def octa_cut() -> str:
    cut = _octahedron().midpoint_cut()
    assert (cut["dots"], cut["tips"], cut["octahedra"]) == (10, 4, 1), (
        f"the cut gave {cut['dots']} dots, {cut['tips']} tips and {cut['octahedra']} octahedra"
    )
    assert cut["tip_share"] == Fraction(1, 8) and cut["core_share"] == Fraction(1, 2), (
        "the tips are not eighths, or the shape between them is not half"
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
    carries("octa_cut", body, dots=f"**{cut['dots']}**", tips=f"**{cut['tips']}**",
            octahedra=f"**{cut['octahedra']}**", tip_share=fraction_text(cut["tip_share"]),
            core_share=fraction_text(cut["core_share"]))
    return block("octa_cut", body,
                 "one tetrahedron cut at the middles of its six lines: the four tips are an eighth "
                 "of it each and the shape between them is exactly half, so the five pieces "
                 "account for all of it")


def octa_counts() -> str:
    octahedron = _octahedron()
    cut = octahedron.midpoint_cut()
    tetra = census()
    counts = (len(tetra["dots"]), len(tetra["lines"]), len(tetra["faces"]), len(tetra["insides"]))
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
        f"names: {' · '.join(octahedron.MID_NAMES)}. Two of them are joined exactly when their "
        f"lines share a corner — which leaves **{len(cut['opposite_pairs'])}** pairs joined by "
        f"nothing at all: {pairs}."
    )
    carries("octa_counts", body, oct_dots=f"**{cut['oct_dots']}**",
            oct_lines=f"**{cut['oct_lines']}**", oct_faces=f"**{cut['oct_faces']}**",
            pairs=pairs, tetra_census=f"| {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |",
            pair_count=f"**{len(cut['opposite_pairs'])}** pairs",
            names=" · ".join(octahedron.MID_NAMES))
    return block("octa_counts", body,
                 f"the census of the shape between the tips — {cut['oct_degree']} lines at every "
                 f"dot, and the three pairs of dots that no line joins, which is the first room in "
                 f"the book")


def octa_poke_table() -> str:
    octahedron = _octahedron()
    poke = octahedron.octahedron_poke_table()
    history = poke["history"]
    assert poke["crossing_ticks"] == 2 and poke["home_ticks"] == 3 and poke["period"] == 12, (
        f"the crossing came out {poke['crossing_ticks']}, home {poke['home_ticks']}, repeat "
        f"{poke['period']}"
    )
    names = octahedron.MID_NAMES
    rows = []
    for tick, row in enumerate(history):
        cells = " | ".join(number(value) for value in row)
        rows.append(f"| {tick} | {cells} | **{number(sum(row))}** |")
    body = (
        f"| tick | {' | '.join(names)} | total |\n"
        f"|---|{'---|' * len(names)}---|\n" + "\n".join(rows)
    )
    # The rows the chapter reads out, and the names it reads them under.
    carries("octa_poke_table", body, header=" | ".join(names),
            crossing=rows[poke["crossing_ticks"]], home=rows[poke["home_ticks"]],
            last=rows[poke["period"]])
    return block("octa_poke_table", body,
                 f"the same rule and the same tick size as the tetrahedron's tables, run on the "
                 f"shape between the tips from a poke of 1 on {poke['poked']}: the whole of it is "
                 f"on the opposite dot {poke['opposite']} at tick {poke['crossing_ticks']} and home "
                 f"at tick {poke['home_ticks']}, the total never moves, and the pair (now, before) "
                 f"does not repeat until tick {poke['period']}")


def octa_face_sum() -> str:
    octahedron = _octahedron()
    surface = octahedron.octahedron_boundary_sum()
    names = octahedron.MID_NAMES
    lines = octahedron.mid_lines()
    faces = octahedron.mid_faces()
    arrows = {line: Fraction(value) for line, value in zip(lines, surface["arrows"])}
    assert surface["sum"] == 0, f"the eight faces summed to {surface['sum']}"
    assert surface["lines_walked_each_way"] == 12, "not every line was walked once each way"

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
    shows_exactly("octa_face_sum's arrows", grouped_table, list(arrows.values()))

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
    carries("octa_face_sum", body, terms=total_terms,
            grouping=f"{word(len(grouped))} groups of "
                     f"{word(len(next(iter(grouped.values()))))}",
            faces_walked=f"each of the {word(len(faces))} faces",
            **{f"face {index}": row for index, row in enumerate(walk_rows)},
            **{f"group {face}": f"| {face} | {' · '.join(items)} |"
               for face, items in grouped.items()})
    return block("octa_face_sum", body,
                 "twelve freely chosen arrows on the shape between the tips, the eight non-zero "
                 "face-numbers they give, and their sum walked from outside — zero, because every "
                 "one of the twelve lines is walked exactly twice, once each way")


def stella_counts() -> str:
    octahedron = _octahedron()
    twin = octahedron.second_tetrahedron()
    both = octahedron.stella_reader_census()
    tetra = census()
    cut = octahedron.midpoint_cut()
    assert (both["dots"], both["lines"]) == (14, 36), (
        f"the two together came out {both['dots']} dots and {both['lines']} lines"
    )
    assert both["tips_independent"] and twin["twin_middles_the_same"], (
        "the two tetrahedra are not threaded through one another"
    )
    assert both["stella_in_tetrahedra"] == Fraction(3, 2), (
        f"the pair came out {both['stella_in_tetrahedra']} of the tetrahedron we cut"
    )
    body = (
        "| | dots | lines |\n"
        "|---|---|---|\n"
        f"| the tetrahedron, from before | {len(tetra['dots'])} | {len(tetra['lines'])} |\n"
        f"| the shape between the tips | {cut['oct_dots']} | {cut['oct_lines']} |\n"
        f"| the two tetrahedra, threaded | **{both['dots']}** | **{both['lines']}** |\n\n"
        f"Those are the {both['middles']} middles and {both['tips']} tips — the four "
        f"you started with and the four the second tetrahedron brought "
        f"({' · '.join(twin['apex_names'])}). Every middle has {both['middle_degree']} lines and "
        f"every tip has {both['tip_degree']}, and **no two tips are joined at all**, so nothing "
        f"gets from one tip to another without going through the middle. Together they fill "
        f"{fraction_text(both['stella_in_its_cube'])} of the cube whose eight corners the tips "
        f"are — half again as much room as the tetrahedron you cut."
    )
    # Phrases, not bare digits: a "6" on its own is in the table too, so asserting the digit would
    # let a literal into the sentence beside it. The attack that found this typed "The 15 are…"
    # under a table saying 14, and every check stayed green (a proofreader, 2026-09-02).
    carries("stella_counts", body, dots=f"**{both['dots']}**", lines=f"**{both['lines']}**",
            middles=f"the {both['middles']} middles", tips=f"{both['tips']} tips",
            middle_degree=f"Every middle has {both['middle_degree']} lines",
            tip_degree=f"every tip has {both['tip_degree']}",
            apexes=" · ".join(twin["apex_names"]),
            in_its_cube=fraction_text(both["stella_in_its_cube"]))
    return block("stella_counts", body,
                 "the two tetrahedra threaded through one another, counted: the second is the same "
                 "size as the first and its own six middles are the same six middles, so they share "
                 "one octahedron and the eight tips are the corners of a cube")


def stella_refusal() -> str:
    octahedron = _octahedron()
    ceilings = octahedron.napkin_ceilings()
    runaway = octahedron.stella_runaway()
    assert ceilings["tick"] == TICK_K, (
        f"the ceilings were worked out at tick {ceilings['tick']}, not the chapters' {TICK_K}"
    )
    assert [row["holds"] for row in ceilings["rows"]] == [True, True, False], (
        "the verdicts are not hold, hold, fail"
    )
    assert runaway["printable_rows"] == 3 and runaway["never_returns"], (
        f"{runaway['printable_rows']} rows print, or the run comes home after all"
    )

    # The chapter's own names for the three objects, keyed by how many dots each has, so a row
    # cannot be labelled as the wrong object: the count is what the module computed.
    called = {4: "the tetrahedron", 6: "the shape between the tips", 14: "the two, threaded"}
    assert sorted(row["dots"] for row in ceilings["rows"]) == sorted(called), (
        "the three objects are no longer the 4-, 6- and 14-dot ones the chapter met"
    )
    # The column says "must stay under", and it means it: `napkin_ceilings` runs each object AT its
    # own bound and asserts the numbers grow there. The first version of this table was headed "the
    # biggest tick it will hold", which a reader disproved on the tetrahedron with a pencil.
    ceiling_rows = "\n".join(
        f"| {called[row['dots']]} | {row['dots']} | {fraction_text(row['bound'])} | "
        f"{'holds' if row['holds'] else '**too big**'} |"
        for row in ceilings["rows"]
    )
    look = dict(runaway["look"])
    bounds = dict(runaway["bounds"])
    growth = []
    for tick, value in runaway["look"]:
        try:
            growth.append((tick, number(value)))
        except AssertionError:
            growth.append((tick, f"past {_thousands(bounds[tick])}"))
    assert any(text.startswith("past") for _, text in growth), (
        "every row wrote down exactly, so the runaway has nothing to show"
    )
    growth_rows = "\n".join(f"| {tick} | {text} |" for tick, text in growth)

    body = (
        f"| | dots | the tick it must stay under | the book's tick, "
        f"{fraction_text(TICK_K)} |\n|---|---|---|---|\n{ceiling_rows}\n\n"
        "So run it anyway, and watch the biggest number anywhere in the world:\n\n"
        f"| tick | the biggest number in it |\n|---|---|\n{growth_rows}"
    )
    carries("stella_refusal", body, column="the tick it must stay under",
            **{f"bound for {row['dots']} dots": fraction_text(row["bound"])
               for row in ceilings["rows"]},
            book_tick=fraction_text(TICK_K),
            last_bound=_thousands(bounds[max(bounds)]))
    example = runaway["example"]
    return block("stella_refusal", body,
                 f"the same poke and the same tick on the two tetrahedra threaded together: the "
                 f"tick is over what this object will take, so nothing sloshes — it runs away, past "
                 f"{_thousands(bounds[max(bounds)])} by tick {max(bounds)}. Only "
                 f"{runaway['printable_rows']} rows of the full table can be written down in halves "
                 f"at all. A tick that does stay under the bound is no rescue: at "
                 f"{fraction_text(example['k'])} the numbers have {example['first_denominator']} "
                 f"underneath them at the first tick and {example['second_denominator']} at the "
                 f"second, and every tick that holds prints two rows at most. And at no tick size that can be written as a fraction does this object "
                 f"ever come home — five were tried, and why none can is proved in "
                 f"`tools/octahedron.py`")


TOKENS = {
    "tetra_counts": tetra_counts,
    "triangle_loop_example": triangle_loop_example,
    "tetra_face_loops": tetra_face_loops,
    "tetra_inside_sum": tetra_inside_sum,
    "slosh_table": slosh_table,
    "slosh_table_dialed": slosh_table_dialed,
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
