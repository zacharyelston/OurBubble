# 0802 — Bridge-8.2: the 4th view (electrical / random-walk) + the stella spanning-tree constant

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf8_2_electrical_gate.rs` · **Status:** CONFIRMED — see [`eval.md`](eval.md)

## Goal (one paragraph)

Add the **4th view** to the multi-view engine (`kinematics::views`, see [VIEWS.md](../../../docs/VIEWS.md)):
the same graph Laplacian read as an **electrical network** (edge = resistor) and as a **random walk**.
Its membership gate is the famous **walks↔circuits duality**, `commute_time(a,b) = 2·|E|·R_eff(a,b)`
(Chandra et al. 1989) — two independent computations (a voltage solve on `L` vs a hitting-time solve on
`I−P`) that must agree. The view's flagship number is the stella **spanning-tree entropy**
`z = lim_{N→∞} (ln τ)/N = ⟨ln λ_L⟩_BZ`, where `τ = (1/N)∏_{λ>0} λ` is the number of spanning trees
(Kirchhoff's Matrix-Tree theorem) — a new 🔵 constant in the Watson family, computed with the same
Bloch machinery as rungs 7.0/7.1.

## Firewall (R3)

*Random walk, resistance, spanning tree, commute time* are graph-theoretic quantities of a **toy**
14-regular lattice complex. `z_stella` is a 🔵 dimensionless fact of graph mathematics — exact/un-tuned
(modulo the stated numerical resolution), never a claim about nature. Dimensionless; c = G = 1.

## Method (sketch)

- **`kinematics::views`** (module additions): `effective_resistance(l,a,b)` (ground `b`, solve `Lv=e_a−e_b`),
  `hitting_time`/`commute_time` (solve `(I−P)H=1` on `P=D⁻¹A`), `spanning_tree_ln(eigs)` (Kirchhoff:
  `ln τ = −ln N + Σ_{λ>0} ln λ`), `dense_solve` (Gaussian elimination). These read a dense graph
  Laplacian — the shared object — so they compose with `TensorView::assemble_laplacian0`.
- **The constant** `z_stella = ⟨ln λ_L⟩_BZ`: the Bloch k-sum over the M³ torus (reusing 7.1's 3×3 screw
  block, `λ_L = 14·eig(cmat)`, zero modes excluded) with a Richardson ladder over `M = 24,48,96,192`.
  **Note (registered):** `ln λ` has an integrable **logarithmic singularity** at the band bottom
  (`λ→0`), so convergence is ~`1/M²` (slower than 7.1's smooth `⟨λ ln λ⟩`, ~`1/M⁵`) and the resolution
  is ~5 digits, not ~10 — stating that limit is part of the result (singularity-subtraction is deferred).
- **Graph:** the rule-built 14-regular stella torus (7.0's `stella_torus_adjacency`; the actual complex
  vertices, no placeholders) — the graph the Bloch model describes. Deterministic f64; no RNG/wall-clock.
  Data → `data/*.csv` (R10). R9 unit tests (module): Cayley `τ(K_m)=m^(m−2)`; cycle `τ(C_n)=n` and
  `commute(adjacent)=2(n−1)`.

## Predictions (registered before the run; tolerances probe-informed)

- **P0 (Kirchhoff controls, closed forms):** `spanning_tree_ln` reproduces `ln(m^(m−2))` for `K_m`
  (m∈{4,5,6}) and `ln n` for the cycle `C_n` (n∈{5,8,12}), each `< 1e-9`. — *gate asserts.*
- **P1 (the new constant):** `z_stella = 2.576122 ± 2e-5` (Bloch `⟨ln λ_L⟩` + Richardson; the ±2e-5 band
  is the honest log-singularity resolution), with internal consistency `|z(192) − z(96)| < 1e-4`. —
  *gate asserts.*
- **P2 (walks↔circuits — the 4th view's membership gate):** on the stella torus (M=3, 27 nodes,
  `|E|=189`), `|commute_time(a,b) − 2·|E|·R_eff(a,b)| < 1e-9` for several node pairs — the electrical
  and random-walk computations, independent, agree. — *gate asserts.*
- **P3 (Bloch↔dense cross-check for z):** `⟨ln λ_L⟩` from the Bloch block at M=6 equals the dense Jacobi
  spectrum of the rule-built M=6 torus (215 nonzero modes): `< 1e-9`. — *gate asserts.*

## What would falsify this

If `spanning_tree_ln ≠` Cayley/cycle closed forms (P0), the Kirchhoff machinery is wrong. If the ladder
lands outside `2.576122 ± 2e-5` (P1), the registered value/resolution is wrong (R5: reported, not
retuned). If `commute ≠ 2E·R_eff` (P2), the electrical and random-walk readings are **not** the same
object — the 4th view fails its membership test and does not join. If Bloch `⟨ln λ⟩ ≠` the dense
spectrum at M=6 (P3), the eigenvalue route for `z` is wrong. Any miss is reported (R5), not retuned.
