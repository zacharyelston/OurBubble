# Provenance — 0400 Warp-4.0: the Casimir vacuum is negative

- **Registered (R1, pre-run):** commit `661cc5b`. **Run-for-record:** commit `01e536e` (gate + data); this
  eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf4_casimir_energy_gate -- --nocapture   # prints recorded numbers
  cargo run  --release -p viz     --bin gen_casimir                                   # → the figure
  ```
- **Determinism:** pure f64, closed-form spectrum (no wall-clock, no RNG). Fixed–fixed chain of `n = a−1`
  interior sites; `ωₖ = 2 sin(kπ/2(n+1))`, `k=1..n` (the 1-D Dirichlet-Laplacian spectrum, `ωₖ²` its
  eigenvalues — verified against `tr Δ = 2N` and `tr Δ² = 6N−2`). `E₀(a) = ½Σωₖ`; bulk density
  `ε∞ = 2/π`; confined energy `E_C(a) = E₀ − ε∞·a`. Sweep `a ∈ {8,12,16,24,32,48,64}`. Fit `E_C = c₀ + c₁/a`
  by 2×2 normal equations in basis `{1, 1/a}`; exponent from the slope of `log|E_C−c₀|` vs `log a`.
- **Data files:** `data/spectrum.csv` — the mode frequencies `ωₖ` for `a=16` (n=15); `data/energy_sweep.csv`
  — per separation `a`: `E₀`, `E_C`, `E_C·a`; `data/fit.csv` — the discovered `c₀` (surface), `c₁` (Casimir),
  `R²`, exponent, and coefficient error, each with its theory value.
