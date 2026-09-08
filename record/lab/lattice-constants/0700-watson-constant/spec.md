# 0700 — Lattice-constants-7.0: the stella random-walk constant (the Watson integral on our own graph)

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf7_0_watson_gate.rs` · **Status:** CONFIRMED (see [`eval.md`](eval.md))

## Goal (one paragraph)

Compute the simple-random-walk **return-probability constant** — equivalently the lattice Green's
function `G(0,0) = Σ_t p_t(0,0)`, with return probability `p = 1 − 1/G` — on (a) the **FCC vertex
graph** (the stella complex's vertex set with its 12 face-diagonal bonds), where Watson's exact 1939
closed form is the answer key, and (b) the **full stella tet-oct complex graph** (FCC + the
screw-assigned octahedral long-diagonal bonds, 14-regular), whose value is — as far as we know —
unpublished mathematics: a new registered lattice constant, the repo's own Madelung number
(issue #155; rung 4.3 is the template).

## Firewall (R3)

*Random walk, return probability, Green's function* are graph sums over a **toy** lattice complex.
Both constants are bucket 🔵 (`PREDICTIONS.md`): dimensionless facts of mathematics about graphs,
exact and un-tuned — **not** predictions about nature. The stella value is *a constant of this
complex*, not a property of matter. Dimensionless; c=1.

## The answer key (verified against two independent references before registration)

For a walk with structure function `λ(k)` (the Fourier transform of the single-step distribution),
`G(0,0) = (1/(2π)³)∫_BZ d³k / (1 − λ(k))`. Closed forms:

- **FCC** (Watson 1939, "Three triple integrals", *Quart. J. Math. Oxford* **10**, 266; confirmed in
  Glasser & Zucker, *PNAS* **74** (1977) 1800, and Silagadze, *J. Stat. Phys.* **145** (2011), both of
  which give the Watson integral `F(0,0,0;3) = 3/(2^{14/3}π⁴)·Γ(1/3)⁶ = 0.4482203944`):

  `G_FCC = 9·Γ(1/3)⁶ / (2^{14/3}·π⁴) = 3·F(0,0,0;3) = 1.344661183165145` (f64 evaluation)
  `p_FCC = 1 − 1/G_FCC = 0.256318236504649`

- **SC control** (same two references): `G_SC = √6/(32π³)·Γ(1/24)Γ(5/24)Γ(7/24)Γ(11/24)
  = 1.516386059151978`, `p_SC = 0.340537329550999`.

## Method (sketch)

**Primary arm — Bloch/Fourier k-sum with Richardson extrapolation.** In FCC primitive
(n-)coordinates the finite periodic torus of size `M³` gives the deflated Green's value
`G_M = (1/M³)Σ_{q≠0} 1/(1−λ(q))`, converging as `G_M = G − c₁/M − c₃/M³ − c₅/M⁵ − …` (probed);
a `kinematics::richardson` ladder (orders 1, 3, 5 over `M = 48, 96, 192, 384`) cancels the terms.
The stella graph has a period-3 screw structure (vertex classes = coordinate-sum mod 3): each
octahedral hole `c` carries one long diagonal along axis `(cx+cy+cz) mod 3`, so every vertex gains
exactly 2 long bonds (14-regular), and the graph is vertex-transitive (cyclic axis rotation ∘
translation by `(2,1,1)`). Its `G_M` is the deflated trace sum `(1/(3M³))Σ_q Tr₃(I − B(q)/14)⁻¹`
over 3×3 Bloch blocks (`M ≡ 0 mod 3`; the three zero-mode copies contribute the deflated `7/3`
each — the non-unit eigenvalues of `B(0)/14` are `2/14, 2/14`).

**Cross-check arm — the actual complex, three ways.** (i) *Exact adjacency:* the interior vertex
adjacency of `geom::mesh_3d_chiral_tetoct(12,12,12, oct_axis)` read from its own `d0_sparse` must
equal the 12-FCC + 2-long-bond rule **exactly**, vertex by vertex. (ii) *Real space vs k-space:*
deflated CG solve of `(I−P)g = δ₀ − 1/N` on the rule-built `M=24` torus must equal the Bloch k-sum
at the same `M` to machine level. (iii) *Dynamics bracket:* the open-mesh matvec partial sum
`S_8 = Σ_{t≤8} p_t(0,0)` (exact infinite-lattice terms — the support cannot reach the boundary) is
a strict lower bound on `G_stella`.

R9 unit tests (hand-derivable): the 1-D ring `G_M = (M²−1)/6M` (the 1-D walk is recurrent — return
probability → 1); the `M=2` SC k-sum (= 29/32); the 3×3 trace-inverse identity; Bloch-vs-dense
brute force on the `M=6` stella torus. Deterministic: pure f64, no RNG, no wall-clock (R8 progress
to stderr). Data → `data/*.csv` (R10 source of truth).

## Predictions (registered before the run; tolerances probe-informed)

- **P0 (control, R5):** the machinery reproduces the **SC** Watson value:
  `|G_SC^lattice − 1.516386059151978| < 1e-10`, and the raw torus sums obey the registered `1/M`
  error law (successive-error ratio in `[1.9, 2.1]` for `M = 48→96→192→384`). — *gate asserts.*
- **P1 (the answer key):** the **FCC** constant matches Watson's closed form:
  `|G_FCC^lattice − 1.344661183165145| < 1e-9` and `|p_FCC^lattice − 0.256318236504649| < 1e-9`.
  (The issue's floor was ≤1e-6; the probe supports 1e-9 with ~3 orders of margin.) — *gate asserts.*
- **P2 (the graph is the complex's):** (a) exact adjacency equality at **every** interior vertex of
  the `n=12` engine mesh (no tolerance — combinatorial), and (b) `|G_CG(24) − G_Bloch(24)| < 1e-10`.
  — *gate asserts.*
- **P3 (the new constant):** the stella tet-oct complex constant is
  `G_stella = 1.3023100141 ± 1e-8` and `p_stella = 0.2321336785 ± 1e-8`
  (registered from the probe; the run-for-record must reproduce it from committed code), with the
  ladder internally consistent (`|R_ord5 − R_ord3^last| < 1e-9` — the extrapolation-order
  sensitivity control) and the strict dynamics bound `S_8 < G_stella` with
  `|S_8 − 1.166371405| < 1e-9`. — *gate asserts.*

## What would falsify this

If the FCC ladder does not land on the Γ-function closed form (P1), either the machinery or the
registered closed form is wrong — the rung fails publicly either way. If the mesh adjacency or the
CG-vs-Bloch identity fails (P2), the Bloch model does *not* describe the engine's complex and the
stella number is unregistered. If the stella ladder is not internally consistent to 1e-9, violates
the `S_8` lower bound, or the run lands outside the registered `±1e-8` (P3), the registered value
is wrong (R5: reported as a miss, not retuned).
