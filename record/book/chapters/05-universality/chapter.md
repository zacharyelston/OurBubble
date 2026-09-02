# 05 · Universality — can the toy predict a number it wasn't built to know?

**Concept:** the ledger drew the line — an *accurate* toy reproduces known physics, but to stop being a toy
it must output a **dimensionless number of nature** it wasn't built to know, with zero tuning. The firewall
forbids the numerology route (α from geometry). The honest route is **universality**: at a critical point,
dimensionless quantities — the central charge `c`, the exponents `ν, β, z` — are the *same* for a lattice
model, the continuum theory, and **real materials**, independent of microscopic detail. The lattice measures
the Ising set (`c = ½, ν = 1, z = 1`) parameter-free. The swing lands the *capability*; the honest scope is
that these are a solvable model's known values.

> **Firewall.** *Ising, critical, central charge, exponent* name universal invariants of a **toy** quantum
> spin chain's critical point (free-fermion solvable), shared with the 2-D Ising model and real Ising-class
> systems (universality). This is universality-class membership, computed — **not** a claim the warp/DEC
> engine "is" a magnet, and **not** a spacetime claim. Dimensionless.

**Source:** lab [`warp-5-universality/0500-ising-universality`](../../../lab/warp-5-universality/0500-ising-universality) ·
gate `core/uniforge/tests/uf5_universality_gate.rs`

---

## The hook  <!-- [PUBLIC] -->

We refused to "derive" the fine-structure constant, because hitting a target with a formula is numerology,
not physics. So what *would* count? A number the toy spits out — without being told the answer — that also
shows up when you measure the real world. Nature hands us exactly such numbers at **critical points** (a
magnet losing its magnetism, a fluid at its boiling ridge). There, the details wash out and a handful of pure
numbers — the *critical exponents* — are shared by wildly different systems. That's **universality**. If our
lattice sits in the same class as a real magnet, it must produce the same numbers. So we made it try.

## The prediction  <!-- [STUDY GUIDE] -->

Registered before the run (R1). Take the critical transverse-field Ising chain (exactly solvable, built on
the same `2−2cos k` lattice-Laplacian spectrum as chapter 4). From **raw finite-size data** — the
ground-state energy `E₀(L)` at a few system sizes — extract the universal invariants with **nothing tuned**:
the **central charge** `c` from the `1/L²` correction (`E₀/L = e∞ − πcv/6L²`, with the velocity `v`
*measured* from the dispersion), the correlation-length exponent `ν` from the gap, the dynamic exponent `z`
from the critical finite-size gap. Predicted values (the Ising class): `c = 1/2`, `ν = 1`, `z = 1`, on the
exact critical energy density `e∞ = −4/π`.

## Figure

**[▶ open the universality figure](../../../lab/warp-5-universality/0500-ising-universality/figures/universality.html)**
— the finite-size-scaling line (its slope gives `c`, its intercept the exact `−4/π`) and the scorecard of the
universal numbers, measured vs exact.

> **Fig. 1.** `E₀/L` vs `1/L²` → the central charge from the slope, plus `c, ν, z` measured against nature's
> exact values. *Data-true (R10): `core/viz gen_universality` from `lab/warp-5-universality/0500`.*

## What happened

**In plain terms** <!-- [PUBLIC] -->: it worked. The lattice returned **c = 0.4999999**, **ν = 1.000000**,
**z = 0.9996** — the exact Ising numbers — and the fit's intercept landed on `−4/π` to nine digits. We never
typed `½` or `1` anywhere; they fell out of how the energy shrinks with system size. And these are not our
numbers — they are the ones a physicist *measures* in a real uniaxial magnet or an order–disorder transition,
because all those systems share the Ising class. For the first time the toy produced a piece of nature it was
not built to know.

**The numbers** <!-- [STUDY GUIDE] -->:

