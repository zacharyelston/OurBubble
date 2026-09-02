# Our Bubble

**A book about a small world we built inside a computer, and what happened when we pointed real
tests at it.**

Fourteen chapters and an appendix. It starts with a child noticing her shadow and a Greek who knew what
to do next, and it ends with you running the checks yourself. In between: a structure built out of
points and lines, a ripple that came out lopsided until one setting fixed it, a wall that worked and
a hoped-for effect that did not, an energy bill, a measurement with no answer key, and a law that
came back gentler than the one we proposed.

> **Scope.** This is a book about a **toy**: a small world built inside a computer, and what happened
> when we pointed real tests at it. Nothing here is a claim about nature. Where a chapter uses a word
> like *vacuum* or *light cone*, the word names a pattern in the model.

The long version of that box is [`FIREWALL.md`](FIREWALL.md). Read it before you quote us.

**Read it online:** <https://zacharyelston.github.io/OurBubble/>

## Three names, one object

**UniForge is the forge.** The engine and the record: where the object is built, and where every claim about it meets a test that was written down before the run. The *uni* is *one* — one lattice, one operator, many sciences. It does not unify the universe; it forges one small world, exactly, and lets you ask it questions.

**The Container is the object.** A finite world made of the least it needs — a point to hold a number, a line to hold a difference — with one dial that gives it geometry. It contains everything that follows. Nothing in it is a claim about nature; The Container is a toy, kept honest.

**Our Bubble is the book.** How a reader comes to understand The Container, told as a journey, standing on the forge's record. *Our*, because we build it together.

UniForge builds The Container. The lab tests it. Our Bubble teaches it.

## How to read it

The reading order is [`chapters/SUMMARY.md`](chapters/SUMMARY.md) — that file is the *only* place
the order is written down, so a chapter carries no number in its name and none in its prose.

The fourteen chapters are narrative. They carry no rung labels and no quotations, on purpose. Everything
a skeptic wants — which registered experiment each chapter rests on, its gate, its data-true figure,
the exact numbers quoted and the file that carries each one, and the commands that regenerate them —
is in [the appendix](chapters/the-simulations.md), one section per chapter, and each chapter closes
with a single link into its own section.

## Reader notes — how someone tells us a section did not land

Every section heading in the built book carries one small link, *Leave a note on this section*, which
opens a prefilled [issue form](.github/ISSUE_TEMPLATE/reader-note.yml) labelled `reader-note`: what
the section said that you read differently, what you expected, anything else. The link arrives with
the chapter, the section, its beat and the page anchor already filled in, so a reader never has to
describe where they were and a maintainer lands on the paragraph they were looking at.

**The limit, plainly: sending a note needs a free GitHub account.** That is the price of the only
version of this we will ship. There is no comment widget, no hosted form and no analytics on any
page — nothing external loads at all, which `check_edition.py --rendered` now refuses on every
build — and the alternative to an account would be handing a reader's words to a third party they
never agreed to.

How it works, for a maintainer:

- the links are **generated at build time** by [`preprocessor.py`](preprocessor.py) from the
  `<!-- beat N -->` markers that already sit under every section heading — nobody maintains a link,
  and no chapter's prose changed to get one;
- the URL format and its parser are one file, [`tools/reader_note.py`](tools/reader_note.py), which
  round-trips itself on every build;
- `python3 check_edition.py --rendered` asserts that every marked section carries exactly **one**
  link, that each link's beat is its own section's marker, and that each URL parses back to that
  page's slug and to the heading id mdBook actually emitted — so a rename or a reorder cannot leave
  a link pointing somewhere else.

## How to build it

