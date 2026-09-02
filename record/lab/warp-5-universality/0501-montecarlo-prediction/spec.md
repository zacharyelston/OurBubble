# 0501 — Warp-5.1: the graduation swing — blind Monte Carlo predicts nature's critical exponents

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_1_montecarlo_gate.rs` · **Status:** registered (pre-run)

## Goal (one paragraph)

Rung 5.0 validated the finite-size-scaling machinery on an *exactly solvable* model (a postdiction). This rung
takes the real swing: run a **generic Monte Carlo** — single-cluster Wolff, which contains **no exact-solution
input** — on the Ising model in 2-D and 3-D, and extract the critical exponents from raw simulation data by the
same FSS the previous rung used. The 2-D case is the **validation** (its exponents are known exactly, so we can
check the blind method). The 3-D case is the **genuine prediction**: the 3-D Ising model has **no closed-form
solution**, yet the exponents the lattice returns are the ones **measured in real 3-D-Ising materials** (the
liquid–gas critical point, uniaxial magnets, binary alloys). A dimensionless number of nature, from a model
with no answer key — the graduation criterion.

## Firewall (R3)

`Ising, Monte Carlo, exponent` name a seeded, deterministic single-cluster Wolff simulation of a **toy** Ising
model on the lattice bench, and universal exponents extracted by finite-size scaling. Universality-class
membership shared with real materials — **not** a claim the warp/DEC engine is a magnet, not a spacetime claim.
The PRNG is a fixed-seed `splitmix64`; the transition probability is precomputed once, so the run is
reproducible. Dimensionless.

## Predictions (registered before the run)

- **P0 (deterministic):** the same seed gives the same result — a 2-D `L=16` run repeated is identical —
  *gate:* the two `χ` values are exactly equal (`==`).
- **P1 (validation — the blind method recovers the exact 2-D exponents):** 2-D Ising Wolff + FSS (`χ = N⟨m²⟩ ~
  L^{γ/ν}`, `⟨|m|⟩ ~ L^{−β/ν}`, at the exact `T_c = 2/ln(1+√2)`) gives `γ/ν = 1.75` and `β/ν = 0.125` —
  *gate:* `|γ/ν − 1.75|/1.75 < 0.03` and `|β/ν − 0.125|/0.125 < 0.05`.
- **P2 (the novel prediction — an unsolved model):** 3-D Ising (no closed form) via the **same** pipeline at
  `T_c ≈ 4.5115` gives the 3-D-Ising-class exponents `γ/ν ≈ 1.966`, `β/ν ≈ 0.518` — *gate:*
  `|γ/ν − 1.966|/1.966 < 0.06` and `|β/ν − 0.518|/0.518 < 0.08`.
- **P3 (distinct classes, both real):** the method resolves the dimensionality — the 2-D and 3-D `γ/ν` differ
  by a wide margin, each matching *its own* universality class (the classes of real 2-D and 3-D critical
  materials) — *gate:* `γ/ν(3D) − γ/ν(2D) > 0.15`.

## Method (sketch)

Single-cluster **Wolff** (add aligned neighbours with `p = 1 − e^{−2/T_c}`, flip the cluster) — a generic
critical-dynamics algorithm with no exact-solution content. Seeded `splitmix64`. 2-D: `L ∈ {8,16,32,64}`,
warmup 4000 + 40000 measured clusters, at exact `T_c`. 3-D: `L ∈ {12,16,24,32}` (drop the smallest — strong
corrections to scaling), warmup 6000 + 60000 clusters, at `T_c = 4.511536`. Observables per size: `⟨|m|⟩` and
`χ = N⟨m²⟩`; exponent ratios from `kinematics::power_law_fit` (`γ/ν` from `χ` vs `L`, `β/ν` from `⟨|m|⟩` vs
`L`). Emit `data/fss_2d.csv`, `data/fss_3d.csv`, `data/exponents.csv` (ratios vs class targets; β, γ via class
ν vs real-material measurements).

## What would falsify this

If the blind 2-D exponents missed the exact values (P1), the method would be untrustworthy. If the 3-D
exponents did not land on the measured 3-D-Ising-class values (P2), the lattice would not sit in that class and
the prediction would fail. If 2-D and 3-D gave the same `γ/ν` (P3), the method would not resolve universality.
Corrections-to-scaling at small `L` bias the 3-D estimates by a few percent (a known systematic); this is
stated, not hidden (R5).
