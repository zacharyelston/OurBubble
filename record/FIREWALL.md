# FIREWALL — scope of claims

**StellaMaxCore is a computational electromagnetism library.** It solves
Maxwell's equations with Discrete Exterior Calculus on tetrahedral
simplicial complexes. That is the entire claim.

- The terms *photon, charge, flux quantum, stella-octangula* name features
  of the discretization and its geometry. They are standard EM / lattice
  vocabulary, used literally for the solver — not metaphysical claims.
- **"It is Maxwell"** means: the DEC operators reproduce the Maxwell /
  wave operator and dispersion on the lattice, validated in `tests/`. It
  does **not** assert anything about a theory of nature.
- **"Faster"** is a *performance hypothesis* about this solver vs a
  traditional grid (FDTD) solver. It is **not demonstrated in this crate
  yet** — there is no benchmark-vs-FDTD here. Do not claim "faster" until
  that benchmark (README Roadmap #1) is run with matched accuracy.
- **`quaternion_link` / `weyl_scale`** are connection *primitives* — the edge
  link generalized to `ℍ* = ℝ₊ × SU(2)` (scale × spinor) and the Weyl-scale
  sector's dynamics. They are in core only because `quaternion_link` is a
  *validated strict superset of the Maxwell connection* (the U(1) sub-case
  reproduces `compute_d_a` to machine precision) — engine, not theory. The
  *research* that uses them (localization-is-curvature, scale-doesn't-self-
  bind, pair+channel binding) stays in the parent project, firewalled.

The **legacy** exploratory research built on this engine in the parent
`stellamax` project (lattice Abelian–Higgs, binder searches,
effective-medium "warp/polarity" studies, any constant-derivation) stays in
that read-only repo and carried its own firewall there.

**One research arc lives here by design** (the "clean break"): the
**Above-the-stella** higher-dimensional program (`docs/ABOVE_THE_STELLA.md`),
tracked under `lab/` and run per the R-rules in [`docs/STELLAMAX.md`](docs/STELLAMAX.md). It is a **toy-model**
study — its terms (*photon, charge, θ-term, statistics, spin, bulk*) are
scaffolding, and any "forced" result (e.g. a forced θ = π) is a **derivation
within the construct**, fenced from any claim about nature, exactly the
discipline the legacy firewall demands. Engine and research claims stay
distinct: validated EM-core claims live in `tests/`; research claims live in
`lab/<...>/eval.md` with predictions registered before the run (R1).
