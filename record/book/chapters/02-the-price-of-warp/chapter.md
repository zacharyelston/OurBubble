# 02 · The price of the bubble — where does the exotic energy come from?

**Concept:** a warp bubble is a *shaped* shift of the lattice. Read its energy straight off the geometry
of that shaping, and out falls the classic warp-drive signature — **negative** energy, on the **wall**, in
a **ring** — with nothing put in by hand. This is the [genesis tenet](../../../GENESIS.md) ("only
geometry") tested on the warp-drive problem itself.

> **Firewall.** *Shift, energy, warp bubble, exotic* name structures of a **toy** lattice: `N` is a
> prescribed field, `16πρ` the quadratic invariant of its gradients. Nothing here is a spacetime, a
> measurement, or a device. Dimensionless; c = G = 1.

**Source:** lab [`warp-2-energy/0200-shaped-shift-energy`](../../../lab/warp-2-energy/0200-shaped-shift-energy) ·
gate `core/uniforge/tests/uf2_energy_structure_gate.rs`

---

## The hook  <!-- [PUBLIC] -->

The famous catch with a warp drive is that it seems to need *exotic* matter — stuff with **negative**
energy — and not just anywhere, but arranged in a very particular way. That sounds like an extra
ingredient you'd have to bolt on. It isn't. Take a lattice, push it along with a shift that is *shaped*
like a bubble (moving fast inside, still outside, with a wall in between), and then simply *measure the
energy of that shape*. The negative energy appears on its own — and it appears exactly where the theory
says it should: in a **ring around the bubble's waist**, vanishing straight ahead and straight behind.
The picture below is that ring, drawn from the numbers the engine computed.

## The prediction  <!-- [STUDY GUIDE] -->

Registered before the run (R1/P0–P3). Prior known physics (Alcubierre): the warp shift's energy density is
`ρ ≤ 0`, localized on the wall (`∝ f'²`), and toroidal (`∝ sin²θ`). Feeding our shift `N = vs·f(r)·ẑ`
through the functional `16πρ = (trK)² − K_ijK^ij` collapses **analytically** to
`16πρ = −½·vs²·f'(r)²·sin²θ` — the same three features. The gate checks the *discrete lattice* delivers them:

- **P0 (control):** a *uniform* shift (no wall) costs **zero** — moving is free, only shaping pays.
- **P1:** the energy is **negative** where significant (`neg_frac ≥ 0.98`, `min < −10⁻³`).
- **P2:** it is **wall-localized** (`mean|16πρ|_wall ≥ 10×` interior and exterior).
- **P3:** it is **toroidal** (`equator ≥ 5×` pole).

## Figure

**[▶ open the energy-structure figure](../../../lab/warp-2-energy/0200-shaped-shift-energy/figures/energy_structure.html)**
— left: where the energy lives, by radial band; right: the torus, each dot a measured angular bin on the
wall shell (brightness ∝ `|16πρ|`), pinching to nothing on the travel axis.

> **Fig. 1.** The shaped shift's energy: negative, wall-localized, toroidal. *Data-true (R10): rendered by
> `core/viz gen_energy` from `lab/warp-2-energy/0200-…/data/` (gate `uf2_energy_structure_gate`).*

## What happened

**In plain terms** <!-- [PUBLIC] -->: pushing the lattice uniformly is free — a bare translation costs
*exactly* nothing. The bill arrives only when you **shape** the push into a bubble, and the whole bill is
paid at the **wall**: the energy there is **336×** what's in the calm interior and **1360×** the far
field. Every bit of it is **negative** — the "exotic" requirement, appearing by itself. And it isn't
spread evenly over the wall; it forms a **ring around the equator** (perpendicular to travel) and fades to
nothing at the front and back. That ring *is* the warp-drive torus everyone talks about — here it's just
the geometry of a shaped push, measured.

**The numbers** <!-- [STUDY GUIDE] -->:

| prediction | expected | measured | pass |
|---|---|---|---|
| P0 · uniform shift `max\|16πρ\|` | `< 10⁻⁹` | **0.0** (exact) | ✅ |
| P1 · negative fraction | `≥ 0.98` | **1.0000** (100%) | ✅ |
| P2 · wall / interior | `≥ 10×` | **336×** | ✅ |
| P2 · wall / exterior | `≥ 10×` | **1360×** | ✅ |
| P3 · equator / pole | `≥ 5×` | **6.1×** | ✅ |

The angular profile falls **monotonically** from equator (`6.0×10⁻³`) to pole (`7.7×10⁻⁴`) — the `sin²θ`
torus, in nine bins. The result **rules in** the genesis tenet for warp: the three defining features of
warp-drive energy are not assumptions — they are consequences of the shift's geometry read through a
quadratic invariant. It **rules out** "the energy is a boundary/discretization artifact": the uniform
control costs exactly zero, so the functional charges only for the shaping, and the negativity is a real
property of the wall's **shear** (`trK² < K_ijK^ij`), not a sign convention.

## What *is* "negative"?  <!-- [STUDY GUIDE] -->

The energy splits exactly into two competing pieces — **expansion** and **shear**:

`16πρ = (2/3)·(trK)² − |σ|²  =  expansion − shear`

so **negative energy just means the shift shears the lattice faster than it expands it.** It is not an
invented mechanism, and not an interpretation — it is the sign of a fixed geometric invariant. Three
data-true rungs pin this down (the **[negative-energy catalog](../../../lab/warp-2-energy/figures/negative_catalog.html)**):

- **2.1 — negative *is* the shear term.** On the bubble wall, every negative cell has shear > expansion;
  the equatorial belt is essentially pure shear, and the poles are where expansion rises to *cancel* shear
  (so the energy fades to zero there). → lab [`0201`](../../../lab/warp-2-energy/0201-expansion-vs-shear).
- **2.2 — pure shear → negative *everywhere*.** A divergence-free shear layer (`trK≡0`) is negative at
  every cell; a shearless expansion field (`σ≡0`) is positive at every cell. No wall, no harmonics, no
  smooth-max needed — the sign is set by shear-vs-expansion alone.
  → lab [`0202`](../../../lab/warp-2-energy/0202-pure-shear-negative).
- **2.3 — nesting doesn't deepen; sharpness does.** Putting a second wall closer does *not* make the
  exotic skin deeper (the peak is flat across the gap); halving the wall width instead multiplies it ~4×
  (a `1/w²` law). Proximity buys more skins, not deeper ones.
  → lab [`0203`](../../../lab/warp-2-energy/0203-nested-walls).

> **Fig. 2.** The "what is negative?" catalog — the shear decomposition, the sign dyad, and the
> sharpness law. *Data-true (R10): `core/viz gen_energy_catalog` from `lab/warp-2-energy/{0201,0202,0203}`.*

## Can the photon pay the bill?  <!-- [STUDY GUIDE] -->

Alcubierre's question was really *"what source generates this?"* — and the answer was exotic matter. So
can **electromagnetism**, the field this whole engine is built on, supply it? Rung 2.4 puts a real EM
stress-energy on the lattice and asks (the **[EM figure](../../../lab/warp-2-energy/0204-can-the-photon-pay/figures/em_bill.html)**):

- **The sign says no.** Classical EM energy density is `ρ = ½(E² + B²) ≥ 0` — for *every* polarization it
  sits on the wrong side of zero. The wall demands `ρ < 0`; EM's floor is `0`. The photon **cannot pay the
  bill**. This is the energy-condition obstruction, now demonstrated in our own engine rather than quoted.
- **But polarization is the knob for the *shape*.** The Maxwell stress `σ_ij = E_iE_j + B_iB_j − ½δ_ij(E²+B²)`
  is shear-rich, and a linear polarization aims its principal (shear) axis *exactly* along the polarization
  angle; a circular state is isotropic. EM has all the shear you want — the shear that rung 2.1 says drives
  negativity — but its energy sign is stuck positive.

So EM is **the right shape, the wrong sign**. The sign is precisely where the **quantum vacuum**
(Casimir / squeezed light) would have to enter — a locally-negative energy density classical fields
forbid, and one bounded by quantum inequalities in real physics. That boundary is outside this toy; the
toy's job was to locate it exactly. → lab [`0204`](../../../lab/warp-2-energy/0204-can-the-photon-pay).

And it holds for the **real, propagated photon**, not just prescribed fields: rung 2.5 evolves `A` on the
edges with the engine's own incidence `d` (the curl-curl) and geometric Hodge star `⋆₁` (the Whitney edge
mass), and reads the energy `E = ½VᵀM₁V + ½c²AᵀKA` straight off those operators. That energy stays `≥ 0`
at every step, is **conserved** to 0.09% (it *is* the solver's Maxwell energy), and sloshes
electric↔magnetic like a real photon — the obstruction, unified with the genesis tenet's `d` and `⋆`.
→ lab [`0205`](../../../lab/warp-2-energy/0205-the-evolved-photon), figure
[photon energy](../../../lab/warp-2-energy/0205-the-evolved-photon/figures/photon_energy.html).

> **Fig. 3.** Demand vs supply: EM energy density is ≥0 for all polarizations (can't reach the wall's
> negative demand), while polarization steers the stress-shear axis. *Data-true (R10): `core/viz gen_em_bill`.*

## Where does the minus sign come from?  <!-- [STUDY GUIDE] -->

If a single field can't carry negative energy, where does a minus sign ever live? The answer:
**relational** quantities — and the knob is **charge / phase flipping**. The
**[sign catalog](../../../lab/warp-2-energy/figures/sign_catalog.html)** maps every classical route:

- **Charge product (2.6).** Two charges: the *interaction* energy `⟨E₁,E₂⟩` has sign `sign(q₁q₂)`. Flip a
  charge → it flips (negative for opposite = binding), while self-energies and the total stay `≥ 0`.
  → lab [`0206`](../../../lab/warp-2-energy/0206-coulomb-interaction-flip).
- **The stella's built-in C (2.7).** The lattice's matter/antimatter parity split *is* a charge
  conjugation: a matter–antimatter pair binds (negative interaction), matter–matter repels.
  → lab [`0207`](../../../lab/warp-2-energy/0207-stella-matter-antimatter).
- **Interference (2.8).** Two modes in quadrature build a negative energy density at their destructive
  fringes — but it is **bounded and paid back** (`∫ = 0`): locally negative, globally on loan. This is the
  classical shadow of the quantum vacuum (Casimir / squeezed light, Ford–Roman).
  → lab [`0208`](../../../lab/warp-2-energy/0208-interference-negative).

> **Fig. 4.** Three relational routes to a minus sign — charge product, the stella's C, and interference.
> *Data-true (R10): `core/viz gen_sign_catalog` from `lab/warp-2-energy/{0206,0207,0208}`.*

**The pattern:** every classical minus sign is relational, and every one is balanced or dominated. A *net*
negative — the thing a warp bubble actually needs — requires a **baseline to subtract**, and that baseline
is the quantum vacuum. The toy takes us exactly to that door and no further, honestly.

## The bill, in numbers — and why warp stays hypothetical  <!-- [STUDY GUIDE] -->

If the negative energy has to come from the quantum vacuum, *how much* can the vacuum lend, and how does
that compare to what a bubble needs? This is prior published physics (Alcubierre 1994; Ford–Roman 1995–96;
Pfenning–Ford 1997; Van Den Broeck 1999), computed as a budget — **not** a lattice result — in the
**[quantum-budget figure](../../../lab/warp-2-energy/0209-quantum-budget/figures/quantum_budget.html)**:

- **The vacuum lends weakly and briefly.** The Ford–Roman quantum inequality bounds sustained negative
  energy density as `|ρ| ≲ ℏ/(c³τ⁴)` — the longer you hold it, the weaker it must be (`τ⁻⁴`). It is
  rung 2.8's "paid back," made quantitative.
- **The quantum inequality forces a Planck-thin wall.** Requiring the Alcubierre wall to obey the QI drives
  its thickness to the **Planck scale** (Pfenning–Ford: ~10²–10³ Planck lengths) — where known physics
  itself runs out.
- **The macroscopic bill is astronomical.** A QI-consistent 100 m bubble needs a negative mass-energy of
  order **10¹² × the mass of the observable universe**.
- **The levers are the toy's own rungs — and none reaches zero.** Sharpen the wall (rung 2.3 — but
  Planck-thin is unphysical), shrink the payload volume (Van Den Broeck, `E ∝ R²`, ÷10³⁴ here — rung 2.3's
  menu), or lower the speed (`E ∝ v²`). They cut *tens of orders* off the bill; they never cancel the
  QI-bounded exotic requirement.

