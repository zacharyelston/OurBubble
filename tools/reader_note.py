#!/usr/bin/env python3
"""The reader's note link: one URL builder, and the parser that reads it back.

A reader who is not Git-native has, until now, had no way to say *this section did not land* short of
a clone, a branch and a diff. This module is the whole of the mechanism that changes that: every
section heading in the built book carries one small link that opens a prefilled GitHub issue form.
There is no JavaScript in it, nothing external loads on the page, and the link works with the
browser's own **open in new tab** — a link is a link.

**Why the builder and the parser live in the same file.** `preprocessor.py` writes these links at
build time; `check_edition.py --rendered` reads them back out of the built HTML and asserts each one
still points at the section it sits under. Two implementations of one URL format is exactly the
arrangement where a checker slowly starts agreeing with a bug, so `build()` and `parse()` are
written next to each other and `self_test()` proves they round-trip on every run.

The pieces of a link, and where each one comes from:

* **the chapter title** — the chapter's `# H1`, as written in the source;
* **the section heading** — the `##` heading the link sits under;
* **the beat** — the `<!-- beat slug.n -->` marker under that heading, which the outline and
  `tools/beat_coverage.py` already treat as the section's identity. Since issue #77 that id is the
  chapter's own slug and the beat's place inside it, so a note filed on `make-it-move.3` still names
  the same beat after the next chapter is inserted anywhere in the book;
* **the page** — the published URL plus mdBook's own heading anchor, so a maintainer opening the
  issue lands on the paragraph the reader was looking at.

**The anchor is a port, and it is the fragile part.** mdBook derives a heading's `id` itself
(`normalize_id`: keep alphanumerics, `-` and `_`, turn whitespace into `-`, drop everything else,
lowercase). `anchor()` below reimplements that, and a reimplementation drifts. So it is not trusted:
the rendered check compares every link's anchor against the `id` mdBook actually emitted on the
heading the link sits under, which turns a drift into a failed build rather than into a link that
scrolls nowhere.

**The limit, stated here because it is stated to the reader too.** Sending a note needs a free GitHub
account. This turns a contribution into one click instead of a checkout; it does not make it
accountless, and no page in this book will ask a reader for anything more than that.

FIREWALL: this is tooling for a book about a toy DEC lattice; nothing here is a claim about nature.
"""

from __future__ import annotations

import re
from typing import Dict, Optional
from urllib.parse import parse_qs, quote, urlencode, urlsplit

# The two ends of the arrangement, written down once. `check_edition.py` cross-checks both against
# what the repository already says about itself — `book.toml`'s `git-repository-url` and the
# published address in `README.md` — so neither can be quietly repointed here.
REPO_URL = "https://github.com/zacharyelston/OurBubble"
BOOK_URL = "https://zacharyelston.github.io/OurBubble"
NEW_ISSUE_URL = f"{REPO_URL}/issues/new"

TEMPLATE = "reader-note.yml"
LABEL = "reader-note"

# The link's visible words. Deliberately a sentence rather than an icon: a reader should not have to
# guess what a glyph beside a heading would do.
LINK_TEXT = "Leave a note on this section"

# `chapter · heading · beat slug.n` and `note · chapter · heading`. The separator is a middle dot with
# spaces, which is the book's own; a heading containing one would make `parse()` fail loudly rather
# than silently mis-split, and a failed build is the outcome we want from that.
SEP = " · "
BEAT_SUFFIX = re.compile(
    r"^(?P<rest>.*?)" + re.escape(SEP) + r"beat (?P<beat>[a-z0-9][a-z0-9-]*\.\d+)$", re.DOTALL)

# One rendered link, as it appears in the built HTML.
LINK_HTML = re.compile(
    r'<a class="section-note-link" href="(?P<href>[^"]+)"[^>]*>(?P<text>[^<]*)</a>'
)

# The `<!-- beat slug.n -->` marker, in source or in a built page — mdBook passes HTML comments
# through untouched, which is what lets the rendered check read the same marker the source declares.
# One group, and it captures the whole id: a caller reading `findall` gets a list of ids rather than
# a list of pairs.
BEAT_MARKER = re.compile(r"<!--[ \t]*beat[ \t]+([a-z0-9][a-z0-9-]*\.\d+)[ \t]*-->")

