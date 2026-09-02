# CANON — the one labeling of the tetrahedron

The tetrahedron is the book's first real object, and a reader meets it more than once. If it is
drawn one way in one chapter and another way in the next — corners renamed, faces reordered, the
picture rotated because it composed better — then every time she turns a page she has to learn the
object again. So there is exactly one labeling and exactly one layout, and this file is it.

**One rule, and everything below is a consequence of it: a label is an identity, not a decoration.**
`AB` is the *name* of a line. It is not a caption that may move to whichever line the drawing looks
best on. Names are never permuted, rotated, or reassigned for aesthetics.

This standard is **derived from [`tools/napkin.py`](tools/napkin.py)**, which already holds this
object because chapters 1–3 count on it in front of the reader. The names, and the order they come
in, are the napkin's. That is not tidiness: it means a name in a drawing and a row in a napkin table
cannot come apart, because there is one place either could come from.
[`tools/canon.py`](tools/canon.py) is this file as data and as the drawing, and `make check` refuses
a build in which the two have drifted.

> **Scope.** This is a standard for drawing a shape in a book about a toy. Nothing in a picture drawn
> to this standard is a claim about nature, and nothing in the picture *means* anything beyond the
> shape: no face stands for a force, a dimension, a domain or a direction of time, and no colour
> encodes a property. [`FIREWALL.md`](FIREWALL.md) is the long version.

## The names

Four dots, named **A, B, C, D** — `napkin.NAMES`. These are already the book's names for them, and
no drawing introduces others. In particular the reader never meets `V0…V3` or `F0…F3`: a letter is
something she can hold in her head, an index is something she has to translate.

Everything larger is named by the dots it is made of, **in ascending order**, which is why every
name is written down only once:

| what | how many | in order |
|---|---|---|
| dots | 4 | A · B · C · D |
| lines | 6 | AB · AC · AD · BC · BD · CD |
| faces | 4 | ABC · ABD · ACD · BCD |

Those are the six ascending pairs and the four ascending triples, in exactly the order
`napkin.simplices()` produces them. **Label order and data order are the same order.** A drawing's
third line is the napkin's third line, so a number in a table and a name on the paper always refer
to the same piece.

Ascending order is also the orientation, and that is the napkin's convention rather than a new one —
it is what makes the alternating signs in the loop sums the only convention in play.

## The canonical layout: the flat unfolded net

Every drawing of the whole tetrahedron in this book is the **flat unfolded net**: the triangle
**ABC** in the middle, with the other three triangles folded out from its three sides. Not a 3-D
perspective view.

The reason is the reader, not the geometry. In a perspective drawing one corner sits inside the
outline and one face is hidden behind the others, so a novice has to work out what she is looking
at before she can look at it. Flat, all four faces are the same size and all of them are visible.

```
             D ──────── C ──────── D
              \        / \        /
               \  ACD /   \ BCD  /
                \    /     \    /
                 \  /  ABC  \  /
                  A ─────────  B
                   \         /
                    \  ABD  /
                     \     /
                      \   /
                        D
```

### The positions

Six positions, side length **3**. `A` at the origin, `B` to its right, `C` above and between them;
the three copies of `D` are each **the mirror image, in the shared line, of the central triangle's
remaining corner**. Stating the layout as a reflection is what makes the four triangles congruent by
construction rather than by proofreading, and it is how `canon.py` computes them:

| position | exact | as a decimal |
|---|---|---|
| A | (0, 0) | (0, 0) |
| B | (3, 0) | (3, 0) |
| C | (3⁄2, 3⁄2·√3) | (1.5, 2.598) |
| D, across AB | (3⁄2, −3⁄2·√3) | (1.5, −2.598) |
| D, across AC | (−3⁄2, 3⁄2·√3) | (−1.5, 2.598) |
| D, across BC | (9⁄2, 3⁄2·√3) | (4.5, 2.598) |

These are PaperTetra's canonical coordinates, restated with the napkin's names. `canon.py` derives
them and asserts they are still these six; `canon.py` also asserts all **twelve** triangle sides are
exactly 3, in exact arithmetic, so "equilateral" is a checked property and not an intention.

### One dot in three places

`D` appears three times. A reader should not have to infer that those are one dot, so the drawing
says so plainly: all three carry the same name, and the SVG's own description says the flat paper
puts one corner of the solid in three places.

The same thing happens to the lines. The net draws **nine** segments for six lines: AB, AC and BC
once each, where two panels meet, and AD, BD and CD twice each, once on each panel that folded out.
A line drawn twice carries its name twice — the same name, because it is the same line. Seeing `CD`
on two edges of the paper is how a reader sees where the fold is.

### Orientation

**Fixed.** `AB` is horizontal, `A` on the left, `B` on the right, `C` above them, and the three
copies of `D` below AB, beyond AC, and beyond BC. The diagram is never rotated and never mirrored,
not even by a quarter turn, and not as a whole.

A rotated copy of a diagram is the same diagram to someone who already knows it and a new diagram to
someone who does not. The reader this book is written for is the second person.

## Where the labels go

Three rules, and no exceptions:

1. **A dot's name sits inside a triangle**, in from its corner by a quarter of the way to that
   triangle's centre — never outside the paper, where it would float free of the shape. Which
   triangle is fixed, not a matter of taste: the central one, where the corner belongs to it, and
   otherwise the one panel that owns that corner. So `A`, `B` and `C` are read inside the central
   triangle, and each `D` inside the triangle it folded out onto.
