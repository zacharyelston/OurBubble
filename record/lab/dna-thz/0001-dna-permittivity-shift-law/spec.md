# 0001 — dna-thz rung 1: dielectric shift law Ω ∝ ε_r^p

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf6_1_thz_shift_law_gate.rs` · **Status:** NEGATIVE — naive √ε_r law falsified; see [`eval.md`](eval.md)

## Goal

Rung 0000 confirmed that scaling the 0-form Hodge star (`⋆₀`) inside a small inclusion block lowers
the lattice's driven resonant frequency. This rung asks a sharper question: over a continuous sweep
of the inclusion weight ε_r, does the resonant peak frequency follow a power law
Ω_peak = C · ε_r^p? And is the exponent consistent with the −1/2 expected from the simple
mass/permittivity scaling of a wave equation, or does the finite inclusion volume modify it?

## Firewall (R3)

"Permittivity", "dielectric", "resonant peak", and "shift law" name operations and outputs of a toy
DEC 1-form wave solver:

- ε_r is a dimensionless per-vertex weight applied through `scale_star0`, not a physical
  permittivity.
- Ω is a dimensionless drive frequency in code units (c = 1).
- The fitted exponent p is an empirical lattice scaling law, not a physical constant.
- No claim is made about real THz frequencies, DNA, cells, or SI material properties.
  See [`../../FIREWALL.md`](../../FIREWALL.md).

## Predictions (registered before the run)

Probe (`dna_thz_shift_law_probe`) measured, on a 16×8×8 tet lattice with a 5×3×3 inclusion block
and the driven-mode band restricted to Ω ∈ [0.20, 0.80]:

| ε_r | peak Ω |
|---|---|
| 1 | 0.6462 |
| 4 | 0.5231 |
| 9 | 0.4000 |
| 16 | 0.3231 |
| 25 | 0.2769 |
| 36 | 0.2615 |
| 49 | 0.2308 |

Full fit: p = −0.2753, R² = 0.9774.
Fit excluding ε_r=1: p = −0.3247, R² = 0.9946.

- **P0 (sanity — the restricted band captures the bare driven mode):** The bare-lattice peak lies
  strictly inside the restricted sweep range [0.20, 0.80]. *Gate:* `bare_peak > 0.20 && bare_peak < 0.80`.

- **P1 (a clean power-law trend exists):** A log–log fit of Ω_peak vs ε_r over the seven cases
  yields R² > 0.95. *Gate:* `law.r2 > 0.95`.

- **P2 (shift direction — higher ε_r lowers the peak):** The fitted exponent p is negative.
  *Gate:* `p < -0.10`.

- **P3 (naive √ε_r law):** The full-fit exponent satisfies |p + 1/2| < 0.05, i.e. p is consistent
  with the −1/2 expected for a uniform mass/permittivity scaling. *Gate:* `(p + 0.5).abs() < 0.05`.

The probe suggests P3 will fail (measured deviation ≈ 0.22). A failure is a first-class result: it
would falsify the naive √ε_r law for this small-inclusion geometry.

## Method

1. `mesh_3d_tetrahedral_grid(16, 8, 8)` with `MeshWaveSolver::with_geometric_hodge`.
2. Feed edge and probe edge: same x-directed edges as rung 0000.
3. Inclusion: same 5×3×3 vertex block centred on the domain; `scale_star0` weight ε_r.
4. Source: `sin(Ω · n)` at each step; `γ = 0.04` global damping.
5. Sweep Ω ∈ [0.20, 0.80], 40 points (restricted band avoids the low-frequency box-mode artifact
   that contaminates the peak finder in the full [0.05, 1.20] range).
6. 400 settle steps + 300 measure steps per frequency; `dt = 0.4`.
7. Cases: ε_r ∈ {1, 4, 9, 16, 25, 36, 49}.
8. Fit `Ω_peak = C · ε_r^p` with `kinematics::power_law_fit` and emit `data/shift_law.csv`.

## What would falsify this

- Bare peak outside [0.20, 0.80] → the restricted band no longer tracks the same driven mode.
- R² < 0.95 → the peak positions do not follow a single power law.
- p ≥ 0 → the inclusion does not shift the peak downward (would contradict rung 0000).
- P3 is a falsifiable target: if |p + 1/2| ≥ 0.05, the naive √ε_r law is ruled out for this geometry.

## Pre-registered caveat / systematic

The naive −1/2 prediction assumes a uniform medium. The inclusion here occupies only a small
fraction of the total lattice volume, so the effective scaling is expected to be weaker than
−1/2. The probe already hints at p ≈ −0.28. P3 failing because the exponent is shallower than −1/2
would be a legitimate negative result, not a bug.
