# 0304 — Warp-3.4: the four-source null — evaluation

**Verdict:** CONFIRMED (R5/R10) · **Gate:** `uf3_4_four_source_null_gate` (green: yes) · **Commit:** `2f81902` (registered `530a325`)

## Result

**The conjecture is backwards — orthogonal polarizations cannot empty a volume, and the reason is exact.**
Energy density is `⟨ρ⟩ = ¼(|Ê|²+|B̂|²)`; for orthogonally-polarized fields the cross term vanishes, so their
energies **add** rather than cancel. Orthogonality is precisely the wrong tool for a null. The lattice
confirms it to machine precision, and pins down the only way superposition ever empties a region (the
trivial one).

| prediction | expected | measured | pass |
|---|---|---|---|
| P0 single wave: uniform energy | `CoV<1%`, residual≈1 | **CoV 0, residual 1.00** | ✅ |
| P1 standing wave: E-nodes, energy uniform | `CoV<2%`, residual∈[0.95,1.05] | **CoV 0, residual 1.00** | ✅ |
| P2 orthogonal set: phase-independent | phase-sweep `CoV<0.1%` | **CoV 1.1×10⁻¹⁶** | ✅ |
| P2 orthogonal set: energies add | `=` sum-of-parts `<1%` | **3.00 = 3×1.00, err 0** | ✅ |
| P2 orthogonal set: can't null | cube residual `>0.8` | **1.00** | ✅ |
| P3 only volume null is trivial | antiphase `max⟨ρ⟩<1e-9` | **1.8×10⁻³⁰** (field ≡ 0) | ✅ |

The numbers are analytic, not noisy: a standing wave's `cos²(kz)+sin²(kz)=1` makes `⟨ρ⟩` *exactly* uniform
(a node in E is an antinode in B — the energy just sloshes, it never disappears); the three
perpendicular pairs deposit their six field components on six distinct axes, so their energies sum with **no
interference term** and the center value `3.0` is completely independent of all three pair phases; and the
only way to drive `⟨ρ⟩→0` over a region is to make the field identically zero everywhere (parallel antiphase
waves), which is no shield at all. Data: [`data/null_configs.csv`](data/null_configs.csv),
[`data/phase_sweep.csv`](data/phase_sweep.csv), [`data/radial.csv`](data/radial.csv). Figure:
`core/viz gen_null`.

## What it rules in / out

- **Rules OUT the "orthogonal polarizations null a region" conjecture (R5):** orthogonal fields don't
  interfere — `|ΣÊ|² = Σ|Ê|²` — so stacking orthogonal polarizations *raises* the energy (it adds sources),
  it never cancels. To cancel you need **parallel** (non-orthogonal) fields.
- **Rules OUT a free-space volume null (unique continuation):** parallel fields *can* cancel, but a
  non-trivial Maxwell field that vanishes on an open set vanishes on the whole connected source-free region.
  So the only superposition null over a volume is the trivial field-zero-everywhere case — darkness, not a
  shield. A null over a finite region with field outside is impossible without sources inside/around it.
- **Rules OUT "complete shield → negative energy" (ties to rung 2.4):** even a perfect null is `⟨ρ⟩ = 0`,
  never `< 0`. EM energy is sign-locked non-negative (2.4/2.5); a shield can empty a region but cannot make
  it exotic. Negative energy needs the quantum vacuum (Casimir / squeezed light), which is Ford–Roman
  bounded (2.9) — not a classical polarization trick.
- **Names the achievable route:** a genuine interior null *is* possible — with a **boundary of real
  currents** (a Faraday cage / a Huygens equivalent-source surface enclosing the region), exactly the
  boundary-shield picture of rungs 3.0–3.2. The null is a *boundary* phenomenon, not a free-space
  superposition, and it costs real sources.

## Deferred / next

Feed the chapter menu: the **Huygens/Faraday boundary null** (surround the target with equivalent surface
sources and show the interior field cancels — the achievable complete shield, and its current budget); and
close the loop to chapter 2 by stating plainly that the shield program tops out at `⟨ρ⟩ ≥ 0` — the exotic
(negative) demand stays with the quantum vacuum.
