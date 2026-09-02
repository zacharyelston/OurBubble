# 0115 — Warp-1.5 lattice-matched isotropy: evaluation

**Verdict:** CONFIRMED · **Gate:** `uf1_5_lattice_matched_gate` (green: yes) · **Commit:** `f8d9952`

## Result

Matching the lattice (the geometric Hodge ⋆) turns the anisotropic `⋆=I` light cone **isotropic**: the
trivial combinatorial Laplacian propagates the pulse **22.4%** faster/slower along a lattice axis than a
body diagonal (the #23 defect), and the geometric Hodge cuts that to **2.2%** — **×10.2 more isotropic**.
So a bubble moves — and steers — at the same speed in every direction *only* when lattice-matched.

| quantity | ⋆=I (trivial) | geometric Hodge | pass |
|---|---|---|---|
| `v_axis [100]` | 0.6289 | 0.7843 | — |
| `v_diag [111]` | 0.8109 | 0.8019 | — |
| anisotropy `|v_ax/v_di − 1|` | **22.4%** | **2.2%** | ✅ P0 (>5%) · ✅ P1 (≥2× drop) |

Data: [`data/isotropy.csv`](data/isotropy.csv). **Figure:** [`figures/isotropy.html`](figures/isotropy.html)
— the data-true light cones (lopsided `⋆=I` vs round geometric ⋆), rendered by `core/viz gen_isotropy`
directly from the CSV (R10, self-contained). This entry is **bit-for-bit identical** to
`stellamax-core`'s original lab/0115 run (verified during the #7 gate port).

## What it rules in / out

- **Rules in:** the geometric ⋆ (Layer 1, `dec::hodge`) restores directional isotropy on the
  tetrahedral lattice — the #23 fix works for the scalar wave through the full `geom→dec→solve` stack.
- **Rules out:** using `⋆=I` for any directional/steering result — on the trivial star the Warp-1.2
  steering would point untrue (axes ~22% faster than diagonals). Lattice-matching is a *precondition*
  for honest directional control, not an optional polish.

## Deferred / next

- Isotropy of the **vector photon** (1-form) is the harder sibling — the Nédélec curl-curl + Whitney
  edge mass (`dec::hodge`); does the ×10 hold for `A`, not just φ? → menu idea.
- A **data-true viz** of the two light cones (round vs lopsided) from `data/isotropy.csv` — the natural
  book chapter (R10). → chapter menu ("viz module").
