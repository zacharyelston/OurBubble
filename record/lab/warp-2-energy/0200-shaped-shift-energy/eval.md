# 0200 — Warp-2.0: the shaped shift's energy structure — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf2_energy_structure_gate` (green: yes) · **Commit:** see [`PROVENANCE.md`](PROVENANCE.md)

## Result

A shaped shift `N = vs·f(r)·ẑ` — a purely geometric deformation of the lattice — read through the
purely-geometric functional `16πρ = (trK)² − K_ijK^ij`, reproduces the **known Alcubierre energy
structure** on the discrete lattice, with **nothing added by hand**: the energy is negative (exotic),
localized on the bubble wall, and toroidal. A *bare translation* (uniform shift) costs exactly zero — the
exotic price is paid for **shaping**, not for moving. Matches the hand-derived `16πρ = −½·vs²·f'(r)²·sin²θ`.

| quantity | expected (P) | measured | pass |
|---|---|---|---|
| P0 uniform-shift `max\|16πρ\|` | `< 1e-9` (moving is free) | **0.0** (exact) | ✅ |
| P1 negative fraction (significant cells) | `≥ 0.98` | **1.0000** (100%) | ✅ |
| P1 minimum `16πρ` | `< −1e-3` | **−0.0188** | ✅ |
| P2 wall / interior mean\|16πρ\| | `≥ 10×` | **336×** | ✅ |
| P2 wall / exterior mean\|16πρ\| | `≥ 10×` | **1360×** | ✅ |
| P3 equator / pole mean\|16πρ\| | `≥ 5×` | **6.1×** | ✅ |

The `|cosθ|` profile falls **monotonically** from equator (`6.0e-3`) to pole (`7.7e-4`) — the `sin²θ`
torus, sampled in 9 angular bins. Data: [`data/energy_by_band.csv`](data/energy_by_band.csv),
[`data/energy_by_angle.csv`](data/energy_by_angle.csv). Figure: `core/viz gen_energy` →
[`figures/energy_structure.html`](figures/energy_structure.html).

## What it rules in / out

- **Rules in the genesis tenet, for warp.** The three defining features of warp-drive energy are not put
  in by hand anywhere — they *fall out* of the geometry of the deformation through a quadratic invariant.
  "Only geometry" survives contact with the core warp claim, not just the wave/light-cone side.
- **Rules out "the energy is a boundary/discretization artifact."** The uniform-shift control costs
  *exactly* zero (P0), so the functional does not charge for translation or for lattice edges — it charges
  only for the shaped wall. The negativity is a real property of the shift's **shear geometry**
  (`trK² < K_ijK^ij` on the wall), not a sign convention.
- **Honest caveat (the crux that remains):** the toroidal ratio (6.1×) is the *weakest* margin, because the
  discrete `sin²θ` has a nonzero residual at the poles (the wall shell is a few cells thick, and the axial
  `∂_zN_z` term never fully vanishes on-axis). Analytically it should be ∞; on the lattice it is finite.
  This is expected discretization, not a defect — but it is where a finer wall would sharpen the torus.
- This energy is computed with **central differences** (`kinematics::eulerian`), i.e. the *kinematic*
  geometry of the shift, not yet the engine's geometric `⋆` (`dec::hodge`). Recomputing through `⋆` (menu
  item) would unify this with the wave-side tenet — the natural next rung.

## Deferred / next

Feeds the chapter menu: **`⋆`-computed energy** (does the torus survive on the engine's Hodge geometry?),
**wall-thickness sweep** (thin wall ⇒ larger `f'` ⇒ more exotic cost — the classic scaling), and
**energy vs `vs`** (confirm the `vs²` prefactor on the lattice). Book chapter 02 authored from this figure.
