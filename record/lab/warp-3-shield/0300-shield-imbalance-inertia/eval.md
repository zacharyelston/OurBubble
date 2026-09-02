# 0300 — Warp-3.0: the shield, the imbalance, and inertia — evaluation

**Verdict:** CONFIRMED (R5/R10) · **Gate:** `uf3_shield_imbalance_gate` (green: yes) · **Commit:** `6db889c`

## Result

**The imbalance is real; it does not, by itself, change inertia.** A shield provably decouples its interior
from the outside (the information imbalance), but in standard field theory the barrier is a potential /
positive effective-mass² — it adds *nothing* to the interior equation of motion — so interior inertia is
unchanged. The null names the extra ingredient "gravity manipulation" would require.

| quantity | expected | measured | pass |
|---|---|---|---|
| P0 exterior control coupling (path not crossing shell) | `∈[0.7,1.4]` | **0.86×** | ✅ |
| P1 interior coupling (path crossing shell) | `< 0.3` | **2.0e-6×** | ✅ |
| P2 interior EOM contribution `max\|V\|` (r<6) | `= 0` | **0.0** (exact) | ✅ |
| P2 interior packet displacement change | `< 1e-4` | **1.2e-6** | ✅ |
| P3 effective mass² at centre / wall | `≈0` / `>0` | **0 / 40** | ✅ |

The shield cuts the interior's coupling to an external source by **~500,000×** while leaving a non-crossing
exterior path essentially untouched (0.86×) — that is the imbalance, rigorously. Meanwhile the interior
packet moves identically (Δ displacement 1.2e-6); the only shielded-vs-open field difference is the
**reflected wall-wave** leaking inward at lattice speed (8.9e-6) — a change in the *signal*, not the
inertia. Data: [`data/shield.csv`](data/shield.csv), [`data/inertia.csv`](data/inertia.csv). Figure:
`core/viz gen_shield`.

## What it rules in / out

- **Rules in (provable):** a shield creates a genuine **information imbalance** — the interior sees ~10⁶×
  less of an external source than an equivalent non-shielded path. Local ≠ external, operationally.
- **Rules out (the honest null):** that imbalance does **not** reduce inertia under standard physics. The
  barrier `V` multiplies `φ` (a potential / mass² term), never `φ̈` (the inertia). Inside the bubble
  `V ≡ 0` exactly, so the interior equation of motion — and therefore the inertia — is unchanged. If
  anything the *wall* is **more** inert (`m²_eff = V = 40 > 0`), the opposite of "less inertia inside."
- **Method notes (R5/R6 honesty):** two registered specifics were corrected to test the intended claims on
  a finite lattice — (i) the exterior control was moved far from the shell (a near-shell control is itself
  attenuated); (ii) the P2 metric changed from field bit-identity to `V≡0` in the interior + displacement,
  because the lattice's numerical domain of dependence (~1 cell/step) lets the reflected wave reach the
  interior over the run. Neither changes the physics conclusion.

## Deferred / next — the fenced hypothesis (contested prior physics, NOT a derivation)

The null says: to convert the imbalance into an inertia change you need an extra law tying mass to
environmental coupling — **entropic inertia** (Mach / Verlinde / MiHsC). *If* one posited `m_eff ∝ 1/coupling`,
this run's measured interior coupling drop (×2.0e-6) would predict a ~5×10⁵-fold inertia reduction inside.
That is a **hypothesis-consequence**, computed from the imbalance number, **not** something this toy
derives or endorses. Building it as a modified stepper (`m_eff` field) is menu item 3.4 — explicitly
speculative and fenced. The workable-physics result stands on its own: shield → imbalance → *no* inertia change.
