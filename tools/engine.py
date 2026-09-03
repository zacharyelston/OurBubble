#!/usr/bin/env python3
"""The vendored engine, read — the one source of every number the book prints.

Since 2026-09-02 there is one engine for the book and its demos: UniForge's `napkin` crate,
registered as `lab/napkin/0001`. Its output is vendored under [`engine/`](../engine/PROVENANCE.md)
and pinned by [`engine.lock`](../engine.lock), exactly the way `record/` is pinned. This module is
the only door between that data and the pages: `tools/napkin.py` renders what it returns and
computes nothing, so a number on a page can be traced to a commit rather than to a second
implementation that agreed with one for a while.

**Everything comes back exact.** Every rational crosses the boundary as an `"n/d"` string and is
parsed here into a `Fraction`. No float is constructed anywhere in this file; the engine refuses to
write one, and the parsing side refuses to invent one.

**Nothing here computes.** The one thing it derives is arrangement — turning the payload's flat lists
into the tuples the renderers ask for. If a value has to be worked out, it is missing from the
engine and belongs in a register row, not in this file.

FIREWALL: the engine computes a toy DEC lattice. Nothing it emits is a claim about nature. See
`../FIREWALL.md`.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = ROOT / "engine"
PAYLOAD = ENGINE_DIR / "napkin.json"
ROWS = ENGINE_DIR / "rows.json"

_CACHE: Dict[Path, Dict[str, Any]] = {}


def _load(path: Path) -> Dict[str, Any]:
    """Parse one vendored file, once per process.

    The failure is written out rather than left as a `FileNotFoundError` three frames deep, because
    the fix is a specific command and the reader of the traceback is usually meeting `engine/` for
    the first time.
    """
    if path not in _CACHE:
        if not path.exists():
            raise SystemExit(
                f"the vendored engine is missing {path.relative_to(ROOT)}. It is committed, so this "
                f"is a broken checkout rather than a build step you skipped — restore it with "
                f"`git checkout -- engine/`, or rebuild it from a UniForge checkout at the pinned "
                f"commit with `tools/build_engine.sh` (see engine.lock)."
            )
        _CACHE[path] = json.loads(path.read_text(encoding="utf-8"))
    return _CACHE[path]


def payload() -> Dict[str, Any]:
    """`engine/napkin.json` — the emitter's canonical payload, byte-identical to the oracle's."""
    return _load(PAYLOAD)


def rows_payload() -> Dict[str, Any]:
    """`engine/rows.json` — R07, R10 and R19: the rows the pinned payload has no room for."""
    return _load(ROWS)


# ── exact values ─────────────────────────────────────────────────────────────────────────────────


def q(text: str) -> Fraction:
    """An exact rational from the engine's `"n/d"` form.

    The round-trip is asserted for the same reason the export asserts it on the way out: this is the
    seam where an exact number could quietly become an approximate one, and it is cheap to hold
    shut from both sides.
    """
    value = Fraction(text)
    written = (str(value.numerator) if value.denominator == 1
               else f"{value.numerator}/{value.denominator}")
    assert written == text, (
        f"{text!r} is not a rational in lowest terms — the engine writes every value reduced, so "
        f"this payload has been edited or was written by something else"
    )
    return value


def qs(values: Sequence[str]) -> List[Fraction]:
    return [q(value) for value in values]


def matrix(rows: Sequence[Sequence[str]]) -> List[List[int]]:
    """An incidence matrix as whole numbers. The signs are `−1 · 0 · +1` and nothing else."""
    out = []
    for row in rows:
        entries = []
        for cell in row:
            value = q(cell)
            assert value.denominator == 1 and value in (-1, 0, 1), (
                f"an incidence entry came back as {cell!r} — the signs are −1, 0 and +1"
            )
            entries.append(int(value))
        out.append(entries)
    return out


def cells(items: Sequence[Sequence[int]]) -> List[Tuple[int, ...]]:
    return [tuple(item) for item in items]


# ── the groups, as the renderers ask for them ────────────────────────────────────────────────────


def complex_on(dots: int) -> Dict[str, Any]:
    """One rung of the ascending census: the cells of each dimension, and the three coboundaries.

    Four rungs are exported — one dot, two, three, four — because chapter 1 walks up them and the
    absence of anything that closes below three dots is as much a result as the triangle is.
    """
    rung = payload()["complexes"][str(dots)]
    return {
        "dots": cells(rung["cells"]["0"]),
        "lines": cells(rung["cells"].get("1", [])),
        "faces": cells(rung["cells"].get("2", [])),
        "insides": cells(rung["cells"].get("3", [])),
        "d0": matrix(rung["coboundary"].get("0", [])),
        "d1": matrix(rung["coboundary"].get("1", [])),
        "d2": matrix(rung["coboundary"].get("2", [])),
    }


def tetrahedron() -> Dict[str, Any]:
    """Chapters 1 and 2's whole object: its census, its corner values, and both sums that close."""
    group = payload()["tetrahedron"]
    return {
        "counts": group["counts"],
        "names": tuple(group["names"]),
        "line_names": list(group["line_names"]),
        "face_names": list(group["face_names"]),
        "corners": qs(group["corners"]),
        "differences": qs(group["differences"]),
        "face_loops": qs(group["face_loops"]),
        "arrows": qs(group["arrows"]),
        "face_numbers": qs(group["face_numbers"]),
        "outward_face_numbers": qs(group["outward_face_numbers"]),
        "inside_incidence": [int(sign) for sign in group["inside_incidence"]],
        "inside_sum": q(group["inside_sum"]),
    }


