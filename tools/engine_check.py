#!/usr/bin/env python3
"""The oracle as guard — recompute the book's arithmetic in Python and demand the engine's bytes.

Until 2026-09-02 `tools/napkin.py` and `tools/octahedron.py` **were** the book's engine: they
computed the numbers the pages print, and `demos/core.mjs` computed them a second time for the
browser. The owner's decision replaced all of it with one engine — UniForge's `napkin` crate,
vendored under `engine/` and pinned by `engine.lock` — and left the Python where it was, with one
job: to disagree.

That is what this file is. It runs the whole Python chain — `oracle.py`'s complex, coboundaries and
leapfrog; `octahedron.py`'s cut, crossing, surface, threading and ceilings; `canon.py`'s net;
`oracle.kinds_of_place`'s wrapped world — and requires the result to be **byte-identical** to what
the engine emitted. Not close, not equal to a tolerance: the same bytes, in the same canonical form,
including the newline at the end.

Two implementations that must agree exactly are worth more than one implementation nobody can check,
and they are worth it in a specific direction: the crate is a thousand lines of Rust with a 1024-bit
integer in it, and this is Python with `fractions.Fraction`. They share no code, no arithmetic
library and no language. When they agree on 22 969 bytes, the number on the page is a fact about the
object rather than a fact about one program.

**What this is not.** It is not the vendoring check. Whether `engine/` holds the bytes `engine.lock`
says, whether a fresh build from the pinned commit reproduces them, and whether the WebAssembly
module is the same engine as the JSON — those are `check_edition.py`'s `check_engine()`, which runs
in every clone with no engine source at all. This check is about the *arithmetic*, and it is why an
edited number in `engine/napkin.json` would have to survive both a hash and an independent
recomputation to reach a page.

Run by `tools/check.sh` in tier 0, beside `octahedron.py`'s own assertions.

FIREWALL: a toy DEC lattice's arithmetic, checked against itself. Nothing here is a claim about
nature. See `../FIREWALL.md`.
"""

from __future__ import annotations

import json
import os
import sys
from fractions import Fraction
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import napkin         # noqa: E402  (needs the path above)
import napkin_export  # noqa: E402
import octahedron     # noqa: E402
import oracle         # noqa: E402

PAYLOAD = ROOT / "engine" / "napkin.json"
ROWS = ROOT / "engine" / "rows.json"


def first_difference(left: str, right: str) -> str:
    """Where two payloads stop agreeing, in a form someone can act on.

    A byte offset is useless on 23 kB of JSON, so this reports the line, and — because the two are
    the same shape — the key path the line sits under is usually visible in the line itself.
    """
    left_lines = left.splitlines()
    right_lines = right.splitlines()
    for index, (a, b) in enumerate(zip(left_lines, right_lines), start=1):
        if a != b:
            return f"line {index}: the oracle has {a.strip()!r}, the engine has {b.strip()!r}"
    if len(left_lines) != len(right_lines):
        return (f"the oracle wrote {len(left_lines)} lines and the engine {len(right_lines)} — one "
                f"payload carries a group the other does not")
    return "the two differ only in trailing bytes — check the final newline"


def check_payload(errors: List[str]) -> str:
    """`engine/napkin.json` against the Python that used to produce it. Byte for byte."""
    recomputed = napkin_export.text()
    vendored = PAYLOAD.read_text(encoding="utf-8")
    if recomputed != vendored:
        errors.append(
            f"engine check: the Python oracle and {PAYLOAD.relative_to(ROOT)} disagree "
            f"({len(recomputed)} bytes recomputed, {len(vendored)} vendored). "
            f"{first_difference(recomputed, vendored)}. Either the vendored engine was edited — see "
            f"engine.lock — or the oracle drifted, and whichever it is, one of them is now printing "
            f"a number the other does not compute."
        )
        return "unavailable"
    return f"{len(vendored)} bytes, byte-for-byte"


def hops(lines: List[tuple], dots: int, source: int) -> List[int]:
    """Breadth-first distance from `source`, for R10. **A check's own arithmetic, not the book's.**

    The oracle never needed this — no token counts hops — so rather than grow `oracle.py` a function
    the book does not use, it lives here, where its only reader is the comparison below.
    """
    neighbours: List[List[int]] = [[] for _ in range(dots)]
    for a, b in lines:
        neighbours[a].append(b)
        neighbours[b].append(a)
    distance = [-1] * dots
    distance[source] = 0
    queue = [source]
    while queue:
        here = queue.pop(0)
        for there in neighbours[here]:
            if distance[there] < 0:
                distance[there] = distance[here] + 1
                queue.append(there)
    return distance


