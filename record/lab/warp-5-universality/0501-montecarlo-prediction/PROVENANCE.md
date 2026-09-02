# Provenance — 0501 Warp-5.1: the graduation swing (blind Monte Carlo)

- **Registered (R1, pre-run):** commit `a0ede91`. **Run-for-record:** commit `45a1c7d` (gate + data); this
  eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`. Runtime ≈ 15 s (release).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf5_1_montecarlo_gate -- --nocapture   # prints recorded numbers
  cargo run  --release -p viz --bin gen_montecarlo                                  # → the figure
  ```
- **Determinism:** seeded `splitmix64` PRNG; the Wolff add-probability `p = 1 − e^{−2/T_c}` is computed once
  (no per-flip transcendental), so a run is reproducible for a given seed (same machine bit-identical;
  cross-machine the exponents agree to well within tolerance). No wall-clock.
- **Method:** single-cluster **Wolff** (add aligned neighbours w.p. `p`, flip cluster) — a generic
  critical-dynamics move with no exact-solution content. Observables `⟨|m|⟩`, `χ = N⟨m²⟩`; exponent ratios
  from `kinematics::power_law_fit` (`γ/ν` ← `χ` vs `L`, `β/ν` ← `⟨|m|⟩` vs `L`).
  - 2-D: `T_c = 2/ln(1+√2)`, `L ∈ {8,16,32,64}`, seed `7+L`, warmup 4000 + 40000 measured clusters.
  - 3-D: `T_c = 4.511536`, `L ∈ {12,16,24,32}`, seed `101+L`, warmup 6000 + 60000 clusters.
  - β, γ via class `ν` (2-D `ν=1`, 3-D `ν=0.6301`).
- **Data files:** `data/fss_2d.csv`, `data/fss_3d.csv` — per `L`: `⟨|m|⟩`, `χ`; `data/exponents.csv` — per
  model: `γ/ν`, `β/ν` (+ class targets), derived `β`, `γ`, and the real-material comparison string.
