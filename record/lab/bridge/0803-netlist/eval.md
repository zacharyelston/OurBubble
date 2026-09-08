# 0803 — the netlist / SPICE view: evaluation

**Verdict:** CONFIRMED · **Gate:** `uf8_3_netlist_gate` (green: yes) · **Register:** `f289b44` · **Run:** `82696f1`

## Result

"The circuit computes it" is now literal. The stella graph exports as a real **SPICE netlist**
([`data/stella.cir`](data/stella.cir) — 189 resistors, runnable in ngspice/LTspice), and an independent
**modified-nodal-analysis** solve (the formulation SPICE uses: a voltage-source probe, `R = V/I`)
reproduces our `effective_resistance` to **5.6e-17** — machine precision. The netlist view earns
membership; the electrical view (#4) is now a physical, portable circuit.

| prediction | expected | measured | pass |
|---|---|---|---|
| P0 MNA series / parallel / **cube-diagonal** | 2 / 0.5 / **5/6** | exact (≤ 1e-15) | ✅ |
| P1 netlist-MNA `==` `effective_resistance` (stella, 4 pairs) | < 1e-9 | ≤ **5.6e-17** | ✅ |
| P2 walks↔circuits `2E·R(netlist) == commute` | < 1e-9 | ≤ 5.0e-14 | ✅ |
| P3 portable `.cir` well-formed (`|E|` resistors, V1/.op/.end) | yes | 189 R-lines ✓ | ✅ |

Data: [`data/`](data) (`stella.cir`, `resistance.csv`, `walks_circuits.csv`, `summary.csv`).
Figure: [`figures/netlist.html`](figures/netlist.html).

## What it rules in / out

- **Rules in:** the electrical view is a *real circuit*. The export is faithful — a textbook
  circuit-analysis method (MNA, what SPICE runs) applied to the emitted netlist lands on the same
  resistances the graph Laplacian gives, to machine precision. And it closes the loop across rungs:
  `2E·R` from the netlist equals rung 8.2's random-walk commute time. This is the analog / in-memory
  (resistor-crossbar, memristor) computing lineage made concrete on the toy graph.
- **The controls matter:** the MNA solver is validated *independently* of the graph path on closed
  forms — series `2 Ω`, parallel `0.5 Ω`, and the classic **cube space-diagonal `5/6 Ω`** — so P1's
  agreement is two trustworthy methods meeting, not one method checking itself.
- **Rules out nothing physical** (firewall): `stella.cir` is a computer *for the toy graph's
  mathematics* (its resistances and walk probabilities) — building or simulating it does not make the
  toy nature.

## Scope / caveats

- **No external SPICE in CI:** the gate's independent check is the in-repo MNA solver (validated on
  closed forms). `data/stella.cir` is portable — running it in ngspice/LTspice is an optional human
  cross-check (the netlist is the artifact; the tool is not a build dependency).
- Numbering: grounding a node must renumber the rest contiguously, or the MNA matrix gets an all-zero
  row and goes singular (caught in the probe; `to_spice_netlist` handles it).

## Deferred / next (→ chapter menu)

- **AC/RLC netlist (impedance view):** emit an LC network whose **resonances are the Laplacian
  eigenvalues** — spectrum as resonant frequencies (the "light cone you can measure on a scope").
- **weighted netlist:** per-edge resistances from a geometric `⋆₁` (not all 1 Ω) — the metric as
  conductances; ties to the #23-defect isotropy story.
- **ngspice CI cross-check:** if a SPICE binary is added to CI, gate `stella.cir` against a real
  external solve (turns the optional human check into an automated one).
