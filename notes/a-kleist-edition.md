# A Kleist edition — what the book would become, and how to branch for it

*Working note, 2026-09-07, after the primers merged at `92de3e9`. Structure lane. Read with
`notes/primers-after-kleist.md` (the review of the fortnight and the primer form) and
`EDITION_STANDARD.md` § *A primer*.*

> **Scope.** This note is about the shape of a book about a **toy**. Nothing in it is a claim about
> nature.

## 1 · The owner's words

> It looks ok. Let's merge and re read it fully. We might even branch here for a new Kleisty version.

Two instructions and a possibility. The merge is done. The full re-read is this note's § 3 and the
fresh reader's table filed beside it. The possibility — a Kleist edition, and a branch point for it —
is § 4 onward, written as a proposal for the owner's judgment, with no prose moved.

## 2 · What the book is now, read in one sitting

Nineteen pages and the appendix. Two movements before any object exists (the door: front door,
*Boundaries*, *Where the inside shows*, *The shadow*, the history), one movement on a napkin (five
chapters, with *Staring into the abyss* at its door), one movement handing the object to a machine
and calibrating it (*Room…*, *Is it round?*), one movement of results (five chapters), and the exit.

What one sitting shows that a chapter at a time does not:

- **Every section ends on a question, and every next section begins by answering it.** The book's
  engine is the Socratic hand-off, and it never rests: across eighteen chapters there is almost no
  section that ends on a statement the reader is allowed to sit with. That is the "too many small
  steps without constant resolidifying" of the owner's brief, seen from inside. The steps are the
  right size. What is missing is a floor between flights of them.
- **The two primers are the only pages where a person is present.** Everywhere else the voice is
  "you" and the child is "she"; the author appears once as "mine" in the last chapter. The primers
  change the temperature of the pages around them — the egg reads differently after the jigsaw, and
  *Two dots* after the shoreline — and then the temperature drops back for eleven chapters.
- **The people in the record chapters are citations, not scenes.** Eratosthenes gets a scene (two
  posts, a well, a walked distance). Aristarchus, Hipparchus, Aristotle, Rømer, Bessel, Kepler, Mach,
  Einstein, Alcubierre, Casimir and Onsager get a sentence each. Kleist would have given the reader
  Mach at his desk and taken the sentence away.
- **One promise is broken and the reader can see it.** *Make it move*'s fifth beat — "Everything the
  rest of this book measures is that sentence, run … There is no second rule for the hard chapters" —
  and the front door's "the one rule everything here is made of" are not what the later chapters do:
  the gap chapter builds a one-dimensional row of oscillators, the answer-key chapter an Ising model,
  the refusal chapter a resonating cavity. Each change is disclosed where it happens; none is
  reconciled with the promise. Issue #73 named this, and the owner's answer there sets the direction:
  the pivot goes about halfway, and the Container is the boundary and inside of the tet-oct lattice.
  Whatever else happens, this is a fix on `main`, not a feature of an edition.
- **The reader's pacing map asks for the third primer one door earlier than this note did**: at
  *Two worlds threaded → Room, and a world with no edge*, where the napkin has just failed and the
  machine is handed the world unseen, with the pivot door second. Both are on the movement map; the
  order is the owner's.
- **The pacing sags in one place.** The five result chapters are each built the same way — the
  question, the ✎ guess, the number, what the number is and is not — and by the third of them the
  ritual is felt as a ritual. A scene at the door of that movement (the record's pivot) is the single
  highest-value primer left to write, and it coincides with where #73's pivot belongs.

## 3 · The re-read: findings for `main`, independent of any edition

These are the Structure lane's own, from the read above. The fresh reader's whole-book table is the
authoritative one — **HOLD, 34 findings, 5 blockers**, filed as
https://github.com/zacharyelston/OurBubble/issues/103 with its pacing map and the #99 sweep; where the
two agree the item is listed once. The reader's first blocker sharpens § 3.1 below and was checked
against the record snapshot before being repeated here: `record/lab/warp-1-move/0115-…/spec.md` runs
the ripple on `mesh_3d_tetrahedral_grid` and times a lattice axis against a body diagonal, `0501`'s
exponents come from a Wolff Monte Carlo, and `0400`'s gap is a fixed–fixed chain. The *Container* the
reader builds — one tetrahedron per cube, its lines all face diagonals — is a cousin of the first and
not the object of the other two. The book's "everything from here is this one thing" is therefore not
a wording problem but a fact about the record, and the pivot #73 asks for has to say so.

1. **`make-it-move.5` and `what-you-will-have.2`** promise one rule for every result; three later
   chapters use other models. Fix per the owner's #73 answer: a visible pivot about halfway (after
   *Is it round?*), the two promises narrowed to the world she builds, each later model's entrance
   naming what it makes readable. PR #97 attempted this on a premise the owner set aside; take its
   *diff* as raw material for the entrances, not its framing.
2. **The record chapters' people** are named but not shown. Where the history chapter already does
   this well (two posts, a well), the later chapters could each afford one sentence of scene for the
   person whose law is being tested. Not a rewrite: one sentence each.
