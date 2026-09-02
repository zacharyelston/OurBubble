# Provenance

## Where this repository came from

Our Bubble was written inside the UniForge engine repository, as `book/our-bubble/`, and moved out
on 2026-09-01 by owner decision: the book is the product, and the engine is the record it stands on.

| | |
|---|---|
| **source repository** | `github.com/zacharyelston/UniForge` (private) |
| **source path** | `book/our-bubble/` |
| **source commit** | `b2759cda18e160327f5c513183579eb826d6738d` (`main`, 2026-09-01) |
| **moved** | 2026-09-01 |

The chapter prose, the illustration studies, the theme, `edition.json`, the checker, the appendix
generator and the three standards documents came across **byte for byte**. What changed is
addressing, and only addressing — see below.

### The pull requests that produced it

Every one of these landed in UniForge before the move; the record commit above contains all of them.

| PR | what it did |
|---|---|
| **#331** | the reader edition itself — nine chapters and the illustration layer |
| **#335** | the Simulations appendix: provenance moved off the narrative and onto a boundary |
| **#336** | the narrative rewrite, chapter by chapter |
| **#345 / #347** | the whole-book pass and the provenance tone pass |
| **#348** | the last commit on `main` before the move |

The lane that produced it is recorded in UniForge's `CONTINUUM.md` as the **Our Bubble** lane, taken
over by the Rewrite lane's agent at the owner's request on 2026-09-01.

### Editorial ancestry

The narrative *voice* — the shadow motif, the welcoming register, the shared sense of discovery — is
adapted from the legacy `UniForgeCore/docs/bubble` manuscript at commit `8cc4d10` (2025-12-11). Its
scientific claims were **not** imported, and the excluded ones are enforced mechanically by the
checker's guard. What was and was not carried over is recorded in
[`LEGACY_MIGRATION.md`](LEGACY_MIGRATION.md).

## What changed in the move

Content did not change. Addressing did, because the evidence is now in a different repository:

1. **Record links.** Chapters cited the record as `../../../<path>` — three levels up, out of
   `book/our-bubble/chapters/` and into the engine's working tree. They now cite
   `../.record/<path>`: the pinned engine checkout. The prefix is defined in exactly one place for
   the appendix (`gen_appendix.py`'s `rel()`) and appears literally in thirteen narrative links.

   The depth is deliberate. `chapters/` (source) and `book/` (rendered) are both one level below the
   repository root, so the *same* link text resolves in the Markdown and in the built page — which is
   what lets the rendered check follow real files rather than trusting the build.

2. **The checker's roots split in two.** `REPO_ROOT` used to mean both "the repository these files
   live in" and "the repository the evidence lives in", because they were the same repository. They
   are now `EDITION_DIR` and `RECORD_DIR`, and every declared entry, gate, figure, standard and
   quotation source resolves against `RECORD_DIR`.

3. **The record contract was added** — `record.lock`, `tools/fetch_record.sh`, and
   `check_record()` in the checker, which refuses to proceed unless `.record/` exists, is the commit
   the lock pins, and the lock's path list is what `edition.json` and the chapters actually depend on.

4. **Build commands.** `python3 book/our-bubble/check_edition.py` → `python3 check_edition.py`,
   `mdbook build book/our-bubble` → `mdbook build`, with `tools/fetch_record.sh` in front. Updated in
   `edition.json`, in the reproduce chapter, and in the checker's own messages. The appendix's
   per-rung `cargo` commands now say which root they mean, because it is no longer this one.

5. **Firewall and README** were written for this repository — a reader's `FIREWALL.md` rather than
   the engine's, and a README that leads with what the book is.

6. `mdbook build` at the repository root is the one-command build; `book.toml` moved to the root and
   its `git-repository-url` now points here.

## The audit

The move is validated by the checker's own output being **identical** on both sides. In UniForge at
`b2759cd`:

```
Our Bubble edition check passed: 10 chapters + the appendix, 35 record quotations anchored in the
appendix, 13 exclusion probes refused, all links, hand-offs, slug bridges and derived section
numbers valid.
```

and here, against the fetched record, character for character the same line — with `--rendered`
adding `in source and rendered output` exactly as before. The 35 quotations are re-verified against
`.record/`, so that count passing means the same 35 strings are still carried by the same files at
the pinned commit.

## The record snapshot (2026-09-01, after the move)

The move left one thing broken for the reader it was meant to serve: the appendix could name the
file behind every number and then not let anyone open it, because the engine is private and stays
private (owner decision, 2026-09-01). A citation you cannot follow is a citation asking for trust.

So the cited files were committed here, in `record/` — verbatim, copied out of a checkout of the
pinned commit by `tools/snapshot_record.sh`, never hand-edited. 54 cited paths, 150 files of
evidence, plus a generated view layer (listed in `record/.generated`) whose only job is to make the
links land on the published site.

What changed with it:

1. **The checker grew a second layer.** Quotations verify against `record/`, which every clone has —
   so the quotation gate no longer depends on engine access at all. A separate integrity layer
   diffs `record/` against the engine at the pinned commit whenever the engine is reachable, because
   a committed copy that only ever checks itself proves consistency, not truth. Both statuses print
   on their own lines, every run.
2. **Record links became `record/…`**, with `chapters/record` a symlink to it. One spelling now
   resolves in the repository browser, in the local render (mdBook copies the tree to
   `book/record/`), and on the published site — 190 record links in the built book, none dead.
3. **The reproduce path lost its caveat.** `tools/fetch_record.sh` is no longer a prerequisite for
   checking the book; the chapter says so.
4. **Bumping the record gained a step** — fetch, *re-snapshot*, check — and the checker refuses a
   pin that does not match the snapshot's stamp, so the two cannot come apart.

An audit during this work found the integrity check's first implementation excluding thirteen real
engine files (`data/.gitkeep`) from the comparison, because it told record from scaffolding by
guessing at filenames. The generator now writes down what it generated. The check passed either
way; it was simply checking less than it said.
