# 0200 — Warp-2.0: the shaped shift's energy structure (the tenet, tested on warp)

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf2_energy_structure_gate.rs` · **Status:** CONFIRMED — see [`eval.md`](eval.md)

## Goal (one paragraph)

Test the [genesis tenet](../../../GENESIS.md) — *only geometry, nothing added by hand* — on the core warp
claim. Build a shaped shift `N = vs·f(r)·ẑ` on the lattice (a purely geometric deformation), read its
energy off the purely-geometric extrinsic-curvature functional `16πρ = (trK)² − K_ijK^ij`, and check
whether the discrete lattice reproduces the **independently known** Alcubierre energy structure with
nothing tuned by hand. If it does, the tenet holds for warp; if the sign leaks or the torus smears, we
have found the boundary of "only geometry" — a first-class negative (R5).

## Firewall (R3)

*Shift, energy, warp bubble, exotic* name structures of a **toy** lattice: `N` is a prescribed vector
field; `16πρ` is the quadratic invariant of its gradients (the ADM/extrinsic-curvature energy of a chosen
shift). No spacetime, no measurement, no device. c = G = 1; unit lattice spacing.

## Predictions (registered before the run)

**Prior physics (Alcubierre):** `ρ ≤ 0`, localized on the wall (∝ `f'²`), toroidal (∝ `sin²θ`).
**Our hand-derivation:** feeding `N = vs·f(r)·ẑ` through the functional gives
`16πρ = −½·vs²·f'(r)²·sin²θ`. The gate checks the discrete lattice against this:

- **P0 (control — moving is free):** a *uniform* shift `N = (0,0,vs)` (no wall, `f ≡ 1`) costs **zero**
  energy everywhere — *gate:* `max|16πρ_uniform| < 1e-9`. (The exotic price is paid for *shaping*, not for
  translating.)
- **P1 (exotic / negative — the warp signature):** the shaped shift's energy is **negative** wherever it
  is significant — *gate:* over cells with `|16πρ| > 1e-3·peak`, the negative fraction `≥ 0.98` **and** the
  minimum `< −1e-3` (with `vs=1`).
- **P2 (wall-localized):** energy concentrates in the wall shell `|r−R| < 2w`, not the flat interior
  (`r < R−2w`) or far exterior (`r > R+2w`) — *gate:* `mean|16πρ|_wall ≥ 10 ×` each of
  `mean|16πρ|_interior` and `mean|16πρ|_exterior`.
- **P3 (toroidal):** within the wall shell the energy peaks at the **equator** (plane ⟂ travel, `|cosθ|`
  small) and vanishes toward the **poles** (on the travel axis `z`) — *gate:*
  `mean|16πρ|_equator ≥ 5 × mean|16πρ|_pole`, where equator = `|cosθ|<0.3`, pole = `|cosθ|>0.85`.

## Method (sketch)

`kinematics::Grid::new(NB=48)`, centre `c0 = 24`. Shift `N=(0,0, vs·f(r))`, `vs=1`,
`f(r) = ½(1 − tanh((r−R)/w))`, `R=14`, `w=2.5` (inline top-hat — see the menu's "top-hat primitive").
Energy per interior cell from `kinematics::eulerian_16pi_rho`. Classify each cell by radial band (r vs R)
and, in the wall shell, by polar angle `cosθ = z_c/r`. Figures-of-merit: `neg_frac`, `min`, `peak`, the
three band means, and the equator/pole ratio. Emits `data/energy_by_band.csv` and `data/energy_by_angle.csv`.
Static (no time evolution) — this is an energy-*structure* measurement, kinematics only.

## What would falsify this

Any of: `neg_frac < 0.98` or a positive minimum (sign leaked — not exotic); `wall/interior < 10` (energy
not wall-localized — the deformation isn't paying at the wall); `equator/pole < 5` (no torus — the
`sin²θ` structure didn't survive discretization). A uniform shift showing nonzero energy (P0 fails) would
mean the functional charges for translation and the whole framing is wrong.