# Markdown that a heading may legitimately carry and a title should not: emphasis and code spans.
# `## The word is *carries*` must title as `The word is carries`, which is also what mdBook renders
# as the heading's text, so the rendered check can compare the two.
HEADING_MARKUP = re.compile(r"[*_`]+")

# Curly punctuation. `smart-punctuation = true` means the built page says `didn’t` where the source
# says `didn't`; comparing a link built from the source against text read from the page has to
# normalise, and this is the whole of that normalisation.
SMART = {"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"}


def plain(heading: str) -> str:
    """A heading as words: emphasis and code markers gone, whitespace collapsed."""
    return " ".join(HEADING_MARKUP.sub("", heading).split())


def straighten(text: str) -> str:
    """Curly punctuation flattened, so source text and rendered text are comparable."""
    for curly, straight in SMART.items():
        text = text.replace(curly, straight)
    return " ".join(text.split())


def anchor(heading: str) -> str:
    """mdBook's `normalize_id`, ported. See the module docstring on why it is checked, not trusted."""
    out = []
    for character in plain(heading):
        if character.isalnum() or character in "-_":
            out.append(character.lower())
        elif character.isspace():
            out.append("-")
    return "".join(out)


def page_url(slug: str, heading: str) -> str:
    return f"{BOOK_URL}/{slug}.html#{anchor(heading)}"


def title(chapter: str, heading: str) -> str:
    return f"note{SEP}{plain(chapter)}{SEP}{plain(heading)}"


def build(chapter: str, heading: str, beat: str, slug: str) -> str:
    """The prefilled new-issue URL for one section.

    Every field is carried in the query string, which is the only prefill mechanism GitHub issue
    forms have: `template` chooses the form, `labels` files it, `title` names it, and the two
    prefilled inputs (`section`, `page`) tell a maintainer which paragraph a note is about even if
    the reader deletes the link out of the body. `quote` rather than the default `quote_plus`, so a
    space is `%20` and the URL survives being pasted somewhere that does not read `+` as a space.
    """
    query = urlencode(
        {
            "template": TEMPLATE,
            "labels": LABEL,
            "title": title(chapter, heading),
            "section": f"{plain(chapter)}{SEP}{plain(heading)}{SEP}beat {beat}",
            "page": page_url(slug, heading),
        },
        quote_via=quote,
        safe="",
    )
    return f"{NEW_ISSUE_URL}?{query}"


def link_html(chapter: str, heading: str, beat: str, slug: str) -> str:
    """One line of raw HTML, because mdBook treats a multi-line HTML block differently.

    `rel="nofollow noopener"` on principle rather than out of need, and `target="_blank"` so a reader
    mid-chapter does not lose their place to a form.
    """
    return (
        '<div class="section-note">'
        f'<a class="section-note-link" href="{build(chapter, heading, beat, slug)}" '
        f'target="_blank" rel="nofollow noopener">{LINK_TEXT}</a>'
        "</div>"
    )


def parse(href: str) -> Optional[Dict[str, object]]:
    """Read a note URL back into its parts, or `None` if it is not one of ours.

    Strict on purpose. Everything the builder puts in must come back out, in the shape it went in:
    a missing field, a mangled encoding, a title that disagrees with the section field, or a page URL
    that is not this book's are each a `None`, and the caller reports them as a broken link rather
    than shrugging. That strictness is what makes the mutation tests in `self_test()` mean something.
    """
    split = urlsplit(href)
    if f"{split.scheme}://{split.netloc}{split.path}" != NEW_ISSUE_URL:
        return None
    query = parse_qs(split.query, keep_blank_values=True, strict_parsing=False)
    single = {key: values[0] for key, values in query.items() if len(values) == 1}
    if set(single) != {"template", "labels", "title", "section", "page"}:
        return None
    if single["template"] != TEMPLATE or single["labels"] != LABEL:
        return None

    marked = BEAT_SUFFIX.match(single["section"])
    if marked is None:
        return None
    parts = marked.group("rest").split(SEP)
    if len(parts) != 2:
        return None
    chapter, heading = parts

    page = urlsplit(single["page"])
    prefix = urlsplit(BOOK_URL)
    if (page.scheme, page.netloc) != (prefix.scheme, prefix.netloc):
        return None
    if not page.path.startswith(prefix.path) or not page.path.endswith(".html"):
        return None
    slug = page.path[len(prefix.path):].lstrip("/")[: -len(".html")]
    if not slug or "/" in slug:
        return None

    if single["title"] != f"note{SEP}{chapter}{SEP}{heading}":
        return None

    return {
        "chapter": chapter,
        "heading": heading,
        "beat": marked.group("beat"),
        "slug": slug,
        "anchor": page.fragment,
    }


