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

## The one rule these pages live under

**A demo may not show a number the napkin did not compute.**

The pages recompute the book's arithmetic rather than displaying numbers Python worked out — that is
the point of them, and it is also the whole risk, because two implementations of the same arithmetic
are two places the book can disagree with itself. So the boundary between them is a checked one:

1. [`tools/napkin_export.py`](../tools/napkin_export.py) dumps every napkin token's **underlying
   data** — the counts, the coboundary matrices, the histories, the volumes, the ceilings — and
   deliberately none of its prose, to [`data/napkin.json`](data/napkin.json). Every rational leaves
   as an exact `"n/d"` string; a float anywhere in the payload is refused by name.
2. It is written on **every build**, by [`preprocessor.py`](../preprocessor.py), for the same reason
   the appendix is: `git status` is then the check.
3. [`core.test.mjs`](core.test.mjs) runs [`core.mjs`](core.mjs) under node and compares the two
   implementations **value by value, as exact strings** — never with a tolerance.
4. It also **scans every table cell of every step of every chapter** for a numeric token the export
   does not contain — where "contain" means an exact value it carries, that value negated (a line
   walked the other way), a length of one of its lists, or an index into one, and nothing else. That
   is the attack the rule exists for: someone typing a number into a page that no arithmetic
   produced.
5. And the swap that a cell scan **cannot** catch is closed from the other side. A small whole number
   traded for another small whole number gets past any such scan, because a page that legitimately
   shows a twelfth tick makes `11` a number the export contains. So the test also reads
   `core.mjs`'s own source and **refuses any string of nothing but digits inside the step
   definitions**: a count has to arrive as `String(cut.dots)`, never as `"10"`. Exactly three
   numbers on these pages are not values of the object — how many rules the law has, how many
   exceptions and assumptions there are, and the two coming-home facts — and those are named
   constants (`ONLY`, `NONE`, `PAIR`) whose values the test checks against its own list. A fourth
   means writing down what it counts, in both places.

   Three mutations, run against this pair: eleven dots where the napkin says ten (caught by the
   lint), fifteen dots where it says fourteen (caught by the lint), a third of the whole where it
   says a half (caught by the scan).
6. `check_edition.py` runs both through `status()`, so the verdict comes from the error count and a
   failing check cannot narrate a clean one. **If node is absent the line reads
   `unverified — node absent`.** It never passes silently; CI has node.
7. The `--rendered` pass then checks the built site actually carries the pages and that every link in
   them resolves, because the wiring that publishes `demos/` is a thing nothing else would notice
   breaking.

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

Numbers are written **on the pieces they belong to**: directly under a piece's own name, at that
name's canonical position, so CANON.md's three placement rules are untouched. `D` appears three
times and carries the same number three times, because it is one dot.

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