def check_rows(errors: List[str]) -> str:
    """`engine/rows.json` — R07, R10 and R19 — against the same Python, row by row.

    Two things the wrapped world's payload cannot carry are asserted here as well, because they are
    claims the chapter makes and the export's shape has no room for them: that each kind of place is
    exactly one value of `(x+y+z) mod 3`, and that the three kinds use all three values. The engine
    returns the sizes, not the labelling, so this is the only place either can be checked at all.
    """
    everything = json.loads(ROWS.read_text(encoding="utf-8"))
    vendored = everything["world"]
    problems = []

    # R07 — the one rule on the triangle, at a tick that is not dyadic and at the book's own.
    triangle = oracle.census([0, 1, 2])
    lines = triangle["lines"]
    corners = [Fraction(2), Fraction(5), Fraction(2)]
    for name, k in (("at_two_thirds", Fraction(2, 3)), ("at_the_book_tick", Fraction(1, 2))):
        run = everything["triangle_motion"][name]
        history = oracle.slosh(oracle.unit_weights(lines), lines, ticks=run["ticks"],
                               initial=corners, k=k)
        rendered = [[napkin_export.frac(value) for value in row] for row in history]
        if rendered != run["history"] or oracle.period(history) != run["period"]:
            problems.append(
                f"R07 {name}: the oracle's run of the triangle at k = {k} is not the vendored one "
                f"(period {oracle.period(history)} against {run['period']})"
            )

    # R10 — the tetrahedron has no room: one hop from any dot to any other.
    tetra = oracle.census()
    room = everything["no_room"]
    distances = [hops(tetra["lines"], len(tetra["dots"]), source)
                 for source in range(len(tetra["dots"]))]
    if distances != room["hops"] or max(max(row) for row in distances) != room["diameter"]:
        problems.append(
            f"R10: the oracle's hop table is {distances}, and the engine vendored {room['hops']} "
            f"with diameter {room['diameter']}"
        )

    for name, cut in (("screw", oracle.screw111), ("control", oracle.uniform_cut)):
        kinds, sizes, labels = oracle.kinds_of_place(oracle.TORUS_MIN, cut)
        expected = vendored[name]
        if [kinds, sizes, 14, oracle.TORUS_MIN] != [
            expected["kinds"], expected["sizes"], expected["degree"], expected["side"]
        ]:
            problems.append(
                f"the {name} run: the oracle counts {kinds} kind(s) of size {sizes} on a "
                f"{oracle.TORUS_MIN}³ world; the engine vendored {expected}"
            )
        if name == "screw":
            by_kind = {}
            for point, kind in labels.items():
                by_kind.setdefault(kind, set()).add(sum(point) % 3)
            if not all(len(values) == 1 for values in by_kind.values()):
                problems.append(f"a kind of place spans more than one position rule: {by_kind}")
            if {next(iter(values)) for values in by_kind.values()} != {0, 1, 2}:
                problems.append(f"the three kinds do not use all three positions: {by_kind}")

    kinds, sizes, _ = oracle.kinds_of_place(oracle.TORUS_CHECK, oracle.screw111)
    bigger = vendored["bigger"]
    if [kinds, sizes] != [bigger["kinds"], bigger["sizes"]]:
        problems.append(
            f"the {oracle.TORUS_CHECK}³ world: the oracle counts {kinds} kind(s) of size {sizes}; "
            f"the engine vendored {bigger}"
        )

    for problem in problems:
        errors.append(f"engine check: {problem}")
    if problems:
        return "unavailable"
    return (f"R07 both ticks, R10 diameter {room['diameter']}, R19 "
            f"{vendored['screw']['kinds']} kinds on {oracle.TORUS_MIN}³ and "
            f"{vendored['bigger']['kinds']} on {oracle.TORUS_CHECK}³ — recomputed and identical")


def running(terms: List[Fraction]) -> List[Fraction]:
    """The sum building term by term. **A check's own arithmetic, not the book's** — like `hops`."""
    out: List[Fraction] = []
    total = Fraction(0)
    for term in terms:
        total += term
        out.append(total)
    return out


def printable_rows(history) -> int:
    """How many rows of a run `napkin.number` will write down before it refuses."""
    for index, row in enumerate(history):
        for value in row:
            try:
                napkin.number(value)
            except AssertionError:
                return index
    return len(history)


