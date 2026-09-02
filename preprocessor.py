#!/usr/bin/env python3
"""mdBook preprocessor: rebuild the Simulations appendix from the record on every build.

This is what makes the appendix a *generated* artifact rather than a maintained one, and it is why
the book can say it assembles the appendix from the record each time it is built. Before this,
`gen_appendix.py` existed but nothing ran it, so the claim was aspirational — a proofread caught
that (2026-09-01, delta read of #347).

mdBook's contract, in full:

* called as `preprocessor.py supports <renderer>` — exit 0 to opt in, non-zero to be skipped;
* otherwise `[context, book]` arrives as JSON on stdin, and the (possibly modified) `book` must be
  the only thing on stdout.

What this does with that: regenerate the appendix, **write it to disk** so the committed copy stays
in step, and substitute the fresh text into the book being built. Writing the file is deliberate — it
puts the appendix under the same discipline the project applies to run data, so `git status` is the
check. Build the book and the working tree stays clean, or the record moved and you want to know.

Failure is loud on purpose: if regeneration raises, this exits non-zero and the build stops rather
than quietly rendering a stale appendix, which is the one outcome the whole arrangement exists to
prevent.
"""

from __future__ import annotations

import json
import sys

import gen_appendix


def substitute(item, slug: str, markdown: str) -> bool:
    """Replace the appendix chapter's content in mdBook's book tree. True if it was found.

    Defensive about two things this version of mdBook taught us: a book item may be a bare string
    (`"Separator"`) rather than a mapping, and the list of items has lived under both `items` and
    `sections` across versions.
    """
    if not isinstance(item, dict):
        return False
    chapter = item.get("Chapter")
    if chapter is None:
        return False
    path = chapter.get("path") or ""
    if path.rsplit("/", 1)[-1] == f"{slug}.md":
        chapter["content"] = markdown
        return True
    return any(substitute(child, slug, markdown) for child in chapter.get("sub_items", []))


def book_items(book: dict) -> list:
    for key in ("items", "sections"):
        if isinstance(book.get(key), list):
            return book[key]
    return []


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "supports":
        return 0  # every renderer: the substitution is renderer-agnostic

    _context, book = json.load(sys.stdin)
    markdown, changed = gen_appendix.write()
    slug = gen_appendix.TARGET.stem

    if not any(substitute(item, slug, markdown) for item in book_items(book)):
        print(
            f"appendix preprocessor: no chapter named {slug}.md in the book — "
            f"is it still listed in chapters/SUMMARY.md?",
            file=sys.stderr,
        )
        return 1

    if changed:
        print(
            f"appendix preprocessor: regenerated chapters/{slug}.md from the record",
            file=sys.stderr,
        )
    json.dump(book, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
