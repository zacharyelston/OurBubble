# 0117 — Warp-1.7: `ω = c·k` discovered blind, in five directions — evaluation

**Verdict:** **CONFIRMED (P0–P4, first run)** · **Gate:**
`core/uniforge/tests/uf1_7_dispersion_isotropy_gate.rs` (green, 14.5 s) · **Run commit:** `f2f610b`
(**registered** `f364fb1`, before the run — R1) · **Figure:**
[`figures/discovery.html`](figures/discovery.html)

## Prior known physics, up front (R3)

Stated in [`spec.md`](spec.md) before the run and repeated here because it is the honest frame: this
is a **discovery reframing of known numerics, not new physics**. On this mesh the geometric ⋆ gives
`⋆₁ = 1` on every axis edge and **exactly `0`** on every face- and body-diagonal edge, so
`Δ₀ = ⋆₀⁻¹D₀ᵀ⋆₁D₀` **is** the textbook 7-point simple-cubic stencil, whose symbol
`λ(k) = Σ_a (2 − 2cos k_a)` is closed-form. The sweep therefore has an exact analytic answer key, and
P0 checks the machinery against it. That is the point of #46's first arm — the bench must be shown
re-deriving physics whose answer is already known, **blind**, before any blind claim about something
unknown is worth anything.

## Result

Handed a sweep with **no dispersion relation supplied**, the bench selects the **linear** law in all
five directions and returns exponent `1.00` to 1.6% at `R² ≥ 0.999906`. The discovered speeds agree
across directions to **1.78%**, and that residue **shrinks with the window** — so the cone is
isotropic in the long-wavelength limit, and the 1.78% is a finite-`k` effect rather than a surviving
cone defect. The identical pipeline on the trivial `⋆ = I` operator returns **33.2%** anisotropy that
does *not* shrink: the detector has teeth.

### P0 — machinery, against the closed-form key

| quantity | measured | bound | pass |
|---|---|---|---|
| `max\|⋆₀ − 1\|` over 262 144 vertices | `4.44e-16` | `< 1e-12` | ✅ |
| `max\|⋆₁ − 1\|` over 786 432 **axis** edges | `1.11e-16` | `< 1e-12` | ✅ |
| `max\|⋆₁\|` over 1 048 576 **diagonal** edges | **`0.0` exactly** | `< 1e-14` | ✅ |
| `max\|λ − Σ_a(2−2cos k_a)\|`, every probed mode (`λ ≤ 3.70`) | `8.23e-12` | `< 1e-9` | ✅ |
| axis-triple relative disagreement (cubic symmetry) | `7.44e-13` | `< 1e-9` | ✅ |
| `min λ` over every probed mode | `9.63e-3` | `> −1e-9` | ✅ |

### P1 — the blind discovery (long-λ window `|k| ≤ 1.05`)

| direction | modes | selected law | sel. `R²` | margin over runner-up | free `p` | `C` | `R²` |
|---|---|---|---|---|---|---|---|
| `[100]`/`[010]`/`[001]` | 10 | **`ω ∝ k¹`** | `0.9996322` | `0.241497` | `0.983720` | `0.971669` | `0.99990602` |
| `[110]` | 7 | **`ω ∝ k¹`** | `0.9998896` | `0.245273` | `0.990773` | `0.985078` | `0.99997633` |
| `[111]` | 6 | **`ω ∝ k¹`** | `0.9999329` | `0.246280` | `0.992702` | `0.989030` | `0.99998695` |

Runner-up is always the **diffusive** `k^{1/2}` at `R² ≈ 0.754`; `k²` scores *below zero*. Bounds:
linear selected in 5/5, margin `0.2415 > 0.15`, `|p − 1| ≤ 0.0163 < 0.03`, `R² ≥ 0.999906 > 0.9995`.
All ✅.

### P2 — isotropy of the discovered speed

| window | `C` range over the 5 directions | anisotropy `A` | bound | pass |
|---|---|---|---|---|
| `\|k\| ≤ 1.05` | `[0.971669, 0.989030]` | `0.017755` | `< 0.03` | ✅ |
| `\|k\| ≤ 0.525` | `[0.988036, 0.994851]` | `0.006879` | — | — |
| ratio `A(K)/A(K/2)` | — | **`2.5811`** | `∈ [2.0, 3.2]` | ✅ |
| `max\|1 − C\|` on the halved window | — | `0.011964` | `< 0.02` | ✅ |