def walk(vertices, degree: int, index: int, values: List[Fraction]) -> dict:
    """One walk's terms in the order a reader takes them, and the sum building term by term.

    A **face** is walked as the cycle `A→B→C→A`, which is not the coboundary's column order; anything
    else has no cycle and is walked in the coboundary row's own order. The total must be the same
    either way, and that is asserted here rather than assumed: a re-ordering that changed the sum
    would be a different computation wearing the same name.
    """
    names = "ABCD"
    cells_lo = oracle.simplices(vertices, degree)
    cells_hi = oracle.simplices(vertices, degree + 1)
    row = oracle.coboundary(cells_lo, cells_hi)[index]

    steps: List[tuple] = []
    if degree == 1:
        cell = cells_hi[index]
        for step in range(3):
            low, high = cell[step], cell[(step + 1) % 3]
            line = (min(low, high), max(low, high))
            sign = 1 if low < high else -1
            steps.append((line, cells_lo.index(line), sign, sign * values[cells_lo.index(line)]))
        order = "cycle"
    else:
        for column, sign in enumerate(row):
            if sign != 0:
                steps.append((cells_lo[column], column, int(sign), sign * values[column]))
        order = "incidence"

    terms = [term for _, _, _, term in steps]
    total = sum(terms)
    assert total == sum(sign * values[c] for c, sign in enumerate(row) if sign != 0), (
        "the walk's order changed its sum, which it must never do"
    )
    return {
        "cell": "".join(names[v] for v in cells_hi[index]),
        "cell_dots": list(cells_hi[index]),
        "degree": degree,
        "index": index,
        "order": order,
        "running": [napkin_export.frac(v) for v in running(terms)],
        "signs": [sign for _, _, sign, _ in steps],
        "step_cells": [column for _, column, _, _ in steps],
        "steps": ["".join(names[v] for v in cell) for cell, _, _, _ in steps],
        "sum": napkin_export.frac(total),
        "terms": [napkin_export.frac(v) for v in terms],
        "values": [napkin_export.frac(v) for v in values],
    }


def compare(where: str, recomputed: dict, vendored: dict, problems: List[str]) -> set:
    """Demand every field this check computed, byte for byte, and report what it did not compute.

    The return value is the set of vendored keys the recomputation had nothing to say about. It is
    printed by the caller whether it is empty or not: a guard that quietly checks four fields of six
    is worse than no guard, because it reads like six.
    """
    for key, value in recomputed.items():
        if key not in vendored:
            problems.append(f"{where}: the engine vendored no {key!r}")
        elif vendored[key] != value:
            problems.append(
                f"{where}.{key}: the oracle recomputes {value!r} and the engine vendored "
                f"{vendored[key]!r}"
            )
    return set(vendored) - set(recomputed)


