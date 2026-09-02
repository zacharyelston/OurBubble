# 0304 — Warp-3.4: the four-source null — can orthogonal polarizations empty a volume?

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf3_4_four_source_null_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

The conjecture that opened this chapter's endgame: *"~4 orthogonal polarizations null an area completely,
and a complete null gives a negative-energy region."* This rung tests it head-on. We superpose coherent
monochromatic plane waves (the most favorable, fully-coherent case) on the lattice and read the
time-averaged energy density `⟨ρ⟩ = ¼(|Ê|²+|B̂|²)` off the engine's own `kinematics::em` functional. The
physics predicts the conjecture is **backwards**: orthogonally-polarized fields do not interfere (their
energies *add*), so orthogonality is exactly the wrong tool for cancellation; and the parallel fields that
*can* cancel can only vanish on measure-zero nodal sets, never a finite volume (unique continuation for
Maxwell). We register that as a first-class negative and name the achievable alternative.

## Firewall (R3)

`source, null, polarization, energy` name coherent classical plane-wave superpositions on a **toy** lattice,
with `⟨ρ⟩ = ¼(|Ê|²+|B̂|²)` the standard time-averaged EM energy density (`kinematics::em_energy` on the
real/imaginary field snapshots). No device/spacetime/matter claim; the quantum vacuum is **not** modelled.
Dimensionless; c = 1.

## Predictions (registered before the run)

- **P0 (control — a traveling wave carries uniform energy):** a single plane wave has spatially uniform
  `⟨ρ⟩` — *gate:* coefficient of variation `CoV < 1%` and target-cube residual (cube mean / domain mean)
  `∈ [0.98, 1.02]`.
- **P1 (a standing wave nulls E but not energy):** counter-propagating equal, *parallel*-polarized waves
  give E-nodes on planes, yet `⟨ρ⟩` is spatially **uniform** (the E-node is a B-antinode — energy just
  sloshes E↔B) — *gate:* `CoV < 2%` and cube residual `∈ [0.95, 1.05]` (no energy null despite the E-nodes).
- **P2 (orthogonal polarizations ADD — the conjecture's fatal flaw):** three mutually-perpendicular
  standing-wave pairs ("orthogonal polarizations") give an energy density that is **phase-independent** and
  equal to the *sum* of the parts — sweeping every pair phase leaves `⟨ρ⟩` unchanged, and it never dips
  below the ambient — *gate:* over a full phase sweep the center `⟨ρ⟩` has `CoV < 0.1%`, equals the
  sum-of-pairs to `< 1%`, and the cube residual stays `> 0.8` (cannot be nulled).
- **P3 (the only superposition that empties a volume is the trivial one):** the sole way to drive `⟨ρ⟩ → 0`
  over a region with superposition is *parallel* co-propagating waves in antiphase — which cancel the field
  **everywhere** (`max ⟨ρ⟩ ≈ 0`), i.e. no field at all, no shield. A non-trivial field cannot be nulled on
  an open set (unique continuation) — *gate:* the antiphase config has `max ⟨ρ⟩ < 1e-9` over the whole
  domain (a volume null exists ⟺ the field is identically zero).

## Method (sketch)

Grid `N=24`, spacing 1, wavelength `λ=8` (`k=2π/λ`, domain = 3λ). Each source is a complex plane wave
`Ê e^{i k·x}` with `B̂ = k̂ × Ê`; total field is the coherent sum. Time-averaged energy
`⟨ρ⟩(x) = ½·(em_energy(Ê_re, B̂_re) + em_energy(Ê_im, B̂_im)) = ¼(|Ê|²+|B̂|²)` (`kinematics::em_energy`).
Configs: (0) single wave; (1) counter-prop parallel-pol standing wave; (2) three perpendicular pairs — pair
A `±ẑ, x̂`; B `±x̂, ŷ`; C `±ŷ, ẑ` — the "orthogonal polarization" set, with a phase sweep on the three pairs;
(3) co-propagating antiphase pair (trivial global cancellation). Figure-of-merit: cube residual (mean `⟨ρ⟩`
over a `λ/2` central cube ÷ domain mean), center `⟨ρ⟩`, `CoV`, `max/min ⟨ρ⟩`. Emit `data/null_configs.csv`,
`data/phase_sweep.csv`, `data/radial.csv`.

## What would falsify this

If the three-pair "orthogonal polarization" set produced a center `⟨ρ⟩` that dropped toward zero as phases
were tuned (P2), or if any non-trivial superposition drove the cube residual to ~0 without zeroing the field
everywhere (P3), the conjecture would be *vindicated* and unique continuation violated — a major positive
result. The gate is written so either outcome is recorded honestly (R5).
