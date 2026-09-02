# eval — 0001 dna-thz rung 1: dielectric shift law Ω ∝ ε_r^p

**Status:** NEGATIVE — naive √ε_r law falsified; clean power-law observed with p ≈ −0.28
**Gate:** `core/uniforge/tests/uf6_1_thz_shift_law_gate.rs`
**Registered commit:** `9f86d75`
**Run commit:** `7fdb4c3`

## Verdict

The measured exponent is p = −0.2753, far from the pre-registered naive prediction of −1/2. This is
a first-class negative result. The inclusion does shift the resonant peak downward in a clean
power-law fashion, but the scaling is much weaker than the uniform-medium √ε_r law would predict.

**Gate encodes the negative (#119).** P3 originally `assert!`ed the naive √ε_r law and so stayed
red forever once it was falsified. It now locks the R5 negative instead: P3 asserts √ε_r is
falsified (|p+1/2| > 0.10) **and** the emergent exponent is held at the measured p ≈ −0.2753
(|Δ| < 0.02). The table row below shows the naive law failing (the science); the gate passes
because it now asserts that failure — so `cargo test` is green and the negative is regression-locked.

## Results table

| Prediction | Expected | Measured | Pass? |
|---|---|---|---|
| P0: bare peak inside restricted band | Ω ∈ (0.20, 0.80) | Ω = 0.6462 | ✓ |
| P1: clean power-law fit | R² > 0.95 | R² = 0.9774 | ✓ |
| P2: downward shift | p < −0.10 | p = −0.2753 | ✓ |
| P3: naive √ε_r law | \|p + 1/2\| < 0.05 | \|p + 1/2\| = 0.2247 | ✗ |

| ε_r | peak Ω | shift vs bare |
|---|---|---|
| 1 | 0.6462 | +0.00% |
| 4 | 0.5231 | −19.05% |
| 9 | 0.4000 | −38.10% |
| 16 | 0.3231 | −50.00% |
| 25 | 0.2769 | −57.14% |
| 36 | 0.2615 | −59.52% |
| 49 | 0.2308 | −64.29% |

Fit: Ω_peak = 0.6968 · ε_r^(−0.2753), R² = 0.9774.

## What this rules in

- A star0-scaled inclusion produces a **clean, reproducible power-law shift** in the driven
  resonant peak over at least ε_r ∈ [1, 49].
- The shift direction is unambiguous: higher ε_r lowers Ω_peak.
- The exponent is **not a free fit target**; it is an emergent number from the lattice geometry
  (small inclusion volume fraction on a finite box).

## What this rules out

- The **naive √ε_r prediction** for this geometry. The uniform-medium / LC-oscillator argument
  assumes the permittivity rescales the entire resonant volume. Here the inclusion occupies only a
  small vertex block (5×3×3 ≈ 3% of the lattice vertices), so the effective scaling is much
  weaker.

## Why −1/2 was expected and why it fails here

For a uniform medium with wave speed c/√ε, the dispersion relation at fixed spatial mode gives
ω ∝ 1/√ε = ε^(−1/2). For an LC oscillator with capacitance C ∝ ε, ω = 1/√(LC) ∝ ε^(−1/2).
Both arguments require ε to control the *entire* resonant volume. On this lattice the inclusion is
localized, so only a fraction of the field energy samples the high-ε region. A perturbative
estimate would give Δω/ω ∝ (volume fraction) · (ε_r − 1), i.e. a much weaker, almost linear shift
at small ε_r. The measured p ≈ −0.28 sits between the perturbative and uniform limits.

## Caveats

- The fitted band [0.20, 0.80] was chosen to avoid a low-frequency box-mode artifact. The choice is
  pre-registered in `spec.md` and reproducible, but it means the result is about one specific
  driven mode, not all modes of the box.
- The inclusion geometry (5×3×3 vertex block) is crude. A volume-fraction sweep (rung 0003 menu
  item) is needed to see whether p approaches −1/2 as the inclusion fills more of the domain.
- The gate uses global damping γ = 0.04. A sharper Q-factor resonance with boundary sponge layers
  might change the absolute peak positions but is unlikely to change the scaling exponent.

## Deferred / next (feeds the chapter menu)

1. **Inclusion volume-fraction sweep:** keep ε_r fixed (e.g. 9 or 16) and vary the inclusion block
   from 1×1×1 to 9×5×5; plot p vs. volume fraction. Test whether p → −1/2 as the inclusion fills
   the domain.
2. **Star1 scaling:** add a `scale_star1` pathway and check whether scaling the edge Hodge star
   produces a different exponent or a qualitatively different signature.
3. **Water shell:** surround the inclusion with a high-permittivity shell and measure the coupling
   shift vs. a dry inclusion.
