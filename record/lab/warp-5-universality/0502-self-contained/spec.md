# 0502 — Warp-5.2: the complete, self-contained prediction — locate T_c and measure ν, blind

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_2_selfcontained_gate.rs` · **Status:** registered (pre-run)

## Goal (one paragraph)

Rung 5.1 predicted a real material's exponents, but it *supplied* two inputs: the critical temperature `T_c`
and the exponent `ν` (used to convert the ratios to `β, γ`). This rung removes both, closing the loop. The
**Binder cumulant** `U = 1 − ⟨m⁴⟩/3⟨m²⟩²` is dimensionless and size-independent *at criticality*, so the
`U_L(T)` curves for different `L` **cross** exactly at `T_c` — locating it with **no exact input** — and its
slope there scales as `dU/dT|_{T_c} ∼ L^{1/ν}`, **measuring `ν`** blind. Then `β` and `γ` follow from the FSS
of `⟨|m|⟩` and `χ` at the *located* `T_c`, times the *measured* `ν`. The toy outputs `T_c, ν, β, γ` (and the
universal Binder value `U*`) end-to-end, nothing handed to it — validated here on 2-D Ising, where every
number has an exact truth to check against.

## Firewall (R3)

`Binder cumulant, T_c, ν` name a seeded, deterministic Wolff simulation of a **toy** Ising model and universal
quantities extracted from it. Universality-class membership shared with real materials — not a claim the
warp/DEC engine is a magnet, no spacetime claim. Only the model (couplings, dimension) is input; `T_c`, `ν`,
`β`, `γ`, `U*` are all **outputs**. Dimensionless.

## Predictions (registered before the run)

- **P0 (the Binder curves cross — a universal `U*`):** the `U_L(T)` curves for different `L` share a crossing,
  with a universal value `U* ≈ 0.61` (2-D Ising) — *gate:* a crossing exists and `U* ∈ [0.55, 0.66]`.
- **P1 (locate `T_c` blind):** the crossing locates the critical temperature — *gate:*
  `|T_c − 2/ln(1+√2)| / T_c < 0.6%` (no exact `T_c` supplied).
- **P2 (measure `ν` blind):** the Binder slope scales as `L^{1/ν}`, giving `ν = 1` — *gate:* `|ν − 1| < 0.09`.
- **P3 (the full exponents, self-contained):** at the *located* `T_c`, with the *measured* `ν`,
  `β = (β/ν)·ν = 0.125` and `γ = (γ/ν)·ν = 1.75` — *gate:* `|β − 0.125|/0.125 < 0.07` **and**
  `|γ − 1.75|/1.75 < 0.09`. Nothing supplied but the model.

## Method (sketch)

Seeded Wolff, 2-D Ising, `L ∈ {8,16,24,32}`, temperature grid `T ∈ [2.25, 2.29]` (9 points), warmup 5000 +
80000 measured clusters per `(L,T)`. Per point: `⟨m²⟩, ⟨m⁴⟩ → U`, `⟨|m|⟩`, `χ = N⟨m²⟩`. **`T_c`** = mean of
the adjacent-`L` `U`-curve crossings (linear interpolation). **`ν`** from `power_law_fit(L, |dU/dT|)` where
`dU/dT` is the per-`L` linear-fit slope of `U(T)`. **`β/ν, γ/ν`** from `power_law_fit(L, ·)` of `⟨|m|⟩`, `χ`
interpolated to the located `T_c`; `β = (β/ν)ν`, `γ = (γ/ν)ν`. Emit `data/binder.csv` (L, T, U), `data/fss.csv`
(L, |m|, χ at T_c), `data/results.csv` (T_c, ν, β, γ, U* vs exact).

## What would falsify this

If the `U_L(T)` curves did not cross (P0), the Binder method fails. If the crossing missed `T_c` (P1), or the
slope FSS missed `ν = 1` (P2), or the self-contained `β, γ` missed the exact 2-D values (P3), the blind
pipeline would be untrustworthy. The `ν` estimate is the noisiest (fourth moments + finite `L`); a few-percent
residual is expected and reported, not hidden (R5).
