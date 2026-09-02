# Provenance — 0300 Warp-3.0: the shield, the imbalance, and inertia

- **Registered (R1, pre-run):** commit `6db889c` (parent). **Run-for-record:** the commit landing this eval + data.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf3_shield_imbalance_gate -- --nocapture
  cargo run  --release -p viz     --bin gen_shield
  ```
- **Determinism:** pure f64. `N=24`, shell `R=9, W=1, V0=40` (compactly supported, `V≡0` for `|r−R|≥3W`);
  screened Poisson `(Δ+κ₀²+V)`, `κ₀²=0.02`, solved by conjugate gradient (tol 1e-9); packet evolution
  `step`-scheme, `σ=1.8, u=0.4, dt=0.05, c=1, 16 steps`. `Δ = compute_laplacian_0form` (geometric ⋆).
- **Data files:** `data/shield.csv` — interior vs exterior-control couplings (open/shielded/ratio);
  `data/inertia.csv` — effective inertia, interior packet displacement, reflected-wave leak, `m²_eff` at
  centre/wall, and the measured interior coupling ratio (for the fenced entropic hypothesis-consequence).
