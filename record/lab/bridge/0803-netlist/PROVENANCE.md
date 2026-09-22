# Provenance — 0803 the netlist / SPICE view

- **Register commit (R1, spec + module + gate):** `f289b44`
- **Run commit (data):** `82696f1`
- **Toolchain:** `rustc 1.91.1 (ed61e7d7e 2025-11-07)`
- **Module:** `core/kinematics/src/views.rs` — `to_spice_netlist`, `mna_resistance` (modified nodal
  analysis), `GraphView::edges`; reference is `effective_resistance` (rung 8.2).
- **Probe (breadcrumb, first-class):** [`core/uniforge/examples/netlist_probe.rs`](../../../core/uniforge/examples/netlist_probe.rs)
  — validated MNA on textbook circuits and caught the grounding-gap singular-matrix bug.
  `cargo run -p uniforge --release --example netlist_probe`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf8_3_netlist_gate -- --nocapture
  # writes data/*.csv and data/stella.cir under lab/bridge/0803-netlist/data/
  ```
- **External (optional, not in CI):** `ngspice -b lab/bridge/0803-netlist/data/stella.cir` reproduces
  the resistances (the netlist is a portable artifact; ngspice is not a build dependency).
- **Determinism:** pure f64, no RNG, no wall-clock. Rule-built 14-regular stella torus (M=3, 27 nodes,
  189 edges).
- **Data files:**
  - `stella.cir` — the SPICE netlist (1 Ω per edge, `V1` probe, ground node 0). Runnable artifact.
  - `resistance.csv` — `pair,mna_netlist,effective_resistance`: P1 agreement per node pair.
  - `walks_circuits.csv` — `pair,elec_2ER_netlist,walk_commute`: P2 cross-rung duality.
  - `summary.csv` — `quantity,value`: cube-diagonal control, edge count, worst netlist-vs-R_eff residual.
