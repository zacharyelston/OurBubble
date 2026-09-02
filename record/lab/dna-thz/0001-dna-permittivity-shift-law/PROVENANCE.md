# PROVENANCE — 0001 dna-thz rung 1

## Commits

| role | SHA | message |
|---|---|---|
| R1 registered | `9f86d75` | code: register dna-thz rung 0001 — dielectric shift law Ω ∝ ε_r^p (R1) |
| run for record | `7fdb4c3` | run: rung 0001 — P3 FAIL, naive √ε_r law falsified (P0-P3) |

## Toolchain

```
rustc 1.92.0 (ded5c06cf 2025-12-08)
```

## Regenerate commands

```bash
cd core
cargo test -p uniforge --release --test uf6_1_thz_shift_law_gate -- --nocapture
```

Output lands in `lab/dna-thz/0001-dna-permittivity-shift-law/data/shift_law.csv`.

## Determinism

The gate is fully deterministic: no RNG, pure f64, fixed mesh (`mesh_3d_tetrahedral_grid(16,8,8)`),
fixed sweep parameters. Running the command above on the same commit and toolchain reproduces
`shift_law.csv` bit-for-bit.

## Data files

| file | description |
|---|---|
| `data/shift_law.csv` | columns: `eps_r,peak_omega` — 7 rows, peak Ω for ε_r ∈ {1,4,9,16,25,36,49} |
| `data/probe_shift_law.csv` | identical format from the throw-away probe run (same numbers) |
