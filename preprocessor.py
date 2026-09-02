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
import re
import sys

import gen_appendix
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent / "tools"))
import napkin  # noqa: E402  (needs the path above)
import napkin_export  # noqa: E402  (needs the path above)

# `{{napkin:NAME}}` — the Rewrite lane writes these in chapter prose; this replaces each with the
# arithmetic run at build time. The token is the whole contract between the two lanes: the lane that
# writes chapters never touches this file, and this file never touches a chapter's prose.
NAPKIN = re.compile(r"\{\{napkin:([a-z0-9_]+)\}\}")


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


def expand_napkins(item, report: list) -> None:
    """Replace every `{{napkin:…}}` in the book tree with its computed block.

    Walks the whole tree rather than a named chapter, because any chapter may use a token and the
    preprocessor should not need telling which. An unknown name is fatal: a typo that silently left
    `{{napkin:tetra_conts}}` in the prose would ship a page with a brace-literal in it, and the
    checker's unresolved-token rule would then be the *second* line of defence rather than the only
    one.
    """
    if not isinstance(item, dict):
        return
    chapter = item.get("Chapter")
    if chapter is None:
        return
    content = chapter.get("content") or ""
    if NAPKIN.search(content):
        def replace(match):
            name = match.group(1)
            if name not in napkin.TOKENS:
                raise KeyError(
                    f"unknown napkin token {{{{napkin:{name}}}}} in "
                    f"{chapter.get('path') or '?'} — known tokens: "
                    f"{', '.join(sorted(napkin.TOKENS))}"
                )
            report.append((chapter.get("path") or "?", name))
            return napkin.render(name)

        chapter["content"] = NAPKIN.sub(replace, content)
    for child in chapter.get("sub_items", []):
        expand_napkins(child, report)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "supports":
        return 0  # every renderer: the substitution is renderer-agnostic

    _context, book = json.load(sys.stdin)

    # The demos' oracle, written on every build for exactly the reason the appendix is: it puts
    # `demos/data/napkin.json` under `git status`, so a change to the napkin that moves a number a
    # demo shows becomes a dirty tree rather than a page that quietly disagrees with the book.
    # `check_edition.py` compares the committed copy against a fresh derivation and fails by name.
    if napkin_export.write():
        print(
            f"napkin export: rewrote {napkin_export.TARGET.name} — the napkin's numbers moved",
            file=sys.stderr,
        )

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

    # The napkin pass runs after the appendix substitution so a generated page could carry a token
    # too. Failure is loud for the same reason the appendix's is: a build that quietly renders an
    # unexpanded token has published a brace-literal where a number should be.
    report: list = []
    try:
        for item in book_items(book):
            expand_napkins(item, report)
    except (KeyError, AssertionError) as failure:
        print(f"napkin preprocessor: {failure}", file=sys.stderr)
        return 1

    if report:
        counts = ", ".join(
            f"{name}×{sum(1 for _, n in report if n == name)}"
            for name in sorted({n for _, n in report})
        )
        print(f"napkin preprocessor: computed {len(report)} block(s) — {counts}", file=sys.stderr)

    json.dump(book, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
