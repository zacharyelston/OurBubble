# 0509 — reprocessing 5.7's `d_f` negative with 5.8's locator: evaluation

**Verdict:** **CONFIRMED — H-DISSOLVE (P0–P4, all 14 gated predictions green)** · **Gate:**
`uf5_9_bond_locator_reprocess_gate` (green: yes, no negative lock needed) · **Commits:** probe
breadcrumb `4b58bae` · registered `90886a1` (R1: spec + gate, before any run) · run-for-record
`8831c45` · **Runtime:** 51.3 s (tier 2)

## Result

**Rung 5.7's registered `d_f` negative dissolves into the locator.** Applying rung 5.8's
crossing-drift estimator to 5.7's committed bond curves moves the stella-bond threshold from 5.7's
naive `0.099641` up to **`0.100648 ± 0.000518`** (the fit's own OLS intercept standard error), and
`d_f` measured there rises from 5.7's `2.02762` to **`2.37985 ± 0.01076`** — closing **71%** of
5.7's registered `0.49533` miss and finishing **`0.81σ`** from the 3-D percolation-class value
`2.52295` once the locator's error is propagated through the *measured* local sensitivity
(`∂d_f/∂p = 340.1`, band `±0.1766`). The registered H-DISSOLVE branch (spec.md P3c) is the outcome;
the H-CERTIFY branch, written down in the same commit, is not.

The decisive control is the one 5.7 ran only in prose and this rung gates: at the **published**
FCC-bond threshold — zero location error — the same code returns `d_f = 2.51943 ± 0.01323` against
the class `2.52295`, a gap of `0.0035`, about a quarter of one statistical σ and **141×** smaller
than 5.7's miss. The finite-size machinery was never the problem.

| prediction | quantity | measured | registered | pass |
|---|---|---|---|---|
| P0a | stella per-batch naive mean / σ (5.7 copy fidelity) | 0.099641 / 0.000312 | 0.099641 / 0.000312 (±1e-6) | ✅ |
| P0b | `d_f` at 5.7's located `p_c` | 2.02746 | 2.02762 (±0.001) | ✅ |
| **P0c** | **`d_f` (FCC) at the PUBLISHED threshold** | **2.51943 ± 0.01323** | 2.52295 (±0.05) | ✅ |
| P1a | `p̂_c` (stella, aggregate-extrapolated, w=2) | 0.100648 | 0.100648 (±1e-5), above 0.099641 | ✅ |
| P1b | OLS intercept se / `r²` stella / `r²` FCC | 0.000518 / 0.0022 / 0.1527 | se ∈ [3e-4, 8e-4]; both `r² < 0.30` | ✅ |
| **P1c** | FCC key error in units of (se \| `w`-spread) | **1.10 / 6.09** | `< 2.5` and `> 3` | ✅ |
| P2a | local `∂d_f/∂p` at the new locator | 340.1 | [250, 450] | ✅ |
| **P2b** | ordering systematic (aggregate vs per-batch) | **0.001330** | [8e-4, 2e-3], aggregate higher | ✅ |
| P2c | FCC key error, aggregate vs per-batch | 0.000360 vs 0.000588 | aggregate closer | ✅ |
| P2d | propagated 1σ band in `d_f` | 0.1766 | [0.10, 0.30] | ✅ |
| P3a | `d_f` at the 5.8 locator | 2.37985 ± 0.01076 | 2.37985 (±0.01) | ✅ |
| P3b | \|`d_f` − class\| vs 5.7's miss | 0.1431 vs 0.49533 | `< 0.5 ×` 5.7's miss, upward | ✅ |
| **P3c** | **`z` = \|`d_f` − class\| / band** | **0.81** | `< 2` ⇒ **H-DISSOLVE** | ✅ |
| P4a | `d_f`-anchored inversion (FCC) vs the published key | +0.0000128 | ±5e-5 | ✅ |
| — | (report-only) `d_f` at the per-batch-extrapolated locator | 1.91924 | — | — |
| — | (report-only) `p_c(d_f`-anchored, stella) — derived, = P3c in `p`-space | 0.101069 | — | — |
| — | (report-only) FCC aggregate-*naive* error vs the key | 0.000201 | vs extrapolated 0.000360 | — |

