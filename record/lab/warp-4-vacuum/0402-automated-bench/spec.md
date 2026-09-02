# 0402 — Warp-4.2: the automated bench — one law-finder, many laws

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf4_automated_bench_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

The chapter's meta-claim: *the lattice is a cheap virtual workbench whose value-add is automation.* Rungs 4.0
and 4.1 each ran an ad-hoc fit inside their gate; this rung factors that into a **reusable engine capability**
(`kinematics::power_law_fit`) and shows the **same** function discovering laws across **different**
experiments — proving the automation reads physics, not a hardcoded per-gate answer. It rediscovers the
Casimir force scaling, and — with `kinematics::heat_kernel_line` — *measures the lattice's own spatial
dimension* from the Laplacian heat-kernel decay `K(t) ∝ t^{−d/2}`, for `d = 1, 2, 3`.

## Firewall (R3)

`fit, exponent, dimension, heat kernel` name pure data-analysis of lattice outputs — a log–log least-squares
power-law fit and the periodic graph-Laplacian heat-kernel trace. No physical claim beyond the fit; the
"dimension" is the spectral dimension of the toy lattice, not a claim about nature. Dimensionless; c = 1.

## Predictions (registered before the run)

- **P0 (the tool is correct):** on synthetic data `y = 3·x⁻²` the fitter returns exponent `−2`, coefficient
  `3`, `R² = 1` — *gate:* `|p+2| < 1e-9`, `|C−3| < 1e-9`, `R² > 1−1e-9`.
- **P1 (it rediscovers the Casimir force law):** `power_law_fit` on the lattice piston force `|F|` vs `a`
  returns exponent `≈ −2` — *gate:* `|p+2| < 0.10` with `R² > 0.999`.
- **P2 (it measures the lattice dimension):** fitting the heat-kernel trace `Kd(t)=line^d` vs `t` gives
  slope `−d/2`, so measured dimension `−2·p` recovers `1, 2, 3` — *gate:* `|dim−d| < 0.03` for each of
  `d=1,2,3`, each `R² > 0.999`.
- **P3 (one reusable tool):** every result above comes from the **same** `kinematics::power_law_fit` (a
  crate-level export with its own unit tests), and all fits are high quality — *gate:* all `R² > 0.99`.

## Method (sketch)

Reusable `kinematics::discover`: `power_law_fit(xs, ys) -> {exponent, coefficient, r2}` (OLS on
`ln x`, `ln|y|`) and `heat_kernel_line(n, t) = Σₖ e^{−t(2−2cos 2πk/n)}` (periodic Laplacian spectrum;
d-D kernel `= line^d`). The gate: (0) fit synthetic `3x⁻²`; (1) build the piston force `F(a)` (as rung 4.1)
over `a∈{8..64}` and fit `|F|`; (2) for `d∈{1,2,3}` build `Kd(t)=heat_kernel_line(4000,t)^d` over
`t∈{16..512}`, fit, report `dim=−2p`. Emit `data/fits.csv` (experiment, exponent, coeff, R², theory) and
`data/heat_kernel.csv` (t, line, K1, K2, K3).

## What would falsify this

If the fitter missed the synthetic law (P0) the tool is broken. If it did not return `≈ −2` for the force
(P1) or the correct dimension for `d=1,2,3` (P2), the automation would not generalize across experiments —
the "automated bench" claim fails. Recorded honestly either way (R5).
