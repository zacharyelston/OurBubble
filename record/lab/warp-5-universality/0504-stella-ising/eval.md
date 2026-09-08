# 0504 — Warp-5.4: Ising on the stella lattice — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf5_4_stella_ising_gate` (green: yes, 40 s) · **Commit:** `fe754c1` (registered `b5b1cdf`)

## Result

**Universality holds on our own lattice.** Ising spins on the engine's stella complex — the graph read from
the mesh's own `d0_sparse` — order at a critical temperature nobody has tabulated, with the same class
exponents as the cubic lattice.

| quantity | measured | check | pass |
|---|---|---|---|
| P0 graph | FCC 2176 vertices (n=16), coordination 14, connected | matches the mesh | ✅ |
| P1 stella `T_c` | **11.638** (crossing spread 0.075) | new; coordination sanity ≈ 11.4 | ✅ |
| P2 `U*` | **0.305**, stable across sizes | ≠ periodic-cubic 0.484 — amplitudes are BC-dependent | ✅ |
| P3 `γ/ν` | **1.895** | class 1.963 (3.5%); cubic run 2.027 (6.5%) | ✅ |
| P3 `β/ν` | **0.515** | class 0.518 (0.6%); cubic run 0.486 (6.1%) | ✅ |

Two lattices — cubic (5.3) and the stella tet-oct complex — different coordination (6 vs 14), different
`T_c` (4.51 vs 11.64), different `U*` (0.484 vs 0.305), **same exponent ratios**. The non-universal numbers
moved; the universal ones didn't. That is the whole claim of universality, checked on the geometry this
engine is actually built from. Data: [`data/stella_graph.csv`](data/stella_graph.csv),
[`data/binder_stella.csv`](data/binder_stella.csv), [`data/results.csv`](data/results.csv). Figure: the
Binder-crossing mechanism is rendered in [5.2's figure](../0502-self-contained/figures/selfcontained.html);
a stella-specific figure is on the menu.

## Notes

- `T_c = 11.638` and `U* = 0.305` are properties of *this* mesh (non-universal), useful as reference values
  for any future spin work on the engine geometry.
- The yz-periodic mesh (open in x) sets `U*` well below the fully-periodic 0.465–0.484 — expected:
  amplitudes depend on boundary geometry. The fully-open mesh (probed) has even stronger surface effects;
  the yz-periodic builder is the right default for critical measurements on the engine mesh.
- Tolerances are the honest few-percent of small-`L` FSS, same as 5.3. Error bars (branch A) would turn
  these into ± statements.

## Deferred / next

A stella-specific Binder figure; the stella **spectral dimension** (heat kernel of the mesh `d†d` — is the
stella 3-dimensional to a walker?); error bars (branch A) to tighten all chapter-5 tolerances.
