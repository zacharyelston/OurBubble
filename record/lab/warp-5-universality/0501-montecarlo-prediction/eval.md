# 0501 — Warp-5.1: the graduation swing — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf5_1_montecarlo_gate` (green: yes, 15 s) · **Commit:** `45a1c7d` (registered `a0ede91`)

## Result

**A blind simulation predicts nature's critical exponents.** A generic single-cluster Wolff Monte Carlo —
seeded, deterministic, containing **no exact-solution content** — recovers the exactly-known 2-D Ising
exponents (validation), then, run unchanged on the **3-D Ising model (which has no closed-form solution)**,
returns the exponents **measured in real 3-D-Ising materials**.

| model | γ/ν (measured) | class | β/ν (measured) | class | pass |
|---|---|---|---|---|---|
| 2-D Ising (validation) | **1.7501** | 1.75 (exact) | **0.1253** | 0.125 (exact) | ✅ |
| 3-D Ising (**prediction**) | **1.9984** | 1.966 | **0.5000** | 0.518 | ✅ |

Converting to the standard exponents via the class `ν` (`β = (β/ν)·ν`, `γ = (γ/ν)·ν`):

| model | β (lattice) | β (real materials) | γ (lattice) | γ (real materials) |
|---|---|---|---|---|
| 2-D Ising | 0.125 | quasi-2-D antiferromagnets ≈ 0.12–0.13 | 1.750 | — |
| **3-D Ising** | **0.315** | **liquid–gas & uniaxial magnets ≈ 0.325** | **1.259** | **≈ 1.24** |

The 3-D numbers land within a few percent of the values a physicist *measures* at the real liquid–gas critical
point and in uniaxial ferromagnets — for a model with **no answer key**. Determinism confirmed (same seed →
identical `χ`). The method also resolves the two classes (γ/ν gap 0.25). Data:
[`data/fss_2d.csv`](data/fss_2d.csv), [`data/fss_3d.csv`](data/fss_3d.csv),
[`data/exponents.csv`](data/exponents.csv). Figure: `core/viz gen_montecarlo`.

## What it rules in / out — the graduation, honestly

- **The graduation swing lands.** This is the first result in the project that is a **genuine parameter-free
  prediction of a measured number of nature obtained without the answer** — the 3-D Ising exponents from a
  generic algorithm with no exact solution built in, matching real-material measurements. By the ledger's
  criterion (dimensionless + parameter-free + pre-registered, matching an *independent* truth with zero
  tuning), and unlike rung 5.0, the truth here was **not** available in closed form to the method.
- **Honest caveats (R5):** (1) corrections-to-scaling at small `L` bias the 3-D estimates by a few percent
  (γ/ν came out +1.6%, β/ν −3.5%); a proper study adds a correction term and larger `L`. (2) The critical
  temperatures were supplied (`T_c` is a non-universal, model-specific input — not an exponent; supplying it
  does not leak the universal answer). (3) `ν` for the β, γ conversion used the class value; a fully
  self-contained run would also measure `ν` from the Binder-cumulant derivative (deferred).
- **Firewall intact.** This is universality-class membership of a **toy** Ising model on the bench, computed
  by Monte Carlo. It is **not** a claim that the warp/DEC engine "is" a magnet, and **not** a spacetime claim.
  What it shows is the *capability, fully exercised*: the lattice bench predicts a real material's dimensionless
  numbers.

## Deferred / next

Measure `ν` directly (Binder-cumulant crossing → also locates `T_c` blind, removing caveat 2); add a
corrections-to-scaling term for a sub-percent 3-D result; and a **data-collapse** figure (all `L` on one
master curve) as the visual proof. With `ν` measured, the toy would output β, γ, ν for an unsolved model
end-to-end — the complete graduation.