def triangle() -> Dict[str, Any]:
    """The chapter's triangle: three corner values, the three differences, and their sum."""
    group = payload()["triangle"]["chapter"]
    return {
        "values": qs(group["values"]),
        "steps": [(step["from"], step["to"], q(step["difference"])) for step in group["steps"]],
        "sum": q(group["sum"]),
    }


def motion() -> Dict[str, Any]:
    """Both runs of chapter 3: every line counting one, and the same run with `AB` counted double."""
    group = payload()["motion"]
    return {
        "k": q(group["k"]),
        "ticks": group["ticks"],
        "dialed_line": group["dialed_line"],
        "dialed_weight": q(group["dialed_weight"]),
        "plain": {"history": [qs(row) for row in group["plain"]["history"]],
                  "period": group["plain"]["period"],
                  "totals": qs(group["plain"]["totals"])},
        "dialed": {"history": [qs(row) for row in group["dialed"]["history"]],
                   "period": group["dialed"]["period"],
                   "totals": qs(group["dialed"]["totals"])},
    }


def cut() -> Dict[str, Any]:
    """The midpoint cut, and the shape it leaves between the tips."""
    group = payload()["cut"]
    return {
        "dots": group["dots"], "tips": group["tips"], "octahedra": group["octahedra"],
        "middles": group["middles"], "corners": group["corners"],
        "tip_share": q(group["tip_share"]), "core_share": q(group["core_share"]),
        "faces_at_a_tip": list(group["faces_at_a_tip"]),
        "faces_in_a_face": list(group["faces_in_a_face"]),
        "oct_dots": group["oct_dots"], "oct_lines": group["oct_lines"],
        "oct_faces": group["oct_faces"], "oct_degree": group["oct_degree"],
        "opposite_pairs": [tuple(pair) for pair in group["opposite_pairs"]],
        "mid_names": tuple(group["mid_names"]),
        "mid_lines": cells(group["mid_lines"]),
        "mid_faces": cells(group["mid_faces"]),
    }


def face_sum() -> Dict[str, Any]:
    """Twelve freely chosen arrows on the shape between the tips, and what goes round its faces."""
    group = payload()["face_sum"]
    return {
        "arrows": qs(group["arrows"]),
        "face_numbers": qs(group["face_numbers"]),
        "lines_walked_each_way": group["lines_walked_each_way"],
        "sum": q(group["sum"]),
    }


def poke() -> Dict[str, Any]:
    """The crossing: a poke of 1 on one dot of the shape between the tips, run at the book's tick."""
    group = payload()["poke"]
    return {
        "k": q(group["k"]),
        "poked": group["poked"], "opposite": group["opposite"],
        "crossing_ticks": group["crossing_ticks"], "home_ticks": group["home_ticks"],
        "period": group["period"],
        "history": [qs(row) for row in group["history"]],
        "totals": qs(group["totals"]),
    }


def stella() -> Dict[str, Any]:
    """The second tetrahedron, threaded through the first."""
    group = payload()["stella"]
    return {
        "dots": group["dots"], "lines": group["lines"],
        "middles": group["middles"], "tips": group["tips"], "added": group["added"],
        "middle_degree": group["middle_degree"], "tip_degree": group["tip_degree"],
        "apex_share": q(group["apex_share"]),
        "apex_names": list(group["apex_names"]),
        "names": list(group["names"]),
        "edges": cells(group["edges"]),
        "in_tetrahedra": q(group["in_tetrahedra"]),
        "in_its_cube": q(group["in_its_cube"]),
    }


