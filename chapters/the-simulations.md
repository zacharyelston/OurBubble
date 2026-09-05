# Appendix · The Simulations

> **Scope.** Everything on this page describes computations inside a **toy** discrete lattice. The
> rung labels, gates, figures and commands below are the project's own record; they are not claims
> about nature. Words such as *vacuum*, *material*, *light cone* and *Ising* name patterns in the
> model.
> See [`FIREWALL.md`](../FIREWALL.md).

This appendix carries everything the narrative deliberately leaves out: which registered
experiment each chapter rests on, its gate, its data-true figure, the exact numbers the chapter
quotes and the file each one is carried by, and the commands that regenerate them.

The split is the point. A reader following the story should not have to step over a rung label to
finish a sentence; a reader checking the story should not have to hunt for the provenance.

**This book has a calculation system inside it.** It is a living document: when it is built, it goes
and reads the record. The section numbers are worked out from the table of
contents. The figures the chapters link to are drawn from their own runs' output, and are redrawn
whenever those runs are. So none of what follows was transcribed by hand once and left to drift: it is
what the record said when this copy of the book was made, and a fresh copy asks again. This page is
written by [`gen_appendix.py`](../gen_appendix.py), which the build runs before rendering; the checking
is done by [`check_edition.py`](../check_edition.py).

**Where the checking stops.** Every figure with a `read from` file beside it is checked, verbatim,
against that file. That column is the boundary. The history section below carries figures that sit
outside it deliberately, because they are not ours to check — they are checkable against the historical
record instead, which is a different and in some ways better guarantee.

Some sections cite no experiment of ours at all — the front door, the opening on method, and the
history chapter — and they say so rather than being left out, because a reader should be able to
tell *no evidence was cited* from *no evidence exists*. The closing chapter rests on commands you
run yourself.

One section per chapter, in reading order, **numbered from `00`** to match the order in
`chapters/SUMMARY.md`. Each also carries a stable anchor keyed to its chapter's name, which is what
the chapters link to.

**Leaving a note.** Every section in this book carries a small link at its heading — *Leave a note on
this section* — and it opens a short form about how that section read to you. A note is a gift and
not a test: "I lost the thread here" is a complete one, and you need not be right about any of the
maths. Sending it does need a free GitHub account, which is the honest limit of a way to write to us
that asks you for no email address and loads nothing onto the page you are reading.

---

<a id="s-what-you-will-have"></a>

## §00 · What you will have — the front door, and no experiment

**The chapter.** [what-you-will-have.md](what-you-will-have.md)

**What this section carries.** No rung, no gate, no figure and no quoted number — the front door is a statement about the book and how to read it, and it is listed here rather than left out so a reader can tell *no evidence was cited* from *no evidence exists*. Its promises are the later chapters' to keep, and each of those has its own section below. The standards are what its one scope claim rests on.


**Standards and record this section rests on.**

- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)
- [`FIREWALL.md`](record/FIREWALL.md)

**Numbers.** None. This section's chapter carries no quoted measurement.

---

<a id="s-the-shadow"></a>

## §01 · The shadow — the method, before any experiment

**The chapter.** [the-shadow.md](the-shadow.md)

**Standards and record this section rests on.**

- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)
- [`FIREWALL.md`](record/FIREWALL.md)
- [`PREDICTIONS.md`](record/PREDICTIONS.md)

**Numbers.** None. This section's chapter carries no quoted measurement.

---

<a id="s-a-few-thousand-years-of-sharper-shadows"></a>

## §02 · A few thousand years of sharper shadows — history, and none of it ours

**The chapter.** [a-few-thousand-years-of-sharper-shadows.md](a-few-thousand-years-of-sharper-shadows.md)

**What this chapter recounts.** Measurement history, and none of it is work of ours — no rung, gate, figure or quoted number here corresponds to any of it. It is listed in the order the chapter tells it, so a reader can check the chapter against the historical record rather than against us.