### P3 — the pre-registered short-wavelength bend-down (R5: a result, not a failure)

| direction | `p` long-λ | `p` full range (`\|k\| ≤ 2.10`) | bend |
|---|---|---|---|
| `[100]`/`[010]`/`[001]` | `0.983720` | `0.941325` | `0.042395` |
| `[110]` | `0.990773` | `0.967728` | `0.023045` |
| `[111]` | `0.992702` | `0.977962` | `0.014739` |

Every direction bends down (min gap `0.0147 > 0.008`), full-range `p ∈ [0.9413, 0.9780] ⊂ (0.90, 1.00)`. ✅

### P4 — negative control: the same pipeline on `⋆ = I`

| window | `C` range | anisotropy | vs geometric ⋆ |
|---|---|---|---|
| `\|k\| ≤ 1.05` | `[1.943338, 2.662536]` | `0.331910` | **18.7×** |
| `\|k\| ≤ 0.525` | — | `0.348777` | — |
| ratio | — | `0.9516` (`∈ [0.8, 1.2]`) | does **not** shrink |

✅ — and the *shape* of the failure is the informative part: `⋆ = I`'s anisotropy is **leading-order**
(constant under `k`-halving, 8.15's discriminator), which is exactly the alternative P2b rules out for
the geometric ⋆.

Data: [`data/`](data) — `dispersion_directions.csv` (63 swept modes: direction, `m`, `k`, `λ`, `ω`,
phase speed, and the closed-form symbol), `discovery.csv` (per-direction discovered laws),
`candidates.csv` (the full 6-candidate `R²` scorecard per direction), `isotropy.csv` (the four
anisotropy measurements), `answer_key.csv` (P0's machinery residuals against their bounds).

## What it rules in / out

- **In — the bench recovers a known law blind, and knows how sure it is.** The selector was given six
  candidate laws and no hint; it returned the linear one in every direction with an `R²` margin of
  `0.24` over the runner-up — a decisive, quotable preference, not a coin flip dressed up as a
  discovery. The free fit then pins the exponent to `1.00 ± 0.016`. This is the "the tool finds the
  law, no answer put in by hand" panel of #46, now with the model-selection step that 1.6 lacked.
- **In — the discovered cone is isotropic in the limit, and that claim is falsifiable.** Two things
  had to hold and both did: the residual directional spread of the discovered speed **shrinks** with
  the `k` window (ratio `2.58`), and the same measurement on a deliberately-broken metric returns a
  spread `18.7×` larger that **does not** shrink. Either half alone would have been weak; together
  they separate "isotropic" from "not resolving the anisotropy".
- **In — rung 1.5's isotropy story survives promotion from a field observable to a discovered law.**
  1.5 measured cone anisotropy `22.4% → 2.2%` (⋆=I → geometric) on lattice fields. Measured instead
  on the *fitted coefficient of a blindly-discovered dispersion law*, the same contrast reads
  `33.2% → 1.78%`. Different observable, different mesh, same physics of the metric ⋆.
- **Out / honest limit — the lattice bends its own cone.** At short wavelength every direction's
  exponent drops below 1 (to `0.941` along `[100]`), pre-registered as P3. The bend is
  direction-dependent — strongest along `[100]` (`0.0424`), weakest along `[111]` (`0.0147`) — which
  is just the closed-form key's `Σ_a u_a⁴` anisotropy of the quartic term showing up in the fit.
- **Out — nothing about photons.** The mechanism that makes the scalar cone this clean is that the
  geometric ⋆ switches the diagonal edges **off entirely** (`⋆₁ = 0` on 2/3 of all edges — 1 048 576
  of 1 835 008). That is benign for the 0-form cone measured here. It is *not* benign in general:
  rung 8.15 showed an exactly-zero ⋆ opening a spurious null space in the 1-form sector. This rung
  makes **no** claim about 1-forms/photons on this mesh, and the census is registered as scoped to
  this mesh and this star.

## Caveats (stated, not hidden)

- **`A` is window-composition sensitive.** Which modes land inside `|k| ≤ K` differs per direction
  (`[100]` gets 10, `[111]` gets 6) and jumps as `N` changes — the probe measured `A(K)` = `0.0224`
  at `N=48`, `0.0178` at `N=64`, `0.0214` at `N=72`, all with the same underlying operator. The
  registered claim is therefore the **ratio** (`A` shrinks with the window) plus a generous
  single-window bound, not a precise value of `A`.
- **The ratio is `2.58`, not the naive `4`.** `ω/k = 1 − S k²/24` with `S = Σ_a u_a⁴` would quarter
  under `k`-halving if `A` were a plain average of the deviation; it is not — the log-log fit's slope
  absorbs part of the `k²` trend and the window's *lower* edge does not move. Hence the band was
  probed (`2.58` at `N=64`, `2.60` at `N=72`) rather than assumed. What is load-bearing is
  `ratio ≫ 1` versus the control's `≈ 1`.
- **The three axis directions are not independent** — they are related by a cubic symmetry of the
  mesh, and agree to `7.4e-13`. The genuine directional content is `[100]` vs `[110]` vs `[111]`;
  the axis triple is reported as a symmetry check (P0), not as three votes.
- **Raw (seam-corrupt) stars were probed but not gated.** The probe's raw-star arm gives
  `A = 0.0249` at `N=64` (vs `0.0178` unfolded) — seam corruption inflates the apparent anisotropy
  ~1.4×, consistent with #177/1.6b. Recorded here as a breadcrumb; the registered run uses unfolded
  stars throughout.
- **`c` is not `c`.** The fitted coefficient is an emergent lattice wave speed in code units. Only
  the exponent and the anisotropy *ratio* are dimensionless and parameter-free.

## Fix vs the registered gate (R5)

None. P0–P4 passed on the first run for record, reproducing every probed number exactly (the probe
and the gate share the mesh, stars and observable, and both are deterministic pure-f64).

## Deferred / next (→ chapter menu)

- **`gen_discovery` dashboard (#46).** This rung's [`figures/discovery.html`](figures/discovery.html)
  is built as a standalone "live discovery" panel; #46 wants it as **one panel** of an aggregated
  discovery dashboard alongside Coulomb `r^{-2}`, Casimir `d^{-3}/d^{-4}`, the heat-kernel spatial
  dimension `1.00/2.00/3.01`, and π/Madelung. `data/discovery.csv` + `data/candidates.csv` are
  already in the shape that dashboard needs.
- **In-repo Coulomb rung (#46).** Re-run `|E| ∝ r^{-2}` inside UniForge so the dashboard's Coulomb
  panel is data-true from this repo rather than a constellation result.
- **Diffusion rung (#46, optional).** `⟨Δx²⟩ ∝ t` on the same lattice Laplacian — with
  `select_power_law` now available, that panel is a short rung.
- **Materials-facing closer (#46).** Reframe the chapter-5 blind Ising prediction as the "predict a
  real material" figure.
- **Extend the selector to non-power-law candidates.** The menu is currently exponents; the natural
  next tool is a candidate *family* (e.g. `ω = c·k·√(1 − a k²)`, a gapped `√(k² + m²)`) scored the
  same way — which would let the bench discover the bend-down's functional form instead of only
  reporting that the exponent drops.
- **Push the isotropy claim to smaller `k`.** `A(K/4)` needs `N ≳ 128` for `[111]` to keep ≥ 3 modes;
  a larger-torus arm would test whether `A → 0` continues cleanly or floors on rounding.
- **Does the diagonal-edge blindness matter anywhere?** `⋆₁ = 0` on 2/3 of edges is a strong
  statement about this mesh. Worth a census rung asking which observables on the Kuhn torus are
  affected (1-form sector, per 8.15) and which are not.

---
**FIREWALL (R3).** A toy DEC scalar wave on a tetrahedral 3-torus. `ω`, `k`, "dispersion", "light
cone", "speed", "isotropy" name numerical properties of the discrete operator `Δ₀ = ⋆₀⁻¹D₀ᵀ⋆₁D₀` and
of least-squares fits to its Rayleigh quotients — never a real photon, a real light cone, or a
measurement of `c`. `c = 1` in code units only. Nothing here is a claim about nature.