def refusal() -> Dict[str, Any]:
    """The three tick ceilings, and what the book's own tick does to the object that is over its."""
    group = payload()["refusal"]
    runaway = group["runaway"]
    return {
        "tick": q(group["tick"]),
        "leapfrog_bound": group["leapfrog_bound"],
        "ceilings": [
            {"dots": row["dots"], "bound": q(row["bound"]), "holds": row["holds"],
             "stiffest": q(row["stiffest"])}
            for row in group["ceilings"]
        ],
        "runaway": {
            "k": q(runaway["k"]),
            "ticks": runaway["ticks"],
            "printable_rows": runaway["printable_rows"],
            "never_returns": runaway["never_returns"],
            "look": [(row["tick"], q(row["biggest"])) for row in runaway["look"]],
            "floors": {row["tick"]: row["floor"] for row in runaway["floors"]},
            "stable_tried": [
                {"k": q(row["k"]), "period": row["period"], "printable": row["printable"]}
                for row in runaway["stable_tried"]
            ],
        },
    }


def kinds_of_place() -> Dict[str, Any]:
    """Register row R19 — the wrapped world, its control, and the bigger world that confirms it."""
    group = rows_payload()["world"]
    return {
        "dots": group["dots"], "bigger_dots": group["bigger_dots"],
        "control": group["control"], "screw": group["screw"], "bigger": group["bigger"],
    }


def no_room() -> Dict[str, Any]:
    """Register row R10 — every dot of the tetrahedron is one hop from every other."""
    group = rows_payload()["no_room"]
    return {"dots": group["dots"], "diameter": group["diameter"],
            "hops": [list(row) for row in group["hops"]]}


def triangle_motion() -> Dict[str, Any]:
    """Register row R07 — three numbers sloshing on the triangle, at `2/3` and at the book's `1/2`.

    `2/3` is the row's point: it is not a dyadic rational, so no float represents it, and the run
    comes home exactly anyway.
    """
    group = rows_payload()["triangle_motion"]

    def run(entry: Dict[str, Any]) -> Dict[str, Any]:
        return {"k": q(entry["k"]), "ticks": entry["ticks"],
                "history": [qs(row) for row in entry["history"]],
                "totals": qs(entry["totals"]),
                "period": entry["period"], "printable_rows": entry["printable_rows"]}

    return {"corners": qs(group["corners"]),
            "at_two_thirds": run(group["at_two_thirds"]),
            "at_the_book_tick": run(group["at_the_book_tick"])}


# ── what is available, and what is not yet used ──────────────────────────────────────────────────

#: Every group the vendored engine carries, and the register rows it covers. `TOKENS.md` is the
#: reader-facing form of this table; it lives here so the two cannot drift, and `check_edition.py`
#: holds `TOKENS.md` to it.
GROUPS: Dict[str, Tuple[str, str]] = {
    "complexes": ("R01 R02", "the ascending census on 1, 2, 3 and 4 dots, and the coboundaries"),
    "triangle": ("R03", "the first thing that closes: three differences and their loop sum"),
    "tetrahedron": ("R04 R05", "six differences, four face loops, and the inside sum"),
    "motion": ("R06 R07 R08 R09", "the one rule, run plain and with one line counted double"),
    "cut": ("R10 R11 R12", "the midpoint cut, and the shape it leaves between the tips"),
    "poke": ("R13", "the crossing, from a poke of 1"),
    "face_sum": ("R14", "eight faces of a closed surface, adding to zero"),
    "stella": ("R15", "the second tetrahedron, threaded"),
    "refusal": ("R16 R17 R18 R20 R21", "the three ceilings, the runaway, and what cannot be printed"),
    "net": ("—", "CANON.md's flat net: panels, segments and labels (the demos draw it)"),
    "triangle_motion": ("R07", "the one rule on the triangle, at 2/3 and at the book's 1/2"),
    "no_room": ("R10", "hops from every dot of the tetrahedron, and its diameter of one"),
    "world": ("R19", "how many kinds of place there are on a wrapped world, and its control"),
}


def available() -> Dict[str, Any]:
    """Every group, as raw data, for a token that does not exist yet.

    The point of this function is that the answer to "can a chapter show X?" is a lookup rather than
    a piece of engine work. All 23 registered computations are already vendored; adding a token is
    writing a renderer for one of them.
    """
    everything = dict(payload())
    everything.update(rows_payload())
    return everything


def publish_demo_data() -> bool:
    """Copy the vendored payload to `demos/data/napkin.json`. True if the file on disk changed.

    The demos are step three-B: their JavaScript still recomputes chapters 1–4 for itself and is
    still measured against this file value by value. What changed on 2026-09-02 is where the file
    comes from — it was written by the Python oracle, and it is now a copy of the engine's own
    bytes, so the browser is measured against the engine rather than against a second opinion.

    Written on every build for the reason the appendix is: it puts the copy under `git status`, so
    an engine bump that moves a number a demo shows becomes a dirty tree rather than a page that
    quietly disagrees with the book.
    """
    target = ROOT / "demos" / "data" / "napkin.json"
    body = PAYLOAD.read_bytes()
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.read_bytes() == body:
        return False
    target.write_bytes(body)
    return True
