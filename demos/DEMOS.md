# The demos — the napkin world, in the reader's browser

Four static pages, one per chapter of the book's first world: the one small enough that every number
in it is finger-countable. Each page walks its chapter's beats in order and **works the answers out
as you read**, in exact arithmetic.

> **Scope.** These pages compute a **toy**. Nothing they draw or print is a claim about nature.
> [`FIREWALL.md`](../FIREWALL.md) is the long version.

| page | chapter | beats |
|---|---|---|
| [`two-dots-and-a-line.html`](two-dots-and-a-line.html) | Two dots, a line, and the first thing that closes | 9–18 |
| [`one-tetrahedron-is-a-whole-world.html`](one-tetrahedron-is-a-whole-world.html) | One tetrahedron is a whole world | 19–26 |
| [`make-it-move.html`](make-it-move.html) | Make it move | 27–35 |
| [`the-shape-between.html`](the-shape-between.html) | The shape between | 36–46 |

## 2026-09-02 — the engine is vendored, and this JavaScript is on notice

The owner's decision that day: **one engine for the book and its demos** — UniForge's `napkin`
crate, registered as `lab/napkin/0001`. It is now vendored in this repository at
[`engine/`](../engine/PROVENANCE.md) and pinned by [`engine.lock`](../engine.lock) exactly the way
`record/` is pinned: the canonical payload, and the crate compiled to WebAssembly with its
`wasm-bindgen` glue, hashed file by file, committed, and served from the built site at
`book/engine/`. The book's thirteen tokens already render from it.

**`core.mjs`'s arithmetic is to be replaced by calls into `engine/napkin.js`.** That is step
three-B, on the `demos/do-not-narrate` branch, and it is not done here — nothing under `demos/` was
rewritten in the vendoring step. What changed underneath these pages is only where their oracle
comes from: `data/napkin.json` is now a copy of `engine/napkin.json` rather than a fresh run of the
Python, so the value-by-value cross-check below already measures this JavaScript against the engine
itself. When the rewrite lands, the second implementation these pages currently carry stops
existing, and the guarantee below gets shorter by one clause.

The module exposes six entry points, strings in and strings out, so no rational type and no float
crosses the boundary: `census_json`, `slosh_json`, `loops_json`, `cut_json`, `certificate_json`,
`number_json`. GitHub Pages serves `.wasm` as `application/wasm`, and the glue falls back to
`arrayBuffer()` if it ever does not.

## What these pages guarantee, and what they do not

**Every number a demo shows is one it computed, it equals the napkin's to the last digit, and no
number is typed into a demo by hand.**

The pages recompute the book's arithmetic rather than displaying numbers Python worked out — that is
the point of them, and it is also the whole risk, because two implementations of the same arithmetic
are two places the book can disagree with itself. So the boundary between them is a checked one:

1. The engine emits every napkin token's **underlying data** — the counts, the coboundary matrices,
   the histories, the volumes, the ceilings — and deliberately none of its prose, as
   [`engine/napkin.json`](../engine/napkin.json). Every rational leaves as an exact `"n/d"` string; a
   float anywhere in the payload is refused by name.
   [`tools/napkin_export.py`](../tools/napkin_export.py) is the Python that used to produce that
   file and now only has to reproduce it, byte for byte, in `tools/engine_check.py`.
2. [`data/napkin.json`](data/napkin.json) is a copy of it, written on **every build** by
   [`preprocessor.py`](../preprocessor.py), for the same reason the appendix is: `git status` is
   then the check.
3. [`core.test.mjs`](core.test.mjs) runs [`core.mjs`](core.mjs) under node and compares the two
   implementations **value by value, as exact strings** — never with a tolerance. This is the check
   that carries the weight.
4. It then scans **every surface a reader meets** for a numeric token the export does not contain:
   every table cell, heading and caption, every step's title, prose and notes, and every piece of
   text inside every drawing — including the SVG `<desc>`, which is all a screen-reader user gets
   from a picture — at every tick of every step. "Contain" means an exact value the export carries,
   that value negated (a line walked the other way), a length of one of its lists, or an index into
   one, and nothing else.