2. **A line's name sits at that segment's midpoint**, moved a quarter of the way toward the centre
   of the panel it bounds, so it is unambiguously on one line and inside one triangle.
3. **A face's name sits at that triangle's centre.**

**Every label is upright.** None is rotated to follow the edge it belongs to or the panel it sits in.
PaperTetra rotated its side panels' labels by ±60° and then had to write a rule forbidding the
rotation that made the bottom one unreadable; the simpler standard is that no label is ever rotated,
and then there is no case to get wrong.

## What is fixed, and what a drawing may not do

Fixed, and checked:

- the names, and their order — derived from the napkin;
- the net, its six positions, and the orientation;
- the three placement rules;
- that every piece is labelled, that every label names a real piece, and that each is labelled once
  per copy the net makes of it — nineteen labels, no more and no fewer;
- that all four panels are drawn identically.

A drawing to this standard must not:

1. rename a dot, or use an index in place of a letter;
2. reorder the lines or the faces;
3. rotate or mirror the diagram, or move to a perspective view;
4. move a label to wherever it fits best;
5. colour one panel differently from another, or give a face, a line or a colour a meaning;
6. be drawn by hand, or by any code other than `tools/canon.py`.

Point 5 is a firewall rule, not a style rule. PaperTetra assigned each face a colour that encoded a
physical meaning; a picture in this book has no meaning to encode, so all four panels take the same
fill and every line the same stroke. `canon.py` asserts there is exactly one panel colour in the
emitted drawing — the way to keep "colour carries nothing" true is to leave no colour to carry it.

## How a tetrahedron gets drawn

```sh
python3 tools/canon.py            # run the self-test; print what it verified
python3 tools/canon.py --svg      # the canonical net, to stdout
python3 tools/canon.py --out X    # the canonical net, to a file
```

`tools/canon.py` is the **only** way a tetrahedron net enters this book. It has no dependencies
beyond the standard library and the napkin, so it runs wherever the book builds.

Its self-test runs inside `python3 check_edition.py`, which is step 2 of `make check` and of CI, and
it prints one line saying exactly what it verified — the discipline `check_edition.py` describes at
`status()`: the check does not hold the pen on its own verdict, so a failing check cannot report a
clean one.

A chapter asset that shows the tetrahedron is composed *around* this drawing, under
[`ART_DIRECTION.md`](ART_DIRECTION.md)'s contract — its caption, its alt text and its `Analogy — not
data.` opener are that document's business. This one governs the object inside the frame. The net's
aspect ratio is fixed by the geometry (it is taller than it is wide relative to a 2:1 study), so an
illustration hosts the net rather than stretching to it.

## What came from PaperTetra, and what did not

The discipline in this file is PaperTetra's — `/Users/zacelston/code/PaperTetra`, commit `93a9f67`,
`CANONICAL_STANDARD.md` and `CANONICAL_INVARIANTS.md`. It had already learned, on its own diagrams,
that a canonical label is an identity and that "just rotate it for the figure" is how a standard
dies. [`LEGACY_MIGRATION.md`](LEGACY_MIGRATION.md) records the import.

Taken: labels as identities, never permuted or relabeled for looks; the flat unfolded net as the one
layout; its coordinate scheme; fixed label placement; a written list of forbidden practices; one
authoritative source that code and diagrams derive from; and determinism as a requirement rather
than a hope.

**Refused, because the book's firewall forbids it:** every interpretation. PaperTetra's faces mean
Time/Flow, Expansion, Reflection and Rotation; its edges are named interactions and mapped to
forces; its colours encode those meanings; its five domain models (Holography, General Relativity,
String Theory, the Standard Model, Quantum Mechanics) and its 3+1 spacetime and right-hand-rule
documents interpret the same four faces. None of it comes in, under any wording. Those are exactly
the analogy claims [`FIREWALL.md`](FIREWALL.md) rules out, and the closest of them —
faces-as-forces — this project has already refused once, in `LEGACY_MIGRATION.md`. The canon carries
geometry and names.

Dropped for other reasons, and worth saying why:

- **`F0…F3` and `E0…E5` as names.** They are indices into an interpretation the book does not have.
  A face here is named by its three dots, which is a name a reader can check against the picture.
- **Whole-diagram rotation and reflection** (PaperTetra's INV-5 permits both). The orientation is
  fixed here instead. PaperTetra's permission is sound for a reader who knows the object; this book
  is written for one who does not.
- **±60° label rotation.** Replaced by "every label is upright", which needs no exception for the
  bottom panel.
- **The colour scheme.** Refused as meaning, and not readopted as style: one fill, four panels.
- **The interaction table and face-edge pairings as a data model.** The pairing of a line to the two
  faces that meet along it is already in the napkin's incidence, computed rather than tabulated.
- **The Rust, SQLite, TikZ and LaTeX stack.** This book builds with Python at mdBook build time.
- **PaperTetra's own edge numbering.** Two of its normative documents disagree about it —
  `CANONICAL_STANDARD.md` says `E0 = F1 × F2` while `CANONICAL_INVARIANTS.md` says
  `E0 = F0 × F1` — which is the best argument in the whole source for the thing this file does
  instead: derive the order from the code that holds the object, and check the derivation on every
  build.
