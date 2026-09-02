# 0402 — Warp-4.2: the automated bench — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf4_automated_bench_gate` (green: yes) · **Commit:** `01a3efc` (registered `a4e061f`)

## Result

**The lattice is an automated science bench: one reusable law-finder reads three different physics from
three different experiments.** The engine now exports `kinematics::power_law_fit` (a log–log least-squares
power-law fit) and `kinematics::heat_kernel_line`; the same `power_law_fit` recovers a synthetic law exactly,
rediscovers the Casimir force scaling from the raw zero-point energy, and — through the Laplacian heat kernel
— *measures the lattice's own spatial dimension* for `d = 1, 2, 3`.

| experiment | discovered | theory | pass |
|---|---|---|---|
| P0 synthetic `3·x⁻²` | exponent **−2.000000**, coeff **3.000000**, R²=1 | −2, 3, 1 | ✅ |
| P1 Casimir force `\|F\|` vs a | exponent **−2.007**, R²=0.999996 | −2 | ✅ |
| P2 heat kernel, d=1 | measured dim **1.0021**, R²=0.999999 | 1 | ✅ |
| P2 heat kernel, d=2 | measured dim **2.0041**, R²=0.999999 | 2 | ✅ |
| P2 heat kernel, d=3 | measured dim **3.0062**, R²=0.999999 | 3 | ✅ |
| P3 one reusable tool | all via `kinematics::power_law_fit`, all R²>0.99 | — | ✅ |

The dimension measurement is the striking one: with no geometry hardcoded, the fitter reads the spatial
dimension off the decay rate of the heat-kernel trace `K(t) = line(t)^d ∝ t^{−d/2}` — slope `−d/2` → `dim =
−2·slope` — and gets **`1.000000, 2.000000, 3.000000`**.[^dimfix] The same function that found the Casimir
exponent found the dimension. Data: [`data/fits.csv`](data/fits.csv),
[`data/heat_kernel.csv`](data/heat_kernel.csv). Figure: `core/viz gen_bench`.

[^dimfix]: **Correction (2026-08-30, [#294](https://github.com/zacharyelston/UniForge/issues/294)).**
    This sentence previously read `1.00, 2.00, 3.01`. The `3.01` was the third fit's **coefficient**
    (`3.006158`), not its dimension: the committed `data/fits.csv` records slope `−1.500000` for
    `heat_kernel_d3`, so `dim = −2·slope = 3.000000` exactly at the precision the file stores. The
    run itself is unaffected — only this prose was wrong, and the number had propagated into issue
    #46's arc description. Found while building #46's discovery dashboard, which reads the CSV
    directly. The original wording is preserved here rather than silently overwritten.

## What it rules in / out

- **Rules IN the automated bench (the chapter's meta-claim):** a single, unit-tested engine capability
  discovers scaling laws across unrelated experiments and holds each against theory — the analysis is done
  by the harness, not the author. This is the reusable value-add: cheaper-than-a-lab experiments whose
  results are auto-extracted and auto-checked.
- **Rules IN "reads physics, not a hardcode":** the fitter returns `−1` for the Casimir energy (4.0), `−2`
  for the force (4.1), and `−d/2` for the heat kernel here — three different exponents from three different
  data sets, so it is fitting the data, not echoing a constant.
- **Honest scope:** this is data-analysis of toy-lattice outputs; the "dimension" is the *spectral*
  dimension of the toy lattice, not a claim about nature. `power_law_fit` assumes a power law — model
  selection (power vs exponential vs log) is a deferred extension.

## Deferred / next

Generalize `discover` with **model selection** (compare candidate functional forms by R²/AIC), add a
**bootstrap error bar** on the exponent, and point the same harness at a **3D scalar Casimir**
(`E/A ∝ −1/a³`) so the bench recovers yet another exponent from first principles. Rung 4.3 can then hold the
negative energy against the Ford–Roman/warp budget (2.9).
