# Provenance — 0115 Warp-1.5 lattice-matched isotropy

- **Commit:** `f8d9952` (the ported gate + `kinematics`/`uniforge` it uses are present at this commit or later).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf1_5_lattice_matched_gate -- --nocapture
  ```
  The gate **writes** [`data/isotropy.csv`](data/isotropy.csv) directly (R10) — the path is anchored to
  `CARGO_MANIFEST_DIR`, so it lands in this entry's `data/` regardless of where `cargo test` is run.
  Re-running reproduces the file byte-for-byte.
- **Determinism:** f64, fixed seed pulse, no wall-clock — identical numbers on every machine (and
  bit-for-bit identical to `stellamax-core`'s original lab/0115).
- **Data files:**
  - `data/isotropy.csv` — `solver, v_axis_100, v_diag_111, anisotropy` for `⋆=I` and the geometric Hodge.
- **Note (R10 wiring):** the gate currently prints these numbers; wiring it to *write* `data/isotropy.csv`
  directly (as `uf1_44` writes its CSVs) is a small follow-up — tracked with the lab-artifact path work (#10).
