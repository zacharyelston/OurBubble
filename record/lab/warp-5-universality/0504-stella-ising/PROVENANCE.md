# Provenance — 0504 Warp-5.4: Ising on the stella lattice

- **Registered (R1, pre-run):** commit `b5b1cdf` (thresholds probe-informed). **Run-for-record:** commit
  `fe754c1` (gate + data); eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`. Runtime ≈ 40 s (release).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf5_4_stella_ising_gate -- --nocapture
  ```
- **Determinism:** seeded `splitmix64` (seed `42 + 17n + tᵢ`), Wolff add-probability computed once per
  `(n,T)`, incremental magnetization. No wall-clock.
- **Method:** mesh = `mesh_3d_chiral_tetoct_yz_periodic(n,n,n, engine_operator::oct_axis)`; vertex
  adjacency from `d0_sparse` (head/tail per edge row), compacted to degree>0 vertices (the FCC sublattice;
  bulk coordination 14 = FCC 12 + octahedral long diagonals). Wolff, `n ∈ {8,12,16,24}`,
  `T ∈ [11.30, 11.70]` step 0.05, warmup 4000 + 60000 measured clusters. `T_c` = mean of adjacent-`L`
  Binder crossings; per-`L` quadratic fits in `T` give `U*`, `ln χ`, `ln⟨|m|⟩` at `T_c`; ratios via
  `kinematics::power_law_fit` over all four sizes.
- **Data files:** `data/stella_graph.csv` — n=16 graph stats; `data/binder_stella.csv` — `U, χ, ⟨|m|⟩` per
  `(L,T)`; `data/results.csv` — `T_c, U*, γ/ν, β/ν` with their checks (class values; 5.3's cubic values).
