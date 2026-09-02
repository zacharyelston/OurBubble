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
