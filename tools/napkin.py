#!/usr/bin/env python3
"""The napkin backend: the book's chapters 1–3 numbers, computed while the page is built.

Chapters 1–3 live on one triangle and one tetrahedron, and every number in them is finger-countable
— four dots, six lines, three differences, ten ticks. Quoting such numbers from a record would be
theatre: the reader can check them on a napkin, so the book should do the same thing in front of her
rather than cite itself. Each `{{napkin:NAME}}` token in a chapter is replaced at build time by the
result of running the arithmetic here, and every rendered block says so.

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
          ticks: int = TICKS) -> List[List[Fraction]]:
    """The engine's leapfrog scalar wave, started from rest, `ticks` times.

    Started from rest (`φ_old = φ_0`) for a reason that matters to the chapter: the rows of `Δ₀` sum
    to zero, so `Σφ` obeys `S' = 2S − S_prev`, and beginning with `S_prev = S_0` makes the total
    *exactly* constant for ever. The conserved total is not a property of the wave in general — it
    is a property of this rule started this way, and the assertion below is what holds us to it.
    """
    current = [Fraction(v) for v in CORNERS]
    previous = list(current)
    history = [list(current)]
    for _ in range(ticks):
        lap = laplacian(current, weights, lines)
        nxt = [2 * c - p - TICK_K * l for c, p, l in zip(current, previous, lap)]
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
        "| dots | lines | faces | inside |\n"
        "|---|---|---|---|\n"
        f"| {counts[0]} | {counts[1]} | {counts[2]} | {counts[3]} |"
    )
    return block("tetra_counts", body,
                 "the tetrahedron's census, and that its boundary closes twice (d∘d = 0 on both rungs)")


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
        "| face | its three line-numbers, walked round | loop |\n|---|---|---|\n"
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
    face_rows = " | ".join(f"**{number(f)}**" for f in face_numbers)
    face_heads = " | ".join(edge_name(face) for face in faces)
    inside_terms = walk_terms(c["d2"][0], face_numbers)
    body = (
        "This time the six line-numbers are given, not worked out from the corners — six arrows in "
        "their own right. So a face's loop need not be zero, and it is not:\n\n"
        f"| line | {line_rows} |\n"
        f"|---|{'---|' * len(lines)}\n"
        f"| arrow | {arrow_rows} |\n\n"
        f"| face | {face_heads} |\n"
        f"|---|{'---|' * len(faces)}\n"
        f"| how much goes round it | {face_rows} |\n\n"
        f"Now walk those four face-numbers around the inside, minding the signs: "
        f"{inside_terms} = **0**."
    )
    return block("tetra_inside_sum", body,
                 "four non-zero face-numbers from six freely chosen line-numbers, and their "
                 "oriented sum around the inside")


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
                 f"the engine's leapfrog scalar wave (φ′ = 2φ − φ_old − c²dt²Δ₀φ, c²dt² = "
                 f"{number(TICK_K)}) run {TICKS} ticks from rest on one tetrahedron with every line "
                 f"counting the same (⋆₁ = 1); the total is conserved exactly, and with nothing to "
                 f"damp it and no room to spread into, the whole world returns to its start every "
                 f"{repeat} ticks")


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
                 f"the same {TICKS} ticks with line {edge_name(DIALED_LINE)} counted double "
                 f"(⋆₁ = 2 there, 1 elsewhere) — the dial, on one line. The total is still conserved "
                 f"exactly and the four numbers still average to {number(average)}; what changed is "
                 f"the motion, which is now faster along {edge_name(DIALED_LINE)} than the rest")


TOKENS = {
    "tetra_counts": tetra_counts,
    "triangle_loop_example": triangle_loop_example,
    "tetra_face_loops": tetra_face_loops,
    "tetra_inside_sum": tetra_inside_sum,
    "slosh_table": slosh_table,
    "slosh_table_dialed": slosh_table_dialed,
}


def render(name: str) -> str:
    if name not in TOKENS:
        raise KeyError(name)
    return TOKENS[name]()


if __name__ == "__main__":
    for token in TOKENS:
        print(f"\n{'=' * 90}\n{token}\n{'=' * 90}")
        print(render(token))
