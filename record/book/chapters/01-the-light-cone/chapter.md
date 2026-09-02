# 01 · The light cone — does the lattice move the same way in every direction?

**Concept:** on a discrete lattice, waves can travel faster in some directions than others; "matching
the lattice" (the geometric Hodge star) makes motion **isotropic** — the precondition for honest
steering.

> **Firewall.** Here, *light cone, isotropy, wave, speed* name the behaviour of a **toy** DEC scalar
> pulse on a tetrahedral lattice. Nothing here is a real light cone, a real measurement, or a warp
> bubble. Dimensionless; c = 1.

**Source:** lab [`warp-1-move/0115-lattice-matched-isotropy`](../../../lab/warp-1-move/0115-lattice-matched-isotropy) ·
gate `core/uniforge/tests/uf1_5_lattice_matched_gate.rs`

---

## The hook  <!-- [PUBLIC] -->

Drop a pebble in a pond and the ripple spreads as a perfect circle — the same speed in every
direction. Now imagine a pond built on a **grid**, where the ripple runs faster along the grid lines
than across the diagonals. The circle would come out squashed, and anything you tried to *aim* would
drift off course.

That squashing is real on the raw tetrahedral lattice this engine runs on — a built-in bias we call
the **#23 defect**. The fix is to let the lattice's *geometry* carry the physics (the "geometric
Hodge star"). Do that, and the ripple rounds back out. The picture below shows both: the biased
wavefront on the left, the corrected one on the right.

## The prediction  <!-- [STUDY GUIDE] -->

Registered before the run (R1/P1):

- **P0 (sanity):** the trivial star `⋆=I` is *clearly* anisotropic — `|v_axis/v_diag − 1| > 5%`.
- **P1:** the geometric Hodge **markedly reduces** it — `aniso_geom < ½·aniso_trivial` and
  `< aniso_trivial − 0.03`.

Measured: a scalar pulse from the centre (`step_scalar_wave`, `nb=24`), speed = distance ÷
time-of-peak along a lattice **axis [100]** vs a body **diagonal [111]**, under `⋆=I`
(`MeshWaveSolver::new`) vs the geometric Hodge (`with_geometric_hodge`).

## Figure

**[▶ open the light-cone figure](../../../lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html)**
— the two wavefronts side by side (dots = measured speeds along each symmetry direction; dashed = a
perfectly round reference).

> **Fig. 1.** Wavefront speed along an axis vs a diagonal, `⋆=I` (lopsided) vs geometric ⋆ (round).
> *Data-true (R10): rendered by `core/viz gen_isotropy` from
> `lab/warp-1-move/0115-…/data/isotropy.csv` (gate `uf1_5_lattice_matched_gate`).*

## What happened

**In plain terms** <!-- [PUBLIC] -->: on the raw lattice the pulse runs **22% faster** along the grid
axes than along the diagonals — visibly lopsided. Matching the lattice cuts that to **~2%** — round to
the eye. So a bubble moves (and steers) the same way in every direction **only** when the lattice is
matched; on the raw star, aiming would point untrue.

**The numbers** <!-- [STUDY GUIDE] -->:

| | ⋆ = I (trivial) | geometric ⋆ | pass |
|---|---|---|---|
| `v_axis [100]` | 0.6289 | 0.7843 | |
| `v_diag [111]` | 0.8109 | 0.8019 | |
| anisotropy `|v_ax/v_di − 1|` | **22.4%** | **2.2%** | ✅ P0 (>5%) · ✅ P1 (≥2× drop) |

**×10.2 more isotropic** when lattice-matched. The result is **bit-for-bit identical** to
`stellamax-core`'s original lab/0115 run (verified during the migration). It rules *out* using `⋆=I`
for any directional result, and rules *in* the geometric ⋆ (Layer 1, `dec::hodge`) as the fix — the
same "geometry lives in the operator" lesson the whole project turns on.

## Reproduce

```bash
cd core
cargo test --release -p uniforge --test uf1_5_lattice_matched_gate -- --nocapture  # writes data/isotropy.csv
cargo run  --release -p viz     --bin gen_isotropy                                    # → the figure
```
Pinned in [`PROVENANCE.md`](PROVENANCE.md). See the lab entry's
[`eval.md`](../../../lab/warp-1-move/0115-lattice-matched-isotropy/eval.md) for the full scorecard.

## Try it  <!-- [STUDY GUIDE] -->

- Turn the geometric Hodge **off** (`MeshWaveSolver::new` instead of `with_geometric_hodge`) — predict
  the anisotropy, then check it against the gate.
- Refine the mesh (`nb = 24 → 32`): does the geometric-⋆ anisotropy shrink further (convergence), while
  `⋆=I` stays biased? *(The vector-photon version of this — the 1-form curl-curl — is the harder
  sibling; see the chapter menu in the lab.)*

---

