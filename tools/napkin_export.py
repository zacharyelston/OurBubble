#!/usr/bin/env python3
"""Dump every napkin number's underlying DATA to `demos/data/napkin.json`.

The demos under `demos/` recompute the book's chapters 1–4 in the reader's browser. That is the
whole point of them — a page that only *displayed* numbers Python had worked out would be a
screenshot with buttons — and it is also the whole risk: two implementations of the same arithmetic
are two places the book can disagree with itself.

So this file is the oracle. It exports the *data* behind each `{{napkin:…}}` token — the counts, the
matrices, the histories, the volumes, the ceilings — and deliberately **not** the prose those tokens
render. `demos/core.test.mjs` then runs the JavaScript core under node and asserts, value by value,
that what the browser would compute is exactly what `tools/napkin.py` and `tools/octahedron.py`
already assert. A demo cannot show a number the napkin did not compute, because the number it shows
is checked against this file before the book is allowed to build.

Two properties this file must have, and both are asserted at the bottom:

* **Exact, and readable as exact.** Every `Fraction` leaves here as `"n/d"` (or `"n"`), a string. No
  float is ever written, so the comparison on the JavaScript side is a string comparison against
  exact rational arithmetic rather than a tolerance.
* **Byte-identical across builds.** Sorted keys, fixed separators, a trailing newline, and no
  timestamp, version stamp or path anywhere in the payload. `check_edition.py` re-derives it and
  compares bytes, so a non-deterministic export fails the build rather than producing a diff nobody
  looks at.

The geometry the demos draw comes from here too — `canon.py`'s six net positions, its nine drawn
segments and its nineteen label placements — so the flat unfolded net in a demo is the net
`CANON.md` governs, not a second drawing of the same object.
"""

from __future__ import annotations

import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import canon      # noqa: E402
import napkin     # noqa: E402
import octahedron  # noqa: E402

TARGET = ROOT / "demos" / "data" / "napkin.json"


# ── exact serialisation ───────────────────────────────────────────────────────────────────────────


def frac(value: Fraction | int) -> str:
    """A rational as an exact string. `3` → `"3"`, `1/2` → `"1/2"`, `−1/2` → `"-1/2"`.

    ASCII hyphen, not the typeset minus `napkin.number()` prints: this is data crossing into another
    language, and the minus sign a reader sees is the presentation layer's business on both sides.
    """
    value = Fraction(value)
    text = str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    assert Fraction(text) == value, f"{value} does not round-trip through {text!r}"
    return text


def fracs(values: Sequence[Fraction | int]) -> List[str]:
    return [frac(value) for value in values]


def rows(matrix: Sequence[Sequence[Fraction | int]]) -> List[List[str]]:
    return [fracs(row) for row in matrix]


def point(p: Sequence[Fraction | int]) -> List[str]:
    return fracs(list(p))


# ── the object, and the two coming-home facts ─────────────────────────────────────────────────────


def complexes() -> Dict[str, Any]:
    """The ascending-simplex census on one, two, three and four dots, and the coboundaries.

    Four rungs of the same rule rather than only the tetrahedron, because chapter 1 walks up them:
    one dot has nothing that closes, two dots and a line still have nothing that closes, and the
    triangle is the first thing that does. The demo has to be able to show the *absence*, so the
    absence is exported.
    """
    out = {}
    for count in (1, 2, 3, 4):
        vertices = tuple(range(count))
        kinds = {str(k): [list(cell) for cell in napkin.simplices(vertices, k)]
                 for k in range(count)}
        boundaries = {}
        for k in range(count - 1):
            lo = napkin.simplices(vertices, k)
            hi = napkin.simplices(vertices, k + 1)
            boundaries[str(k)] = rows(napkin.coboundary(lo, hi))
        out[str(count)] = {"cells": kinds, "coboundary": boundaries}
    return out


def triangle() -> Dict[str, Any]:
    """Beat 14's walk, and beat 15's answer to "would any three numbers do that?".

    The second triple is the demo's own control and it is checked here rather than there: the claim
    beat 15 makes is *every time*, so the export carries a walk on numbers that are not the
    chapter's and asserts its sum is zero too.
    """
    def walk(values: Sequence[int]) -> Dict[str, Any]:
        vals = [Fraction(v) for v in values]
        steps = [(a, b, vals[b] - vals[a]) for a, b in ((0, 1), (1, 2), (2, 0))]
        total = sum(step[2] for step in steps)
        assert total == 0, f"the triangle's loop sum came out {total} on {values}"
        return {
            "values": fracs(vals),
            "steps": [{"from": napkin.NAMES[a], "to": napkin.NAMES[b], "difference": frac(d)}
                      for a, b, d in steps],
            "sum": frac(total),
        }

    return {"chapter": walk((2, 5, 1)), "another": walk((7, 7, -2))}


