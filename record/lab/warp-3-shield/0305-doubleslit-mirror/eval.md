# 0305 — eval (R5)

**VERDICT: CONFIRMED, P0–P3 all pass** — gate `uf3_5_doubleslit_mirror_gate`
(registered `4435bca`, run `490f006`; probe breadcrumb `154c578`). Runtime 1.9 s.

> **FIREWALL.** Toy DEC scalar wave on a 200×140 triangle lattice. *Slit, screen, fringe,
> intensity* name lattice features and derived observables, never claims about nature. Not a
> Maxwell/EM simulation; no claim about physical double-slit experiments.

## Results

| prediction | measured | registered | pass |
|---|---|---|---|
| P0 front-arrival frame (demo arm A) | 231 | exactly 231 | ✅ |
| P0 slit-lobe ratio (A) | 3.758 | [3.0, 4.5] | ✅ |
| P0 screen-intensity mirror asym (A) | 1.372 | > 0.5 | ✅ |
| P1 max station asym (C, crossed + ⋆=I) | 5.17e-15 | < 1e-12 | ✅ |
| P1 intensity asym (C) | 4.41e-16 | < 1e-12 | ✅ |
| P1 front frame (C) | 228 | [200, 260] | ✅ |
| P1 fringe centers pair under y→140−y | exact (32↔108, 53↔87, 70) | ≤ 1 cell | ✅ |
| P2 max station asym (B, uniform + geom ⋆) | 1.42e-7 | < 1e-5 | ✅ |
| P2 crossed-mesh ⋆₀ mirror defect | 0.0 exactly | = 0 | ✅ |
| P2 max station asym (D, crossed + geom ⋆) | 4.33e-15 | < 1e-12 | ✅ |
| P3 fringe spacing (C) | 19.00 | [17, 22] | ✅ |
| P3 relative deviation from Δy = λL/d = 27.125 | 0.300, smaller | > 0.2, smaller | ✅ |
| P3 Fresnel parameter d²/(λL) | 2.36 | > 1 (documentation) | ✅ |

## What this rules in / out

- **The #252 diagnosis is confirmed as the mechanism, not just a correlation:** the identical
  scene on the alternating-diagonal mesh (`mesh_2d_triangle_grid_crossed`, y-mirror a mesh
  automorphism — unit-tested) is y-symmetric to machine precision (5e-15) at the same amplitude
  scale and timing (front 228 vs 231). The demo's ~3.4–3.8× lobe ratio is entirely the uniform
  diagonal's stencil asymmetry — the `⋆=I`/#23 family on a public page.
- **The #23 fix (geometric ⋆) kills the stencil asymmetry but is NOT machine-exact on the open
  uniform-diagonal mesh:** 1.4e-7, bounded by the boundary — the lumped ⋆₀ is itself
  mirror-asymmetric at the open corners (defect 1/6, full-population census). With the crossed
  mesh the ⋆₀ defect is exactly 0 and the geometric arm is machine-exact (4e-15). The two repairs
  compose; each mechanism is separately measured.
- **The geometric ⋆ is not a drop-in repair for THIS demo:** it changes the dispersion regime the
  page was tuned to — front arrives at frame 318 (vs 231), transmitted amplitude ~20× weaker at
  the demo's thresholds, fringe spacing 13.25. The drop-in repair is the crossed mesh at ⋆=I.
- **The #250 caveat now carries numbers:** the demo geometry is NOT in the far field
  (d²/(λL) = 2.36 > 1), so Δy = λL/d is out of its validity regime at these parameters
  independent of any lattice effect; the repaired lattice measures 19.0 vs the formula's 27.125
  (−30%). The page must present the formula as an out-of-regime textbook comparison, or drop it.

## Caveats (stated, not hidden)

- All bounds are scoped to the OPEN 200×140 mesh at the demo's exact parameters (λ=14, sep=64,
  dt=0.3, the two-column pinned drive). The P2 1e-5 bound in particular is about this mesh
  family/boundary, not a general statement about the cotan ⋆.
- The source is a PINNED two-column drive: the strip between source and barrier is a weak-loss
  driven cavity, so absolute transmitted amplitudes are detuning-sensitive (probed: the geometric
  arm's incident amplitude at the barrier is ~2.8× smaller). Amplitude ratios BETWEEN arms are
  therefore not clean dispersion statements; only the symmetry/timing/spacing observables are
  registered. (This is also #137's "accumulates transients / normalizes per-profile" complaint.)
- The fringe-spacing estimator is the clustered-local-maxima mean over the sponge-free band; the
  arm-B/D spacing (13.25) is reported but not registered — a separate rung would need to relate
  it to the actual lattice wavelength of the 5-point operator at this drive.

## Deferred / next (fed to the chapter menu)

- Wire the repair into the public page: `gen_doubleslit` exports a crossed-mesh "after" dataset;
  `doubleslit.html` gets a before/after toggle + the #250 out-of-regime caveat (this rung's
  remaining demo-wiring step; #137 remains the release-hardening epic).
- The driven-cavity systematic: measure the standing-wave detuning between source and barrier vs
  gap/λ — makes the absolute amplitudes registerable (feeds #137's "screen observable" item).
- The crossed mesh's light cone: the alternating diagonal restores mirror symmetry but not
  isotropy — measure its cone anisotropy vs the uniform mesh's (the 2-D cousin of the bridge
  chapter's 8.14 story).
- The geometric-⋆ demo: retune (λ, thresholds, frames) for the 5-point regime so the #23 fix is
  demo-visible too; then the page could show all three (defect / mesh repair / metric repair).