## Addendum — does the lattice's own handedness split the photon? <!-- [PUBLIC] -->

The light cone above asks whether the lattice moves a wave the same speed in every *direction*. A
related question asks whether it treats the wave's two **handednesses** — left- and right-circular
polarization — the same. The stella lattice can be built with a genuine geometric screw (a
[111]-axis twist in how its octahedral cells split, `chiral_oct_screw111`), so it is a fair question:
does that twist act like a tiny optical-activity medium, making one circular polarization travel
faster than the other?

**Source:** lab [`warp-1-move/0141-bloch-helicity-split`](../../../lab/warp-1-move/0141-bloch-helicity-split)
· gate `core/uniforge/tests/uf1_41_bloch_helicity_split_gate.rs` — closing legacy `stellamax-core`
lab/0140's deferred "cleanest possible version" (a genuine periodic Bloch chiral mesh, real
helicity eigenstates, not a seed-prone open-mesh ensemble).

**The prediction (registered as a bounded null, R1)** <!-- [STUDY GUIDE] -->: 0140's prior expects
no split ("θ is a genuine input"); P1 registered `max_k |split_hel_rel(screw)| < 1e-5` — a
probe-informed bound roughly 4 orders of magnitude below 0140's own noise floor `3.06e-2`.

**Figure:** [▶ open the helicity-split figure](../../../lab/warp-1-move/0141-bloch-helicity-split/figures/bloch_helicity.html)
— helicity magnitude vs `k` (top, → ±1: the pair really are circular-polarization eigenstates) and
the log-scale split vs `k` for the achiral control, the screw, and its mirror image (bottom), against
the registered bound.

**What happened:** no. The chiral screw's two circular polarizations came out helicity-split by only
`1.28e-6` at the largest probed wavevector — about **4.4 decades tighter** than 0140's own
resolution, and indistinguishable from its mirror-image twist (`1.70e-6`, no consistent sign
relationship between the two). The achiral control sits at a true numerical zero (`2.4e-14`). Three
independent methods now agree the toy's `[111]` screw does **not** geometrically split the photon's
handedness — the lattice's own chirality is not, at any resolution probed so far, an optical-activity
mechanism. Full scorecard in the lab entry's [`eval.md`](../../../lab/warp-1-move/0141-bloch-helicity-split/eval.md).

---

## Addendum — the orbit that knew its own box <!-- [PUBLIC] -->

Put a "mass" at the middle of a flat lattice — pin the potential down at one point, hold the edge
at zero, and let the engine relax the field between them. Drop in a test particle with a sideways
kick and it orbits, tracing a rosette: each loop's closest-approach point creeps around the center.
The angle between one closest approach and the next is the **apsidal angle**, and for this kind of
potential the textbook has an exact answer — near a circular orbit, 127.28° (π/√2 radians). Our
demo page had noticed its orbit landing close to that number; this experiment registers the claim
properly — including a prediction of exactly *how far off* the textbook number the lattice should
land, because our box has corners and the textbook's doesn't.

**Source:** lab [`warp-1-move/0142-apsidal-advance`](../../../lab/warp-1-move/0142-apsidal-advance)
· gate `core/uniforge/tests/uf1_42_apsidal_advance_gate.rs` — registering the `mercury.html`
demo's unregistered observation (#254, from the #244 review).

