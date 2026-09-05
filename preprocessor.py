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

It does two more things to the book on the way past, both of them additions to a page rather than
edits to prose: it renders every `{{napkin:…}}` token from the vendored
engine, and it puts one **reader's note link** at each section heading. The note pass is driven by the `<!-- beat slug.n -->` marker that already sits
under every section heading, which is the only place in the book where a section's heading and its
beat number are written down together — so a section that is renamed, renumbered or moved carries a
correct link without anyone maintaining one. `tools/reader_note.py` holds the URL format;
`check_edition.py --rendered` reads every link back out of the built HTML and asserts it still points
at the section it sits under.

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
import engine  # noqa: E402  (needs the path above)
import napkin  # noqa: E402  (needs the path above)
import reader_note  # noqa: E402  (needs the path above)

# `{{napkin:NAME}}` — the Rewrite lane writes these in chapter prose; this replaces each with the
# block `tools/napkin.py` renders from the vendored engine (`engine/`, pinned by `engine.lock`).
# The token is the whole contract between the two lanes: the lane that writes chapters never touches
# this file, and this file never touches a chapter's prose.
NAPKIN = re.compile(r"\{\{napkin:([a-z0-9_]+)\}\}")

# The chapter's own title, and its section headings. Used by the reader-note pass below, which adds
# HTML *around* the prose and never inside it — the same contract the napkin token has, read from the
# other direction: the lane that writes chapters writes only the `<!-- beat slug.n -->` markers it
# already writes, and this file turns each one into a link.
CHAPTER_TITLE = re.compile(r"^# +(.+?)\s*$", re.M)
SECTION_HEADING = re.compile(r"^## +(.+?)\s*$", re.M)


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


def with_note_links(markdown: str, slug: str, report: list) -> str:
    """One reader's-note link under every section heading that declares a beat. **Pure.**

    Split out of the tree walk so the rule can be exercised on constructed markdown rather than only
    on the book — the shape the rest of this repository's guards are held to.

    Three decisions worth writing down:

    * **The marker is the trigger, not the heading.** A heading with no `<!-- beat slug.n -->`
      under it gets no link, which is what keeps the generated appendix (all headings, no
      markers) out of this and makes the rendered check's rule a two-way one: marked sections carry
      exactly one link, unmarked headings carry none.
    * **The link goes immediately after the heading**, before the marker and the prose, so the
      reader meets it where the section starts and the stylesheet can pull it up beside the heading.
    * **Only the first marker in a section counts.** A second one would be a defect in the prose,
      not a second link — and the rendered check refuses a section carrying two markers rather than
      this file guessing which one is meant.
    """
    titled = CHAPTER_TITLE.search(markdown)
    if titled is None:
        return markdown  # no `# H1`: not a chapter page, so there is no chapter title to carry
    chapter = titled.group(1)

    headings = list(SECTION_HEADING.finditer(markdown))
    out: list = []
    cursor = 0
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        marked = reader_note.BEAT_MARKER.search(markdown[heading.end():end])
        out.append(markdown[cursor:heading.end()])
        cursor = heading.end()
        if marked is None:
            continue
        beat = marked.group(1)
        out.append("\n\n" + reader_note.link_html(chapter, heading.group(1), beat, slug))
        report.append((slug, beat))
    out.append(markdown[cursor:])
    return "".join(out)


def add_note_links(item, report: list) -> None:
    """Walk the book and let `with_note_links` at every page that has a source path.

    The path is what supplies the slug, and the slug is what makes the link point at the published
    page: a page mdBook synthesised with no path of its own cannot be linked to, so it is skipped
    rather than linked wrongly.
    """
    if not isinstance(item, dict):
        return
    chapter = item.get("Chapter")
    if chapter is None:
        return
    path = chapter.get("path") or ""
    leaf = path.rsplit("/", 1)[-1]
    if leaf.endswith(".md"):
        chapter["content"] = with_note_links(
            chapter.get("content") or "", leaf[: -len(".md")], report
        )
    for child in chapter.get("sub_items", []):
        add_note_links(child, report)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "supports":
        return 0  # every renderer: the substitution is renderer-agnostic

    _context, book = json.load(sys.stdin)

    # The demos' copy of the engine's payload, written on every build for exactly the reason the
    # appendix is: it puts `demos/data/napkin.json` under `git status`, so an engine bump that moves
    # a number a demo shows becomes a dirty tree rather than a page that quietly disagrees with the
    # book. `check_edition.py` compares the committed copy against the vendored engine and against
    # the Python oracle, and fails by name.
    if engine.publish_demo_data():
        print(
            "napkin export: rewrote demos/data/napkin.json from engine/ — the engine's numbers "
            "moved",
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

    # The reader's note links, last: they are added around the prose, so they neither hide a napkin
    # token from the pass above nor get scanned as one. The module's own round-trip test runs first —
    # a URL format that cannot be read back is not one to write into fourteen pages.
    broken = reader_note.self_test()
    if broken:
        print("reader-note preprocessor: " + "; ".join(broken), file=sys.stderr)
        return 1
    notes: list = []
    for item in book_items(book):
        add_note_links(item, notes)
    if notes:
        print(
            f"reader-note preprocessor: {len(notes)} section link(s) across "
            f"{len({slug for slug, _ in notes})} page(s)",
            file=sys.stderr,
        )

    json.dump(book, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
