#!/usr/bin/env python3
"""The canon: one labeling of the tetrahedron, and the only way the book draws its net.

[`CANON.md`](../CANON.md) is the prose standard; this file is the standard as data, and the two
cannot disagree because the prose is written against what is here and the check below re-derives it.

**Everything is derived from the napkin.** `tools/napkin.py` already holds the object the book's
early chapters count on — four dots named `A B C D`, the six ascending pairs, the four ascending
triples — and it holds them in one order, the order `simplices()` produces. So the canon does not
restate that order; it imports it. A label in a drawing and a row in a napkin table then carry the
same name by construction, and a change to one is a change to both.

**The labels are identities, not decoration.** `AB` is the name of a line, not a caption placed
where it looked best, and nothing here may permute, rotate or relabel a name to improve a picture.
That rule is taken from PaperTetra (`/Users/zacelston/code/PaperTetra`, commit `93a9f67`), whose
`CANONICAL_STANDARD.md` learned it the hard way on its own diagrams; see `LEGACY_MIGRATION.md` for
what came across and what was refused.

**Nothing here means anything.** No face stands for a force, a dimension or a domain; no colour
encodes a property. All four panels are filled identically and every line is drawn identically, and
the self-test asserts that — a diagram in this book carries geometry and names, and that is all.
`FIREWALL.md` is the long version.

**No floating point.** Coordinates are exact rationals in a representation that keeps `√3` symbolic
(a point is `(x, u)`, meaning the plane point `(x, u·√3)`), so side lengths compare exactly rather
than nearly. Only the final SVG numbers are decimals, produced by integer arithmetic from a fixed
rational for `√3`, so two runs on two machines emit the same bytes.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

import napkin

# ── the canon, as data ────────────────────────────────────────────────────────────────────────────

#: The vertex names. The napkin's, because they are already the book's.
NAMES: Tuple[str, ...] = napkin.NAMES

#: The vertices, the six lines and the four faces — in `simplices()` order and no other.
DOTS: List[Tuple[int, ...]] = napkin.simplices(napkin.VERTICES, 0)
LINES: List[Tuple[int, ...]] = napkin.simplices(napkin.VERTICES, 1)
FACES: List[Tuple[int, ...]] = napkin.simplices(napkin.VERTICES, 2)

#: A simplex's name: its vertices' letters, in ascending order. `napkin.edge_name`, reused so that
#: there is exactly one function in the repository that turns a simplex into a label.
name = napkin.edge_name

#: The side of every triangle in the net, in net units. PaperTetra's `3`, kept so its coordinate
#: table and this one are the same numbers.
SIDE = Fraction(3)

#: A point in the net: `(x, u)` stands for the plane point `(x, u·√3)`. Every position the layout
#: produces lands in this ring, which is why exactness costs nothing here.
Point = Tuple[Fraction, Fraction]

#: The central panel is the face on the three lowest vertices — `FACES[0]`, derived, not chosen.
CENTRAL = FACES[0]

#: The one anchor: the central triangle, `A` at the origin, `B` to its right, `C` above between them.
#: Everything else in the layout is a reflection of these three points, so this is the whole of the
#: layout's freedom and it is spent here, once.
ANCHOR: Dict[int, Point] = {
    CENTRAL[0]: (Fraction(0), Fraction(0)),
    CENTRAL[1]: (SIDE, Fraction(0)),
    CENTRAL[2]: (SIDE / 2, SIDE / 2),
}

#: How far a vertex label sits in from its corner, as a fraction of the corner-to-centroid distance.
VERTEX_INSET = Fraction(1, 4)

#: How far a line's label sits in from that line's midpoint, the same way.
LINE_INSET = Fraction(1, 4)


# ── exact vector arithmetic in the `(x, u·√3)` ring ───────────────────────────────────────────────


def _sub(p: Point, q: Point) -> Point:
    return (p[0] - q[0], p[1] - q[1])


def _add(p: Point, q: Point) -> Point:
    return (p[0] + q[0], p[1] + q[1])


def _scale(p: Point, t: Fraction) -> Point:
    return (p[0] * t, p[1] * t)


def _dot(p: Point, q: Point) -> Fraction:
    """`p·q` for two points of the ring: `x₁x₂ + 3u₁u₂`, because the second axis carries `√3`."""
    return p[0] * q[0] + 3 * p[1] * q[1]


def _norm2(p: Point, q: Point) -> Fraction:
    """The squared distance between two points — rational, so lengths compare exactly."""
    d = _sub(p, q)
    return _dot(d, d)


def _mid(p: Point, q: Point) -> Point:
    return _scale(_add(p, q), Fraction(1, 2))


def _centroid(points: Sequence[Point]) -> Point:
    total: Point = (Fraction(0), Fraction(0))
    for point in points:
        total = _add(total, point)
    return _scale(total, Fraction(1, len(points)))


def _reflect(point: Point, a: Point, b: Point) -> Point:
    """`point` mirrored in the line through `a` and `b`. Exact: the ring is closed under this."""
    direction = _sub(b, a)
    offset = _sub(point, a)
    along = 2 * _dot(offset, direction) / _dot(direction, direction)
    return _add(a, _sub(_scale(direction, along), offset))


# ── the layout: the flat unfolded net ─────────────────────────────────────────────────────────────


def panels() -> List[Tuple[Tuple[int, ...], Tuple[Point, ...]]]:
    """The four triangles of the net, in `FACES` order, each as `(face, its three positions)`.

    The central panel is the anchor. Each other panel shares two vertices with it and folds out
    across that shared line, so its third corner is *the reflection of the central panel's remaining
    corner* in that line. Stating the layout as a reflection rather than as three more coordinate
    pairs is what makes the four triangles congruent by construction instead of by proofreading.
    """
    out: List[Tuple[Tuple[int, ...], Tuple[Point, ...]]] = []
    for face in FACES:
        if face == CENTRAL:
            out.append((face, tuple(ANCHOR[vertex] for vertex in face)))
            continue
        shared = tuple(vertex for vertex in face if vertex in ANCHOR)
        apex_vertices = tuple(vertex for vertex in face if vertex not in ANCHOR)
        assert len(shared) == 2 and len(apex_vertices) == 1, (
            f"face {name(face)} shares {len(shared)} vertices with the central panel {name(CENTRAL)}; "
            f"the net folds only if it shares exactly two"
        )
        opposite = next(vertex for vertex in CENTRAL if vertex not in shared)
        apex = _reflect(ANCHOR[opposite], ANCHOR[shared[0]], ANCHOR[shared[1]])
        out.append((
            face,
            tuple(ANCHOR[vertex] if vertex in ANCHOR else apex for vertex in face),
        ))
    return out


PANELS = panels()


def segments() -> List[Tuple[Tuple[int, ...], Tuple[Point, Point], Tuple[int, ...]]]:
    """The nine lines the net actually draws, as `(the line, its two ends, the panel it bounds)`.

    Nine, not six and not twelve: the three lines of the central panel are drawn once, where two
    panels meet, and the other three are drawn twice, once on each panel that folded out. A line
    drawn twice carries its name twice — the same name, because it is the same line, and seeing `CD`
    on two edges of the paper is how a reader sees where the fold is.
    """
    central_lines = set(napkin.simplices(CENTRAL, 1))
    out: List[Tuple[Tuple[int, ...], Tuple[Point, Point], Tuple[int, ...]]] = []
    for face, positions in PANELS:
        place = dict(zip(face, positions))
        for line in napkin.simplices(face, 1):
            if face != CENTRAL and line in central_lines:
                continue  # already drawn, as the central panel's own side
            out.append((line, (place[line[0]], place[line[1]]), face))
    return out


SEGMENTS = segments()


def vertex_labels() -> List[Tuple[Tuple[int, ...], Point, Tuple[int, ...]]]:
    """Where each dot's name goes: `(the dot, the label's position, the panel it sits in)`.

    A dot's name sits **inside** a triangle, in from its corner, never outside the paper. Which
    triangle is fixed and not a matter of taste: the central one where the corner belongs to it, and
    otherwise the single panel that owns that corner. So `A`, `B`, `C` are read inside the central
    triangle and `D` inside each of the three that fold out — three labels for one dot, because the
    net puts that one dot in three places.
    """
    owners: Dict[Point, List[Tuple[int, ...]]] = {}
    vertex_at: Dict[Point, int] = {}
    for face, positions in PANELS:
        for vertex, position in zip(face, positions):
            owners.setdefault(position, []).append(face)
            if position in vertex_at:
                assert vertex_at[position] == vertex, (
                    f"two different dots landed on the same net position {position} — the layout "
                    f"has folded wrongly"
                )
            vertex_at[position] = vertex

    out: List[Tuple[Tuple[int, ...], Point, Tuple[int, ...]]] = []
    for face, positions in PANELS:
        for position in positions:
            candidates = owners[position]
            chosen = CENTRAL if CENTRAL in candidates else candidates[0]
            if chosen != face:
                continue  # this panel is not the one that labels this corner
            centroid = _centroid(positions)
            out.append((
                (vertex_at[position],),
                _add(position, _scale(_sub(centroid, position), VERTEX_INSET)),
                chosen,
            ))
    return out


def line_labels() -> List[Tuple[Tuple[int, ...], Point, Tuple[int, ...]]]:
    """Where each drawn line's name goes: in from the line's midpoint, into the panel it bounds."""
    out: List[Tuple[Tuple[int, ...], Point, Tuple[int, ...]]] = []
    for line, (start, end), face in SEGMENTS:
        positions = next(entry[1] for entry in PANELS if entry[0] == face)
        midpoint = _mid(start, end)
        centroid = _centroid(positions)
        out.append((
            line,
            _add(midpoint, _scale(_sub(centroid, midpoint), LINE_INSET)),
            face,
        ))
    return out


def face_labels() -> List[Tuple[Tuple[int, ...], Point, Tuple[int, ...]]]:
    """Where each face's name goes: at that triangle's centroid, upright, like every other label."""
    return [(face, _centroid(positions), face) for face, positions in PANELS]


# ── the drawing ───────────────────────────────────────────────────────────────────────────────────

#: A fixed rational for `√3`, to twenty places. Not `math.sqrt`: the emitted bytes must be the same
#: on every machine, and a decimal that is written down cannot be rounded differently elsewhere.
SQRT3 = Fraction(17_320_508_075_688_772_935, 10 ** 19)

SCALE = Fraction(100)          # SVG units per net unit
PAD = Fraction(45, 100)        # net units of margin, so no label touches the frame

INK = "#20314a"                # ART_DIRECTION's ink, for every line and every label
PAPER = "#f4ead8"              # ART_DIRECTION's paper, for every panel — the same fill four times
FONT = "ui-sans-serif, system-ui, 'Helvetica Neue', Arial, sans-serif"


def _decimal(value: Fraction) -> str:
    """`value` as a decimal string with at most two places, by integer arithmetic only."""
    hundredths = round(value * 100)
    whole, part = divmod(abs(hundredths), 100)
    sign = "-" if hundredths < 0 else ""
    return f"{sign}{whole}" if part == 0 else f"{sign}{whole}.{part:02d}"


def _extent() -> Tuple[Fraction, Fraction, Fraction, Fraction]:
    """`(x_min, y_max, width, height)` of the net in net units, including the margin."""
    xs = [position[0] for _, positions in PANELS for position in positions]
    us = [position[1] for _, positions in PANELS for position in positions]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(us) * SQRT3, max(us) * SQRT3
    return x_min, y_max, (x_max - x_min) + 2 * PAD, (y_max - y_min) + 2 * PAD


EXTENT = _extent()


def _project(position: Point) -> Tuple[str, str]:
    """A net point as SVG coordinates. The only place the drawing's `y`-axis is flipped."""
    x_min, y_max, _, _ = EXTENT
    x = (position[0] - x_min + PAD) * SCALE
    y = (y_max + PAD - position[1] * SQRT3) * SCALE
    return _decimal(x), _decimal(y)


def _text(label: str, position: Point, size: int) -> str:
    x, y = _project(position)
    return (
        f'    <text x="{x}" y="{y}" font-size="{size}" text-anchor="middle" '
        f'dominant-baseline="central">{label}</text>'
    )


def net_svg() -> str:
    """The canonical net, drawn. This is the only place in the book a tetrahedron net is drawn.

    Uniform on purpose. The four panels take the same fill and the nine lines the same stroke, so a
    reader cannot read a meaning out of a colour, because there is no colour to read: what the
    picture says is which dots, which lines, which faces, and which of them touch.
    """
    _, _, width, height = EXTENT

    body: List[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {_decimal(width * SCALE)} {_decimal(height * SCALE)}" role="img">',
        "  <title>The tetrahedron, unfolded flat</title>",
        "  <desc>"
        f"The four faces of one tetrahedron laid out flat: the triangle {name(CENTRAL)} in the "
        "middle, with the three others folded out from its sides. Every dot, line and face carries "
        f"its name. The dot {NAMES[3]} appears three times, once on each folded-out triangle, "
        "because the flat paper puts one corner of the solid in three places. Nothing in the "
        "drawing means anything beyond the shape: all four triangles are drawn identically."
        "</desc>",
    ]

    body.append('  <g stroke="none">')
    for face, positions in PANELS:
        points = " ".join(",".join(_project(position)) for position in positions)
        body.append(f'    <polygon points="{points}" fill="{PAPER}"/>')
    body.append("  </g>")

    body.append(
        f'  <g stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">'
    )
    for _, (start, end), _ in SEGMENTS:
        x1, y1 = _project(start)
        x2, y2 = _project(end)
        body.append(f'    <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"/>')
    body.append("  </g>")

    body.append(f'  <g font-family="{FONT}" fill="{INK}">')
    body.append('    <g font-weight="700">')
    for dot, position, _ in vertex_labels():
        body.append("  " + _text(name(dot), position, 34))
    body.append("    </g>")
    for line, position, _ in line_labels():
        body.append(_text(name(line), position, 24))
    for face, position, _ in face_labels():
        body.append(_text(name(face), position, 28))
    body.append("  </g>")

    body.append("</svg>")
    return "\n".join(body) + "\n"


# ── the check ─────────────────────────────────────────────────────────────────────────────────────

#: The coordinates `CANON.md` prints, in net units, keyed by the name of the position. Typed here on
#: purpose: the layout above *derives* them, and a derivation nobody compares against a written-down
#: answer is a derivation that can quietly change. The names are the reader's — `D across AB` is
#: where the dot `D` sits on the triangle folded out from the line `AB`.
PUBLISHED: Dict[str, Point] = {
    "A": (Fraction(0), Fraction(0)),
    "B": (Fraction(3), Fraction(0)),
    "C": (Fraction(3, 2), Fraction(3, 2)),
    "D across AB": (Fraction(3, 2), Fraction(-3, 2)),
    "D across AC": (Fraction(-3, 2), Fraction(3, 2)),
    "D across BC": (Fraction(9, 2), Fraction(3, 2)),
}

_TEXT = re.compile(r"<text[^>]*>([^<]*)</text>")
_POLYGON_FILL = re.compile(r'<polygon[^>]*fill="([^"]*)"')


def published_positions() -> Dict[str, Point]:
    """The derived layout, keyed the way `PUBLISHED` and `CANON.md` key it."""
    out: Dict[str, Point] = {}
    for vertex in CENTRAL:
        out[NAMES[vertex]] = ANCHOR[vertex]
    for face, positions in PANELS:
        if face == CENTRAL:
            continue
        shared = tuple(vertex for vertex in face if vertex in ANCHOR)
        apex_vertex = next(vertex for vertex in face if vertex not in ANCHOR)
        apex = next(
            position for vertex, position in zip(face, positions) if vertex == apex_vertex
        )
        out[f"{NAMES[apex_vertex]} across {name(shared)}"] = apex
    return out


def self_test() -> str:
    """Assert the canon against the napkin and against itself; return what was checked.

    The headline is written after the assertions, from what they counted, and there is no path
    through this function that produces a headline without them — a failure raises, so it cannot
    narrate a clean line over its own problem. That is `check_edition.py`'s status discipline in its
    smallest form: the check does not hold the pen on its own verdict.

    What is asserted, in order: the canon's dots, lines and faces are the napkin's, in the napkin's
    order; the layout's four triangles are congruent, exactly; the derived coordinates are the ones
    `CANON.md` publishes; the drawing carries every name and only names, as many times as the net
    puts that piece on the paper; nothing in the drawing distinguishes one panel from another; and
    two renders are the same bytes.
    """
    # 1. The object is the napkin's, name for name and in its order.
    assert DOTS == napkin.simplices(napkin.VERTICES, 0), "the canon's dots are not the napkin's"
    assert LINES == napkin.simplices(napkin.VERTICES, 1), "the canon's lines are not the napkin's"
    assert FACES == napkin.simplices(napkin.VERTICES, 2), "the canon's faces are not the napkin's"
    assert (len(DOTS), len(LINES), len(FACES)) == (4, 6, 4), (
        f"the census came out {(len(DOTS), len(LINES), len(FACES))}, not 4 dots, 6 lines, 4 faces"
    )
    assert len(NAMES) == len(DOTS), f"{len(NAMES)} names for {len(DOTS)} dots"
    for cells in (DOTS, LINES, FACES):
        for cell in cells:
            assert list(cell) == sorted(cell), f"{cell} is not ascending, so its name is not canonical"
        assert cells == sorted(cells), f"{cells} is not in ascending order"

    # 2. The four triangles are congruent — every one of the twelve sides is the same length.
    sides = [
        _norm2(positions[i], positions[j])
        for _, positions in PANELS
        for i, j in ((0, 1), (0, 2), (1, 2))
    ]
    assert len(sides) == 12, f"{len(sides)} sides for four triangles"
    assert all(side == SIDE * SIDE for side in sides), (
        f"the net's triangles are not equilateral and equal: squared sides {sorted(set(sides))}, "
        f"expected {SIDE * SIDE} throughout"
    )

    # 3. The derived layout is the one the standard publishes.
    derived = published_positions()
    assert derived == PUBLISHED, (
        f"the layout no longer agrees with the coordinates CANON.md prints: derived {derived}, "
        f"published {PUBLISHED}"
    )

    # 4. Every label is a name of a real piece, every piece is labelled, and each is labelled once
    #    per copy the net makes of it.
    expected: Counter = Counter()
    for dot in DOTS:
        expected[name(dot)] = 1 if dot[0] in CENTRAL else 3
    for line in LINES:
        expected[name(line)] = 1 if set(line) <= set(CENTRAL) else 2
    for face in FACES:
        expected[name(face)] = 1

    svg = net_svg()
    drawn = Counter(_TEXT.findall(svg))
    assert drawn == expected, (
        f"the drawing's labels are not the napkin's simplices: drawn {dict(sorted(drawn.items()))}, "
        f"expected {dict(sorted(expected.items()))}"
    )
    assert sum(drawn.values()) == len(vertex_labels()) + len(line_labels()) + len(face_labels()), (
        "the drawing emitted a different number of labels than the layout placed"
    )

    # 5. No panel is distinguished from another. Colour carries nothing here, and the way to keep
    #    that true is to check that there is only one colour to carry it.
    fills = set(_POLYGON_FILL.findall(svg))
    assert len(fills) == 1, (
        f"the four panels are filled {len(fills)} different ways ({sorted(fills)}) — in this book a "
        f"panel's colour must not distinguish it from another panel"
    )
    assert len(_POLYGON_FILL.findall(svg)) == len(PANELS), (
        f"{len(_POLYGON_FILL.findall(svg))} panels drawn, expected {len(PANELS)}"
    )

    # 6. Two renders, the same bytes. "Derived from the napkin" is a promise about every build.
    assert net_svg() == svg, "the net is not deterministic — two renders in one process differ"

    return (
        f"{sum(drawn.values())} labels are the napkin's "
        f"{len(DOTS)} dots, {len(LINES)} lines and {len(FACES)} faces and nothing else; "
        f"{len(sides)} net sides all exactly {SIDE}; "
        f"{len(derived)} coordinates match CANON.md; "
        f"{len(PANELS)} panels drawn one way; two renders identical"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--svg", action="store_true", help="print the canonical net to stdout")
    parser.add_argument("--out", type=Path, help="write the canonical net to this file")
    args = parser.parse_args(argv)

    headline = self_test()
    print(f"canon self-test: {headline}")

    if args.out:
        args.out.write_text(net_svg(), encoding="utf-8")
        print(f"wrote {args.out}")
    if args.svg:
        sys.stdout.write(net_svg())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
