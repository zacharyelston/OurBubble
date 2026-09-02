# Our Bubble

**A book about a small world we built inside a computer, and what happened when we pointed real
tests at it.**

Nine chapters and an appendix. It starts with a child noticing her shadow and a Greek who knew what
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

The nine chapters are narrative. They carry no rung labels and no quotations, on purpose. Everything
a skeptic wants — which registered experiment each chapter rests on, its gate, its data-true figure,
the exact numbers quoted and the file that carries each one, and the commands that regenerate them —
is in [the appendix](chapters/the-simulations.md), one section per chapter, and each chapter closes
with a single link into its own section.

## How to build it

You need Python 3 and [mdBook](https://rust-lang.github.io/mdBook/), plus read access to the record
repository (see below).

```sh
make check          # the whole pass: fetch record → check → build → check the built pages
```

or the steps by hand, from the repository root:

```sh
tools/fetch_record.sh          # check the pinned engine commit out into .record/
python3 check_edition.py       # the edition against the record
mdbook build                   # regenerates the appendix, then renders into book/
python3 check_edition.py --rendered
```

`make check` is this repository's **tier 0** — the pass to run before every push. It is also exactly
what CI runs.

Building can legitimately modify a tracked file: `chapters/the-simulations.md` is *generated* from
`edition.json` and the reading order on every build, so the appendix cannot go stale between a change
to the record and someone remembering to run a script. `git status` is therefore part of the check —
a clean tree after a build means the appendix and the record agree.

## The record contract

**The evidence is not in this repository.** It lives in the UniForge engine — the lab entries, the
gates, the data-true figures, the predictions file — and it stays there, because that is where it is
produced and where it is authoritative.

What this repository holds instead is a pin:

- [`record.lock`](record.lock) names the record repository, one **commit SHA**, and the exact list of
  record files this edition cites or quotes. The path list is derived from `edition.json` and the
  chapters' own links, and the checker refuses a lock that has drifted from either.
- [`tools/fetch_record.sh`](tools/fetch_record.sh) shallow-fetches that single commit into the
  ignored `.record/`.
- [`check_edition.py`](check_edition.py) verifies **every declared quotation verbatim against
  `.record/<path>`** — never against anything in this repository. There is nothing here to quote.

So a number in this book is true in a checkable sense: it is carried, character for character, by a
named file at a named commit of the engine.

### Bumping the record

Advancing the book's evidence is a deliberate commit, and it looks like this:

1. edit `sha` in `record.lock` to the new UniForge commit;
2. `tools/fetch_record.sh` — re-checks `.record/` out at the new commit;
3. `python3 check_edition.py` — every quotation re-verified against it;
4. fix whatever moved, or, if nothing moved, commit the one-line SHA change on its own.

Step 3 is the point. If a bump changes a number the book quotes, the check fails by name and tells
you which file stopped carrying it. A record bump that goes green is a record bump you can trust.

## Layout

| path | what it is |
|---|---|
| `chapters/` | the book — `SUMMARY.md` (the reading order), nine chapters, the generated appendix, and `assets/` (the editorial illustration studies) |
| `theme/` | the edition's CSS |
| `edition.json` | the manifest: per-chapter sources, the appendix's sections, the declared quotations, and the excluded-claims guard with the probe sentences that test it |
| `check_edition.py` | the checker |
| `gen_appendix.py` · `preprocessor.py` | the appendix generator, and the mdBook hook that runs it on every build |
| `record.lock` · `tools/fetch_record.sh` | the record contract |
| `tools/check.sh` · `Makefile` | tier 0 |
| `ART_DIRECTION.md` · `EDITION_STANDARD.md` · `LEGACY_MIGRATION.md` | the illustration contract, the writing contract, and what was and was not carried over from the legacy manuscript |
| `FIREWALL.md` | scope of claims |
| `CONTINUUM.md` | the agent-lane ledger for this repository |
| `PROVENANCE.md` | where this edition came from |

`book/` (the rendered site) and `.record/` (the fetched engine) are build outputs and are not
committed.

## Publishing

`.github/workflows/pages.yml` builds the book on every push to `main` and publishes it to GitHub
Pages at <https://zacharyelston.github.io/OurBubble/>. It runs the same `tools/check.sh` that
`make check` runs — one implementation, so CI and the pre-push pass cannot drift.

**Two honest caveats, while the engine record is a private repository.**

1. CI can only fetch the record if a `RECORD_TOKEN` secret exists (a fine-grained PAT with
   Contents:read on UniForge). Without one the checker cannot run at all, and the workflow builds
   and publishes while saying so, loudly, in the job summary of every run. It does not pretend to
   have checked. Set the secret — or make the record repository public — and the quotation check
   becomes a publish gate with no other change.
2. The published site does not carry the record, so the appendix's links into `.record/…` — the lab
   entries, the gates, the data-true figures — resolve only for a reader who has fetched it. A
   reader on the public site can see exactly which file each number comes from, and cannot yet click
   through to it.

## Working on it

The lane ledger is [`CONTINUUM.md`](CONTINUUM.md). The binding writing rules are
[`EDITION_STANDARD.md`](EDITION_STANDARD.md); the illustration rules are
[`ART_DIRECTION.md`](ART_DIRECTION.md). Every owner-judged draft gets a proof-reader pass before it
reaches the owner — the loop is in [`.claude/skills/proof-reader/`](.claude/skills/proof-reader).