def tetrahedron() -> Dict[str, Any]:
    census = napkin.census()
    values = [Fraction(v) for v in napkin.CORNERS]
    differences = napkin.apply(census["d0"], values)
    face_loops = napkin.apply(census["d1"], differences)
    assert all(loop == 0 for loop in face_loops), f"a face loop came out non-zero: {face_loops}"

    arrows = [Fraction(a) for a in napkin.ARROWS]
    face_numbers = napkin.apply(census["d1"], arrows)
    inside = napkin.apply(census["d2"], face_numbers)
    assert all(value != 0 for value in face_numbers), "a face came out zero"
    assert inside == [Fraction(0)], f"the inside sum came out {inside}"

    # Each face walked the way the boundary operator takes it — outward — which is the form the
    # chapter's table prints and therefore the form the demo must reproduce.
    outward = [census["d2"][0][index] * value for index, value in enumerate(face_numbers)]
    assert sum(outward) == 0, f"the four outward face-numbers came to {sum(outward)}"

    return {
        "counts": {"dots": 4, "lines": 6, "faces": 4, "insides": 1},
        "names": list(napkin.NAMES),
        "line_names": [napkin.edge_name(line) for line in census["lines"]],
        "face_names": [napkin.edge_name(face) for face in census["faces"]],
        "corners": fracs(values),
        "differences": fracs(differences),
        "face_loops": fracs(face_loops),
        "arrows": fracs(arrows),
        "face_numbers": fracs(face_numbers),
        "outward_face_numbers": fracs(outward),
        "inside_sum": frac(inside[0]),
        "inside_incidence": [int(sign) for sign in census["d2"][0]],
    }


def motion() -> Dict[str, Any]:
    """Chapter 3's two runs: the one rule at `k = 1/2`, plain and with `AB` counted double."""
    census = napkin.census()
    lines = census["lines"]

    plain = napkin.slosh(napkin.unit_weights(lines), lines)
    weights = napkin.unit_weights(lines)
    weights[napkin.DIALED_LINE] = Fraction(2)
    dialed = napkin.slosh(weights, lines)
    assert plain != dialed, "doubling a line changed nothing — the dial is not wired up"

    def run(history) -> Dict[str, Any]:
        totals = {sum(row) for row in history}
        assert len(totals) == 1, f"the total moved: {totals}"
        return {
            "history": [fracs(row) for row in history],
            "totals": fracs([sum(row) for row in history]),
            "period": napkin.period(history),
        }

    return {
        "k": frac(napkin.TICK_K),
        "ticks": napkin.TICKS,
        "dialed_line": napkin.edge_name(napkin.DIALED_LINE),
        "dialed_weight": frac(Fraction(2)),
        "plain": run(plain),
        "dialed": run(dialed),
    }


# ── the shape between, and the shape it is half of ────────────────────────────────────────────────


def cut() -> Dict[str, Any]:
    data = octahedron.midpoint_cut()
    return {
        "dots": data["dots"],
        "corners": data["corners"],
        "middles": data["middles"],
        "tips": data["tips"],
        "octahedra": data["octahedra"],
        "tip_share": frac(data["tip_share"]),
        "tip_side": frac(data["tip_side"]),
        "core_share": frac(data["core_share"]),
        "oct_dots": data["oct_dots"],
        "oct_lines": data["oct_lines"],
        "oct_faces": data["oct_faces"],
        "oct_degree": data["oct_degree"],
        "opposite_pairs": [list(pair) for pair in data["opposite_pairs"]],
        "faces_at_a_tip": list(data["faces_at_a_tip"]),
        "faces_in_a_face": list(data["faces_in_a_face"]),
        "mid_names": list(octahedron.MID_NAMES),
        "mid_points": [point(p) for p in octahedron.MID_POINTS],
        "tet_corners": {name: point(p) for name, p in octahedron.TET_CORNERS.items()},
        "mid_lines": [list(line) for line in octahedron.mid_lines()],
        "mid_faces": [list(face) for face in octahedron.mid_faces()],
    }


