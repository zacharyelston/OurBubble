# 0503 — Warp-5.3: the full-blind 3-D composition — T_c, U*, and the exponents of an unsolved model, end-to-end

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_3_blind3d_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

The closing composition: run the fully-blind Binder pipeline (rung 5.2) on the **3-D Ising model** (rung 5.1)
— the model with **no closed-form solution** whose universality class is measured in real materials. Nothing
supplied but the model: the Binder crossing **locates the 3-D `T_c`**, the crossing height gives the
**universal 3-D `U*`**, and FSS at the located `T_c` gives the exponent ratios `γ/ν`, `β/ν`. The Binder-slope
`ν` is also measured — and pre-registered as **corrections-limited**: probing (not run-for-record) shows the
`L ≤ 32` slope estimator lands systematically high of the class value 0.630 (the known `ω ≈ 0.83`
corrections-to-scaling at small sizes). Stating that boundary is part of the result (R5): the bench reports
what it can and cannot resolve at this compute scale.

## Firewall (R3)

`Ising, Binder, T_c, exponent` name a seeded, deterministic Wolff simulation of a **toy** 3-D Ising model;
`T_c, U*, ν, β/ν, γ/ν` are **outputs**, only the model is input. Universality-class membership shared with
real materials (liquid–gas critical point, uniaxial magnets) — not a claim the warp/DEC engine is a magnet,
no spacetime claim. Literature values quoted only as *checks after the fact*, never as inputs.

## Predictions (registered before the run)

- **P0 (locate the 3-D `T_c` blind):** adjacent-`L` Binder crossings exist and locate the critical
  temperature — *gate:* `|T_c − 4.51152|/4.51152 < 0.3%` (probes landed ≤ 0.06%).
- **P1 (the universal 3-D Binder value):** the crossing height gives the 3-D-Ising `U*` — *gate:*
  `U* ∈ [0.43, 0.50]` (literature ≈ 0.465).
- **P2 (the exponent ratios of the unsolved model, at the located `T_c`):** `γ/ν` within 6% of 1.963 and
  `β/ν` within 10% of 0.518 — the 3-D-Ising class read off raw data with a *located*, not supplied, `T_c`.
- **P3 (the honest boundary — `ν` is corrections-limited at `L ≤ 32`):** the Binder-slope `ν` lands **high**
  of 0.630, inside `[0.63, 0.80]` — the documented small-size systematic (`ω ≈ 0.83`), reported as the
  method's stated resolution limit, not hidden — *gate:* `ν` in that interval **and** `ν > 0.630` (the
  registered bias direction).

## Method (sketch)

Seeded Wolff with **incremental magnetization** (a cluster flip changes `M` by `−2·old·size` — no full-lattice
sum per step), 3-D Ising, `L ∈ {12,16,24,32}`, `T ∈ [4.49, 4.53]` step 0.005 (9 points), warmup 8000 + 50000
measured clusters per `(L,T)`. Per point: `U = 1 − ⟨m⁴⟩/3⟨m²⟩²`, `⟨|m|⟩`, `χ = N⟨m²⟩`. **`T_c`** = mean of
adjacent-`L` `U`-crossings. Per-`L` **quadratic fits** in `T` give `dU/dT|_{T_c}` (→ `ν` via
`power_law_fit(L, |dU/dT|)`) and `ln χ`, `ln⟨|m|⟩` at `T_c` (→ `γ/ν`, `β/ν` via `power_law_fit`). Emit
`data/binder3d.csv`, `data/fss3d.csv`, `data/results.csv` (each output vs the literature check).

## What would falsify this

No crossing, or a `T_c` off by >0.3% (P0), would break the blind-location claim. `U*` or the ratios outside
their windows (P1/P2) would put the lattice outside the 3-D-Ising class. `ν` landing *low* of 0.630 or beyond
0.80 (P3) would contradict the registered corrections systematic — meaning we don't understand our own
estimator. All recorded honestly (R5).
