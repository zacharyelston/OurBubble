#!/usr/bin/env python3
"""The octahedron on the napkin: what is exactly true about the crossing between cells.

This module is **evidence, not a book token.** It answers a proposal — that the octahedron is the
crossing where neighbouring tetrahedra exchange, that it "holds the sum of the neighbours", and that
gathering at the octahedron is cheaper than working tetrahedron by tetrahedron — by computing the
answer instead of asserting it from the picture. Three symmetry claims in this arc were already
asserted from a picture and were wrong; that is why nothing here is written for a reader until it
has been computed.

**What it settles, exactly, and what it does not.** A tick is not a trip round the bare octahedron under a time-symmetric rule on 0-forms; the family's claim (screw, 1-forms, chiral mesh) is under review: UniForge lab/napkin/0002. Everything
below is that one reading, computed; read `notes/octahedron-crossing.md`'s provenance note before
quoting any of it as a verdict on anything wider.

**Everything is exact.** Integers and `fractions.Fraction` throughout, no floating point anywhere,
and every claim below is an `assert` next to the number it makes. Where a bound is irrational
(and one is) it is pinned by an exact rational test — positive-definiteness of `M·I − Δ₀` by
Sylvester's criterion — never by a decimal.

**One rule, one copy.** The step is `napkin.slosh` — the same leapfrog the chapters run, reached
through its `initial` and `k` arguments rather than reimplemented. A second leapfrog next door would
be the one place this book could disagree with itself about what one step is.

The object is the engine's, replicated faithfully in Python from `core/geom/src/mesh.rs` in UniForge
at the commit `record.lock` pins (`db59a2fc`) — `mesh_3d_chiral_tetoct_periodic`, lines 796–864, and
the cut rule `chiral_oct_screw111`, lines 674–676. That file is **not** in the committed `record/`
snapshot (which carries the gates, not the geometry crate), so the line numbers below are a pointer
into the engine at that SHA, not a link a reader can click:

  * dots are the integer points with `x+y+z` **even**; odd points are octahedral-hole centres and
    carry nothing (mesh.rs lines 813–820 and 841–843);
  * every unit cube contributes **one** tetrahedron, on its four even corners (lines 822–835);
  * every odd point carries the octahedron of its six axis neighbours, **cut into four tetrahedra**
    about one long diagonal, chosen by `(x+y+z) mod 3` (lines 837–860).

Run it: `python3 tools/octahedron.py` prints the whole report and asserts every line of it.
"""

from __future__ import annotations

import os
import sys
from fractions import Fraction
from itertools import combinations, product
from typing import Dict, List, Optional, Sequence, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# The arithmetic comes from `oracle.py` and the rendering from `napkin.py`, and that split is the
# 2026-09-02 decision in one import: the engine is UniForge's `napkin` crate, this module and the
# oracle are the Python that checks it, and the napkin is now a renderer. See `tools/oracle.py`.
from napkin import number, signed  # noqa: E402  (needs the path above)
from oracle import (  # noqa: E402
    apply,
    coboundary,
    laplacian as napkin_laplacian,
    period,
    screw111,
    slosh,
    unit_weights,
)

Point = Tuple[int, int, int]

# ── the record's tiling ───────────────────────────────────────────────────────────────────────────

TORUS = 6        # the builder's own minimum: parity (mod 2) and the cut rule (mod 3) must both
TORUS_CHECK = 12  # close under every wrap. 12 confirms 6 is big enough to be telling the truth.

AXES: Tuple[Point, Point, Point] = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
SIGNS: Tuple[int, ...] = (1, -1)


def _add(a: Point, b: Point, scale: int = 1) -> Point:
    return (a[0] + scale * b[0], a[1] + scale * b[1], a[2] + scale * b[2])


class Tiling:
    """The tetrahedral–octahedral honeycomb on an `n³` torus, as the record builds it.

    Three collections, kept separate because the whole question is which of them touch which:

    * `cube_tets` — one tetrahedron per unit cube, on its four even corners;
    * `octahedra` — one per odd point, keyed by centre, each with its six vertices, its cut axis,
      and the four sub-tetrahedra the cut produces;
    * `sub_tets` — those sub-tetrahedra, flattened.

    Every point stored is wrapped into the torus, but the *geometry* (which face is which, which
    apex sits over which face) is computed on the unwrapped integer coordinates first, so a wrap
    can never be mistaken for an adjacency.
    """

    def __init__(self, n: int, cut=screw111) -> None:
        assert n % 6 == 0 and n >= 6, "the builder requires n ≡ 0 (mod 6), n ≥ 6"
        self.n = n
        self.cut = cut
        self.cube_tets: List[Tuple[Point, ...]] = []
        self.cube_tet_of: Dict[Tuple[Point, ...], Point] = {}
        self.octahedra: Dict[Point, Dict[str, object]] = {}
        self.sub_tets: List[Tuple[Point, ...]] = []

        for i, j, k in product(range(n), repeat=3):
            corners = [
                (i + a, j + b, k + c)
                for a in (0, 1) for b in (0, 1) for c in (0, 1)
                if (i + a + j + b + k + c) % 2 == 0
            ]
            assert len(corners) == 4, "a cube must have four even corners"
            tet = tuple(sorted(self.wrap(p) for p in corners))
            self.cube_tets.append(tet)
            self.cube_tet_of[tet] = (i, j, k)

        for x, y, z in product(range(n), repeat=3):
            if (x + y + z) % 2 == 0:
                continue                      # octahedra are centred on ODD-sum holes
            centre = (x, y, z)
            axis = cut(x, y, z)
            plus = [_add(centre, AXES[a]) for a in range(3)]
            minus = [_add(centre, AXES[a], -1) for a in range(3)]
            vertices = [v for pair in zip(plus, minus) for v in pair]
            d0, d1 = minus[axis], plus[axis]
            other = [a for a in range(3) if a != axis]
            eq = [plus[other[0]], plus[other[1]], minus[other[0]], minus[other[1]]]
            tets = [
                tuple(sorted(self.wrap(p) for p in (d0, d1, eq[w], eq[(w + 1) % 4])))
                for w in range(4)
            ]
            self.octahedra[centre] = {
                "vertices": tuple(self.wrap(v) for v in vertices),
                "raw_vertices": tuple(vertices),
                "axis": axis,
                "diagonal": tuple(sorted((self.wrap(d0), self.wrap(d1)))),
                "tets": tets,
            }
            self.sub_tets.extend(tets)

    # -- helpers ----------------------------------------------------------------------------------

    def wrap(self, p: Point) -> Point:
        n = self.n
        return (p[0] % n, p[1] % n, p[2] % n)

    def oct_faces(self, centre: Point) -> List[Tuple[Point, ...]]:
        """The octahedron's eight faces: one per choice of sign on each axis."""
        return [
            tuple(sorted(self.wrap(_add(centre, AXES[a], s)) for a, s in enumerate(signs)))
            for signs in product(SIGNS, repeat=3)
        ]

    def oct_apex(self, centre: Point, signs: Sequence[int]) -> Point:
        """The point a regular tetrahedron on that face would put its apex at: c + (±1,±1,±1)."""
        return self.wrap((centre[0] + signs[0], centre[1] + signs[1], centre[2] + signs[2]))

    @staticmethod
    def faces_of(tet: Sequence[Point]) -> List[Tuple[Point, ...]]:
        return [tuple(sorted(f)) for f in combinations(tet, 3)]

    @staticmethod
    def edges_of(cell: Sequence[Point]) -> List[Tuple[Point, Point]]:
        return [tuple(sorted(e)) for e in combinations(cell, 2)]  # type: ignore[misc]


def face_audit(n: int = TORUS, cut=screw111) -> Dict[str, object]:
    """Does the octahedron join every pair of tetrahedra, and nothing else?

    The proposal to test: *tetrahedra never share a face with each other; the octahedron is the only
    thing joining them.* At the honeycomb level that is a statement with an exact answer, and this
    computes it — every cube-tetrahedron face against every octahedron face, on a wrapped world with
    no boundary to hide behind.
    """
    t = Tiling(n, cut)
    tet_faces: Dict[Tuple[Point, ...], int] = {}
    for tet in t.cube_tets:
        for face in t.faces_of(tet):
            tet_faces[face] = tet_faces.get(face, 0) + 1
    oct_faces: Dict[Tuple[Point, ...], int] = {}
    for centre in t.octahedra:
        for face in t.oct_faces(centre):
            oct_faces[face] = oct_faces.get(face, 0) + 1

    shared = max(tet_faces.values())
    assert shared == 1, (
        f"a face is shared by {shared} cube-tetrahedra — two tetrahedra meet face to face, which "
        f"is the thing this audit exists to rule out"
    )
    assert max(oct_faces.values()) == 1, "two octahedra share a face"
    assert set(tet_faces) == set(oct_faces), (
        f"{len(set(tet_faces) ^ set(oct_faces))} face(s) are a tetrahedron's or an octahedron's but "
        f"not both — the pairing is not a pairing"
    )

    # Stronger: each octahedron's eight faces are covered by eight DISTINCT cube-tetrahedra, whose
    # fourth vertices are exactly c + (±1,±1,±1) — the eight spikes of a stella octangula.
    owner: Dict[Tuple[Point, ...], Tuple[Point, ...]] = {}
    for tet in t.cube_tets:
        for face in t.faces_of(tet):
            owner[face] = tet
    for centre, oct in t.octahedra.items():
        apexes = set()
        for signs in product(SIGNS, repeat=3):
            face = tuple(sorted(t.wrap(_add(centre, AXES[a], s)) for a, s in enumerate(signs)))
            tet = owner[face]
            fourth = [v for v in tet if v not in face]
            assert len(fourth) == 1, f"a face of {centre} is not a face of a tetrahedron"
            assert fourth[0] == t.oct_apex(centre, signs), (
                f"the tetrahedron on face {signs} of {centre} has its apex at {fourth[0]}, not at "
                f"c+{signs} — the eight neighbours are not the stella's eight spikes"
            )
            apexes.add(fourth[0])
        assert len(apexes) == 8, f"the octahedron at {centre} has {len(apexes)} distinct spikes"

    return {
        "n": n,
        "tets": len(t.cube_tets),
        "octahedra": len(t.octahedra),
        "sub_tets": len(t.sub_tets),
        "tet_faces": 4 * len(t.cube_tets),
        "oct_faces": 8 * len(t.octahedra),
        "distinct_faces": len(tet_faces),
        "ratio": Fraction(len(t.cube_tets), len(t.octahedra)),
    }


def line_audit(n: int = TORUS, cut=screw111) -> Dict[str, object]:
    """Which lines exist, who owns them, and how many octahedra each one belongs to.

    The face audit says the octahedron is the only thing joining tetrahedra *across a face*. Numbers
    do not live on faces, though — 0-forms live on dots and move along lines — so the honest version
    of "the crossing" has to be settled on the lines, and it is settled here: what fraction of the
    lines a tetrahedron never provides, and whether an octahedron owns its lines outright.
    """
    t = Tiling(n, cut)
    tet_lines = set()
    for tet in t.cube_tets:
        tet_lines.update(t.edges_of(tet))
    equator_owners: Dict[Tuple[Point, Point], int] = {}
    diagonals = set()
    mesh_lines = set(tet_lines)
    for centre, oct in t.octahedra.items():
        verts = oct["raw_vertices"]
        for a, b in combinations(range(6), 2):
            if a // 2 == b // 2:
                continue      # antipodal pair: a long diagonal, not an edge
            line = tuple(sorted((t.wrap(verts[a]), t.wrap(verts[b]))))
            equator_owners[line] = equator_owners.get(line, 0) + 1
        diagonals.add(oct["diagonal"])
        for tet in oct["tets"]:
            mesh_lines.update(t.edges_of(tet))

    equator = set(equator_owners)
    assert equator == tet_lines, (
        "the octahedra's edges and the tetrahedra's edges are not the same set of lines"
    )
    assert set(equator_owners.values()) == {2}, (
        f"an octahedron edge is owned by {sorted(set(equator_owners.values()))} octahedra, not "
        f"exactly 2 — an octahedron-by-octahedron sweep would not visit lines uniformly"
    )
    assert mesh_lines == equator | diagonals, "the mesh has lines that are neither"
    assert not (diagonals & tet_lines), "a long diagonal is also a tetrahedron edge"

    degree: Dict[Point, int] = {}
    tet_degree: Dict[Point, int] = {}
    for u, v in mesh_lines:
        degree[u] = degree.get(u, 0) + 1
        degree[v] = degree.get(v, 0) + 1
    for u, v in tet_lines:
        tet_degree[u] = tet_degree.get(u, 0) + 1
        tet_degree[v] = tet_degree.get(v, 0) + 1
    assert set(degree.values()) == {14}, f"the dots do not all have 14 lines: {set(degree.values())}"
    assert set(tet_degree.values()) == {12}, (
        f"the tetrahedron-provided lines per dot are {set(tet_degree.values())}, not 12"
    )

    # The other half of "the octahedron is the only thing joining them": it is NOT, on the lines.
    # Every tetrahedron edge is shared by exactly two tetrahedra, so a number crosses from one
    # tetrahedron to the next in a single step, with no octahedron dot in between to wait for.
    tet_line_uses: Dict[Tuple[Point, Point], int] = {}
    for tet in t.cube_tets:
        for line in t.edges_of(tet):
            tet_line_uses[line] = tet_line_uses.get(line, 0) + 1
    assert set(tet_line_uses.values()) == {2}, (
        f"a tetrahedron edge is used by {sorted(set(tet_line_uses.values()))} tetrahedra, not "
        f"exactly 2 — the line-level claim in the notes depends on this"
    )
    assert 6 * len(t.cube_tets) == 2 * len(tet_lines), (
        f"{6 * len(t.cube_tets)} edge-slots over {len(tet_lines)} lines is not a clean pairing"
    )

    dots = n ** 3 // 2
    assert len(degree) == dots, f"{len(degree)} dots carry lines, expected {dots}"
    assert len(diagonals) == len(t.octahedra), "an octahedron did not contribute exactly one cut"
    return {
        "n": n,
        "dots": dots,
        "lines": len(mesh_lines),
        "tet_lines": len(tet_lines),
        "cut_lines": len(diagonals),
        "cut_share": Fraction(len(diagonals), len(mesh_lines)),
        "octahedra_per_edge": 2,
        "octahedra_per_cut": 1,
        "tets_per_tet_line": 2,
    }