| invariant | lattice (measured) | exact / nature |
|---|---|---|
| central charge `c` | **0.4999999** | `1/2` |
| correlation-length exponent `ν` | **1.000000** | `1` |
| dynamic exponent `z` | **0.999617** | `1` |
| critical energy density `e∞` | **−1.273240** | `−4/π` |
| velocity `v` (measured, not assumed) | 2.000000 | 2 |
| magnetization exponent `β` (cited) | 0.125 | `1/8` |

**The honest scope.** This is the graduation *swing landing the capability* — a parameter-free, dimensionless
number of nature, extracted by exactly the methodology (finite-size scaling) that condensed-matter physics
uses on real data. But the transverse-field Ising chain is **exactly solvable**, so `c = ½` is a value we
already knew: this rung *validates the machinery*, it is not yet a **novel** prediction. The true graduation —
the thing that would make the toy "no longer a toy" — is to run the *identical* machinery on a model that is
**not** solvable (by Monte Carlo or DMRG) and predict a **real material's** exponents *before looking them
up*. That is the next rung. The door is open; we have not yet walked through it.

## Reproduce

```bash
cd core
cargo test --release -p uniforge --test uf5_universality_gate -- --nocapture  # writes data/*.csv
cargo run  --release -p viz     --bin gen_universality                          # → the figure
```
Full scorecard: the lab entry's [`eval.md`](../../../lab/warp-5-universality/0500-ising-universality/eval.md);
the whole-project honesty audit: [`PREDICTIONS.md`](../../../PREDICTIONS.md).

## The swing lands: blind Monte Carlo predicts a real material  <!-- [STUDY GUIDE] -->

Rung 5.0 used an *exactly-solvable* model, so its numbers were known — it validated the method but didn't
predict anything new. So we took the real swing (rung 5.1): a **generic Monte Carlo** — single-cluster Wolff,
which contains **no exact solution** — run first on the 2-D Ising model as a *blind check* (it returned
`γ/ν = 1.750`, `β/ν = 0.125`, the exact Onsager values, to a fraction of a percent), then run *unchanged* on
the **3-D Ising model — which has no closed-form solution at all.** The 3-D exponents it produced:

| | lattice (blind MC) | real materials (measured) |
|---|---|---|
| β | **0.315** | liquid–gas critical point & uniaxial magnets ≈ **0.325** |
| γ | **1.259** | ≈ **1.24** |

Within a few percent of the numbers a physicist *measures* at a boiling-point critical ridge or in a real
ferromagnet — for a model nobody can solve on paper. The simulation didn't know the answer; it computed one,
and nature agrees. → lab [`0501`](../../../lab/warp-5-universality/0501-montecarlo-prediction), figure
[the graduation swing](../../../lab/warp-5-universality/0501-montecarlo-prediction/figures/montecarlo.html).

> **This is the milestone.** By the ledger's own rule — dimensionless, parameter-free, pre-registered,
> matching an *independent* truth with zero tuning — and unlike everything before it, the truth here was **not
> in any answer key** available to the method. The toy demonstrated it *can predict a measured number of
> nature.* **Honest boundary (R3/R5):** this is universality-class membership of a toy Ising model, computed by
> Monte Carlo — not a claim about the warp engine or spacetime — with stated caveats (small-`L` corrections
> bias the 3-D estimate a few %; `T_c` and `ν` were supplied). The door is walked through for the Ising class;
> the warp ambitions remain a firewalled toy.

## Nothing supplied but the model: the self-contained prediction  <!-- [STUDY GUIDE] -->

The 3-D prediction above was honest but leaned on two supplied numbers: the critical temperature `T_c` and the
exponent `ν` (used to turn the ratios into `β, γ`). Rung 5.2 removes both, using one more universal tool — the
**Binder cumulant** `U = 1 − ⟨m⁴⟩/3⟨m²⟩²`. It has a magic property: *at* criticality it stops depending on
system size, so the `U_L(T)` curves for every `L` **cross at a single point.** That crossing *is* `T_c` — the
simulation finds it with no exact input — and the crossing height is itself a universal number, `U* ≈ 0.61`.
Then the way the curves steepen with size, `dU/dT|_{T_c} ∼ L^{1/ν}`, **measures `ν`.** With those in hand,
`β` and `γ` follow from the magnetization and susceptibility at the located `T_c`. Everything is an output:

