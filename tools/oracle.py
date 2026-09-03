#!/usr/bin/env python3
"""The Python oracle — the book's chapters 1–5 arithmetic, kept as a **check** and nothing else.

**This module is not the engine any more.** Until 2026-09-02 it was: `tools/napkin.py` computed the
numbers the book prints, `demos/core.mjs` computed them again for the browser, and UniForge's
`napkin` crate computed them a third time. Three implementations of one arithmetic are three places
a book can disagree with itself, and the owner's decision was to keep one — the crate — and make the
other two renderers of what it emits.

So what lives here is the arithmetic as Python had it, moved out of the renderer intact, and the one
job it has left is to disagree. `tools/engine_check.py` runs it on every `make check` and asserts
its output is **byte-identical** to the vendored `engine/napkin.json` and `engine/rows.json`. That
is the same relationship `record/` has with the engine's own files: an independent copy whose only
purpose is to make drift into a failure with a name on it.

Nothing on the rendering path may import this module. `tools/napkin.py` reads `engine/` through
`tools/engine.py` and computes nothing; if this file were reachable from a token again there would
be two engines again, and `check_edition.py`'s engine check says so by name.

**Everything is exact.** `fractions.Fraction` throughout. There is no floating point anywhere in
this file, so two runs of the same commit cannot differ.

The object and the rule are the engine's, replicated faithfully:

* the complete complex on 4 dots, ascending orientation, and the simplicial coboundary
  `(d f)(σ) = Σ_i (−1)^i f(σ minus its i-th vertex)` — `core/geom/src/mesh.rs`'s incidence signs;
* one tick is `step_scalar_wave` from `core/solve/src/wave_solver.rs`:
  `φ' = 2φ − φ_old − c²dt² Δ₀φ`, with `Δ₀ = ⋆₀⁻¹ d₀ᵀ ⋆₁ d₀` from `core/dec/src/operators.rs`
  (`apply_laplacian_0_metric`). With `⋆₀ = 1` and `⋆₁ = w_e` that is exactly
  `(Δφ)_i = Σ_j w_ij (φ_i − φ_j)`;
* the wrapped world is `mesh_3d_chiral_tetoct_periodic` with `chiral_oct_screw111`.

FIREWALL: this is a toy DEC lattice's arithmetic. Nothing here is a claim about nature. See
`../FIREWALL.md`.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations
from typing import Dict, List, Sequence, Tuple

from napkin import NAMES, VERTICES  # noqa: F401 — the book's names; the renderer owns them

# ── the object ────────────────────────────────────────────────────────────────────────────────────


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



DIALED_LINE: Tuple[int, ...] = (0, 1)


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