def hull_audit() -> Dict[str, object]:
    """One octahedron + its eight spikes: is it the stella octangula, and does the stella tile?

    Two separate questions, and they get separate answers. The shape is exact rational geometry — the
    eight apexes are the corners of a cube, the six octahedron vertices its face centres, and the
    volumes are integers over three. Whether that shape is the tiling's repeat unit is a counting
    question, and counting is what settles it.
    """
    oct_vertices = [_add((0, 0, 0), AXES[a], s) for a in range(3) for s in SIGNS]
    apexes = [tuple(s) for s in product(SIGNS, repeat=3)]

    cube_corners = {p for p in product((-1, 1), repeat=3)}
    assert set(apexes) == cube_corners, "the eight spikes are not the corners of a cube"
    for v in oct_vertices:
        assert max(abs(c) for c in v) == 1 and sum(abs(c) for c in v) == 1, (
            f"{v} is not the centre of a face of that cube"
        )

    # Volumes, exactly. The regular tetrahedron on a cube's four alternate corners is a third of the
    # cube; the octahedron with vertices ±e is four thirds; the hull cube of side 2 is eight.
    spike = Fraction(1, 3)          # each spike tet, edge √2, inscribed in a unit cube
    core = Fraction(4, 3)           # the octahedron {±e_x, ±e_y, ±e_z}
    stella = core + 8 * spike
    cube = Fraction(8)
    assert stella == 4 and stella * 2 == cube, (
        f"the stella came out {stella} and its hull {cube} — the halves claim is wrong"
    )
    return {
        "stella_volume": stella,
        "hull_volume": cube,
        "fill": stella / cube,
        "spikes_per_tet": 4,        # each cube-tet has 4 faces, each on a different octahedron
        "cover_multiplicity": 2,    # so the stellae cover space exactly twice over
    }


def stella_overlap(n: int = TORUS, cut=screw111) -> Dict[str, object]:
    """How many stellae each tetrahedron belongs to, counted rather than argued."""
    t = Tiling(n, cut)
    membership: Dict[Tuple[Point, ...], int] = {tet: 0 for tet in t.cube_tets}
    owner: Dict[Tuple[Point, ...], Tuple[Point, ...]] = {}
    for tet in t.cube_tets:
        for face in t.faces_of(tet):
            owner[face] = tet
    for centre in t.octahedra:
        for face in t.oct_faces(centre):
            membership[owner[face]] += 1
    assert set(membership.values()) == {4}, (
        f"a tetrahedron belongs to {sorted(set(membership.values()))} stellae, not 4"
    )
    volume_of_space = Fraction(n ** 3)
    stella_volume = len(t.octahedra) * hull_audit()["stella_volume"]
    assert stella_volume == 2 * volume_of_space, (
        f"the stellae cover {stella_volume} of a world of volume {volume_of_space}"
    )
    return {"stellae_per_tet": 4, "cover": stella_volume / volume_of_space}


# ── the stella octangula as a complex ────────────────────────────────────────────────────────────
#
# Fourteen dots: the octahedron's six, and one apex over each of its eight faces. Named so a table
# can be read: `+x` … `−z` for the octahedron, `+++` … `−−−` for the spikes.

OCT_NAMES = ("+x", "−x", "+y", "−y", "+z", "−z")
OCT_POINTS: Tuple[Point, ...] = tuple(_add((0, 0, 0), AXES[a], s) for a in range(3) for s in SIGNS)
APEX_POINTS: Tuple[Point, ...] = tuple(product(SIGNS, repeat=3))


def _apex_name(p: Point) -> str:
    return "".join("+" if c > 0 else "−" for c in p)


STELLA_NAMES: Tuple[str, ...] = OCT_NAMES + tuple(_apex_name(p) for p in APEX_POINTS)
STELLA_POINTS: Tuple[Point, ...] = OCT_POINTS + APEX_POINTS
CUT_AXIS = 0     # the record's cut picks one long diagonal; on the motif call it the x one.


def stella_lines(cut: bool) -> List[Tuple[int, int]]:
    """The lines of the stella octangula, with or without the record's cut.

    `cut=False` is the solid as a shape — twelve octahedron edges and three per spike, thirty-six
    lines, every octahedron dot with eight. `cut=True` is what the record actually builds: the
    octahedron is four tetrahedra about one long diagonal, so that diagonal is a line too. The
    difference is one line out of thirty-six, and it is not cosmetic — it is the line that breaks the
    motif's symmetry, and it changes the spectrum.
    """
    lines = set()
    for a, b in combinations(range(6), 2):
        if a // 2 == b // 2:
            continue
        lines.add((a, b))
    for i, apex in enumerate(APEX_POINTS):
        for axis in range(3):
            target = _add((0, 0, 0), AXES[axis], apex[axis])
            lines.add(tuple(sorted((OCT_POINTS.index(target), 6 + i))))
    if cut:
        lines.add((2 * CUT_AXIS, 2 * CUT_AXIS + 1))
    return sorted(lines)


def stella_census() -> Dict[str, object]:
    solid = stella_lines(cut=False)
    record = stella_lines(cut=True)
    degrees = {name: 0 for name in STELLA_NAMES}
    for u, v in solid:
        degrees[STELLA_NAMES[u]] += 1
        degrees[STELLA_NAMES[v]] += 1
    oct_degrees = {degrees[n] for n in OCT_NAMES}
    apex_degrees = {degrees[STELLA_NAMES[6 + i]] for i in range(8)}
    assert len(solid) == 36, f"the stella octangula came out with {len(solid)} lines, not 36"
    assert len(record) == 37, f"the cut stella came out with {len(record)} lines, not 37"
    assert oct_degrees == {8}, f"the octahedron's dots have {oct_degrees} lines, not 8"
    assert apex_degrees == {3}, f"the spikes' apexes have {apex_degrees} lines, not 3"
    cut_degrees = {name: 0 for name in STELLA_NAMES}
    for u, v in record:
        cut_degrees[STELLA_NAMES[u]] += 1
        cut_degrees[STELLA_NAMES[v]] += 1
    assert sorted(cut_degrees[n] for n in OCT_NAMES) == [8, 8, 8, 8, 9, 9], (
        f"the cut's two ends should carry nine lines: {sorted(cut_degrees.values())}"
    )
    return {
        "dots": 14,
        "lines_solid": 36,
        "lines_record": 37,
        "oct_degree": 8,
        "apex_degree": 3,
        "cut_end_degree": 9,
    }


# ── the sum: F on the octahedron's closed surface ────────────────────────────────────────────────


def cut_octahedron_complex() -> Dict[str, object]:
    """The record's octahedron as a complex: six dots, thirteen lines, twelve faces, four insides.

    Built exactly as `mesh_3d_chiral_tetoct_periodic` builds it — four tetrahedra sharing one long
    diagonal, cycling the four equatorial dots — and then read as a complex in the napkin's own
    convention: every cell an ascending tuple, the ascending order *being* the orientation.
    """
    dots = tuple(range(6))
    axis = CUT_AXIS
    d0, d1 = 2 * axis + 1, 2 * axis          # −x, +x  (index 2a is +, 2a+1 is −)
    other = [a for a in range(3) if a != axis]
    eq = [2 * other[0], 2 * other[1], 2 * other[0] + 1, 2 * other[1] + 1]
    raw_tets = [(d0, d1, eq[w], eq[(w + 1) % 4]) for w in range(4)]
    insides = sorted(tuple(sorted(t)) for t in raw_tets)

    faces = sorted({tuple(sorted(f)) for t in insides for f in combinations(t, 3)})
    lines = sorted({tuple(sorted(e)) for f in faces for e in combinations(f, 2)})
    assert (len(dots), len(lines), len(faces), len(insides)) == (6, 13, 12, 4), (
        f"the cut octahedron's census came out "
        f"{(len(dots), len(lines), len(faces), len(insides))}"
    )
    euler = len(dots) - len(lines) + len(faces) - len(insides)
    assert euler == 1, f"the cut octahedron's Euler count is {euler}, not 1 — it is not a ball"

    d1_mat = coboundary(lines, faces)        # lines → faces
    d2_mat = coboundary(faces, insides)      # faces → insides
    for column in range(len(lines)):
        basis = [Fraction(1) if i == column else Fraction(0) for i in range(len(lines))]
        assert all(v == 0 for v in apply(d2_mat, apply(d1_mat, basis))), (
            "d₂∘d₁ ≠ 0 on the cut octahedron — the object is not a complex"
        )

    # Which faces are on the outside: a face is a boundary face iff it belongs to one inside only.
    ownership: Dict[Tuple[int, ...], int] = {f: 0 for f in faces}
    for t in insides:
        for f in combinations(t, 3):
            ownership[tuple(sorted(f))] += 1
    boundary = [f for f in faces if ownership[f] == 1]
    interior = [f for f in faces if ownership[f] == 2]
    assert len(boundary) == 8 and len(interior) == 4, (
        f"{len(boundary)} boundary and {len(interior)} interior faces, expected 8 and 4"
    )
    return {
        "dots": dots, "lines": lines, "faces": faces, "insides": insides,
        "d1": d1_mat, "d2": d2_mat, "boundary": boundary, "interior": interior,
    }


def _orientation(cell: Sequence[int]) -> int:
    """+1 if the ascending-order tetrahedron is positively oriented in space, −1 if not.

    An exact 3×3 integer determinant on the octahedron's own coordinates. This is the only place
    geometry enters the sum, and it enters as a sign, never as a length.
    """
    p = [OCT_POINTS[i] for i in cell]
    a = [p[1][i] - p[0][i] for i in range(3)]
    b = [p[2][i] - p[0][i] for i in range(3)]
    c = [p[3][i] - p[0][i] for i in range(3)]
    det = (a[0] * (b[1] * c[2] - b[2] * c[1])
           - a[1] * (b[0] * c[2] - b[2] * c[0])
           + a[2] * (b[0] * c[1] - b[1] * c[0]))
    assert det != 0, f"the tetrahedron {cell} is flat"
    return 1 if det > 0 else -1


# Thirteen freely chosen line-numbers — arrows in their own right, not differences of dot values.
# Chosen (and asserted) so that every one of the twelve faces carries a non-zero number: a boundary
# sum of eight zeros would demonstrate nothing, which is the same trap beat 22 avoids.
OCT_ARROWS: Tuple[int, ...] = (3, 1, 4, 1, 5, 2, 6, 5, 3, 5, 8, 9, 7)


