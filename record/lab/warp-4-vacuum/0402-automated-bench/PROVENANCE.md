# Provenance — 0402 Warp-4.2: the automated bench

- **Registered (R1, pre-run):** commit `a4e061f` (also adds `kinematics::discover`). **Run-for-record:**
  commit `01a3efc` (gate + data); this eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p kinematics discover                                     # the reusable tool's unit tests
  cargo test --release -p uniforge --test uf4_automated_bench_gate -- --nocapture
  cargo run  --release -p viz --bin gen_bench                                      # → the figure
  ```
- **Determinism:** pure f64, closed-form (no wall-clock, no RNG). Reusable `kinematics::power_law_fit` (OLS
  on `ln x`, `ln|y|`) and `kinematics::heat_kernel_line(n,t) = Σₖ e^{−t(2−2cos 2πk/n)}`. Experiments:
  synthetic `y = 3x⁻²` over `x=1..10`; Casimir piston force `F(a)` (bath `N_tot=4000`, central difference)
  over `a ∈ {8,12,16,24,32,48,64}`; heat kernel `Kd(t) = heat_kernel_line(4000,t)^d` over
  `t ∈ {16,32,64,128,256,512}`, `d ∈ {1,2,3}`; spectral dimension `= −2·exponent`.
- **Data files:** `data/fits.csv` — per experiment: discovered exponent, coefficient (or measured
  dimension), R², and the theory exponent; `data/heat_kernel.csv` — `t`, the 1-D trace `line(t)`, and
  `K1,K2,K3 = line^{1,2,3}`.
