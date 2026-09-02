# 0500 — Warp-5.0: universality — the lattice measures the Ising central charge and exponents

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_universality_gate.rs` · **Status:** registered (pre-run)

## Goal (one paragraph)

The graduation swing. `PREDICTIONS.md` says the toy stops being a toy only when it outputs a **dimensionless
number of nature** it wasn't built to know, with zero tuning. Universality provides exactly that: the
critical point of the transverse-field Ising chain (free-fermion solvable, same lattice bench) carries
universal invariants — the **central charge `c`** and the exponents **`ν`, `z`** — that are *identical* for
this toy, the 2-D classical Ising model, and real Ising-class materials. We extract them from raw finite-size
data with no fitted physics constant: the central charge from the `1/L²` correction to the ground-state
energy, `ν` from the correlation length, `z` from the critical gap. The velocity `v` is **measured** from the
dispersion, not assumed, so the result is fully parameter-free.

## Firewall (R3)

`Ising, critical, central charge, exponent` name universal invariants of a **toy** quantum spin chain's
critical point on the lattice bench. Shared with the 2-D classical Ising model and real Ising-class systems
(universality). Not a claim that the warp/DEC engine is a magnet; not a spacetime claim. Dimensionless; c = 1.

## Predictions (registered before the run)

- **P0 (control — the exact critical energy density):** the finite-size fit's intercept recovers the known
  critical ground-state energy density `e∞ = −4/π` — *gate:* `|e∞ − (−4/π)| < 1e-4`.
- **P1 (the central charge — the graduation number):** finite-size scaling `E₀(L)/L = e∞ − πcv/(6L²)` in the
  physical (Neveu–Schwarz) sector, with `v` measured from the dispersion, gives the Ising central charge
  `c = 1/2` — *gate:* `|c − 0.5| < 1e-3`.
- **P2 (correlation-length exponent):** `ξ(h) = v/Δ(h)` with gap `Δ = ε(k=0,h)`; a power-law fit of `ξ` vs
  `|h − h_c|` gives `ν = 1` — *gate:* `|ν − 1| < 0.02`.
- **P3 (dynamic exponent):** the critical finite-size gap `Δ(L) = ε(π/L, h_c)` scales as `L^{−z}` with
  `z = 1` — *gate:* `|z − 1| < 0.02`.

## Method (sketch)

Critical TFIM `H = −Σσᶻσᶻ − hΣσˣ`, `h_c = 1`. Jordan–Wigner → free fermions with `ε(k,h) = 2√(1+h²−2h cos k)`
(built on the same `2−2cos k` lattice-Laplacian spectrum used in ch. 4). Ground-state energy (NS sector)
`E₀(L) = −½ Σ_{m} ε(π(2m+1)/L, 1)`. Fit `E₀/L = e∞ + b/L² (+ d/L⁴)`; `v = ε(k→0)/k` measured;
`c = −6b/(πv)`. `ν` from `power_law_fit(|h−1|, v/ε(0,h))`; `z` from `power_law_fit(L, ε(π/L,1))` (both
`kinematics::power_law_fit`). Emit `data/fss.csv` (L, E₀/L), `data/nu.csv` (Δh, ξ), `data/exponents.csv`
(c, ν, z, e∞, v with targets). Note: `β = 1/8` (Pfeuty exact `M=(1−h²)^{1/8}`) — the directly-measured
magnetization exponent of the same class, cited here, computed directly in a later rung.

## What would falsify this

If the `1/L²` coefficient did not give `c = 1/2` (P1), or `ν`/`z` missed 1 (P2/P3), or `e∞ ≠ −4/π` (P0), the
lattice would not sit in the Ising universality class and the graduation swing would miss — recorded honestly
(R5). (A near-miss in `c` would most likely mean the wrong fermion sector or an un-measured `v`.)
