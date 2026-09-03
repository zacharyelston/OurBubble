# The demos — the napkin world, run in the reader's browser

Five static pages, one per chapter of the book's first world: the one small enough that every number
in it is finger-countable. Each page walks its chapter's beats in order, and at every one of them
the reader **does something** and watches the object answer.

> **Scope.** These pages run a **toy**. Nothing they draw or print is a claim about nature.
> [`FIREWALL.md`](../FIREWALL.md) is the long version.

| page | chapter | beats | steps |
|---|---|---|---|
| [`two-dots-and-a-line.html`](two-dots-and-a-line.html) | Two dots, a line, and the first thing that closes | 9–18 | 9 |
| [`one-tetrahedron-is-a-whole-world.html`](one-tetrahedron-is-a-whole-world.html) | One tetrahedron is a whole world | 19–26 | 6 |
| [`make-it-move.html`](make-it-move.html) | Make it move | 27–38 | 9 |
| [`the-shape-between.html`](the-shape-between.html) | The shape between | 39–43 | 5 |
| [`two-worlds-threaded.html`](two-worlds-threaded.html) | Two worlds threaded | 44–49 | 5 |

**Those beat numbers are not written anywhere in `demos/`,** and neither is that table's arithmetic —
see *Nothing here knows a beat number* below.

## 2026-09-02 — the owner's two verdicts, and what they changed

