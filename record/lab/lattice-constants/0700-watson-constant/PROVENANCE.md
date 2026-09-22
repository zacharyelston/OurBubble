# Provenance — 0700 the stella random-walk constant (Watson integral)

- **Commits:** registered `2cbe186` (`code:`, R1 — spec + gate before any run-for-record),
  `ff649a2` (`fix:` — relative Hermiticity residue bound; see eval.md "Fix vs the registered
  gate (R5)"), run-for-record `cf357dd` (`run:` — the committed `data/`).
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`
- **Regenerate:**
  ```bash
  cd core
  cargo test -p uniforge --release --test uf7_0_watson_gate -- --nocapture   # ~3 s; prints the scorecard
  # data/*.csv land under this entry's data/
  cargo run -p viz --release --bin gen_watson -- <run-commit-sha>            # renders figures/watson.html
  ```
- **Determinism:** pure f64, no RNG, no wall-clock — the torus k-sums, the CG solve, the mesh
  adjacency check, and the matvec partial sums produce the same numbers on every machine.
- **Data files:**
  - `watson_constants.csv` — the scorecard: measured vs target vs tolerance for `g_sc`, `g_fcc`,
    `p_fcc`, `g_stella`, `p_stella`, the Watson integral `F(0,0,0;3) = g_fcc/3`, and the `S₈`
    lower bound.
  - `sc_conv.csv`, `fcc_conv.csv` — raw deflated torus sums `G_M` at `M = 48, 96, 192, 384` with
    errors vs the Γ-function closed forms.
  - `stella_conv.csv` — the same four raw sums for the stella tet-oct graph (no external target).
  - `ladder.csv` — every Richardson-ladder level (orders 1, 3, 5) for all three lattices.
  - `stella_partial_sum.csv` — the open-mesh return series `p_t(0,0)` and partial sums `S_t`,
    `t = 0…8` (the strict lower bound leg).
