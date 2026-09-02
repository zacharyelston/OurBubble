# Provenance — 0503 Warp-5.3: the full-blind 3-D composition

- **Registered (R1, pre-run):** commit `918cb3b` (thresholds set from probes, incl. the ν bias direction).
  **Run-for-record:** commit `8fd47f3` (gate + data); this eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`. Runtime ≈ 106 s (release).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf5_3_blind3d_gate -- --nocapture   # prints recorded numbers
  ```
- **Determinism:** seeded `splitmix64`; Wolff add-probability computed once per `(L,T)`; **incremental
  magnetization** (a cluster flip changes `M` by `−2·old·size` — no full-lattice sum per step). No wall-clock.
- **Method (all outputs; literature only checked after):** 3-D Ising, single-cluster Wolff,
  `L ∈ {12,16,24,32}`, `T ∈ [4.49, 4.53]` step 0.005 (9 points), seed `555 + 131·Lᵢ + Tᵢ`, warmup 8000 +
  50000 measured clusters. **`T_c`** = mean of adjacent-`L` Binder crossings. Per-`L` **quadratic fits** in
  `T` give `dU/dT|_{T_c}` (→ `ν = 1/power_law_fit(L, |dU/dT|).exponent`) and `ln χ`, `ln⟨|m|⟩` at `T_c`
  (→ `γ/ν`, `β/ν` via `power_law_fit`). `U*` = quadratic value of the largest `L` at `T_c`.
- **Data files:** `data/binder3d.csv` — `U` per `(L,T)`; `data/fss3d.csv` — `⟨|m|⟩`, `χ`, `|dU/dT|` at the
  located `T_c` per `L`; `data/results.csv` — `T_c, U*, γ/ν, β/ν, ν` (+ β, γ via measured ν) vs literature.