def self_test() -> list:
    """Round-trip, then the mutations — every run, before either caller trusts this file.

    The round trip alone proves very little: a builder and a parser written in one sitting agree with
    each other by construction. What is asserted here is that the parser **refuses** each way the
    link can be wrong, because those refusals are the entire value of the rendered check. Three of
    them are the mutations this work was ratified with (a link dropped, a beat pointed at the wrong
    section, an encoding broken); the rest are their neighbours, pinned so a later edit cannot trade
    one for another.
    """
    failures = []
    chapter, heading, beat, slug = ("The shape between", "The word is *carries*",
                                    "make-it-move.3", "make-it-move")
    href = build(chapter, heading, beat, slug)
    found = parse(href)

    if found is None:
        return ["reader-note self-test: a freshly built link does not parse at all"]
    expected = {
        "chapter": chapter,
        "heading": "The word is carries",
        "beat": beat,
        "slug": slug,
        "anchor": "the-word-is-carries",
    }
    for key, value in expected.items():
        if found[key] != value:
            failures.append(
                f"reader-note self-test: round trip gave {key}={found[key]!r}, expected {value!r}"
            )

    # Nothing raw survives into the query: a space, the separator and the `#` are all encoded.
    for raw in (" ", SEP.strip(), "#"):
        if raw in href.split("?", 1)[1]:
            failures.append(f"reader-note self-test: {raw!r} is unencoded in the query string")

    def refuses(label: str, mutated: str):
        if parse(mutated) is not None:
            failures.append(f"reader-note self-test: the parser accepts a link with {label}")

    # MUTATION — the encoding broken. A raw space (the shape a hand-written link takes) and a
    # double-encoded separator both stop being this URL.
    refuses("a raw space in the title", href.replace("note%20%C2%B7%20", "note "))
    refuses("a double-encoded separator", href.replace("%C2%B7", "%25C2%25B7"))
    # MUTATION — the title and the section field disagree, which is what a link edited on one side
    # of the URL and not the other looks like.
    refuses("a title that disagrees with its section field", href.replace("note%20%C2%B7", "x%20%C2%B7"))
    # the fields themselves
    refuses("no beat in the section field", href.replace("%20%C2%B7%20beat%20make-it-move.3", ""))
    refuses("a book-wide beat number in the section field",
            href.replace("beat%20make-it-move.3", "beat%2037"))
    refuses("the template dropped", href.replace(f"template={TEMPLATE}&", ""))
    refuses("the wrong label", href.replace(f"labels={LABEL}", "labels=bug"))
    refuses("a page on another site", href.replace(quote(BOOK_URL, safe=""), "https%3A%2F%2Felsewhere.example"))
    refuses("a page that is not a chapter page", href.replace("make-it-move.html", "make-it-move"))
    refuses("an extra field nobody wrote", href + "&assignees=someone")
    refuses("a different issues endpoint", href.replace("/issues/new", "/issues/new/choose"))

    # A heading carrying the separator itself would mis-split, so it must fail rather than parse
    # into the wrong pieces. Stated as a test because it is a stated limit of the format.
    odd = build(chapter, "One · two · three", beat, slug)
    refuses("a heading containing the separator", odd)

    return failures


if __name__ == "__main__":
    problems = self_test()
    print("\n".join(problems) if problems else "reader-note: self-test clean")
    raise SystemExit(1 if problems else 0)
