# 0400 — Warp-4.0: the Casimir vacuum is negative — and the lattice discovers the law

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf4_casimir_energy_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

The warp wall needs `ρ < 0`; classical fields can't (ch. 2) and shields only reach zero (ch. 3). The one
mechanism that genuinely gives negative energy is the **quantum vacuum with boundaries** — the Casimir
effect. We build it as the zero-point energy `E₀ = ½Σℏωₖ` of a toy scalar field on a fixed–fixed lattice
chain (the engine's Dirichlet Laplacian `d†d`; `ωₖ² = 4sin²(kπ/2(N+1))` are its eigenvalues). The lattice
spectrum is its own UV cutoff, so `E₀` is finite with no zeta regularization. Subtracting the bulk vacuum
leaves a genuinely **negative** confined energy. This rung is also the chapter's automation proof: the gate
does not check a hardcoded number — it **sweeps the plate separation, least-squares-fits the law, and
discovers** both the exponent (`E_Casimir ∝ 1/a`) and the coefficient (`−π/24`), then holds them against
theory.

## Firewall (R3)

`vacuum, Casimir, plate, mode, energy` name the zero-point energy `½Σℏωₖ` of a **toy** scalar field (a
fixed–fixed oscillator chain = the engine's 1-D Dirichlet Laplacian) with prescribed boundaries on a **toy**
lattice. `ℏ` is a dimensionless bookkeeping constant; standard QFT zero-point bookkeeping, **not** a real
device, spacetime claim, or free energy. c = 1.

## Predictions (registered before the run)

- **P0 (the spectrum is the engine's Laplacian):** the mode frequencies satisfy `ωₖ² = ` eigenvalues of the
  1-D Dirichlet Laplacian — *gate:* `Σωₖ² = tr(Δ) = 2N` to `< 1e-9` (we sum the zero-point energy of the
  right operator).
- **P1 (the confined vacuum energy is NEGATIVE):** after removing the bulk vacuum density `ε∞ = 2/π`, the
  confined energy `E_C(a) = ½Σωₖ − ε∞·a < 0` for every tested separation — *gate:* `E_C(a) < 0` for all `a`
  in the sweep.
- **P2 (the lattice DISCOVERS the Casimir law):** a two-parameter least-squares fit `E_C(a) = c₀ + c₁/a`
  recovers the surface term `c₀ → −1/2` and the **Casimir coefficient** `c₁ → −π/24 ≈ −0.13090` — *gate:*
  fit `R² > 0.999`, `|c₀ + 0.5| < 0.02`, and `|c₁ − (−π/24)| / (π/24) < 0.03` (discovered coefficient within
  3% of theory).
- **P3 (attractive — the plates are pulled together):** the Casimir energy deepens as the plates approach,
  `∂E_C/∂a > 0` throughout the sweep (energy rises toward the bulk value as `a` grows) — *gate:* `E_C(a)` is
  strictly increasing in `a`.

## Method (sketch)

Fixed–fixed chain of `N = a−1` interior sites (plates at `0` and `a`); mode frequencies
`ωₖ = 2 sin(kπ/2(N+1))`, `k=1..N` (closed form of the Dirichlet-Laplacian spectrum; `ωₖ²` verified against
`tr Δ`). Zero-point energy `E₀(a) = ½Σωₖ`. Bulk density `ε∞ = (1/π)∫₀^π sin(q/2)dq = 2/π`. Confined energy
`E_C(a) = E₀(a) − ε∞·a`. Sweep `a ∈ {8,…,64}`; fit `E_C = c₀ + c₁/a` by normal equations in the basis
`{1, 1/a}`, report `c₀, c₁, R²`, and the discovered exponent (slope of `log|E_C−c₀|` vs `log a → −1`). Emit
`data/spectrum.csv` (ωₖ for one a), `data/energy_sweep.csv` (a, E₀, E_C), `data/fit.csv` (c₀, c₁, R², exponent).

## What would falsify this

If `E_C(a) ≥ 0` anywhere (P1), the boundary vacuum would not be negative and the Casimir claim fails. If the
fit did not select `1/a` (`R²` low, or exponent ≠ −1) or the coefficient missed `−π/24` (P2), the lattice
would not reproduce the known Casimir law — the automated bench would be untrustworthy. Either is recorded
honestly (R5).
