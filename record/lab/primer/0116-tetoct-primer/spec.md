# 0116 — Primer-1: the TetOct stella complex — census + data-true render

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/primer_tetoct_census_gate.rs` · **Status:** registered (pre-run)

## Goal (one paragraph)

The primer chapter's reference picture: register the structural census of the chiral tet-oct
stella complex at n=4 — `mesh_3d_chiral_tetoct(4,4,4, chiral_oct_screw111)` — and export the
exact complex so the interactive 3D render in [`figures/`](figures) is data-true (R10): every
vertex, edge, and tet on screen is the engine's output, with the construction scaffold (the unit
cubes whose even-sum corners host the stella tets) available as an overlay. Origin: the uniforge
MCP handshake demo (this entry's render was first built as an exploratory probe in an MCP
session; the numbers below were observed there and are registered here for the run-for-record).

## Firewall (R3)

*Matter/antimatter* name the parity 2-colouring of the stella tet families — which of the two
regular-tetra orientations a unit cube contributes, decided by its origin parity `(i+j+k) mod 2`.
*Chirality* names the absence of an orientation-reversing isometry under the `screw111` octahedron
split (audited in `tests/lattice_audit.rs`, not claimed here). Toy DEC computation; no claim about
nature; c=G=1.

## Predictions (registered before the run)

- **P0 (sanity):** `d²=0` holds exactly (integer identity over all D1·D0 rows); the dense vertex
  layout is (n+1)³ = 125 with exactly the even-sum points active — 63 vertices carry all cells,
  odd-sum points stay degree-0 (they are octahedral-hole centres) — *gate:* exact `assert_eq!`s.
- **P1 (census):** 254 edges (240 of length² 2, **14 long diagonals** of length² 4), 312 faces,
  120 tets splitting **32 matter + 32 antimatter + 56 oct**, with the classification derived from
  geometry alone (all-edges²=2 ⇒ stella, family by cube min-corner parity; edge²=4 ⇒ oct) — *gate:*
  exact counts, and a `panic!` if any tet fits neither pattern.
- **P2 (chirality wiring):** the 56 oct tets fan out over exactly 14 odd-sum interior holes,
  **every long diagonal shared by exactly 4 tets**, and the `screw111` axis census over those holes
  is **(2, 6, 6)** for axes (x, y, z) — i.e. (8, 24, 24) tets — *gate:* exact `assert_eq!`s.

## Method (sketch)

The gate builds the mesh through the `uniforge` facade (`geom` L0 underneath), asserts P0–P2, and
on green writes [`data/lattice.json`](data) directly (R10, path anchored to `CARGO_MANIFEST_DIR`):
`verts` (dense coords + activity), `edges` (+length²), `tets` (+kind/axis), and `cubes` (the 64
construction cubes + parity — scaffold geometry, explicitly not part of the complex).
[`figures/inject.py`](figures/inject.py) embeds that file verbatim into the self-contained canvas
viewer [`figures/tetoct-render.template.html`](figures/tetoct-render.template.html); colour,
shading, explode, and the cube-scaffold overlay are labels, never geometry edits.

## What would falsify this

Any census mismatch (P0/P1); a tet whose edge pattern is neither stella nor oct; a long diagonal
shared by ≠4 oct tets; an axis census other than (2,6,6) under `screw111` — any of these would mean
the builder or the registered reading of it is wrong, and the entry records that as a NEGATIVE (R5).
