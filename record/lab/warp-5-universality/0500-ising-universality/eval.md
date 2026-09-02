# 0500 — Warp-5.0: universality — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf5_universality_gate` (green: yes) · **Commit:** `962dacb` (registered `dc2c12e`)

## Result

**The lattice measures nature's Ising numbers, parameter-free — the graduation swing lands.** From raw
finite-size data of the critical transverse-field Ising chain, with the velocity `v` *measured* from the
dispersion (not assumed), the lattice returns the universal invariants of the 2-D Ising universality class:

| invariant | measured | exact | pass |
|---|---|---|---|
| P0 critical energy density `e∞` | −1.273239545 | `−4/π` = −1.273239545 | ✅ |
| P1 **central charge `c`** | **0.49999987** | `1/2` | ✅ |
| P2 correlation-length exponent `ν` | 1.000000 | 1 | ✅ |
| P3 dynamic exponent `z` | 0.999617 | 1 | ✅ |
| (measured) velocity `v` | 2.000000 | 2 | — |
| (cited) magnetization exponent `β` | 0.125 | `1/8` (Pfeuty) | — |

Nothing was tuned: `½, 1, 1` emerged from the `E₀(L)` scaling (`E₀/L = e∞ − πcv/6L²`, coefficient
`b = −0.5236 = −π/6`). These are the **same numbers measured in real Ising-class materials** (uniaxial
magnets, order–disorder transitions) — universality means they don't depend on the microscopic model. Data:
[`data/fss.csv`](data/fss.csv), [`data/nu.csv`](data/nu.csv), [`data/exponents.csv`](data/exponents.csv).
Figure: `core/viz gen_universality`.

## What it rules in / out — and the honest scope

- **Rules IN the capability the ledger demanded:** the lattice bench produces a **dimensionless,
  parameter-free number of nature** (`c = 1/2` and the exponents), extracted from raw data with the velocity
  measured — exactly the prediction-grade bar from [rung 4.4](../../warp-4-vacuum/0404-energy-number). And it
  reused the engine's own `kinematics::power_law_fit` for `ν, z`, on the same `2−2cos k` lattice-Laplacian
  spectrum from chapter 4.
- **Honest about "no longer a toy":** `c = 1/2` for the transverse-field Ising chain is a **postdiction** —
  the model is exactly solvable, so its universal numbers are known. This rung therefore *validates the
  machinery* (finite-size scaling on the lattice yields the exact universal invariants) rather than
  delivering a **novel** prediction. The true graduation is to run the identical machinery on an **unsolved**
  model and predict a **real material's** exponents before they're looked up — that is rung 5.x, not this one.
- **Firewall intact:** this is universality-class membership of a toy Ising critical point, shared with real
  Ising-class systems. It is **not** a claim that the warp/DEC engine "is" a magnet, and not a spacetime
  claim. `c = 1/2` was not put in; but neither was it a discovery — it is the known invariant of a known
  class, reproduced.

## Deferred / next

**Data collapse** (scale `M·L^{β/ν}` vs `(h−h_c)L^{1/ν}` onto one curve — the visual proof of universality);
the **magnetization exponent `β = 1/8`** computed directly (Toeplitz/correlators, not cited); and the real
graduation: an **unsolved model → a real material's exponents**, a genuinely novel parameter-free prediction.