- ~240 BCE · Eratosthenes of Cyrene — the Earth's circumference, from two upright posts (Syene and Alexandria) and one shadow angle.
- ~270 BCE · Aristarchus of Samos — the Sun's distance, attempted. Right method; the angle needed is about 89.85°, and reading it as 87° puts the Sun ~20× the Moon's distance instead of ~400×. A resolution failure, not a reasoning one.
- ~150 BCE · Hipparchus of Nicaea — the Moon's distance, from the Earth's shadow on it during an eclipse. Very nearly right, because that geometry does not amplify a small angular error.
- Aristotle, *On the Heavens* II.14 (~350 BCE) — argues from the absence of any stellar shift that the Earth does not move. The null was real; the inference from it was not. Archimedes records Aristarchus's opposite reading — an enormous sphere of fixed stars. ~150 CE · Claudius Ptolemy's *Almagest* comes down on the same side, and that is the version that carried for over a thousand years.
- 1676 · Ole Rømer — that light takes time to travel, from Jupiter's moon Io slipping out of schedule with the Earth's distance. Rømer put the slippage at ~22 minutes across the width of Earth's orbit; the modern figure is ~17. Rømer gave the delay; Christiaan Huygens turned it into a speed, ~25% low because the delay was long.
- 1761–1769 · Edmond Halley (the method, set out decades earlier) and the transit expeditions, James Cook to Tahiti among them — the Sun's distance, at last, from Venus transits timed at widely separated places.
- 1838 · Friedrich Bessel — stellar parallax, found. ~0.3 arcseconds for 61 Cygni. The answer to the ~150 CE null, seventeen centuries later.
- 1912 · Henrietta Swan Leavitt — the period–luminosity relation: a pattern turned into a distance ruler, reaching past what any triangle could.

What the book carries forward is the **method** — measure, state your resolution, let a finer instrument overturn you — never the discoveries. The record's own two self-corrections are set against that history much later, in the chapter that published the misses.

**Numbers.** None declared, and none checked here. The dates and angles in the list above are historical: they are checkable against the historical record rather than against this repository, which is the one guarantee this book cannot give you itself.

---

<a id="s-two-dots-and-a-line"></a>

## §03 · Two dots, a line, and the first thing that closes — the object, from nothing

**The chapter.** [two-dots-and-a-line.md](two-dots-and-a-line.md)

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)

**Numbers.** None quoted. Every number in this section's chapter is worked out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), which holds the rule and the tables, and [`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes larger than one tetrahedron — and re-derived on every build, so the thing to check is not a file but the arithmetic, which the chapter shows you.

---

<a id="s-one-tetrahedron-is-a-whole-world"></a>

## §04 · One tetrahedron is a whole world — every kind of number, on a napkin

**The chapter.** [one-tetrahedron-is-a-whole-world.md](one-tetrahedron-is-a-whole-world.md)

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)

**Numbers.** None quoted. Every number in this section's chapter is worked out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), which holds the rule and the tables, and [`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes larger than one tetrahedron — and re-derived on every build, so the thing to check is not a file but the arithmetic, which the chapter shows you.

---

<a id="s-make-it-move"></a>

## §05 · Make it move — the one rule, and what one tick does

**The chapter.** [make-it-move.md](make-it-move.md)

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)

**Numbers.** None quoted. Every number in this section's chapter is worked out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), which holds the rule and the tables, and [`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes larger than one tetrahedron — and re-derived on every build, so the thing to check is not a file but the arithmetic, which the chapter shows you.

---

<a id="s-the-shape-between"></a>

## §06 · The shape between — one tetrahedron, cut open

**The chapter.** [the-shape-between.md](the-shape-between.md)

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)

**Numbers.** None quoted. Every number in this section's chapter is worked out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), which holds the rule and the tables, and [`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes larger than one tetrahedron — and re-derived on every build, so the thing to check is not a file but the arithmetic, which the chapter shows you.

---

<a id="s-two-worlds-threaded"></a>

## §07 · Two worlds threaded — the last object that fits on a napkin, and the first that does not

**The chapter.** [two-worlds-threaded.md](two-worlds-threaded.md)

**What this chapter deliberately does not say.** Two readings of the threaded pair were put to the same arithmetic and refused. Both are on the page above, rather than argued with in the prose.

