# Provenance — 0502 Warp-5.2: the complete, self-contained prediction

- **Registered (R1, pre-run):** commit `4e6cb63`. **Run-for-record:** commit `87cbd96` (gate + data); this
  eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`. Runtime ≈ 23 s (release).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf5_2_selfcontained_gate -- --nocapture   # prints recorded numbers
  cargo run  --release -p viz --bin gen_selfcontained                                  # → the figure
  ```
- **Determinism:** seeded `splitmix64`; the Wolff add-probability `p = 1 − e^{−2/T}` is computed once per
  `(L,T)`, so runs are reproducible. No wall-clock.
- **Method (all outputs, only the model is input):** 2-D Ising, single-cluster Wolff, `L ∈ {8,16,24,32}`,
  temperature grid `T ∈ [2.25, 2.29]` step 0.005 (9 points), seed `777 + 131·Lᵢ + Tᵢ`, warmup 5000 + 80000
  measured clusters. Binder `U = 1 − ⟨m⁴⟩/3⟨m²⟩²`. **`T_c`** = mean of adjacent-`L` `U`-curve crossings
  (linear interpolation). **`ν`** = `1 / power_law_fit(L, |dU/dT|).exponent`, `dU/dT` the per-`L` OLS slope of
  `U(T)`. **`β/ν, γ/ν`** = `power_law_fit(L, ·)` of `⟨|m|⟩`, `χ` interpolated to the located `T_c`;
  `β=(β/ν)ν`, `γ=(γ/ν)ν`. `U*` = `U` of the largest `L` at `T_c`.
- **Data files:** `data/binder.csv` — `U` per `(L,T)`; `data/fss.csv` — `⟨|m|⟩`, `χ` at the located `T_c` per
  `L`; `data/results.csv` — `T_c, U*, ν, β, γ, β/ν, γ/ν` vs exact.