def check_gaps(errors: List[str]) -> str:
    """`engine/rows.json` → `gaps` — the five rows of `lab/napkin/0003`, recomputed in Python.

    The five are the demos' engine gaps: the dial, the outward eight-face sum, the two-dot complex,
    the triangle's tick certificate, and the running partial sums along a walk. Three of them the
    oracle has always been able to compute and was never asked to (`oracle.slosh` with one weight
    changed, `octahedron.octahedron_boundary_sum`, `oracle.census([0, 1])`); two are computed here,
    from the oracle's own coboundaries and Laplacian, for the same reason `hops` is.

    Every field this function computes is demanded byte for byte. Every vendored field it does *not*
    compute is named in the summary line, so "the gaps check passed" can never mean "the gaps check
    looked at three of thirteen keys".
    """
    everything = json.loads(ROWS.read_text(encoding="utf-8"))
    if "gaps" not in everything:
        errors.append("engine check: engine/rows.json carries no `gaps` group — the engine was "
                      "vendored from a commit before lab/napkin/0003")
        return "unavailable"
    vendored = everything["gaps"]
    problems: List[str] = []
    unchecked: List[str] = []

    def note(where: str, keys: set) -> None:
        unchecked.extend(f"{where}.{key}" for key in sorted(keys))

    # G01 — the dial: the tetrahedron's run with AB counted double.
    tetra = oracle.census()
    lines = tetra["lines"]
    weights = oracle.unit_weights(lines)
    weights[lines[0]] = Fraction(2)
    corners = [Fraction(v) for v in oracle.CORNERS]
    history = oracle.slosh(weights, lines, ticks=10, initial=corners, k=Fraction(1, 2))
    note("dial", compare("dial", {
        "history": [[napkin_export.frac(v) for v in row] for row in history],
        "k": napkin_export.frac(Fraction(1, 2)),
        "object": "tetrahedron",
        "period": oracle.period(history),
        "printable_rows": printable_rows(history),
        "ticks": 10,
        "totals": [napkin_export.frac(sum(row)) for row in history],
        "weights": [napkin_export.frac(weights[line]) for line in lines],
    }, vendored["dial"], problems))

    # G02 — the outward eight-face sum, per face, with the cycles the walk used.
    oct_lines, oct_faces = octahedron.mid_lines(), octahedron.mid_faces()
    arrows = {line: Fraction(v) for line, v in zip(oct_lines, octahedron.MID_ARROWS)}
    cycles, numbers = [], []
    for face in oct_faces:
        start = face.index(min(face))
        cycle = [face[(start + step) % 3] for step in range(3)]
        cycles.append(cycle)
        total = Fraction(0)
        for step in range(3):
            low, high = cycle[step], cycle[(step + 1) % 3]
            total += arrows[(min(low, high), max(low, high))] * (1 if low < high else -1)
        numbers.append(total)
    note("outward_face_sum", compare("outward_face_sum", {
        "arrows": [napkin_export.frac(Fraction(a)) for a in octahedron.MID_ARROWS],
        "cycles": cycles,
        "cycle_names": [[octahedron.MID_NAMES[i] for i in cycle] for cycle in cycles],
        "face_numbers": [napkin_export.frac(v) for v in numbers],
        "lines_walked_each_way": 12,
        "object": "octahedron",
        "orientation": "outward",
        "running": [napkin_export.frac(v) for v in running(numbers)],
        "sum": napkin_export.frac(sum(numbers)),
    }, vendored["outward_face_sum"], problems))

    # G03 — two dots and a line: no closed walk exists, at either degree.
    two = oracle.census([0, 1])
    values = [Fraction(2), Fraction(5)]
    differences = oracle.apply(two["d0"], values)
    assert oracle.simplices([0, 1], 2) == [], "two dots and a line have no face"
    note("two_dots.degree_0", compare("two_dots.degree_0", {
        "closed_walks": 0, "degree": 0, "object": "two-dots",
        "loops": [napkin_export.frac(v) for v in differences],
        "sum": napkin_export.frac(sum(differences)),
        "values": [napkin_export.frac(v) for v in values],
    }, vendored["two_dots"]["degree_0"], problems))
    note("two_dots.degree_1", compare("two_dots.degree_1", {
        "closed_walks": 0, "degree": 1, "object": "two-dots", "loops": [],
        "sum": napkin_export.frac(Fraction(0)),
        "values": [napkin_export.frac(v) for v in differences],
    }, vendored["two_dots"]["degree_1"], problems))

    # G04 — the triangle's ceiling: λ = 3 with an integer eigenvector, so the bound is 4/3.
    triangle = oracle.census([0, 1, 2])
    matrix = octahedron.laplacian_matrix(3, triangle["lines"])
    vector = [Fraction(-1), Fraction(1), Fraction(0)]
    applied = [sum(matrix[r][c] * vector[c] for c in range(3)) for r in range(3)]
    assert applied == [3 * v for v in vector], f"Δ₀v ≠ 3v on the triangle: {applied}"
    bound = Fraction(4, 3)
    for name, tick in (("at_the_book_tick", Fraction(1, 2)), ("at_the_bound", bound)):
        note(f"triangle_certificate.{name}", compare(
            f"triangle_certificate.{name}",
            {
                "bound": napkin_export.frac(bound), "eigenvalue": 3, "eigenvector": [-1, 1, 0],
                "holds": tick < bound, "k": napkin_export.frac(tick), "object": "triangle",
            },
            vendored["triangle_certificate"][name], problems))

    # G05 — the three walks, each with its sum building term by term.
    triangle_differences = oracle.apply(triangle["d0"], [Fraction(2), Fraction(5), Fraction(1)])
    tetra_arrows = [Fraction(a) for a in oracle.ARROWS]
    tetra_faces = oracle.apply(tetra["d1"], tetra_arrows)
    for name, computed in (
        ("triangle_face", walk([0, 1, 2], 1, 0, triangle_differences)),
        ("tetrahedron_face", walk([0, 1, 2, 3], 1, 0, tetra_arrows)),
        ("tetrahedron_inside", walk([0, 1, 2, 3], 2, 0, tetra_faces)),
    ):
        computed["object"] = "triangle" if name == "triangle_face" else "tetrahedron"
        note(f"walks.{name}", compare(f"walks.{name}", computed, vendored["walks"][name], problems))

    for problem in problems:
        errors.append(f"engine check: {problem}")
    if problems:
        return "unavailable"
    if unchecked:
        return (f"G01–G05 recomputed and identical, EXCEPT {len(unchecked)} vendored field(s) this "
                f"check does not compute: {', '.join(unchecked)}")
    return "G01–G05 recomputed and identical — every vendored field, none unchecked"


def main() -> int:
    errors: List[str] = []
    payload = check_payload(errors)
    rows = check_rows(errors)
    gaps = check_gaps(errors)
    for problem in errors:
        print(problem, file=sys.stderr)
    if errors:
        return 1
    print(f"engine_check.py: the oracle reproduces engine/napkin.json — {payload} · "
          f"engine/rows.json — {rows} · gaps — {gaps}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