| quantity | measured (blind) | exact |
|---|---|---|
| `T_c` | 2.2668 | 2.2692 (0.10%) |
| `U*` | 0.614 | ≈ 0.61 |
| `ν` | 1.040 | 1 |
| `β` | 0.126 | 0.125 |
| `γ` | 1.828 | 1.75 |

Nothing was handed to the toy but the model itself; it returned the critical temperature *and* the full set of
exponents, each matching the exact 2-D-Ising truth (and hence real 2-D-Ising materials). → lab
[`0502`](../../../lab/warp-5-universality/0502-self-contained), figure
[the Binder crossing](../../../lab/warp-5-universality/0502-self-contained/figures/selfcontained.html).

> **Where the arc leaves us (R5).** The graduation criterion is met *for the Ising class*: a dimensionless
> number of nature, predicted parameter-free, without the answer key, end-to-end. The `ν` estimate (4%) is the
> honest weak point and propagates into `γ`. The only piece left is compute, not method — running this same
> fully-blind pipeline on the *3-D* model (heavy temperature scans) so its `T_c` and `ν` are measured too. And
> the firewall is unchanged throughout: this is universality-class membership of a toy Ising model, not a claim
> about the warp engine or spacetime.

## The close: the unsolved model, fully blind  <!-- [STUDY GUIDE] -->

Rung 5.3 composes the two halves: the fully-blind Binder pipeline, run on the **3-D model** — no closed form,
nothing supplied. Seven Binder crossings locate the 3-D critical temperature at **`T_c = 4.5099`** (literature
4.5115 — **0.036%**, four parts in ten thousand, for a model nobody can solve on paper), at the universal 3-D
value `U* = 0.484` (≈0.465). Finite-size scaling *at that located point* returns the 3-D-Ising-class ratios
`γ/ν = 2.03`, `β/ν = 0.49`. And the honest boundary was itself a registered prediction: the Binder-slope `ν`
was pre-registered to land **high** of 0.630 at these sizes (the known `ω ≈ 0.83` corrections) — it did, at
0.766. The bench predicted its own resolution limit, then confirmed it (R5). The fix is compute, not method.
→ lab [`0503`](../../../lab/warp-5-universality/0503-blind-3d).

**Where chapter 5 ends:** 5.0 validated the machinery, 5.1 predicted the unsolved class, 5.2 removed the
supplied inputs, 5.3 composed them — `T_c, U*, γ/ν, β/ν` of an unsolved model, end-to-end, blind, with the
one unresolved number flagged in advance. The ledger's graduation criterion is met for the Ising class.

## Coda: a second class — percolation on the engine's own graph  <!-- [STUDY GUIDE] -->

The chapter's pattern is not Ising-specific, and rung 5.6 proves it on a different universality class
entirely. Site percolation — occupy each vertex of a graph with probability `p`, ask when a cluster
spans — has its own critical point and its own universal exponents, measured in real porous media and
gels. The Binder crossing has a percolation analog: the **wrapping probability** `R_L(p)` (does a
cluster wind the periodic torus?) is dimensionless, so its finite-size curves cross at the threshold.

The pipeline runs the chapter's playbook: license the machinery on a **solved** lattice (the
triangular lattice, where `p_c = 1/2` is *exact* — the located 0.50099 hits it), check the 3-D arm on
a **published** one (FCC, 0.19946 vs 0.1992365(10)), then hand it the engine's own stella tet-oct
graph — the same 14-regular adjacency rung 7.0 proved is the mesh's `d0`. Out comes a previously
untabulated number: **`p_c(stella-site) = 0.17445 ± 0.00041`**, below FCC exactly as a superset graph
must be. At the located threshold, `τ = 2.121` and `γ/ν = 2.143` sit in the 3-D percolation class as
registered.

