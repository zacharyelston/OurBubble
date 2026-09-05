# 0116 — TetOct primer: evaluation

**Verdict:** CONFIRMED · **Gate:** `primer_tetoct_census_gate` (green: yes) · **Commit:** `5b7a22d` (registered) → run at the following commit

## Result

The tet-oct stella complex at n=4 has exactly the registered structure, and the gate's export is
byte-identical (verts/edges/tets) to the exploratory MCP-session probe that motivated the entry.
The interactive render ([`figures/tetoct-render.html`](figures/tetoct-render.html)) embeds that
data verbatim, with the 64 construction cubes as a toggleable scaffold overlay.

| quantity | expected | measured | pass |
|---|---|---|---|
| d²=0 (integer identity, all D1·D0 rows) | true | true | ✅ |
| vertices (dense / active even-sum) | 125 / 63 | 125 / 63 | ✅ |
| edges (√2 / long diagonals) | 240 / 14 | 240 / 14 | ✅ |
| faces | 312 | 312 | ✅ |
| tets (matter / antimatter / oct) | 32 / 32 / 56 | 32 / 32 / 56 | ✅ |
| oct tets per long diagonal | 4 (all 14) | 4 (all 14) | ✅ |
| screw111 axis census (holes x/y/z) | 2 / 6 / 6 | 2 / 6 / 6 | ✅ |

Data: [`data/lattice.json`](data/lattice.json). Figure: [`figures/tetoct-render.html`](figures/tetoct-render.html)
(self-contained; published as a Claude artifact from this file).

## What it rules in / out

The census pins the n=4 reference numbers for every later primer/render (any regression in the
builder now trips a registered gate, not a picture). Honestly ruled OUT of scope: there is **no 4D
TetOct builder** — the tetoct complex is the 3D spatial lattice ("4D" in the repo tagline is the
spacetime of the sim; `Cell4` appears only in the canonical single 4-simplex), and this entry's
render says so on its face. The scaffold cubes are construction geometry, not complex edges (unit
length 1 vs lattice √2), and are labelled as such in the viewer.

## Deferred / next

- **mcp-export** (chapter menu): produce `lattice.json` over the MCP surface and gate on byte
  equality with this entry's data — closes the loop this chapter exists for.
- Periodic-variant and mirror-handedness primers (menu rows), which reuse this gate's
  classification helper pattern.
