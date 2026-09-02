# 0300 — Warp-3.0: the shield, the imbalance, and inertia

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf3_shield_imbalance_gate.rs` · **Status:** CONFIRMED — see [`eval.md`](eval.md)

## Goal (one paragraph)

Test the hypothesis: *a shield decouples a region from its environment (an information imbalance) — does
that reduce the region's inertia (a start on gravity manipulation)?* We split it into the provable half and
the honest null. **Part A** measures the **information imbalance** rigorously: a shield barrier suppresses
the interior↔exterior linear response (the screened-Poisson Green's function) — the inside "sees less" of
the outside. **Part B** asks whether that imbalance changes **inertia**: in standard field theory a barrier
is a *potential / effective-mass* term, not a change to the inertial (`φ̈`) coefficient, so the prediction
is a **null** for the interior — and, if anything, the barrier is a *positive* mass² term (more inertia at
the wall, not less). The null names exactly the extra ingredient "gravity manipulation" would require.

## Firewall (R3)

*shield, information, inertia, gravity* name a prescribed barrier potential and the linear response of a
probe scalar field on a **toy** lattice (`compute_laplacian_0form`, `step_scalar_wave`). **Real EM does not
screen gravity**; the entropic-inertia idea (Mach / Verlinde / MiHsC) is **contested prior physics**,
computed here only as a fenced hypothesis-*consequence*, never a derivation. c = 1.

## Predictions (registered before the run)

- **P0 (the shield acts locally — control):** coupling between the exterior source and a *nearby exterior*
  probe (a path that does **not** cross the shell) is ≈ unchanged by the shield — *gate:*
  `G_shielded/G_open ∈ [0.7, 1.4]` for the exterior control pair.
- **P1 (the information imbalance — provable):** coupling from the exterior source to the *interior* (bubble
  centre) is strongly suppressed by the shield — *gate:* `G_shielded(centre)/G_open(centre) < 0.3`. Local ≠
  external: the inside sees less of the outside.
- **P2 (inertia is unchanged inside — the honest null):** an interior excitation's dynamics are identical
  with the shield on vs off (the barrier is zero in the interior, so the interior evolution operator is
  literally unchanged) — *gate:* an interior wave packet's ballistic displacement over `T` steps is
  **bit-for-bit identical** shielded vs open (`< 1e-12`). Shielding does not reduce interior inertia.
- **P3 (the barrier is a mass² term, not an inertia reducer):** the shield contributes a **positive**
  effective mass² `m²_eff(x) = V(x) ≥ 0`, localized on the wall, with `m²_eff(interior) ≈ 0` (unchanged) —
  *gate:* `V(centre) < 1e-6` and `V(wall) > 0`. If anything the wall is *more* inert, opposite to "less
  inertia inside."

## Method (sketch)

`mesh_3d_tetrahedral_grid(N=24)`, centre `c0=12`. Spherical shell shield `V(r) = V0·exp(−((r−R)/w)²)`,
`R=8, w=1.2, V0=40`. **Part A:** solve the screened Poisson `(Δ + κ₀² + V)φ = δ_{x_ext}` (Richardson
iteration; `Δ = compute_laplacian_0form`, the positive `d†d`; `κ₀²=0.05` regularizer) for a unit source
just outside the shell; read `φ` at the centre (interior), at a nearby-exterior control point, both for
`V` on and off; ratios are the couplings. **Part B:** evolve an interior Gaussian packet with initial
velocity via `step_scalar_wave` for `T` steps, shield on vs off, compare the packet's displacement/energy;
read `V` at centre vs wall. Emit `data/shield.csv` (couplings) + `data/inertia.csv` (packet + mass² terms).

## What would falsify this

If interior coupling were *not* suppressed (P1), there is no imbalance. If the interior packet moved
*differently* with the shield (P2), inertia would change under standard shielding — but it cannot, because
`V ≡ 0` inside, so a non-null there would signal a bug. If the barrier gave a *negative* `m²_eff` (P3),
it would reduce inertia directly — it does not.