And the rung carries the chapter's R5 signature too, sharpened: the `d_f` arm **missed** its
registered band (2.4378 vs 2.523 ± 0.06). Not retuned — diagnosed. Exponents measured *at a located
critical point* inherit the locator's tiny error amplified by `~L^{1/ν}`: the gate measures
`∂d_f/∂p ≈ 117`, so the ±0.0008 wobble in the crossing estimate moves `d_f` by ~0.09 — and at the
*pre-registered* constant `p = 0.1752` the same estimator returns `d_f = 2.525`, dead on the class
value. The miss is locked into the gate as a first-class negative with its measured diagnosis: the
bench, once again, states its own resolution limit. → lab
[`0506`](../../../lab/warp-5-universality/0506-stella-percolation), figure
[the wrapping crossing](../../../lab/warp-5-universality/0506-stella-percolation/figures/percolation.html).

## Coda continued: bond percolation — turning the lesson into a design  <!-- [STUDY GUIDE] -->

Rung 5.7 asks the same question with edges diluted instead of sites — every vertex present, each
**bond** occupied with probability `p` — the identical wrapping-crossing and union-find machinery,
one line of the sampler changed. Licensed against the published FCC-bond threshold
(`p_c = 0.1201635(10)`, Lorenz & Ziff 1998, independently confirmed by Tarasevich & van der Marck
1999), the pipeline hands the stella graph a **second** previously untabulated constant:
**`p_c(stella-bond) = 0.09964 ± 0.00031`**, again below FCC-bond, again as the superset graph must
be. `τ = 2.150` and `γ/ν = 1.964` sit in the 3-D percolation class, as before.

The interesting move is what happens to `d_f`. Rather than wait to discover the locator-sensitivity
problem the hard way (as 5.6 did), this rung probed it first: bond percolation's `∂d_f/∂p` turns
out to be **~3× steeper** than site's (`≈338` vs `≈117`) — confirmed a genuine sensitivity effect,
not a bug, by checking `d_f` at the *exact* literature FCC-bond threshold (zero location error),
where it converges cleanly to the class value. Knowing that up front, the gate **pre-registers**
both arms as bounded misses — the located threshold's `d_f` in `[1.70, 2.30]`, a differently
probed constant's `d_f` in `[1.50, 2.20]`, and the sensitivity itself in `[150, 600]` — *before*
running once for the record. All three held, exactly as predicted: `2.028`, `1.906`, and `338`.
Unlike 5.6, *neither* arm recovers the class value at these sizes — a harder finding, but one the
bench called correctly in advance, which is the more informative outcome: it demonstrates the
machinery understands its own resolution limit, not just that it got lucky on one draw. → lab
[`0507`](../../../lab/warp-5-universality/0507-stella-bond-percolation), figure
[the bond-percolation crossing](../../../lab/warp-5-universality/0507-stella-bond-percolation/figures/bond_percolation.html).

## Coda, third movement: we went back and checked, and the mistake was ours

Two rungs later there was a better tool. Rung 5.8 replaced "average the crossings" with "fit the way
the crossings *drift* with size and take the limit" — the textbook move, and a small one: no new
simulation, just better arithmetic on numbers already committed. It was only ever tried on the site
data. Rung 5.9 pointed it at the bond data and asked the question that had been sitting there:
**was 5.7's failure about the lattice, or about us?**

Both answers were written down before the run, which is the only way that question can be asked
honestly. The answer came back: **us.** At the better-centred threshold, `d_f` rises from `2.028` to
`2.380`, and once you propagate the threshold's own uncertainty through the steepness — the
`∂d_f/∂p ≈ 340` that 5.7 had already measured — that sits `0.8` standard deviations from the class
value. Statistically, it agrees.

The clinching evidence is a control that costs almost nothing and settles everything. Take the
locator out of the experiment: measure `d_f` at a threshold *somebody else published*, for FCC bonds,
where our estimate plays no part. The same code, the same seeds, the same fit window returns
**`2.5194`** against the class value `2.52295` — a gap of `0.0035`, about a quarter of one
statistical error bar, and 141 times smaller than 5.7's miss. The machinery was never broken. A
sub-thousandth error in *where you think the critical point is* was worth a tenth of an exponent, and
we had been about half a thousandth off.

