# Legacy Bubble migration notes

What this edition took from the project's own history, and what it refused. One section per source.

## The legacy manuscript — `/docs/bubble`, UniForgeCore `8cc4d10`, 2025-12-11

The source manuscript is `/docs/bubble` in the legacy UniForgeCore repository, last committed as
`8cc4d10` on 2025-12-11. It is a valuable editorial ancestor and an intentionally non-authoritative
scientific source.

### Carried forward

- The child-and-shadow opening and the Eratosthenes motif.
- The inclusive “we” voice: discovery as something author and reader do together.
- The repeated movement from observation to proposed structure to check.
- Concrete images—the shadow, the boundary, the ripple, the wall—before abstraction.
- The closing invitation to apply the method rather than merely accept a conclusion.

### Rewritten

- “Get data, give it shape, check, repeat” now requires a falsifier and a pre-registered control
  before the record run.
- Zero/one/two/four metaphysics becomes the measured eleven-step construction of the actual lattice:
  point, line, loop identity, clock, ripple, metric, patch, triangle, tetrahedral compromise, stella,
  and a two-science check.
- “Our bubble” becomes a reader-edition frame for a bounded toy region, never the shape of nature.
- Celebration moves from “the numbers matched” to the more durable achievement: the method can
  reproduce, predict, fail, diagnose, and correct itself in public.

### Not carried forward as results

The legacy manuscript's constant formulas and structural correspondences—including a tetrahedral
derivation of the fine-structure constant, `7π⁵ − 306`, faces-as-forces, octonion projection,
cosmological and black-hole numerology, and “eight tests passed”—do not meet the current R1/R3/R5
record standard. They remain part of project history, not part of this edition's evidence.

The legacy `index.html` is also not reused. It loads a Markdown parser from a CDN and renders
hand-authored claims. Our Bubble uses the current mdBook source and existing self-contained,
data-true lab figures.

## PaperTetra — `/Users/zacelston/code/PaperTetra`, commit `93a9f67`, imported 2026-09-02

A Rust + SQLite + TikZ project that generated tetrahedron figures for the legacy Physics-101 paper.
Its `CANONICAL_STANDARD.md` and `CANONICAL_INVARIANTS.md` had already worked out something this book
needs and did not have: that a canonical label is an **identity**, and that "just rotate it for this
figure" is how a standard dies. That discipline is what was imported, into
[`CANON.md`](CANON.md) and [`tools/canon.py`](tools/canon.py).

Its content was not imported, and could not be — the tetrahedron there carries a physics
interpretation, and this edition's [`FIREWALL.md`](FIREWALL.md) rules that out.

### Carried forward — the discipline

- **Labels are identities, not decorations.** Never permuted, rotated, or relabeled for aesthetics.
  (PaperTetra's "Critical Invariant", and its INV-1, INV-2, INV-3, INV-6.)
- **One canonical 2-D layout: the flat unfolded net**, not a 3-D perspective view — a central
  triangle with three folded out from its sides.
- **Its coordinate scheme for that net**, side 3, restated in `CANON.md` with the napkin's names.
  `tools/canon.py` derives the same six positions by reflection and asserts they are still those.
- **Fixed placement rules** for vertex, edge and face labels, and a stated fixed orientation.
- **A written list of forbidden practices** — the part of a standard that survives contact with a
  deadline.
- **One authoritative source that code and diagrams derive from** (INV-10), sharpened here: the
  source is `tools/napkin.py`, which the book already computes its early chapters from, so the
  standard is derived rather than restated and `make check` fails on drift.
- **Determinism as a requirement, not a hope** (INV-7), sharpened here from "up to floating-point
  tolerance" to exact: `canon.py` has no floating point, and two renders are asserted byte-identical.

### Refused — the interpretation

None of the following came in, under any wording:

- the five **domain models** over the four faces — Holography, General Relativity, String Theory, the
  Standard Model, Quantum Mechanics;
- the **face meanings** Time/Flow, Expansion, Reflection and Rotation, and the `F0…F3` indices that
  name them;
- the **edges as interactions** and as forces — "Color Mixing", "Structural Confinement",
  "E–B Coupling", "Gravitational Curvature", "Phase Inversion", "Field Induction", and their
  strong/weak/em/gravity categories;
- the **3+1 spacetime** and right-hand-rule documents that read a spacetime off the same net;
- **colours as physics** — the yellow/green/blue/red scheme whose whole purpose is to encode those
  meanings (INV-4).

These are analogy claims about nature attached to a combinatorial object, which is exactly what this
edition's firewall exists to stop. The closest of them — faces-as-forces — this file already refused
once, in the legacy manuscript section above. `tools/canon.py` enforces the refusal where it is
easiest to let slip: all four panels take the same fill, and the self-test asserts the emitted
drawing contains exactly one panel colour, so there is no colour left to carry a meaning.

### Refused — the stack

Not imported: Rust, SQLite, TikZ, LaTeX, `pdflatex`, the `paper-tetra` CLI, the seeded database and
the figure/caption generation scripts. This book builds with Python at mdBook build time and takes
no new dependency.

### Dropped for other reasons

- **`F0…F3` and `E0…E5` as names.** Indices into an interpretation this book does not have. A face
  here is named by its three dots, which a reader can check against the picture.
- **Whole-diagram rotation and reflection**, which PaperTetra's INV-5 explicitly permits. Fixed here
  instead: INV-5 is sound for a reader who already knows the object, and this book is written for one
  who does not.
- **±60° label rotation** on the side panels, and the special rule PaperTetra then needed to stop the
  bottom panel's labels being rotated into illegibility. Replaced by "every label is upright", which
  needs no exception.
- **The face-edge interaction table as a data model.** Which two faces meet along a line is already
  in the napkin's incidence, computed rather than tabulated.
- **Its own edge numbering**, in both forms — because there are two, and they disagree:
  `CANONICAL_STANDARD.md` says `E0 = F1 × F2`, `CANONICAL_INVARIANTS.md` says `E0 = F0 × F1`, and
  both are marked NORMATIVE. That contradiction is the best argument in the source for what
  `CANON.md` does instead: derive the order from the code that holds the object, and check the
  derivation on every build.
