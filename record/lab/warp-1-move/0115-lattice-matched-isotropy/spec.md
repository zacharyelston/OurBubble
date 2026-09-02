# 0115 — Warp-1.5: the lattice-matched bubble (isotropy of motion)

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf1_5_lattice_matched_gate.rs` · **Status:** registered (mirrors the original lab/0115 registration)

## Goal (one paragraph)

"Matching the lattice would do what?" In this engine, matching the lattice **is** the geometric Hodge
star (the metric-carrying ⋆); the trivial `⋆=I` gives an anisotropic light cone (the #23 defect). Evolve
a scalar pulse from the centre and measure its propagation speed along a lattice axis `[100]` vs a body
diagonal `[111]` (time-of-peak at equal-distance probes, `v = dist / t_peak`), under `⋆=I`
(`MeshWaveSolver::new`) vs the geometric Hodge (`with_geometric_hodge`). The anisotropy
`|v_axis/v_diag − 1|` is the figure of merit — it decides whether *steering* (Warp-1.2) is
direction-true or points untrue.

## Firewall (R3)

Internal lattice numerics — a toy DEC scalar pulse on a tetrahedral mesh. *light cone / isotropy /
lattice-matched* name solver behaviour, never a real EM/gravity measurement or a real warp bubble. c=1.

## Predictions (registered before the run)

- **P0 (sanity):** `⋆=I` is *clearly anisotropic* — `|v_axis/v_diag − 1| > 5%`. If not, the probe is
  under-resolved and the run is inconclusive.
- **P1:** the geometric Hodge **markedly reduces** the anisotropy — `aniso_geom < ½·aniso_trivial`
  *and* `aniso_geom < aniso_trivial − 0.03` (isotropy restored by lattice-matching).

## Method (sketch)

`nb = 24` tetrahedral grid; centred Gaussian pulse (σ=2); `step_scalar_wave`, `dt = 0.04`, ~350 steps.
Axis probes at offset 8, diagonal probes at offset 5 (`5√3 ≈ 8.66 ≈ 8`); speed = distance / mean
time-of-peak. Engine via the `uniforge` facade (`mesh_3d_tetrahedral_grid`, `MeshWaveSolver`); lattice
index via `kinematics::Grid`.

## What would falsify this

If the geometric Hodge left the anisotropy roughly where `⋆=I` put it (no ≥2× reduction), lattice-matching
would *not* buy isotropic motion — steering would be intrinsically direction-biased and the P1 claim false.