def face_sum() -> Dict[str, Any]:
    data = octahedron.octahedron_boundary_sum()
    return {
        "arrows": fracs([Fraction(a) for a in data["arrows"]]),
        "face_numbers": fracs(data["face_numbers"]),
        "sum": frac(data["sum"]),
        "lines_walked_each_way": data["lines_walked_each_way"],
    }


def poke() -> Dict[str, Any]:
    data = octahedron.octahedron_poke_table()
    return {
        "k": frac(data["k"]),
        "poked": data["poked"],
        "opposite": data["opposite"],
        "crossing_ticks": data["crossing_ticks"],
        "home_ticks": data["home_ticks"],
        "period": data["period"],
        "history": [fracs(row) for row in data["history"]],
        "totals": fracs([sum(row) for row in data["history"]]),
    }


def stella() -> Dict[str, Any]:
    census = octahedron.stella_reader_census()
    twin = octahedron.second_tetrahedron()
    return {
        "dots": census["dots"],
        "lines": census["lines"],
        "middles": census["middles"],
        "tips": census["tips"],
        "pieces": census["pieces"],
        "middle_degree": census["middle_degree"],
        "tip_degree": census["tip_degree"],
        "in_tetrahedra": frac(census["stella_in_tetrahedra"]),
        "in_its_cube": frac(census["stella_in_its_cube"]),
        "names": list(octahedron.STELLA_READER_NAMES),
        "points": [point(p) for p in octahedron.stella_reader_points()],
        "edges": [list(line) for line in octahedron.stella_reader_lines()],
        "apex_names": list(twin["apex_names"]),
        "apex_share": frac(twin["apex_share"]),
        "added": twin["added"],
        "hull": twin["hull"],
    }


def refusal() -> Dict[str, Any]:
    ceilings = octahedron.napkin_ceilings()
    runaway = octahedron.stella_runaway()
    return {
        "tick": frac(ceilings["tick"]),
        "leapfrog_bound": ceilings["bound"],
        "ceilings": [
            {
                "dots": row["dots"],
                "stiffest": frac(row["stiffest"]),
                "bound": frac(row["bound"]),
                "book_tick_product": frac(row["book_tick_product"]),
                "holds": row["holds"],
            }
            for row in ceilings["rows"]
        ],
        "runaway": {
            "k": frac(runaway["k"]),
            "ticks": octahedron.RUNAWAY_TICKS,
            "look": [{"tick": tick, "biggest": frac(value)} for tick, value in runaway["look"]],
            "floors": [{"tick": tick, "floor": floor} for tick, floor in runaway["bounds"]],
            "printable_rows": runaway["printable_rows"],
            "push_at_a_middle": runaway["push_at_a_middle"],
            "never_returns": runaway["never_returns"],
            "stable_tried": [
                {"k": frac(entry["k"]), "printable": entry["printable"], "period": entry["period"]}
                for entry in runaway["stable_tried"]
            ],
        },
        "denominators_number_prints": list(octahedron.NAPKIN_DENOMINATORS),
    }


# ── the drawing, from the one place a tetrahedron net is drawn ─────────────────────────────────────


def net() -> Dict[str, Any]:
    """`canon.py`'s layout as data, so a demo draws the canonical net rather than a second one.

    Points leave here in `canon.py`'s own ring: `(x, u)` stands for the plane point `(x, u·√3)`,
    both halves exact rationals. The demo projects them with the same `√3`, the same scale and the
    same padding, which is why a still rendered by a demo and the SVG `canon.py` emits put every
    label in the same place.
    """
    x_min, y_max, width, height = canon.EXTENT
    return {
        "side": frac(canon.SIDE),
        "sqrt3": frac(canon.SQRT3),
        "scale": frac(canon.SCALE),
        "pad": frac(canon.PAD),
        "extent": {"x_min": frac(x_min), "y_max": frac(y_max),
                   "width": frac(width), "height": frac(height)},
        "published": {name: point(p) for name, p in canon.PUBLISHED.items()},
        "panels": [
            {"face": canon.name(face), "positions": [point(p) for p in positions]}
            for face, positions in canon.PANELS
        ],
        "segments": [
            {"line": canon.name(line), "panel": canon.name(face),
             "from": point(start), "to": point(end)}
            for line, (start, end), face in canon.SEGMENTS
        ],
        "labels": (
            [{"kind": "dot", "text": canon.name(cell), "at": point(at), "panel": canon.name(face)}
             for cell, at, face in canon.vertex_labels()]
            + [{"kind": "line", "text": canon.name(cell), "at": point(at),
                "panel": canon.name(face)}
               for cell, at, face in canon.line_labels()]
            + [{"kind": "face", "text": canon.name(cell), "at": point(at),
                "panel": canon.name(face)}
               for cell, at, face in canon.face_labels()]
        ),
    }


