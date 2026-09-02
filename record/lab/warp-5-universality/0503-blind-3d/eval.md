# 0503 — Warp-5.3: the full-blind 3-D composition — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf5_3_blind3d_gate` (green: yes, 106 s) · **Commit:** `8fd47f3` (registered `918cb3b`)

## Result

**Chapter 5 closes: `T_c`, `U*`, `γ/ν`, `β/ν` of an unsolved model, end-to-end, blind.** The fully-blind
Binder pipeline (rung 5.2), run on the 3-D Ising model (rung 5.1) — which has **no closed-form solution** —
with nothing supplied but the model. Literature values were used only as *post-hoc checks*, never as inputs.

| quantity | measured (blind) | literature | pass |
|---|---|---|---|
| P0 located 3-D `T_c` | **4.50988** | 4.51152 (**0.036%**) | ✅ |
| P1 universal Binder value `U*` | **0.4844** | ≈ 0.465 | ✅ |
| P2 `γ/ν` at located `T_c` | **2.027** | 1.963 (3.3%) | ✅ |
| P2 `β/ν` at located `T_c` | **0.486** | 0.518 (6.3%) | ✅ |
| P3 Binder-slope `ν` | **0.766** | 0.630 — **high, as pre-registered** | ✅ |

The crossing of seven adjacent-`L` Binder pairs pinned the 3-D critical temperature to four parts in 10⁴ —
for a model nobody can solve on paper, with no exact input. The exponent ratios at that *located* `T_c` land
in the 3-D-Ising class (the one measured at the real liquid–gas critical point and in uniaxial magnets).
Incremental-magnetization Wolff (a cluster flip changes `M` by `−2·old·size`) made the `L=32` temperature
scans tractable. Data: [`data/binder3d.csv`](data/binder3d.csv), [`data/fss3d.csv`](data/fss3d.csv),
[`data/results.csv`](data/results.csv). Figure: the Binder-crossing mechanism is rendered in
[rung 5.2's figure](../0502-self-contained/figures/selfcontained.html); a dedicated 3-D figure is on the menu.

## The honest boundary (R5) — pre-registered, then observed

The Binder-slope `ν = 0.766` lands **high** of the class value 0.630, in the registered direction and
interval. Three independent probes (linear-slope, narrow-window, quadratic-derivative estimators; `L` up to
32; up to 150k clusters) all landed `ν ∈ [0.70, 0.77]` — this is a **systematic**, not noise: the known
`ω ≈ 0.83` corrections-to-scaling of the 3-D Ising class at small sizes. The fix is **larger lattices** (and
a correction term in the fit), i.e. compute — not a different method. Registering the bias direction *before*
the run, and having the run confirm it, is the bench reporting its own resolution limit honestly.

## What it rules in / out

- **Closes the chapter-5 arc.** 5.0 validated the FSS machinery (solvable model); 5.1 predicted the unsolved
  3-D exponent ratios (with `T_c`, `ν` supplied); 5.2 made the pipeline self-contained (2-D); 5.3 composes
  them: **the unsolved model, fully blind**. The graduation criterion of `PREDICTIONS.md` is met for the
  Ising class with every critical number an output.
- **Rules in the bench's self-knowledge:** it states what it can resolve at this compute scale (`T_c` to
  0.04%, ratios to a few %, `U*` to ~4%) and what it cannot (`ν` beyond ~15% at `L ≤ 32`) — and the
  limitation was *predicted*, not discovered post-hoc.
- **Firewall intact:** universality-class membership of a **toy** 3-D Ising model. Not a claim the warp/DEC
  engine is a magnet; no spacetime claim.

## Deferred / next

Larger-`L` 3-D runs with an explicit `(1 + c·L^{−ω})` correction term to bring `ν` in (compute-bound); a
dedicated 3-D Binder figure; a **data-collapse** capstone figure; and pointing the now-proven pipeline at a
model whose class is *genuinely debated* — a live prediction with no literature check at all.