5. And it reads `core.mjs`'s own source and **refuses any digit inside any string literal in the step
   definitions** — double-quoted, single-quoted, or a template's text, with `${…}` cut out because
   that is code. A count arrives as `String(cut.dots)` or it does not arrive. Exactly three numbers
   on these pages are not values of the object at all (how many rules the law has, how many
   exceptions and assumptions there are, and the two coming-home facts); those are named constants
   declared above the step region, and the test holds the same three.

### What no check here can catch

**A number computed correctly and then put in the wrong place.** `cut.octDots` printed in the "lines"
column reads as *six lines, twelve dots*, and every value in it is one the napkin computed — so no
scan over the numbers can see it. Nor can one see `cut.dots + 1`, because eleven is a number the
export contains as an index. Only reading the page catches those, which is what the proof-reader pass
is for, and it is why this section is written down rather than left implied.

The first version of this file claimed more than it checked. A fresh reviewer walked twelve wrong
numbers past it — through a caption, a title, a body, a note, a drawing, an SVG description, a
backtick and a single quote — with every check green. Seven of those classes are closed above; the
three that remain are the paragraph you have just read.

Run it by hand:

```sh
python3 tools/napkin_export.py     # re-derive the oracle
node demos/core.test.mjs           # the cross-check on its own
make check                         # tier 0, which runs both
```

## Exact, or refused

Every displayed number is a rational over `BigInt`. There is no floating point in any value a reader
is asked to check, and `numberText` refuses anything it cannot write down exactly and briefly — the
same rule, and the same list of denominators, as `napkin.number()`.

The refusal is not a formatting fallback. It is chapter 4's finding: on the two tetrahedra threaded
together, at the tick that has worked all along, the arithmetic leaves the napkin, and the page says
so rather than rounding. Floats appear in one place only — SVG coordinates — and never in a number.

## The drawings: two conventions, and no third

### The tetrahedron — CANON.md's flat unfolded net

Every drawing of the whole tetrahedron is the net [`CANON.md`](../CANON.md) governs: the triangle
`ABC` in the middle with the other three folded out from its sides, the same six positions, the same
names `A B C D`, all four panels the same fill, every label upright, and the diagram never rotated or
mirrored. The coordinates are `tools/canon.py`'s own, in its exact `(x, u·√3)` ring, and
`core.test.mjs` checks that all nineteen labels land where `canon.py` puts them, to the precision a
drawing has.

Numbers are written **on the pieces they belong to**, and the *name never moves*: it stays at its
canonical position and the number takes a fixed step from it — into the panel for a dot, straight
down for a line or a face. That rule is worth stating because the two obvious alternatives both
failed. Moving the name and the number inward together piles a panel's four labels onto its middle;
stepping a line's number sideways pushes it onto the next line's name across the fold. `D` appears
three times and carries the same number three times, because it is one dot.

Chapter 1 draws its dots as dots, and the net does not. That is not an inconsistency to be tidied
away: in the net a corner is where lines meet, and there is always a line. In beat 9 there is not —
the beat is *where could you put a number*, and its answer needs something to point at.

Chapter 1's triangle is the net's central panel, framed to itself — same anchor, same orientation,
`AB` horizontal with `A` on the left. Nothing is learned twice: when the fourth dot arrives, the
triangle is already where the net puts `ABC`.

### The octahedron and the stella — the ring

`CANON.md` governs the tetrahedron and nothing else, so these two need a convention, and this is the
proposal. **Six dots on two concentric circles**: the middles of the three lines that leave `A` on
the outside, and the three no line joins them to on the inside, each placed on the same ray out of
the centre as its partner and on the other side of it.

So *opposite* is literally straight through the middle, which is what beats 38 and 39 need a reader
to see — three pairs joined by nothing at all, and a poke that crosses to the far dot. The three
joins that are **not** there are marked by a faint line through the centre, and that is the only mark
in either drawing standing for an absence.

All twelve lines are drawn once and none of them crosses another. That is checked before a stroke is
emitted, by `ringPlanarity()`, and it is checked because it was once false: at exactly half the outer
radius each inner dot lands *on* the outer triangle's edge, and the twelve lines then draw as six.

Two honest costs, both stated on the page:

