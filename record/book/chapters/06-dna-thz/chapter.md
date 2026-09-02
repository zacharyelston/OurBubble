# 06 · A toy bridge — can the lattice speak to THz and DNA at once?

## Public voice

Two literatures sit on either side of a frequency gap. One studies terahertz spectroscopy as a
clinical tool: cells, tissues, and lab-grown samples leave measurable fingerprints in the 0.1–1.0 THz
window. The other studies DNA as an electromagnetic object: resonant modes, phonon-like waves, and
claims of emitted radiation in the same range. The dna-thz chapter does not try to prove either. It
asks whether a structure-preserving lattice Maxwell solver can reproduce the *kinds of signatures both
literatures agree on* — frequency shifts and resonant coupling — using only geometry and material
contrast, with no biological claim built into the engine.

The firewall is strict. Every word — antenna, inclusion, permittivity, DNA-range, water — names a
geometric or material assignment on a simplicial lattice. The results are dimensionless ratios of
lattice frequencies. No SI unit, no real molecule, no clinical claim.

## What we have so far

**Rung 0000** established that scaling the 0-form Hodge star (`⋆₀`) of a small inclusion block near
a driven edge lowers the lattice's resonant frequency. The shift is monotone with the inclusion
weight ε_r and reproducible. The peak moved from Ω = 0.6347 (bare) to 0.4008 at ε_r = 9 and 0.1280
at ε_r = 60 — a −37% to −80% downward shift.

**Rung 0001** sharpened that observation into a quantitative law. Over ε_r ∈ {1, 4, 9, 16, 25, 36, 49}
the peak positions follow a clean power law Ω_peak = C · ε_r^p with R² = 0.9774. The bench
*discovered* the exponent blindly: **p = −0.2753**. This is not close to the naive **p = −1/2**
expected from a uniform mass/permittivity scaling. The uniform-medium argument fails because the
inclusion occupies only a small fraction of the lattice volume; most of the resonant mode lives in
unweighted space, so the effective scaling is much weaker.

That is a first-class negative result. It rules in the existence of a reproducible shift law; it
rules out the simplest √ε_r analogy for this geometry.

<figure>
  <a href="../../../lab/dna-thz/0001-dna-permittivity-shift-law/figures/shift_law.html">
    <img src="../../../lab/dna-thz/0001-dna-permittivity-shift-law/figures/shift_law.png" alt="Shift-law log-log plot"/>
  </a>
  <figcaption>
    <b>Data-true figure (R10):</b> log Ω_peak vs log ε_r for the driven lattice mode. Dots are the
    run; gold line is the blind fit Ω = C · ε_r^(−0.2753); dashed violet line is the naive uniform-medium
    p = −1/2 prediction. The naive prediction is falsified. Gate <code>uf6_1_thz_shift_law_gate</code>,
    commit <code>7fdb4c3</code>.
  </figcaption>
</figure>

## Study-guide voice

- **The engine primitive:** `MeshWaveSolver::with_geometric_hodge` on a 16×8×8 tetrahedral grid,
  with `scale_star0` encoding material contrast as a per-vertex Hodge weight.
- **The observable:** steady-state RMS amplitude at a probe edge, swept over drive frequency Ω. The
  peak Ω is read off by the gate, not hardcoded.
- **The law-discovery tool:** `kinematics::power_law_fit` performs a log–log least-squares fit and
  returns exponent, coefficient, and R². The gate asserts the pre-registered predictions.
- **Why the naive prediction fails:** p = −1/2 assumes ε controls the whole resonant volume. A small
  inclusion only perturbs a fraction of the mode; the measured p ≈ −0.28 reflects the actual
  volume-fraction-weighted scaling of this geometry.
- **Honest next steps:** vary the inclusion volume fraction to see whether p → −1/2 as the inclusion
  fills the domain; try scaling `⋆₁` instead of `⋆₀`; add a water-like high-permittivity shell.

## Firewall reminder

This chapter is a toy bridge. The signatures it reproduces are lattice signatures. They share *shape*
with the THz diagnostics and DNA-wave literatures — resonant shifts, coupling, frequency dependence —
but the engine never imports a DNA model, a cell model, or a SI frequency. The word “DNA” in the
chapter name is a thematic label, not a claim.