The first version of these pages went live and the owner read them. Two sentences came back, and
this pass is both of them (issues [#46](https://github.com/zacharyelston/OurBubble/issues/46),
[#44](https://github.com/zacharyelston/OurBubble/issues/44),
[#59](https://github.com/zacharyelston/OurBubble/issues/59)).

### "It feels forced. Like just repeating slop recitation of text without understanding it."

He was right, and the diagnosis was specific: every step carried a paraphrased paragraph of its own
chapter. A reader met the same sentence twice — once written well in the book, once written worse on
the page beside it — and did nothing in between.

**The words belong to the book. The demo is the sim.** Every step is now exactly three things:

* its **title** is the outline's own question, verbatim;
* its **one line** tells her what to *do* — "Poke AB." · "Tick." · "Cut." · "Add a tip on a bare
  face." — and nothing that explains, interprets, or concludes;
* its **action** is something she performs, whose consequence appears in the drawing and in the
  table.

The step definitions have **no field for prose**. A step that wanted to explain itself would have to
add one, which is a thing a reviewer can see in a diff.

**A beat with nothing to do is not a step**, so seven pairs are folded into one step each: 17–18,
19–20, 25–26, 27–28, 30–31, 37–38 and 48–49. A folded step keeps the question of the beat whose
action it performs — the later one in the first pair, the earlier one in the other six — its chip
carries the range, and it covers both sections' anchors, which the check holds it to. Forty-one
beats, thirty-four steps.

**The budget.** All the reader-facing text on a page — the masthead, the scope box, the footer, every
step's title and instruction, every control's label — is **under 250 words**, and `check_edition.py`
prints each page's count on every run so it cannot drift back. Each distinct piece of text is counted
once; a button labelled the same way on nine steps is one label, not nine. A table's caption and its
column headings are **labels on data**, not prose, and are not counted — but they are held to the same
rule about numbers as everything else. The counts today: 247 · 220 · 183 · 246 · 170.

### "If those lines are drawn from the code we're doomed."

They were: all thirty-six of the threaded pair's lines, flat, from the same census the table prints.
Flat, thirty-six lines lay strokes across dots they never touch, and a reader cannot count an edge
off a picture whose crossings mean nothing.

So chapter 5 gets the one thing the demos' charter reserved for this: **the simplest possible
orthographic wireframe.** No shading, no perspective camera, no library, no fill. It follows the
record's own conventions rather than inventing new ones — the rotation, the vertical, and the drag
sensitivity are UniForge's
`lab/primer/0116-tetoct-primer/figures/tetoct-render.template.html`, which is the record's existing
data-true render of this same lattice — with its perspective divide dropped, because a foreshortening
in a picture whose job is letting a reader count lines is a foreshortening in the way.

The first tetrahedron is drawn in the full stroke, the second lighter, and the octahedron's twelve
lines between them. The three families are **derived from what each line joins**, not declared, and
the check holds them to twelve each. Every dot carries its canon name. Drag it, or use the arrow
keys with the drawing focused, to turn it; **straighten it** returns to the opening view.

**The default view is chosen by counting.** `bestView()` sweeps a fixed grid of directions and scores
each one by how much of what the flat page says is not true — a crossing between two lines that do
not share an end costs one, a dot sitting on a line it does not end costs four, and an edge that has
projected to a point costs twelve. It opens at

> **yaw 5.585, pitch −0.654 radians** (320° and −37.5°), with **20 crossings, no dot sitting on a
> line it does not end, and no edge lost.**

Twenty is the floor of the **score**, and this paragraph is under a rule of its own, because it has
been wrong three rounds running. Every figure in it is asserted by a gate — `SWEEP` in
`core.test.mjs`, checked on every build — and **it may quote no figure that gate does not assert.**
A number that turns out to be wrong here gets deleted rather than corrected. The sweep it describes
is the 72×72 one the shipped code actually runs, the one that chooses the view a reader opens on.

Over those **5 184 directions**: no view scores under **20**, **200** of them score exactly twenty,
and every single one of those has the same shape — **20 crossings, no dot on a line it does not end,
no edge lost.**

It does **not** say twenty crossings is the fewest possible. **12** of the directions have no
crossings at all, and every one of them projects **6** of the thirty-six edges onto a point, so those
edges are not in the picture to be counted.

And at such a view the crossing count stops being a fact about the object. What separates a usable
view from a degenerate one is how many pairs of lines *touch* — pass through one another's endpoints,
or lie along one another — because for a touching pair, whether you call it a crossing is a decision
about arithmetic tolerance rather than about the shape. At the opening view **48** unrelated pairs
touch. Down an axis, **228** do. Both figures hold steady across four orders of magnitude of
tolerance, which is exactly what the crossing count of a degenerate view does not do: two careful
counts of the same axis view disagreed, 8 against 18, and both were honest.

That is the argument for leaving the plane, and it does not need the strong claim: *every flat
drawing of this object is either full of crossings, or full of joins that are not there.* The score
has three terms because those are the two ways it can go wrong, and the opening view is the one that
takes all of the first kind and none of the second.

**The step before the wireframe shows the octahedron and four tips only** — the four faces that look
at a tip of the tetrahedron we cut — and not the whole threaded pair, which is the second half of the
owner's note. The four bare faces get their tips one at a time on the next beat, on the ring, before
the object leaves the plane.

## Nothing here knows a beat number

The preface being drafted will insert beats at the **front** of `OUTLINE.md` and shift every number
in the book again. It has happened twice already — tranche C added a chapter and moved every beat
from the old 36 on, tranche D moved them by three more — and each time, anything holding a beat
number in its own source went stale silently.

So the demos hold none. [`tools/demo_steps.py`](../tools/demo_steps.py) reads each beat's **question**
off `OUTLINE.md` and its **number** off the chapter's own `<!-- beat N -->` marker, keyed by the
section's anchor, and writes [`steps.json`](steps.json). A step declares which sections it covers by
anchor — a string a renumber cannot touch — and the page renders its title, its beat label and the
chapter's beat range from what the generator wrote.

A renumber therefore changes `OUTLINE.md` and the chapters, `steps.json` follows, and **no file under
`demos/` is edited at all**. `check_edition.py` regenerates the file and fails if the committed one
is not what the contract now derives, and the cross-check insists that the step anchors **partition**
the chapter's marked sections: each covered once, none left over, none named that the chapter has not
got.

## One engine, and the pages compute nothing

The owner's other decision that day: **there is one engine for the book and its demos** — UniForge's
`napkin` crate, registered as `lab/napkin/0001`, vendored at [`engine/`](../engine/PROVENANCE.md) and
pinned by [`engine.lock`](../engine.lock).

**`core.mjs`'s seven hundred lines of exact rational arithmetic are deleted.** There is no `Frac`
class in `demos/` any more, no `BigInt`, no second implementation of anything. Every number a page
shows arrives through [`engine.mjs`](engine.mjs), from one of exactly two places:

* the compiled engine, `../engine/napkin.js` — six entry points, strings in and strings out, so no
  rational type and no float crosses the boundary: `census_json`, `cut_json`, `loops_json`,
  `slosh_json`, `certificate_json`, `number_json`;
* the vendored data, `../engine/napkin.json` and `../engine/rows.json`, whose every rational is an
  exact `"n/d"` string.

**The page formats and never computes.** Even the printing is the engine's: `number_json` says how a
napkin writes a value, or refuses it, and the page's only contribution is a plus sign in front of a
difference. The one arithmetic operation left in `demos/` is turning an `"n/d"` string into an SVG
coordinate, in `draw.mjs`, and the check below is what keeps its output out of every piece of text.

`data/napkin.json` is still written on every build and still checked, and the pages no longer read
it. It is now purely a guard: it is where `tools/napkin_export.py` — the Python that used to be the
engine — has to reproduce the vendored payload byte for byte. Two implementations sharing no code,
no arithmetic library and no language, agreeing on 22 969 bytes, is what makes a number on a page a
fact about the object rather than about a program. The pages themselves read `../engine/` directly.

### What the cross-check now means

It used to compare **two implementations** and it no longer can, because there is one. So
[`core.test.mjs`](core.test.mjs) asks a different question: **does the page show what the engine
said?** Ten gates:

1. **The engine is the engine.** The vendored wasm answers the census question with the vendored
   JSON's own bytes — byte for byte, not value for value.
2. **Every rendered number is the engine's.** Every step is rendered in every state a reader can
   drive it into, and every numeric token on every surface she meets — a table's cells, its caption
   and its column headings, the step's title, its one instruction, every control's label, and every
   piece of text inside every drawing including the SVG `<desc>` — is a value the engine returned in
   that run, that value negated, the length of one of its lists, or an index into one.
3. **No number was typed.** [`steps.mjs`](steps.mjs)'s own source is read and **any digit inside any
   string literal is refused**, in any quote style, with `${…}` cut out because that is code. The
   same rule is held over the pages' HTML: no digit in any text a reader sees, which is why the beat
   ranges on the pages are written by JavaScript at run time.
4. **The drawing is the census.** The wireframe may emit **only** `svg`, `title`, `desc`, `g`,
   `line`, `circle` and `text` — a whitelist, not a search — and every `line` is an edge the engine
   exported, every `circle` one of its vertices: thirty-six and fourteen, both directions checked,
   and checked **by where the ends of each stroke actually are** rather than by what the stroke says
   about itself. Every one of those clauses is a hole that was walked through rather than foreseen.
   A drawing that names its lines correctly and points them all at the wrong dot is the failure a
   reader is invited to catch by counting. An unlabelled stroke joining nothing to nothing rode into
   a commit while the labelled count stayed at thirty-six. And when that was fixed by counting every
   `<line>`, the same stroke came back as a `<path>`. A drawing does not get to decide which of its
   own marks are up for checking — not by leaving off a label, and not by choosing an element name.
   The ring is held separately to drawing its twelve lines with none crossing another. And a
   drawing's `<title>` and `<desc>` carry **no digit at all**: they are prose, and prose about this
   object counts in words.
5. **The steps are the outline's**, as above.
6. **The words are under budget**, printed either way.
7. **A table says what its numbers mean, and a total is a total.** Every table whose rows carry
   three or more numbers declares itself — `{ total: i }`, meaning column `i` is the sum of the
   numbers before it, or `{ notASum: true }`, meaning they are simply several numbers. A declared
   total is added up here, on the digits a reader sees, in exact arithmetic: **614 of them on every
   run.** The declaration is by **column index**, and that is the whole point of its shape: the first
   version of this gate read the column *headed* "added up", and a proof-reader switched it off by
   renaming that column in the same edit that broke the arithmetic under it, then switched it off
   again by moving the terms into a second table. Neither works now — a renamed heading changes
   nothing, and a table that splits its terms away has rows of three numbers and must declare itself.
   A heading that still reads like a total, with two or more printed numbers beside it, must *be* the
   declared column.

   What it does not reach: a total of numbers the table does not print (a run's total beside a tick,
   say) has no terms on the page to add, so it is reported, not checked. And a declaration can still
   be deleted — that is a line a reviewer sees removed, not a caption edit.

   It is here because the hole was not hypothetical: this pass shipped two walks whose printed terms
   did not add to their printed total, and a fresh reader found both by doing the arithmetic the page
   invites her to do.
8. **No label is struck through, and no two labels touch.** Every piece of text in every drawing, at
   every state, has its box tested against every stroke, every dot **and every other label** in that
   drawing — read off the emitted SVG, not taken on the placement code's word. The label-versus-label
   half arrived last and by the worst route: the first version of the search dodged strokes
   perfectly and put numbers on top of names, because it was handed a *copy* of its own record of
   what it had already placed, so every number was positioned as though it were the first. A reader
   found `0` and `−1` rendering as the single token `0−1` on chapter 2's net, twice. Two labels
   touching is the wrong-noun defect in visual form, so none may — a name and its own number
   included, since those must read as two things. And **not overlapping is not the test**: the boxes
   are inflated by a fixed gap first, because the version that asked only whether two boxes
   intersected passed a drawing whose closest pair had four tenths of a pixel between them, and four
   tenths of a pixel on a screen is two numbers touching. The gap is one constant, exported from
   `draw.mjs` and imported by the check, so the placement and the check cannot drift apart. The
   tightest pair in all 162 drawings is exactly at it. Three successive label *rules* were called fixed and were not, so the
   placement no longer asserts: it **searches** a fixed ladder of positions out along the ray from
   each dot and takes the first that touches nothing, and this gate is what says it found one. 162
   drawings: no label on a stroke, none on a dot, no two labels overlapping. The net's *names* are
   exempt from the search and not from the gate — CANON.md's rule 4 forbids moving them — so only
   their numbers are placed, and the fixed names are obstacles like any other ink.
9. **The sweep figures in DEMOS.md are the sweep's.** Every number the crossings paragraph above
   quotes is asserted from the shipped 72×72 sweep, including the touching-pair counts at four
   tolerances. That paragraph carried a wrong measured figure in three consecutive rounds while every
   number on the pages was gated; this is the gate it was missing.
10. **Every still stands on its own.** The still button is the reason the drawing code exists, and it
   is the one surface a reader reaches by downloading rather than by looking — a proof-reader could
   not exercise it at all. So every step, in every state, is rendered to its still, and the still is
   held to carrying its own stylesheet, its own title and description, and the firewall: 162 of them
   on every run.

### What no check here can catch

**Any value the engine produced, anywhere, put where it does not belong.** `cut.oct_dots` printed in
the "lines" column reads as *six lines, twelve dots*; a tip named `A′` in a table beside a drawing
that has just placed `D′` is right in every number and wrong in every noun; a bare `36` in a drawing,
attached to nothing, is a number the engine did produce. None of the three can be seen by a scan over
numbers. Gate 3 is what shrinks the hole — a wrong number cannot be *typed* anywhere, so it has to be
a real value used wrongly, and gate 7 is what closes the commonest and most checkable case of that
— a row of numbers with a total under them. What is left after those two is a value that is neither
typed nor part of a printed sum, and only reading the page catches it, which is what the proof-reader
pass is for. That is not hypothetical: the first round of this pass shipped three of them, and a
fresh reader found all three. Two were sums, and are now a gate; the third — a table naming the tips
`A′ B′ C′ D′` beside a drawing that had just placed `D′` — is the kind that remains.

The first version of this file claimed more than it checked, and a fresh reviewer walked twelve wrong
numbers past it. This pass was attacked the same way — six times by its author, then fourteen times
by a fresh reader, before it was offered. A digit in a caption or a column heading, a number computed
in JavaScript into a cell, a number in an SVG label, a wrong count in an SVG `<title>` or `<desc>`, a
number written into a page's own HTML, a beat number typed into a step, a step that drops a chapter
section or claims one twice, a tampered `engine/napkin.json`: all red. **Two got through, and are now
closed** — a wrong count hidden in an SVG description, closed by the no-digit rule on `<title>` and
`<desc>`; and a wireframe whose every line pointed at the wrong dot while its `data-edge` attribute
stayed honest, closed by resolving each stroke's ends to the nearest drawn dot and holding *that*
pair to the census.

The suite is now run as a suite, against the branch as it stands: **thirteen mutations, thirteen
caught.** A digit in a caption; a digit in a column heading; a number computed in JavaScript into a
cell; a number appended to a drawing's title; a wrong count in its description; a number written into
a page's own HTML; a beat number typed into a step; every line in the wireframe pointed at the wrong
dot; a stray unlabelled `<line>`; the same stray stroke as a `<path>`; a walk whose terms do not add
to its total; that same walk with its heading renamed; and a step quietly dropping a chapter section.

One of the thirteen looked at first like an escape and was not: appending a number to `drawWire`'s
**fallback** title changed nothing, because every step passes a title of its own and that fallback is
never reached — confirmed by rendering all 162 drawings and finding none without an explicit title.
Mutating the title a step actually uses turns the check red twice over. The lesson kept from that:
a mutation that fails to fail may be a hole or may be dead code, and the two are told apart by
checking that the mutation was reachable, not by reading the diff.

A second read of the same branch got four more past: a printed total whose column had been renamed;
a printed total whose terms had been moved to another table; a stray stroke drawn as a `<path>`
rather than a `<line>`; and two counters of the same thing disagreeing on the face-walk. **Six in
all, then, and every one of them closed** — three by making a guard read the drawing's geometry or a
table's declaration instead of its own labelling, one by a whitelist, one by deleting a second
counter, and one by the arithmetic gate above. The paragraph above is what remains.

One more thing this file has to say, because it cost something: **a reviewer and an author must not
share a working tree.** The proof-reader for this pass worked in the author's worktree and reverted
its own attack edits with `git checkout --`, which silently reverted two of the author's uncommitted
fixes; and one attack edit was still in the tree when the author committed, so an unlabelled stroke
shipped. Both were caught, and the second is now gate 4's business rather than luck. The reviewer
gets its own checkout.

Run it by hand:

```sh
python3 tools/demo_steps.py --check   # the scaffolding is what the contract derives
node demos/core.test.mjs              # the cross-check on its own
make check                            # tier 0, which runs both
```

## Gaps in the engine

**Four** things a step wanted and the engine's browser surface does not expose, and a fifth noted
rather than wanted. **None of them is computed in JavaScript**; each is either taken from the
vendored payload — where the engine did compute it, for one fixed set of inputs — or the interaction
is narrowed to what the engine can answer. They are the register rows to ask UniForge for.

| what a step wanted | what it does instead |
|---|---|
| **the rule with the dial turned** — `slosh_json` runs with every line counted the same, so the reader cannot turn the dial and re-run | beat 36 offers the two positions the engine computed and vendored (`motion.plain`, `motion.dialed`, `AB` counted double), as a choice rather than a dial |
| **the outward-oriented eight-face sum** — `loops_json` walks the octahedron's faces in the complex's own orientation, which does not sum to zero; the vendored `face_sum` is the outward walk, and it does | beat 43 walks the eight faces of the vendored arrow set; the reader steps through the faces rather than changing an arrow |
| **the two-dot complex** — `loops_json` answers for the book's four objects, and two dots and a line is not one of them | beat 10 asks the triangle for the difference on `AB` and reads `AB` alone. It is the same line and the same coboundary either way |

The fourth: `certificate_json` panics on `"triangle"` rather than answering, so beat 33 shows the
triangle's two ticks through their runs — which rows a napkin can write, and whether it comes home —
rather than through a ceiling.

The fifth, noted rather than wanted: `loops_json` gives no **running partial sums** along a walk, so
beat 14 shows each step's own contribution and the engine's total rather than a running tally. What
it *does* give is each line's contribution on its own — ask it about one line with every other set to
nothing, and what comes back is that line's term in the walk, with the orientation the object gives
it. That is how the walk's terms are got (`Engine.contribution`), and it is why **the page never
flips a sign**.

## The drawings: three conventions, and no fourth

### The tetrahedron — CANON.md's flat unfolded net

The net [`CANON.md`](../CANON.md) governs: `ABC` in the middle with the other three folded out from
its sides, the same six positions, the same names `A B C D`, all four panels the same fill, every
label upright, the diagram never rotated or mirrored. **The coordinates are the engine's** —
`napkin.json`'s `net` block, which is `tools/canon.py`'s own exact `(x, u·√3)` ring — and `draw.mjs`
places them rather than deriving them.

Numbers are written **on the pieces they belong to**, and the *name never moves*: it stays at its
canonical position and the number takes a fixed step from it — into the panel for a dot, straight
down for a line or a face. Both obvious alternatives failed. Moving the name and the number inward
together piles a panel's four labels onto its middle; stepping a line's number sideways pushes it
onto the next line's name across the fold. `D` appears three times and carries the same number three
times, because it is one dot.

Chapter 1 draws its dots as dots, and the net does not. That is not an inconsistency to be tidied
away: in the net a corner is where lines meet, and there is always a line. In beat 9 there is not —
the question is *where could you put a number*, and its answer needs something to point at. Chapter
1's triangle is the net's central panel, framed to itself, so when the fourth dot arrives the
triangle is already where the net puts `ABC`.

### The octahedron — the ring

**Six dots on two concentric circles**: the middles of the three lines that leave `A` on the outside,
and the three no line joins them to on the inside, each on the same ray out of the centre as its
partner and on the other side of it. So *opposite* is literally straight through the middle, which is
what the poke beat needs a reader to see. The three joins that are **not** there are marked by a
faint line through the centre, and that is the only mark in any of these drawings standing for an
absence.

All twelve lines are drawn once and none crosses another. That is checked before a stroke is emitted,
by `ringPlanarity()`, and it is checked because it was once false: at exactly half the outer radius
each inner dot lands *on* the outer triangle's edge, and the twelve lines then draw as six.

Two honest costs, both stated on the page:

- **One face is the outside of the paper.** Flat paper always makes one face the outside, so when the
  eight faces are walked one at a time, that one is shown by thickening its three lines instead of
  filling a region.
- **Four of the eight tips cannot sit inside their own face.** Three of the ring's faces are thin
  slivers and the eighth has no inside at all, so those four sit outside the ring, each on the ray
  through its own face — except the outside face, whose three dots average to the centre exactly and
  so names no ray; that one is placed straight above, and it is the single arbitrary choice in the
  convention. Their lines in are the only lines in either flat drawing that cross anything: seven
  crossings, all among the tips' own lines, none among the twelve. The count is pinned in the check.

**A net was considered for the octahedron and refused**, for one reason: a net puts a dot in more
than one place, and the whole of the poke beat is *it crossed to the opposite dot and is nowhere
else*. On a net, "the opposite dot" is two or three marks on the paper.

### The threaded pair — the wireframe

Above. The charter's condition for leaving the plane was that 2-D genuinely could not show the step,
and the crossings count is the evidence: twenty is the floor.

### Where a label goes: searched, not ruled

Three successive label *rules* were called fixed and were not — a fixed step outward, then a fixed
step down, then a fixed step outward along the ray — and each time a proof-reader counted names and
numbers struck through by the very line they belonged to. A rule that has to be right everywhere on
a drawing with twelve or thirty-six lines through it will be wrong somewhere.

So a label's position is **searched**. A fixed ladder of candidate spots — ten distances out from the
dot, each swung to sixteen angles either side of the ray from the middle of the drawing — is tried in
a fixed order, and the first spot whose box touches no stroke, no dot and no label already placed is
taken. Beyond the ladder there is a coarse sweep outward, every ten degrees to a distance that covers
any of these drawings, because a refused fraction like `−15/8` is a far wider box than a
two-character name and the ladder is shaped for names.

**Everything already on the paper counts**, and getting that wrong is how the search's first version
went out: it was handed a filtered *copy* of its record of what it had placed, so `taken.push` went
into a throwaway and each number was placed as if none of the others existed. The fixed names of the
net — and the face name, which was the one box never recorded at all — are in the record too. The ladder and the order are fixed, so the drawing is identical every time; gate 8 then checks
the *emitted SVG* rather than taking the placement code's word, so a ladder too short to find a clear
spot fails the build instead of shipping a struck-through number.

**On the ring and the wireframe, a dot's name and its number are one label.** Searching for them
separately did stop anything being struck through, and made a worse drawing: the six numbers went
wherever there was room — one far left, one far right, one below the rim — and which number belonged
to which dot stopped being obvious. On a drawing whose whole point is *which number is on which dot*,
that is the wrong thing to trade a collision for. Written as one string, `AB 1`, they cannot come
apart, and the search has one box to place rather than two that must both be clear and adjacent.

**The net's names are exempt from the search and not from the gate.** `CANON.md`'s rule 4 forbids
moving a label to wherever it fits, and the net's nineteen positions are the engine's, so they stay
— and the name/number pairing above is *not* applied there, because on the net the name must not
move and the number must follow it. Only where the number sits beside the fixed name is searched,
which was never CANON's to say. That the two conventions differ is the point: CANON governs the
tetrahedron and nothing else.

### A drawing carries what its beat is about

The last thing the label search taught, which no gate says: **a drawing that carries every number is
not more honest, it is just unreadable.** Chapter 2's net at beat 21 was made to carry four corner
numbers, six differences and four face totals at once — thirty-eight labels on one small frame — and
once nothing overlapped any more it was still the worst drawing of the three. The beat asks *what
does each face say?*, so the drawing now carries the corners she typed and the zero each face comes
to, and the six differences are in the table immediately below it, where they were all along.

Nothing is lost by that: **every number is in a table, on every step**, which is a rule a gate does
hold. What the drawing chooses is which of them are worth ink.

### No colour means anything

One panel fill, one stroke, and one heavier stroke marking *the piece this step is about* — never a
kind of piece. That is `CANON.md`'s rule 5 kept honestly: there is no colour spare to encode with.
The wireframe's three line weights are the exception that proves it — they say which of the three
families a line belongs to, they are stated in the drawing's own description, and they are weights
rather than colours for exactly that reason. Light and dark are the same drawing with ink and paper
exchanged.

## Exact, or refused

Every displayed number is an exact rational the engine wrote as a string, and the engine decides how
it prints. There is no floating point in any number a reader is asked to check, and the refusal —
when a value cannot be written down shortly and exactly — is shown as a refusal rather than rounded.
That is not a formatting fallback: it is two of the book's own findings, in chapter 3 where the
triangle is run at the wrong tick and in chapter 5 where the arithmetic leaves the napkin altogether.
Floats appear in one place only — SVG coordinates — and never in a number.

## The stills, and how the studies get replaced

Every step has a **still** button that renders exactly what is on screen to a standalone SVG: its own
stylesheet inlined, its own `<title>` and `<desc>`, and a comment naming the chapter and the beat it
came from. Those stills are the intended replacement for the placeholder studies in
`chapters/assets/`, which the owner has called amateurish and AI slop.

**This is not that PR.** Replacing a study touches `chapters/` and `ART_DIRECTION.md`, and it is a
judgement about the book's art rather than about its arithmetic, so it is the owner's to make. When
it happens, the shape of it is:

1. pick the beats whose stills earn a place in the prose — not one per chapter by quota;
2. commit each still under `chapters/assets/`, generated by a small script that drives the demo
   modules under node so the committed SVG is derived and not hand-touched (the same discipline
   `tools/canon.py` already holds for the net);
3. replace one asset at a time under `ART_DIRECTION.md`'s replacement rule, updating its `alt` text
   and its caption in the same commit;
4. and drop the `Analogy — not data.` opener for these, because a still **is** the data — which is an
   `ART_DIRECTION.md` change, and the reason that document is not touched here.

## Accessibility and honesty

- **Keyboard-steppable.** `←` / `→` (or `j` / `k`) walk the beats; the tick and the choices are
  buttons. On the wireframe, with the drawing focused, the arrow keys turn it instead.
- **Every number is text.** Whatever a drawing shows, the same values are in a table underneath, so a
  page reads correctly with the pictures ignored entirely. A step with no table fails the check.
- **Light and dark**, following the reader's system, with an override remembered per browser.
- **No easing.** The rule has no in-between, so the motion cuts from one tick to the next. A drawing
  that slid between two ticks would be inventing something the rule does not do.
- **Nothing loaded from anywhere.** No framework, no CDN, no font, no image, no analytics. Four
  modules, one stylesheet, and the engine this site already serves.
- **A deep link is a beat**: `#beat-31` opens that step.

## How it reaches the published site

`demos/` sits outside `chapters/`, so mdBook carries it through the `chapters/demos` symlink — the
same mechanism that publishes `record/` and `engine/`. The pages land at
`https://zacharyelston.github.io/OurBubble/demos/`, they load the engine from `../engine/` beside
them, and `check_edition.py --rendered` confirms both are there and that every link resolves before
anything is deployed.

## Reading them locally

```sh
mdbook build
python3 -m http.server --directory book 8000
# then open http://localhost:8000/demos/
```

Serving the whole built book is the right way round: each page links back to its chapter with
`../<chapter>.html`, and reaches the engine at `../engine/`. Serving the repository root works too,
for the same reason — `demos/` and `engine/` are siblings in both trees — but the back-links will
404, because there is no book there to go back to.

The pages are ES modules and they instantiate WebAssembly, so `file://` will not do; they need a
server, any server.

**One trap, which has now caught both a writer and a reader of this repository.** mdBook *copies*
`demos/*.mjs` into `book/demos/`; they are not symlinks. So a server left running across a rebuild
serves a page whose HTML looks current while the browser holds the previous modules from its cache,
and a cache-busting query on the HTML does not help, because the page imports `./core.mjs` without
one. A proof-reader reported a defect twice from a build like that, and the author took two
screenshots of a fix that was not on screen. If a change does not appear: stop the server, rebuild,
start it on a **new port**, and load the page fresh — or check the drawing by rendering it under
node, which is what the checks do and what settled every measurement in this lane's last two rounds.