3. **Relative counts in prose** (#83): "the last four chapters", "Two chapters, three noes", "seven
   things". The primer insertions did not disturb any of them, by luck of placement. They remain the
   next thing to go stale.
4. **`a-number-without-the-answer-key.1`** — "this project used to do it": the author's voice, in a
   chapter otherwise in the book's. Either own it as a primer-style aside or make it the book's.
5. **The appendix** reads as a reference and says so; its one prose defect is that the section for
   the history chapter and the two primer sections say "no evidence was cited" in the same formula,
   which is right but reads as boilerplate three times in a row at the front. A reader who opens the
   appendix at §00 meets four near-identical paragraphs before the first rung.

## 4 · What "a Kleisty version" would be

Kleist's piece is one conversation, on one evening, in one place. Everything in it is either a
scene the narrator was in, a story the dancer tells him, or the narrator's own resistance. The
thesis is never announced; it is what the reader is left holding. Read against that, the book as it
stands is Herr C.'s side of the conversation with the narrator taken out: the explanations, in order,
excellently paced, and nobody in the room.

A Kleist edition puts the room back. Concretely, three moves, in increasing depth:

**A. Primers at every door (the shallow version).** Five movements, five scenes, all the owner's;
two exist. This is already the plan and it needs no branch — it is `main`'s next three primers, as
the owner's scenes arrive. Cost: three pages. What it fixes: the floors between flights. What it does
not fix: the eleven chapters between the primers still have nobody in them.

**B. A narrator who resists (the middle version).** Keep every chapter, and give the chapters a
first-person voice at exactly the places where the book currently says "hold it lightly", "write
your guess down", "go and look at your guess". Kleist's narrator says *I could not believe it* and
the dancer answers with a story; our reader is asked to guess and the machine answers with a number.
The move is to let the author be the one who guessed wrong first — "I wrote *square root*, in
writing, in advance" is already nearly on the page in the refusal chapter — so that every ✎ moment
has a person in it before the reader is asked to be one. Cost: one or two sentences in each of the
nine ✎ chapters, plus the two promises in § 3.1. What it fixes: the temperature drop after each
primer. What it risks: the firewall — a first-person author is a person who can be read as
believing something, so every such sentence is about the guess and the record, never the world.

**C. One conversation (the deep version).** Recast the book as Kleist cast his: a frame (the owner
and an interlocutor, over the days the book's questions were asked), the napkin chapters as things
done on the table between them, the record chapters as stories the interlocutor tells and the
narrator disbelieves, the numbers arriving as the ends of stories. This is a different book with the
same record behind it. Cost: a rewrite of every chapter's opening and closing, a new contract
(`OUTLINE.md`'s beats would stay; their questions become the narrator's), and a decision about who
the interlocutor is — the child grown up, the engine as it answers, or a real person the owner
worked this out with. What it fixes: everything the brief names. What it risks: two editions to
maintain, and a form that Kleist sustained for eight pages being asked to hold for a hundred.

**Recommendation.** B on `main`, now, with A as the owner's scenes arrive; and a branch point kept
for C rather than a branch started. The reason is the record: the two-voice discipline the book runs
on (the guards, the tokens, the pinned record, the proof-reader loop) is what makes its numbers worth
reading, and B keeps all of it while putting a person on every page that asks the reader to be one.
C is worth doing only if B turns out not to be enough, and B is the cheapest way to find that out.

## 5 · "Branch here" — the mechanics, whichever version

The owner's phrase is exact and should be honoured literally, at no cost:

1. **Tag the merge.** `pre-kleist` at `92de3e9` marks the book as it stood when the primers landed
   and the question was asked. A tag is the branch point kept, without the second edition started;
   anyone can `git checkout pre-kleist` and read that book.
2. **Do B on `main`.** It is small enough to be one tranche with a proof-read, under the standing
   order, and it does not change the book's contract — the beats, the tokens, the appendix — only
   its voice at the ✎ moments and the two promises.
3. **If C is wanted, branch `edition/kleist` from `main` after B**, not from `pre-kleist`: C inherits
   B's voice and the #73 fix rather than redoing them. The branch carries its own `OUTLINE.md`
   questions (the narrator's) and its own `SUMMARY.md`; it merges `main` for tooling and record bumps
   and never the other way; it publishes at a second path (`/kleist/`) from the same Pages workflow,
   or replaces the default when the owner says so. The proof-reader reads it as its own edition —
   the persona changes: a reader who has agreed to listen to a conversation.
4. **Never fork the repository.** Two repositories are two records, and the pin, the engine and the
   guards would drift within a week.

## 6 · What this note does not do

It moves no prose. It does not write the three open primers (the machine, the pivot, the exit) —
those scenes are the owner's. It does not decide who the interlocutor of a C edition would be. And
it does not settle the two disputed nits from PR #102's table (the opening "us, not them" line; the
history chapter's "blank page" close), which are the owner's.

## 7 · Next round, proposed

1. Owner: A, B or C; the tag; the two disputed nits.
2. On `main`, one tranche: the #73 pivot and the two promises (§ 3.1), with B's voice at the ✎
   moments if the owner takes B. Fresh proof-read, owner's word.
3. The reader-facing findings from the whole-book table, as small PRs.
4. Primers three to five, as the owner's scenes arrive; the pivot's first.

FIREWALL: this note concerns the shape of a book about a toy DEC lattice; nothing here is a claim
about nature.
