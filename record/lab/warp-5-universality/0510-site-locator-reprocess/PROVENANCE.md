# Provenance — 0510 reprocessing 5.6's SITE `d_f` negative with 5.8's locator + 5.9's band

- **Commits:** probe breadcrumb `d9c154f` (`core/uniforge/examples/uf5_10_site_locator_probe.rs`) ·
  registered `2e6134d` (R1: `spec.md` + gate, **before** any run for record) · run-for-record
  `4334cff` (`data/`) · figure + docs in the landing commit of this entry.
  (`git -C UniForge rev-parse HEAD`)
- **Toolchain:** `rustc 1.97.1 (8bab26f4f 2026-07-14)`
- **Input (read-only, never modified):**
  `lab/warp-5-universality/0506-stella-percolation/data/rw_curves.csv` — the K=5-batch aggregate
  wrapping-probability curves for all three families, committed by rung 5.6. 5.6's gate and its
  `data/` are the immutable record; this rung reads them and writes only under `0510-*/`.
- **Answer keys (independent of anything in this repo):**
  - `p_c(triangular-site) = 1/2` **exactly** — Sykes & Essam, J. Math. Phys. **5**, 1117 (1964);
    rigorous: Kesten, Comm. Math. Phys. **74**, 41 (1980).
  - `d_f(2-D percolation) = 91/48` **exactly** — den Nijs, J. Phys. A **12**, 1857 (1979); SLE₆.
  - `p_c(FCC-site) = 0.1992365(10)` — Lorenz & Ziff, J. Stat. Phys. **98**, 961 (2000).
  - `d_f(3-D percolation) = 3 − β/ν = 2.52295(15)`, `β/ν = 0.47705(15)` — Wang, Zhou, Zhang, Garoni,
    Deng, Phys. Rev. E **87**, 052107 (2013).
  - Quoted, not recomputed: rung 5.9's committed bond sensitivities (`275.7` FCC-bond, `340.1`
    stella-bond) and its FCC-bond ordering errors (`3.60e-4` aggregate, `5.88e-4` per-batch), used in
    the cross-rung sensitivity table and the ordering-fork panel.
- **Regenerate:**
  ```bash
  cd core
  # the run for record (~27 s, tier 2) — prints the recorded scorecard and rewrites data/
  cargo test --release -p uniforge --test uf5_10_site_locator_reprocess_gate -- --nocapture
  # the probe breadcrumb (~24 s) — the wider ladder, the two-key calibration, the timings
  cargo run --release -p uniforge --example uf5_10_site_locator_probe
  # the figure, from the committed data/ only
  cargo run -p viz --bin gen_site_locator -- <commit-sha>
  ```
- **Determinism:** seeded splitmix64 throughout, all seeds compile-time constants echoed into
  `data/seeds.csv` (sweep base `0x5EED ⊕ k·2⁵⁰`, measurement base `0xABCD`, K=5 batches × R=300 sweep
  samples, R=2400 measurement samples, fixed 4-way thread striping so accumulation order is
  independent of core count). The measurement seeds do **not** depend on `p`, so two `p`-points are a
  paired comparison and every `∂d_f/∂p` finite difference is far quieter than two independent runs.
  The re-analysis arms are closed-form least squares on a committed CSV. Pure `f64`, no wall-clock, no
  unseeded RNG — the same numbers on every machine, every run.
- **Machinery provenance:** the percolation machinery in the gate (`Rng`, `Graph`, `triangular`,
  `fcc`, `stella`, `Uf`, `measure`, `sample`, `crossings_of`, `crossing_estimate`, `sweep_batch`, and
  the `measure_at` seed scheme) is **copied verbatim** from
  `core/uniforge/tests/uf5_6_stella_percolation_gate.rs` — a copy, never an import, so 5.6's gate
  stays untouched. Copy fidelity is gated: **P0a** reproduces 5.6's committed per-batch threshold
  estimates for **all three families** (`0.500986 ± 0.001348`, `0.199457 ± 0.000296`,
  `0.174453 ± 0.000410`) at all six committed decimals, and **P0b** reproduces **both** of its
  committed `d_f` values (`2.43793` vs `2.43782`, the `1.15e-4` residue being `113 ×` the 6-decimal
  rounding of the committed threshold; and `2.52498` vs `2.52498` to `7.2e-7`, since 5.6's
  pre-registered constant is exact in the paper trail). One deliberate difference: `measure` does not
  accumulate χ' or the log-s histogram, which no arm of this rung uses (R7 forbids a dead field); the
  RNG, the site draw order, the union-find and the `s_max` path are unchanged.
