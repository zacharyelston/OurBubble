# 03 · The shield — does cutting a region off from the world change its inertia?

**Concept:** a shield that blocks signals into a region creates a real **information imbalance** — the
inside "sees less" of the outside. Tempting thought: if inertia comes from a body's link to the rest of
the universe (Mach), cutting the link should lighten it. We test both halves and find: **the imbalance is
real; the inertia change is not** — in standard physics. The null names exactly the missing ingredient.

> **Firewall.** *shield, information, inertia, gravity* name a prescribed barrier and a probe field's
> linear response on a **toy** lattice. **Real EM does not screen gravity** (no gravitational Faraday
> cage); the entropic-inertia idea (Mach / Verlinde / MiHsC) is **contested prior physics**, shown only as
> a fenced hypothesis, never derived. Dimensionless; c = 1.

**Source:** lab [`warp-3-shield/0300-shield-imbalance-inertia`](../../../lab/warp-3-shield/0300-shield-imbalance-inertia) ·
gate `core/uniforge/tests/uf3_shield_imbalance_gate.rs`

---

## The hook  <!-- [PUBLIC] -->

Put a wall around a room so no sound gets in. Now the room is *out of touch* with the world — an imbalance
between inside and out. Here's the seductive leap: physicists since Mach have wondered whether an object's
**inertia** (its resistance to being pushed) comes from its connection to all the other matter in the
universe. If so, sealing the room off should make things inside *lighter* — easier to push. That's the
first rung of "gravity manipulation," and it's worth testing honestly. We build the wall, prove it really
does cut the room off — and then check whether anything inside actually got lighter.

## The prediction  <!-- [STUDY GUIDE] -->