**No tick both holds and comes home.** The book's tick is over the size this shape's own numbers allow, so the run grows instead of sloshing. A smaller tick stops the growth and buys nothing else. At no tick that can be written as a fraction does the pair of rows return to the pair it started from.

**And no such tick gives a table.** Every tick under the bound prints two rows at most. After that the numbers stop fitting in a couple of decimal places, which is the test every table in these chapters is held to.

Both come from the vendored engine, rendered by `stella_refusal` — register rows R16, R17, R18 and R20 of `lab/napkin/0001`. The bound is certified by an integer eigenvector: whole numbers throughout, no decimals, no square roots. That is why a refusal about an object of fourteen dots is still something a reader can check.

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)

**Numbers.** None quoted. Every number in this section's chapter is worked out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), which holds the rule and the tables, and [`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes larger than one tetrahedron — and re-derived on every build, so the thing to check is not a file but the arithmetic, which the chapter shows you.

---

<a id="s-room-and-a-world-with-no-edge"></a>

## §08 · Room, and a world with no edge — why tetrahedra need a compromise

**The chapter.** [room-and-a-world-with-no-edge.md](room-and-a-world-with-no-edge.md)

**Registered rungs.**

- The Container, chapter 00 — the eleven-step object ramp

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`viz/synthesis-slow-ramp.html`](record/viz/synthesis-slow-ramp.html)
- [`viz/synthesis.html`](record/viz/synthesis.html)

**Standards and record this section rests on.**

- [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md)
- [`book/chapters/README.md`](record/book/chapters/README.md)

**Numbers the narrative may quote.**

