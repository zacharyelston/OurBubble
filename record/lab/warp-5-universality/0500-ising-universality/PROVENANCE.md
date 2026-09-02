# Provenance — 0500 Warp-5.0: universality (Ising central charge and exponents)

- **Registered (R1, pre-run):** commit `dc2c12e`. **Run-for-record:** commit `962dacb` (gate + data); this
  eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf5_universality_gate -- --nocapture   # prints recorded numbers
  cargo run  --release -p viz --bin gen_universality                                # → the figure
  ```
- **Determinism:** pure f64, closed-form free-fermion spectrum (no wall-clock, no RNG, no Monte Carlo).
  Critical transverse-field Ising chain, `h_c = 1`, dispersion `ε(k,h) = 2√(1+h²−2h cos k)`. Ground-state
  energy (Neveu–Schwarz sector) `E₀(L) = −½ Σ_{m=0}^{L−1} ε(π(2m+1)/L, 1)`. Finite-size scaling fit
  `E₀/L = e∞ + b/L² + d/L⁴` (3-param least squares) over `L ∈ {16,32,64,128,256,512}`; velocity
  `v = ε(k→0)/k` measured at `k = 2π/8192`; central charge `c = −6b/(πv)`. `ν` from
  `power_law_fit(|h−1|, v/ε(0,h))` over `Δh ∈ {0.2,…,0.005}`; `z` from `power_law_fit(L, ε(π/L,1))`.
- **Data files:** `data/fss.csv` — per `L`: `E₀/L`; `data/nu.csv` — per `Δh`: correlation length `ξ`;
  `data/exponents.csv` — `c, ν, z, e∞, v` (+ cited `β`) with their exact targets.