Data: [`data/`](data) · probe breadcrumb log: [`data/probe_log.txt`](data/probe_log.txt) · figure
(R10): [`figures/bond_locator.html`](figures/bond_locator.html) (`core/viz gen_bond_locator`,
rendered from this entry's `data/*.csv` only).

## The honest crux — three mistakes found in the estimator's own record

The owner's framing for this rung was *"reprocess a simple failed one and look for mistakes."* The
verdict above is the reprocessing; these are the mistakes, all now gated rather than narrated.

**1. A `w`-scan spread is not the locator's error bar (P1c).** Rung 5.8's headline evidence that it
had "collapsed" 5.6's window systematic was the spread of the extrapolated `p_c` across
`w ∈ [1.6, 2.4]` — `4e-5` to `5e-4` on 5.6's data. On the one **bond** lattice with a published
answer key, that yardstick can be checked: the FCC-bond fit's *actual* distance from
`0.1201635` is `3.60e-4`, which is `1.10×` the fit's OLS intercept standard error (covered, as an
error bar should be) but `6.09×` its `w`-spread. A `w`-scan measures **fit-choice stability**;
accuracy is measured by the residual scatter about the fit. Quoting the former as the locator's
uncertainty understates the real error ~6-fold here. Fixed at the source, not just noted:
`kinematics::CrossingExtrapolation` now carries `p_c_stderr`, documented with this calibration and
covered by three unit tests — a hand-computed OLS case, the degenerate cases (`n = 2`, zero design
spread ⇒ `INFINITY`, so a caller propagating it gets an honestly unbounded band), and a
200-realization statistical test that the standard error tracks the true error while the `w`-spread
comes out systematically too small.

**2. Aggregate-then-extrapolate ≠ extrapolate-then-average, and nobody had registered which (P2b/P2c).**
5.7 committed only the K=5-batch **aggregate** wrapping curve, so applying 5.8's estimator has two
inequivalent orderings. They differ by **`1.330e-3`** on stella-bond: about **3.7×** the `3.6e-4`
window systematic 5.8 was built to remove, and 3.7× the per-batch replica `σ` itself. The mechanism
is 5.6's own: averaging the curves first suppresses the noise that manufactures spurious low-`p`
sign-changes, so the aggregate crossings sit higher. This matters because **the two orderings give
opposite verdicts** — the per-batch ordering lands `p̂_c = 0.099318`, where `d_f = 1.919`, and would
have *certified* 5.7's negative. It is therefore gated, not chosen: the published FCC-bond key
licenses the aggregate ordering (`3.60e-4` vs `5.88e-4`), which is also 5.8's own recipe, since 5.8
read 5.6's committed aggregate curve. Neither 5.6, 5.7 nor 5.8 states which ordering it used.

**3. On bond data the extrapolation is better-*centred*, not a better fit (P1b, and report-only).**
Registered up front rather than discovered by a reader: the drift is **not resolvable** in 5.7's bond
curves (`r² = 0.0022` stella, `0.1527` FCC — 5.6's site curves had a real drift; these do not, at
`R = 1500` per point). And on the one lattice with an answer key the plain aggregate **mean** of the
pair crossings is actually *closer* to the published threshold (`2.01e-4`) than the extrapolated
intercept (`3.60e-4`). So the case for the extrapolation here is not accuracy — it is that the
intercept is centred where `d_f` agrees with the class **and** that it carries an error bar that
survives contact with an answer key. Anyone reading 5.8's "collapsed" claim as "more accurate"
should read this row instead.

## What it rules in / out

- **In (the rung's own question):** 5.7's `d_f` miss was **our estimator**, not the lattice. The
  evidence is three-fold and independent: the miss shrinks 3.5× at a better-centred locator; the
  residual `0.1431` is `0.81σ` of the locator-propagated band; and at a *published* threshold with
  the locator removed entirely the same code returns the class value to `0.0035`.
- **In (the resolution statement, pre-registered as P2d):** at any crossing-located threshold of
  this precision, `d_f` **cannot** resolve 3-D-percolation class membership better than `±0.18` at
  `L ≤ 48`. That band is not a concession — it is the measured product of the locator's real error
  and the measured `∂d_f/∂p = 340`, and it is why "in band" here means *consistent with*, never
  *confirms*. `d_f` at these sizes is a thermometer for the locator, not a class test.
- **In (a licensed by-product, P4a):** invert the thermometer. Anchoring `d_f` at the class value and
  dividing by the measured sensitivity recovers the **published** FCC-bond threshold to `+1.28e-5`
  — ~15× tighter than the best crossing estimator on the same curves — and the residual is exactly
  the finite-size `d_f` bias (`0.0035`) over the sensitivity (`276`). Applied to stella-bond it gives
  `0.101069`. **Bucket honesty:** it consumes the literature class exponent as an input, so it is a
  🔵 method cross-check and can never be 🟢 prediction-grade; spec.md said so before the run.
- **Out:** the reading that a `w`-scan spread bounds a crossing-drift locator's error (mistake 1),
  and the reading that "extrapolate the crossings" is a single well-defined estimator (mistake 2).
- **Not claimed:** that `d_f(stella-bond)` is *confirmed* to be `2.52295`. The band is far too wide,
  by design and by measurement. Nor is the stella-bond threshold re-quoted as a new headline
  constant — see the caveat below.

## The marked upgrade to 5.7 (not a retraction)

5.7's registered scope-statement **stands verbatim**: its windows, its sizes, its two candidate
thresholds, its pre-registered miss bands (`[1.70, 2.30]`, `[1.50, 2.20]`) and its sensitivity range
(`[150, 600]`) all held, and this rung reproduces its committed numbers to the paper trail's own
6-decimal resolution (P0a/P0b). What changes is the *interpretation*: 5.7 read the miss as a
statement about bond percolation on this graph being harder than 5.6's site case; with the locator
error now quantified, it reads as a statement about the **crossing-mean estimator**. That upgrade is
written into [`../0507-stella-bond-percolation/eval.md`](../0507-stella-bond-percolation/eval.md) as
a dated, marked note with a cross-reference — never silently — and 5.7's `PREDICTIONS.md` row
carries the same pointer.

## Caveats (stated, not hidden)

- **The threshold is not re-quoted as the headline constant.** `0.100648 ± 0.000518` is a
  *methodology* cross-check on one committed curve, and it sits `0.0010` above 5.7's published
  `0.09964 ± 0.00031` — outside 5.7's own error bar, which is itself part of the finding (the two
  estimators disagree by more than either quotes). A genuine re-quote needs new Monte Carlo with the
  extrapolation applied per batch *and* the ordering question settled by more than one answer key —
  on the chapter menu.