**The predictions (R1, probe-informed)** <!-- [STUDY GUIDE] -->: P0 — the quadrature answer key
reproduces π/√2 at circular and the leapfrog integrator matches it to <10⁻³° in the analytic
potential. P1 — on the lattice (geometric ⋆, N = 40/80/160) the angle converges, landing
**−0.30° to −0.05° below** the free-space value: the pre-registered square-boundary (l=4)
correction, whose amplitude the gate measures independently (a₄/K ∈ [0.5, 2]×10⁻²). P2 — the
integrator's energy drift falls ≈O(dx²) with resolution. P3 — two registered negatives: the
trivial-⋆ arm must NOT converge (the #23/#252 anisotropy, elliptic equipotentials), and a
deliberately broken (non-symplectic) integrator must fail the energy check while posting a
plausible-looking angle.

**Figure:** [▶ open the apsidal figure](../../../lab/warp-1-move/0142-apsidal-advance/figures/apsidal.html)
— the Φ(N) convergence into the pre-registered offset band under the continuum line, and the
energy ladder that separates a correct integrator from a broken one that fakes the angle.

**What happened:** all four held, first run. The lattice angle settles by N=80 at 126.906° —
0.145° below the textbook value, inside the pre-registered band, with the boundary term measured
at the predicted size. The same mesh with the trivial ⋆ scatters its apsides across 89° and never
converges — the anisotropy defect the light-cone section met as a lopsided wavefront, re-met here
as a rosette that cannot decide where its perihelion is. And the broken integrator's angle was
right to five decimal places while its energy drifted eleven orders of magnitude more than the
symplectic one: the reason the gate checks energy, not just the answer. Full scorecard in
[`eval.md`](../../../lab/warp-1-move/0142-apsidal-advance/eval.md). *(Firewall: a toy lattice and
a textbook formula — no Mercury, no relativity.)*

---

## Addendum — the bench is told nothing, and returns the law <!-- [PUBLIC] -->

Everything above tests the lattice against an answer we already had. This experiment turns the
question around: **don't tell the tool anything, and see what it says.**

We ran waves of many different wavelengths across the lattice, in five different directions, and
handed the machine nothing but two columns of numbers — the wavelength, and the frequency that came
back. No formula. No hint. Then we gave it a short menu of the kinds of law a physicist would
recognise — *frequency flat, or growing like the square root of k, or straight-line in k, or like
k²…* — and asked which one the data prefers.

It picked the straight line. In every direction. And it said how strongly: the linear law beat the
runner-up by a margin the machine reports as a number, not a shrug. Then, allowed to fit the
exponent freely, it came back with **1.00**, to within 1.6%.

That is the whole idea of a discovery bench in one page: point it at a system, and it hands back the
governing law with its own confidence attached.

**Source:** lab [`warp-1-move/0117-dispersion-isotropy`](../../../lab/warp-1-move/0117-dispersion-isotropy)
· gate `core/uniforge/tests/uf1_7_dispersion_isotropy_gate.rs` — the first task on the
Discovery-Bench checklist (#46), extending rung 1.6's single-direction version.

**Why "blind" is a claim and not a boast** <!-- [STUDY GUIDE] -->: the only code path from the swept
data to a stated law is one function whose entire signature is the two data columns —
`discover_law(&[f64], &[f64]) -> Discovery`. There is no parameter through which an expected answer
could be passed in, which is a thing a reader can check rather than trust. The candidate menu was
registered before the run. Every assertion in the gate reads what came *back*.

**The predictions (R1, probe-informed)** <!-- [STUDY GUIDE] -->: P0 — the machinery reproduces a
closed-form answer key (see below) to 10⁻¹². P1 — the linear law is selected in all five directions
with an R² margin > 0.15, and the free exponent lands in 1.00 ± 0.03 at R² > 0.9995. P2 — the
discovered *speeds* agree across directions to better than 3%, and — the sharper half — that
residual disagreement **shrinks when the wavelength window shrinks**, which is what distinguishes
"finite-wavelength effect" from "the cone really is lopsided". P3 — the finite lattice bends its own
cone down at short wavelength (registered as a prediction, not excused as a limitation). P4 — a
**negative control**: run the identical pipeline on the deliberately-wrong metric of chapter 1's
opening section, and it must come back *anisotropic*.

**Figure:** [▶ open the discovery figure](../../../lab/warp-1-move/0117-dispersion-isotropy/figures/discovery.html)
— the sweep with the discovered law drawn through it and the *rejected* candidates visibly peeling
away, the candidate scorecard, and the isotropy bars beside their control.

**What happened:** all five held, first run. The linear law won 5/5 by a margin of 0.24; the
exponent came back 1.00 ± 0.016 at R² ≥ 0.999906. The speeds agreed to 1.78%, and halving the
window cut that to 0.69% — so the cone is isotropic in the long-wavelength limit, and on the halved
window every direction's speed sits within 0.012 of 1 in the lattice's own units. The control did
its job: with the trivial metric the same pipeline reported **33.2%** anisotropy — 18.7 times worse
— and, crucially, that number did *not* shrink when the window halved. A test that cannot fail is
not a test; this one can, and we showed it failing on purpose.

**The honest footnote — where the answer key came from** <!-- [STUDY GUIDE] -->: while probing, we
found *why* this cone is so clean. On this mesh the geometric Hodge star gives every axis edge
weight 1 and every diagonal edge weight **exactly zero** — the three-dimensional version of the
"cot 90° = 0" effect the double-slit section met — so the lattice wave operator here *is* the
textbook seven-point stencil, whose dispersion has a closed form. The bench was therefore
re-deriving, blind, a law whose answer was already knowable. That is deliberate and it is the point:
a discovery tool earns the right to be believed on an unknown by first being caught getting a known
one right without being told. It also fences the result — those exact zeros mean the operator is
blind to diagonal edges, which is harmless for the waves measured here and is *not* harmless in
general (rung 8.15 found a zero star opening a spurious null space in the photon sector). No claim
is made here about photons on this mesh. Full scorecard in
[`eval.md`](../../../lab/warp-1-move/0117-dispersion-isotropy/eval.md). *(Firewall: a toy lattice
operator and fits to its own numbers — the exponent and the anisotropy ratio are the dimensionless,
pre-registered quantities; the fitted speed is a lattice code-unit number, never a measurement
of `c`.)*
