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

import napkin_export  # noqa: E402  (needs the path above)
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


def main() -> int:
    errors: List[str] = []
    payload = check_payload(errors)
    rows = check_rows(errors)
    for problem in errors:
        print(problem, file=sys.stderr)
    if errors:
        return 1
    print(f"engine_check.py: the oracle reproduces engine/napkin.json — {payload} · "
          f"engine/rows.json — {rows}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