Registered before the run (R1). **Part A (provable):** a shield suppresses the interior↔exterior linear
response (the screened-Poisson Green's function) — the inside couples far less to an external source.
**Part B (a registered null):** in standard field theory the barrier `V` multiplies the field `φ` (a
potential / effective-mass² term), **not** its acceleration `φ̈` (the inertia). Inside the bubble `V ≡ 0`,
so the interior equation of motion — and the inertia — is unchanged; if anything the *wall* is more inert
(`m²_eff = V > 0`).

## Figure

**[▶ open the shield figure](../../../lab/warp-3-shield/0300-shield-imbalance-inertia/figures/shield.html)**
— the imbalance (interior coupling collapses, the non-crossing control holds) and the inertia (effective
mass² zero inside, positive at the wall; interior motion unchanged), with the entropic hypothesis fenced.

> **Fig. 1.** Shield on vs off: interior coupling to an external source, and the interior's effective mass²
> and packet motion. *Data-true (R10): `core/viz gen_shield` from `lab/warp-3-shield/0300`.*

## What happened

**In plain terms** <!-- [PUBLIC] -->: the wall works — an external signal reaches the inside about
**half a million times less** than it would without the wall, while a path that never crosses the wall is
barely touched. So the imbalance is genuine: the room really is cut off. But *nothing inside got lighter.*
A test blob inside moves exactly as it did before; the wall only pushes back at its *own location*, not on
the room. Cutting off the information did not cut the inertia.

**The numbers** <!-- [STUDY GUIDE] -->:

| | measured | reading |
|---|---|---|
| interior coupling (crosses shell) | **×2.0×10⁻⁶** | the imbalance — inside sees ~500,000× less |
| exterior control (doesn't cross) | **×0.86** | shield is local, as it should be |
| interior EOM contribution `max\|V\|` | **0** (exact) | shield adds *nothing* inside |
| interior packet displacement | **unchanged** (Δ 1.2×10⁻⁶) | inertia not reduced |
| `m²_eff` centre / wall | **0 / 40** | wall is *more* inert, not less |

The result **rules in** the information imbalance and **rules out** an inertia change under standard
physics: a shield is a potential, and a potential never touches the inertial term. To get the Machian
effect you would need an extra law tying mass to environmental coupling (entropic inertia) — a separate,
contested hypothesis. Under it, this run's coupling drop would *predict* a ~500,000× lighter interior; the
toy neither derives nor endorses that (it's fenced in the figure). What the toy does, cleanly, is separate
the provable from the assumed and name the exact ingredient the bold idea requires.

## Building the wall: opposed magnets and the null  <!-- [STUDY GUIDE] -->

If a shield is a region that "does something to the lattice," how do you *make* one physically? Not with a
single field — a static field doesn't repel another universally. **Orientation** is the knob. Two magnetic
dipoles on the lattice, with one rotated through a full turn, sweep from **attracting** to **opposing**;
and at the **mirrored** orientation their fields refuse to add — they cancel into a genuine **magnetic
null** between them (the "neutral point" of opposed magnets), which is exactly where the repulsive magnetic
pressure peaks. The **[magnet figure](../../../lab/warp-3-shield/0301-magnet-orientation-sweep/figures/magnet.html)**
shows the sweep and the null forming as a dark spot between the two poles.

| orientation | interaction `Σ B_A·B_B` | field null `min\|B\|` | midplane stress |
|---|---|---|---|
| aligned (θ=0°) | −0.010 | 1.2×10⁻³ | +6.8×10⁻⁵ (tension) |
| **mirrored (θ=180°)** | **+0.010** | **9.8×10⁻¹⁹** (a true null) | **−5.6×10⁻⁵ (repulsion)** |

So a magnetic barrier wall is built from **opposed, correctly-oriented** fields — the null-and-pressure of
mirrored dipoles. (This is *field–field* opposition; a static field is still transparent to a neutral
signal in vacuum, so this wall reflects *charged* matter, not information — the next rung tests that.)
→ lab [`0301`](../../../lab/warp-3-shield/0301-magnet-orientation-sweep).

## Does the wall reflect? The magnetic mirror  <!-- [STUDY GUIDE] -->

A wall you can't push anything against isn't a shield. So fire a **charged particle** at the shaped field
and integrate its real Lorentz trajectory. It works: with enough **pitch angle** the particle is turned
around (its axial velocity reverses and it stays inside the field's throats), its speed exactly conserved
because a magnetic field does no work. Reflection is gated by the **loss cone** — too little pitch and the
particle slips through — and the boundary matches the textbook mirror condition `sin²θ_c = 1/R_m`
(θ_c ≈ 30° for a mirror ratio of 4). A **neutral** particle flies straight through: it is the Lorentz
force, not geometry. This is the achievable deflector — a mini-magnetosphere for charged matter.
→ lab [`0302`](../../../lab/warp-3-shield/0302-magnetic-mirror), figure
[the loss cone](../../../lab/warp-3-shield/0302-magnetic-mirror/figures/mirror.html).

## A semi-permeable wall: the tunable double slit  <!-- [STUDY GUIDE] -->

A perfect shield is a wall; a *useful* one is **tunable** — it should let light through to a chosen side. So
build a double slit where **each slit is its own phased source set** and see whether tuning skews the pattern
on the wall. It does, and the literature (Young's double slit; asymmetric-diffraction metasurfaces) fixes
exactly how, giving two independent knobs. A **relative phase** behind one slit walks the bright **fringes**
sideways while the diffraction **envelope** stays centred — the canonical "put a slab of glass behind one
slit." Sweeping that phase steers the beam smoothly (here, 14 cells across half a turn). A per-slit **tilt**
— a linear phase gradient across the aperture — does the opposite: it **blazes the envelope** off-axis
(`x ≈ Y·τ`), like a prism or a phased array. So the pattern skews to whichever side you tune, and
beam-*steering* (phase → fringes) is cleanly separable from beam-*deflection* (tilt → envelope). That is the
signature a real, polarization-built semi-permeable shield would have to show.
→ lab [`0303`](../../../lab/warp-3-shield/0303-asymmetric-double-slit), figure
[phase vs tilt](../../../lab/warp-3-shield/0303-asymmetric-double-slit/figures/slit.html).

> **Scope (R3/R5).** This is *scalar* Huygens–Fresnel diffraction from **prescribed** slit sources — it
> shows how a tuned aperture routes light, not that opposed EM fields build such an aperture in vacuum. The
> "four orthogonal polarizations null a region" idea that motivated it is **not** tested here; this rung only
> establishes the phase-vs-tilt diagnostic a real aperture would need.

## The conjecture, tested: can orthogonal polarizations empty a volume?  <!-- [STUDY GUIDE] -->

The idea driving the whole endgame was: stack ~4 orthogonal polarizations and you should be able to *null a
whole region* — a complete shield, maybe even a negative-energy pocket. So we tested it directly, and the
answer is a clean, instructive **no** — because the physics runs backwards to the intuition. Energy density
is `⟨ρ⟩ = ¼(|Ê|² + |B̂|²)`, and for **orthogonally-polarized** fields the interference (cross) term is zero:
`|Ê₁ + Ê₂|² = |Ê₁|² + |Ê₂|²`. Orthogonal fields **don't interfere — their energies add.** So stacking
orthogonal polarizations *raises* the energy (three perpendicular pairs sit at `⟨ρ⟩ = 3`, exactly three
times one pair) and the center value doesn't even flinch as you tune every phase (it's constant to one part
in 10¹⁶). Orthogonality is the *wrong* tool for a null.

To *cancel* you need **parallel** (interfering) fields — but there the second wall appears: a non-trivial
Maxwell field that vanishes over a whole volume must vanish **everywhere** (unique continuation). Indeed the
only superposition in the test that empties a region is parallel waves in antiphase, which zero the field in
*all* space — darkness, not a shield. And a standing wave, the naive "opposed fields cancel" picture, nulls
`E` on planes but leaves `⟨ρ⟩` perfectly uniform (an `E`-node is a `B`-antinode; the energy just sloshes).
→ lab [`0304`](../../../lab/warp-3-shield/0304-four-source-null), figure
[the four-source null](../../../lab/warp-3-shield/0304-four-source-null/figures/null.html).

The honest conclusion, and it ties the whole chapter together: a genuine interior null **is** possible, but
only with a **boundary of real currents** — a Faraday cage / a Huygens equivalent-source surface *enclosing*
the region (exactly the boundary-shield of rungs 3.0–3.2), which costs sources. And even a perfect null is
`⟨ρ⟩ = 0`, **never** `< 0`: EM energy is sign-locked non-negative (chapter 2.4). A shield can empty a region;
it cannot make it exotic. The negative-energy demand stays with the quantum vacuum — and that bill is
Ford–Roman bounded (chapter 2.9).

## The lopsided double slit — when the lattice photobombs the demo (rung 3.5)

The public double-slit page had a secret: its "two-slit interference" pattern was **3.8× brighter on
one side** of a perfectly symmetric scene. Same slits, same drive, same damping above and below the
midline — lopsided fringes. The culprit is not the wave but the canvas it runs on: the demo's mesh
triangulates every grid square with the **same** diagonal, so each vertex talks to its neighbors
through a stencil that looks the same rotated 180° but *not* reflected top-to-bottom. A mirror-symmetric
question posed on a mirror-asymmetric lattice gets a mirror-asymmetric answer — the same `⋆=I`
anisotropy family as the chapter-1 light-cone defect (#23), caught red-handed in a public demo.

The rung repairs it twice, and the two repairs teach different lessons. Alternate the diagonals
checkerboard-style (`mesh_2d_triangle_grid_crossed`) and the mirror becomes an exact symmetry *of the
mesh itself*: the pattern snaps symmetric to 5×10⁻¹⁵ — machine rounding — at the same amplitude and
timing (the demo page now has a before/after toggle). Or keep the lopsided mesh and turn on the
geometric Hodge ⋆ (the #23 fix): every diagonal edge sits opposite two right angles, so its cotan
weight is exactly **zero** and the interior operator collapses to the symmetric 5-point stencil — but
the field is only symmetric to 10⁻⁷, because the *boundary* ⋆₀ of an open mesh is itself
mirror-asymmetric at the corners. Both knobs of `⋆₀⁻¹D₀ᵀ⋆₁D₀` matter; probe the full population,
boundary included. Bonus honesty for the page (#250): its textbook fringe formula `Δy = λL/d` is a
far-field formula, and the demo's geometry isn't in the far field (`d²/λL ≈ 2.4`) — the lattice
measures 19 px where the formula says 27. The formula is now labeled a comparison, not a prediction.
The full before/after: [the mirror figure](../../../lab/warp-3-shield/0305-doubleslit-mirror/figures/doubleslit_mirror.html).

## Reproduce

```bash
cd core
cargo test --release -p uniforge --test uf3_shield_imbalance_gate -- --nocapture  # writes data/*.csv
cargo run  --release -p viz     --bin gen_shield                                     # → the figure
# the magnetic wall, its mirror, and the tunable double slit:
cargo test --release -p uniforge --test uf3_1_magnet_sweep_gate    -- --nocapture && cargo run --release -p viz --bin gen_magnet
cargo test --release -p uniforge --test uf3_2_magnetic_mirror_gate -- --nocapture && cargo run --release -p viz --bin gen_mirror
cargo test --release -p uniforge --test uf3_3_double_slit_gate     -- --nocapture && cargo run --release -p viz --bin gen_slit
cargo test --release -p uniforge --test uf3_4_four_source_null_gate -- --nocapture && cargo run --release -p viz --bin gen_null
cargo test --release -p uniforge --test uf3_5_doubleslit_mirror_gate -- --nocapture && cargo run --release -p viz --bin gen_doubleslit_mirror
```
Full scorecard: the lab entry's [`eval.md`](../../../lab/warp-3-shield/0300-shield-imbalance-inertia/eval.md).

## Try it  <!-- [STUDY GUIDE] -->

- **Make the shield out of real EM** (menu 3.1): a ponderomotive `|E|²` barrier that reflects a test
  charge — the achievable "force field," using chapter 2's Maxwell stress.
- **Adopt the entropic law** (menu 3.4, speculative/fenced): promote `m_eff ∝ 1/coupling` to a modified
  stepper and evolve — does a decoupled packet *then* move lighter? A toy test of the contested hypothesis,
  clearly labeled as such.
