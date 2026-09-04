# TOKENS — what the book can show, and what it currently shows

> **FIREWALL.** Every number named here is arithmetic on a **toy** DEC lattice. *Dot, line, face,
> inside, tick, slosh, poke, crossing, stella, world* name features of that lattice, never claims
> about nature. [`FIREWALL.md`](FIREWALL.md) is the long version.

There is one engine: UniForge's `napkin` crate, vendored under [`engine/`](engine/PROVENANCE.md) and
pinned by [`engine.lock`](engine.lock). It computes **23 registered rows** (`lab/napkin/0001`) and,
since the 2026-09-04 bump, **five more** the demos asked for (`lab/napkin/0003` — see the section
below; no chapter renders those yet).
**Twenty-one of them are vendored as data**, and the two that are not — R22 and R23 — are not data
at all: they are properties of the engine (it refuses a non-complex; its output is canonical JSON,
byte for byte), and they are checked rather than shown. The chapters currently render **sixteen**.

This file is the difference between those two numbers. It exists so that the answer to "can a
chapter show *that*?" is a lookup rather than a piece of engine work: if a row is listed here, the
data is already in the repository and adding a token is writing a renderer for it.

Nothing here proposes a new token. Deciding what a chapter shows is the Structure lane's, and it
happens against `OUTLINE.md`'s beats.

## The sixteen the chapters render today

Each is a `{{napkin:NAME}}` in a chapter's prose; `preprocessor.py` replaces it at build time with
what `tools/napkin.py` renders from `engine/`. Every rendered block carries the italic line
*computed while this page was built — …* and says what was computed.

| token | chapter | register rows | what it puts on the page |
|---|---|---|---|
| `tetra_counts` | One tetrahedron is a whole world | R01 R02 | the census `4 · 6 · 4 · 1` |
| `triangle_loop_example` | Two dots, a line, and the first thing that closes | R03 | three differences from the corners 2, 5, 1, and their sum |
| `tetra_face_loops` | One tetrahedron is a whole world | R04 | six differences, and each of four faces walked round to zero |
| `tetra_inside_sum` | One tetrahedron is a whole world | R05 | four non-zero faces from six freely chosen arrows, adding to zero |
| `triangle_slosh_table` | Make it move | R07 | the triangle at `2/3`, from 2, 5, 2 — eleven whole-numbered rows |
| `tick_belongs_to_shape` | Make it move | R07 R16 | the same three numbers at `1/2`: three printable rows, no return, and the four-dot ceiling |
| `slosh_table` | Make it move | R08 | ten ticks from rest, every line counting one |
| `slosh_table_dialed` | Make it move | R09 | the same ten with `AB` counted double — the dial |
| `no_room` | Make it move | R10 | the four dots' hops: one line from each to each, so the diameter is 1 |
| `vertex_classes` | Room, and a world with no edge | R19 | three kinds of place on a `6³` wrapped world, and the control |
| `octa_cut` | The shape between | R11 | the midpoint cut: four tips at an eighth, one shape at a half |
| `octa_counts` | The shape between | R12 | `6 · 12 · 8`, and the three pairs no line joins |
| `octa_poke_table` | The shape between | R13 | the crossing: a poke of 1 on `AB`, whole on `CD` at tick 2 |
| `octa_face_sum` | The shape between | R14 | eight faces of a closed surface, walked from outside, summing to zero |
| `stella_counts` | Two worlds threaded | R15 | the second tetrahedron threaded: 14 dots, 36 lines |
| `stella_refusal` | Two worlds threaded | R16 R17 R18 R20 | three tick ceilings, and the runaway past the third |

## All 23 rows, and where their data lives

`tools/engine.py` is the only door to this data. `engine.available()` returns the whole payload;
the named accessors beside it return the same values as `Fraction`s and tuples.

