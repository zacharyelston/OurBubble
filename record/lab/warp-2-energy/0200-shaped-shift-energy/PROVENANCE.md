# Provenance — 0200 Warp-2.0: the shaped shift's energy structure

- **Registered (R1, pre-run):** commit `61a9b83` (spec.md + gate, before any run-for-record).
- **Run-for-record:** the commit that lands this eval + data + figure (this entry's final commit).
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf2_energy_structure_gate -- --nocapture  # prints numbers; writes data/*.csv
  cargo run  --release -p viz     --bin gen_energy                                     # → figures/energy_structure.html
  ```
  Data lands under this entry's `data/` (path anchored to `CARGO_MANIFEST_DIR`, not cwd).
- **Determinism:** pure f64, analytic field (no seed, no wall-clock, no evolution) — bit-identical on every
  machine. `NB=48, vs=1, R=14, wall=2.5`.
- **Data files:**
  - `data/energy_by_band.csv` — mean `|16πρ|` and cell count for the interior / wall / exterior radial bands.
  - `data/energy_by_angle.csv` — mean `|16πρ|` vs `|cosθ|` in 9 angular bins (equator → pole), the toroidal profile.
