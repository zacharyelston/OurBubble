> **Provenance note (2026-09-02).** Issue #28 chartered this file as *octahedron-timekeeper.md*; the
> owner reframed the question mid-lane ("we don't have to call it time — it's information transfer")
> and the file was renamed to *crossing* without the rename being recorded. Recorded here.
>
> **What is scoped how, because one scope was doing the work of two** (a proofreader, 2026-09-02).
> The rows below fall into two kinds. **Rows 1, 2, 4 and 6 are counts and closures on the record's
> own chiral periodic tiling** — the `6³` and `12³` meshes, the face pairing, the line census, the
> line-visit comparison, the hull — and they stand as counts: they are what that mesh contains,
> whatever a rule does on it. **Rows 3 and 5 are readings of the tick**, and they test ONE reading:
> the bare octahedron, 0-forms, a time-symmetric leapfrog. They say nothing about the family's actual
> claim — a one-way screw on the chiral periodic mesh, on 1-forms — which remains open: see UniForge
> `lab/napkin/0002-octahedron-clock-review/review.md` (issue #356). So "computed FALSE" as a verdict
> on *the octahedron and time* is warranted only for *a tick is not a trip round the bare
> octahedron*; where FALSE appears in rows 2 and 6 it is a count that came out otherwise than the
> proposal said, on the mesh the record builds.

# The octahedron as the crossing between cells — what the numbers say

Lane note, not chapter text. Issue [#28](https://github.com/zacharyelston/OurBubble/issues/28).
Every number here is produced and asserted by [`tools/octahedron.py`](../tools/octahedron.py) —
`python3 tools/octahedron.py` prints this report and takes itself down if any line of it stops being
true. Exact throughout: integers and `fractions.Fraction`, no floating point anywhere, and the one
irrational bound is pinned by exact rational tests (Sylvester's criterion on `M·I − Δ₀`), never by a
decimal.

The object is the record's: `core/geom/src/mesh.rs` in UniForge at the pinned commit `db59a2fc`
(`mesh_3d_chiral_tetoct_periodic`, lines 796–864; the cut rule `chiral_oct_screw111`, lines 674–676).
That file is **not** in the committed `record/` snapshot, so it is a pointer into the engine at that
SHA, not a clickable link.

FIREWALL: this is arithmetic on a toy DEC lattice. Nothing here is a claim about nature.

---

## Verdict table

| # | the claim, as put | verdict | the number that decides it |
|---|---|---|---|
| 1 | **THE SUM** — the octahedron "holds the sum of the neighbours" | **TRUE**, in exactly one sense | the 8 outside faces carry `+5 −4 −12 +6 −2 +7 +10 −10` and sum to **0**, for every `A` whatever |
| 2 | **THE CROSSING** — no tetrahedron shares a face with another, so every transfer between tetrahedra crosses an octahedron | **TRUE at the face level, FALSE at the line level** | 864 tetrahedron faces and 864 octahedron faces on the 6³ torus, a perfect 1:1 pairing — but two tetrahedra do share **lines**, and a transfer takes one step across one |
| 3 | **TRANSFER COUNTS** — a step is "how long it takes to go round the octahedron" | **FALSE** | crossing the octahedron is **2** steps; spike → adjacent spike **2**, → opposite spike **3**; the octahedron's own return is **12** steps and moves when the step size does |
| 4 | **EFFICIENCY** — gathering at the octahedron is cheaper than working tetrahedron by tetrahedron | **SAME-WORK** on the motif, **worse** on the tiling | 37 line-visits either way on the motif; 1404 vs 756 (**13/7×**) on the 6³ torus |
| 5 | **"must complete its calculation before the cube is stable"** | **UNDEFINED under the rule tested** — no such ordering | under the synchronous leapfrog on 0-forms one step reads only the previous step, so nothing completes before anything else; whether the screw introduces an ordering is the review's question |
| 6 | **"8 tetrahedra + 1 octahedron = the stella octangula, hull a cube"** | **TRUE of the motif, FALSE as the tile** | the stella fills **1/2** of its own hull cube (volume 4 of 8); each tetrahedron sits in **4** stellae, so the stellae cover space **2×** over |

---

## 1 · THE SUM — TRUE, and it is beat one-tetrahedron-is-a-whole-world.1 again

Put a freely chosen arrow on each of the record's cut octahedron's **13** lines (6 dots, 13 lines,
12 faces, 4 insides; Euler `6 − 13 + 12 − 4 = 1`, a ball). `F = dA` is then a number on each face —
how much goes round it — and all twelve come out non-zero, so nothing below is true by being empty:

```
arrows        3  1  4  1  5  2  6  5  3  5  8  9  7
face numbers  4  5  7  1  5  4 12  6  2  7 10 10
```

Eight of those twelve faces are the octahedron's outside. Orient the four insides the same way in
space and add their boundaries: the **4 interior faces cancel in pairs**, term by term (asserted, not
argued), leaving each outside face walked exactly once:

```
+5  −4  −12  +6  −2  +7  +10  −10   =   0
```

Exactly zero, for **every** `A` — because each of the four insides walks its own four faces to zero
on its own (`0 0 0 0`), and that is chapter 2's `tetra_inside_sum` token, run four times and added.
No length is used anywhere in it: the only place geometry enters is as the *sign* of an integer 3×3
determinant fixing which way round each inside is walked.

**So the honest reading of "holds the sum" is a conservation, not a store.** The octahedron does not
accumulate what its eight neighbours push at it. What it guarantees is that the eight pushes across
its closed surface **cannot fail to cancel** — `d² = 0` on a closed surface, combinatorially, with
nothing to tune. That is a real and strong statement and it is worth a beat. It is not the statement
that the octahedron holds a value.

## 2 · THE CROSSING — TRUE at the face level, FALSE at the line level

On a 6³ torus (and confirmed unchanged on 12³): **216 tetrahedra, 108 octahedra, ratio 2:1**; 4 faces
each and 8 faces each give **864 tetrahedron faces and 864 octahedron faces, 864 distinct** — a
perfect one-to-one pairing. No two tetrahedra share a face; no two octahedra do either. And the
pairing is tighter than counting: for every octahedron, the eight tetrahedra on its eight faces are
eight *distinct* tetrahedra whose apexes are exactly `c + (±1,±1,±1)` — the eight spikes of a stella
octangula, checked octahedron by octahedron.

Then the level that actually matters, because numbers do not live on faces. 0-forms live on dots and
move along lines, and on the lines the picture is different:

| | count on the 6³ torus | per dot |
|---|---|---|
| lines in all | 756 | 14 |
| lines a tetrahedron provides | 648 | 12 |
| lines only the octahedron's cut provides | 108 (**1/7** of them) | 2 |

Every dot in this world is a corner of 8 tetrahedra **and** a vertex of 6 octahedra; there is no
octahedron-only dot. Two tetrahedra genuinely do share lines, so a disturbance passes from one to
another in **one step**, without waiting for anything. What is true, and is the reformulation worth
keeping: **every line in the world is a line of some octahedron**, and one line in seven — two of
every dot's fourteen — exists *only* because the octahedron had to be cut. No tetrahedron provides
those. Each octahedron edge belongs to exactly 2 octahedra; each cut to exactly 1.

## 3 · TRANSFER COUNTS — the step counts, and the refutation

Poke one spike apex on the stella octangula (14 dots; 36 lines as a solid, **37** as the record cuts
it — the cut is a line too, and it raises its two ends from 8 lines to 9). The leapfrog is a
three-point rule, so support grows by exactly one line per step; *first move* equals *steps along
lines* at every dot, asserted, so nothing below is an accident of cancellation.

| from a spike apex to… | steps |
|---|---|
| its own three octahedron dots | 1 |
| an adjacent spike (6 of them) | 2 |
| the opposite spike | 3 |
| anywhere at all (diameter) | 3 |

No two apexes share a line — the eight apexes are an independent set — so every spike-to-spike path
runs through octahedron dots only: **1** intermediate step for an adjacent spike, **2** for the
opposite one. On the bare octahedron, crossing from a dot to its opposite dot is **2** steps.

**"A step is how long it takes to go round the octahedron" is FALSE, under every reading we could
make precise.** Going round the octahedron's 4-line equator is 4 steps, not 1. Crossing it is 2.
Spike to opposite spike is 3, which is not an integer number of either. And the one reading that
looked promising — that the return matches the line count — dies twice:

| object | lines | returns after | at a different step size |
|---|---|---|---|
| tetrahedron | 6 | **4** | — (4 ≠ 6 already) |
| octahedron | 12 | **12** | `k = 1/4`: never · `k = 1/5`: never |
| stella octangula | 37 | **never** | never, at *any* rational step size |

The tetrahedron kills it on its own: 4 ≠ 6. The octahedron's 12 = 12 looks like a match and is a
property of the step size, not the shape — turn the dial to `1/4` or `1/5` and it stops returning at
all. And the stella never returns, provably: a mode of eigenvalue λ rotates by θ with
`2cos θ = 2 − kλ`, which returns only if θ is a rational part of a turn, and then `2cos θ` is an
algebraic integer. The stella's irrational pair are the roots of `λ² − 11λ + 20`, so `2 − kλ` has
trace `4 − 11k` and norm `4 − 22k + 20k²`; for `k = p/q` in lowest terms the trace forces `q | 11`
and the norm then forces `11 | p`, a contradiction. A poke at a spike excites that pair (checked
exactly, by the minimal polynomial of the poke's own Krylov space), so it never comes home.

### And the step size itself: the stella will not fit on a napkin

The uncut stella's `Δ₀` spectrum, certified exactly (one polynomial identity plus two traces —
trace 72, trace² 528, no eigensolver):

```
0 · 3⁴ · ((11−√41)/2)³ · 7 · ((11+√41)/2)³ · 10²
```

`λ_max = 10`, and the leapfrog needs `kλ < 4`, so **`k < 2/5` exactly** — the chapters' own
`TICK_K = 1/2` is over the line and **unstable on this object**. With the record's cut, `λ_max`
*rises*, to between `1053/100` and `1057/100`, tightening the ceiling to under `400/1057`: the
record's octahedron is the less forgiving object, not the more.

And no step size rescues the table. The first push from a one-dot poke is `(3, −1, −1, −1)`, greatest
common divisor 1, so `kΔ₀φ` lands on whole numbers only if `k` is a whole number — and no whole
number is under `2/5`. Every fraction squares its denominator every tick or two and walks out of
`number()`'s list. Measured, in printable ticks before `number()` refuses:

| `k` | 1/2 | 9/20 | 2/5 | 39/100 | 7/20 | 1/4 | 1/5 | 1/10 |
|---|---|---|---|---|---|---|---|---|
| stable? | no | no | no | yes | yes | yes | yes | yes |
| ticks printable | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

**The bare octahedron, though, goes on the napkin whole** — and at the chapters' own `k = 1/2`
unchanged. `λ_max = 6`, so `kλ = 3 < 4`; `2I − kΔ₀` comes out as half the octahedron's own adjacency,
and the run stays in **whole numbers and halves for ever** — all 21 rows print, denominators 1 and 2
only. Two facts inside that table are worth more than the table: at tick **2** the entire poke is on
the opposite dot and nowhere else, and at tick **3** the entire poke is back where it started (the
pair *(now, before)* only repeats at 12, which is why the period is 12 and not 3).

## 4 · EFFICIENCY — SAME-WORK, and worse on the tiling

Counted in line-visits, the unit that matters: every line's difference must be formed, weighted, and
delivered to both ends, and all an organisation can change is how many times a line is picked up.
One step on the 756 lines of the 6³ world:

| organisation | line-visits | vs the napkin's loop |
|---|---|---|
| per line (what `napkin.laplacian` already does) | **756** | 1× |
| per dot, gathering each dot's 14 | 1512 | 2× |
| per octahedron, 13 lines each | 1404 | **13/7× — worse** |

Gathering at the octahedron is **not** cheaper. On the motif alone it is exactly the same work
differently grouped: the octahedron's 13 lines and the spikes' 3 each partition all 37 lines exactly
once, so `13 + 24 = 37` line-visits, the same as the per-line loop. On the tiling it is strictly
worse, and for a reason that is itself the interesting finding: **each octahedron edge belongs to two
octahedra**, so an octahedron-by-octahedron sweep picks 12 of every octahedron's 13 lines up twice.
It does beat the naive per-dot gather (13/14×), but the napkin was never doing that.

## 5 · "must complete its calculation before the cube is stable" — UNDEFINED under the rule tested

Under the synchronous leapfrog on 0-forms there is no such ordering; whether the screw introduces
one is the review's question. In the rule tested here there is no ordering for this to be a
statement about at all. One step computes every dot's next number from the *previous* step's numbers
alone; nothing inside a step waits for anything else inside that step, and nothing completes first. The nearest true statement is the
transfer count in §3: a disturbance needs 2 steps to reach an adjacent spike and 3 to reach the
opposite one, and every one of those paths spends its intermediate steps on octahedron dots. That is
a distance, not a dependency.

## 6 · The stella octangula — TRUE of the motif, FALSE as the tile

One octahedron plus the eight tetrahedra on its eight faces **is** a stella octangula, exactly: the
eight apexes are the corners of a cube of side 2 centred on the octahedron's odd point, and the
octahedron's six dots are that cube's face centres. So "whose convex hull is a cube" is true.

What is false is that this builds the tiling. The stella has volume **4** and its hull cube **8** — it
fills **half** of its own hull. Each tetrahedron has 4 faces on 4 *different* octahedra, so it
belongs to **4** stellae, and the stellae cover the world **twice over**. What tiles is 2 tetrahedra
to 1 octahedron, not 8 to 1.

One more thing the record does not do, worth saying because the phrase invites it: the *one-cube*
stella octangula — two interpenetrating tetrahedra on all eight corners of a unit cube — **never
occurs in this mesh**. Every unit cube carries exactly one tetrahedron, on its four even corners; the
other four corners are odd-sum hole centres and are not dots at all. The two tetra families alternate
from cube to cube; they never share one. The stella that does occur is the one above, at twice the
scale, centred on a hole.

---

## What these numbers were spent on

*Beat numbers below were brought up to the outline's current ones when the change landed, so they
are correct as they stand; the last section records what the change was.*

Beat two-worlds-threaded.2 already tells her the tetrahedra never meet face to face and that octahedra sit between them;
the computed fact worth adding is the exact 1:1 pairing — 864 tetrahedron faces, 864 octahedron
faces, each face one of each — and then the correction her next question earns: on the *lines*, where
numbers actually live, tetrahedra do touch each other directly, and what the octahedron uniquely
supplies is one line in seven, two of every dot's fourteen, that no tetrahedron provides. A new chapter
between beats make-it-move.5 and the-shape-between.5 can give her the octahedron on its own napkin at the same tick size she already
has: poke one dot, and at tick 2 the whole of it is on the opposite dot, at tick 3 the whole of it is
home, and it does not truly repeat until 12 — her first object where crossing takes longer than one
tick, which is exactly the room beat make-it-move.4 says the tetrahedron does not have. The strongest new idea is
the one for beat one-tetrahedron-is-a-whole-world.1's callback: whatever the eight tetrahedra push across an octahedron's closed
surface sums to **exactly zero**, with no lengths in it — the same coming-home she proved on four
faces, now on eight, and the honest meaning of "the octahedron holds the sum". Three things must not
be said: that a tick is a trip round the octahedron (crossing is 2 steps, going round is 4, and the
returns are the tick size's doing, not the shape's), that the octahedron finishes a calculation before
anything else does (the rule is synchronous and has no order in it), and that gathering at the
octahedron saves work (it is the same 37 line-visits on the motif and 13/7 times as many on the
tiling). And if a beat ever wants the stella's own table, it cannot have one: `k = 1/2` is unstable
there, every stable step size is under `2/5`, and none of them keeps the numbers short enough for
`number()` to print.


### What was written (2026-09-02, issue [#34](https://github.com/zacharyelston/OurBubble/issues/34))

A new chapter, **The shape between** — outline chapter 4, beats **36–46** — reached this object the
way a reader can: not by tiling anything, but by cutting the one tetrahedron she already has at the
middles of its six lines. Four tips and one octahedron, and the octahedron is exactly half of it.
That route is computed in `tools/octahedron.py` §7–§8 (`midpoint_cut`, `octahedron_poke_table`,
`octahedron_boundary_sum`, `second_tetrahedron`, `stella_reader_census`, `napkin_ceilings`,
`stella_runaway`), which assert it is the *same object* as §1–§6's — the graph is checked against
`octahedron_lines()` and the fourteen-dot one against `stella_lines()`, under the name map — so the
reader's route and the record's cannot come apart. Six napkin tokens carry it into the prose:
`octa_cut`, `octa_counts`, `octa_poke_table`, `octa_face_sum`, `stella_counts`, `stella_refusal`.

Two things landed differently from the sketch above. The eight-face sum is stated on the **uncut**
octahedron — twelve arrows, eight faces, every line walked once each way — because that is the form
the reader can check, with the four-insides version kept as the cross-check next to it. And the
stella's refusal became the chapter's climax rather than a footnote: the largest tick each object
will hold (1, 2/3, 2/5) against the book's own 1/2, and the run that goes past a hundred million by
tick 20. The three refuted readings are in the appendix, as this chapter's `note` in `edition.json`,
and appear nowhere in the prose.
