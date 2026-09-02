# 04 · The vacuum — the one place negative energy is real, and the lattice as an automated lab

**Concept:** empty space is not empty. Confine a quantum field between two plates and its zero-point energy
drops **below** the free vacuum — a genuinely **negative** energy density (the Casimir effect). This is the
one mechanism that gives the `ρ < 0` chapters 2–3 proved classical fields and shields can't. We build it on
the lattice, where the discrete spectrum is its own cutoff (no regularization trick), and we let the bench
**discover the law itself** — proving the lattice works as a cheap, automated science lab.

> **Firewall.** *vacuum, Casimir, plate, mode, energy* name the zero-point energy `½Σℏωₖ` of a **toy**
> scalar field (a fixed–fixed oscillator chain = the engine's Dirichlet Laplacian) on a **toy** lattice.
> `ℏ` is a dimensionless bookkeeping constant. This is standard QFT zero-point bookkeeping — **not** a real
> Casimir device, **not** free energy, **not** a spacetime claim. Dimensionless; c = 1.

**Source:** lab [`warp-4-vacuum/0400-casimir-negative-energy`](../../../lab/warp-4-vacuum/0400-casimir-negative-energy) ·
gate `core/uniforge/tests/uf4_casimir_energy_gate.rs`

---

## The hook  <!-- [PUBLIC] -->

Chapters 2 and 3 hit a wall: a warp drive needs a region of *negative* energy, and every classical trick we
tried gives zero or more, never less. Real physics has exactly one escape hatch — the **quantum vacuum**.
Even "empty" space hums with zero-point energy, and if you put two plates close together you forbid some of
that hum between them. The result is that the space *between* the plates has **less** energy than empty space
outside — a measured, Nobel-adjacent fact (the Casimir effect, and the plates are pulled together). So we
build it on our lattice and ask two things: does the vacuum really go negative here? And — the bigger point
— can the lattice act as an *automated lab* that finds the physical law on its own?

## The prediction  <!-- [STUDY GUIDE] -->

Registered before the run (R1). The zero-point energy of the confined field is `E₀ = ½Σℏωₖ`, summed over the
normal modes `ωₖ` of a field pinned to zero at two "plates." On the lattice those `ωₖ` are exactly the
eigenvalues of the engine's Dirichlet Laplacian, and the sum is **finite** — the lattice spacing is a
built-in cutoff, so no zeta-function sleight of hand is needed. **(A)** After subtracting the bulk vacuum,
the confined energy `E_C(a)` is **negative** at every plate separation `a`. **(B)** the automated fit will
recover `E_C(a) = c₀ + c₁/a` with a surface term `c₀ → −½` and the universal **Casimir coefficient**
`c₁ → −π/24`, exponent `−1` — *discovered from the data, not hardcoded.*

## Figure

**[▶ open the Casimir figure](../../../lab/warp-4-vacuum/0400-casimir-negative-energy/figures/casimir.html)**
— the confined vacuum energy dipping below zero with the discovered fit overlaid, and a scorecard of exactly
what the bench extracted (surface term, Casimir coefficient, exponent, R²) held against theory.

> **Fig. 1.** `E_C(a)` vs plate separation with the auto-discovered law `c₀ + c₁/a`, and the discovery
> scorecard. *Data-true (R10): `core/viz gen_casimir` from `lab/warp-4-vacuum/0400`.*

## What happened

**In plain terms** <!-- [PUBLIC] -->: the vacuum went negative — every measured point sits below the
free-space line, and the closer the plates, the deeper it goes (that downhill slope *is* the attractive
Casimir force). And the lattice found the textbook law by itself: sweep the plate spacing, fit the numbers,
and out come the surface term (−0.500 vs the exact −½) and the Casimir coefficient (**−0.13099 vs the exact
−π/24 = −0.13090, a 0.07% match**), with the power-law exponent pinned at −1.00 and a fit quality of
0.9999999. Nobody typed those constants in — the automation discovered and checked them.

**The numbers** <!-- [STUDY GUIDE] -->:

| | discovered | theory | reading |
|---|---|---|---|
| spectrum vs Laplacian | `Σωₖ²=30, Σωₖ⁴=88` | `2N=30, 6N−2=88` | the modes *are* the engine's `d†d` |
| confined energy sign | `−0.516 … −0.502` | `< 0` | the vacuum is exotic (`ρ<0`) |
| surface term `c₀` | `−0.4999997` | `−½` | the two plate edges |
| Casimir coefficient `c₁` | `−0.13099` | `−π/24 = −0.13090` | **the universal law, to 0.07%** |
| exponent · R² | `−0.9997 · 0.9999999` | `−1 · 1` | it really is `1/a` |

The result **rules in** genuine negative energy — the sign classical EM (2.4) and shields (3.4) could never
reach — and **rules in the lattice as an automated bench**: it ran a parameter sweep and *extracted a
physical law*, coefficient and all, with the analysis done by the harness, not the author. That is the
value-add the whole program is arguing for — experiments cheaper and faster than a wet lab, whose results
are automatically fit and theory-checked.

Two honest fences remain. The negative energy is **real but bounded**: it is static (so it doesn't violate
the Ford–Roman quantum inequalities, which limit *time-sampled* negative energy) yet its magnitude is tiny
and steep (`∝1/a` here, `∝1/a⁴` for the 3D force), so meeting the warp-wall demand would force Planck-thin
plates — the same wall as chapter 2.9. And this is **bookkeeping, not a battery**: the Casimir energy is a
shift in the vacuum baseline, not extractable free energy. What the toy shows cleanly is *where* negative
energy comes from, and that the bench can find its law unaided.

## The force, subtraction-free — and a second discovered law  <!-- [STUDY GUIDE] -->

The energy above needed a bulk subtraction to expose the negative piece. The **force** needs none: put a
*movable* plate — a piston — in a long chain and measure the force on it as the change in total zero-point
energy when it shifts. Because the total length is fixed, the bulk and surface energies cancel exactly, and
what's left is the physical Casimir pull. It comes out **attractive** at every separation, **zero** for a
symmetric split, and **independent of the far wall** (doubling the bath changes it by 5 parts in 10⁵) — a
purely local property of the near plate. And the bench discovers the force law too, now with a **different
exponent** than the energy:

| discovered | from the run | theory |
|---|---|---|
| force exponent | `−2.007` | `−2` |
| coefficient `\|F\|·a²` | `0.1315` | `π/24 = 0.1309` (0.5%) |
| symmetric-split force | `−3×10⁻¹¹` | `0` |
| far-wall dependence | `5×10⁻⁵` | `0` |

That the same law-finder returns `−1` for the energy and `−2` for the force — from the same lattice machinery
— is the point: it is reading the physics, not repeating a constant. → lab
[`0401`](../../../lab/warp-4-vacuum/0401-casimir-force-piston).

## Reproduce

```bash
cd core
cargo test --release -p uniforge --test uf4_casimir_energy_gate -- --nocapture  # writes data/*.csv
cargo run  --release -p viz     --bin gen_casimir                                  # → the figure
cargo test --release -p uniforge --test uf4_casimir_force_gate  -- --nocapture  # the piston force
```
Full scorecard: the lab entry's [`eval.md`](../../../lab/warp-4-vacuum/0400-casimir-negative-energy/eval.md).

## The bench, generalized: one law-finder, many laws  <!-- [STUDY GUIDE] -->

The two rungs above each ran a fit inside their gate. The chapter's larger claim — *the lattice is a cheap
automated lab* — is worth making structural, so the fit became a **reusable engine tool**
(`kinematics::power_law_fit`, with its own unit tests) and we pointed the *same* function at three unrelated
experiments. It recovers a synthetic law exactly; it rediscovers the Casimir force scaling from the raw
zero-point energy; and — through the Laplacian **heat kernel** — it *measures the lattice's own spatial
dimension*. The heat-kernel trace decays as `K(t) ∝ t^{−d/2}`, so on log–log axes each dimension is a
straight line of slope `−d/2`, and the fitter reads dimension `= −2·slope`:

| the one fitter found | discovered | theory |
|---|---|---|
| synthetic `3·x⁻²` | exponent −2.000, coeff 3.000 | −2, 3 |
| Casimir force `\|F\|` vs a | exponent −2.007 | −2 |
| lattice dimension, d = 1 / 2 / 3 | **1.002 / 2.004 / 3.006** | 1 / 2 / 3 |

Three experiments, three *different* exponents (−1 for the Casimir energy, −2 for the force, −d/2 for the
heat kernel), all from the same tested function — the automation is reading the physics, not echoing a
hardcoded constant. That is the value-add the whole program argues for: experiments cheaper than a wet lab,
with the analysis *and* the theory check done by the harness. → lab
[`0402`](../../../lab/warp-4-vacuum/0402-automated-bench), figure
[the automated bench](../../../lab/warp-4-vacuum/0402-automated-bench/figures/bench.html).

## Harder numbers: π, ln 2, and the Madelung constant  <!-- [STUDY GUIDE] -->

How hard a number can the bench reach? We pushed it at three famous constants, each from a lattice sum and
each sharpened by a *different* automated technique (all reusable engine tools). **π** comes straight out of
the confined vacuum — the Casimir coefficient is `−π/24`, and one Richardson extrapolation of the swept
values gives `π = 3.141592626` (7–8 digits). **ln 2** is the one-dimensional ionic-chain Madelung constant
`2Σ(−1)ⁿ⁺¹/n`; the raw sum is stuck at 3 digits, but series acceleration of 24 partials nails it to
`3.7×10⁻¹⁰` — a **×2.7-million** gain, so the automation *is* the result. And the **NaCl Madelung constant**
`1.7475646` — the canonical hard number of lattice electrostatics — falls out of an Evjen neutral-cube sum,
converging monotonically to six digits.

| the lattice computed | to | via |
|---|---|---|
| **π** | 3.141592626 (err 3×10⁻⁸) | Casimir coefficient + Richardson |
| **2·ln 2** | 1.386294361 (err 4×10⁻¹⁰) | Madelung + series acceleration |
| **NaCl Madelung** | 1.74756380 (err 8×10⁻⁷) | Evjen neutral cubes |

→ lab [`0403`](../../../lab/warp-4-vacuum/0403-harder-numbers), figure
[harder numbers](../../../lab/warp-4-vacuum/0403-harder-numbers/figures/hardnum.html).

> **Firewall (R3), sharply.** These are **mathematical / lattice-sum** constants — the lattice computes them
> *by definition* (they are what those sums equal). That is categorically different from an **empirical
> constant of nature** such as the fine-structure constant α ≈ 1/137.036, which is *measured*, has no
> accepted first-principles derivation, and is nowhere contained in this toy. The bench can compute π; it
> cannot — and must not claim to — "derive α." Hitting 137 with a lattice formula would be numerology, the
> exact thing the firewall exists to forbid.

## How a measurement is taken — the energy number, and what could be a prediction  <!-- [STUDY GUIDE] -->

Everything above quoted numbers — but a number means nothing until you say *in what units*. A toy can only
measure **ratios to a standard**, so we give the toy one **energy number** `E₀` (its fundamental quantum —
every mode energy is `εₖ = E₀·fₖ`) and make the measurement explicit. Then the sharp test: rescale the
standard, `E₀ → 3.7 E₀`, and re-measure. The **dimensionless** quantities don't move — the frequency ratio
`ε₅/ε₁` and the Casimir coefficient `−π/24` are identical to machine precision — while the **dimensionful**
ones (a mode energy, the total Casimir energy) scale by exactly 3.7. A number that changes when you change
your arbitrary unit is not telling you about the world.

That gives the criterion that governs the whole project: **a result can be a prediction of nature only if it
is dimensionless *and* parameter-free** (and, by R1, pre-registered — committed before the run, so it can't
have been fitted). The Casimir coefficient qualifies; a raw energy does not. We apply this criterion to every
rung in the **[predictions ledger](../../../PREDICTIONS.md)** — the honest scoreboard of what the toy
*predicts* versus what it *assumes*. → lab [`0404`](../../../lab/warp-4-vacuum/0404-energy-number), figure
[the energy number](../../../lab/warp-4-vacuum/0404-energy-number/figures/energynum.html).

> **The north star.** *An accurate toy is still a toy; a toy that predicts is no longer a toy.* So far this
> toy **accurately reproduces** known physics, parameter-free — genuine postdictions. It has not yet output a
> novel, measured number it wasn't built to know. The firewall (and R1) exist precisely so that if it ever
> does, the prediction will be believable rather than a tuned coincidence.

## Try it  <!-- [STUDY GUIDE] -->

- **Hold it against the warp bill** (menu): the static negative density vs the Ford–Roman budget and the
  warp-wall demand of 2.9 — why even real negative energy leaves warp Planck-limited.
- **Grow the law-finder** (menu): model selection (power vs exponential vs log by R²/AIC), a bootstrap error
  bar, more accelerators (Aitken Δ², Wynn's ε), and other hard lattice numbers (Catalan's constant, the
  Watson lattice-Green's-function integral).