- **Tool provenance:** `kinematics::crossing_extrapolate` is rung 5.8's; `CrossingExtrapolation::
  p_c_stderr` is rung 5.9's addition. No `kinematics` change was needed by this rung.
- **Data files:**
  - `data/locator_ladder.csv` — `family,label,p,d_f,sigma_df,smax_a..smax_e`: every `d_f`
    measurement. Six points for stella-site across the candidate locators (5.6's located threshold,
    5.6's pre-registered constant, the per-batch-extrapolated locator, and the aggregate-extrapolated
    one with `±0.0006` for the paired sensitivity); three for triangular (the **exact** `1/2` and
    `±0.005` for its much gentler sensitivity); two for FCC-site (the published key and the
    extrapolated locator). `sigma_df` is the replica error over the 4 seed stripes (the 5.5 rule);
    `smax_e` is populated only for triangular, which has five FSS sizes.
  - `data/locator_estimates.csv` — `family,kind,estimator,p_c_or_width,error_bar,r2,err_vs_key`.
    `kind` separates a **threshold** estimate (where a distance to an answer key is meaningful) from
    an **error_bar_candidate** — a width, which must never be compared to a threshold (the 5.9
    lesson). Five threshold estimators per family plus the exact/published keys and the
    `d_f`-anchored inversions; four width candidates per family (OLS intercept se, the `w`-scan
    spread, the per-batch replica σ, and the aggregate fit's *actual* error against its key), plus
    the ordering systematic and 5.6's own σ propagated through its own sensitivity.
  - `data/verdict_by_locator.csv` — `locator,p,d_f,loc_err,band,abs_delta,z,dissolves`: P3c's
    ordering-robust verdict, one row per candidate locator, each with its own quoted error. This is
    the figure's money-panel source.
  - `data/sensitivity_table.csv` — `dimension,dilution,lattice,sensitivity,source`: the cross-rung
    amplification table (2-D site · 3-D site · 3-D bond), with 5.9's bond rows marked as quoted from
    its committed record rather than re-measured here.
  - `data/crossing_pairs.csv` — `family,l_eff,p_star`: the consecutive-size pair crossings per family
    (5 for triangular, 4 for each 3-D family), recomputed read-only from 5.6's aggregate curve, at
    `L_eff = √(L_a·L_b)`.
  - `data/w_scan.csv` — `family,w,p_c`: the extrapolated threshold across `w ∈ [1.0, 2.6]`,
    report-only; the quantity P1c shows is *not* the locator's error bar.
  - `data/verdict.csv` — `prediction,quantity,measured,registered,pass`: the registered scorecard,
    sixteen gated rows plus three report-only rows. Ranges are written `[lo..hi]` and lists with `|`,
    never with a comma inside a comma-delimited field (`lab/LESSONS.md`, 7.2 / 5.9).
  - `data/seeds.csv` — every seed, count, window and step, plus the read-only input path.
  - `data/probe_log.txt` — the committed probe's full stdout (the breadcrumb): the two-key error-bar
    calibration, the ordering-fork discovery, the wider `d_f` ladder, the exact-key control and the
    per-stage timings that set the gate's budget.
- **Figure (R10):** `figures/site_locator.html`, generated from the committed `data/` only —
  `core/viz/src/bin/gen_site_locator.rs` + `core/viz/assets/site_locator_template.html`, with a
  self-containment unit test in `core/viz/src/lib.rs` (placeholders replaced, no `http(s)`/CDN, data
  and commit injected, firewall block and all four answer keys named). Every CSV reader in the
  generator asserts its expected field count per row — the 5.9 lesson, mechanised. Verified by
  rendering the page headless and reading every panel back.