# ── the payload ───────────────────────────────────────────────────────────────────────────────────


def payload() -> Dict[str, Any]:
    """Everything the demos may display, and nothing about how they display it.

    Deliberately absent: every caption, every table heading and every worded fraction. Those are
    `napkin.py`'s rendering and the chapters' prose, and a demo that copied them would be quoting
    the book rather than computing it. What crosses this boundary is arithmetic.
    """
    return {
        "complexes": complexes(),
        "triangle": triangle(),
        "tetrahedron": tetrahedron(),
        "motion": motion(),
        "cut": cut(),
        "face_sum": face_sum(),
        "poke": poke(),
        "stella": stella(),
        "refusal": refusal(),
        "net": net(),
    }


def text() -> str:
    """The export as bytes-to-be. Sorted keys, fixed separators, one trailing newline."""
    return json.dumps(payload(), sort_keys=True, indent=2, separators=(",", ": "),
                      ensure_ascii=True) + "\n"


def no_floats(node: Any, where: str = "$") -> None:
    """Refuse a float anywhere in the payload, by walking it.

    The rule the whole export rests on is that a number crossing into JavaScript is an exact
    rational written as a string. A float would be silently accepted by `json.dumps` and silently
    parsed on the other side, and the cross-check would then be comparing two roundings.
    """
    if isinstance(node, float):
        raise AssertionError(f"{where} is a float ({node!r}) — every number leaves here as an exact "
                             f"string, so the browser's arithmetic can be compared, not approximated")
    if isinstance(node, dict):
        for key, value in node.items():
            assert isinstance(key, str), f"{where}: the key {key!r} is not a string"
            no_floats(value, f"{where}.{key}")
    elif isinstance(node, (list, tuple)):
        for index, value in enumerate(node):
            no_floats(value, f"{where}[{index}]")


def self_test() -> str:
    """What this export guarantees, checked — and returned as one line for `status()` to print."""
    first = text()
    second = text()
    assert first == second, "two exports of the same commit differ — the payload is not deterministic"
    data = json.loads(first)
    no_floats(data)

    # The handful of numbers the chapters' own sentences lean on, re-asserted here so that a demo
    # built against this file cannot be built against a silently changed one.
    assert data["tetrahedron"]["counts"] == {"dots": 4, "lines": 6, "faces": 4, "insides": 1}
    assert data["tetrahedron"]["inside_sum"] == "0"
    assert data["motion"]["k"] == "1/2" and data["motion"]["plain"]["period"] == 4
    assert data["cut"]["tip_share"] == "1/8" and data["cut"]["core_share"] == "1/2"
    assert (data["cut"]["oct_dots"], data["cut"]["oct_lines"], data["cut"]["oct_faces"]) \
        == (6, 12, 8)
    assert data["poke"]["crossing_ticks"] == 2 and data["poke"]["home_ticks"] == 3
    assert data["poke"]["period"] == 12
    assert data["face_sum"]["sum"] == "0"
    assert (data["stella"]["dots"], data["stella"]["lines"]) == (14, 36)
    assert data["refusal"]["runaway"]["printable_rows"] == 3
    assert [row["holds"] for row in data["refusal"]["ceilings"]] == [True, True, False]
    assert len(data["net"]["segments"]) == 9 and len(data["net"]["labels"]) == 19

    return (f"{len(first)} bytes, deterministic, no float anywhere — "
            f"{len(data)} groups for demos/core.test.mjs")


def write() -> bool:
    """Write the export. True if the file on disk changed.

    Written to disk on every build for the same reason `preprocessor.py` writes the appendix: it
    puts the export under `git status`, so a change to the napkin that moves a demo's numbers shows
    up as a dirty tree rather than as a page that quietly disagrees with the book.
    """
    body = text()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    existing = TARGET.read_text(encoding="utf-8") if TARGET.exists() else None
    if existing == body:
        return False
    TARGET.write_text(body, encoding="utf-8")
    return True


def main() -> int:
    line = self_test()
    changed = write()
    print(f"napkin export: {line}")
    print(f"napkin export: {'rewrote' if changed else 'unchanged'} "
          f"{TARGET.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
