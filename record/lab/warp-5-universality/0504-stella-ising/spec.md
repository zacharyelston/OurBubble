# 0504 — Warp-5.4: Ising on the stella lattice — universality tested on our own geometry

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_4_stella_ising_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

Chapters 4–5 ran on chains and cubic grids. This rung brings the method home: Ising spins on the vertices of
the **engine's own stella complex** (`mesh_3d_chiral_tetoct_yz_periodic` — FCC vertices, face-diagonal bonds
from the stella tets, one long-diagonal bond per octahedral hole; adjacency read straight from the mesh's
`d0_sparse`). Universality's claim is that the lattice doesn't matter: the exponent ratios must match the
3-D Ising class even though this graph (bulk coordination 14, mixed boundary) appears in no textbook. Its
`T_c` is a new number — nobody has tabulated this lattice — while `U*` should *differ* from the fully-periodic
cubic value, because amplitudes are boundary-condition-dependent and exponents are not. Both halves of that
statement are registered.

## Firewall (R3)

`Ising, stella, T_c, exponent` name a seeded Wolff simulation with spins on the **toy** engine mesh's
vertices and bonds on its edges. Universality-class membership shared with real Ising-class materials — not
a claim the engine is a magnet, no spacetime claim. The class values (1.963, 0.518) and the cubic run (5.3)
are post-hoc checks; `T_c`, `U*`, and the ratios are outputs.

## Predictions (registered before the run)

- **P0 (the graph is the engine's):** adjacency extracted from `d0_sparse` of the yz-periodic stella mesh;
  active vertices = the FCC sublattice (`(n+1)·n²/2`), most-common bulk coordination = **14**, graph
  connected — *gate:* all three checked for `n = 16`.
- **P1 (locate the stella `T_c` — a new number):** adjacent-`L` Binder crossings exist, spread `< 0.15`, and
  locate `T_c ∈ [11.3, 12.0]` (probe: ≈ 11.64; sanity: FCC's 9.79 scaled by coordination 14/12 ≈ 11.4) —
  *gate:* as stated.
- **P2 (amplitude is BC-dependent, and stable):** the crossing value `U* ∈ [0.24, 0.38]`, consistent across
  sizes (max−min `< 0.06`), and **below** the fully-periodic cubic 0.484 by more than 0.05 — amplitudes
  depend on boundary geometry; this one should not match 5.3's — *gate:* as stated.
- **P3 (the exponents don't care about the lattice):** FSS at the located `T_c` over `n ∈ {8,12,16,24}`
  gives `γ/ν` within **6%** of 1.963 and `β/ν` within **8%** of 0.518, and each within **10%** of the cubic
  values measured in 5.3 (2.027, 0.486) — same class, different lattice — *gate:* as stated.

## Method (sketch)

`mesh_3d_chiral_tetoct_yz_periodic(n,n,n, engine_operator::oct_axis)`; neighbor lists from `d0_sparse`
(head/tail per edge row), compacted to degree>0 vertices. Seeded Wolff (`splitmix64`, incremental
magnetization), `n ∈ {8,12,16,24}`, `T ∈ [11.30, 11.70]` step 0.05 (9 points), warmup 4000 + 60000 measured
clusters, seed `42 + 17n + tᵢ`. `T_c` = mean of adjacent-`L` Binder crossings; per-`L` quadratic fits give
`U*`, `ln χ`, `ln⟨|m|⟩` at `T_c`; ratios via `kinematics::power_law_fit` over all four sizes. Emit
`data/stella_graph.csv`, `data/binder_stella.csv`, `data/results.csv`.

## What would falsify this

If the ratios missed the class windows (P3), the stella lattice would *not* be in the 3-D Ising class —
universality would fail on our own geometry, which would be a major (and suspicious) result pointing first
at the adjacency extraction. If `U*` matched the periodic-cubic 0.484 (P2), the amplitude/exponent
distinction would be wrong. If no crossing existed (P1), the lattice wouldn't order like a 3-D system at all.