The useful part of the rung, though, is what it found by looking hard at its own new tool.
**First:** 5.8 had quoted the spread of its answer across a range of the fit's fixed exponent as
evidence its problem had "collapsed". On the lattice with a published answer, that spread turns out
to be six times *smaller* than the fit's actual distance from the truth — it measures how stable your
fitting choice is, not how right you are. The honest error bar is the ordinary least-squares
uncertainty of the intercept, which does cover the real error, and which is now part of the tool
rather than a remark. **Second:** "extrapolate the crossings" is not one estimator. You can average
the five simulation batches into one curve and extrapolate that, or extrapolate each batch and
average the answers — and on this data those differ by more than the problem 5.8 set out to fix. They
also disagree about the verdict: one dissolves 5.7's negative, the other certifies it. Nobody had
written down which one they meant. Now the published answer key picks, and the choice is a test
rather than a habit.

And the steepness that ruined `d_f` as a class test is a gift if you turn it around. If a tenth of an
exponent buys you a thousandth in `p`, then *assuming* the class value and reading off the threshold
is an extremely sensitive way to locate a critical point. Checked against the published FCC-bond
number, it lands within `1.3×10⁻⁵` — about fifteen times better than any crossing estimator here.
That is not a prediction (it eats the literature exponent to produce the answer), and the ledger
files it accordingly. It is a good instrument.

None of this retracts 5.7. Every band 5.7 registered held; its scope statement is true as written.
What changed is the sentence underneath it — and the change is recorded *in* 5.7, dated and marked,
because a record you can quietly improve is not a record. → lab
[`0509`](../../../lab/warp-5-universality/0509-bond-locator-reprocess), figure
[d_f against the locator](../../../lab/warp-5-universality/0509-bond-locator-reprocess/figures/bond_locator.html).

<!-- [STUDY GUIDE] -->
> **The mechanics.** `d_f` comes from `s_max(L) ~ L^{d_f}` fitted over the largest three of
> `L ∈ {18,24,36,48}`, R = 2400 samples each, seeds independent of `p` so two thresholds are a
> *paired* comparison and the finite-difference `∂d_f/∂p` is far quieter than two independent runs.
> The acceptance band is `√((∂d_f/∂p · σ_{p_c})² + σ_stat²) = ±0.1766`, of which 94% is locator error
> — which is exactly why more sampling at fixed `L` cannot help, and why the pre-registered claim is
> a *resolution* statement (`d_f` cannot decide class membership better than `±0.18` at these sizes)
> rather than a confirmation. `σ_stat` is a replica error over 4 independent seed stripes (the 5.5
> rule). Fourteen gated predictions, all green; both verdict branches registered in advance.
> Two reporting-layer bugs in the rung's own CSV/figure layer were caught by rendering the page and
> reading it back — one of them a comma hidden inside a comma-delimited field, `lab/LESSONS.md`'s 7.2
> lesson landing for a second time — and both are documented in `eval.md` under R5.

## Coda, fourth movement: the other one too — and it was in the file all along

Having found that 5.7's failure was our own threshold, the obvious question was whether 5.6's was as
well. It has the same shape: an exponent measured at a threshold we located ourselves, a registered
band, a miss, a diagnosis. So the same test was pointed at it, with both answers written down first.

It dissolves. But the interesting part is *how cheaply*. The better locator does help — the exponent
moves from `2.438` to `2.491`, inside the band 5.6 had registered — yet you don't need the better
locator at all. Rung 5.6 published its threshold as `0.17445 ± 0.00041`, and later in the same
document it measured how much the exponent moves per unit of threshold error: about `117`. Multiply
those two numbers together and you get `± 0.048` — **eighty percent of the `± 0.06` band it declared
a miss against.** With the exponent's own noise folded in, the class value was inside the error bar at
5.6's own threshold. Both numbers were on the page. Nobody multiplied them.

