# Provenance — 0304 Warp-3.4: the four-source null

- **Registered (R1, pre-run):** commit `530a325`. **Run-for-record:** commit `2f81902` (gate + data); this
  eval + provenance land in the following commit.
- **Toolchain:** `rustc 1.94.1 (e408947bf 2026-03-25)`.
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test uf3_4_four_source_null_gate -- --nocapture   # prints recorded numbers
  cargo run  --release -p viz     --bin gen_null                                          # → the figure
  ```
- **Determinism:** pure f64, closed-form plane-wave superposition (no wall-clock, no RNG). Grid `N=24`,
  spacing 1, wavelength `λ=8` (`k=2π/λ`, domain = 3λ). Each wave is `Ê e^{i(k·x+φ)}` with `B̂ = k̂ × Ê`;
  time-averaged energy `⟨ρ⟩ = ½·(em_energy(Ê_re,B̂_re) + em_energy(Ê_im,B̂_im)) = ¼(|Ê|²+|B̂|²)`
  (`kinematics::em_energy`). Central cube = `±λ/4` about the domain center (side `λ/2`). Phase sweep over
  `(pa, 0.7·pa, 1.9·pa)` for `pa ∈ [0,2π]` in 8 steps.
- **Data files:** `data/null_configs.csv` — per config (single / standing_1pol / orthogonal_3pair /
  parallel_antiphase): cube residual, center `⟨ρ⟩`, domain mean, `CoV`, max/min `⟨ρ⟩`; `data/phase_sweep.csv`
  — center `⟨ρ⟩` vs pair phase for the orthogonal set (flat = phase-independent); `data/radial.csv` — `⟨ρ⟩`
  along the body diagonal from center for the orthogonal and standing configs (flat = no null).
