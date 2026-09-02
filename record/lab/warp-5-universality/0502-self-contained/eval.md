# 0502 — Warp-5.2: the complete, self-contained prediction — evaluation

**Verdict:** CONFIRMED (R10) · **Gate:** `uf5_2_selfcontained_gate` (green: yes, 23 s) · **Commit:** `87cbd96` (registered `4e6cb63`)

## Result

**Nothing supplied but the model — the toy now outputs `T_c, ν, β, γ` end-to-end.** The Binder cumulant
`U = 1 − ⟨m⁴⟩/3⟨m²⟩²` is size-independent at criticality, so the `U_L(T)` curves cross at a universal point;
that crossing **locates `T_c` blind**, and its slope FSS **measures `ν` blind**. Everything else follows.

| quantity | measured (blind) | exact | pass |
|---|---|---|---|
| P0 universal Binder value `U*` | **0.6135** | ≈ 0.61 | ✅ |
| P1 located `T_c` | **2.26683** | 2.26919 (0.10%) | ✅ |
| P2 correlation-length exponent `ν` | **1.040** | 1 (4.0%) | ✅ |
| P3 magnetization exponent `β` | **0.126** | 0.125 (0.8%) | ✅ |
| P3 susceptibility exponent `γ` | **1.828** | 1.75 (4.5%) | ✅ |

The Binder curves cross at `2.2623, 2.2704, 2.2678` (adjacent-`L` pairs), averaging to `T_c = 2.2668` —
0.10% from the Onsager value, with **no exact `T_c` supplied**. The slope `|dU/dT| = 0.28, 0.58, 0.82, 1.07`
across `L = 8,16,24,32` scales as `L^{1/ν}` → `ν = 1.040`. At the located `T_c`, `⟨|m|⟩` and `χ` give
`β/ν = 0.1215`, `γ/ν = 1.7579`; times the measured `ν` → `β = 0.126`, `γ = 1.828`. Data:
[`data/binder.csv`](data/binder.csv), [`data/fss.csv`](data/fss.csv), [`data/results.csv`](data/results.csv).
Figure: `core/viz gen_selfcontained`.

## What it rules in / out

- **Closes rung 5.1's two caveats.** 5.1 supplied `T_c` and `ν`; this rung *measures* both from the same
  simulation data. The pipeline is now genuinely **self-contained** — the only input is the model (couplings,
  dimension); `T_c, ν, β, γ, U*` are all **outputs**, each matching the exact 2-D-Ising truth (and hence real
  2-D-Ising materials).
- **The `ν` residual is the honest limit.** `ν = 1.040` (4%) is the noisiest number — it rides on fourth
  moments and a finite-`L` slope — and it propagates into `γ` (4.5% high). Larger `L`, more statistics, and a
  corrections-to-scaling term would tighten it; the few-percent residual is reported, not hidden (R5).
- **Firewall intact.** Universal quantities of a **toy** Ising model, computed by seeded Monte Carlo. Not a
  claim about the warp/DEC engine or spacetime.

## Deferred / next

The one remaining composition: run this **fully-blind pipeline on the 3-D model** (locate 3-D `T_c` by the
Binder crossing, measure 3-D `ν`), so the *novel* 3-D prediction of rung 5.1 becomes self-contained too —
compute-bound (3-D temperature scans), not method-bound, since both pieces (5.1's 3-D exponents, 5.2's blind
`T_c`/`ν`) are now proven. Then a **data-collapse** figure as the visual capstone of chapter 5.
