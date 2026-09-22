# 0803 — Bridge-8.3: the netlist / SPICE view (the electrical view, made a real circuit)

**Chapter:** [`..`](..) · **Gate:** `core/uniforge/tests/uf8_3_netlist_gate.rs` · **Status:** CONFIRMED — see [`eval.md`](eval.md)

## Goal (one paragraph)

Make "the circuit computes it" literal (Epic #224). Export the stella graph as a real **SPICE netlist**
(a 1 Ω resistor per edge, a 1 V probe source, one node grounded) — a portable artifact a person could
run in ngspice/LTspice or breadboard — and verify that an **independent** circuit-level solve reproduces
our `effective_resistance`. The independent solver is **modified nodal analysis (MNA)**, the formulation
SPICE itself uses (a voltage source augments the system; `R = V/I`), a genuinely different code path
from rung 8.2's "ground a node and solve `L`". This makes the electrical view (view #4) *physical* and
ties to the analog / in-memory (resistor-crossbar / memristor) computing lineage.

## Firewall (R3)

A resistor network of a **toy** 14-regular lattice graph. It is a physical *computer for the toy's graph
mathematics* (resistances, walk probabilities) — **never** a physical realization of the warp/photon
analogy. Emitting or building the circuit does not make the toy nature; it runs the toy's linear algebra
in copper instead of f64. Dimensionless; c = G = 1.

## Method (sketch)

- **`kinematics::views`** (module additions): `to_spice_netlist(edges, probe_a, ground_b)` (emits the
  `.cir`; non-ground nodes numbered contiguously so grounding leaves no gap → non-singular MNA);
  `mna_resistance(netlist)` (parses R/V lines, stamps the conductance matrix + the voltage-source
  augmentation, solves via `dense_solve`, returns `R = V/I`); `GraphView::edges`.
- **Graph:** the rule-built 14-regular stella torus (M=3, 27 nodes, 189 edges — 7.0's graph), from which
  the gate builds both the edge list (→ netlist) and the dense Laplacian (→ `effective_resistance`,
  reference). Deterministic f64; no RNG/wall-clock. The stella `.cir` is written to `data/` (R10 artifact).
- **No external SPICE in CI:** ngspice is not assumed present; the gate's independent check is the in-repo
  MNA solver (textbook formulation, validated on closed-form circuits). The emitted `.cir` is portable —
  an external SPICE run is an optional human check, noted in `eval.md`.

R9 unit tests (module): MNA reproduces series 2 Ω, parallel 0.5 Ω, and the **cube space-diagonal 5/6 Ω**;
MNA `==` `effective_resistance` on the cube.

## Predictions (registered before the run; tolerances probe-informed)

- **P0 (MNA controls, closed forms):** `mna_resistance` of the emitted netlists reproduces the textbook
  values — series `2`, parallel `0.5`, cube diagonal `5/6` — each `< 1e-9`. — *gate asserts.*
- **P1 (the netlist-view membership gate):** on the stella torus (M=3), `mna_resistance` of the emitted
  netlist equals `kinematics::views::effective_resistance` for several node pairs, `< 1e-9` (probe:
  ≤ 5.6e-17). The export is faithful and the SPICE formulation agrees — the view joins. — *gate asserts.*
- **P2 (cross-rung: walks↔circuits via the netlist):** `2·|E|·R(netlist) == commute_time` (rung 8.2's
  random walk) for several pairs, `< 1e-9` — the netlist export closes the same duality that defined the
  4th view. — *gate asserts.*
- **P3 (portable artifact):** the emitted stella `.cir` is well-formed — exactly `|E|` resistor lines,
  a `V1` probe source, `.op`, and `.end` — and is written to `data/stella.cir`. — *gate asserts.*

## What would falsify this

If `mna_resistance ≠` the closed forms (P0), the MNA solver is wrong. If netlist-MNA `≠`
`effective_resistance` on the stella graph (P1), the export is unfaithful and the netlist view fails its
membership test. If `2E·R ≠ commute_time` (P2), the netlist and random-walk views disagree. If the `.cir`
is malformed (P3), it is not a runnable circuit. Any miss is reported (R5), not retuned.