> **Fig. 5.** The gap on log ladders: what the vacuum can supply (Ford–Roman, Casimir) vs what the wall
> demands, and the bubble's total mass against the Sun and the universe. *All values prior physics;
> `core/viz gen_budget` from `lab/warp-2-energy/0209-quantum-budget`.*

**The honest end of the chapter.** The toy did its job precisely: it located the door (the exotic
requirement is real, it is a *shear* effect, and the minus sign is *relational* — it needs a vacuum
baseline), and it showed classical fields — including the photon this engine is built on — cannot open it.
The quantum inequality then prices the room beyond that door, and the price is astronomical. That is why
warp remains hypothetical: not a flaw the toy hides, but a boundary the toy draws honestly, in numbers.

## Reproduce

```bash
cd core
cargo test --release -p uniforge --test uf2_energy_structure_gate -- --nocapture  # writes data/*.csv
cargo run  --release -p viz     --bin gen_energy                                     # → the figure
```
Pinned in [`PROVENANCE.md`](PROVENANCE.md). Full scorecard in the lab entry's
[`eval.md`](../../../lab/warp-2-energy/0200-shaped-shift-energy/eval.md).

## Try it  <!-- [STUDY GUIDE] -->

- **Thin the wall** (`WALL = 2.5 → 1.5`): a steeper `f'` should make the energy *more* negative — the
  classic "thinner wall costs more exotic matter." Predict the change in `min`, then run.
