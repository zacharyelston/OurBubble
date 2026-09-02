# 0510 — reprocessing 5.6's SITE `d_f` negative: evaluation

**Verdict:** **CONFIRMED — H-DISSOLVE, ordering-robust (P0–P4, all 16 gated predictions green)** ·
**Gate:** `uf5_10_site_locator_reprocess_gate` (green: yes, no negative lock needed) · **Commits:**
probe breadcrumb `d9c154f` · registered `2e6134d` (R1: spec + gate, before any run) · run-for-record
`4334cff` · **Runtime:** 27.1 s (tier 2) · **Closes** issue #306; **answers** issue #305.

## Result

**Rung 5.6's site `d_f` negative dissolves too — and the sharper finding is that it was inside an
error bar 5.6 could have drawn from numbers it already published.**

Two statements, in increasing order of force:

1. **With the newer locator.** 5.8's crossing-drift estimator moves the stella-site threshold from
   5.6's `0.174453` to `0.174911 ± 0.000514` (the fit's own OLS intercept standard error), and `d_f`
   there rises from `2.43782` to **`2.49050 ± 0.02197`** — **inside 5.6's own registered `± 0.06`
   band**, closing 62% of its `0.08513` miss, `0.52σ` from the class value on the propagated band.
2. **Without any new estimator at all (P2d).** 5.6's **own published** replica error (`± 0.000410`),
   propagated through the amplification **5.6 itself measured** (`116.7`), is `± 0.0478` — about
   **80%** of the `± 0.06` band it registered. Add `d_f`'s own statistical error and the class value
   sits inside at `z = 1.69` **at 5.6's own threshold**. The registered band was narrower than the
   uncertainty the rung's own two numbers already implied.

And the verdict is **ordering-robust**, which is what 5.9 could not claim: every candidate locator
dissolves.

| locator | `p` | `d_f` | its quoted loc. error | propagated band | \|Δ vs class\| | `z` |
|---|---|---|---|---|---|---|
| 5.6's own located `p_c` | 0.174453 | 2.43793 | ±0.000410 | ±0.0504 | 0.0850 | **1.69** |
| per-batch extrapolated | 0.174369 | 2.42851 | ±0.000446 | ±0.0546 | 0.0944 | **1.73** |
| aggregate extrapolated (5.8) | 0.174911 | 2.49050 | ±0.000514 | ±0.0623 | 0.0325 | **0.52** |

