# Provenance — 0116 TetOct primer

- **Commit:** spec + gate registered at `5b7a22d` (R1); data/figure produced by the run recorded in
  this entry's second commit (`git log --follow lab/primer/0116-tetoct-primer/data/lattice.json`).
- **Toolchain:** `rustc 1.92.0 (ded5c06cf 2025-12-08)`; figure build needs only python3 (stdlib).
- **Regenerate:**
  ```bash
  cd core
  cargo test --release -p uniforge --test primer_tetoct_census_gate -- --nocapture
  # the gate WRITES data/lattice.json directly (R10) — path anchored to CARGO_MANIFEST_DIR,
  # so it lands in this entry's data/ regardless of where cargo test is run
  python3 ../lab/primer/0116-tetoct-primer/figures/inject.py
  # -> figures/tetoct-render.html (the template + the data, pure substitution)
  ```
- **Determinism:** purely combinatorial integer census — no floats, no seed, no wall-clock; the
  JSON is byte-identical on every machine (verified equal to the pre-registration exploratory
  probe built in the MCP demo session).
- **Data files:**
  - `data/lattice.json` — `meta` (builder string + counts), `verts` `[x,y,z,active]` (dense id =
    index), `edges` `[a,b,len²]`, `tets` `[v0..v3,kind,axis]` (kind 0/1 = matter/antimatter
    stella, 2 = oct), `cubes` `[i,j,k,parity]` (construction scaffold, not part of the complex).