- **Recompute through the geometric `⋆`** (`dec::hodge`) instead of central differences: does the torus
  survive on the *engine's* geometry? That unifies this result with the light-cone chapter — the harder
  sibling, and the next rung in the [chapter menu](../../../lab/warp-2-energy).
- **Turn off the shaping** (`f ≡ 1`): confirm P0 by hand — why does a bare boost carry no energy at all?

---

## Addendum — nothing about 1/r went in, and the inverse-square law came out <!-- [PUBLIC] -->

This chapter has used charges before — to chase the minus sign, we prescribed a Coulomb-shaped
potential and asked what its energy did. That is a fine way to answer *that* question and a useless
way to answer this one, because the answer is typed in.

So we did it the other way round. Pin a "charge" at the middle of a lattice box. Ground the outside
of the box. Then let the engine **solve** for the field between them — a linear solve on the same
discrete Laplacian the wave chapter uses, with no formula for the potential supplied anywhere. Read
the field strength off the lattice, average it over shells at each radius, and hand the machine two
columns of numbers and five candidate laws: *constant, one over r, one over r squared, one over r
cubed, one over r to the fourth.*

It picked one over r squared, by a wide margin.

**Source:** lab [`warp-2-energy/0210-coulomb-discovery`](../../../lab/warp-2-energy/0210-coulomb-discovery)
· gate `core/uniforge/tests/uf2_10_coulomb_discovery_gate.rs` — the second task on the
Discovery-Bench checklist (#46), after the light cone.

**The part that is not a curve fit** <!-- [PUBLIC] -->: getting the *shape* right is the easy half.
The fit also needs a number out front — how strong the field is — and that number turns out to be the
charge. We can measure the charge a completely different way, without any fitting at all: add up what
the operator itself says is inside a sphere. That is Gauss's law, and on this lattice it is exact —
the sum came out identical to nine digits whether the sphere had radius 4, 8, 12 or 16, because the
arithmetic telescopes. The two numbers agree to **0.72%**. One of them never looks at a radius; the
other never looks at the operator.

**The control that can fail** <!-- [PUBLIC] -->: a detector that always answers "inverse square" would
have answered it here too. So we ran the whole thing again with two opposite charges a couple of cells
apart — a dipole — changing nothing else at all. The same pipeline came back with **one over r
cubed**, which is the right answer for a dipole and the wrong answer for everything else it might
have said.

**The predictions (R1, probe-informed)** <!-- [STUDY GUIDE] -->: P0 — the solve converges and Gauss's
law is radius-independent to `1e-9`. P1 — the selector returns `−2` with an R² margin > 0.15, and the
free exponent lands in `−2.00 ± 0.05`. P2 — `4πC` from the fit matches the Gauss charge to better
than 1.5%. P3 — the near field is *worse*, in a specific pre-registered way. P4 — the dipole returns a
different exponent.

**Figure:** [▶ open the Coulomb figure](../../../lab/warp-2-energy/0210-coulomb-discovery/figures/coulomb.html)
— the profile with the rejected laws visibly peeling away, the same data compensated by r² (a flat
line *is* an inverse-square law, and its height *is* the charge), and the monopole-vs-dipole
scorecard.

**What happened, including the honest part:** all five held on the first run. And P3 is the one worth
reading. Close to the source — within about three cells — the lattice is *not* Coulombic: the
exponent there is `−2.19` and the coefficient is 8% too big. We predicted that before running, and we
predicted *why*: on a lattice a "point charge" is not a point, it is a pinned vertex, so the near
field is measuring the pixel rather than the physics. The way to tell that story from the alternative
— "your box is too small" — is to make the box bigger. We did, by 40%, and the error moved by less
than one part in ten thousand. It is the grid spacing, and no amount of extra room will fix it. Full
scorecard in [`eval.md`](../../../lab/warp-2-energy/0210-coulomb-discovery/eval.md).

*(Firewall: a toy lattice operator with pinned vertices, and fits to its own numbers. "Charge",
"field" and "Coulomb" name properties of that operator — never a real charge, a real field, or a
measurement of any physical coupling. The `4π` is the textbook conversion used to score one route
against the other, not something the lattice derived.)*