| row | what it computes | vendored under | reached by |
|---|---|---|---|
| R01 | the ascending census on 1, 2, 3 and 4 dots | `napkin.json` → `complexes.{1,2,3,4}.cells` | `engine.complex_on(n)` |
| R02 | the coboundaries `d₀ d₁ d₂`, and `d∘d = 0` in integers | `complexes.{n}.coboundary` | `engine.complex_on(n)` |
| R03 | the triangle's three differences and their loop sum | `triangle.chapter` (and a second set under `triangle.another`) | `engine.triangle()` |
| R04 | the tetrahedron's six differences and four face loops | `tetrahedron.differences`, `.face_loops` | `engine.tetrahedron()` |
| R05 | the inside sum from six freely chosen arrows | `tetrahedron.arrows`, `.face_numbers`, `.outward_face_numbers`, `.inside_sum` | `engine.tetrahedron()` |
| R06 | `Δ₀` over `Q`, and one tick of the leapfrog | in `motion` — every history row is that rule applied once | `engine.motion()` |
| R07 | the rule on the **triangle**, at a tick that is not dyadic | `rows.json` → `triangle_motion.at_two_thirds` (and `.at_the_book_tick`) | `engine.triangle_motion()` |
| R08 | ten ticks from rest on the tetrahedron | `motion.plain` | `engine.motion()` |
| R09 | the dial: line `AB` counted double | `motion.dialed`, `.dialed_line`, `.dialed_weight` | `engine.motion()` |
| R10 | the tetrahedron has no room — no ring, no direction | `rows.json` → `no_room.hops`, `.diameter` | `engine.no_room()` |
| R11 | the midpoint cut: ten dots, four tips at `1/8`, one shape at `1/2` | `cut.dots`, `.tips`, `.tip_share`, `.core_share` | `engine.cut()` |
| R12 | the shape between, counted: `6 · 12 · 8`, degree 4, three unjoined pairs | `cut.oct_*`, `.opposite_pairs` | `engine.cut()` |
| R13 | the crossing: poke `AB` at `k = 1/2` | `poke` | `engine.poke()` |
| R14 | eight faces of a closed surface adding to zero | `face_sum` | `engine.face_sum()` |
| R15 | the second tetrahedron, threaded: 14 dots, 36 lines, the volumes | `stella` | `engine.stella()` |
| R16 | three tick ceilings, certified by integer eigenvectors | `refusal.ceilings` | `engine.refusal()` |
| R17 | the runaway, and how few rows of it can be written down | `refusal.runaway.look`, `.floors`, `.printable_rows` | `engine.refusal()` |
| R18 | and no smaller tick rescues it | `refusal.runaway.stable_tried` | `engine.refusal()` |
| R19 | kinds of place on a wrapped world, and the control | `rows.json` → `world` | `engine.kinds_of_place()` |
| R20 | **negative** — a number that is not finger-countable is refused | `refusal.denominators_number_prints` | `engine.refusal()`; the refusal itself is `napkin.number()` |
| R21 | **negative** — a tick violating the stability bound is refused | `refusal.ceilings[*].holds` | `engine.refusal()` |
| R22 | **negative** — a non-complex is refused at construction | not data: a property of the crate, asserted in its own tests | — |
| R23 | the cross-check: canonical JSON, byte for byte | not data: it is the *form* of `napkin.json` and `rows.json` | `tools/engine_check.py` |

`engine/napkin.json` carries eighteen of the twenty-one; `engine/rows.json` carries the other three
(R07, R10, R19), because the payload's shape is pinned byte for byte to the Python oracle's output
and nothing may be added to it.

## The five the demos asked for — `lab/napkin/0003`