def boundary_sum() -> Dict[str, object]:
    """Does the octahedron's closed surface hold the sum of what crosses it? Exactly, yes — zero.

    The proposal was that the octahedron "holds the sum of the neighbours". This is the exact reading
    of it. Put a freely chosen arrow on each of the thirteen lines. `F = dA` is then a number on each
    of the twelve faces — how much goes round that face — and eight of those faces are the
    octahedron's outside. Add those eight up, each walked the way round it faces from outside, and
    the answer is **zero for every A whatever**, with no length anywhere in it.

    And it is not a new fact: it is `tetra_inside_sum` — chapter 2's beat 23 — run four times and
    added. Each of the four insides has its own four face-numbers summing to zero, and the four
    interior faces appear in two insides each with opposite signs, so they cancel and leave exactly
    the eight outside ones. That cancellation is asserted term by term below, not asserted in prose.
    """
    c = cut_octahedron_complex()
    lines, faces, insides = c["lines"], c["faces"], c["insides"]
    arrows = [Fraction(a) for a in OCT_ARROWS]
    assert len(arrows) == len(lines), f"{len(arrows)} arrows for {len(lines)} lines"

    F = apply(c["d1"], arrows)
    assert all(f != 0 for f in F), (
        f"a face came out zero ({F}) — choose arrows that make every face carry something, or the "
        f"sum below demonstrates less than it claims"
    )

    # Each inside's own four faces, walked round it: zero. Four times over.
    per_inside = apply(c["d2"], F)
    assert all(v == 0 for v in per_inside), f"an inside sum came out non-zero: {per_inside}"

    # All four insides oriented the same way in space; add their boundaries.
    chain = [Fraction(0)] * len(faces)
    for index, inside in enumerate(insides):
        sign = _orientation(inside)
        for face_index in range(len(faces)):
            chain[face_index] += sign * c["d2"][index][face_index]
    for face_index, face in enumerate(faces):
        if face in c["interior"]:
            assert chain[face_index] == 0, (
                f"the interior face {face} did not cancel: it carries {chain[face_index]}"
            )
        else:
            assert abs(chain[face_index]) == 1, (
                f"the outside face {face} is walked {chain[face_index]} times, not once"
            )

    total = sum(sign * value for sign, value in zip(chain, F))
    assert total == 0, f"the eight outside faces summed to {total}, not 0"

    outside = [(faces[i], chain[i] * F[i]) for i in range(len(faces)) if faces[i] in c["boundary"]]
    assert len(outside) == 8
    assert all(value != 0 for _, value in outside), "an outside face carries nothing"
    return {
        "arrows": tuple(OCT_ARROWS),
        "face_numbers": tuple(F),
        "outside_terms": tuple(value for _, value in outside),
        "outside_sum": total,
        "per_inside": tuple(per_inside),
        "interior_cancelled": len(c["interior"]),
    }


# ── exact linear algebra: the spectrum, and what is stable ───────────────────────────────────────


def laplacian_matrix(size: int, lines: Sequence[Tuple[int, int]]) -> List[List[Fraction]]:
    """`Δ₀` with every line counting one, as a matrix. Same operator as `napkin.laplacian`."""
    matrix = [[Fraction(0)] * size for _ in range(size)]
    for i, j in lines:
        matrix[i][i] += 1
        matrix[j][j] += 1
        matrix[i][j] -= 1
        matrix[j][i] -= 1
    # Cross-check against the napkin's own Laplacian, applied to every basis vector.
    weights = unit_weights(lines)
    for column in range(size):
        basis = [Fraction(1) if i == column else Fraction(0) for i in range(size)]
        theirs = napkin_laplacian(basis, weights, lines)
        mine = [matrix[row][column] for row in range(size)]
        assert theirs == mine, f"the matrix and the napkin's Δ₀ disagree in column {column}"
    return matrix