That is a different kind of mistake from a wrong prediction, and worth naming precisely: not bad
physics, not a bug, but a **band drawn without propagating an error the rung had already measured**.
Two registered negatives in this chapter turned out to be that same omission.

The control that settles it is the nicest experiment in the thread, because for once nothing is
approximate. Two-dimensional site percolation on the triangular lattice has a threshold that is known
*exactly* — one half — and a fractal dimension that is known *exactly*: ninety-one forty-eighths. Feed
the exact threshold in and there is no locator left in the experiment and no literature uncertainty at
either end. The answer comes back **1.89613** against **1.8958333**: a gap of three ten-thousandths,
about four percent of one statistical error bar. The machinery was never the problem. And nudge that
threshold by half a percent either way and the exponent swings from `1.83` to `1.94` — at these sizes
the exponent is not really testing the universality class, it is reading back the threshold you fed
it.

One number, then, explains the whole thread. How hard does the exponent lean on the threshold? In 2-D,
about `10`: a threshold error of a thousandth costs a hundredth of an exponent and nobody notices. In
3-D site percolation, about `100`. In 3-D *bond* percolation, about `300`. So the same threshold
precision that is entirely adequate in two dimensions is worth a tenth of an exponent in three — which
is exactly the size of both registered misses. It is not a constant of percolation: it grows with
dimension and again with the dilution rule, so it has to be re-measured for each variant, and any
exponent quoted at a *located* critical point needs it attached.

This rung also had to correct its predecessor. Rung 5.9 had found an unwritten choice inside the
estimator — average the five simulation batches and fit once, or fit each and average — and picked the
option its single answer key preferred. Site percolation offers two keys, one of them exact, and they
both prefer the *other* option, by a factor of three to five. So there is no universally right choice
here; the honest rule is that the aggregation order has to be declared per experiment. Which is why
this rung's verdict was built not to depend on it: the test was run at all three candidate thresholds,
and all three dissolve. → lab
[`0510`](../../../lab/warp-5-universality/0510-site-locator-reprocess), figure
[the miss was inside an error bar](../../../lab/warp-5-universality/0510-site-locator-reprocess/figures/site_locator.html).

<!-- [STUDY GUIDE] -->
> **The mechanics, and the limits.** `z = |d_f − d_f(class)| / √((∂d_f/∂p · σ_{p_c})² + σ_stat²)`,
> evaluated at three locators, each with its own quoted `σ_{p_c}`: `1.69` (5.6's own), `1.73`
> (per-batch extrapolated), `0.52` (aggregate extrapolated). All `< 2`, which was the registered
> dissolve criterion — chosen at 2σ rather than 1σ because with only 4–5 crossing pairs the standard
> error has 2–3 degrees of freedom and heavy tails. Note what is *not* claimed: `z < 2` means the miss
> is **not statistically significant**, not that the exponent is confirmed; the band is `±0.05–0.06`
> wide and that width, pre-registered, is the actual result. Two further honest limits carried in the
> eval: the newer estimator is **not** more accurate — on all three answer keys in this chapter the
> plain mean of the crossings is closer, so what it contributes is an error bar that survives a key,
> not a better number — and the 3-D finite-size bias in `d_f` (~`0.015` at `L ≤ 48`, in the opposite
> direction to what 5.6 pre-registered) is measured but deliberately left *out* of the band, since
> including it would only widen the band and strengthen the verdict.

## Try it  <!-- [STUDY GUIDE] -->

- **Sharpen ν** (menu): larger `L` with an explicit `(1 + c·L^{−ω})` correction term — compute-bound.
- **Data collapse** (menu): scale `M·L^{β/ν}` vs `(h−h_c)L^{1/ν}` — every size on one curve, the visual
  fingerprint of universality.
- **A genuinely open case**: point the pipeline at a model whose class is *debated* — a real, live prediction.