| value | what it is | read from |
|---|---|---|
| `70.5288°` | the angle between two faces of one tetrahedron, meeting along an edge | [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md) |
| `5.1043` | how many such tetrahedra it would take to close a full turn around that edge — not a whole number | [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md) |
| `7.3561°` | the wedge left over once five are packed in: what no sixth tetrahedron can fill | [`book/chapters/00-the-object/chapter.md`](record/book/chapters/00-the-object/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo run --release -p viz --bin gen_synthesis -- "$(git rev-parse --short HEAD)"
```

---

<a id="s-the-round-ripple"></a>

## §09 · Is it round? — the dial, set twice

**The chapter.** [the-round-ripple.md](the-round-ripple.md)

**Registered rungs.**

- warp-1 1.5 — lattice-matched isotropy
- warp-1 1.7 — blind dispersion in five directions
- warp-3 3.5 — the demo's mesh asymmetry, and its repair

**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/warp-1-move/0115-lattice-matched-isotropy`](record/lab/warp-1-move/0115-lattice-matched-isotropy)
- [`lab/warp-1-move/0117-dispersion-isotropy`](record/lab/warp-1-move/0117-dispersion-isotropy)
- [`lab/warp-3-shield/0305-doubleslit-mirror`](record/lab/warp-3-shield/0305-doubleslit-mirror)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf1_5_lattice_matched_gate.rs`](record/core/uniforge/tests/uf1_5_lattice_matched_gate.html)
- [`core/uniforge/tests/uf1_7_dispersion_isotropy_gate.rs`](record/core/uniforge/tests/uf1_7_dispersion_isotropy_gate.html)
- [`core/uniforge/tests/uf3_5_doubleslit_mirror_gate.rs`](record/core/uniforge/tests/uf3_5_doubleslit_mirror_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html`](record/lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html)
- [`lab/warp-1-move/0117-dispersion-isotropy/figures/discovery.html`](record/lab/warp-1-move/0117-dispersion-isotropy/figures/discovery.html)
- [`lab/warp-3-shield/0305-doubleslit-mirror/figures/doubleslit_mirror.html`](record/lab/warp-3-shield/0305-doubleslit-mirror/figures/doubleslit_mirror.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `22.4%` | [`book/chapters/01-the-light-cone/chapter.md`](record/book/chapters/01-the-light-cone/chapter.md) |
| `2.2%` | [`book/chapters/01-the-light-cone/chapter.md`](record/book/chapters/01-the-light-cone/chapter.md) |
| `10.2` | [`book/chapters/01-the-light-cone/chapter.md`](record/book/chapters/01-the-light-cone/chapter.md) |
| `1.00 ± 0.016` | [`book/chapters/01-the-light-cone/chapter.md`](record/book/chapters/01-the-light-cone/chapter.md) |
| `33.2%` | [`book/chapters/01-the-light-cone/chapter.md`](record/book/chapters/01-the-light-cone/chapter.md) |
| `3.8×` | [`book/chapters/03-the-shield/chapter.md`](record/book/chapters/03-the-shield/chapter.md) |
| `5×10⁻¹⁵` | [`book/chapters/03-the-shield/chapter.md`](record/book/chapters/03-the-shield/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf1_5_lattice_matched_gate -- --nocapture
cargo run  --release -p viz     --bin gen_isotropy
cargo test --release -p uniforge --test uf3_5_doubleslit_mirror_gate -- --nocapture
cargo run  --release -p viz     --bin gen_doubleslit_mirror
```

---

<a id="s-the-bubble-and-its-bill"></a>

## §10 · What does pushing on it cost? — the shaped push and its bill

**The chapter.** [the-bubble-and-its-bill.md](the-bubble-and-its-bill.md)

**Registered rungs.**

- warp-2 2.0 — the shaped shift's energy structure

**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/warp-2-energy/0200-shaped-shift-energy`](record/lab/warp-2-energy/0200-shaped-shift-energy)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf2_energy_structure_gate.rs`](record/core/uniforge/tests/uf2_energy_structure_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/warp-2-energy/0200-shaped-shift-energy/figures/energy_structure.html`](record/lab/warp-2-energy/0200-shaped-shift-energy/figures/energy_structure.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `336×` | [`book/chapters/02-the-price-of-warp/chapter.md`](record/book/chapters/02-the-price-of-warp/chapter.md) |
| `1360×` | [`book/chapters/02-the-price-of-warp/chapter.md`](record/book/chapters/02-the-price-of-warp/chapter.md) |
| `6.1×` | [`book/chapters/02-the-price-of-warp/chapter.md`](record/book/chapters/02-the-price-of-warp/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf2_energy_structure_gate -- --nocapture
cargo run  --release -p viz     --bin gen_energy
```

---

<a id="s-the-wall-that-worked-and-didnt"></a>

## §11 · Can you wall a piece off? — one experiment, one yes and one no

**The chapter.** [the-wall-that-worked-and-didnt.md](the-wall-that-worked-and-didnt.md)

**Registered rungs.**

- warp-3 3.0 — shield imbalance and inertia
- warp-3 3.4 — the four-source volume null

**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/warp-3-shield/0300-shield-imbalance-inertia`](record/lab/warp-3-shield/0300-shield-imbalance-inertia)
- [`lab/warp-3-shield/0304-four-source-null`](record/lab/warp-3-shield/0304-four-source-null)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf3_shield_imbalance_gate.rs`](record/core/uniforge/tests/uf3_shield_imbalance_gate.html)
- [`core/uniforge/tests/uf3_4_four_source_null_gate.rs`](record/core/uniforge/tests/uf3_4_four_source_null_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/warp-3-shield/0300-shield-imbalance-inertia/figures/shield.html`](record/lab/warp-3-shield/0300-shield-imbalance-inertia/figures/shield.html)
- [`lab/warp-3-shield/0304-four-source-null/figures/null.html`](record/lab/warp-3-shield/0304-four-source-null/figures/null.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `2.0×10⁻⁶` | [`book/chapters/03-the-shield/chapter.md`](record/book/chapters/03-the-shield/chapter.md) |
| `0.86` | [`book/chapters/03-the-shield/chapter.md`](record/book/chapters/03-the-shield/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf3_shield_imbalance_gate -- --nocapture
cargo run  --release -p viz     --bin gen_shield
cargo test --release -p uniforge --test uf3_4_four_source_null_gate -- --nocapture
cargo run  --release -p viz     --bin gen_null
```

---

<a id="s-where-negative-energy-appears"></a>

## §12 · Can a gap be emptier than empty? — the one place the sign is real

**The chapter.** [where-negative-energy-appears.md](where-negative-energy-appears.md)

**Registered rungs.**

- warp-4 4.0 — the Casimir-like negative baseline
- warp-4 4.2 — the automated bench that fitted it

**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/warp-4-vacuum/0400-casimir-negative-energy`](record/lab/warp-4-vacuum/0400-casimir-negative-energy)
- [`lab/warp-4-vacuum/0402-automated-bench`](record/lab/warp-4-vacuum/0402-automated-bench)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf4_casimir_energy_gate.rs`](record/core/uniforge/tests/uf4_casimir_energy_gate.html)
- [`core/uniforge/tests/uf4_casimir_force_gate.rs`](record/core/uniforge/tests/uf4_casimir_force_gate.html)
- [`core/uniforge/tests/uf4_automated_bench_gate.rs`](record/core/uniforge/tests/uf4_automated_bench_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/warp-4-vacuum/0400-casimir-negative-energy/figures/casimir.html`](record/lab/warp-4-vacuum/0400-casimir-negative-energy/figures/casimir.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `−0.13099` | [`book/chapters/04-the-vacuum/chapter.md`](record/book/chapters/04-the-vacuum/chapter.md) |
| `−π/24 = −0.13090` | [`book/chapters/04-the-vacuum/chapter.md`](record/book/chapters/04-the-vacuum/chapter.md) |
| `0.07%` | [`book/chapters/04-the-vacuum/chapter.md`](record/book/chapters/04-the-vacuum/chapter.md) |
| `−0.9997` | [`book/chapters/04-the-vacuum/chapter.md`](record/book/chapters/04-the-vacuum/chapter.md) |
| `−2.007` | [`book/chapters/04-the-vacuum/chapter.md`](record/book/chapters/04-the-vacuum/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf4_casimir_energy_gate -- --nocapture
cargo test --release -p uniforge --test uf4_casimir_force_gate  -- --nocapture
cargo run  --release -p viz     --bin gen_casimir
```

---

<a id="s-a-number-without-the-answer-key"></a>

## §13 · Can it tell me something I didn't tell it? — the answer key taken away

**The chapter.** [a-number-without-the-answer-key.md](a-number-without-the-answer-key.md)

**Registered rungs.**

- warp-5 5.0 — the solved two-dimensional validation
- warp-5 5.1 — the blind three-dimensional swing
- warp-5 5.2 — the self-contained pipeline
- warp-5 5.3 — the fully blind close, with its registered limit
- warp-5 5.9 · warp-5 5.10 — the two negatives re-analysed, and traced to the estimator rather than the lattice

**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/warp-5-universality/0500-ising-universality`](record/lab/warp-5-universality/0500-ising-universality)
- [`lab/warp-5-universality/0501-montecarlo-prediction`](record/lab/warp-5-universality/0501-montecarlo-prediction)
- [`lab/warp-5-universality/0502-self-contained`](record/lab/warp-5-universality/0502-self-contained)
- [`lab/warp-5-universality/0503-blind-3d`](record/lab/warp-5-universality/0503-blind-3d)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf5_universality_gate.rs`](record/core/uniforge/tests/uf5_universality_gate.html)
- [`core/uniforge/tests/uf5_3_blind3d_gate.rs`](record/core/uniforge/tests/uf5_3_blind3d_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/warp-5-universality/0500-ising-universality/figures/universality.html`](record/lab/warp-5-universality/0500-ising-universality/figures/universality.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `0.4999999` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `1.000000` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.9996` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.315` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `1.259` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.325` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `1.24` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `T_c = 4.5099` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `4.5115` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.036%` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.630` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |
| `0.766` | [`book/chapters/05-universality/chapter.md`](record/book/chapters/05-universality/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf5_universality_gate -- --nocapture
cargo run  --release -p viz     --bin gen_universality
cargo test --release -p uniforge --test uf5_3_blind3d_gate -- --nocapture
```

---

<a id="s-when-the-expected-law-fails"></a>

## §14 · When the world you built says no — the obvious answer refused, and two published misses dissolved

**The chapter.** [when-the-expected-law-fails.md](when-the-expected-law-fails.md)

**Registered rungs.**

- dna-thz 6.1 — the permittivity shift law, and the falsified square root
- warp-5 5.9 — reprocessing a registered negative: the bond miss dissolves into the locator
- warp-5 5.10 — the site miss dissolves inside an error bar the rung had already published

The chapter guards the vocabulary it actually uses — cavity, resonance, material weight, exponent. The record's own name for this experiment is wider: it was registered as a **toy bridge toward terahertz spectroscopy of biological material**, asking whether a lattice Maxwell solver reproduces the frequency-shift signatures that field shares. No molecule, cell or clinical sample appears anywhere in the run; the bridge is the question the rung was aimed at, and the exponent below is the answer it got.

**The last two beats are a coda about the record, not about this experiment.** They look back at two quantities this record had published as misses. Both were later dissolved. The bond one went to the locator's own published margin, carried through at last. The site one needed an estimator written for the next rung. Both re-analyses are rungs in their own right, and they are listed above with the refusal: the chapter that owns a miss owns its correction. The history the coda measures itself against is in the section for [a few thousand years of sharper shadows](a-few-thousand-years-of-sharper-shadows.md), which cites no work of ours.


**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.

- [`lab/dna-thz/0001-dna-permittivity-shift-law`](record/lab/dna-thz/0001-dna-permittivity-shift-law)
- [`lab/warp-5-universality/0509-bond-locator-reprocess`](record/lab/warp-5-universality/0509-bond-locator-reprocess)
- [`lab/warp-5-universality/0510-site-locator-reprocess`](record/lab/warp-5-universality/0510-site-locator-reprocess)

**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.

- [`core/uniforge/tests/uf6_1_thz_shift_law_gate.rs`](record/core/uniforge/tests/uf6_1_thz_shift_law_gate.html)
- [`core/uniforge/tests/uf5_9_bond_locator_reprocess_gate.rs`](record/core/uniforge/tests/uf5_9_bond_locator_reprocess_gate.html)
- [`core/uniforge/tests/uf5_10_site_locator_reprocess_gate.rs`](record/core/uniforge/tests/uf5_10_site_locator_reprocess_gate.html)

**Data-true figures.** Rendered from the run's own committed output — no analogy art.

- [`lab/dna-thz/0001-dna-permittivity-shift-law/figures/shift_law.html`](record/lab/dna-thz/0001-dna-permittivity-shift-law/figures/shift_law.html)

**Numbers the narrative may quote.**

| value | read from |
|---|---|
| `p = −0.2753` | [`book/chapters/06-dna-thz/chapter.md`](record/book/chapters/06-dna-thz/chapter.md) |
| `R² = 0.9774` | [`book/chapters/06-dna-thz/chapter.md`](record/book/chapters/06-dna-thz/chapter.md) |
| `p = −1/2` | [`book/chapters/06-dna-thz/chapter.md`](record/book/chapters/06-dna-thz/chapter.md) |

**Regenerate.** From the engine checkout (`.record/`, or your own UniForge clone):

```sh
cd core
cargo test --release -p uniforge --test uf6_1_thz_shift_law_gate -- --nocapture
cargo run  --release -p viz     --bin gen_shift_law
```

---

<a id="s-cast-your-own-shadow"></a>

## §15 · Cast your own shadow — the reproduce path

**The chapter.** [cast-your-own-shadow.md](cast-your-own-shadow.md)

**Standards and record this section rests on.**

- [`PREDICTIONS.md`](record/PREDICTIONS.md)
- [`book/LESSON_STANDARD.md`](record/book/LESSON_STANDARD.md)
- [`docs/DEMOS.md`](record/docs/DEMOS.md)

**Numbers.** None. This section's chapter carries no quoted measurement.

**Regenerate.** From this repository's root:

```sh
python3 check_edition.py
mdbook build
python3 check_edition.py --rendered
```
