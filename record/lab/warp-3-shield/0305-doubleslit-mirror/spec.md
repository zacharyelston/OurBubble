# 0305 — warp-3.5: the double-slit demo's mirror asymmetry — cause and two exact repairs

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf3_5_doubleslit_mirror_gate.rs` ·
**Status:** CONFIRMED (P0–P3; run `490f006`, see `eval.md`) · **Issues:** #252, #250 (under #137's discipline)

## Goal (one paragraph)

The public double-slit demo (viz/doubleslit.html, the committed `gen_doubleslit` snapshot) shows a
y-asymmetric "two-slit" pattern (#252: slit-lobe ratio ~3.4×) on a provably y-symmetric scene. The
diagnosed cause is `mesh_2d_triangle_grid`'s uniform cell diagonal — a vertex stencil invariant
under 180° rotation but not under y → −y — the documented `⋆=I` / #23 anisotropy family, showing up
in a public-facing page. This rung measures the asymmetry as a registered observable at the demo's
exact parameters and tests two repairs against it: (i) the alternating-diagonal
(`mesh_2d_triangle_grid_crossed`) mesh, whose y-mirror is an exact mesh automorphism for even H;
(ii) the geometric 2-D cotan ⋆ (the #23 fix), under which every diagonal edge has weight exactly 0
(both opposite angles are 90°) and the interior operator collapses to the y-symmetric 5-point
stencil. It also measures the lattice fringe spacing against the page's continuum formula
Δy = λL/d (#250) so the page's caveat carries a number rather than a disclaimer.

## Firewall (R3)

Toy DEC scalar wave `φ̈ = −c²Δ₀φ`, `Δ₀ = ⋆₀⁻¹D₀ᵀ⋆₁D₀`, on a 200×140 2-D triangle lattice with
Dirichlet walls, sponge damping, and a pinned two-column plane-wave drive — the demo's exact scene
(`solve::scene::ScalarScene`). *Slit, screen, fringe, intensity* name lattice features and derived
observables, never claims about nature. This is not a Maxwell/EM simulation; no claim about
physical double-slit experiments is made. The continuum formula Δy = λL/d appears ONLY as the
textbook comparison the page currently displays; the lattice is under no obligation to match it,
and the measured mismatch is a statement about the demo's regime, not about optics. c = 1
throughout (demo units).

## Predictions (registered before the run; every threshold probe-informed —
`core/uniforge/examples/doubleslit_mirror_probe.rs`, probe commit on this branch)

Metrics (all deterministic; no RNG anywhere in the pipeline):
`asym(f) = Σ_y|f(y) − f(H−y)| / Σ_y|f(y)|` over the sponge-free band y ∈ [12, 128], evaluated on
the final-frame field column at x ∈ {32, 66, 120, 188} and on the time-mean screen intensity;
the slit-lobe ratio `max|φ|` in ±8 windows about the two slit centers (y = 38, 102) at x = 66;
the wavefront arrival frame at the screen column (threshold as stated per arm); fringe centers =
clustered local maxima of the screen intensity (gap ≤ 4 merges), and their mean spacing.

- **P0 (control — the committed demo reproduces):** arm A (`mesh_2d_triangle_grid`, ⋆=I, 340
  frames, threshold 0.01) has front-arrival frame **exactly 231** (matches the committed
  snapshot), slit-lobe ratio ∈ **[3.0, 4.5]** (probed 3.758; #252's 3.4× at its own frame/metric),
  and screen-intensity asym > **0.5** (probed 1.372). *If P0 fails the run is inconclusive.*
- **P1 (the drop-in repair):** arm C (`mesh_2d_triangle_grid_crossed`, ⋆=I, same params) has
  final-frame asym < **1e-12** at ALL four stations and intensity asym < **1e-12** (probed
  ≤ 5.2e-15 / 4.4e-16 — machine); front-arrival frame ∈ **[200, 260]** (probed 228: the demo's
  timing survives); max screen intensity > 0; and the fringe centers pair under y → 140−y to
  within **1 cell** (probed exactly: 32↔108, 53↔87, 70 fixed).
- **P2 (the #23 fix, scoped):** arm B (uniform-diagonal mesh, geometric 2-D ⋆, 800 frames,
  threshold 0.002) has final-frame asym < **1e-5** at all stations — 5+ orders below arm A but
  registered ABOVE machine, because the open mesh's boundary ⋆₀ is itself mirror-asymmetric
  (probed corner defect 1.667e-1; measured field asym up to 1.4e-7). Arm D (crossed mesh +
  geometric ⋆) has ⋆₀ mirror-defect **exactly 0** and asym < **1e-12** (probed ≤ 4.3e-15). Scope:
  these bounds are for the OPEN 200×140 mesh at the demo parameters; the geometric-⋆ statement
  is about this mesh family, not all meshes.
- **P3 (the #250 number):** on the repaired arm C, the measured mean fringe spacing ∈ **[17, 22]**
  (probed 19.0) and differs from the page's continuum Δy = λL/d = 27.125 by **> 20%** relative
  (probed 30%). Pre-registered direction: the lattice spacing is SMALLER than the formula's. The
  demo geometry's Fresnel parameter d²/(λL) = 64²/(14·124) = 2.36 > 1 (near field) — the far-field
  formula is out of its validity regime at these parameters independent of any lattice effect;
  the gate asserts this arithmetic as documentation.

## Method (sketch)

`geom::mesh_2d_triangle_grid` / `geom::mesh_2d_triangle_grid_crossed` (new builder, unit-tested
mirror automorphism) × {⋆=I via `MeshWaveSolver::new`, geometric 2-D cotan ⋆ via
`MeshWaveSolver::with_geometric_hodge`}; the scene is `solve::scene::ScalarScene` built with the
demo's exact wall/slit/damping/source constructors (copied verbatim from `gen_doubleslit`). The
gate runs all four arms (~2 s total), prints a scorecard, writes `data/arms.csv` (per-arm metrics)
and `data/screen_intensity.csv` (per-arm profiles), and asserts P0–P3.

## What would falsify this

P1: any station of the crossed-mesh arm showing asym above 1e-12 (the automorphism argument would
be wrong or the builder broken), or the front arriving outside [200, 260] (the repair would not be
drop-in). P2: arm B failing to beat 1e-5 (the diagonal-weight-zero collapse would not hold), or
arm D failing 1e-12 (the ⋆₀-defect mechanism would be wrong). P3: the measured spacing landing
within 20% of 27.125 (the page's formula would be fine as displayed and #250 overstated).