- **One face is the outside of the paper.** Flat paper always makes one face the outside, so when the
  eight faces are walked one at a time, that one is shown by thickening its three lines instead of
  filling a region, and the drawing says which it is.
- **Four of the eight tips cannot sit inside their own face.** Three of the ring's faces are thin
  slivers and the eighth has no inside at all, so those four tips sit outside the ring, each on the
  ray through its own face — except the outside face, whose three dots average to the centre exactly
  and so names no ray; that one is placed straight above, and it is the single arbitrary choice in
  the convention. Their lines in are the only lines in either drawing that cross anything: seven
  crossings, all among the tips' own lines, none among the twelve. The count is pinned in the test,
  so a change to the layout has to be looked at rather than shipped.

### A net was considered for the octahedron, and refused

The obvious alternative was the octahedron's own unfolded net, which would have matched the
tetrahedron's convention exactly. It was refused for one reason: a net puts a dot in more than one
place, and the whole of beat 39 is *the poke crossed to the opposite dot and is nowhere else*. On a
net, "the opposite dot" is two or three marks on the paper, and the reader has to reassemble the
solid in her head before she can see the thing the beat is about. The ring shows it in one glance.

### 3-D

Not used. Nothing in beats 9–46 needed it. If a later beat genuinely cannot be shown flat, the
standard to reach for is the simplest possible orthographic wireframe — no shading, no perspective
camera, no library — and a note saying why 2-D would not do.

### No colour means anything

One panel fill, one stroke, and one heavier stroke marking *the piece this step is about* — never a
kind of piece. That is `CANON.md`'s rule 5 kept honestly: there is no colour spare to encode with.
Light and dark are the same drawing with ink and paper exchanged.

## The stills, and how the studies get replaced

Every step has a **still** button that renders exactly what is on screen to a standalone SVG: its own
stylesheet inlined, its own `<title>` and `<desc>`, and a comment naming the chapter and the beat it
came from. Those stills are the intended replacement for the placeholder studies in
`chapters/assets/`, which the owner has called amateurish and AI slop.

**This is not that PR.** Replacing a study touches `chapters/` and `ART_DIRECTION.md`, and it is a
judgement about the book's art rather than about its arithmetic, so it is the owner's to make. When
it happens, the shape of it is:

1. pick the beats whose stills earn a place in the prose — not one per chapter by quota;
2. commit each still under `chapters/assets/`, generated by a small script that drives `core.mjs`
   under node so the committed SVG is derived and not hand-touched (the same discipline
   `tools/canon.py` already holds for the net);
3. replace one asset at a time under `ART_DIRECTION.md`'s replacement rule, updating its `alt` text
   and its caption in the same commit;
4. and drop the `Analogy — not data.` opener for these, because a still **is** the data — which is
   an `ART_DIRECTION.md` change, and the reason that document is not touched here.

## Accessibility and honesty

- **Keyboard-steppable.** `←` / `→` (or `k` / `j`) walk the beats; the tick controls are buttons.
- **Every number is text.** Whatever a drawing shows, the same values are in a table underneath, so
  a page reads correctly with the pictures ignored entirely.
- **Light and dark**, following the reader's system, with an override remembered per browser.
- **No easing.** The rule has no in-between, so the motion cuts from one tick to the next. A drawing
  that slid between two ticks would be inventing something the rule does not do.
- **Nothing loaded from anywhere.** No framework, no CDN, no font, no image, no analytics. One
  module, one stylesheet, one JSON file.
- **A deep link is a beat**: `#beat-31` opens that step.

## How it reaches the published site

`demos/` sits outside `chapters/`, so mdBook carries it through the `chapters/demos` symlink — the
same mechanism that already publishes `record/`. The pages land at
`https://zacharyelston.github.io/OurBubble/demos/`, and `check_edition.py --rendered` confirms they
are there and that every link in them resolves before anything is deployed.

## Reading them locally

```sh
mdbook build
python3 -m http.server --directory book 8000
# then open http://localhost:8000/demos/
```

Serving the whole built book is the right way round, because each demo links back to its chapter with
`../<chapter>.html`. Serving the repository root instead works for the demos themselves, but those
back-links will 404 — there is no book there to go back to.

The pages are ES modules, so `file://` will not do; they need a server, any server.