- **One answer key licenses the ordering choice.** P2c rests on FCC-bond alone (`3.60e-4` vs
  `5.88e-4`, a gap comparable to the errors themselves). That is thin, and it is the single load-
  bearing judgement in the rung: the other ordering certifies the negative. Deferred: run the same
  comparison on 5.6's site curves, where there are two more answer keys (exact triangular, published
  FCC-site).
- **`z = 0.81` is a `1σ`-style statement with `n = 4` crossing pairs**, so the standard error has 2
  degrees of freedom and its own tails are heavy. `z < 2` was registered, not `z < 1`, for exactly
  that reason.
- **`d_f`'s own statistical error is negligible here** (`±0.011`, from 4 independent seed stripes —
  the 5.5 rule) — the band is `94%` locator error. That is the whole point, and also the reason more
  Monte Carlo at fixed `L` would not help.
- **No 2-D exact control in this rung** (5.6 licensed the crossing/union-find machinery; FCC-bond is
  this rung's control, as in 5.7).

## Fix vs the registered gate (R5)

Two **reporting-layer** bugs were found by inspecting the emitted CSVs and by rendering the figure
before committing either — no prediction, threshold, tolerance or measured value changed, and the
re-run reproduced every number bit-for-bit:

1. `locator_estimates.csv` computed a distance-to-the-answer-key for rows that are error-bar
   **widths** rather than thresholds (comparing a width to a threshold is nonsense), and printed
   FCC's per-batch replica σ as stella's. A `kind` column now separates thresholds from width
   candidates and each family carries its own σ.
2. One estimator label contained a comma (`w-scan spread over [1.6,2.4]`) inside a comma-delimited
   file, which shredded the figure generator's reader and rendered every canvas blank — precisely
   `lab/LESSONS.md`'s 7.2 lesson, hit again. The label now reads `[1.6..2.4]`, the generator asserts
   its expected field count on every row, and the summary CSV's `[lo,hi]` ranges are written `..`
   / `|` throughout. Caught only because R10's verification step renders the actual page.

## Deferred / next (fed back into the chapter menu)

- **Settle the ordering question on 5.6's site curves**, where three answer keys exist (exact
  triangular, published FCC-site, and 5.6's own bracket) instead of one. This is the thin plank in
  P2c and it is cheap — 5.6's sweep is committed machinery.
- **Re-quote `p_c(stella-bond)` properly**: new Monte Carlo, extrapolation applied per batch with
  `replica_stats` over the *extrapolated* estimates, on two sweep windows — which also closes 5.8's
  own deferred "genuine two-window comparison" for the bond family.
- **`ν` from the crossing slope** (`dR/dp|_{p_c} ~ L^{1/ν}`, on the menu since 5.6): it would make
  the band self-consistent — the amplification is `~L^{1/ν}` and is currently taken from literature.
- **The `L` ladder** (5.7's own deferred item): `L` up to ~96–128 at a *fixed* locator, to watch the
  `340` sensitivity shrink as `L^{1/ν}` predicts. This rung makes it a sharper test than before,
  because the expected size of the effect is now measured rather than guessed.
- **Audit 5.6 with the same lens:** 5.6's `d_f` miss was locked with a post-hoc diagnosis at its
  pre-registered constant. Its locator's OLS standard error was never computed, so its band was never
  propagated either. The same three-line re-analysis applies.
