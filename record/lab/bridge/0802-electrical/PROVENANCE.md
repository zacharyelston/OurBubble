# Provenance — 0802 the 4th view (electrical / random-walk)

- **Register commit (R1, spec + module + gate):** `1b61300`
- **Run commit (data):** `73a4d40`
- **Toolchain:** `rustc 1.91.1 (ed61e7d7e 2025-11-07)`
- **Module:** `core/kinematics/src/views.rs` — `effective_resistance`, `hitting_time`, `commute_time`,
  `spanning_tree_ln` (Kirchhoff), `dense_solve`. The `⟨ln λ⟩` Bloch sum lives in the gate (screw-specific).
- **Probe (breadcrumb, first-class):** [`core/uniforge/examples/electrical_probe.rs`](../../../core/uniforge/examples/electrical_probe.rs)
  — learned z, its log-singularity convergence, and the walks↔circuits identity; caught the
  engine-mesh-vs-rule-built-torus graph mismatch. `cargo run -p uniforge --release --example electrical_probe`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf8_2_electrical_gate -- --nocapture
  # writes data/*.csv under lab/bridge/0802-electrical/data/
  ```
- **Determinism:** pure f64, no RNG, no wall-clock. Bloch k-sum over M=24,48,96,192 (Richardson);
  dense Jacobi + Gaussian-elimination solves on the rule-built torus.
- **Graph:** the rule-built 14-regular stella torus (7.0's `stella_torus_adjacency`) — the actual complex
  vertices; NOT the engine periodic mesh (placeholders would corrupt `⟨ln λ⟩`).
- **Data files:**
  - `kirchhoff_controls.csv` — `graph,ln_tau,expected`: Cayley/cycle spanning-tree controls (P0).
  - `entropy_ksum.csv` — `M,z_M`: the Bloch `⟨ln λ⟩` ladder (P1).
  - `walks_circuits.csv` — `pair,R_eff,elec_2ER,walk_commute`: the P2 membership identity per node pair.
  - `summary.csv` — `quantity,value`: `z_stella`, `z_6` dense vs Bloch.
