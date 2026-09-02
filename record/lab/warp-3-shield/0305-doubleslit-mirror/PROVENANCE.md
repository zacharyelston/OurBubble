# PROVENANCE — 0305 doubleslit-mirror

- **Registered (R1):** `4435bca` — spec + gate + `geom::mesh_2d_triangle_grid_crossed` (before the run).
- **Probe (breadcrumb):** `154c578` — `core/uniforge/examples/doubleslit_mirror_probe.rs`
  (4 arms; every registered threshold measured there first, boundary populations included).
- **Run-for-record:** `490f006` — gate green, data committed.
- **Toolchain:** `rustc 1.97.1 (8bab26f4f 2026-07-14)`, release profile, CPU (macOS arm64).

## Regenerate

```
cd core && cargo test -p uniforge --release --test uf3_5_doubleslit_mirror_gate -- --nocapture
```

Rewrites both CSVs below in place (~2 s). The probe:
`cd core && cargo run --release -p uniforge --example doubleslit_mirror_probe`.

## Determinism

Pure f64, no RNG, no wall-clock anywhere in the pipeline (mesh builders, `ScalarScene`, the
pinned sinusoidal drive, the metrics). Identical output on every run of the same build; expected
identical across machines up to libm `sin` differences (none observed vs the committed snapshot's
front frame).

## Data files

- `data/arms.csv` — one row per arm (A demo / B uniform+geometric ⋆ / C crossed+⋆=I /
  D crossed+geometric ⋆): front-arrival frame, the four station asymmetries (x = 32, 66, 120,
  188), slit-lobe ratio, screen-intensity mirror asymmetry, max intensity, mean fringe spacing.
- `data/screen_intensity.csv` — the four time-mean screen-intensity profiles, y = 0..140
  (the R10 figure's source of truth).

FIREWALL: toy DEC scalar wave on a lattice; nothing here is a claim about nature.