| prediction | quantity | measured | registered | pass |
|---|---|---|---|---|
| P0a | per-batch naive mean/σ vs 5.6's committed, 3 families | tri 0.500986/0.001348 · fcc 0.199457/0.000296 · st 0.174453/0.000410 | 5.6's committed values (±1e-6) | ✅ |
| P0b | `d_f` at 5.6's two quoted thresholds | 2.43793 \| 2.52498 | 2.43782 \| 2.52498 (±1e-3) | ✅ |
| **P0c** | **`d_f` (triangular) at the EXACT `1/2`** | **1.89613 ± 0.00722** | 91/48 = 1.8958333 exact (±0.02) | ✅ |
| P0d | `d_f` (FCC-site) at the PUBLISHED threshold | 2.50814 ± 0.01334 | 2.52295 (±0.05) | ✅ |
| P1a | `p̂_c` (stella, aggregate, w=2) | 0.174911 | 0.174911 (±1e-5), above 0.174453 | ✅ |
| P1b | OLS se (stella) \| `r²` tri/fcc/stella | 0.000514 \| 0.2424/0.4050/0.1758 | se ∈ [3e-4, 8e-4]; all `r² < 0.50` | ✅ |
| **P1c** | key error in units of (se \| `w`-spread) | tri **0.81 \| 5.28** · fcc **0.55 \| 2.25** | `< 1.5` and `> 2` on BOTH keys | ✅ |
| P2a | local `∂d_f/∂p` \| 5.6's secant | 113.4 \| 116.7 | both ∈ [80, 150] | ✅ |
| P2b | ordering systematic (stella) | 0.000542 | [3e-4, 9e-4], aggregate higher | ✅ |
| **P2c** | **ordering licence on BOTH site keys** | tri **7.66e-4 vs 2.53e-3** · fcc **7.9e-5 vs 3.88e-4** | per-batch closer on both (opposite to 5.9's bond key) | ✅ |
| **P2d** | propagated band \| 5.6's own σ propagated | 0.0623 \| **0.0478** | band ∈ [0.045, 0.09]; 5.6's own > 0.70 × 0.06 | ✅ |
| P3a | `d_f` at the 5.8 locator | 2.49050 | 2.49050 (±0.01) | ✅ |
| P3b | \|`d_f` − class\| vs 5.6's miss | 0.0325 vs 0.08513 | `< 0.5 ×` 5.6's miss, upward | ✅ |
| **P3c** | **`z` at ALL THREE locators** | **1.69 \| 1.73 \| 0.52** | all `< 2` ⇒ **H-DISSOLVE** | ✅ |
| **P4a** | inversion (triangular) vs the **EXACT** `1/2` | **−2.92e-5** | ±2e-4 | ✅ |
| P4b | inversion (FCC-site) vs the published key | +1.49e-4 | ±3e-4 | ✅ |
| — | (report-only) `d_f` at the per-batch locator | 2.42851 | — | — |
| — | (report-only) inversion (stella) vs 5.6's pre-registered constant | 0.175197 vs 0.1752 | — (not independent) | — |
| — | (report-only) naive vs extrapolated accuracy on the keys | tri 2.23e-4 vs 2.53e-3 · fcc 4.8e-5 vs 3.88e-4 | — (naive closer on both) | — |

Data: [`data/`](data) · probe breadcrumb: [`data/probe_log.txt`](data/probe_log.txt) · figure (R10):
[`figures/site_locator.html`](figures/site_locator.html) (`core/viz gen_site_locator`, rendered from
this entry's `data/*.csv` only).

## The control that settles it — an exactly known threshold and an exactly known exponent (P0c)

This is the arm most able to have killed the rung, and 2-D site percolation is the one place where
nothing is approximate: `p_c = 1/2` **exactly** (Sykes–Essam 1964; rigorous Kesten 1980/82) and
`d_f = 91/48` **exactly** (den Nijs 1979 / SLE₆). Measuring the exponent *at* the exact threshold
removes the locator with **no literature uncertainty at either end**:

> `d_f(triangular, p = 1/2) = 1.89613 ± 0.00722` against `91/48 = 1.8958333` — a gap of
> **`3.0e-4`, or `0.04` of one statistical σ.**

Nothing is wrong with how the exponent is measured. And moving the threshold by `±0.005` swings the
answer from `1.834` to `1.937`: at these sizes `d_f` is not really testing class membership, it is
**reading back the threshold it was given**. Which is also why it inverts so well (P4a): anchoring on
the exact exponent recovers the exact threshold to `−2.9e-5`.

## #305, answered — and not the way 5.9 guessed (P2c)

5.9 found that "extrapolate the pair crossings" is two inequivalent estimators (average the batch
curves and fit once, vs fit each batch and average the intercepts), that the two differ by more than
the systematic 5.8 was built to remove, and that **the two orderings gave opposite verdicts** on
5.7's negative. It picked the aggregate ordering because its single answer key (FCC-bond) preferred
it, and registered that as a stated plank. Site percolation has two keys, one exact:

| key | aggregate-then-extrapolate | extrapolate-then-average | closer |
|---|---|---|---|
| triangular site (**EXACT** `1/2`) | 2.530e-3 | 7.66e-4 | **per-batch** (3.3×) |
| FCC site (published) | 3.88e-4 | 7.9e-5 | **per-batch** (4.9×) |
| FCC **bond** (rung 5.9's record) | 3.60e-4 | 5.88e-4 | *aggregate* |

**The licence does not generalise.** On both site keys — including the exact one — the per-batch
ordering is 3–5× more accurate; on the bond key the aggregate ordering won. So #305's honest answer is
**there is no universal right ordering: it must be registered per rung, and both arms reported**.
5.9's plank is hereby narrowed to exactly what its one key supported, and this is why P3c here was
designed to be evaluated at *all three* locators — so that this rung's verdict does not inherit the
ambiguity. (It does not: all three dissolve.)

## What it rules in / out

- **In (the rung's own question):** 5.6's `d_f` miss was **the locator's error, unpropagated** — not
  the lattice, and not a class exclusion. Three independent legs: the miss shrinks 2.6× at a
  better-centred locator; the class value is inside the propagated band at *every* candidate locator
  including 5.6's own; and with the locator removed entirely against an **exact** answer the machinery
  lands within `0.04σ`.
- **In (the resolution statement, pre-registered as P2d):** at `L ≤ 48`, a crossing-located threshold
  of this precision cannot resolve 3-D percolation class membership in `d_f` better than about
  `± 0.05–0.06`. That is the measured product of the locator's real error and the measured
  amplification — so "inside the band" means *consistent with*, never *confirms*.
- **In (the cross-rung mechanism, report-only but the most transferable result):** the amplification
  is not a constant of percolation. Measured: 2-D site `10.3` · 3-D site `99.4` (FCC) / `113.4`
  (stella) · 3-D bond `275.7` / `340.1` (5.9's record). It grows with dimension and again with the
  dilution rule — roughly `bond ≈ 3 × site` and `site ≈ 10 × 2-D` — so it must be re-measured per
  variant (5.7's lesson, now quantified across five lattice/rule combinations). Any exponent quoted at
  a *located* critical point needs this number attached.
- **In (a licensed by-product, P4a/P4b):** the inverted locator now has an **exact** test. Anchoring
  `d_f` at the class value and dividing by the measured sensitivity recovers the exact triangular
  threshold to `−2.9e-5` and the published FCC-site threshold to `+1.49e-4` (the latter residual being
  the finite-size `d_f` bias `0.0148` over the sensitivity `99.4`, identically). **Bucket honesty:**
  it consumes the class exponent as an input, so it is 🔵 and can never be 🟢 prediction-grade.
- **Out:** the reading that 5.6's registered `± 0.06` was a fair band for an exponent measured at a
  threshold it had located to `± 0.00041` (P2d), and 5.9's reading that the aggregate ordering is
  universally licensed (P2c).
- **Not claimed:** that `d_f(stella-site)` is *confirmed* to be `2.52295`; that the threshold is
  re-quoted; or that the newer estimator is more *accurate* — see the caveats.

## Caveats (stated, not hidden)

- **The extrapolation is still not demonstrably more accurate.** On all three answer keys in this
  chapter the plain **naive mean** of the pair crossings is closer than the extrapolated intercept
  (triangular `2.23e-4` vs `2.53e-3`; FCC-site excl-smallest `4.8e-5` vs `3.88e-4`; and 5.9 found the
  same for FCC-bond). What the extrapolation contributes is a **quantified error bar** that survives
  contact with an answer key — not accuracy. Anyone reading 5.8's "collapsed" claim as accuracy should
  read this row instead.
- **P0d's direction is opposite to 5.6's registration.** At the *published* FCC-site threshold `d_f`
  comes out `0.0148` **low**, where 5.6 pre-registered corrections-to-scaling making it **high**
  (its spec's "pre-registered systematics"). In band, but the sign is wrong, and it matters: 5.6's own
  FCC value at its *located* threshold (`2.52727`) looked closer to the class value than the value at
  the *published* one does — because its located threshold sat `2.2e-4` high and `2.2e-4 × 99.4 ≈
  0.022` pushed it up. 5.6's FCC "agreement" was therefore partly a cancellation of two errors. This
  weakens nothing in the dissolve argument (which rests on the exact 2-D control), but the 3-D
  finite-size `d_f` bias at `L ≤ 48` is real, is ~`0.015`, and is **not** in the band this rung
  propagates. Folding it in would widen the band and strengthen the dissolve, so it is left out as the
  conservative choice — and named here so nobody has to rediscover it.
- **The threshold is not re-quoted.** `0.174911 ± 0.000514` is a methodology cross-check on one
  committed curve; 5.6's `0.17445 ± 0.00041` remains the chapter's headline constant. The two agree
  within ~1σ (unlike the bond case in 5.9, where they did not).
- **`z ≈ 1.7` at two of the three locators is not a comfortable margin** with only 4–5 crossing pairs
  (the standard error has 2–3 degrees of freedom and heavy tails). `z < 2` was registered, not `z < 1`,
  for exactly that reason, and "dissolves" here means *the miss is not statistically significant*,
  not *the exponent is confirmed*.
- **`d_f`'s own statistical error is small** (`±0.020` stella, `±0.007` triangular): the bands are
  85–95% locator error. More sampling at fixed `L` cannot help; only a better threshold or larger `L`
  can.
- No 2-D/3-D graph-identity walk in this rung (5.6's own P2a proved the stella graph is the mesh's
  `d0` adjacency at 365 interior vertices, and the graph is unchanged).

## The marked upgrade to 5.6 (not a retraction)

5.6's registered scope-statement **stands verbatim**: its windows, its sizes, its three thresholds,
its locked miss and its diagnosis arm all held, and this rung reproduces its committed numbers to the
paper trail's own resolution (P0a: all three families' batch estimates at six decimals; P0b: both of
its quoted `d_f` values). What changes is the *interpretation*: 5.6 read the miss as a resolution
statement about needing a tighter `p_c`; with the locator's error now quantified it reads as a miss
that was **never statistically significant to begin with**. That upgrade is written into
[`../0506-stella-percolation/eval.md`](../0506-stella-percolation/eval.md) as a dated, marked note
with a cross-reference — never silently — and 5.6's `PREDICTIONS.md` row carries the same pointer.

One detail worth recording because it explains 5.6's own diagnosis: the `d_f`-anchored inversion on
stella-site lands at `0.175197`, within `3e-6` of 5.6's **pre-registered constant** `0.1752`. That is
*not* independent evidence — it is algebraically 5.6's diagnosis arm restated — but it does explain
*why* that arm recovered the class value so precisely: 5.6's pre-registered constant was, unknowingly,
the `d_f`-anchored threshold.

## Deferred / next (fed back into the chapter menu)

- **`ν` from the crossing slope** (`dR/dp|_{p_c} ~ L^{1/ν}`, on the menu since 5.6, still open, and
  now the highest-value item in the thread): it would make the band **self-consistent**. Every band in
  5.9 and 5.10 uses an amplification measured by finite difference and a class exponent taken from
  literature; a measured `ν` closes that loop and would let `∂d_f/∂p ~ L^{1/ν}` be *predicted* rather
  than measured per variant.
- **The `L` ladder** (5.7's deferred item, twice-motivated now): `L` up to ~96–128 at a fixed locator,
  to watch the amplification shrink as `L^{1/ν}` predicts. This rung makes it a sharp test — the
  expected size is now measured across five lattice/rule combinations.
- **Fold the finite-size `d_f` bias into the band.** P0d measured it (~`0.015` at `L ≤ 48` in 3-D,
  direction opposite to 5.6's registration). A band that includes it is the honest one; it was left out
  here as the conservative choice.
- **Register the aggregation order in `kinematics`.** #305's answer is "declare it per rung", which
  means the tool should stop letting it be implicit: `crossing_extrapolate` could take the replica
  structure explicitly rather than a pre-averaged sequence, so the choice appears in the call.
- **A genuine two-window comparison for site** (5.8's own deferred item, still open): needs new MC.