You need Python 3 and [mdBook](https://rust-lang.github.io/mdBook/). Nothing else — the record the
book quotes is committed here, so no engine access is required to build or check it.

```sh
make check          # the whole pass: integrity → quotations → build → rendered links
```

or the steps by hand, from the repository root:

```sh
python3 check_edition.py       # the edition against the committed record snapshot
mdbook build                   # regenerates the appendix, then renders into book/
python3 check_edition.py --rendered
```

`make check` is this repository's **tier 0** — the pass to run before every push. It is also exactly
what CI runs.

Building can legitimately modify a tracked file: `chapters/the-simulations.md` is *generated* from
`edition.json` and the reading order on every build, so the appendix cannot go stale between a change
to the record and someone remembering to run a script. `git status` is therefore part of the check —
a clean tree after a build means the appendix and the record agree.

The build also **computes some of the book's numbers**. Chapters 1–4 live on one triangle, one
tetrahedron and the two shapes it is made of, where every number is finger-countable, so rather than
quote them the chapters carry `{{napkin:…}}` tokens that the preprocessor replaces with arithmetic it
runs at build time — the census, the loop sums, the ten-tick table, the octahedron's crossing. Each rendered block says so on its last line. The
arithmetic is exact (rational, no floating point), recomputed twice on every check to prove it is
deterministic, and each token asserts its own invariant — loop sums zero, total conserved — before it
renders anything. The tokens and the scope of their one exemption from the appendix-anchoring rule
are specified in [`EDITION_STANDARD.md`](EDITION_STANDARD.md); the backend is
[`tools/napkin.py`](tools/napkin.py).

## The demos

Chapters 1–4 have a companion page each, under [`demos/`](demos), that **recomputes the chapter's
numbers in the reader's browser** and walks her through the chapter's beats one at a time. They are
plain static pages — one shared vanilla-JS module, one stylesheet, nothing loaded from anywhere — and
they are published beside the book, at `…/OurBubble/demos/`, through the `chapters/demos` symlink
that mdBook copies.

The rule they live under is the book's own, one layer out: **every number a demo shows is one it
computed, it equals the napkin's to the last digit, and no number is typed into a demo by hand.**
`tools/napkin_export.py` dumps the napkin's data (not its prose) to `demos/data/napkin.json` on every
build; `node demos/core.test.mjs` runs the browser's arithmetic and compares it to that export value
by value as exact rational strings, refuses any numeric token the export does not contain on any
surface a reader meets — cell, caption, title, prose, note or drawing — and refuses any digit typed
into the step definitions at all. Both run inside `make check`, and when node is not installed the
line says `unverified — node absent` rather than passing. What no such check can catch is a number
computed correctly and put in the wrong place; `demos/DEMOS.md` says so rather than implying
otherwise.

[`demos/DEMOS.md`](demos/DEMOS.md) is the full statement: the cross-check, the two drawing
conventions and why the octahedron does not get a net, and how the stills these pages produce are
meant to replace the illustration studies.

## The record contract

**The evidence is produced in another repository.** The lab entries, the gates, the data-true
figures and the predictions file live in the UniForge engine — that is where they are made and where
they are authoritative — and that repository is private.

So the book carries two things: a pin, and a copy.

- [`record.lock`](record.lock) names the engine, one **commit SHA**, and the exact list of record
  files this edition cites or quotes. The path list is derived from `edition.json` **and the
  chapters' own links**, and the checker refuses a lock that has drifted from either.
- [`record/`](record) is the **committed snapshot**: those files, verbatim, copied out of a checkout
  of that commit by [`tools/snapshot_record.sh`](tools/snapshot_record.sh). It is derived, never
  hand-edited, and it is why a reader on the published site can click from a number in the appendix
  straight through to the `eval.md` it came from.

### The two layers, and why there are two

1. **Quotations, against `record/`.** Every declared number is verified verbatim in the snapshot.
   This layer needs nothing but a clone, so it holds identically on a dev box, in CI, and for a
   stranger with no engine access.
2. **Snapshot integrity, against the engine.** A committed copy is, by itself, only a copy — it
   could be edited to agree with the prose and layer 1 would pass against the edit. So whenever the
   engine is reachable ([`tools/fetch_record.sh`](tools/fetch_record.sh) checks the pinned commit
   out into the ignored `.record/`), every snapshotted file is diffed against the real repository at
   that commit, byte for byte, and any drift fails by name.

The checker prints both, on their own lines, every run — including `snapshot integrity: unverified`
when layer 2 could not run. It never lets a green tick imply a check that did not happen.

### Bumping the record

Advancing the book's evidence is a deliberate commit, and it is the only way the evidence moves:

1. edit `sha` in `record.lock` to the new engine commit;
2. `tools/fetch_record.sh` — check the new commit out;
3. `tools/snapshot_record.sh` — re-derive `record/` from it;
4. `python3 check_edition.py` — quotations re-verified, drift reported by file;
5. fix whatever moved, or commit the SHA and the re-derived snapshot together.

All five land in **one** commit. Bumping the pin without re-snapshotting is refused: the snapshot
records the SHA it was taken at, and it must match the lock.

## Layout

| path | what it is |
|---|---|
| `chapters/` | the book — `SUMMARY.md` (the reading order), nine chapters, the generated appendix, and `assets/` (the editorial illustration studies) |
| `theme/` | the edition's CSS |
| `edition.json` | the manifest: per-chapter sources, the appendix's sections, the declared quotations, and the excluded-claims guard with the probe sentences that test it |
| `check_edition.py` | the checker |
| `gen_appendix.py` · `preprocessor.py` | the appendix generator, and the mdBook hook that runs it on every build |
| `record.lock` · `record/` · `tools/fetch_record.sh` · `tools/snapshot_record.sh` | the record contract: the pin, the committed snapshot, and the two scripts that derive it |
| `tools/napkin.py` · `tools/octahedron.py` · `preprocessor.py` | the numbers chapters 1–4 compute at build time, the object the later ones are computed on, and the mdBook hook that runs them |
| `tools/renumber_beats.py` | moves beat numbers through `OUTLINE.md` and every chapter's markers together, when a beat is inserted |
| `demos/` · `tools/napkin_export.py` | the demos: one page per chapter of the napkin world, recomputing its numbers in the reader's browser, and the export they are checked against — `demos/DEMOS.md` |
| `CANON.md` · `tools/canon.py` | the one labeling of the tetrahedron, derived from the napkin, and the only code that draws its net |
| `tools/check.sh` · `Makefile` | tier 0 |
| `ART_DIRECTION.md` · `EDITION_STANDARD.md` · `LEGACY_MIGRATION.md` | the illustration contract, the writing contract, and what was and was not carried over from each earlier source |
| `FIREWALL.md` | scope of claims |
| `CONTINUUM.md` | the agent-lane ledger for this repository |
| `PROVENANCE.md` | where this edition came from |

`book/` (the rendered site) and `.record/` (the fetched engine) are build outputs and are not
committed. `record/` **is** committed — it is the evidence, and `record/README.md` says what it is.

## Publishing

`.github/workflows/pages.yml` builds the book on every push to `main` and publishes it to GitHub
Pages at <https://zacharyelston.github.io/OurBubble/>. It runs the same `tools/check.sh` that
`make check` runs — one implementation, so CI and the pre-push pass cannot drift.

**The published site carries the record.** `chapters/record` is a symlink to `record/`, so mdBook
copies the snapshot into the built book, and every citation in the appendix is a live link: the lab
entry, its `spec.md` and `eval.md`, the gate, the data-true figure. The `--rendered` check confirms
every one of them resolves before anything is deployed. A reader needs no access to the engine, and
the engine stays private.

One caveat worth stating plainly: CI can only run the **snapshot-integrity** layer if a
`RECORD_TOKEN` secret exists (a fine-grained PAT with Contents:read on the engine). Without one the
quotation gate still runs in full, and the workflow says `snapshot integrity unverified —
RECORD_TOKEN not set` in the job summary of every run rather than implying it checked.

## Working on it

The lane ledger is [`CONTINUUM.md`](CONTINUUM.md). The binding writing rules are
[`EDITION_STANDARD.md`](EDITION_STANDARD.md); the illustration rules are
[`ART_DIRECTION.md`](ART_DIRECTION.md). Every owner-judged draft gets a proof-reader pass before it
reaches the owner — the loop is in [`.claude/skills/proof-reader/`](.claude/skills/proof-reader).
