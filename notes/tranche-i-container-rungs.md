# Tranche I — the Container rungs the record already has

*Working note, 2026-09-08. Structure lane. Scopes
https://github.com/zacharyelston/OurBubble/issues/107 (the book side) against the UniForge campaign
https://github.com/zacharyelston/UniForge/issues/364 (C-6, "cite what exists", is this tranche).
Read after `notes/a-kleist-edition.md` § 3.1 and PR #106, which named each result chapter's object.*

> **Scope.** A note about which computations on a **toy** lattice a book about that toy may cite.
> Nothing in it is a claim about nature.

## 1 · The question

PR #106 made the book honest about its objects: none of the five result chapters runs on the
Container, the world the reader finishes building in *Room, and a world with no edge*. The owner's
next question was whether the labs should be redesigned so that the book can run on one object. They
should, and that is the UniForge campaign. But before any lab is redesigned, the record at the
commit the book pins already holds runs on the Container that the book does not cite. Citing them
costs no run and changes what the reader is told about the object she built. That is this tranche.

## 2 · What the pinned record holds

Checked against `.record/` at `db59a2fc`, the commit `record.lock` pins. Every rung below exists at
that commit, so this tranche is **not a record bump**: the pin stays, and only the list of cited
paths grows.

| rung | object | what it measured | verdict |
|---|---|---|---|
| `lab/warp-5-universality/0504-stella-ising` (5.4) | the stella tet-oct complex, `mesh_3d_chiral_tetoct_yz_periodic` — the Container's geometry, wrapped in two directions and open in the third | Ising switches on the mesh's own vertices (coordination 14). `T_c = 11.638`, located blind inside the registered range `[11.3, 12.0]`; `U* = 0.305` against the cubic 0.484, as registered; `γ/ν = 1.895` and `β/ν = 0.515`, within 3.5 % and 0.6 % of the class values, inside the registered 6 % and 8 % | CONFIRMED |
| `lab/lattice-constants/0700-watson-constant` (7.0) | the stella graph, `mesh_3d_chiral_tetoct` (14-regular, vertex-transitive) | the simple-random-walk return constant `G = 1.302310014103`, after reproducing Watson's closed forms on the simple-cubic and face-centred lattices to 1e-12 | CONFIRMED |
| `lab/lattice-constants/0701-spectral-entropy` (7.1) | the same graph | the spectral-entropy defect `σ = −0.0439377153`; a registered negative on the "metric as prior" bridge | CONFIRMED + NEGATIVE (P3) |
| `lab/bridge/0802-electrical` (8.2) | the same graph | the Laplacian read as a resistor network and as a random walk; commute time equals `2|E|·R_eff` to 5.7e-14; spanning-tree entropy `z = 2.5761244` | CONFIRMED |
| `lab/bridge/0803-netlist` (8.3) | the same graph | the graph exported as a SPICE netlist (189 resistors) and solved by modified nodal analysis, an independent formulation; agrees with the engine's effective resistance to 5.6e-17 | CONFIRMED |
| `lab/warp-2-energy/0207-stella-matter-antimatter` (2.7) | `mesh_3d_tetrahedral_grid` — the cube cut six ways, with the parity two-colouring | opposite colours bind, like colours repel, equal magnitude | CONFIRMED |
| `lab/warp-5-universality/0506`, `0507` (5.6, 5.7) | `mesh_3d_chiral_tetoct` | site and bond percolation thresholds of the stella graph, two new constants; one registered negative on 5.6's fractal-dimension arm | CONFIRMED + NEGATIVE |

## 3 · Where each lands, and where it does not

The rule from PR #106 holds: a chapter names its object where the run begins, and a number is
called registered only if the spec carries it.

**5.4 → *Can it tell me something I didn't tell it?*, a new beat after the miss and before the last
question.** The chapter's own claim structure — two lattices, different non-universal numbers, the
same class numbers — is exactly what 5.4 did, on the reader's object. The beat says what the object
was (the Container's shapes and cuts, wrapped in two directions for the run, with ends in the
third), that the critical temperature was registered as a range with its reason, and that the class
numbers held inside their registered margins. It quotes four numbers in bold, all from 5.4's
`eval.md`, all declared in the appendix. The record has no stella-specific figure for this rung
(its `eval.md` says so), so the beat links none.

**7.0, 8.2, 8.3 → *Cast your own shadow*, in the beat that asks the reader to re-run a test.** These
are the most checkable things in the record: a three-second gate, and a circuit file any circuit
simulator will run. The beat names them as the Container's own and as the shortest re-runs; their
rungs, gates, figures and commands go in the chapter's appendix section. No number is quoted in
prose. This is the "sentence" option of #107's question about the circuit view; a primer door or a
chapter of its own is the owner's call and is not foreclosed by a sentence.

***Room, and a world with no edge*, last beat.** The sentence "its runs were made on plainer worlds
like it" is no longer true once 5.4 is cited. It narrows to "most of its runs", and says that where
a run was made on this object, the chapter says so. No count, so nothing to go stale as the
campaign lands.

**7.1 — not cited.** Its confirmed part is a constant with no chapter to belong to, and its negative
is about a bridge the book does not walk.

**2.7 — not cited.** Its object is the cube cut six ways, not the Container. The two-colouring it
tests is the one the reader performs in *Room*, and the result is worth a sentence one day, but it
would have to name its object, and that object is the ripple's world, which the reader has not met
when she colours the corners. It waits for the campaign's C-1, or for the push chapter.

**5.6, 5.7 — not cited.** The answer-key chapter is at ten beats and the reader has one new object
to absorb there, not three constants. They are listed in the campaign issue.

## 4 · Mechanics

- `edition.json`: three appendix sections gain rungs, entries, gates, figures, commands and (for 5.4)
  record quotes. No chapter entry changes.
- `record.lock`: the `path =` block is regenerated with the command in its header. The pin does not
  move.
- `record/`: re-derived with `tools/snapshot_record.sh` from `.record/` at the pin.
- `OUTLINE.md`: the answer-key chapter's beats 8–10, *Room*'s beat 8, the exit chapter's beat 4.
- Tier 0 as always: `check_edition.py` (full, with the attacks), `mdbook build`, `--rendered`,
  `tools/beat_coverage.py`, `tools/demo_steps.py --check`, `tools/figures.mjs --check`.
- Content: fresh reader before the owner, per the standing order; merges on the owner's word.

## 5 · What this tranche leaves for the campaign

The five wave and switch results still run where PR #106 says they run. The campaign's order stands:
the Container's dial first (C-0; the geometric ⋆₁ is indefinite on the screw bonds, rung 8.13, with
positive repairs at 8.14 and 8.16), then the ripple, the wall, the box, the gap and the push bill.
As each lands, the object line in its chapter changes, and the "plainer worlds" sentence in *Room*
retires.

FIREWALL: this note concerns a book about a toy DEC lattice; the rungs named are computations on it,
never claims about nature.
