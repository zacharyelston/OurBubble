# Provenance — 0117 Warp-1.7: `ω = c·k` discovered blind, in five directions

- **Registered (R1):** `f364fb14fbb234cf99bffeb936d4ef89b4986da7` — `spec.md` + the gate committed
  **before** the run for record.
- **Run for record:** `f2f610b5e48a9d650ddecaef18d56842c4ea2a48` — the gate green (P0–P4), `data/`
  written by that run.
- **Toolchain:** `rustc 1.97.1 (8bab26f4f 2026-07-14)`, `--release`.
- **Gate:** `core/uniforge/tests/uf1_7_dispersion_isotropy_gate.rs` (14.5 s wall, tier-2).
- **Regenerate:**
  ```bash
  cd core
  cargo test -p uniforge --release --test uf1_7_dispersion_isotropy_gate -- --nocapture
  # rewrites every file in this entry's data/ and prints the scorecard above
  cargo run  -p viz      --release --bin gen_discovery
  # rebuilds figures/discovery.html from that data/
  ```
- **Probe (breadcrumb).** `core/uniforge/examples/dispersion_isotropy_probe.rs` — the committed
  record of how the registered thresholds were chosen:
  ```bash
  cd core && cargo run -p uniforge --release --example dispersion_isotropy_probe
  ```
  It carries an `N ∈ {48, 64, 72}` size ladder (showing the window-composition sensitivity of the
  anisotropy `A` and the stability of the `A(K)/A(K/2)` ratio at `2.58`–`2.60`), a raw-vs-unfolded
  star arm (seam corruption inflates apparent anisotropy ~1.4×, #177/1.6b — probed, not gated), and
  the `⋆₁`-by-edge-class census that discovered the mechanism behind P0's closed-form key.
- **Determinism:** pure `f64`, no RNG, no wall-clock, no parallel reduction in the measured path —
  identical numbers on every machine. The gate's own elapsed-time print is the only wall-clock use
  and enters no assertion.
- **Reused, not re-derived:** `geom::mesh::mesh_3d_tetrahedral_grid_periodic`,
  `solve::bloch::{unfolded_scalar_stars, Lattice}`, `dec::operators::apply_laplacian_0_metric`,
  `kinematics::{select_power_law, fit_fixed_exponent, power_law_fit}`. The last two are new in the
  register commit, with their own unit tests in `core/kinematics/src/discover.rs`.

## Data files

| file | what it holds |
|---|---|
| `dispersion_directions.csv` | the raw sweep: `direction, m, k, lambda, omega, phase_speed, symbol_lambda` — 63 modes over the five directions out to `\|k\| ≤ 2.10`. `symbol_lambda` is the closed-form 7-point key `Σ_a(2−2cos k_a)`, P0's answer key. |
| `discovery.csv` | per direction: window sizes, the **selected** candidate exponent and its `R²`, the selection margin over the runner-up, the free-fit `exponent`/`coefficient`/`r2` on the long-λ window, the full-range exponent, and the bend. |
| `candidates.csv` | the model-selection scorecard: `direction, candidate_exponent, r2, selected` for all six candidates × five directions (30 rows) — the source of the figure's candidate panel. |
| `isotropy.csv` | four anisotropy measurements: geometric ⋆ and `⋆ = I`, each at the long and halved windows, with the `C` ranges. |
| `answer_key.csv` | P0's machinery residuals paired with the bound each was registered against. |
