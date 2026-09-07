# Primers, after Kleist — a review of the fortnight and a proposal

*Working note, 2026-09-07. Structure lane. Read with `EDITION_STANDARD.md` § *A primer* and the
drafter's note on the primers at the foot of `OUTLINE.md`.*

> **Scope.** This note is about the pacing of a book about a **toy**. Nothing in it is a claim about
> nature.

## 1 · What the owner asked

Two pieces of the owner's own writing arrived — *Staring into the Abyss* (a house a block from the
ocean, the void, and zero) and *Boundaries* (an all-white jigsaw, and where you start) — with this
brief:

> these should be fit and reflowed into the existing book pacing. perhaps at each major chapter we
> have some personal experience primer doc. the book is currently to abstract and vague and relies on
> too many small steps without constant resolidifying. it 's not working and needs a personal touch.
> lets think like Kleist in the Marionette Theater.

The owner had already named Kleist once, answering issue #73 on 2026-09-05: *"OurBubble is an
allegory study the way Kleist's 'On The Marionette Theater' walks the reader through the scenes."*
So this is the second time the same instruction has been given, and the note treats it as a standing
direction rather than a passing reference.

## 2 · The fortnight in review (2026-08-24 → 2026-09-07)

Both repositories were read: the merged pull requests, the open ones, the epic
(https://github.com/zacharyelston/OurBubble/issues/67) and its eleven comments, and the two ledgers.

**What landed in the book.** The reader edition moved out of UniForge (2026-09-01) and then rebuilt
itself in five days: the napkin world on one triangle and one tetrahedron (tranche A), the record
chapters (B), the octahedron (C), time as two rows and the threaded pair (D), the history moved
forward to sit after *The shadow* (E), a chapter on boundaries (F) and a signposted interlude in *Is
it round?* (G). Around the prose: one engine, vendored and pinned; demos that do rather than narrate,
with a mutation suite; figures drawn by the demo code and refused when hand-touched; beats renamed
`slug.n` so an insertion renumbers one chapter; reader notes as prefilled issues; a proof-reader skill
with thirteen named failure modes and a standing order that a fresh reader sees every draft before
the owner does. Seventeen chapters and an appendix at `589a965`.

**What landed in the engine.** The `napkin` crate (`lab/napkin/0001`, 23 rows, exact rationals),
its five gaps filled (`lab/napkin/0003`), the fair octahedron-clock test registered but blocked
(`lab/napkin/0004`, UniForge #356: the σ-odd generator is an existence proof), and the review that
scoped the octahedron negative to the one reading it tested (`lab/napkin/0002`). UniForge's five open
pull requests (#61, #84, #111, #115, #126) all predate the fortnight — July work, untouched since —
and none is about the book.

**State at the pause (owner, 2026-09-05: "we should pause after this round").**

| item | state | what I found |
|---|---|---|
| https://github.com/zacharyelston/OurBubble/pull/97 (draft for #73) | open, **conflicts with `main`** | Opened by a Codex cloud session from a recovered checkpoint; carries `ISSUE-73-CHECKPOINT.md` at the repository root, which must not merge. More important: its premise is *one method, several instruments*, and the owner's answer on #73 says that is not the intended reading — the "one method" is the Hodge star's reduction to other sciences, the pivot belongs about halfway, and *Container-specific* means the parts not about the girl. The draft's eleven files rewrite the front door's road, *Make it move*'s "nothing else, ever", the tiling chapter's close and the ending to the rejected premise. It needs re-scoping before a proof-reader spends a round on it. |
| https://github.com/zacharyelston/OurBubble/issues/100 (figure guard) | open | Three guard blockers from PR #98's review, merged unapplied at the pause; and the ruling that *Is it round?* must carry the two isotropy rings drawn from the record's CSV. Tooling and a figure; owner judges the picture. |
| https://github.com/zacharyelston/OurBubble/issues/99 (writing rule) | open | A thing is described by what it is; one comparison, never a list. The instance is *The shadow*'s "Not an instrument, not a talent, not a laboratory". Rule text, grep sweep, skill mode. This note's two primers were written under it. |
| #82, #83, #87, #88, #89, #90–#95 | open findings | Filed, not fixed. #83 (relative chapter counts in prose) and #82 (bare numbers in `demos/DEMOS.md`) are the two this insertion could have worsened; it did not — the chapter distances the four live instances count are unchanged, because both primers sit before the run of chapters they measure. |

**On the previous session's proposed order** (#100 first, then #99, then the zero beat and the
shadow-as-comparison intro): the owner's brief supersedes it for the Rewrite lane. #100 is tooling
and can run beside it. #99's rule is applied here rather than after.

## 3 · The diagnosis, and what the book already does about it

The owner's sentence is "too abstract and vague and relies on too many small steps without constant
resolidifying." Read against the book as it stands, that is not a complaint about any one chapter.
Every chapter is built to the same grain — a question, a hundred-odd words, the next question — and
the grain is what makes the small steps possible. What the grain cannot do is stop. Between the
front door and the first napkin fact the reader meets three arguments in a row (edges, the shadow,
resolution) and nothing she can stand in. The book's tools for solidifying are all *inside* the
argument: the ✎ pause, the token that computes in front of her, the record link. None of them is a
place to rest before the argument begins.

What the two pieces supply is exactly that: a scene. A table, a box of pieces, a shoreline at the end
of a commute. Nothing in either is an argument, and each ends on a sentence the next chapter needs.

## 4 · Kleist, operationally

*On the Marionette Theatre* (Heinrich von Kleist, 1810; the owner's link is
https://southerncrossreview.org/9/kleist.htm) is a short prose piece and the whole of it is one
conversation. What it does, as a matter of construction:

1. **It opens in a place, not on a claim.** A winter evening in a public garden, the narrator, and
   Herr C., the first dancer at the opera, who has been watching the puppets in the marketplace. The
   thesis — about grace, and about consciousness — is not stated until the last page, and when it
   arrives the reader has already been made to agree with it by what she watched.
2. **One mechanism carries everything.** The puppeteer controls one thing, the centre of gravity, and
   the limbs follow of their own accord; the line the centre travels is, C. says, the path of the
   dancer's soul. Every later claim is a consequence of that one line. The book has the same shape:
   one rule for a tick, one dial, and the results as consequences.
3. **The narrator resists.** He says he does not believe it, more than once, and C. answers with a
   story rather than an argument. The book's version of the resisting narrator is the reader, and her
   instrument is the ✎ pause and the "hold it lightly" the boundaries chapter asks for.
4. **Few scenes.** Three anecdotes — the puppets, the youth who saw himself in the mirror and lost his
   grace in the trying to repeat it, the fencing bear who parried every thrust and ignored every
   feint — and each one is the argument told again from a different side. Kleist did not need a fourth.
5. **It ends on what the reader must do.** The last exchange is about eating again of the tree of
   knowledge — the way back to grace runs through more knowledge, not less — and the piece stops. The
   book's version is *Cast your own shadow*.

"Think like Kleist" therefore means, for this book: put the reader in a scene before each movement;
let the idea be what the scene turned out to mean; keep the scenes few and the narrator's voice
consistent; and never explain the scene in the scene.

## 5 · The form: a primer

A **primer** is a page at the door of a movement of the book — one scene from the author's own life,
in the first person, with the idea arriving last and landing on the next chapter's first move. The
contract is in `EDITION_STANDARD.md` § *A primer*; the two rules worth repeating here are that a
primer is **reflowed, never invented** (the drafter cuts, reorders and tightens the owner's words and
adds no experience), and that primers are **few** — one per movement, never one per chapter.

To the tooling a primer is a chapter, deliberately. It gets a slug, a Scope block, beat markers and
an outline block, an appendix section that says *no evidence was cited*, the grain band and the
`Next`. The alternative — a page the guards do not read — would be the one page in the book that
could carry a count, a chapter number or a nature claim unrefused.

## 6 · The two primers as drafted

### *Boundaries* — `start-at-the-boundaries`, between the front door and *Where the inside shows*

The owner's *Boundaries*, in five beats: why boundaries are good to have; the all-white puzzle and its
border; tomorrow, and the one solution; tension and release, and *working* rather than *solving*;
and the hand-off — this book describes a puzzle, and we start with the boundaries. The egg in the
chapter after it is named so the reader walks straight into it.

The slug is not `boundaries` for the reason the boundaries chapter's own note gives: the guard finds
a beat id by its slug's hyphen. The title is the owner's.

**Meanings moved in the reflow**, for the owner to accept or reverse:

- "You do that in the first evening, 25 per side" — the per-side count came off the page. A
  thousand-piece border is about a hundred and twenty-six pieces, not a hundred; "a hundred-odd" is
  kept and the twenty-five is not, because it is a number the reader can check.
- "like all puzzles there is only one way this puzzle goes together" is kept, with one clause added
  so the sentence pays what *Room, and a world with no edge* delivers — every step forced but one —
  rather than promising more: "you will be told plainly where a hand had to choose."
- "Puzzles have 1 Solution" — the claim is about jigsaws and stays. It is not about the toy.
- The front door's opening line "the one page that talks about the book" lost its *one*, because the
  primer's last beat also talks about the book. The count was already noted in the outline as a
  count nothing guards.

### *Staring into the abyss* — `staring-into-the-abyss`, between the history and the napkin chapters

The owner's *Staring into the Abyss*, in four beats: the house a block from the ocean and the smile;
what the void was — less than the other direction, peace by selection; write nothing down — the zero,
the one, the two bursting on to the scene; one direction — infinity emergent, the blank page as the
right place to be standing, and *draw the first thing*. The history chapter already ends on "a blank
page, and the smallest thing anyone could draw on it," so the primer sits on a hand-off that was
already there, and *Two dots, a line…* already opens "Start with nothing."

The title corrects the owner's "Starring" to "Staring"; if the pun was intended, say so and it goes
back.

**Meanings moved in the reflow:**

- "you have just created all you need to form the universe" became "zero is what made all of this
  possible" — *this* being the book's counting. The original is the one sentence in either piece
  that reads as a claim about nature, and the firewall does not allow it; the Scope block says
  plainly that the zero is a mark on paper.
- "the spark of life would be Zero's claim" became "if zero could make a claim, it would claim to be
  the spark" — the claim stays zero's, and *life* is gone for the same reason.
- "It's kind of the definition, which isn't life" became "That is more or less its definition." The
  clause it lost was a second negation in a definition (issue #99).
- "Eastern shore of America" is kept as written, lower-cased. If the owner means the Eastern Shore of
  Maryland and Virginia as a place, the capitals should go back.

**What neither primer carries:** a figure, a token, a quotation, a number about the book, a chapter
number, a physics word. Both pass the grain band in every section; the checker's own counter puts
*Boundaries* at 720 reader words and *Staring into the abyss* at 672.

## 7 · The movement map — two doors filled, three open

| movement | door | primer | state |
|---|---|---|---|
| the door | *Where the inside shows* | *Boundaries* | drafted here |
| the napkin | *Two dots, a line…* | *Staring into the abyss* | drafted here |
| the machine | *Room, and a world with no edge* | — | open: the scene is the owner's to supply |
| the record's pivot | wherever #73's pivot lands (owner: about halfway) | — | open; a primer is a natural form for the visible pivot #73 asks for |
| the exit | *Cast your own shadow* | — | open |

The three open slots are left empty on purpose. A primer that a drafter wrote would be a scene the
author did not live, and the form has no value then. The owner's "the zero beat and the
shadow-as-comparison intro from our riff" (last session's state report) are the two candidates
already named; the zero beat is this note's second primer.

## 8 · What this branch changes, file by file

- `chapters/start-at-the-boundaries.md`, `chapters/staring-into-the-abyss.md` — new.
- `chapters/SUMMARY.md` — the two entries.
- `OUTLINE.md` — two new blocks; every later chapter heading up by one or two; the ritual paragraph's
  range; the boundaries note's chapter numbers; the front door's count note; a drafter's note on the
  primers.
- `edition.json` — two chapter entries, two appendix sections, one retired phrasing (the front door's
  egg pointer) with its probe.
- `chapters/what-you-will-have.md` — the closing pointer and `Next` go to the puzzle; "the one page"
  loses its count.
- `chapters/a-few-thousand-years-of-sharper-shadows.md` — `Next` goes to the abyss; the closing
  paragraph is unchanged, because the primer stands on it.
- `EDITION_STANDARD.md` — § *A primer*; the illustration contract's front-matter paragraph; the
  napkin range `4–8` → `6–10`.
- `README.md` — the two counts, the opening sentence, the napkin range twice.
- `gen_appendix.py` — the appendix preamble names the primers among the sections that cite nothing.
- `tools/attacks_beats.py` — the outline-block mutation's needle, which named a heading number.
- `chapters/the-simulations.md` — regenerated by the build.
- `CONTINUUM.md` — a Primers lane row.

**Tier 0 on this branch:** `tools/beat_coverage.py` reports every outline beat claimed and every
section inside the grain band; `tools/attacks_beats.py` 24 mutations refused by name;
`tools/figures.mjs --check` green; `mdbook build` green with 19 pages; `check_edition.py --rendered`
passed — 19 chapters and the appendix, 12 retired phrasings absent, 49 exclusion probes refused. The
full `check_edition.py` pass (with the demo attack suite) is recorded on the pull request. Snapshot
and engine integrity read *unverified* here, as they do in any clone without the private engine.

## 9 · What a proof-reader should look for

- **Voice (mode 6).** The primers are the only first-person pages in the book. The break is the
  point, and it is declared in the Scope block; a reader should still say whether it lands as a
  register change or as a stumble.
- **Firewall (mode 7).** The zero primer's "infinity is emergent" is about counting and says so; the
  puzzle primer's "goes together one way" is about the toy and is paid by the tiling chapter. Read
  both as someone who skipped the grey box.
- **Negatives (issue #99).** Each primer keeps one comparison — "not a puzzle; it describes one",
  "not an absence — the one place a first mark could go". If either reads as a list, it is a finding.
- **The front door's road.** Its road beat still opens "First, why measuring gets done at edges";
  the puzzle now comes before that. It is a primer rather than a step, so the road may be right to
  skip it — or the road wants one more clause. Owner's call.
- **Placement of *Boundaries*.** Before the front door is the other honest reading of "we're going to
  start with the Boundaries." It sits after because the front door's own road then stays true.

## 10 · The next round, revised

1. This pull request: a fresh proof-reader to CLEAR, the owner's read, the owner's word on the moved
   meanings in § 6.
2. #73 / PR #97: re-scope to the owner's answer before any prose is touched again — the Hodge star's
   reduction, the halfway pivot, Container-specific as the parts not about the girl — and decide
   whether the pivot is a primer.
3. #100 (figure guard and the rings) in parallel, as tooling.
4. #99 sweep of the remaining chapters, with the skill mode.
5. The three open primer doors, as and when the owner has a scene for each.

FIREWALL: this note concerns the pacing of a book about a toy DEC lattice; nothing here is a claim
about nature.