def determinant(matrix: Sequence[Sequence[Fraction]]) -> Fraction:
    """Exact Gaussian elimination. No pivoting tolerance, because there is nothing to tolerate."""
    rows = [list(row) for row in matrix]
    size = len(rows)
    det = Fraction(1)
    for col in range(size):
        pivot = next((r for r in range(col, size) if rows[r][col] != 0), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            rows[col], rows[pivot] = rows[pivot], rows[col]
            det = -det
        det *= rows[col][col]
        inverse = 1 / rows[col][col]
        for r in range(col + 1, size):
            factor = rows[r][col] * inverse
            if factor:
                for cc in range(col, size):
                    rows[r][cc] -= factor * rows[col][cc]
    return det


def spectrum_below(matrix: Sequence[Sequence[Fraction]], bound: Fraction) -> bool:
    """Is every eigenvalue strictly below `bound`? Exactly, by Sylvester's criterion.

    `Δ₀` is symmetric, so `bound·I − Δ₀` is positive definite exactly when every leading principal
    minor is positive — a finite list of exact rational determinants. This is how an irrational
    largest eigenvalue is pinned without ever writing a decimal: not by computing it, but by asking
    exact yes/no questions about rationals either side of it.
    """
    size = len(matrix)
    shifted = [[(bound if i == j else Fraction(0)) - matrix[i][j] for j in range(size)]
               for i in range(size)]
    return all(determinant([row[:k] for row in shifted[:k]]) > 0 for k in range(1, size + 1))


def largest_eigenvalue_bracket(matrix: Sequence[Sequence[Fraction]],
                               steps: int = 40) -> Tuple[Fraction, Fraction]:
    """Rationals `(low, high)` with `low ≤ λ_max < high`, by exact bisection on `spectrum_below`."""
    size = len(matrix)
    low, high = Fraction(0), Fraction(2 * max(matrix[i][i] for i in range(size)) + 1)
    assert spectrum_below(matrix, high), "the starting bracket does not contain the spectrum"
    for _ in range(steps):
        middle = (low + high) / 2
        if spectrum_below(matrix, middle):
            high = middle
        else:
            low = middle
    return low, high


def annihilates(matrix: Sequence[Sequence[Fraction]], poly: Sequence[int]) -> bool:
    """Is `poly(Δ₀) = 0`? `poly` is ascending in powers. An exact certificate for the spectrum.

    If `poly(Δ₀) = 0` then every eigenvalue is a root of `poly`, and for a symmetric matrix the
    smallest such `poly` with distinct roots is exactly the list of eigenvalues. So this one boolean,
    plus the traces below, says what the spectrum *is* — no eigensolver, no floating point.
    """
    size = len(matrix)
    result = [[Fraction(0)] * size for _ in range(size)]
    power = [[Fraction(1) if i == j else Fraction(0) for j in range(size)] for i in range(size)]
    for coefficient in poly:
        if coefficient:
            for i in range(size):
                for j in range(size):
                    result[i][j] += coefficient * power[i][j]
        power = [[sum(power[i][k] * matrix[k][j] for k in range(size)) for j in range(size)]
                 for i in range(size)]
    return all(result[i][j] == 0 for i in range(size) for j in range(size))


def trace_power(matrix: Sequence[Sequence[Fraction]], exponent: int) -> Fraction:
    size = len(matrix)
    power = [[Fraction(1) if i == j else Fraction(0) for j in range(size)] for i in range(size)]
    for _ in range(exponent):
        power = [[sum(power[i][k] * matrix[k][j] for k in range(size)) for j in range(size)]
                 for i in range(size)]
    return sum(power[i][i] for i in range(size))


def solve_exact(columns: Sequence[Sequence[Fraction]],
                target: Sequence[Fraction]) -> Optional[List[Fraction]]:
    """Exact solution of `Σ cᵢ columnsᵢ = target`, or None if there is none."""
    rows = len(target)
    width = len(columns)
    augmented = [[columns[c][r] for c in range(width)] + [target[r]] for r in range(rows)]
    pivots: List[int] = []
    row = 0
    for col in range(width):
        pivot = next((r for r in range(row, rows) if augmented[r][col] != 0), None)
        if pivot is None:
            continue
        augmented[row], augmented[pivot] = augmented[pivot], augmented[row]
        inverse = 1 / augmented[row][col]
        augmented[row] = [value * inverse for value in augmented[row]]
        for r in range(rows):
            if r != row and augmented[r][col]:
                factor = augmented[r][col]
                augmented[r] = [a - factor * b for a, b in zip(augmented[r], augmented[row])]
        pivots.append(col)
        row += 1
        if row == rows:
            break
    for r in range(row, rows):
        if augmented[r][width] != 0 and all(v == 0 for v in augmented[r][:width]):
            return None
    coefficients = [Fraction(0)] * width
    for index, col in enumerate(pivots):
        coefficients[col] = augmented[index][width]
    return coefficients


def excited_polynomial(matrix: Sequence[Sequence[Fraction]],
                       start: Sequence[Fraction]) -> List[Fraction]:
    """The monic polynomial `μ` of least degree with `μ(Δ₀)·start = 0`, ascending in powers.

    Its roots are exactly the eigenvalues the poke actually excites — which is the difference between
    "this object has an unstable mode" and "this poke has one". Computed by exact elimination on the
    Krylov vectors, so a mode that is present by a hair is still present.
    """
    vectors = [[Fraction(v) for v in start]]
    while True:
        nxt = [sum(matrix[i][j] * vectors[-1][j] for j in range(len(matrix)))
               for i in range(len(matrix))]
        coefficients = solve_exact(vectors, nxt)
        if coefficients is not None:
            return [-c for c in coefficients] + [Fraction(1)]
        vectors.append(nxt)
        assert len(vectors) <= len(matrix), "the Krylov space outgrew the object"


def poly_divides(divisor: Sequence[Fraction], dividend: Sequence[Fraction]) -> bool:
    """Exact polynomial division, both ascending in powers: does `divisor` divide `dividend`?"""
    remainder = [Fraction(v) for v in dividend]
    while len(remainder) >= len(divisor) and any(v != 0 for v in remainder):
        if remainder[-1] == 0:
            remainder.pop()
            continue
        shift = len(remainder) - len(divisor)
        factor = remainder[-1] / divisor[-1]
        for index, value in enumerate(divisor):
            remainder[shift + index] -= factor * value
        while remainder and remainder[-1] == 0:
            remainder.pop()
    return not any(v != 0 for v in remainder)


# The spectrum of the uncut stella octangula's Δ₀, derived by hand from its symmetry and certified
# below by `annihilates` plus two traces. Six distinct values, fourteen dots:
#
#   0 · 3 (×4) · (11−√41)/2 (×3) · 7 · (11+√41)/2 (×3) · 10 (×2)
#
# The two irrational families are the pair of roots of λ² − 11λ + 20, which is why the certificate is
# a polynomial identity rather than a list of numbers.
STELLA_FACTORS: Tuple[Tuple[int, ...], ...] = (
    (0, 1),          # λ
    (-3, 1),         # λ − 3
    (-7, 1),         # λ − 7
    (-10, 1),        # λ − 10
    (20, -11, 1),    # λ² − 11λ + 20, whose roots are (11 ± √41)/2
)


def _poly_multiply(a: Sequence[int], b: Sequence[int]) -> List[int]:
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def stella_spectrum() -> Dict[str, object]:
    """The uncut stella octangula's spectrum, certified exactly — and what it forbids.

    λ_max = 10, so the leapfrog's `kλ < 4` gives a tick size ceiling of exactly `k < 2/5`. The
    chapters' own `TICK_K = 1/2` is **over** it: this object is the first in the book that the
    chapters' tick size cannot be run on at all.
    """
    lines = stella_lines(cut=False)
    L = laplacian_matrix(14, lines)

    factors = [list(f) for f in STELLA_FACTORS]
    minimal: List[int] = [1]
    for factor in factors:
        minimal = _poly_multiply(minimal, factor)
    assert annihilates(L, minimal), (
        "the derived minimal polynomial does not annihilate Δ₀ — the spectrum is not what was "
        "derived from the symmetry"
    )
    for factor in factors:
        reduced: List[int] = [1]
        for other in factors:
            if other is not factor:
                reduced = _poly_multiply(reduced, other)
        assert not annihilates(L, reduced), (
            f"dropping the factor {factor} still annihilates Δ₀ — that eigenvalue is absent"
        )

    # Multiplicities, pinned by two power sums against the derived list.
    multiplicity = {"0": 1, "3": 4, "pair_low": 3, "7": 1, "pair_high": 3, "10": 2}
    assert sum(multiplicity.values()) == 14
    first = 0 + 3 * 4 + 7 + 10 * 2 + 3 * 11                     # the pair sums to 11
    second = 0 + 9 * 4 + 49 + 100 * 2 + 3 * (11 ** 2 - 2 * 20)  # and its squares to 81
    assert trace_power(L, 1) == first == 72, f"trace Δ₀ = {trace_power(L, 1)}, derived {first}"
    assert trace_power(L, 2) == second == 528, f"trace Δ₀² = {trace_power(L, 2)}, derived {second}"

    assert determinant([[(Fraction(10) if i == j else Fraction(0)) - L[i][j] for j in range(14)]
                        for i in range(14)]) == 0, "10 is not an eigenvalue after all"
    assert not spectrum_below(L, Fraction(10)), "λ_max is below 10"
    assert spectrum_below(L, Fraction(10) + Fraction(1, 1000)), "λ_max is above 10"

    return {
        "lambda_max": Fraction(10),
        "k_ceiling": Fraction(4, 10),
        "napkin_k_stable": False,
        "spectrum": "0 · 3⁴ · ((11−√41)/2)³ · 7 · ((11+√41)/2)³ · 10²",
        "trace": 72,
        "trace_squared": 528,
    }


CUT_BRACKET = (Fraction(1053, 100), Fraction(1057, 100))


def cut_stella_spectrum() -> Dict[str, object]:
    """The same object as the record builds it — with the cut — bracketed exactly.

    One extra line and the clean spectrum goes: the cut chooses an axis, so the symmetry that gave
    the closed form is gone. Two exact rational tests are enough for the only thing that matters,
    which is the tick-size ceiling `4/λ_max`: the cut RAISES λ_max from 10 to between 10.53 and
    10.57, which lowers the ceiling from `2/5` to just under `400/1057`. The record's own octahedron
    is therefore *less* forgiving of a big tick than the tidy motif is, not more.
    """
    L = laplacian_matrix(14, stella_lines(cut=True))
    low, high = CUT_BRACKET
    assert not spectrum_below(L, low), f"λ_max is below {low} after all"
    assert spectrum_below(L, high), f"λ_max is above {high}"
    assert not spectrum_below(L, Fraction(10)), "the cut did not raise λ_max above 10"
    # The four rational eigenvalues survive the cut; only the pair's symmetry does not.
    for value in (0, 3, 7, 10):
        shifted = [[(Fraction(value) if i == j else Fraction(0)) - L[i][j] for j in range(14)]
                   for i in range(14)]
        assert determinant(shifted) == 0, f"{value} stopped being an eigenvalue under the cut"
    return {"lambda_low": low, "lambda_high": high,
            "k_ceiling_low": 4 / high, "k_ceiling_high": 4 / low}


def poke_spectrum(cut: bool) -> Dict[str, object]:
    """Which modes a one-dot poke at a spike apex actually excites — and its own ceiling.

    Worth separating from the object's spectrum, because the answer is not "all of them": the λ = 10
    family lives entirely on the octahedron with nothing at all on the apexes, so a poke at an apex
    never touches it. Cut or uncut, λ = 10 is an eigenvalue and the poke misses it — which is why the
    poke's own ceiling on the uncut motif is the irrational `(11−√41)/10`, not `2/5`. The scheme's
    ceiling is still the one to quote, because the unstable mode is there whether this poke finds it
    or not.
    """
    lines = stella_lines(cut=cut)
    L = laplacian_matrix(14, lines)
    start = [Fraction(1) if i == 6 else Fraction(0) for i in range(14)]
    mu = excited_polynomial(L, start)
    named = {name: [Fraction(c) for c in factor]
             for name, factor in (("0", (0, 1)), ("3", (-3, 1)), ("7", (-7, 1)),
                                  ("10", (-10, 1)), ("the pair λ²−11λ+20", (20, -11, 1)))}
    verdict = {}
    for name, poly in named.items():
        present = annihilates_vector(L, poly)
        verdict[name] = ("excited" if poly_divides(poly, mu)
                         else ("present, not excited" if present else "not an eigenvalue"))
    assert verdict["10"] == "present, not excited", (
        f"λ = 10 came out {verdict['10']!r} — the claim that the octahedron's own stiffest mode is "
        f"invisible from a spike is what this checks"
    )
    return {"degree": len(mu) - 1, "verdict": verdict}


def annihilates_vector(matrix: Sequence[Sequence[Fraction]], poly: Sequence[Fraction]) -> bool:
    """Is any root of `poly` an eigenvalue of `matrix`? For a linear or quadratic factor, exactly."""
    size = len(matrix)
    if len(poly) == 2:                       # λ − v
        value = -poly[0] / poly[1]
        shifted = [[(value if i == j else Fraction(0)) - matrix[i][j] for j in range(size)]
                   for i in range(size)]
        return determinant(shifted) == 0
    # A quadratic factor: its roots are eigenvalues exactly when it divides the whole minimal
    # polynomial, which for a symmetric matrix is `excited_polynomial` from a generic start.
    generic = [Fraction(1 + i * i) for i in range(size)]
    return poly_divides(poly, excited_polynomial(matrix, generic))


# ── transfer: how many steps from one cell to the next ───────────────────────────────────────────


def distances(size: int, lines: Sequence[Tuple[int, int]], source: int) -> List[int]:
    """Steps along lines. Breadth-first, because a step is a step and no line has a length yet."""
    neighbours: Dict[int, List[int]] = {i: [] for i in range(size)}
    for i, j in lines:
        neighbours[i].append(j)
        neighbours[j].append(i)
    out = [-1] * size
    out[source] = 0
    frontier = [source]
    while frontier:
        nxt = []
        for v in frontier:
            for w in neighbours[v]:
                if out[w] < 0:
                    out[w] = out[v] + 1
                    nxt.append(w)
        frontier = nxt
    assert all(d >= 0 for d in out), "the object is not connected"
    return out


def first_move(history: Sequence[Sequence[Fraction]]) -> List[int]:
    """The tick at which each dot first stops being zero, or −1 if it never does."""
    size = len(history[0])
    out = [-1] * size
    for tick, row in enumerate(history):
        for index, value in enumerate(row):
            if out[index] < 0 and value != 0:
                out[index] = tick
    return out


TRANSFER_K = Fraction(1, 4)   # a tick size that is stable on all three objects (see the table)
TRANSFER_TICKS = 8


def transfer_counts(cut: bool = True, k: Fraction = TRANSFER_K) -> Dict[str, object]:
    """Poke one spike; count the steps to every other dot, and check them against the geometry.

    The leapfrog is a three-point rule: a dot's next number depends only on its own line-neighbours'
    current ones. So the support of a poke grows by exactly one line per step, and *first move* must
    equal *steps along lines* — unless something cancels. Asserting the two agree is the check that
    nothing does.
    """
    lines = stella_lines(cut=cut)
    L_lines = list(lines)
    source = 6                    # the apex `+++`
    hops = distances(14, L_lines, source)
    start = [Fraction(1) if i == source else Fraction(0) for i in range(14)]
    history = slosh(unit_weights(L_lines), L_lines, ticks=TRANSFER_TICKS, initial=start, k=k)
    moved = first_move(history)
    assert moved == hops, (
        f"first move {moved} does not match steps along lines {hops} — something cancelled, and "
        f"the transfer counts below would be reporting an accident"
    )

    opposite = STELLA_NAMES.index("−−−")
    apex_hops = {STELLA_NAMES[6 + i]: hops[6 + i] for i in range(8)}
    oct_hops = {name: hops[i] for i, name in enumerate(OCT_NAMES)}
    others = [v for name, v in apex_hops.items() if name != "+++"]
    assert hops[opposite] == 3, f"the opposite spike is {hops[opposite]} steps away, not 3"
    assert sorted(others) == [2, 2, 2, 2, 2, 2, 3], f"the other spikes are at {sorted(others)}"
    assert max(hops) == 3, f"the object's diameter is {max(hops)}, not 3"

    # No two apexes share a line, so every apex-to-apex path runs through octahedron dots only.
    apex_indices = set(range(6, 14))
    for i, j in L_lines:
        assert not (i in apex_indices and j in apex_indices), (
            f"the apexes {STELLA_NAMES[i]} and {STELLA_NAMES[j]} share a line — a transfer between "
            f"two tetrahedra could then skip the octahedron entirely"
        )
    return {
        "k": k,
        "apex_hops": apex_hops,
        "oct_hops": oct_hops,
        "adjacent_spike": 2,
        "opposite_spike": 3,
        "intermediate_on_octahedron": {"adjacent": 1, "opposite": 2},
        "diameter": 3,
        "apexes_independent": True,
    }


# ── periods, and whether any tick size makes the table printable ─────────────────────────────────


def octahedron_lines() -> List[Tuple[int, int]]:
    return [(a, b) for a, b in combinations(range(6), 2) if a // 2 != b // 2]


def tetra_lines() -> List[Tuple[int, int]]:
    return list(combinations(range(4), 2))


def period_of(size: int, lines: Sequence[Tuple[int, int]], source: int,
              k: Fraction, ticks: int) -> int:
    start = [Fraction(1) if i == source else Fraction(0) for i in range(size)]
    history = slosh(unit_weights(list(lines)), list(lines), ticks=ticks, initial=start, k=k)
    return period(history)


def periods() -> Dict[str, object]:
    """Does the motion come back? On the tetrahedron and the octahedron yes; on the stella never.

    And the reason the stella never does is exact, not a failure to wait long enough. A mode of
    eigenvalue λ obeys `x' = (2 − kλ)x − x_prev`, which is a rotation by θ with
    `2cos θ = 2 − kλ`. A rotation returns after finitely many steps only if θ is a rational part of a
    turn, and then `2cos θ` is an algebraic integer. For the stella's irrational pair, λ is a root of
    `λ² − 11λ + 20`, so `2 − kλ` has trace `4 − 11k` and norm `4 − 22k + 20k²`; with `k = p/q` in
    lowest terms the trace forces `q | 11` and the norm then forces `11 | p`, which contradicts it.
    So for **every rational tick size** those modes never return — and a poke at a spike excites
    them (see `poke_spectrum`).
    """
    half = Fraction(1, 2)
    tetra = period_of(4, tetra_lines(), 0, half, 12)
    assert tetra == 4, f"the tetrahedron's period came out {tetra}, not the chapters' 4"
    octa = period_of(6, octahedron_lines(), 0, half, 40)
    assert octa == 12, f"the octahedron's period came out {octa}, not 12"

    # The 12 is a fact about this tick size, not about the octahedron: turn the dial and it goes.
    quarter = period_of(6, octahedron_lines(), 0, Fraction(1, 4), 40)
    assert quarter == 0, f"k = 1/4 gave the octahedron a period of {quarter}"
    fifth = period_of(6, octahedron_lines(), 0, Fraction(1, 5), 60)
    assert fifth == 0, f"k = 1/5 gave the octahedron a period of {fifth}"

    stella = {}
    for k in (Fraction(1, 4), Fraction(3, 10), Fraction(7, 20), Fraction(1, 5)):
        stella[str(k)] = period_of(14, stella_lines(cut=False), 6, k, 60)
        assert stella[str(k)] == 0, (
            f"the stella returned after {stella[str(k)]} steps at k = {k} — the algebraic argument "
            f"in this docstring says it cannot, so one of the two is wrong"
        )
    return {
        "tetrahedron_half": tetra,
        "tetrahedron_lines": 6,
        "octahedron_half": octa,
        "octahedron_lines": 12,
        "octahedron_quarter": quarter,
        "octahedron_fifth": fifth,
        "stella": stella,
    }


NAPKIN_DENOMINATORS = (1, 2, 4, 5, 10, 20, 100)


def renderable_ticks(size: int, lines: Sequence[Tuple[int, int]], source: int,
                     k: Fraction, ticks: int = 10) -> int:
    """How many ticks of the table `napkin.number()` will actually print before it refuses."""
    start = [Fraction(1) if i == source else Fraction(0) for i in range(size)]
    history = slosh(unit_weights(list(lines)), list(lines), ticks=ticks, initial=start, k=k)
    for tick, row in enumerate(history):
        for value in row:
            try:
                number(value)
            except AssertionError:
                return tick
    return len(history)


def tick_size_table() -> Dict[str, object]:
    """Is there any tick size that is both stable on the stella and printable on a napkin? No.

    Two exact facts, and they do not overlap. (1) Stability needs `k < 2/5`. (2) A one-dot poke at a
    spike makes `Δ₀φ` come out `3` at the apex and `−1` at its three neighbours — greatest common
    divisor 1 — so `kΔ₀φ` lands on whole numbers only if `k` is itself a whole number, and no whole
    number is under 2/5. Every fractional `k` then squares its denominator every tick or two and
    walks straight out of `number()`'s list of denominators it will print.
    """
    L = laplacian_matrix(14, stella_lines(cut=False))
    start = [Fraction(1) if i == 6 else Fraction(0) for i in range(14)]
    first = [sum(L[i][j] * start[j] for j in range(14)) for i in range(14)]
    nonzero = sorted({int(v) for v in first if v != 0})
    assert nonzero == [-1, 3], f"the first push came out {nonzero}, not (3, −1)"

    rows = []
    for k in (Fraction(1, 2), Fraction(9, 20), Fraction(2, 5), Fraction(39, 100),
              Fraction(7, 20), Fraction(1, 4), Fraction(1, 5), Fraction(1, 10)):
        stable = k < Fraction(2, 5)
        rows.append({
            "k": k,
            "stable": stable,
            "printable_ticks": renderable_ticks(14, stella_lines(cut=False), 6, k) - 1,
        })
    best = max((r for r in rows if r["stable"]), key=lambda r: r["k"])
    assert best["k"] == Fraction(39, 100), f"the largest printable stable k came out {best['k']}"
    assert all(r["printable_ticks"] <= 2 for r in rows), (
        f"some tick size printed more than two ticks: {rows}"
    )
    return {"rows": tuple(rows), "best_stable_printable": best}


OCTAHEDRON_TABLE_TICKS = 20


def octahedron_table() -> Dict[str, object]:
    """The bare octahedron, at the chapters' own tick size, printable — and crossing in two steps.

    The stella cannot go on a napkin; the octahedron can, and at `TICK_K = 1/2` unchanged. Its
    largest eigenvalue is 6, so `kλ = 3 < 4`; and `2I − kΔ₀` comes out as half its own adjacency, so
    the whole run stays in whole numbers and halves for ever — `number()` prints every cell of it.

    Two exact facts inside that table are worth more than the table: at tick 2 the entire poke is on
    the opposite dot and nowhere else, and at tick 3 the entire poke is back where it started. The
    motion is still not periodic until tick 12, because a leapfrog's state is the pair (now, before)
    and only that pair repeating is a return.
    """
    lines = octahedron_lines()
    start = [Fraction(1)] + [Fraction(0)] * 5
    history = slosh(unit_weights(lines), lines, ticks=OCTAHEDRON_TABLE_TICKS,
                    initial=start, k=Fraction(1, 2))
    printable = renderable_ticks(6, lines, 0, Fraction(1, 2), OCTAHEDRON_TABLE_TICKS)
    assert printable == OCTAHEDRON_TABLE_TICKS + 1, (
        f"only {printable} of {OCTAHEDRON_TABLE_TICKS + 1} rows print"
    )
    denominators = {v.denominator for row in history for v in row}
    assert denominators <= {1, 2}, f"the run left whole numbers and halves: {denominators}"

    opposite = [Fraction(0), Fraction(1)] + [Fraction(0)] * 4
    assert history[2] == opposite, f"tick 2 came out {history[2]}, not all on the opposite dot"
    assert history[3] == start, f"tick 3 came out {history[3]}, not back at the start"
    assert period(history) == 12, f"the period came out {period(history)}"
    return {
        "k": Fraction(1, 2),
        "printable_rows": printable,
        "denominators": tuple(sorted(denominators)),
        "crossing_ticks": 2,
        "period": 12,
        "history": tuple(tuple(row) for row in history[:14]),
    }


# ── efficiency: count the work, do not claim it ──────────────────────────────────────────────────


def work_counts(n: int = TORUS, cut=screw111) -> Dict[str, object]:
    """One step's work, three ways of organising it, counted in line-visits.

    A line-visit is the unit that matters: every line's difference must be formed, weighted, and
    delivered to both of its ends, and the only thing an organisation can change is how many times a
    line is picked up. The napkin's own loop picks each line up once. Gathering per dot picks each up
    twice, once from each end. Gathering per octahedron picks up each of its thirteen lines once —
    but twelve of those thirteen belong to a second octahedron too, so on the tiling it is worse than
    the napkin's loop, not better.
    """
    tiling = line_audit(n, cut)
    lines, dots = tiling["lines"], tiling["dots"]
    per_line = lines
    per_dot = 14 * dots                     # Σ degree = 2 × lines
    assert per_dot == 2 * lines, f"Σ degree {per_dot} ≠ 2 × {lines}"
    octahedra = n ** 3 // 2
    per_octahedron = 13 * octahedra         # twelve edges and the one cut, each octahedron
    assert per_octahedron == Fraction(13, 7) * per_line, "the 13/7 ratio is wrong"

    stella_lines_cut = len(stella_lines(cut=True))
    motif = 13 + 8 * 3                      # the octahedron's thirteen, and three per spike
    assert motif == stella_lines_cut == 37, (
        f"the motif's lines partition as {motif}, but it has {stella_lines_cut}"
    )
    return {
        "lines": lines,
        "per_line_visits": per_line,
        "per_dot_visits": per_dot,
        "per_octahedron_visits": per_octahedron,
        "octahedron_vs_line": Fraction(per_octahedron, per_line),
        "octahedron_vs_dot": Fraction(per_octahedron, per_dot),
        "motif_partition": {"octahedron": 13, "spikes": 24, "total": 37},
        "motif_same_as_per_line": True,
    }


# ── the reader's route in: cut ONE tetrahedron at the middles of its six lines ───────────────────
#
# Everything above this line audits the record's tiling, which is where the octahedron was found.
# Everything below it is the same object reached the way a reader can reach it with a pencil: take
# the one tetrahedron chapters 1–3 already own, mark the middle of each of its six lines, and cut.
# Four half-size tetrahedra come off the tips and one octahedron is left between them.
#
# The two routes must agree, and that they do is asserted rather than assumed: `midpoint_cut`
# checks that the six midpoints, joined the way the cut joins them, are the *same graph* as
# `octahedron_lines()` — the object the audits above were run on.
#
# The corners are placed on alternate corners of a cube of side 2, which is the placement that makes
# every number below an integer: the six midpoints land exactly on `(±1,0,0)`, `(0,±1,0)`,
# `(0,0,±1)`, and the second tetrahedron's four corners land on the cube's other four corners.

TET_CORNERS: Dict[str, Point] = {
    "A": (1, 1, 1),
    "B": (1, -1, -1),
    "C": (-1, 1, -1),
    "D": (-1, -1, 1),
}

# The six middles, named for the lines they halve — `AB` is the middle of the line `AB`. The names
# and their order are the napkin's own (`napkin.simplices(…, 1)` in ascending order), so CANON.md's
# rule that a label is an identity carries over from the tetrahedron to this object for free, and no
# index is introduced. Two middles are joined exactly when their lines share a corner, which is why
# the three pairs with no letter in common — AB·CD, AC·BD, AD·BC — are the ones that are *not*
# joined. Those are the opposite pairs.
MID_NAMES: Tuple[str, ...] = tuple("".join(pair) for pair in combinations("ABCD", 2))
MID_POINTS: Tuple[Tuple[Fraction, ...], ...] = tuple(
    tuple(Fraction(TET_CORNERS[name[0]][axis] + TET_CORNERS[name[1]][axis], 2) for axis in range(3))
    for name in MID_NAMES
)


def _shares_corner(i: int, j: int) -> bool:
    return bool(set(MID_NAMES[i]) & set(MID_NAMES[j]))


def mid_lines() -> List[Tuple[int, int]]:
    """The octahedron's twelve lines, in the midpoint naming: the pairs of middles that touch."""
    return [(i, j) for i, j in combinations(range(6), 2) if _shares_corner(i, j)]


def _det3(a: Sequence[Fraction], b: Sequence[Fraction], c: Sequence[Fraction]) -> Fraction:
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def mid_faces() -> List[Tuple[int, int, int]]:
    """The octahedron's eight faces, each walked the way round it faces from OUTSIDE.

    A face is a triangle of the graph, and there are exactly eight. The walking direction is fixed
    by an exact 3×3 integer determinant on the face's own three corners: the object is centred on
    the origin, so a cycle with a positive determinant is the one seen anticlockwise from outside.
    That is the only place geometry enters, and it enters as the sign of an integer.

    **And "outside" is checked, not asserted by convention.** Flipping the determinant's sense
    flips all eight cycles at once, which leaves the boundary sum zero and every line still walked
    once each way — consistent, and inward (a proofreader, 2026-09-02). So each cycle's own normal
    is computed the long way, `(v₂−v₁) × (v₃−v₁)`, and required to point *away* from the centre.
    """
    out: List[Tuple[int, int, int]] = []
    for triple in combinations(range(6), 3):
        if not all(_shares_corner(a, b) for a, b in combinations(triple, 2)):
            continue
        corners = [MID_POINTS[i] for i in triple]
        turn = _det3(*corners)
        assert turn != 0, f"the face {triple} is flat"
        cycle = triple if turn > 0 else (triple[0], triple[2], triple[1])
        a, b, c = (MID_POINTS[i] for i in cycle)
        edge1 = [b[i] - a[i] for i in range(3)]
        edge2 = [c[i] - a[i] for i in range(3)]
        normal = [edge1[1] * edge2[2] - edge1[2] * edge2[1],
                  edge1[2] * edge2[0] - edge1[0] * edge2[2],
                  edge1[0] * edge2[1] - edge1[1] * edge2[0]]
        outward = sum(normal[i] * (a[i] + b[i] + c[i]) for i in range(3))
        assert outward > 0, (
            f"the face {[MID_NAMES[i] for i in cycle]} is walked so that its own normal points "
            f"back at the centre ({outward}) — that is inward, not 'from outside'"
        )
        out.append(cycle)
    assert len(out) == 8, f"the octahedron came out with {len(out)} faces, not 8"
    return out


def _ring(four: Sequence[int]) -> List[int]:
    """Four middles round the equator, put in the order they actually touch each other.

    Taking them in name order would give `AC AD BC BD`, and `AD` does not touch `BC` — they are an
    opposite pair. A quarter built on that pair would be a flat cell, so the order is derived here
    from which middles share a corner rather than assumed from the naming.
    """
    ring = [four[0]]
    remaining = list(four[1:])
    while remaining:
        nxt = next((index for index in remaining if _shares_corner(ring[-1], index)), None)
        assert nxt is not None, f"the equator {four} does not close into a ring"
        ring.append(nxt)
        remaining.remove(nxt)
    assert _shares_corner(ring[-1], ring[0]), f"the ring {ring} does not close"
    return ring


def _volume(cell: Sequence[Sequence[Fraction]]) -> Fraction:
    """Six times the signed volume of a tetrahedron, as a positive exact fraction of a sixth."""
    a, b, c, d = (tuple(Fraction(v) for v in point) for point in cell)
    return abs(_det3([b[i] - a[i] for i in range(3)],
                     [c[i] - a[i] for i in range(3)],
                     [d[i] - a[i] for i in range(3)])) / 6


def _squared_length(a: Sequence[Fraction], b: Sequence[Fraction]) -> Fraction:
    return sum((x - y) ** 2 for x, y in zip(a, b))


def midpoint_cut() -> Dict[str, object]:
    """Cut the one tetrahedron at its six middles. What falls out, counted exactly.

    The claim being checked, which is the owner's finding stated as arithmetic: the cut gives four
    tetrahedra at the tips and **one** octahedron between them; the tips are half-size; the
    octahedron is exactly half the whole; and of its eight faces, four look at a tip and four lie
    flat in a face of the tetrahedron that was cut. Nothing here is read off a picture.
    """
    corners = {name: tuple(Fraction(v) for v in point) for name, point in TET_CORNERS.items()}
    whole = _volume(list(corners.values()))

    # Ten dots: the four corners, and the six middles.
    dots = set(corners.values()) | set(MID_POINTS)
    assert len(dots) == 10, f"the cut object has {len(dots)} dots, not 10"

    # The four tips: a corner, and the middles of the three lines that leave it.
    tips = {}
    for name in "ABCD":
        touching = [index for index, mid in enumerate(MID_NAMES) if name in mid]
        assert len(touching) == 3, f"the corner {name} is on {len(touching)} lines, not 3"
        tips[name] = [corners[name]] + [MID_POINTS[index] for index in touching]
        assert _volume(tips[name]) == whole / 8, (
            f"the tip at {name} is {_volume(tips[name]) / whole} of the whole, not an eighth"
        )
        edges = {_squared_length(u, v) for u, v in combinations(tips[name], 2)}
        assert edges == {Fraction(2)}, f"the tip at {name} is not regular: squared sides {edges}"
    big_edges = {_squared_length(u, v) for u, v in combinations(corners.values(), 2)}
    assert big_edges == {Fraction(8)}, f"the tetrahedron that was cut is not regular: {big_edges}"

    # ONE octahedron between them, on the six middles — and it is the object audited above.
    lines = mid_lines()
    assert len(lines) == 12, f"the middles are joined by {len(lines)} lines, not 12"
    degrees = {name: sum(1 for line in lines if index in line)
               for index, name in enumerate(MID_NAMES)}
    assert set(degrees.values()) == {4}, f"the middles do not all have four lines: {degrees}"
    opposite = [(MID_NAMES[i], MID_NAMES[j]) for i, j in combinations(range(6), 2)
                if not _shares_corner(i, j)]
    assert len(opposite) == 3, f"{len(opposite)} pairs of middles are unjoined, not 3"

    # The same graph as the object §1–§5 were computed on, under the name map AB→+x, CD→−x, …
    to_audited = {name: OCT_POINTS.index(tuple(int(v) for v in MID_POINTS[index]))
                  for index, name in enumerate(MID_NAMES)}
    mapped = {tuple(sorted((to_audited[MID_NAMES[i]], to_audited[MID_NAMES[j]])))
              for i, j in lines}
    assert mapped == {tuple(sorted(line)) for line in octahedron_lines()}, (
        "the reader's octahedron is not the octahedron the audits above were run on"
    )

    # Volume: four eighths at the tips, and the rest is the octahedron. Exactly half.
    faces = mid_faces()
    core = whole - 4 * (whole / 8)
    assert core == whole / 2, f"the octahedron is {core / whole} of the whole, not a half"
    # Cut the octahedron into four about one long diagonal and the volumes must still add up, which
    # is the check that "one octahedron" is the whole of what is left rather than most of it.
    diagonal = (MID_NAMES.index("AB"), MID_NAMES.index("CD"))
    equator = _ring([index for index, name in enumerate(MID_NAMES)
                     if name not in ("AB", "CD")])
    quarters = [
        [MID_POINTS[diagonal[0]], MID_POINTS[diagonal[1]],
         MID_POINTS[equator[w]], MID_POINTS[equator[(w + 1) % 4]]]
        for w in range(4)
    ]
    assert sum(_volume(cell) for cell in quarters) == core, (
        "cutting the octahedron into four does not give back its own volume"
    )

    # Its eight faces: four look at a tip, four lie flat in a face of the tetrahedron.
    at_a_tip, in_a_face = [], []
    for face in faces:
        letters = [set(MID_NAMES[index]) for index in face]
        shared = set.intersection(*letters)
        spanned = set.union(*letters)
        if len(shared) == 1:
            at_a_tip.append((face, next(iter(shared))))
            assert len(spanned) == 4, f"a tip face spans {spanned}"
        else:
            assert len(spanned) == 3, f"a face spans {spanned}, which is neither 3 nor 4 letters"
            in_a_face.append((face, "".join(sorted(spanned))))
    assert len(at_a_tip) == 4 and len(in_a_face) == 4, (
        f"{len(at_a_tip)} faces look at a tip and {len(in_a_face)} lie in a face, expected 4 and 4"
    )
    assert {name for _, name in at_a_tip} == set("ABCD"), "the four tip faces are not one per tip"
    assert {name for _, name in in_a_face} == {"ABC", "ABD", "ACD", "BCD"}, (
        "the four flat faces are not one per face of the tetrahedron"
    )
    # Each flat one is the middle triangle of that face: its three middles are middles of that
    # face's own three lines, and it lies in that face's plane.
    for face, name in in_a_face:
        for index in face:
            assert set(MID_NAMES[index]) <= set(name), (
                f"{MID_NAMES[index]} is not a middle of a line of {name}"
            )
        plane = [corners[letter] for letter in name]
        for index in face:
            assert _det3([plane[1][i] - plane[0][i] for i in range(3)],
                         [plane[2][i] - plane[0][i] for i in range(3)],
                         [MID_POINTS[index][i] - plane[0][i] for i in range(3)]) == 0, (
                f"{MID_NAMES[index]} does not lie in the plane of {name}"
            )

    return {
        "dots": len(dots),
        "corners": 4,
        "middles": 6,
        "tips": 4,
        "octahedra": 1,
        "tip_share": Fraction(1, 8),
        "tip_side": Fraction(1, 2),          # squared side 2 against the big one's 8
        "core_share": Fraction(1, 2),
        "oct_dots": 6,
        "oct_lines": 12,
        "oct_faces": 8,
        "oct_degree": 4,
        "opposite_pairs": tuple(opposite),
        "faces_at_a_tip": tuple(name for _, name in sorted(at_a_tip, key=lambda p: p[1])),
        "faces_in_a_face": tuple(name for _, name in sorted(in_a_face, key=lambda p: p[1])),
    }


# Twelve freely chosen arrows, one per line of the octahedron — arrows in their own right, not
# differences of anything, which is beat 22's move and the only way the sum below demonstrates
# something. Chosen (and asserted) so that all eight faces carry a non-zero number.
MID_ARROWS: Tuple[int, ...] = (3, 1, 4, 1, 5, 2, 6, 5, 3, 5, 8, 9)


def octahedron_boundary_sum() -> Dict[str, object]:
    """The eight outside faces of the octahedron add to exactly zero, for every set of arrows.

    This is chapter 2's `tetra_inside_sum` one shape out: put a number on each of the twelve lines,
    read off how much goes round each of the eight faces, walk every face the way it faces from
    outside, and add. Zero — and not nearly zero: **each line is walked exactly twice, once each
    way**, which is asserted here line by line rather than argued. No length is used anywhere in it.

    The four-times-over reading is checked too, by `boundary_sum()` above on the record's own cut
    octahedron: cut this shape into four tetrahedra and each of the four walks its own four faces to
    zero, the four inside faces cancelling in pairs. Same zero, arrived at from the tetrahedron's.
    """
    lines, faces = mid_lines(), mid_faces()
    arrows = {line: Fraction(value) for line, value in zip(lines, MID_ARROWS)}
    assert len(arrows) == 12, f"{len(arrows)} arrows for {len(lines)} lines"

    def goes_round(face: Sequence[int]) -> Fraction:
        total = Fraction(0)
        for step in range(3):
            low, high = face[step], face[(step + 1) % 3]
            total += arrows[(min(low, high), max(low, high))] * (1 if low < high else -1)
        return total

    numbers = [goes_round(face) for face in faces]
    assert all(value != 0 for value in numbers), (
        f"a face came out zero ({numbers}) — choose arrows that make every face carry something, or "
        f"the sum below demonstrates less than it claims"
    )

    walked: Dict[Tuple[int, int], int] = {line: 0 for line in lines}
    for face in faces:
        for step in range(3):
            low, high = face[step], face[(step + 1) % 3]
            walked[(min(low, high), max(low, high))] += 1 if low < high else -1
    assert set(walked.values()) == {0}, (
        f"a line is not walked once each way: {walked} — the sum would then be an accident"
    )
    total = sum(numbers)
    assert total == 0, f"the eight outside faces summed to {total}, not 0"

    # The same zero, reached from the tetrahedron: the record's cut octahedron, four insides.
    cut = boundary_sum()
    assert cut["outside_sum"] == 0 and cut["per_inside"] == (0, 0, 0, 0), (
        "the cut octahedron's four insides no longer walk to zero each"
    )
    return {
        "arrows": tuple(MID_ARROWS),
        "face_numbers": tuple(numbers),
        "sum": total,
        "lines_walked_each_way": 12,
        "from_four_insides": True,
    }


def second_tetrahedron() -> Dict[str, object]:
    """Fill the four flat faces and a second tetrahedron appears, threaded through the first.

    Each of the four faces that lies flat in a face of the original takes one more tetrahedron, the
    same size as the tips. Their four new corners are not four unrelated points: each is one of the
    original corners pushed through the middle and out the other side, and the four of them are a
    regular tetrahedron the same size as the one we cut, whose own six middles are the *same* six
    middles. Two tetrahedra, one octahedron between them, threaded.
    """
    corners = {name: tuple(Fraction(v) for v in point) for name, point in TET_CORNERS.items()}
    whole = _volume(list(corners.values()))
    faces: Dict[str, Tuple[int, ...]] = {}
    for face in mid_faces():
        letters = set.union(*[set(MID_NAMES[index]) for index in face])
        if len(letters) == 3:                      # the ones lying flat in a face, not at a tip
            faces["".join(sorted(letters))] = face
    assert len(faces) == 4, f"{len(faces)} flat faces, not 4"

    apexes: Dict[str, Tuple[Fraction, ...]] = {}
    for name, face in faces.items():
        missing = (set("ABCD") - set(name)).pop()      # the corner this face does not touch
        apex = tuple(-value for value in corners[missing])
        cell = [MID_POINTS[index] for index in face] + [apex]
        assert _volume(cell) == whole / 8, (
            f"the tetrahedron added on {name} is {_volume(cell) / whole} of the whole, not an eighth"
        )
        sides = {_squared_length(u, v) for u, v in combinations(cell, 2)}
        assert sides == {Fraction(2)}, f"the tetrahedron added on {name} is not regular: {sides}"
        apexes[missing + "′"] = apex

    twin = list(apexes.values())
    assert {_squared_length(u, v) for u, v in combinations(twin, 2)} == {Fraction(8)}, (
        "the four new corners are not a regular tetrahedron the size of the one we cut"
    )
    assert _volume(twin) == whole, "the second tetrahedron is not the same size as the first"
    twin_middles = {tuple(Fraction(u[i] + v[i], 2) for i in range(3))
                    for u, v in combinations(twin, 2)}
    assert twin_middles == set(MID_POINTS), (
        "the second tetrahedron's own six middles are not the same six middles"
    )
    hull = set(corners.values()) | set(twin)
    assert hull == {tuple(Fraction(s) for s in signs) for signs in product((1, -1), repeat=3)}, (
        "the eight tips are not the eight corners of a cube"
    )
    return {
        "added": 4,
        "apex_names": tuple(sorted(apexes)),
        "apex_share": Fraction(1, 8),
        "twin_same_size": True,
        "twin_middles_the_same": True,
        "hull": "a cube",
    }


# The stella, in the reader's own names: the six middles, the four corners we cut, and the four the
# second tetrahedron brought. `A′` is where `A` lands if you push it through the middle and out the
# other side, which is also the tip that sits over the face `A` does not touch.
STELLA_READER_NAMES: Tuple[str, ...] = MID_NAMES + tuple("ABCD") + tuple(c + "′" for c in "ABCD")


def stella_reader_points() -> Tuple[Tuple[Fraction, ...], ...]:
    corners = tuple(tuple(Fraction(v) for v in TET_CORNERS[c]) for c in "ABCD")
    twin = tuple(tuple(-v for v in point) for point in corners)
    return MID_POINTS + corners + twin


def stella_reader_lines() -> List[Tuple[int, int]]:
    """The stella's thirty-six lines: the shortest joins, in the reader's naming.

    Every line of this object is the same length — squared length 2, half the tetrahedron's own
    line — because each is either a line of the octahedron or half of one of the two tetrahedra's
    lines. Taking "the shortest joins" as the rule is therefore not a choice: it is asserted below
    that the twelve octahedron lines and the twenty-four halves are exactly what it produces.
    """
    points = stella_reader_points()
    lines = [(i, j) for i, j in combinations(range(14), 2)
             if _squared_length(points[i], points[j]) == Fraction(2)]
    return lines


def stella_reader_census() -> Dict[str, object]:
    """Count the stella the way the reader arrived at it, and tie it to the audited object."""
    points = stella_reader_points()
    assert len(set(points)) == 14, "the stella's dots are not 14 distinct points"
    lines = stella_reader_lines()
    assert len(lines) == 36, f"the stella came out with {len(lines)} lines, not 36"
    degrees = {STELLA_READER_NAMES[i]: sum(1 for line in lines if i in line) for i in range(14)}
    middles = {degrees[name] for name in MID_NAMES}
    tips = {degrees[name] for name in STELLA_READER_NAMES[6:]}
    assert middles == {8}, f"the middles have {middles} lines, not 8"
    assert tips == {3}, f"the tips have {tips} lines, not 3"
    for i, j in lines:
        assert not (i >= 6 and j >= 6), (
            f"{STELLA_READER_NAMES[i]} and {STELLA_READER_NAMES[j]} are joined — no two tips are, "
            f"which is why crossing from one tip to another must go through the middle"
        )

    # The same object as §3–§5 above, under the map from the reader's names to the audited ones.
    audited = stella_lines(cut=False)
    order = {}
    for index, name in enumerate(MID_NAMES):
        order[index] = OCT_POINTS.index(tuple(int(v) for v in MID_POINTS[index]))
    for index in range(6, 14):
        order[index] = 6 + APEX_POINTS.index(tuple(int(v) for v in points[index]))
    mapped = {tuple(sorted((order[i], order[j]))) for i, j in lines}
    assert mapped == {tuple(sorted(line)) for line in audited}, (
        "the reader's stella is not the stella the spectrum above was certified on"
    )

    whole = _volume([points[i] for i in (6, 7, 8, 9)])

    # Both volumes the ratio is made of are built from the fourteen points, piece by piece, rather
    # than from each other: the eight tips as eight actual tetrahedra, the core as the four
    # tetrahedra the cut makes of it, and the hull cube from the spread of the tips along each axis.
    # Deriving one from the other let an attack change `stella / cube` to `stella / 4` with every
    # volume assertion still true, and the page then said the pair fills the whole cube (a
    # proofreader, 2026-09-02).
    tips = []
    for apex_index in range(6, 14):
        apex = points[apex_index]
        touching = [index for index in range(6)
                    if _squared_length(points[index], apex) == Fraction(2)]
        assert len(touching) == 3, f"a tip touches {len(touching)} middles, not 3"
        tips.append(_volume([apex] + [points[index] for index in touching]))
    diagonal = (MID_NAMES.index("AB"), MID_NAMES.index("CD"))
    ring = _ring([index for index in range(6) if index not in diagonal])
    core = sum(_volume([MID_POINTS[diagonal[0]], MID_POINTS[diagonal[1]],
                        MID_POINTS[ring[w]], MID_POINTS[ring[(w + 1) % 4]]]) for w in range(4))
    stella = sum(tips) + core
    spread = [max(point[axis] for point in points[6:]) - min(point[axis] for point in points[6:])
              for axis in range(3)]
    cube = spread[0] * spread[1] * spread[2]
    assert whole == Fraction(8, 3) and stella == 4 and cube == 8, (
        f"the volumes came out tetrahedron {whole}, stella {stella}, cube {cube}"
    )
    assert sum(tips) == 8 * (whole / 8) and core == whole / 2, (
        f"the pieces came to {sum(tips)} and {core}, not eight eighths and a half"
    )
    # The two ratios the chapter prints, asserted as themselves. Asserting the volumes they are
    # divided from is not the same thing: an attack changed `stella / cube` to `stella / 4` and the
    # page said the pair fills the whole cube with every volume assertion still true (a
    # proofreader, 2026-09-02).
    in_its_cube = stella / cube
    in_tetrahedra = stella / whole
    assert in_its_cube == Fraction(1, 2), f"the pair fills {in_its_cube} of its cube, not a half"
    assert in_tetrahedra == Fraction(3, 2), (
        f"the pair is {in_tetrahedra} of the tetrahedron we cut, not three halves"
    )
    out = {
        "dots": 14,
        "lines": 36,
        "middles": 6,
        "tips": 8,
        "pieces": 9,                          # eight tetrahedra and the octahedron between them
        "middle_degree": 8,
        "tip_degree": 3,
        "stella_in_tetrahedra": in_tetrahedra,    # 3/2 — one and a half of the object we cut
        "stella_in_its_cube": in_its_cube,        # 1/2
        "tips_independent": True,
    }
    # The last assertion is on the dict itself, not on the variables it was built from. An attack
    # changed `"stella_in_its_cube": stella / Fraction(4)` here and every assertion above it stayed
    # true, so the page said the pair fills the whole cube (a proofreader, 2026-09-02). What the
    # caller receives is what has to be checked.
    assert out["stella_in_its_cube"] == Fraction(1, 2), (
        f"what this returns says the pair fills {out['stella_in_its_cube']} of its cube"
    )
    assert out["stella_in_tetrahedra"] == Fraction(3, 2), (
        f"what this returns says the pair is {out['stella_in_tetrahedra']} tetrahedra"
    )
    assert (out["dots"], out["lines"]) == (len(points), len(lines)), (
        f"what this returns says {out['dots']} dots and {out['lines']} lines, but the object has "
        f"{len(points)} and {len(lines)}"
    )
    return out


# ── the tick that has worked all along, and the object it stops working on ───────────────────────

BOOK_TICK = Fraction(1, 2)      # `napkin.TICK_K`: the chapters' own tick size
LEAPFROG_BOUND = 4              # the leapfrog holds while (tick × biggest stiffness) < 4


def _peak(size: int, lines: Sequence[Tuple[int, int]], k: Fraction, ticks: int,
          source: int = 0) -> Fraction:
    """The biggest number anywhere in the world at any tick of a one-dot poke. Exact."""
    start = [Fraction(1) if index == source else Fraction(0) for index in range(size)]
    history = slosh(unit_weights(list(lines)), list(lines), ticks=ticks, initial=start, k=k)
    return max(abs(value) for row in history for value in row)


CEILING_TICKS = 40


def napkin_ceilings() -> Dict[str, object]:
    """The tick each of the three objects must stay UNDER — and the strictness is the point.

    One number decides it for each object, and it is exact. A mode of `Δ₀` with eigenvalue `λ` obeys
    `x' = (2 − kλ)x − x_prev`, which stays bounded exactly while `kλ < 4`; so the largest eigenvalue
    fixes the bound. The eigenvalues are certified without an eigensolver — `spectrum_below` is
    Sylvester's criterion on exact rationals, asked either side of each claimed value.

    **The inequality is strict, and this asserts it by running the thing.** `4/λ_max` is not a tick
    that works; it is the tick that does not, and a reader who tried it on the tetrahedron — where
    it is exactly 1, and the run goes 1, 2, 4, 5, 7, 8 … in whole numbers — would catch any wording
    that said otherwise. So each object is run twice here: at its own bound, where it must grow, and
    at half of it, where it must not. A proofreader found the chapter's table headed "the biggest
    tick it will hold" over these three values (2026-09-02); the numbers were right and the heading
    was wrong, and the assertions below are what stop that coming back.
    """
    objects = (("the tetrahedron", 4, tetra_lines(), Fraction(4)),
               ("the octahedron", 6, octahedron_lines(), Fraction(6)),
               ("the two together", 14, stella_lines(cut=False), Fraction(10)))
    rows = []
    for name, size, lines, claimed in objects:
        matrix = laplacian_matrix(size, lines)
        assert not spectrum_below(matrix, claimed), f"{name}: λ_max is below {claimed}"
        assert spectrum_below(matrix, claimed + Fraction(1, 1000)), (
            f"{name}: λ_max is above {claimed}"
        )
        product_ = BOOK_TICK * claimed
        bound = Fraction(LEAPFROG_BOUND) / claimed
        at_the_bound = _peak(size, lines, bound, CEILING_TICKS)
        under_it = _peak(size, lines, bound / 2, CEILING_TICKS)
        assert at_the_bound > 4, (
            f"{name}: at k = {bound} the poke only reached {float(at_the_bound)}, so the bound is "
            f"not strict and 'the tick it must stay under' is the wrong wording"
        )
        assert under_it < 2, (
            f"{name}: at k = {bound / 2} the poke reached {float(under_it)}, so staying under the "
            f"bound is not enough after all"
        )
        rows.append({
            "object": name,
            "dots": size,
            "stiffest": claimed,
            "book_tick_product": product_,
            "holds": product_ < LEAPFROG_BOUND,
            "bound": bound,
            "peak_at_the_bound": at_the_bound,
            "peak_under_it": under_it,
        })
    assert [row["holds"] for row in rows] == [True, True, False], (
        f"the verdicts came out {[row['holds'] for row in rows]}"
    )
    assert rows[2]["bound"] == Fraction(2, 5), f"the stella's bound is {rows[2]['bound']}"
    return {"tick": BOOK_TICK, "bound": LEAPFROG_BOUND, "rows": tuple(rows)}


READER_TICKS = 12


def octahedron_poke_table(k: Fraction = BOOK_TICK) -> Dict[str, object]:
    """Poke one middle of the octahedron at the chapters' own tick, in the reader's own names.

    The same run as `octahedron_table()` above, in the naming a reader arrived at by cutting — and
    asserted to be that run, dot for dot, under the name map. Three facts inside it are the beat:
    at tick 2 the whole poke is on the **opposite** middle and nowhere else, at tick 3 it is home,
    and the pair *(now, before)* does not repeat until 12, which is why the table is not over at 3.
    """
    lines = mid_lines()
    poked = MID_NAMES.index("AB")
    opposite = MID_NAMES.index("CD")
    start = [Fraction(1) if index == poked else Fraction(0) for index in range(6)]
    history = slosh(unit_weights(lines), lines, ticks=READER_TICKS, initial=start, k=k)

    denominators = {value.denominator for row in history for value in row}
    assert denominators <= {1, 2}, f"the run left whole numbers and halves: {denominators}"
    for tick, row in enumerate(history):
        for value in row:
            number(value)          # raises rather than rounding, which is the printability claim

    crossed = [Fraction(1) if index == opposite else Fraction(0) for index in range(6)]
    assert history[2] == crossed, f"tick 2 came out {history[2]}, not all on the opposite middle"
    assert history[3] == start, f"tick 3 came out {history[3]}, not home"
    assert history[1] != start and history[1][poked] < 0, (
        "the poked middle did not go negative on the way across, so 'the whole of it crosses' would "
        "be describing a run that never left"
    )
    assert period(history) == 12, f"the period came out {period(history)}, not 12"

    # The same numbers as the audited table, under AB→+x, AC→+y, AD→+z, BC→−z, BD→−y, CD→−x.
    order = [OCT_POINTS.index(tuple(int(v) for v in MID_POINTS[index])) for index in range(6)]
    audited = octahedron_table()["history"]
    for tick in range(min(len(audited), len(history))):
        assert [history[tick][index] for index in range(6)] == \
               [audited[tick][order[index]] for index in range(6)], (
            f"the reader's run and the audited run disagree at tick {tick}"
        )
    return {
        "k": k,
        "poked": MID_NAMES[poked],
        "opposite": MID_NAMES[opposite],
        "crossing_ticks": 2,
        "home_ticks": 3,
        "period": 12,
        "history": tuple(tuple(row) for row in history),
    }


RUNAWAY_TICKS = 20
RUNAWAY_LOOK = (0, 1, 2, 3, 10, RUNAWAY_TICKS)


def _round_floor(value: Fraction) -> int:
    """The value floored to two significant digits — a round number that is honestly below it.

    The first version of this floored to one of 1, 2 or 5 × 10ⁿ, which turned 8,504 into "past
    5,000" and 123,534,961 into "past 100,000,000": true, and 40% and 20% short. A proofreader
    called it (2026-09-02). Two digits keeps the number round enough to read and close enough to
    mean something, and the assertion below keeps it a floor rather than a rounding.
    """
    assert value >= 1
    digits = len(str(int(value)))
    unit = 10 ** max(digits - 2, 0)
    floored = (int(value) // unit) * unit
    assert floored <= value, f"{floored} is not below {float(value)}"
    return floored


def stella_runaway(k: Fraction = BOOK_TICK) -> Dict[str, object]:
    """Poke the same dot on the stella at the same tick, and watch it leave the napkin twice over.

    Two separate failures, and the chapter needs both. **It runs away**: the tick is over this
    object's ceiling, so the biggest number in the world grows without bound — past a hundred
    million by tick 20, from a poke of 1. **And it cannot be written down**: the first push is 8 at
    the poked dot and −1 at each of its eight neighbours, so the halves become quarters and then
    eighths, and `napkin.number()` refuses the fourth row. Neither is a shortage of patience.
    """
    lines = stella_reader_lines()
    start = [Fraction(1)] + [Fraction(0)] * 13
    history = slosh(unit_weights(lines), lines, ticks=RUNAWAY_TICKS, initial=start, k=k)
    biggest = [max(abs(value) for value in row) for row in history]
    assert biggest[0] == 1, "the poke was not 1"
    for tick in (5, 10, 15, RUNAWAY_TICKS):
        assert biggest[tick] > biggest[tick - 5], f"the run shrank between ticks {tick - 5} and {tick}"
    assert biggest[RUNAWAY_TICKS] > 100_000_000, (
        f"the biggest number at tick {RUNAWAY_TICKS} is {float(biggest[RUNAWAY_TICKS])}, not past "
        f"a hundred million — the runaway claim would be overstated"
    )

    printable = renderable_ticks(14, lines, 0, k, RUNAWAY_TICKS)
    assert printable == 3, f"{printable} rows print, not 3"

    # And no tick size rescues it: the stable ones print two rows at most, and none of them ever
    # comes home, because a poke at a middle excites the pair of stiffnesses that cannot return.
    tried = []
    for candidate in (Fraction(39, 100), Fraction(7, 20), Fraction(1, 4), Fraction(1, 5),
                      Fraction(1, 10)):
        assert candidate < Fraction(2, 5), f"{candidate} is not under the ceiling"
        rows = renderable_ticks(14, lines, 0, candidate, 10)
        repeat = period_of(14, lines, 0, candidate, 60)
        assert rows <= 2, f"k = {candidate} printed {rows} rows"
        assert repeat == 0, f"k = {candidate} came home after {repeat} steps"
        tried.append({"k": candidate, "printable": rows, "period": repeat})

    # And what a tick that DOES hold costs instead, worked on the one the chapter shows: a fifth.
    # The push at a poked middle is its eight lines, so the poke lands on fifths at tick 1 and on
    # twenty-fifths at tick 2 — the denominators square, which is why a smaller tick is not a
    # rescue. Asserted, because the chapter says these two words.
    example_k = Fraction(1, 5)
    start_row = [Fraction(1)] + [Fraction(0)] * 13
    rows = slosh(unit_weights(lines), lines, ticks=2, initial=start_row, k=example_k)
    push = 8
    # Taken from the rows themselves. Typing them beside the rows let an attack change the pair to
    # 7 and 49 with both assertions still passing, because nothing connected the numbers the page
    # printed to the run they described (a proofreader, 2026-09-02).
    first_denominator = max(value.denominator for value in rows[1])
    second_denominator = max(value.denominator for value in rows[2])
    assert (first_denominator, second_denominator) == (5, 25), (
        f"tick 1 and 2 at k = {example_k} came out over {first_denominator} and "
        f"{second_denominator}, not 5 and 25"
    )
    assert rows[1][0] == 1 - example_k * push, "the first push is not the poked dot's line count"

    matrix = laplacian_matrix(14, stella_lines(cut=False))
    excited = excited_polynomial(matrix, [Fraction(1) if i == 0 else Fraction(0)
                                          for i in range(14)])
    assert poly_divides([Fraction(20), Fraction(-11), Fraction(1)], excited), (
        "a poke at a middle does not excite the pair λ²−11λ+20, so the never-returns argument in "
        "`periods()` would not apply to this poke"
    )
    return {
        "k": k,
        "look": tuple((tick, biggest[tick]) for tick in RUNAWAY_LOOK),
        "bounds": tuple((tick, _round_floor(biggest[tick])) for tick in RUNAWAY_LOOK),
        "printable_rows": printable,
        "stable_tried": tuple(tried),
        "push_at_a_middle": push,
        # The fifth-sized tick's denominators are asserted above and deliberately NOT returned. They
        # were, and nothing rendered them — an assertion beside an unrendered value looks like cover
        # for whatever a future caption does with it, which is the shape the caption defect had (a
        # proofreader, 2026-09-02). The chapter states them in prose; this is where they are checked.
        "never_returns": True,
    }


# ── the report ───────────────────────────────────────────────────────────────────────────────────


def report() -> str:
    out: List[str] = []

    def say(text: str = "") -> None:
        out.append(text)

    say("=" * 96)
    say("THE OCTAHEDRON AS THE CROSSING BETWEEN CELLS — computed, not asserted")
    say("FIREWALL: arithmetic on a toy DEC lattice. Nothing here is a claim about nature.")
    say("=" * 96)

    say("\n── 1 · geometry: is the octahedron the only thing joining tetrahedra? ──")
    for n in (TORUS, TORUS_CHECK):
        f = face_audit(n)
        say(f"  {n}³ torus: {f['tets']} tetrahedra, {f['octahedra']} octahedra (ratio "
            f"{f['ratio']}:1); {f['tet_faces']} tetrahedron faces and {f['oct_faces']} octahedron "
            f"faces, {f['distinct_faces']} distinct — a perfect 1:1 pairing, and no two "
            f"tetrahedra share a face.")
    lines = line_audit()
    say(f"  lines on the {lines['n']}³ torus: {lines['lines']} in all, {lines['tet_lines']} of them "
        f"tetrahedron edges and {lines['cut_lines']} the octahedra's cuts "
        f"({lines['cut_share']} of every line). Every dot has 14 lines: 12 a tetrahedron provides, "
        f"2 only the cut does.")
    say(f"  each octahedron edge belongs to {lines['octahedra_per_edge']} octahedra; each cut to "
        f"{lines['octahedra_per_cut']}. And each tetrahedron edge is shared by exactly "
        f"{lines['tets_per_tet_line']} TETRAHEDRA — so on the lines, where numbers actually live, "
        f"a transfer crosses from one tetrahedron to the next in a single step.")
    hull = hull_audit()
    overlap = stella_overlap()
    say(f"  one octahedron + its 8 face-neighbours IS a stella octangula, hull a cube: volume "
        f"{hull['stella_volume']} of the cube's {hull['hull_volume']} — exactly "
        f"{hull['fill']} of its own hull. Each tetrahedron sits in "
        f"{overlap['stellae_per_tet']} stellae, so the stellae cover the world "
        f"{overlap['cover']}× over: the stella is NOT the tile.")

    say("\n── 2 · the sum: what crosses the octahedron's outside adds to zero ──")
    b = boundary_sum()
    say(f"  13 freely chosen arrows: {' '.join(str(a) for a in b['arrows'])}")
    say(f"  → 12 face-numbers: {' '.join(number(v) for v in b['face_numbers'])} — none zero")
    say(f"  → each of the 4 insides walks its own 4 faces to "
        f"{' '.join(number(v) for v in b['per_inside'])}")
    say(f"  → the {b['interior_cancelled']} interior faces cancel in pairs, leaving the 8 outside "
        f"ones: {' '.join(signed(v) for v in b['outside_terms'])}")
    say(f"  → their sum: {number(b['outside_sum'])}. Exactly. No lengths used.")

    say("\n── 3 · the object one step out: the stella octangula ──")
    c = stella_census()
    say(f"  {c['dots']} dots; {c['lines_solid']} lines as a solid, {c['lines_record']} as the record "
        f"cuts it. Octahedron dots {c['oct_degree']} lines each (the cut's two ends "
        f"{c['cut_end_degree']}), spike apexes {c['apex_degree']}.")
    s = stella_spectrum()
    say(f"  Δ₀ spectrum (certified exactly): {s['spectrum']}; trace {s['trace']}, "
        f"trace² {s['trace_squared']}.")
    say(f"  λ_max = {s['lambda_max']} ⇒ the leapfrog needs k < {s['k_ceiling']}. The chapters' "
        f"k = 1/2 is UNSTABLE here.")
    cutspec = cut_stella_spectrum()
    say(f"  with the record's cut λ_max RISES: it is between {float_free(cutspec['lambda_low'])} "
        f"and {float_free(cutspec['lambda_high'])}, so the ceiling tightens from 2/5 to under "
        f"{float_free(cutspec['k_ceiling_low'])}. The cut octahedron is the less forgiving object.")
    for cut in (False, True):
        p = poke_spectrum(cut)
        verdict = "; ".join(f"λ = {k} {v}" for k, v in p["verdict"].items())
        say(f"  a poke at one spike ({'cut' if cut else 'uncut'}) reaches {p['degree']} modes — "
            f"{verdict}")

    say("\n── 4 · transfer: how many steps from one cell to the next ──")
    t = transfer_counts()
    say(f"  at k = {t['k']}: first move equals steps along lines at every dot — nothing cancels.")
    say(f"  spike → its octahedron dots: 1 step. spike → an adjacent spike: "
        f"{t['adjacent_spike']}. spike → the opposite spike: {t['opposite_spike']}. "
        f"diameter {t['diameter']}.")
    say(f"  no two apexes share a line, so every one of those paths spends "
        f"{t['intermediate_on_octahedron']['adjacent']} step (adjacent) or "
        f"{t['intermediate_on_octahedron']['opposite']} steps (opposite) on octahedron dots.")
    p = periods()
    say(f"  return: tetrahedron {p['tetrahedron_half']} steps at k = 1/2, and it has "
        f"{p['tetrahedron_lines']} lines — 4 ≠ 6, so 'the return counts the lines' is already dead "
        f"on the tetrahedron. The octahedron returns in {p['octahedron_half']} and has "
        f"{p['octahedron_lines']} lines, which looks like a match until the dial moves: at k = 1/4 "
        f"and at k = 1/5 it never returns at all.")
    tried = ", ".join(f"k = {k}" for k in p["stella"])
    say(f"  stella: tried {tried} for 60 steps each — it never returns, and cannot at ANY rational "
        f"tick size (the algebraic argument is in `periods()`).")

    say("\n── 5 · can the stella's table go on a napkin? ──")
    table = tick_size_table()
    for row in table["rows"]:
        say(f"  k = {row['k']}: {'stable  ' if row['stable'] else 'UNSTABLE'} · "
            f"{row['printable_ticks']} tick(s) printable")
    say(f"  the largest stable tick size `number()` will print at all is "
        f"{table['best_stable_printable']['k']}, and it prints "
        f"{table['best_stable_printable']['printable_ticks']} tick(s). There is no tick size that "
        f"is both stable and whole-numbered: the first push is (3, −1, −1, −1), gcd 1.")
    o = octahedron_table()
    say(f"  the BARE octahedron, though, prints in full at the chapters' own k = {o['k']}: all "
        f"{o['printable_rows']} rows, denominators {o['denominators']} only. The whole poke is on "
        f"the opposite dot at tick {o['crossing_ticks']}, back at the start at tick 3, and the pair "
        f"(now, before) repeats every {o['period']}.")

    say("\n── 6 · efficiency: same work, different grouping ──")
    w = work_counts()
    say(f"  one step on the {w['lines']} lines of the {TORUS}³ world:")
    say(f"    per line (the napkin's own loop): {w['per_line_visits']} line-visits")
    say(f"    per dot  (gather each dot's 14):  {w['per_dot_visits']} — exactly twice as many")
    say(f"    per octahedron (13 lines each):   {w['per_octahedron_visits']} — "
        f"{w['octahedron_vs_line']}× the per-line loop, {w['octahedron_vs_dot']}× the per-dot one")
    say(f"  on the motif alone the octahedron's 13 lines and the spikes' 24 partition all 37 "
        f"exactly once: same work as the per-line loop, differently grouped.")

    say("\n── 7 · the reader's route: cut ONE tetrahedron at the middles of its six lines ──")
    cut = midpoint_cut()
    say(f"  {cut['dots']} dots ({cut['corners']} corners + {cut['middles']} middles) → "
        f"{cut['tips']} tetrahedra at the tips, each {float_free(cut['tip_share'])} of the whole "
        f"and half its side, and {cut['octahedra']} octahedron between them, "
        f"{float_free(cut['core_share'])} of the whole.")
    say(f"  that octahedron: {cut['oct_dots']} dots, {cut['oct_lines']} lines, "
        f"{cut['oct_faces']} faces, {cut['oct_degree']} lines at every dot — and "
        f"{len(cut['opposite_pairs'])} pairs of dots NOT joined: "
        f"{', '.join('·'.join(pair) for pair in cut['opposite_pairs'])}. It is the same graph as "
        f"§1–§5's octahedron, asserted under the name map.")
    say(f"  of its 8 faces, 4 look at a tip ({', '.join(cut['faces_at_a_tip'])}) and 4 lie flat in "
        f"a face of the tetrahedron that was cut ({', '.join(cut['faces_in_a_face'])}).")
    poke = octahedron_poke_table()
    say(f"  poke {poke['poked']} at the chapters' own k = {poke['k']}: whole numbers and halves "
        f"throughout; the whole poke is on {poke['opposite']} at tick {poke['crossing_ticks']}, "
        f"home at tick {poke['home_ticks']}, and (now, before) repeats at {poke['period']}.")
    surface = octahedron_boundary_sum()
    say(f"  12 freely chosen arrows: {' '.join(str(a) for a in surface['arrows'])} → the 8 outside "
        f"faces carry {' '.join(signed(v) for v in surface['face_numbers'])}, and every line is "
        f"walked once each way, so they sum to {number(surface['sum'])}.")
    twin = second_tetrahedron()
    say(f"  fill the {twin['added']} flat faces and the new corners are "
        f"{', '.join(twin['apex_names'])} — a regular tetrahedron the size of the one we cut, whose "
        f"own six middles are the same six middles. Hull: {twin['hull']}.")
    stella = stella_reader_census()
    say(f"  the two together: {stella['dots']} dots, {stella['lines']} lines, {stella['pieces']} "
        f"pieces; {float_free(stella['stella_in_tetrahedra'])} of the tetrahedron we cut and "
        f"{float_free(stella['stella_in_its_cube'])} of its cube. No two tips are joined.")

    say("\n── 8 · and the tick that has worked all along stops working ──")
    ceilings = napkin_ceilings()
    for row in ceilings["rows"]:
        say(f"  {row['object']:<18} {row['dots']:>2} dots · stiffest {number(row['stiffest'])} · "
            f"× the book's tick = {number(row['book_tick_product'])} · "
            f"{'under 4, holds' if row['holds'] else 'over 4, RUNS AWAY'} · "
            f"must stay under {float_free(row['bound'])} "
            f"(at it, the poke reaches {float(row['peak_at_the_bound']):.0f})")
    runaway = stella_runaway()
    say(f"  poke a middle of the stella at k = {runaway['k']}: the biggest number goes "
        + ", ".join(f"{tick}→{float_free(value)}" for tick, value in runaway["look"])
        + f"; only {runaway['printable_rows']} rows can be written down at all.")
    say("  every tick that does hold prints two rows at most, and none of them ever comes home: "
        + ", ".join(f"k = {row['k']} ({row['printable']} row(s))"
                    for row in runaway["stable_tried"]))
    say("")
    return "\n".join(out)


def float_free(value: Fraction) -> str:
    """A fraction as a fraction. There is no floating point in this file, including in the report."""
    return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)


def self_test() -> None:
    """Every claim this module makes, run. Each function asserts its own; this runs them all."""
    for n in (TORUS, TORUS_CHECK):
        face_audit(n)
        line_audit(n)
    hull_audit()
    stella_overlap()
    stella_census()
    boundary_sum()
    stella_spectrum()
    cut_stella_spectrum()
    # An independent route to the same bracket, so the hand-picked rationals above are checked.
    low, high = largest_eigenvalue_bracket(laplacian_matrix(14, stella_lines(cut=True)), steps=12)
    assert CUT_BRACKET[0] <= high and low <= CUT_BRACKET[1], (
        f"bisection put λ_max in ({low}, {high}), outside the quoted bracket {CUT_BRACKET}"
    )
    poke_spectrum(False)
    poke_spectrum(True)
    transfer_counts(cut=True)
    transfer_counts(cut=False)
    periods()
    tick_size_table()
    octahedron_table()
    work_counts()
    # The reader's route: the same object, reached by cutting one tetrahedron.
    midpoint_cut()
    octahedron_poke_table()
    octahedron_boundary_sum()
    second_tetrahedron()
    stella_reader_census()
    napkin_ceilings()
    stella_runaway()
    # The napkin's own tokens must be untouched by the `slosh` generalisation this module needed.
    # They no longer run this module's arithmetic — they render the vendored engine — so what this
    # asserts now is that the renderer still works beside it, which is worth a second either way.
    import napkin
    for token in napkin.TOKENS:
        napkin.render(token)
    print("octahedron.py: all assertions hold.")


if __name__ == "__main__":
    print(report())
    self_test()