Writing the demos (PR #60) found five places the engine's browser surface could not be asked a
question the page wanted, and each demo did the honest thing: it narrowed the interaction to what the
engine *had* computed and wrote the gap down. UniForge #362 closed all five, and this engine bump
brings them in. **No token renders any of them yet** — that is the next pass, and it is a Structure
decision against `OUTLINE.md`'s beats, not an engine one.

The demos will reach these through the WebAssembly module, where they are *questions* rather than one
fixed answer: `slosh_weighted_json`, `face_sum_json` and `walk_json` are new entry points, and
`loops_json` and `certificate_json` now answer where they used to have nothing to say. They are
vendored as data as well, under `rows.json` → `gaps`, so that `tools/engine_check.py` recomputes all
five in Python and demands the same bytes.

| row | what it computes | vendored under | asked in the browser by |
|---|---|---|---|
| G01 | **the dial** — a run of the one rule with a weight per line (`AB` counted double) | `rows.json` → `gaps.dial` | `slosh_weighted_json(object, initial, weights, k, ticks)` |
| G02 | **the outward eight-face sum**, per face, with the cycles the walk used and the sum building face by face | `gaps.outward_face_sum` | `face_sum_json(object, arrows)` |
| G03 | **two dots and a line** — no closed walk exists, at either degree, as a count rather than an error | `gaps.two_dots` | `loops_json("two-dots", values, degree)`, and every answer's new `closed_walks` |
| G04 | **the triangle's tick ceiling** — `λ = 3`, integer eigenvector `(−1, 1, 0)`, bound `4/3` | `gaps.triangle_certificate` | `certificate_json("triangle", k)` |
| G05 | **a walk's running partial sums** — the sum building line by line, in the order a reader takes it | `gaps.walks` | `walk_json(object, degree, index, values)` |

Two properties of the whole surface came with them and are not data:

* **no entry point panics.** An unknown object, a value that is not an exact rational, a walk index
  that does not exist — each comes back as `{"object": …, "refused": …}`. On
  `wasm32-unknown-unknown` a panic is an unrecoverable trap: the page would not get an error, it
  would lose the engine.
* **the existing answers' bytes did not move.** `napkin.json` is byte-identical across this bump
  (`sha256 = a770f4c4…`, unchanged), and across every browser entry point the only difference is one
  *added* key, `closed_walks`. UniForge's `lab/napkin/0003-engine-gaps/data/byte-compatibility.txt`
  is the measured diff.

Beside the rows, the payload also carries `net` — `CANON.md`'s flat unfolded net, four panels, nine
segments and nineteen labels — which is what the demos draw so that a picture in a demo is the
picture the canon governs rather than a second drawing of the same object.

## Three things not in the payload, on purpose

* **No prose.** No caption, table heading or worded fraction crosses the boundary. Those are
  `tools/napkin.py`'s rendering and the chapters' own writing; a demo that copied a caption would be
  quoting the book rather than computing it.
* **No float, anywhere.** Every rational leaves the engine as an exact `"n/d"` string and is parsed
  back into a `Fraction`. The engine's own type has no float variant, so this is a property of the
  payload rather than a check that runs afterwards.
* **No `√41`.** The threaded pair's spectrum contains `(11 ± √41)/2`, and neither is ever computed,
  in floating point or otherwise. Neither is the stiffest mode either: that is **10**, which is why
  the ceiling comes out as an exact `2/5`. What is vendored is an *integer eigenvector* for `λ = 10`
  certifying the bound — which is why the refusal in *Two worlds threaded* is checkable on a
  napkin.

## Adding a token

1. Find the row here and read its data through `tools/engine.py` — add an accessor if the group has
   no named one yet, but **compute nothing**: if a value must be worked out, it is missing from the
   engine and belongs in a UniForge register row.
2. Write the renderer in `tools/napkin.py`, add it to `TOKENS`, and give it the assertions its own
   chapter's sentences lean on.
3. Add the phrasings its numbers *disprove* to `REFUSED_IN_PROSE`, so a later edit two paragraphs
   away cannot contradict it.
4. Write `{{napkin:NAME}}` into the chapter, and add the row to the table at the top of this file.

`make check` then holds all of it: the token renders identically twice, its caption is under the
ceiling, no chapter carrying it says anything its arithmetic refuses, and the data it read hashes to
what `engine.lock` pins.
