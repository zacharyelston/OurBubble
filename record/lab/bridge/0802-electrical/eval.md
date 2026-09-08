# 0802 — the 4th view (electrical / random-walk): evaluation

**Verdict:** CONFIRMED · **Gate:** `uf8_2_electrical_gate` (green: yes) · **Register:** `1b61300` · **Run:** `73a4d40`

## Result

The multi-view engine gains a **4th view**: the stella graph read as an **electrical network** and as a
**random walk**. It earns membership by the walks↔circuits duality — `commute_time(a,b) = 2|E|·R_eff(a,b)`
holds to **5.7e-14** on the stella graph, two independent solves (voltages on `L`, hitting times on
`I−P`) landing on the same number. The view's flagship constant is the stella **spanning-tree entropy**
`z_stella = 2.5761244 ± 2e-5` — a new 🔵 Watson-family number, the growth rate of the number of spanning
trees, computed with the same Bloch machinery as 7.0/7.1.

| prediction | expected | measured | pass |
|---|---|---|---|
| P0 Kirchhoff `τ(K_m)=m^(m−2)` (Cayley) | 0 error | ≤ 1.8e-15 | ✅ |
| P0 Kirchhoff `τ(C_n)=n` | exact | 5, 8, 12 | ✅ |
| P1 spanning-tree entropy `z_stella` | 2.576122 ± 2e-5 | **2.5761244** | ✅ |
| P1 ladder internal `\|z(192)−z(96)\|` | < 1e-4 | 8.8e-6 | ✅ |
| P2 walks↔circuits `commute = 2E·R_eff` | < 1e-9 | ≤ **5.7e-14** | ✅ |
| P3 Bloch `z₆` == dense (215 modes) | < 1e-9 | 7.1e-14 | ✅ |

Data: [`data/`](data) (`kirchhoff_controls.csv`, `entropy_ksum.csv`, `walks_circuits.csv`, `summary.csv`).
Figure: [`figures/electrical.html`](figures/electrical.html).

## What it rules in / out

- **Rules in:** electrical + random-walk join the multi-view as a genuine view — the membership test
  (round-trip identity) passes: `commute = 2E·R_eff` binds the two independent computations. `z_stella`
  is registered as the spanning-tree entropy of the 14-regular stella complex — validated by exact
  closed forms (Cayley, cycle) and by the Bloch↔dense cross-check.
- **The resolution is honestly ~5 digits, not ~10:** `⟨ln λ⟩` has an integrable **logarithmic
  singularity** at the band bottom (`λ→0`), so the k-sum converges ~`1/M²` (vs 7.1's smooth `⟨λ ln λ⟩`
  at ~`1/M⁵`). Stating that limit is the result; **singularity-subtraction** (subtract the analytic
  `∫ln|k|` near `k=0`, add it back) would recover more digits — deferred.
- **Rules out nothing physical** (firewall): spanning-tree entropy and the walks↔circuits duality are
  graph mathematics of the toy complex, never claims about nature.

## Scope / caveats

- `z` is on the **rule-built** 14-regular stella torus (7.0's `stella_torus_adjacency` — the actual
  complex vertices), *not* the engine periodic mesh (whose isolated odd-sum placeholders would corrupt
  `⟨ln λ⟩`; that mismatch was caught in the probe and is why the cross-check uses the rule-built graph).
- Resistance/commute use dense solves (small graphs); a sparse/iterative path is the large-N follow-on.

## Deferred / next (→ chapter menu)

- **singularity-subtraction for z:** recover z_stella to ~10 digits by handling the `ln|k|` singularity
  analytically — turns the ±2e-5 into ±1e-9.
- **quantum / stat-mech views (5th/6th):** partition function `tr e^{−βL}`, Gaussian free field,
  tight-binding spectrum — more languages of the same `Δ`, each with its own identity gate.
- **effective-resistance metric:** the `R_eff` resistance-distance geometry of the stella graph — a new
  metric to embed and study (spectral embedding / Laplacian eigenmaps).
- **Kemeny constant / mean first-passage:** the next random-walk moments after the return constant (7.0).
