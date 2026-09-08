# 0700 — the stella random-walk constant: evaluation

**Verdict:** CONFIRMED · **Gate:** `uf7_0_watson_gate` (green: yes) · **Commits:** registered `2cbe186`, fix `ff649a2`, run `cf357dd`

## Result

The machinery reproduces Watson's exact closed forms on SC and FCC with zero tuning, and the same
ladder on the engine's own stella tet-oct graph registers a **new lattice constant**:

> **G_stella = 1.302310014103**, return probability **p_stella = 0.232133678486** —
> the simple-random-walk return constant of the stella tet-oct complex graph
> (FCC + the screw-assigned octahedral long diagonals; 14-regular, vertex-transitive).
> As far as we know this number is unpublished mathematics — the repo's own Madelung number.

| quantity | expected (registered) | measured | pass |
|---|---|---|---|
| P0 · G_SC vs Watson closed form | `1.516386059151978 ± 1e-10` | err `2.79e-13`; raw-error ratios 1.9999/2.0000/2.0000 (the 1/M law) | ✅ |
| P1 · G_FCC vs Watson 1939 | `1.344661183165145 ± 1e-9` | `1.344661183159` (err `6.05e-12`) | ✅ |
| P1 · p_FCC | `0.256318236504649 ± 1e-9` | err `3.35e-12` | ✅ |
| P2a · mesh d0 adjacency == rule | exact, every interior vertex | 365/365 vertices exact (n=12) | ✅ |
| P2b · real-space CG vs Bloch k-sum (M=24) | `< 1e-10` | `6.88e-15` | ✅ |
| P3 · G_stella | `1.3023100141 ± 1e-8` | `1.302310014103` (err `3.07e-12`) | ✅ |
| P3 · p_stella | `0.2321336785 ± 1e-8` | `0.232133678486` (err `1.39e-11`) | ✅ |
| P3 · ladder consistency (ord5 vs ord3) | `< 1e-9` | `2.42e-12` | ✅ |
| P3 · dynamics bound S₈ < G, S₈ registered | `1.166371405 ± 1e-9` | `1.166371405` (< G) | ✅ |

Data: [`data/`](data). Figure: [`figures/watson.html`](figures/watson.html) (rendered by
`core/viz gen_watson` from `data/` only, commit-stamped `cf357dd`).

## Fix vs the registered gate (R5)

The **first run-for-record failed** — not on a registered prediction but on the gate's *internal*
machinery sanity assert: the Hermiticity check on the 3×3 Bloch trace was registered as an
**absolute** bound (`max|Im| < 1e-9`), and at `M=384` the rounding residue of the analytically-real
trace reached `1.81e-9` — because the residue scales with the `k→0`-amplified real part
(`Re ~ 10⁴` near the deflated mode). A follow-up probe measured the **relative** residue at
`≤ 1.4e-13` for all `M ≤ 384`; the bound is now relative (`|Im|/(1+|Re|) < 1e-11`, two orders of
margin). Classification: **coding bug (an unprobed internal threshold), not a wrong prediction** —
P0–P3 and their tolerances were untouched (`fix:` commit `ff649a2`). Lesson appended to
`lab/LESSONS.md`: probe *internal* sanity thresholds too, and bound rounding residues relative to
the quantity they ride on.

## What it rules in / out

- **The answer keys license the machinery.** The deflated-torus k-sum + order-(1,3,5) Richardson
  ladder lands on two independent Γ-function closed forms (SC `2.8e-13`, FCC `6.1e-12`) from raw
  sums that are only good to `3e-3` at `M=384` — acceleration, not compute, is the precision lever
  (the 4.3 lesson, confirmed again). The FCC value is **3 digits beyond** the issue's 1e-6 floor
  with ~3 orders of assert margin.
- **The stella number is the complex's, not a model's.** The Bloch model's hop set was proven equal
  to the engine mesh's own `d0` adjacency vertex-by-vertex (P2a), the k-space and real-space routes
  agree to `7e-15` (P2b), and the open-mesh return series brackets the constant from below (S₈) —
  three independent legs under one number.
- **Vertex-transitivity holds** (the screw structure notwithstanding): the R9 brute-force oracle and
  the CG solve both return the class-independent `g[0]` that the trace formula assumes.
- **Ruled out:** the naive absolute-Hermiticity bound as a valid sanity gate near deflated modes
  (see the R5 fix above).

**Honest caveats.** The stella constant has no external answer key; its error bar is *internal*
(ladder self-consistency `2.4e-12`, plus the two exact answer keys run through identical machinery).
The registered `±1e-8` is conservative by ~3.5 orders. `S₈` is a strict but loose bound (coverage
`~0.90·G`); it guards against gross machinery error, not the last digits. FIREWALL (R3): all of
this is bucket 🔵 — facts of graph mathematics on a toy complex, not claims about nature.

## Deferred / next

- **BCC Watson constant** (`Γ(1/4)⁴/(4π³)` answer key) — one more scalar λ(k), near-zero cost,
  hardens the bench. → chapter menu.
- **The 11-simplex complex constant** (`geom::mesh_11d`) — the same "our own Madelung" move on the
  other in-house geometry. → chapter menu.
- **First-passage moments / Kemeny constant** on the stella graph — the next moments after G(0,0).
  → chapter menu.
- **Off-diagonal decay G(0,r)** — the lattice-Coulomb tail; would connect this chapter to the 4.3
  Madelung machinery. → chapter menu.
