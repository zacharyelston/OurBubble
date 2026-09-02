# 0509 — Warp-5.9: reprocess 5.7's `d_f` NEGATIVE with 5.8's locator — dissolve it or certify it

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf5_9_bond_locator_reprocess_gate.rs` ·
**Status:** REGISTERED (R1) — predictions below are committed before any run for record

Origin: the `warp-5-universality` menu row **"apply 5.8's estimator to 5.7 (bond)"** — the half rung
5.8 explicitly did *not* do (5.7 landed after 0508 was written, so 5.7's ~0.00036 window systematic
and its `d_f` miss were untouched by the estimator that was built to fix exactly that class of
problem). Claimed here; the menu row is marked done in the same commit as this rung's landing.

## Goal (one paragraph)

Rung 5.7 registered a first-class **negative**: on the stella tet-oct graph under **bond** dilution,
the fractal dimension `d_f` measured at the crossing-located threshold missed the 3-D
percolation-class value `2.52295` badly (`2.028` at the located `p_c`, `1.906` at a differently
windowed pre-registered constant), and the miss was *predicted in advance* from a probed
`∂d_f/∂p ≈ 338`. Rung 5.8 then built a better locator — fit the pair-crossing **drift**
`p*(L_eff) = p_c + c·L_eff^{-w}` and take the intercept, instead of averaging the crossings — and
demonstrated it on 5.6's (site) curves only. This rung applies 5.8's locator to 5.7's committed bond
curves and asks the two-outcome question: **does 5.7's `d_f` miss dissolve at the better locator (the
miss was the LOCATOR), or does it survive (the negative is certified harder)?** Both outcomes are
results and both are written down below before the run. Because the whole question is *how much
locator error there is*, this rung's first job is to measure the locator's **own error bar** — and to
check that error bar against a published answer key (FCC-bond) at zero location error.

## Firewall (R3)

*Percolation, cluster, threshold, wrapping, fractal dimension* name properties of edge-diluted **toy
graphs**: an edge is "occupied" with probability `p` under a seeded RNG, clusters are connected
components of the occupied-edge subgraph, `R_L(p)` is the probability a component winds a periodic
torus, and `d_f` is the fitted exponent of `s_max(L) ~ L^{d_f}`. `p_c(stella-bond)` is **a constant
of this complex** (bucket 🔵): exact mathematics of a toy graph, never a property of matter. `d_f`,
`τ`, `γ/ν` are dimensionless universal invariants of the 3-D percolation class, shared with real
disordered media — this rung claims **class-membership resolution, computed**, and (where it lands)
that a *previous* class-membership miss was an artefact of *our own estimator*, not a statement about
nature. Toy DEC computation; `c = G = 1`, dimensionless throughout.

## Answer keys (independent of anything this repo computed)

- **FCC-bond threshold:** `p_c = 0.1201635(10)` — Lorenz & Ziff, Phys. Rev. E **57**, 230 (1998);
  independently tabulated in Tarasevich & van der Marck, Int. J. Mod. Phys. C **10**, 1193 (1999).
  Used here as a **zero-location-error** anchor: measuring `d_f` *at a published threshold* removes
  the locator from the experiment entirely, which is the only clean way to ask whether `d_f` itself
  is sound at these lattice sizes.
- **3-D percolation class exponent:** `β/ν = 0.47705(15)` ⇒ `d_f = 3 − β/ν = 2.52295(15)`
  (Wang, Zhou, Zhang, Garoni, Deng, Phys. Rev. E **87**, 052107 (2013)).

## The immutable inputs (5.7's committed record — read-only, never modified)

| quantity | value | source |
|---|---|---|
| stella-bond located `p_c` (5.7's naive per-batch estimator) | `0.099641 ± 0.000312` | `0507-…/data/percolation_summary.csv` |
| `d_f` there | `2.02762` | same |
| 5.7's registered constant / its `d_f` | `0.09928` / `1.90585` | same |
| 5.7's registered miss | `\|2.02762 − 2.52295\| = 0.49533` | derived |
| the wrapping curves (K=5-batch aggregate) | `0507-…/data/rw_curves.csv` | 5.7, PR merged |
| FCC-bond located `p_c` / `d_f` (report-only in 5.7) | `0.119724 ± 0.000471` / `2.39293` | same |

## Method (sketch)

The percolation machinery — `Rng` (splitmix64), the FCC and stella torus edge lists (rung 7.0's
rule), the union-find-with-displacement wrapping detector, `sample`/`measure`, `sweep_batch`, the
`measure_at` FSS measurement and its seed scheme (`SEED_MEAS ^ (l<<40) ^ (rep<<2)`, **independent of
`p`**, so two `p`-points are a *paired* comparison) — is **copied verbatim** from
`uf5_7_stella_bond_percolation_gate.rs`. Copy fidelity is not assumed; it is P0a/P0b below.
The locator machinery is `kinematics::crossing_extrapolate` (5.8's tool), with one addition made in
this rung: **`CrossingExtrapolation::p_c_stderr`**, the OLS standard error of the intercept — the
locator's own error bar, with its own unit tests in `core/kinematics/src/crossing.rs`.

Five things get measured, in this order:

1. **The locator.** 5.8's estimator, applied exactly as 5.8 applied it (the committed K-batch
   **aggregate** curves, fixed class drift exponent `w = 2 = 1/ν + θ`), for both bond families.
   Registered grid, stated explicitly per the 5.6 lesson: stella `p ∈ [0.094, 0.108]` (8 points,
   step 0.002), FCC `p ∈ [0.114, 0.126]` (7 points, step 0.002), `L ∈ {12,18,24,36,48}` — 5.7's own
   windows, unchanged; the pair-crossing sequence is 4 points at `L_eff = √(L_a·L_b) ∈
   {14.70, 20.78, 29.39, 41.57}`. Report-only `w`-scan over `[1.0, 2.6]` and the `w ∈ [1.6, 2.4]`
   spread (5.8's stability yardstick), so the two candidate error bars can be compared.
2. **The locator's error bar, calibrated on the answer key.** `p_c_stderr` vs the `w`-spread vs the
   FCC-bond fit's *actual* distance from the published threshold.
3. **The estimator-ordering systematic.** 5.7 committed only the batch-*aggregate* curve, so
   "extrapolate the aggregate" and "extrapolate each batch, then average" are two different
   estimators. Both are computed (the per-batch arm re-runs 5.7's sweep with 5.7's seeds — no new
   randomness, and its naive per-batch estimates must reproduce 5.7's committed `pc_batches.csv`
   exactly), and the answer key decides which ordering is licensed.
4. **`d_f` and `∂d_f/∂p` at the NEW locator** — a paired central difference over `±0.0006`, because
   5.7's `338` was a secant across a *lower* interval and the 5.7 lesson is that this amplification
   is not universal. `d_f`'s own statistical error comes from the 4 independent seed stripes
   (`kinematics::replica_stats` over 4 sub-replicas of the whole fit — the 5.5 rule).
5. **The verdict**, as a z-score against a band that is the locator's real error propagated through
   the measured sensitivity: `band = √((sens·p_c_stderr)² + σ_stat(d_f)²)`.

Skipped deliberately: the engine-mesh-`d0`-vs-rule graph identity walk (5.6 and 5.7 both prove it,
and the graph is unchanged). Reproducing 5.7's committed batch estimates *and* its committed `d_f`
is a strictly stronger check that this rung's copy is the same machinery; the cheap structural R9
test against rung 7.0's adjacency is kept.

## Predictions (registered before the run)

Every threshold below was measured first by the committed probe
(`core/uniforge/examples/uf5_9_bond_extrapolation_probe.rs`; its full log is
[`data/probe_log.txt`](data/probe_log.txt)) — the LESSONS rule "never register a threshold you
haven't probed". The re-analysis arms are deterministic functions of committed data and the MC arms
are seeded, so the gate *reproduces* these numbers rather than discovering them; that is stated
plainly rather than dressed up.

### P0 — controls. If any of these fails, nothing about stella can be claimed.

- **P0a (sweep copy fidelity):** re-running 5.7's stella-bond sweep with 5.7's seeds reproduces its
  committed per-batch naive estimator: `|mean − 0.099641| < 1e-6` and `|σ_mean − 0.000312| < 1e-6`
  (the committed numbers are printed to 6 decimals, so 1e-6 is the paper trail's own resolution).
  *Probed: reproduced at all 6 decimals, batch by batch.*
- **P0b (measurement copy fidelity):** `|d_f(stella, p = 0.099641) − 2.02762| < 1e-3`. *Probed:
  `2.02746`, `|Δ| = 1.62e-4` — and `1.62e-4 / 340 = 4.8e-7` sits inside the `±5e-7` rounding of
  5.7's 6-decimal committed `p_c`, so the residue is the paper trail's rounding times the
  sensitivity, an internal consistency check of the sensitivity itself, not a code difference.*
- **P0c (the zero-location-error license — the arm that decides "is `d_f` broken, or is it the
  locator?"):** on FCC-bond at the **published** threshold `0.1201635`,
  `|d_f − 2.52295| < 0.05`. *Probed: `2.51943 ± 0.01323` (stat), `|Δ| = 0.0035` = `0.27σ_stat`.*
  5.7 ran this check in prose (its spec's sanity paragraph, L-triples 2.51–2.54); here it is an
  assert, because the entire dissolve/certify question rests on it.

### P1 — the locator 5.8's estimator returns on 5.7's bond curves, and its honest error bar

- **P1a:** `|p̂_c(stella-bond, aggregate, w=2) − 0.100648| < 1e-5`, and it sits **above** 5.7's
  located `0.099641` (registered direction: `p̂_c − 0.099641 > 0`; probed gap `+0.00101`).
- **P1b (the fit is honest about itself):** `p_c_stderr ∈ [3.0e-4, 8.0e-4]` (probed `5.18e-4`), and
  `r² < 0.30` for **both** bond families (probed stella `0.0022`, FCC `0.1527`). The low `r²` is
  registered *up front*: unlike 5.6's site curves, **the drift is not resolvable in 5.7's bond data**,
  so this estimator is not being sold as a better fit — only as a better-centred intercept with a
  quantified error.
- **P1c (error-bar calibration against the answer key):** on FCC-bond,
  `|p̂_c − 0.1201635| < 2.5 × p_c_stderr` **and** `|p̂_c − 0.1201635| > 3 × (w∈[1.6,2.4] spread)`.
  *Probed: the real error is `3.60e-4` = `1.10 ×` the standard error and `6.09 ×` the `w`-spread.*
  This is the falsifiable form of a methodological correction to 5.8: a `w`-scan measures
  **fit-choice stability**, not accuracy, and quoting it as the locator's uncertainty understates
  the real error by ~6× on the one bond lattice with a published answer.

### P2 — the systematics that set the band (probed BEFORE the band, per the 5.6/5.7 lesson)

- **P2a (local sensitivity at the NEW locator):** paired central difference over `±0.0006`,
  `∂d_f/∂p ∈ [250, 450]`. *Probed `340.1`; 5.7's secant over the lower interval was `337.6` — the
  near-equality is what licenses propagating the error linearly across a `0.001` move in `p`.*
- **P2b (the estimator-ORDERING systematic — measured, not assumed):**
  `|p̂_c(aggregate-then-extrapolate) − p̂_c(extrapolate-then-average)| ∈ [8e-4, 2e-3]` for
  stella-bond, with the aggregate arm **higher**. *Probed `1.330e-3`, i.e. ≈3.7× the `3.6e-4`
  bond window systematic 5.8 was built to remove, and 3.7× the per-batch replica `σ_mean` itself.*
  Registered because no rung in this chapter (5.6, 5.7 or 5.8) registered which ordering it used.
- **P2c (the answer key licenses the ordering):** on FCC-bond,
  `|agg-extrap − 0.1201635| < |per-batch-extrap − 0.1201635|`. *Probed `3.60e-4 < 5.88e-4`.* So the
  aggregate ordering — 5.8's own recipe, since 5.8 read 5.6's committed aggregate curve — is the
  more accurate one, and it is the arm this rung reports as **the** 5.8-estimator answer.
- **P2d (the propagated band, and the resolution statement):**
  `band = √((sens × p_c_stderr)² + σ_stat(d_f)²) ∈ [0.10, 0.30]`. *Probed `0.1766`
  (`340.1 × 5.18e-4 = 0.1763`, `σ_stat = 0.0108`).* Registering that the band is **wide** is itself
  the result (the 5.3 pattern — predicting your own resolution limit): at any crossing-located
  threshold of this precision, `d_f` **cannot** resolve class membership better than `±0.18`, and no
  choice of crossing estimator changes that.

### P3 — the verdict. Two outcomes, both registered now.

- **P3a (reproducibility):** `|d_f(stella, p̂_c) − 2.37985| < 0.01`.
- **P3b (the improvement claim — falsifiable and directional):**
  `|d_f(p̂_c) − 2.52295| < 0.5 × 0.49533 = 0.2477` **and** `d_f(p̂_c) > 2.02762` (the better locator
  must move `d_f` **upward**, the sign the positive sensitivity demands, and must close at least
  half of 5.7's registered miss). *Probed: `2.37985`, miss `0.1431` — 71% of 5.7's miss closed.*
  This can fail: a locator that moves `p` without moving `d_f` toward the class value, or that
  overshoots past it, breaks P3b while leaving P1/P2 intact.
- **P3c (dissolve or certify):** `z = |d_f(p̂_c) − 2.52295| / band`.
  - **Registered branch — H-DISSOLVE, `z < 2`:** 5.7's `d_f` miss was **the locator**. At a locator
    whose error is honestly quantified, the measured `d_f` is statistically consistent with the 3-D
    percolation-class value, so the negative dissolves into a *resolution* statement: 5.7's
    registered scope-statement stands verbatim (its windows, its sizes, its numbers, its
    pre-registered miss bands all held), while its *interpretation* is upgraded — the miss measured
    the estimator, not the lattice. *Probed `z = 0.81`.* The upgrade is written into 5.7's own
    `eval.md` as a dated, marked note with a cross-reference, never silently.
  - **Pre-registered alternative — H-CERTIFY, `z ≥ 2`:** the negative is certified harder: the
    stella graph's bond `d_f` misses the class band even at a better-centred locator with a
    propagated band, which would be a genuine finding about **this family and this graph at
    `L ≤ 48`** (never about nature or about percolation in general), and the next discriminator is
    named in advance: `L` up to ~96–128 at fixed locator (5.7's own deferred item), since the
    amplification is `~L^{1/ν}` and must shrink if it is finite-size in origin.
  - *gate:* assert the registered branch. If the run returns the alternative, the R5 negative-lock
    path applies (commit the failing data first, then re-register to keep the verdict false in the
    scorecard while asserting the miss and its diagnosis reproduce) — the rung is **not** re-narrated
    after the fact either way.

### P4 — the by-product the steep sensitivity licenses, with its own answer-key test

- **P4a:** invert the thermometer. Anchoring `d_f` at the class value and dividing by the measured
  local sensitivity, `p_c(d_f-anchored) = p + (2.52295 − d_f(p))/sens`, recovers FCC-bond's
  **published** threshold to `|Δ| < 5e-5`. *Probed `0.1201763` vs `0.1201635`, `+1.28e-5` — about
  15× tighter than the best crossing estimator on the same committed curves (`2.0e-4`), and the
  residual is exactly the finite-size `d_f` bias (`0.0035`) divided by the sensitivity (`276`).*
  **Bucket honesty:** this consumes the literature class exponent as an input, so it is a 🔵
  method/cross-check and can **never** be a 🟢 prediction; it is registered because a steep
  `∂d_f/∂p` is a *defect* for class testing and a *lever* for locating, and the answer key is what
  turns that observation into a licensed tool. *gate:* assert.
- **Derived, reported, not an independent assert:** the same inversion on stella-bond gives
  `p_c(d_f-anchored) ≈ 0.101069`, which differs from the crossing-extrapolated locator by
  `|Δ| = 4.2e-4 = 0.81 × p_c_stderr`. This is **algebraically the same statement as P3c** viewed in
  `p`-space (`|Δ| = |d_f − class| / sens`), so it is not counted as extra evidence — but it is the
  clearest reading of what "dissolve" means: *the threshold you would infer from the class exponent
  and the threshold you locate from the crossings agree inside the crossing locator's own error bar.*

**Report-only (written to `data/`, not gated):** the full 6-point `d_f`-vs-locator ladder (including
the per-batch-extrapolated locator, `d_f = 1.919`, which shows the ordering systematic's effect
directly), the `w`-scans, the per-batch tables for both families, and the naive-vs-extrapolated
accuracy comparison on FCC-bond — where the plain aggregate mean of the pair crossings (`0.119963`,
error `2.0e-4`) is in fact *closer* to the published threshold than the extrapolated intercept
(`0.119804`, error `3.6e-4`). Reported plainly: on **bond** data at this statistics the extrapolation
is not demonstrably more accurate than the mean it replaces; what it does here is move the locator
into the region where `d_f` agrees with the class, and quantify its own error while doing so.

## What would falsify this

- **P0a/P0b failing** ⇒ the copied machinery is not 5.7's machinery; every number below is void,
  and the rung reports an inconclusive re-analysis (R5) rather than any verdict on 5.7.
- **P0c failing** ⇒ `d_f` is *not* sound at these sizes even with the locator removed. Then 5.7's
  miss is not a locator story at all and this rung's whole framing is wrong — reported as such, and
  the follow-on is an `L`-ladder on the FSS fit itself, not another estimator.
- **P1c failing** ⇒ either the standard error does not cover the real error (then this rung's band is
  not trustworthy and no dissolve claim can be made), or the `w`-spread turns out to be a fair error
  bar after all (then the methodological correction to 5.8 is withdrawn). Either way it is reported.
- **P2b/P2c failing** ⇒ the ordering choice is either not a real systematic or not licensed by the
  answer key; in the latter case the reported locator would have to be the per-batch arm, which
  gives `d_f = 1.919` and **certifies** the negative instead — this is exactly why the ordering is
  gated rather than quietly chosen.
- **P3b failing with P0–P2 green** ⇒ the better locator does not move `d_f` toward the class value:
  a first-class negative about the *locator-error explanation itself*, not about the class.
- **P3c returning `z ≥ 2`** ⇒ H-CERTIFY, above. Not a failure of the rung — the other registered
  outcome.
- **P4a failing** ⇒ the inverted estimator is not licensed; it is withdrawn (reported, not widened),
  and the derived stella number is deleted from the record rather than quoted without a license.

## Determinism

Seeded splitmix64 throughout, all seeds compile-time constants echoed into `data/seeds.csv`
(sweep base `0x5EED ⊕ k·2⁵⁰`, measurement base `0xABCD`, `K=5` batches × `R=300` sweeps,
`R=2400` measurement reps, fixed 4-way thread striping). The re-analysis arms read a committed CSV
and are closed-form least squares. Pure `f64`, no wall-clock, no unseeded RNG — the same numbers on
every machine, every run.
