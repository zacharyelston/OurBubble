#!/usr/bin/env python3
"""Validate the Our Bubble reader edition against its current evidence sources."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


EDITION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EDITION_DIR / "tools"))

import reader_note  # noqa: E402  (needs the path above)

# THE RECORD, IN TWO LAYERS.
#
# The evidence is a different repository — the UniForge engine — pinned by SHA in `record.lock`, and
# it is private. That left the book in an awkward position: it could tell a reader which file every
# number came from and then not let them open it. So the cited files are **committed here**, in
# `record/`, copied verbatim out of a checkout of the pinned commit.
#
#   RECORD  = `record/`   the committed snapshot. Always present, in every clone and on the
#                         published site. **Quotations are verified against this**, so the
#                         quotation gate never depends on engine access.
#   FETCHED = `.record/`  a checkout of the pinned commit, when someone can reach the engine.
#                         Used for one thing: proving `record/` still equals it, byte for byte.
#
# The split is what keeps the snapshot honest. On its own a committed copy is just a copy — it could
# be edited to say anything, and the quotation check would happily pass against the edit. The
# integrity layer is what makes it evidence: whenever the engine is reachable, every snapshotted
# path is diffed against the real repository at the pinned commit, and any drift fails loudly. When
# it is not reachable the check says so rather than implying it ran.
RECORD_LOCK = EDITION_DIR / "record.lock"
RECORD_DIR = EDITION_DIR / "record"
FETCHED_DIR = EDITION_DIR / ".record"

# The commit the snapshot was taken at, written by `tools/snapshot_record.sh`. The scaffolding it
# generates alongside is listed in `record/.generated` and excluded from the comparison.
SNAPSHOT_STAMP = ".snapshot-sha"
MANIFEST_PATH = EDITION_DIR / "edition.json"
SUMMARY_PATH = EDITION_DIR / "chapters" / "SUMMARY.md"
APPENDIX_FILE = "chapters/the-simulations.md"
RENDER_DIR = EDITION_DIR / "book"

MARKDOWN_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
HTML_LINK = re.compile(r"(?:href|src)=[\"']([^\"']+)[\"']")
SUMMARY_LINK = re.compile(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", re.MULTILINE)
WORD = re.compile(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+(?:[’'][A-Za-zÀ-ÖØ-öø-ÿ0-9]+)?")
SENTENCE_END = re.compile(r"[.!?]+(?:[\"'”’)]*)\s+")
BOLD_NUMBER = re.compile(r"\*\*([^*\n]*\d[^*\n]*)\*\*")

# `{{napkin:NAME}}` — a token the Rewrite lane writes in chapter prose for the build to replace with
# arithmetic it runs itself (`tools/napkin.py`). Two rules follow from that, both below: one left
# unexpanded is a published brace-literal, and the digits inside an expanded one are computed rather
# than quoted, so they answer to a different rule than the rest of the prose.
NAPKIN_TOKEN = re.compile(r"\{\{napkin:([a-z0-9_]+)\}\}")
NAPKIN_SPAN = re.compile(r"<!--\s*napkin:([a-z0-9_]+)\s*-->.*?<!--\s*/napkin:\1\s*-->", re.DOTALL)
RENDERED_BOLD = re.compile(r"<strong>(.*?)</strong>", re.DOTALL)
TAG = re.compile(r"<[^>]+>")


def forbidden_hits(
    text: str,
    phrases: Sequence[str],
    patterns: Sequence[Dict[str, str]],
) -> List[str]:
    """Every excluded-legacy-claim hit in `text`, as human-readable reasons.

    Two layers, because one is not enough. **Phrases** catch the legacy manuscript's claims as it
    actually worded them, verbatim. **Patterns** catch the same claims *paraphrased* — which a
    mutation test showed the phrase list alone does not: rewriting "four faces = four forces" as
    "its four faces are the four forces" walked straight through. A firewall check that only
    recognises one spelling of a claim is a spell-checker, not a firewall.
    """
    lowered = text.casefold()
    hits: List[str] = []
    for phrase in phrases:
        if phrase.casefold() in lowered:
            hits.append(f"unsupported legacy phrase present: {phrase!r}")
    for rule in patterns:
        pattern = str(rule["pattern"])
        found = re.search(pattern, lowered, flags=re.IGNORECASE)
        if found:
            hits.append(
                f"unsupported legacy claim present ({rule.get('why', 'excluded')}): "
                f"{found.group(0)!r}"
            )
    return hits


def self_test(manifest: Dict[str, object], errors: List[str]) -> None:
    """Prove the exclusion guard bites, on probe texts declared in the manifest.

    Without this, the forbidden list is untested code that only ever runs against text written to
    satisfy it. Each probe is a sentence the edition must refuse; if any probe passes the guard, the
    guard has a hole and this fails rather than the hole being discovered by a reader.
    """
    phrases = list(manifest["forbidden_chapter_phrases"])
    patterns = list(manifest.get("forbidden_chapter_patterns", []))
    probes = list(manifest.get("forbidden_probe_texts", []))
    if not probes:
        errors.append("self-test: no forbidden_probe_texts declared, so the guard is untested")
        return
    for probe in probes:
        if not forbidden_hits(str(probe), phrases, patterns):
            errors.append(f"self-test: the exclusion guard does NOT catch {probe!r}")
    # …and the guard must not fire on the edition's own text (checked by the chapter pass, but a
    # pattern that matched everything would satisfy the probes above while being useless).
    benign = [
        "This book does not try to infer the shape of the universe.",
        "We did not measure the universe. We inspected one constructed object.",
        "The lattice is a toy, and its exponents are dimensionless.",
    ]
    for sentence in benign:
        stray = forbidden_hits(sentence, phrases, patterns)
        if stray:
            errors.append(f"self-test: the guard false-positives on {sentence!r}: {stray}")


# A retired phrasing is compared on its WORDS. Everything else about a sentence — where the lines
# break, which half is bold, whether the comma became an em dash, whether part of it sits inside a
# link — is presentation, and every one of those walked past the first two versions of this while a
# reader read the retired sentence unchanged (a proofreader, rounds 2 and 3, 2026-09-04).
LINK_TARGET = re.compile(r"\]\([^)]*\)")
NOT_WORD = re.compile(r"[^0-9a-z]+")


def flattened(text: str) -> str:
    """A string as its lowercase words, single-spaced: markup, punctuation and line breaks gone.

    Prose in `chapters/` is hard-wrapped at about a hundred columns and hand-offs carry bold and
    links, so a sentence long enough to be worth refusing is a sentence that will be broken across
    lines and marked up in the middle. Matching the raw file therefore catches the phrase only in a
    shape the chapters never have: a proofreader put a retired hand-off back wrapped (round 2), then
    put it back with one bolded word, one italic, one em dash for a comma, and part of it inside a
    link (round 3) — and each of those built green while the page read exactly as before.

    **What is left, stated because a denylist's limit is only a limit when it is written down.** The
    same sentence *reworded* passes, and always will: this refuses the sentences somebody wrote
    down, in any punctuation and any markup, not the idea behind them.
    """
    return NOT_WORD.sub(" ", LINK_TARGET.sub("", text).casefold()).strip()


def retired_hits(text: str, retired: Sequence[Dict[str, str]]) -> List[str]:
    """Every retired phrasing present in `text`, as human-readable reasons. **Pure.**"""
    flat = flattened(text)
    return [f"carries a retired phrasing ({rule.get('why', 'moved')}): {rule['phrase']!r}"
            for rule in retired if flattened(str(rule["phrase"])) in flat]


def check_retired_phrasings(manifest: Dict[str, object], order: Sequence[str],
                            errors: List[str]) -> None:
    """Refuse a sentence that was only true of a position the chapter no longer holds.

    A chapter that moves keeps every sentence it had, including the ones that only made sense where
    it used to sit. Tranche E moved the history chapter from last-but-one to second, and its opening
    — "You have just watched an instrument refuse a law its owners committed to" — was rewritten by
    hand. A proofreader (2026-09-04, §2b) put the old opening back at the top of the now-second
    chapter and tier 0 stayed green: the exact defect the move existed to fix built clean, so the
    next chapter move would re-create it with only a reader to catch it.

    Checking that the *new* sentence is present cannot close that, because the old one is present
    too — the writing contract's rule 4, on a hand-off. So the old ones are refused, in every
    chapter, by their own words — matched on the words alone, so wrapping, markup and punctuation
    cannot smuggle one back (see `flattened`). The list doubles as an audit trail: it says what the
    book used to say, and where it used to make sense.

    **Each phrasing carries its own probe, and the probe is tested against that phrasing alone.**
    The first version asked only that every probe hit *some* rule, and a proofreader replaced all
    four probes with four copies of one of them: green, and the pass line still said each phrasing
    was proved by its own probe. A probe that proves a rule other than its own proves nothing about
    that rule, and the report line said otherwise, which is the headline defect exactly.

    **What it cannot see, because a limit is only a limit when it is written down.** It reads
    `chapters/*.md` and nothing else — not `OUTLINE.md`, not the titles and notes in `edition.json`
    that render into the appendix, not `demos/`. And it refuses only the sentences somebody thought
    to declare: a hand-off nobody wrote down here is still the writer's job. `EDITION_STANDARD.md`
    says the same, beside the exclusion denylist's limit.
    """
    retired = [dict(rule) for rule in manifest.get("retired_phrasings", [])]
    if not retired:
        errors.append("retired phrasings: none declared, so a moved chapter's old hand-off is "
                      "refused by nothing")
        return
    for rule in retired:
        probe = str(rule.get("probe", ""))
        if not probe:
            errors.append(f"retired phrasings: {rule['phrase']!r} carries no probe, so nothing "
                          f"shows it still bites")
        elif not retired_hits(probe, [rule]):
            errors.append(f"self-test: the retired-phrasing guard does NOT catch its own probe for "
                          f"{rule['phrase']!r}")
    for slug in order:
        path = EDITION_DIR / "chapters" / f"{slug}.md"
        if not path.exists():
            continue
        for hit in retired_hits(path.read_text(encoding="utf-8"), retired):
            errors.append(f"chapters/{slug}.md: {hit}")


def load_manifest() -> Dict[str, object]:
    with MANIFEST_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


def words(text: str) -> List[str]:
    return WORD.findall(text)


def prose_paragraphs(markdown: str) -> Iterable[str]:
    in_fence = False
    pending: List[str] = []

    def flush() -> Iterable[str]:
        nonlocal pending
        if pending:
            yield " ".join(line.strip() for line in pending)
            pending = []

    for line in markdown.splitlines():
        if line.startswith("```"):
            yield from flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.strip():
            yield from flush()
            continue
        if line.startswith(("#", ">", "- ", "* ", "|", "<", "1. ", "2. ", "3. ", "4. ")):
            yield from flush()
            continue
        pending.append(line)
    yield from flush()


def cleaned_prose(markdown: str) -> str:
    text = re.sub(r"```.*?```", " ", markdown, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return text


def check_links(chapter_path: Path, markdown: str, errors: List[str]) -> None:
    targets = MARKDOWN_LINK.findall(markdown) + HTML_LINK.findall(markdown)
    for raw_target in targets:
        target = raw_target.strip().strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        path_part = target.split("#", 1)[0].split("?", 1)[0]
        if not path_part:
            continue
        resolved = (chapter_path.parent / path_part).resolve()
        if not resolved.exists():
            errors.append(f"{chapter_path.relative_to(EDITION_DIR)}: dead link {target!r}")


def check_rendered(
    order: Sequence[str],
    sections: Dict[str, object],
    errors: List[str],
) -> None:
    if not RENDER_DIR.exists():
        errors.append(
            "rendered book is absent; run `mdbook build` before --rendered"
        )
        return

    for slug in order:
        rendered_path = RENDER_DIR / f"{slug}.html"
        if not rendered_path.exists():
            errors.append(f"rendered chapter is absent: {rendered_path.relative_to(EDITION_DIR)}")
            continue

        html = rendered_path.read_text(encoding="utf-8")

        # Every built page: no token may survive the build.
        check_napkin_tokens(str(rendered_path.relative_to(EDITION_DIR)), html, errors)

        # Narrative pages only — the same scope as the source rule this extends. The appendix's
        # numbers are generated from the manifest and checked verbatim against the record, so the
        # anchoring rule has never applied to it.
        if slug in sections:
            anchored = [
                str(dict(quote)["text"])
                for quote in dict(sections[slug]).get("record_quotes", [])
            ]
            check_rendered_bold(
                str(rendered_path.relative_to(EDITION_DIR)), html, anchored, errors
            )

        for raw_target in HTML_LINK.findall(html):
            target = raw_target.strip().strip("<>")
            if not target or target.startswith(
                ("#", "data:", "http://", "https://", "javascript:", "mailto:")
            ):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if not path_part:
                continue
            resolved = (rendered_path.parent / path_part).resolve()
            if resolved.exists():
                continue
            # mdBook rewrites outbound Markdown source links to .html. The canonical book
            # documents this limitation; accept the link only when the source Markdown exists.
            markdown_source = resolved.with_suffix(".md") if resolved.suffix == ".html" else None
            if markdown_source is not None and markdown_source.exists():
                continue
            errors.append(
                f"{rendered_path.relative_to(EDITION_DIR)}: dead rendered link {target!r}"
            )


def check_napkin_tokens(label: str, text: str, errors: List[str]) -> None:
    """No `{{napkin:…}}` survives into a built page.

    The preprocessor already fails on an unknown token name, so this catches the other half: a token
    the preprocessor never saw — in a file it does not walk, or written with a typo'd delimiter that
    the token pattern misses on one side. Either way the reader would be shown braces where a number
    belongs, which is the single most embarrassing way this arrangement could fail.
    """
    for found in NAPKIN_TOKEN.finditer(text):
        errors.append(
            f"{label}: unresolved napkin token {found.group(0)!r} — the build did not compute it. "
            f"Check the name against tools/napkin.py's TOKENS and that the page is in "
            f"chapters/SUMMARY.md"
        )


def check_rendered_bold(label: str, html: str, anchored: Sequence[str], errors: List[str]) -> None:
    """Emphasised numbers in a **built** narrative page: anchored in the appendix, or computed here.

    The source rule (`check_chapter`) cannot see either side of this. Napkin blocks do not exist in
    the chapter source — they are substituted at build time — so their numbers never reach that rule,
    and the numbers *this* file computes are legitimately not in the appendix: they are checkable on
    a napkin, which is the entire reason they are computed in front of the reader instead of quoted.

    So the exemption lives here and is **bounded by the block**. Everything between a napkin's
    fence comments is exempt; every other emphasised number on the page answers to the appendix
    exactly as before. Excising the spans first — rather than allow-listing values — is what keeps
    the boundary honest: a computed `0` cannot license an unanchored `0` three paragraphs later.
    """
    outside = NAPKIN_SPAN.sub(" ", html)
    for found in RENDERED_BOLD.findall(outside):
        text = TAG.sub("", found).strip()
        if not any(character.isdigit() for character in text):
            continue
        if any(quote in text for quote in anchored):
            continue
        errors.append(
            f"{label}: emphasised number {text!r} in the built page is neither anchored in this "
            f"chapter's appendix section nor inside a napkin block — quote a value the appendix "
            f"carries, compute it in a napkin, or drop the emphasis"
        )


RENDERED_H1 = re.compile(r'<h1 id="[^"]*"[^>]*>(?P<inner>.*?)</h1>', re.DOTALL)
RENDERED_H2 = re.compile(r'<h2 id="(?P<id>[^"]*)"[^>]*>(?P<inner>.*?)</h2>', re.DOTALL)
ISSUE_FORM = EDITION_DIR / ".github" / "ISSUE_TEMPLATE" / reader_note.TEMPLATE

# An asset the page would fetch from somewhere else. `<a href>` is deliberately not in the list — a
# book may of course link out — and neither is anything a reader chooses to follow. What is refused
# is a load: a script, a stylesheet, a frame, an image or a media file that arrives from another
# host when a page is merely opened.
EXTERNAL_ASSET = re.compile(
    r"<(?P<tag>script|link|iframe|frame|img|source|video|audio|embed|object|track)\b"
    r"[^>]*?\b(?P<attribute>src|href|data)\s*=\s*[\"'](?P<url>(?:https?:)?//[^\"']*)[\"']",
    re.IGNORECASE,
)


def text_of(html_fragment: str) -> str:
    """A rendered fragment as comparable words: tags gone, entities decoded, curls straightened."""
    return reader_note.straighten(unescape(TAG.sub("", html_fragment)).strip())


def check_note_links(order: Sequence[str], errors: List[str]) -> str:
    """Every marked section in the **built** book carries exactly one reader's-note link, and it fits.

    This is the check that makes the links maintainable rather than merely present. They are
    generated at build time from the `<!-- beat slug.n -->` markers (`preprocessor.py`), and the
    failure mode of a generated link is not that it disappears — it is that it survives a rename or a
    reorder and quietly points somewhere else. So each link is read back out of the HTML mdBook
    actually wrote and made to agree with the section it sits under, on all four of the things it
    carries:

    * the **beat** in the link equals the marker in that section, not the one next door;
    * the **page** in the link is this page's slug;
    * the **anchor** in the link equals the `id` mdBook emitted on this heading — which is what
      keeps `reader_note.anchor()`, a port of mdBook's own id rule, from drifting unnoticed;
    * the **heading and chapter title** in the link equal the heading and the `<h1>` on the page.

    And it is two-way, which is what a mutation showed it had to be. Requiring "a link under every
    marked heading" catches a dropped link; it does not catch a link appearing where no section is,
    which is exactly what a heading swallowed by a code fence would produce. So an unmarked heading
    must carry **none**, a marked one exactly **one**, and nothing above the first heading may carry
    one at all.

    **Two stated limits, so the pass line is not read as more than it is.** A chapter's opening prose
    — everything above the first `##`, which may itself declare a beat — carries no link; the reader
    meets the first one at the first section heading. And the generated appendix has no markers by
    construction, so it carries none either, which this asserts rather than assumes.
    """
    if not RENDER_DIR.exists():
        errors.append("rendered book is absent; run `mdbook build` before checking the note links")
        return "not run"

    # The two addresses the links are built from, cross-checked against what the repository already
    # says about itself. A link pointing at the wrong repository or the wrong site would be perfectly
    # well-formed, and every other check here would pass.
    book_toml = (EDITION_DIR / "book.toml").read_text(encoding="utf-8")
    if f'git-repository-url = "{reader_note.REPO_URL}"' not in book_toml:
        errors.append(
            f"tools/reader_note.py files notes at {reader_note.REPO_URL!r}, which is not the "
            f"`git-repository-url` in book.toml"
        )
    if reader_note.BOOK_URL not in (EDITION_DIR / "README.md").read_text(encoding="utf-8"):
        errors.append(
            f"tools/reader_note.py points readers at {reader_note.BOOK_URL!r}, which is not the "
            f"published address README.md gives"
        )

    # The form the links open. A renamed file or a renamed field id would leave 120 links opening a
    # blank issue instead of the form, with nothing else here objecting.
    if not ISSUE_FORM.exists():
        errors.append(
            f"every note link opens {reader_note.TEMPLATE}, which does not exist at "
            f"{ISSUE_FORM.relative_to(EDITION_DIR)}"
        )
    else:
        form = ISSUE_FORM.read_text(encoding="utf-8")
        for field in ("section", "page", "read-differently"):
            if not re.search(rf"^\s*id:\s*{re.escape(field)}\s*$", form, re.M):
                errors.append(
                    f"{ISSUE_FORM.relative_to(EDITION_DIR)}: no field with id {field!r} — the "
                    f"links prefill by field id, so a rename here silently stops prefilling"
                )
        if f'labels: ["{reader_note.LABEL}"]' not in form:
            errors.append(
                f"{ISSUE_FORM.relative_to(EDITION_DIR)}: the form does not carry the "
                f"{reader_note.LABEL!r} label the links ask for"
            )

    links = 0
    marked = 0
    pages = 0
    for slug in order:
        rendered_path = RENDER_DIR / f"{slug}.html"
        if not rendered_path.exists():
            continue  # check_rendered reports an absent page; one error per fault is enough
        label = str(rendered_path.relative_to(EDITION_DIR))
        html = rendered_path.read_text(encoding="utf-8")

        titled = RENDERED_H1.search(html)
        if titled is None:
            errors.append(f"{label}: no chapter `<h1>` — a note link has no chapter title to carry")
            continue
        chapter_title = text_of(titled.group("inner"))

        headings = list(RENDERED_H2.finditer(html))
        opening = html[: headings[0].start()] if headings else html
        stray = len(reader_note.LINK_HTML.findall(opening))
        if stray:
            errors.append(
                f"{label}: {stray} note link(s) above the first section heading — a link belongs to "
                f"a heading, so this is a heading that did not render (a code fence, most likely)"
            )

        page_had_links = False
        for index, heading in enumerate(headings):
            end = headings[index + 1].start() if index + 1 < len(headings) else len(html)
            region = html[heading.end():end]
            heading_text = text_of(heading.group("inner"))
            where = f"{label} §{heading_text}"

            beats = reader_note.BEAT_MARKER.findall(region)
            found = list(reader_note.LINK_HTML.finditer(region))
            if not beats:
                if found:
                    errors.append(
                        f"{where}: carries a note link but declares no `<!-- beat slug.n -->` "
                        f"marker"
                    )
                continue
            marked += 1
            if len(beats) > 1:
                errors.append(f"{where}: declares {len(beats)} beat markers; a section declares one")
                continue
            if len(found) != 1:
                errors.append(
                    f"{where}: {len(found)} note link(s) — every section carries exactly one, and "
                    f"the build puts it there (preprocessor.py)"
                )
                continue

            link = found[0]
            links += 1
            page_had_links = True
            if link.group("text") != reader_note.LINK_TEXT:
                errors.append(
                    f"{where}: the note link reads {link.group('text')!r}, not "
                    f"{reader_note.LINK_TEXT!r}"
                )
            parsed = reader_note.parse(unescape(link.group("href")))
            if parsed is None:
                errors.append(
                    f"{where}: the note link's URL does not parse back — a field is missing, "
                    f"misencoded, or disagrees with another: {unescape(link.group('href'))!r}"
                )
                continue
            if parsed["beat"] != beats[0]:
                errors.append(
                    f"{where}: the note link says beat {parsed['beat']}, the section's marker says "
                    f"beat {beats[0]}"
                )
            if parsed["slug"] != slug:
                errors.append(
                    f"{where}: the note link's page is {parsed['slug']!r}, not this page ({slug!r})"
                )
            if parsed["anchor"] != heading.group("id"):
                errors.append(
                    f"{where}: the note link scrolls to #{parsed['anchor']}, but mdBook gave this "
                    f"heading the id {heading.group('id')!r}"
                )
            # Both sides straightened, and only for the comparison. `smart-punctuation = true`
            # means the built page says `didn’t` and `-` where the source (and therefore the link a
            # reader sees) says `didn't` and `—`; the link keeps the author's punctuation, and the
            # comparison ignores exactly that difference and nothing else.
            if reader_note.straighten(str(parsed["heading"])) != heading_text:
                errors.append(
                    f"{where}: the note link names the section {parsed['heading']!r}, which is not "
                    f"this heading"
                )
            if reader_note.straighten(str(parsed["chapter"])) != chapter_title:
                errors.append(
                    f"{where}: the note link names the chapter {parsed['chapter']!r}; this page's "
                    f"title is {chapter_title!r}"
                )
        if page_had_links:
            pages += 1

    appendix_page = RENDER_DIR / f"{Path(APPENDIX_FILE).stem}.html"
    appendix_links = (
        len(reader_note.LINK_HTML.findall(appendix_page.read_text(encoding="utf-8")))
        if appendix_page.exists()
        else 0
    )
    if appendix_links:
        errors.append(
            f"the generated appendix carries {appendix_links} note link(s); it declares no beats, "
            f"so it should carry none"
        )

    broken = reader_note.self_test()
    for failure in broken:
        errors.append(failure)

    return (
        f"{links} link(s) under {marked} marked section(s) on {pages} page(s) — exactly one per "
        f"marked section and none anywhere else, each carrying the beat its own marker declares, "
        f"and each URL parsed back to this page's slug, to the id mdBook gave this heading, and to "
        f"this heading's and chapter's own text; the URL round trip and every refusal in "
        f"tools/reader_note.py asserted; the appendix's generated headings carry none, and a "
        f"chapter's opening prose carries none"
    )


def check_no_external_assets(order: Sequence[str], errors: List[str]) -> str:
    """Nothing on a book page is fetched from another host. Opening a page contacts this site only.

    Written down as a check because the obvious way to collect reader feedback is the one thing this
    refuses: a comment widget, a hosted form, an analytics tag. Each is one `<script src>` away, each
    would work, and each would mean a reader of a book about a toy lattice being observed by a third
    party they never agreed to. The note links are `<a href>`s a reader chooses to follow, which is
    the whole difference this check is drawing.

    `<a>` is therefore not in scope; a load is. Scoped to the book's own pages plus the two mdBook
    generates (`print.html`, `404.html`) — `book/record/` is the committed snapshot's own views.
    """
    if not RENDER_DIR.exists():
        errors.append("rendered book is absent; run `mdbook build` before checking for external assets")
        return "not run"

    pages = [RENDER_DIR / f"{slug}.html" for slug in order]
    pages += [RENDER_DIR / name for name in ("index.html", "print.html", "404.html")]
    checked = 0
    for page in pages:
        if not page.exists():
            continue
        checked += 1
        for found in EXTERNAL_ASSET.finditer(page.read_text(encoding="utf-8")):
            errors.append(
                f"{page.relative_to(EDITION_DIR)}: <{found.group('tag').lower()}> loads "
                f"{found.group('url')!r} from another host — no widget, form service or analytics "
                f"may load on a reader's page; inline it or drop it"
            )
    return f"{checked} built page(s) load nothing from another host — no script, style, frame, image or media"


def check_napkin_determinism(errors: List[str]) -> str:
    """Every token, computed twice, must come out identical — and its own assertions must hold.

    Two builds of one commit have to agree, or "computed while this page was built" is a liability
    rather than a guarantee: a reader who rebuilds and sees a different table has caught the book
    inventing numbers. The tokens use exact rational arithmetic and no clock, seed or dict ordering,
    but *intending* determinism is not the same as testing it, and this is cheap enough to run on
    every check rather than in a suite someone remembers to run.

    It doubles as the invariant test. Each token asserts its own claims — loop sums zero, total
    conserved, the average unmoved, every face non-zero — before it returns anything, so calling
    them all here means a broken invariant fails the check even if no chapter uses that token yet.
    """
    try:
        import napkin
    except ImportError as failure:
        errors.append(f"napkin self-test: cannot import tools/napkin.py ({failure})")
        return "unavailable"

    for name in sorted(napkin.TOKENS):
        try:
            first = napkin.render(name)
            second = napkin.render(name)
        except AssertionError as failure:
            errors.append(f"napkin self-test: {name} failed its own invariant — {failure}")
            continue
        except Exception as failure:  # noqa: BLE001 - any failure here must surface, not crash
            errors.append(f"napkin self-test: {name} raised {type(failure).__name__}: {failure}")
            continue
        if first != second:
            errors.append(
                f"napkin self-test: {name} is not deterministic — two runs in one process differ"
            )
        if not NAPKIN_SPAN.fullmatch(first.strip()):
            errors.append(
                f"napkin self-test: {name} is not fenced by its napkin comments, so the "
                f"computed-on-build exemption could not be bounded to it"
            )
        if "computed while this page was built" not in first:
            errors.append(f"napkin self-test: {name} does not say it was computed on build")

    return f"{len(napkin.TOKENS)} tokens, recomputed and identical"


CHAPTER_CAPTION_CEILING = 300


def check_napkin_captions(errors: List[str]) -> str:
    """Every computed caption is measured, and no chapter can grow inside its captions.

    The grain band and the chapter word range both read a chapter's **source**, where a token is the
    seven characters `{{napkin:…}}`. So the captions — real reader-facing prose, rendered into the
    page on every build — were the one surface with no measurement at all, and one of them reached
    118 words and took over the following section's argument before a reader counted it
    (2026-09-02).

    Two ceilings, and they are deliberately not the chapter's: `napkin.block()` refuses a caption
    over `CAPTION_CEILING` words as it renders, and this refuses a chapter whose captions come to
    more than `CHAPTER_CAPTION_CEILING` between them. Folding caption words into the 350–1800
    chapter range instead was considered and rejected as a change the Structure lane owns, not this
    check: it would put `the-shape-between` at 2,044 words against an 1,800 ceiling and force a
    244-word cut in prose a reader had just passed. The numbers are on this line either way, so the
    trade is visible rather than assumed.
    """
    try:
        import napkin
    except ImportError as failure:
        errors.append(f"napkin captions: cannot import tools/napkin.py ({failure})")
        return "unavailable"

    def caption(name: str) -> str:
        # A token whose own assertion fails is `check_napkin_determinism`'s report to make, by name;
        # it runs first and has already said so. Re-raising here would replace that named error with
        # a traceback, and a traceback is a status line nobody wrote — found by mutating a number in
        # engine/napkin.json and re-hashing the lock, 2026-09-02.
        try:
            rendered = napkin.render(name)
        except Exception:  # noqa: BLE001 - reported by the self-test above, by name
            return ""
        marker = "*computed while this page was built — "
        if marker not in rendered:
            return ""
        return rendered.split(marker, 1)[1].split("*", 1)[0]

    lengths = {name: len(words(caption(name))) for name in napkin.TOKENS}
    longest = max(lengths, key=lambda name: lengths[name])
    per_chapter: Dict[str, int] = {}
    for path in sorted((EDITION_DIR / "chapters").glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        used = NAPKIN_TOKEN.findall(markdown)
        if not used:
            continue
        total = sum(lengths.get(name, 0) for name in used)
        per_chapter[path.stem] = total
        if total > CHAPTER_CAPTION_CEILING:
            errors.append(
                f"chapters/{path.name}: its computed captions come to {total} words, over the "
                f"{CHAPTER_CAPTION_CEILING}-word ceiling — the chapter is growing where the grain "
                f"band cannot see it"
            )
    if not per_chapter:
        errors.append("napkin captions: no chapter carries a token, so this check saw nothing")
        return "unavailable"
    heaviest = max(per_chapter, key=lambda slug: per_chapter[slug])
    return (
        f"longest {lengths[longest]} words ({longest}), ceiling {napkin.CAPTION_CEILING}; "
        f"heaviest chapter {per_chapter[heaviest]} ({heaviest}), ceiling "
        f"{CHAPTER_CAPTION_CEILING}"
    )


def check_napkin_contradictions(errors: List[str]) -> str:
    """A chapter may not say what its own tokens disprove — checked against the prose, not the token.

    Every other fidelity check in this file reads what the *tool* wrote. This one reads what the
    *author* wrote, which is where the defect was: `stella_refusal`'s table was corrected to "the
    tick it must stay under" and the prose two paragraphs below still said "a largest tick it will
    hold, the table says what they are", pointing at a table that said the opposite (a proofreader,
    2026-09-02). `napkin.REFUSED_IN_PROSE` is each token's list of phrasings its own arithmetic
    disproves, plus a `*` list refused in every chapter — the three readings the record's own
    computation refuted, which belong to the appendix and to no chapter's prose.

    Self-tested below on constructed sentences, because a guard nobody has made fail is a guard
    nobody has tested.
    """
    try:
        import napkin
    except ImportError as failure:
        errors.append(f"napkin contradictions: cannot import tools/napkin.py ({failure})")
        return "unavailable"

    refused = napkin.REFUSED_IN_PROSE
    everywhere = refused.get("*", [])

    def hits(text: str, phrases: Sequence[str]) -> List[str]:
        lowered = cleaned_prose(text).casefold()
        return [phrase for phrase in phrases if phrase.casefold() in lowered]

    # The guard, tested before it is trusted.
    for phrase in everywhere + refused.get("stella_refusal", []):
        if not hits(f"A sentence that says {phrase} in passing.", [phrase]):
            errors.append(f"napkin contradictions: the guard does not catch {phrase!r}")
    if hits("The tick that must stay under two fifths is the one we brought.", everywhere):
        errors.append("napkin contradictions: the guard false-positives on a correct sentence")

    # The captions first, because they are the surface this was missed on: `REFUSED_IN_PROSE` reads
    # a chapter's markdown, and a token's caption is not in the markdown — it is rendered into the
    # page at build time. A blocked phrasing typed one file over, into the caption, went green (a
    # proofreader, 2026-09-02). The caption is the sentence claiming the page computed its numbers;
    # it answers to the same refusal list as the prose it sits under.
    for name in sorted(napkin.TOKENS):
        try:
            rendered = napkin.render(name)
        except Exception:  # noqa: BLE001 - reported by the napkin self-test above, by name
            continue
        phrases = everywhere + refused.get(name, [])
        for phrase in hits(rendered, phrases):
            errors.append(
                f"tools/napkin.py: {name}'s rendered block says {phrase!r}, which its own "
                f"arithmetic refuses — see napkin.REFUSED_IN_PROSE"
            )

    checked = 0
    for path in sorted((EDITION_DIR / "chapters").glob("*.md")):
        markdown = path.read_text(encoding="utf-8")
        if path.name == APPENDIX_FILE.split("/")[-1]:
            continue                     # the appendix is where the refuted readings belong
        phrases = list(everywhere)
        for name in NAPKIN_TOKEN.findall(markdown):
            phrases.extend(refused.get(name, []))
        checked += 1
        for phrase in hits(markdown, phrases):
            errors.append(
                f"chapters/{path.name}: the prose says {phrase!r}, which this chapter's own "
                f"arithmetic refuses — see napkin.REFUSED_IN_PROSE"
            )
    return (f"{checked} chapters and {len(napkin.TOKENS)} rendered blocks read for "
            f"{len(everywhere)} refused readings and each token's own")


def check_canon(errors: List[str]) -> str:
    """The canonical tetrahedron labeling still agrees with the napkin it is derived from.

    `CANON.md` says the book draws the tetrahedron one way, and `tools/canon.py` is that standard as
    data: the names, the six lines, the four faces, the net's coordinates, and the drawing itself,
    all computed from `oracle.simplices`. Derived is only worth something if the derivation is
    checked, so it is checked here rather than in a suite someone remembers to run — a change to the
    napkin's object that the canon has not followed fails this build, and so does a drawing whose
    labels have stopped being the napkin's simplices.

    The self-test's own headline is used verbatim when it passes, because it is written from what its
    assertions counted; when it fails there is no headline at all, only the raise, so `status()`
    reports the failure. Same discipline, one layer down.
    """
    try:
        import canon
    except ImportError as failure:
        errors.append(f"canon self-test: cannot import tools/canon.py ({failure})")
        return "unavailable"

    try:
        return canon.self_test()
    except AssertionError as failure:
        errors.append(f"canon self-test: the canon failed one of its own assertions — {failure}")
    except Exception as failure:  # noqa: BLE001 - any failure here must surface, not crash
        errors.append(f"canon self-test: raised {type(failure).__name__}: {failure}")
    return "unavailable"


DEMOS_DIR = EDITION_DIR / "demos"
DEMO_EXPORT = DEMOS_DIR / "data" / "napkin.json"
DEMO_TEST = DEMOS_DIR / "core.test.mjs"

# What `demos/` must contain for the published site to carry a working demo. Listed rather than
# globbed: a page that stopped being written to disk, or a chapter that lost its demo, should fail
# by name here instead of quietly not being published.
DEMO_PAGES = (
    "index.html",
    "two-dots-and-a-line.html",
    "one-tetrahedron-is-a-whole-world.html",
    "make-it-move.html",
    "the-shape-between.html",
    "two-worlds-threaded.html",
)
# The five modules a page needs, and the scaffolding it reads its beat numbers off. `steps.json` is
# generated from OUTLINE.md and the chapters' markers by `tools/demo_steps.py`, so it is listed here
# for the same reason the pages are: a page that lost it would render with no beats at all.
DEMO_ASSETS = (
    "core.mjs", "core.test.mjs", "engine.mjs", "draw.mjs", "steps.mjs", "steps.json",
    "demo.css", "data/napkin.json",
)
DEMO_ATTACKS = DEMOS_DIR / "attacks.mjs"
BEAT_ATTACKS = EDITION_DIR / "tools" / "attacks_beats.py"
DEMO_STEPS = DEMOS_DIR / "steps.json"



ENGINE_DIR = EDITION_DIR / "engine"
ENGINE_LOCK = EDITION_DIR / "engine.lock"
ENGINE_WASM_PROBE = EDITION_DIR / "tools" / "engine_wasm_check.mjs"


def load_engine_lock(errors: List[str]) -> Dict[str, List[str]]:
    """`engine.lock`, in `record.lock`'s format: `key = value`, `#` comments, keys accumulating."""
    if not ENGINE_LOCK.exists():
        errors.append("engine: engine.lock is missing — the vendored engine has no pin")
        return {}
    out: Dict[str, List[str]] = {}
    for line in ENGINE_LOCK.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out.setdefault(key.strip(), []).append(value.strip())
    return out


def check_engine(errors: List[str]) -> str:
    """Layer 1 and 2 of the engine contract — **the vendored bytes, and that they are one engine.**

    `record.lock`'s two layers, read from the other side. The record is what the book *quotes*; the
    engine is what it *runs*, and since 2026-09-02 there is one of it: UniForge's `napkin` crate,
    vendored under `engine/` because Our Bubble is public and UniForge is not. A vendored artifact
    with nothing over it is just a file someone put there, so:

    1. **the hashes**, in both directions. Every file `engine.lock` names is present and hashes to
       what it says, and every file under `engine/` is named by the lock. One direction alone is
       satisfied by adding a file; the other, by deleting one.
    2. **the wasm is the same engine as the JSON.** The hashes prove both artifacts are the bytes
       that were built; they say nothing about whether the module *computes* what the payload
       carries. So the module is loaded under node and asked one question the payload already
       answers — the census of the complete complex on four dots, chapters 1 and 2's whole object —
       and the two are compared **byte for byte**. A tolerance here would be the exact seam the
       one-engine decision closes.

    Both run in any clone, with no access to UniForge. Proving the vendored bytes are still what
    that commit produces is `check_engine_integrity`'s job, and it is separate for the record's
    reason: a check that needs a private repository must not be the one holding the gate.
    """
    import hashlib

    lock = load_engine_lock(errors)
    if not lock:
        return "unavailable"

    declared: Dict[str, str] = {}
    for entry in lock.get("sha256", []):
        parts = entry.split()
        if len(parts) != 2:
            errors.append(f"engine: malformed sha256 line in engine.lock: {entry!r}")
            continue
        declared[parts[1]] = parts[0]
    if not declared:
        errors.append("engine: engine.lock declares no files — it pins nothing")
        return "unavailable"

    # `PROVENANCE.md` is the one hand-written file under `engine/` and is deliberately not hashed —
    # see `tools/lock_engine.py`. It is held to the thing that matters instead, below.
    present = {
        str(path.relative_to(EDITION_DIR)): path
        for path in sorted(ENGINE_DIR.rglob("*"))
        if path.is_file() and not path.name.startswith(".") and path.suffix != ".md"
    }
    for rel in sorted(set(declared) | set(present)):
        if rel not in present:
            errors.append(f"engine: {rel} is named by engine.lock but is not in this checkout")
        elif rel not in declared:
            errors.append(
                f"engine: {rel} is vendored but engine.lock does not name it — re-run "
                f"tools/build_engine.sh, or delete the file"
            )
        else:
            actual = hashlib.sha256(present[rel].read_bytes()).hexdigest()
            if actual != declared[rel]:
                errors.append(
                    f"engine: {rel} does not hash to what engine.lock says "
                    f"({actual[:12]}… against {declared[rel][:12]}…). Nothing under engine/ is "
                    f"edited by hand; restore it with `git checkout -- engine/` or rebuild it with "
                    f"tools/build_engine.sh"
                )
    if errors:
        return "unavailable"

    sha_pinned = (lock.get("sha") or [""])[0]
    note = ENGINE_DIR / "PROVENANCE.md"
    if not note.exists():
        errors.append("engine: engine/PROVENANCE.md is missing — the vendored artifact has no note")
        return "unavailable"
    if sha_pinned not in note.read_text(encoding="utf-8"):
        errors.append(
            f"engine: engine/PROVENANCE.md does not name the commit engine.lock pins "
            f"({sha_pinned[:7]}) — the note and the lock disagree about where these bytes came from"
        )
        return "unavailable"

    census = engine_wasm_census(errors)
    if census is None:
        return "unavailable"

    vendored = json.dumps(
        json.loads((ENGINE_DIR / "napkin.json").read_text(encoding="utf-8"))["complexes"]["4"],
        sort_keys=True, indent=2, separators=(",", ": "), ensure_ascii=True,
    ) + "\n"
    if census != vendored:
        errors.append(
            f"engine: the wasm module's census of four dots is not the vendored payload's "
            f"({len(census)} bytes from the module, {len(vendored)} in engine/napkin.json) — the "
            f"two artifacts under engine/ are not the same engine"
        )
        return "unavailable"

    return (f"{len(declared)} vendored file(s) hashed against engine.lock at {sha_pinned[:7]}, "
            f"named by engine/PROVENANCE.md; the wasm's census of 4 dots is the payload's own "
            f"{len(census)} bytes")


def engine_wasm_census(errors: List[str]) -> "str | None":
    """Load `engine/napkin_bg.wasm` under node and return its answer to `census_json(4)`.

    Node is present in tier 0 and in CI, so this is not the record's optional layer — a missing node
    here is a broken environment and is reported as a failure rather than waved through. That is the
    difference between "the engine could not be reached" and "the tool that runs the check is not
    installed": only the first is a fact about the world.
    """
    import shutil
    import subprocess

    if not ENGINE_WASM_PROBE.exists():
        errors.append(f"engine: {ENGINE_WASM_PROBE.relative_to(EDITION_DIR)} is missing")
        return None
    node = shutil.which("node")
    if node is None:
        errors.append(
            "engine: node is not installed, so the vendored wasm could not be loaded and proved to "
            "be the same engine as the vendored JSON. Install node, or run tier 0 in CI"
        )
        return None
    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [node, str(ENGINE_WASM_PROBE)],
        capture_output=True, text=True, cwd=EDITION_DIR, timeout=300, check=False,
    )
    if finished.returncode != 0:
        detail = (finished.stderr or "").strip().splitlines()
        errors.append(
            f"engine: loading the vendored wasm failed — "
            f"{detail[-1] if detail else f'node exited {finished.returncode}'}"
        )
        return None
    return finished.stdout


def check_engine_integrity(errors: List[str]) -> str:
    """Layer 3 — **a fresh build from the pinned commit reproduces the vendored bytes.**

    The hashes prove `engine/` is what was committed. They cannot prove it is what UniForge's
    `napkin` crate emits at the commit `engine.lock` names, and that is the claim the whole
    arrangement rests on: an artifact built from some other tree, or edited before it was hashed,
    would satisfy every other check here.

    So when `UNIFORGE_SRC` points at a UniForge checkout **at that commit**, the emitter is run and
    its output compared to the vendored payload byte for byte. When it does not — which for a
    private repository means almost everywhere — this returns
    `unverified — engine source absent` and asserts nothing. Same shape as the record's
    snapshot-integrity layer, and for the same reason: a check that quietly skips is worse than one
    that is absent, because it teaches people the green tick means something it does not.
    """
    import subprocess

    source = os.environ.get("UNIFORGE_SRC")
    if not source:
        return "unverified — engine source absent (set UNIFORGE_SRC to a UniForge checkout)"
    root = Path(source).expanduser()
    if not (root / "core" / "napkin").is_dir():
        return f"unverified — engine source absent ({source} is not a UniForge checkout)"

    lock = load_engine_lock(errors)
    pinned = (lock.get("sha") or [""])[0]
    head = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=60, check=False,
    ).stdout.strip()
    if head != pinned:
        return (f"unverified — the engine source is at {head[:7] or '?'} and engine.lock pins "
                f"{pinned[:7]}")

    built = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        ["cargo", "run", "--quiet", "--release", "-p", "napkin", "--bin", "napkin-export"],
        capture_output=True, text=True, cwd=root / "core", timeout=1800, check=False,
    )
    if built.returncode != 0:
        detail = (built.stderr or "").strip().splitlines()
        errors.append(
            f"engine integrity: the emitter would not build at the pinned commit — "
            f"{detail[-1] if detail else f'cargo exited {built.returncode}'}"
        )
        return "unavailable"

    vendored = (ENGINE_DIR / "napkin.json").read_text(encoding="utf-8")
    if built.stdout != vendored:
        errors.append(
            f"engine integrity: a fresh export from {pinned[:7]} is not the vendored "
            f"engine/napkin.json ({len(built.stdout)} bytes built, {len(vendored)} vendored) — "
            f"engine/ was not produced by the commit engine.lock names, or it was edited afterwards"
        )
        return "unavailable"
    return f"verified — a fresh export from {pinned[:7]} is the vendored bytes, all {len(vendored)}"


def check_napkin_export(errors: List[str]) -> str:
    """The demos' oracle is in step with the napkin, exact, and byte-identical across two builds.

    `demos/` recomputes chapters 1–4 in the reader's browser, which is the point of it and also the
    risk: two implementations of the same arithmetic are two places the book can disagree with
    itself. `tools/napkin_export.py` is the boundary between them — the napkin's *data*, with none of
    its prose — and this holds it to three things:

    * it is what is committed. A stale `demos/data/napkin.json` would let the cross-check below pass
      against arithmetic the napkin no longer does, so the file is re-derived here and compared byte
      for byte, and the diff is reported as a change to the export rather than as a mystery.
    * it is deterministic, and carries no float anywhere. Both are the export's own assertions; they
      run here so that they run on every check.
    * every number in it is an exact rational written as a string, which is what lets the JavaScript
      side be compared rather than approximated.
    """
    try:
        import napkin_export
    except ImportError as failure:
        errors.append(f"napkin export: cannot import tools/napkin_export.py ({failure})")
        return "unavailable"

    try:
        line = napkin_export.self_test()
    except AssertionError as failure:
        errors.append(f"napkin export: failed one of its own assertions — {failure}")
        return "unavailable"
    except Exception as failure:  # noqa: BLE001 - any failure here must surface, not crash
        errors.append(f"napkin export: raised {type(failure).__name__}: {failure}")
        return "unavailable"

    fresh = napkin_export.text()
    if not DEMO_EXPORT.exists():
        errors.append(
            f"napkin export: {DEMO_EXPORT.relative_to(EDITION_DIR)} is missing — run "
            f"`python3 tools/napkin_export.py` and commit it"
        )
        return "unavailable"
    committed = DEMO_EXPORT.read_text(encoding="utf-8")
    if committed != fresh:
        errors.append(
            f"napkin export: {DEMO_EXPORT.relative_to(EDITION_DIR)} is not what the napkin now "
            f"exports ({len(committed)} bytes committed, {len(fresh)} derived) — the arithmetic "
            f"moved. Run `python3 tools/napkin_export.py`, check what changed, and commit it with "
            f"whatever moved it"
        )
    return line


def check_demo_steps(errors: List[str]) -> str:
    """The demos' step scaffolding is what `OUTLINE.md` and the chapters' markers now derive.

    No beat number is typed into a demo. `tools/demo_steps.py` reads the questions off `OUTLINE.md`
    and the ids off each chapter's `<!-- beat slug.n -->` markers, keyed by section anchor, and
    writes `demos/steps.json`; the pages render their titles from that. So the file has to
    be in step with the contract, and this is where a renumber that has not been regenerated becomes
    a red check rather than a page quoting last week's numbering. The preface being drafted will move
    every beat in the book, which is precisely the event this is here for.
    """
    import subprocess

    script = EDITION_DIR / "tools" / "demo_steps.py"
    if not script.exists():
        errors.append("demo steps: tools/demo_steps.py is missing")
        return "unavailable"
    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [sys.executable, "-B", str(script), "--check"],
        capture_output=True, text=True, cwd=EDITION_DIR, timeout=120, check=False,
    )
    if finished.returncode != 0:
        for line in (finished.stderr or finished.stdout or "").splitlines():
            if line.strip():
                errors.append(f"demo steps: {line.strip()}")
        return "unavailable"
    if not DEMO_STEPS.exists():
        errors.append("demo steps: demos/steps.json is missing")
        return "unavailable"
    scaffold = json.loads(DEMO_STEPS.read_text(encoding="utf-8"))
    sections = sum(len(chapter["sections"]) for chapter in scaffold["chapters"].values())
    return (f"{len(scaffold['chapters'])} chapters and {sections} beats, read off OUTLINE.md and "
            f"the chapters' markers")


def check_demo_cross_check(errors: List[str]) -> str:
    """Run the demo pages under node and hold every number they render to what the engine emitted.

    This check changed its meaning when the engine was vendored, and the change is the point of the
    rebuild. It used to compare **two implementations** of the book's arithmetic — the demos' own
    exact rationals in JavaScript against the napkin's in Python — because there were two. There is
    one now, so what is asked is no longer *do the two agree* but **does the page show what the
    engine said**.

    Six gates, and `demos/core.test.mjs` states each one at the point it runs: the vendored wasm and
    the vendored JSON agree byte for byte on the census; every numeric token on every surface a
    reader meets, at every state of every step, is a value the engine returned in that run; no digit
    is typed into a step's source or into a page's HTML at all; every segment the wireframe draws is
    an edge of the engine's census and every dot one of its vertices; every step maps onto exactly
    one marked chapter section and the beat numbers agree; and every page's reader-facing words are
    counted and held under the owner's budget — printed either way, so the count cannot drift back.

    What it does not catch, and `demos/DEMOS.md` says so in the same words: a number computed
    correctly and put in the wrong place. Only reading the page catches that, which is what the
    proof-reader pass is for.

    **When node is absent this reports `unverified`, and never a pass.** That is the same shape as
    the snapshot-integrity layer: a check that could not run says so, on its own line, rather than
    letting a green tick imply it happened. CI has node, so the gap closes there.
    """
    import shutil
    import subprocess

    if not DEMO_TEST.exists():
        errors.append(f"demo cross-check: {DEMO_TEST.relative_to(EDITION_DIR)} is missing")
        return "unavailable"
    node = shutil.which("node")
    if node is None:
        return "unverified — node absent, so the demos' numbers were not compared to the napkin's"

    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [node, str(DEMO_TEST)],
        capture_output=True, text=True, cwd=EDITION_DIR, timeout=300, check=False,
    )
    if finished.returncode != 0:
        for line in (finished.stderr or "").splitlines():
            if line.strip():
                errors.append(f"demo cross-check: {line.strip()}")
        if not (finished.stderr or "").strip():
            errors.append(
                f"demo cross-check: node exited {finished.returncode} with nothing on stderr"
            )
        return "unavailable"
    lines = [line for line in finished.stdout.splitlines() if line.startswith("core.test.mjs:")]
    # The per-chapter word counts are printed rather than folded into the headline, because the
    # owner's budget is the thing most likely to drift back and the only way it stays visible is if
    # a reader of the check output sees it on every run.
    for line in lines[:-1]:
        print(f"    {line.split(': ', 1)[1]}")
    return lines[-1].split(": ", 1)[1] if lines else "passed, with no summary line"



def check_demo_attacks(errors: List[str]) -> str:
    """Every guard in the demos' cross-check, with the mutation that proves it bites.

    The standing rule this implements (2026-09-03): **no new guard lands without its mutation, in
    the same commit.** Five rounds running, a guard written to close a hole was found on the next
    read to have a hole of its own — a census that checked identity and not geometry, a sum check
    keyed to a word, a paragraph rule whose window excluded the figures it existed for, a dot test
    measuring centres instead of ink, a step enumerator that never typed anything. Every one of
    those had been "tested" by an attack run once in a shell and thrown away.

    So the attacks live in the repository and run here. Each mutation is applied to a **private copy**
    of `demos/` and `engine/` under the system temp directory, the cross-check is run from that copy
    and required to complain **by name**, and the copy is deleted; the working tree is never written,
    and the suite asks git afterwards whether it kept its word. It also reports how many of the
    cross-check's own fail sites the mutations reached, against a committed baseline. A mutation
    whose needle has gone stale fails too, which is how a refactor says an attack has stopped
    testing anything instead of passing quietly.

    Needs node, like the cross-check itself; without it this reads `unverified` rather than passing.
    And the suite refuses to run at all on a dirty `demos/` or `engine/` — it cannot verify its own
    no-write claim from a dirty start — which it reports by exiting 3, read here as `unverified`
    rather than as a failure, so uncommitted demo work does not make the rest of tier 0 unrunnable.
    """
    import shutil
    import subprocess

    if not DEMO_ATTACKS.exists():
        errors.append(f"demo attacks: {DEMO_ATTACKS.relative_to(EDITION_DIR)} is missing")
        return "unavailable"
    node = shutil.which("node")
    if node is None:
        return "unverified — node absent, so no guard was shown to bite"

    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [node, str(DEMO_ATTACKS)],
        capture_output=True, text=True, cwd=EDITION_DIR, timeout=900, check=False,
    )
    if finished.returncode == 3:
        return ("unverified — demos/ or engine/ has uncommitted changes, so the suite could not "
                "run: it verifies afterwards that it left the tree as it found it")
    if finished.returncode != 0:
        for line in (finished.stderr or "").splitlines():
            if line.strip():
                errors.append(f"demo attacks: {line.strip()}")
        if not (finished.stderr or "").strip():
            errors.append(f"demo attacks: node exited {finished.returncode} with nothing on stderr")
        return "unavailable"
    summary = [line for line in finished.stdout.splitlines() if line.startswith("attacks.mjs:")]
    return summary[-1].split(": ", 1)[1] if summary else "passed, with no summary line"


def check_beat_attacks(errors: List[str]) -> str:
    """Every rule of the beat-id contract, with the mutation that proves `beat_coverage.py` bites.

    The demos have had their mutations in the repository since `demos/attacks.mjs`; the Python
    checks had none, so "the coverage tool catches this" was a claim in a commit message rather than
    something the repository runs. `tools/attacks_beats.py` is the same arrangement in Python: each
    mutation is applied to a **private copy** of the contract and the prose under the system temp
    directory, `tools/beat_coverage.py` is run from that copy and required to complain **by name**,
    and the copy is deleted. It runs the unmutated copy first — an attack suite that cannot tell red
    from red proves nothing — and asks git afterwards whether it left the working tree alone.

    A mutation whose needle has gone stale fails too, which is how a refactor says an attack has
    stopped testing anything instead of passing quietly.
    """
    import subprocess

    if not BEAT_ATTACKS.exists():
        errors.append(f"beat attacks: {BEAT_ATTACKS.relative_to(EDITION_DIR)} is missing")
        return "unavailable"
    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [sys.executable, "-B", str(BEAT_ATTACKS)],
        capture_output=True, text=True, cwd=EDITION_DIR, timeout=900, check=False,
    )
    if finished.returncode != 0:
        for line in (finished.stdout or "").splitlines():
            if line.strip().startswith("PROBLEM:"):
                errors.append(f"beat attacks: {line.strip()[len('PROBLEM: '):]}")
        if not [error for error in errors if error.startswith("beat attacks:")]:
            errors.append(f"beat attacks: the suite exited {finished.returncode} with no problem "
                          f"line of its own")
        return "unavailable"
    summary = [line for line in finished.stdout.splitlines() if line.startswith("beat attacks:")]
    return summary[-1].split(": ", 1)[1] if summary else "passed, with no summary line"


def check_engine_published(errors: List[str]) -> str:
    """The built site actually carries the engine, byte for byte.

    `engine/` sits outside `chapters/`, so it reaches the published site only through the
    `chapters/engine` symlink that mdBook copies — the same mechanism that carries `record/` and
    `demos/`. That is a piece of wiring nothing would notice breaking: the book would build, every
    check above would pass, and the reader's browser would 404 on the WebAssembly module.

    The bytes are compared rather than the names, because a truncated copy of a 322 kB module is a
    file that exists. GitHub Pages serves `.wasm` as `application/wasm`, which is what
    `WebAssembly.instantiateStreaming` requires, so no MIME configuration is needed here — and if
    that ever stopped being true, the glue falls back to `arrayBuffer()` and the page still runs.
    """
    built = RENDER_DIR / "engine"
    if not built.is_dir():
        errors.append(
            "engine published: book/engine/ does not exist — mdBook did not copy engine/ into the "
            "build. Is chapters/engine still a symlink to ../engine?"
        )
        return "unavailable"
    total = 0
    for source in sorted(ENGINE_DIR.rglob("*")):
        if not source.is_file() or source.name.startswith(".") or source.suffix == ".md":
            continue
        published = built / source.relative_to(ENGINE_DIR)
        if not published.is_file():
            errors.append(f"engine published: book/engine/{source.name} is missing from the site")
        elif published.read_bytes() != source.read_bytes():
            errors.append(f"engine published: book/engine/{source.name} is not the vendored file")
        else:
            total += published.stat().st_size
    return f"{total:,} bytes of engine served from book/engine/, byte-for-byte"


def check_demos_published(errors: List[str]) -> str:
    """The built site actually carries the demos, and each one links back to its chapter.

    `demos/` sits outside `chapters/`, so it reaches the published site only through the
    `chapters/demos` symlink that mdBook copies — the same mechanism that carries `record/`. That is
    a piece of wiring nothing would notice breaking: the book would build, the check would pass, and
    the demo links would 404 for readers only. So the built tree is looked at.
    """
    built = RENDER_DIR / "demos"
    if not built.is_dir():
        errors.append(
            "demos published: book/demos/ does not exist — mdBook did not copy demos/ into the "
            "build. Is chapters/demos still a symlink to ../demos?"
        )
        return "unavailable"
    for name in DEMO_PAGES + DEMO_ASSETS:
        if not (built / name).is_file():
            errors.append(f"demos published: book/demos/{name} is missing from the built site")
    for name in DEMO_PAGES:
        page = built / name
        if not page.is_file():
            continue
        for target in HTML_LINK.findall(page.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "#", "mailto:", "data:")):
                continue
            resolved = (page.parent / target.split("#", 1)[0]).resolve()
            if not resolved.exists():
                errors.append(f"demos published: book/demos/{name} links to {target}, which is not there")
    return f"{len(DEMO_PAGES)} pages and {len(DEMO_ASSETS)} files, every link resolved"


def appendix_sections(markdown: str) -> Dict[str, str]:
    """The appendix split into its per-chapter sections, keyed by **slug**.

    Each section opens with a stable anchor — `<a id="s-<slug>"></a>` — and the visible heading
    carries a derived section number for the reader. Splitting on the anchor rather than the heading
    is what makes the numbers free to change: a chapter's pointer links to `#s-<slug>`, which no
    insertion can invalidate.
    """
    out: Dict[str, str] = {}
    current: str | None = None
    buffer: List[str] = []
    for line in markdown.splitlines():
        anchor = re.match(r'^<a id="s-([a-z0-9-]+)"></a>\s*$', line.strip())
        if anchor:
            if current is not None:
                out[current] = "\n".join(buffer)
            current = anchor.group(1)
            buffer = [line]
            continue
        if current is not None:
            buffer.append(line)
    if current is not None:
        out[current] = "\n".join(buffer)
    return out


def check_appendix(
    manifest: Dict[str, object],
    numbers: Dict[str, str],
    narrative: Sequence[str],
    forbidden: Sequence[str],
    forbidden_patterns: Sequence[Dict[str, str]],
    errors: List[str],
) -> None:
    """The appendix carries **all** the verbatim anchoring, and the bridge to the narrative.

    Four obligations, and they are the reason the narrative can be written free:

    1. **Every chapter has a section**, reachable by a stable slug anchor — no chapter loses its
       provenance by being rewritten, renamed or moved in the reading order.
    2. **The displayed section numbers match the reading order** taken from `SUMMARY.md`. They are
       derived at generation time; this is the check that the generated file was not left stale.
    3. **Every rung's entry, gate and figure path exists**, so a section cannot cite an experiment
       the repository does not have.
    4. **Every declared quotation is verbatim in its own section AND carried by its canonical
       source.**

    **The scope of obligation 4, written down because it was discovered rather than read** (a
    proofreader, 2026-09-02). The verbatim test reads the **appendix section's body** and the record
    file. It does not read the chapter prose, and that is by design: the chapters carry no
    quotations at all — moving the provenance to a boundary is the entire point of the appendix, and
    `check_chapter` asks the narrower question that remains, that any number a chapter *emphasises*
    is one its own appendix section anchored.

    The consequence follows and is worth stating before someone relies on the opposite: a chapter
    can *lose* the prose that earned its numbers with nothing here objecting. The appendix still
    carries them, they still verify against the record, and parity stays at 35/13 with tier 0 green.
    Whether each chapter still says what it was written to say is `tools/beat_coverage.py`'s job,
    and above that a reader's — never this function's.
    """
    appendix = manifest.get("appendix")
    if not isinstance(appendix, dict):
        errors.append("edition.json declares no appendix; the narrative would have no anchor")
        return

    relative = str(appendix["file"])
    path = EDITION_DIR / relative
    if not path.exists():
        errors.append(f"missing appendix: {relative}")
        return
    markdown = path.read_text(encoding="utf-8")

    if "> **Scope.**" not in markdown:
        errors.append(f"{relative}: missing visible Scope block")
    if "toy" not in markdown.casefold():
        errors.append(f"{relative}: scope never says this is a toy")

    # the hardened legacy-claims guard runs here too — paraphrase risk does not stop at the
    # narrative boundary, and the appendix is where the excluded programme's vocabulary lives.
    for hit in forbidden_hits(markdown, forbidden, forbidden_patterns):
        errors.append(f"{relative}: {hit}")

    bodies = appendix_sections(markdown)
    if list(bodies) != list(narrative):
        errors.append(
            "the appendix's sections are not the chapters in reading order: "
            f"{list(bodies)!r} != {list(narrative)!r}"
        )

    sections: Dict[str, object] = dict(appendix["sections"])
    for slug in narrative:
        number = numbers[slug]
        label = f"{relative} §{number} ({slug})"
        body = bodies.get(slug)
        if body is None:
            errors.append(f'{label}: no `<a id="s-{slug}"></a>` section in the appendix')
            continue
        if f"## §{number} ·" not in body:
            errors.append(
                f"{label}: the section's displayed number does not match the reading order — "
                f"regenerate the appendix"
            )
        section = dict(sections[slug])

        for key in ("entries", "gates", "figures", "standards"):
            for target in section.get(key, []):
                if not (RECORD_DIR / str(target)).exists():
                    errors.append(f"{label}: declared {key[:-1]} does not exist: {target}")
                if str(target) not in body:
                    errors.append(f"{label}: declared {key[:-1]} is not shown in the section: {target}")

        for quote in section.get("record_quotes", []):
            text = str(quote["text"])
            source = str(quote["source"])
            source_path = RECORD_DIR / source
            if text not in body:
                errors.append(f"{label}: declared quotation is absent from the section: {text!r}")
            if not source_path.exists():
                errors.append(f"{label}: quotation source is absent: {source}")
            elif text not in source_path.read_text(encoding="utf-8"):
                errors.append(f"{label}: {text!r} is not carried by declared source {source}")

    # The appendix reads in the book's voice, so it answers to the book's prose standard. Two earlier
    # attempts to wire these in matched nothing and failed silently, which is why they are asserted
    # by the self-test below rather than trusted.
    check_prose_integrity(relative, markdown, errors)
    paragraph_length_ok(markdown, relative, errors)
    sentence_length_ok(markdown, relative, errors)
    check_links(path, markdown, errors)


# `…and it That provenance…` — a conjunction and its subject with the predicate gone, butted against
# the next sentence. The capitalised word is the tell: with no full stop before it, the join is broken.
# Determiners (`this`, `that`) are excluded from the subject set because "so this Alexandria
# measurement" is legitimate English; only pronouns that must take a verb are listed.
BROKEN_JOIN = re.compile(
    r"\b(and|but|or|so|yet|because|although|while|however)\s+"
    r"(it|they|he|she|we|there|I)\s+"
    r"([A-Z]\w+)"
)


def paragraph_length_ok(markdown: str, relative_file: str, errors: List[str]) -> None:
    """No prose paragraph over 150 words. Shared by the chapters and the appendix."""
    for paragraph in prose_paragraphs(markdown):
        count = len(words(paragraph))
        if count > 150:
            errors.append(f"{relative_file}: prose paragraph has {count} words (limit 150)")


def sentence_length_ok(markdown: str, relative_file: str, errors: List[str]) -> bool:
    """Average sentence length, measured over **prose paragraphs only**.

    It used to be measured over `cleaned_prose(markdown)` — the whole file with links and code spans
    removed — which on a page that is mostly tables and bullet lists is not measuring sentences at
    all. Stripped of its links, a run of table rows has no sentence-ending punctuation in it, so the
    splitter returned whole table blocks as single 120-word "sentences" and the appendix's average
    drifted to exactly 24.0 against a 24 ceiling. The next honest line added to it would have failed
    the build, and the obvious way to make the number go down would have been to damage the prose.

    Measuring the paragraph stream — the same one the 150-word paragraph rule already uses, which
    skips headings, blockquotes, lists, tables and HTML — makes the metric mean what it says. It is
    not a relaxation: two chapters' averages go *up* under it, because their tables were dragging
    them down.
    """
    joined = " ".join(cleaned_prose(paragraph) for paragraph in prose_paragraphs(markdown))
    sentences = [segment for segment in SENTENCE_END.split(joined) if len(words(segment)) >= 4]
    if not sentences:
        return True
    average = sum(len(words(sentence)) for sentence in sentences) / len(sentences)
    if average > 24:
        errors.append(f"{relative_file}: average sentence length {average:.1f} exceeds 24 words")
        return False
    return True


def check_prose_integrity(relative_file: str, markdown: str, errors: List[str]) -> None:
    """Catch a sentence that stopped mid-clause — the defect a find-and-replace prose pass leaves.

    Why this exists (proofread re-read, 2026-09-01): a tone pass replaced the second half of a
    sentence and left the first half hanging — `That is a deliberate choice, and it` followed by a
    fresh sentence. **The whole edition check was green.** Every other rule here asks whether the
    prose agrees with the record; none of them reads the prose as a sentence, so a reader caught it
    and the tool could not.

    Deliberately narrow, and narrower than the first attempt. The obvious general rule — *a paragraph
    may not end on a word no sentence ends on* — was written, run, and thrown away: it fired 28 times
    on prose that is correct, because sentences end on "it", on "that", and on stranded prepositions
    all the time ("…what the least is", "…the number you started from"). A check that has to be
    argued with is a check that gets switched off.

    What is left looks for one shape only, and it is the residue of *editing* rather than of writing:
    a conjunction and its subject run into the start of the next sentence, with the predicate between
    them removed. That is what the blocker was.
    """
    for paragraph in prose_paragraphs(markdown):
        found = BROKEN_JOIN.search(paragraph)
        if found:
            errors.append(
                f"{relative_file}: {found.group(0)!r} — a conjunction and its subject with no verb, "
                f"run into the start of the next sentence. A predicate was removed here."
            )


def check_chapter_references(
    relative_file: str,
    markdown: str,
    known: Sequence[str],
    errors: List[str],
) -> None:
    """A cross-reference to another chapter must be a **link that resolves to a chapter slug**.

    History of this rule, because its shape changed once already. The proofread of 2026-09-01 (B1)
    found three references written as bare prose — "the wall from chapter 03" and two more — that an
    insertion had silently left pointing one chapter too low. The first version of this rule required
    the link form and then compared the number in the link text against the number in the filename.

    The slug migration removed the second half of that: **filenames no longer carry numbers, so there
    is nothing left for a number in the text to disagree with.** What replaces it is stricter in the
    way that matters — a chapter number in narrative prose is now refused outright, whether or not it
    sits inside a link, because positions are derived from `SUMMARY.md` at generation time and prose
    that hard-codes one is a stale reference waiting to happen. Refer to a chapter by name, and link
    it; the link resolves against the chapter set, so a rename breaks the build and a reorder cannot.

    Scoped to the narrative. The appendix's cross-references are generated from `edition.json`, and it
    legitimately cites *another book's* chapters ("The Container, chapter 00").
    """
    for found in re.finditer(r"chapters?\s+\d{1,2}\b", markdown, re.IGNORECASE):
        errors.append(
            f"{relative_file}: {found.group(0)!r} hard-codes a position that is derived from "
            f"chapters/SUMMARY.md — name the chapter and link it instead, e.g. "
            f"`[the bubble and its bill](the-bubble-and-its-bill.md)`"
        )

    for text, target in re.findall(r"\[([^\]]*)\]\(([^)]+)\)", markdown):
        leaf = target.split("#", 1)[0].split("/")[-1]
        if not leaf.endswith(".md") or "/" in target.split("#", 1)[0]:
            continue
        slug = leaf[: -len(".md")]
        if slug == Path(APPENDIX_FILE).stem or slug in known:
            continue
        errors.append(
            f"{relative_file}: link {text!r} points at {leaf!r}, which is not a chapter in "
            f"chapters/SUMMARY.md"
        )


def check_chapter(
    slug: str,
    entry: Dict[str, object],
    section: Dict[str, object],
    number: str,
    known: Sequence[str],
    forbidden: Sequence[str],
    forbidden_patterns: Sequence[Dict[str, str]],
    is_last: bool,
    errors: List[str],
) -> None:
    relative_file = f"chapters/{slug}.md"
    chapter_path = EDITION_DIR / relative_file
    if not chapter_path.exists():
        errors.append(f"missing chapter: {relative_file}")
        return

    markdown = chapter_path.read_text(encoding="utf-8")
    lowered = markdown.casefold()

    if "> **Scope.**" not in markdown:
        errors.append(f"{relative_file}: missing visible Scope block")
    if "toy" not in lowered:
        errors.append(f"{relative_file}: scope never says this is a toy")
    if not is_last and "**Next:**" not in markdown:
        errors.append(f"{relative_file}: missing purposeful Next hand-off")
    if is_last and "**Next:**" in markdown:
        errors.append(f"{relative_file}: epilogue should close rather than hand off")

    count = len(words(cleaned_prose(markdown)))
    if count < 350 or count > 1800:
        errors.append(f"{relative_file}: {count} words is outside the 350–1800 reader range")

    paragraph_length_ok(markdown, relative_file, errors)

    prose = cleaned_prose(markdown)
    sentence_length_ok(markdown, relative_file, errors)

    for hit in forbidden_hits(markdown, forbidden, forbidden_patterns):
        errors.append(f"{relative_file}: {hit}")

    for source in entry.get("sources", []):
        source_path = RECORD_DIR / str(source)
        if not source_path.exists():
            errors.append(f"{relative_file}: declared source does not exist: {source}")

    # **Verbatim anchoring is appendix-only.** The narrative is written free; what it still owes is
    # that any number it *emphasizes* is one the appendix has anchored for this chapter.
    anchored = [str(quote["text"]) for quote in section.get("record_quotes", [])]
    for emphasized_result in BOLD_NUMBER.findall(prose):
        if not any(quote in emphasized_result for quote in anchored):
            errors.append(
                f"{relative_file}: emphasized number {emphasized_result!r} is not anchored in the "
                f"appendix section for this chapter — either quote a value the appendix carries, or "
                f"tell it in story form without emphasis"
            )

    # Every chapter points at its own appendix section, **by slug**: an anchor no reorder can stale.
    pointer = f"({Path(str(APPENDIX_FILE)).name}#s-{slug})"
    if pointer not in markdown:
        errors.append(
            f"{relative_file}: missing the closing pointer to its appendix section — the link must "
            f"end {pointer!r} (§{number} in the current reading order)"
        )

    check_prose_integrity(relative_file, markdown, errors)
    check_chapter_references(relative_file, markdown, known, errors)
    check_links(chapter_path, markdown, errors)


def load_lock() -> Dict[str, List[str]]:
    """`record.lock`, as `{key: [values…]}`.

    Deliberately the dumbest format that can carry the contract: `key = value`, one per line, `#`
    comments, repeated keys accumulate. No parser to install, nothing to get subtly wrong, and a
    human diff of a record bump reads as exactly what changed.
    """
    out: Dict[str, List[str]] = {}
    if not RECORD_LOCK.exists():
        return out
    for line in RECORD_LOCK.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line or "=" not in line:
            continue
        key, value = line.split("=", 1)
        out.setdefault(key.strip(), []).append(value.strip())
    return out


def declared_record_paths(manifest: Dict[str, object]) -> List[str]:
    """Every record path this edition depends on: `edition.json`'s declarations **and the links**.

    Derived, never maintained — the same discipline as the appendix's section numbers. `record.lock`
    writes the list down so a reader can see the book's footprint in the engine without reading the
    manifest, and the check below is what keeps the written copy honest.

    The chapter links matter as much as the manifest and were nearly left out: a chapter may link a
    record file the manifest never declares (the double-slit demo is one), and such a link is a real
    dependency — `check_links` fails without it. A footprint that listed only what was declared would
    have been quietly, provably wrong on its first day.
    """
    paths = set()
    prefix = f"{RECORD_DIR.name}/"
    views = generated_manifest()
    for chapter in sorted((EDITION_DIR / "chapters").glob("*.md")):
        markdown = chapter.read_text(encoding="utf-8")
        for raw in MARKDOWN_LINK.findall(markdown) + HTML_LINK.findall(markdown):
            target = raw.strip().strip("<>").split("#", 1)[0].split("?", 1)[0]
            if not target.startswith(prefix):
                continue
            inside = target[len(prefix):]
            # A link to a generated view is a link to the file it renders. Normalising here is what
            # lets the appendix send a reader to a readable `.rs` gate while the footprint stays a
            # list of real record files.
            paths.add(views.get(inside) or inside)
    for section in dict(manifest["appendix"]["sections"]).values():
        entry = dict(section)
        for key in ("entries", "gates", "figures", "standards"):
            paths.update(str(target) for target in entry.get(key, []))
        for quote in entry.get("record_quotes", []):
            paths.add(str(dict(quote)["source"]))
    for chapter in dict(manifest["chapters"]).values():
        paths.update(str(source) for source in dict(chapter).get("sources", []))
    return sorted(paths)


# Every status line this checker prints goes through `status()` below, and the log is what lets
# `report()` re-assert the property afterwards rather than trusting that it held.
_STATUS_LOG: List[Tuple[str, str, int]] = []


def status(errors: List[str], label: str, run, quiet: bool = False) -> str:
    """Run a check, then print its status line — with the verdict derived from what it *did*.

    This exists because the same defect shipped twice. A check that appends to `errors` and also
    returns a human-readable headline computed its headline without consulting whether it had just
    failed, so `snapshot integrity: verified — 150 files byte-for-byte` printed directly above its
    own drift error, and `napkin self-test: 6 tokens, recomputed and identical` above five of them.
    Both were correct in their errors and wrong in the line a reader actually skims.

    Fixing the two call sites twice would have been fixing the instances. The class is *a status a
    check narrates about itself*, so the narration is taken away from the check: `run()` returns only
    what it observed, and the verdict comes from the error-count delta, which cannot be fibbed.
    A check that fails now cannot report clean — not by discipline, but because it no longer holds
    the pen.

    The mirror case is caught too: a check that announces failure without appending an error has
    also lied, and its errors would be invisible to `report()`'s exit code.
    """
    before = len(errors)
    detail = run()
    added = len(errors) - before

    if added:
        # The check's own detail is discarded here on purpose: it was computed on the assumption
        # that things were fine. The specifics are already in the ERROR lines, by name.
        headline = f"FAILED — {added} problem(s)"
    else:
        headline = str(detail)
        assert "FAILED" not in headline, (
            f"{label} reports failure but appended no error, so nothing would fail the run: "
            f"{headline!r}"
        )

    # `quiet` is for the self-test probe below and nothing else: its deliberate failure must not
    # be logged as one of this run's checks, nor printed, or every clean run would show a FAILED
    # line and teach the reader to ignore them.
    if not quiet:
        _STATUS_LOG.append((label, headline, added))
        print(f"{label}: {headline}", flush=True)
    return headline


def check_status_discipline(errors: List[str]) -> None:
    """Two guards on the pattern itself, so it stays a property and does not decay into a habit.

    First, the log must be self-consistent: a `FAILED` headline exactly when that check appended
    errors. Given `status()` that is nearly a tautology — which is the point, since it is what
    catches a later edit that computes a headline some other way.

    Second, and the one that actually stops the habit returning: no status line may be printed
    outside `status()`. That is a source-level check, because the defect was never in the logic — it
    was in someone reaching for `print()` and writing the headline by hand. A new check that does
    the same thing fails here rather than in six months' reading.
    """
    for label, headline, added in _STATUS_LOG:
        if bool(added) != headline.startswith("FAILED"):
            errors.append(
                f"status discipline: {label!r} reported {headline!r} having appended {added} "
                f"error(s) — the headline and the outcome disagree"
            )

    # The whole file, not the part after `status()`: an earlier draft scanned only from the helper
    # downwards, which would have let a status line added above it through. `status()`'s own print
    # is not a match because its format string opens with `{label}`, not a literal.
    source = Path(__file__).read_text(encoding="utf-8")
    stray = re.findall(r'^\s*print\(f"[a-z][a-z .-]*: \{', source, re.MULTILINE)
    if stray:
        errors.append(
            f"status discipline: {len(stray)} status line(s) printed outside status() — route them "
            f"through it so the verdict is derived from the error count, not written by hand"
        )


def _status_self_test(errors: List[str]) -> None:
    """Prove the choke point overrides a lying check, on a check written to lie.

    The mutation the fix is worth: a check that appends an error and then claims everything is fine
    — the exact shape that shipped twice. Expressed here deliberately, against a throwaway error
    list, and asserted to come out `FAILED`. If someone rewrites `status()` so the detail wins, this
    is what stops it.
    """
    scratch: List[str] = []

    def liar() -> str:
        scratch.append("a real problem")
        return "all good — 100 things verified"

    headline = status(scratch, "status self-test", liar, quiet=True)
    if not headline.startswith("FAILED"):
        errors.append(
            f"status self-test: a check that appended an error still reported {headline!r} — the "
            f"choke point is not deriving the verdict from the error count"
        )
    if "all good" in headline:
        errors.append("status self-test: the lying check's own wording survived into the headline")


def generated_manifest() -> Dict[str, str]:
    """`record/.generated`, as `{generated path: the record file it shows, or ""}`.

    An explicit list rather than a name heuristic, and the reason is a caught bug: the first version
    guessed — skip `index.html`, skip an `.html` beside a text file, skip dotfiles — and that guess
    silently excluded thirteen real engine files (`data/.gitkeep`) from the byte-for-byte
    comparison. The check still passed; it was just checking less than it claimed. The generator now
    writes down what it made, so record and scaffolding are told apart by record, not by resemblance.

    The second field arrived with the gate links. A `.rs` file is served by GitHub Pages as a
    download, so the appendix points at the view page instead — and without this mapping that link
    would look like a dependency on `…/gate.html`, a file the record does not contain, and the
    footprint check would reject it. The map says which record file a view stands for.
    """
    listing = RECORD_DIR / ".generated"
    if not listing.exists():
        return {}
    out: Dict[str, str] = {}
    for line in listing.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        generated, _, source = line.partition("\t")
        out[generated.strip()] = source.strip()
    return out


def generated_paths() -> set:
    """Just the paths — the set the byte-for-byte comparison skips."""
    return set(generated_manifest())


def snapshot_files(root: Path, cited: Sequence[str], skip: set = frozenset()) -> Dict[str, bytes]:
    """The **verbatim** files under one root, keyed by record-relative path.

    Walks only the cited paths, so a stray file elsewhere under `record/` is never mistaken for
    evidence. `skip` carries the generated view layer when reading the snapshot, and is empty when
    reading the engine — which has no scaffolding to skip.
    """
    out: Dict[str, bytes] = {}
    for entry in cited:
        base = root / entry
        candidates = sorted(base.rglob("*")) if base.is_dir() else [base]
        for path in candidates:
            if not path.is_file():
                continue
            rel = path.relative_to(root).as_posix()
            if rel in skip:
                continue
            out[rel] = path.read_bytes()
    return out


def check_snapshot_integrity(cited: Sequence[str], errors: List[str]) -> str:
    """Layer 2 — **`record/` is still byte-for-byte the engine at the pinned commit.**

    This is the check that turns a committed copy into evidence. Layer 1 verifies every quotation
    against `record/`, and would pass just as happily against a `record/` somebody had edited to
    agree with the prose; on its own it proves the book is self-consistent, not that it is true.
    Here the snapshot is diffed against the real repository — same commit, same bytes — and any
    difference at all is a failure naming the file.

    It can only run when the engine is reachable, which for a private repository means locally, or in
    CI with a token. When it cannot run it returns a status saying so and asserts nothing, because a
    check that quietly skips is worse than one that is absent: it teaches people the green tick means
    something it does not.
    """
    if not FETCHED_DIR.exists():
        return "unverified — .record/ not fetched"

    engine = snapshot_files(FETCHED_DIR, cited)
    committed = snapshot_files(RECORD_DIR, cited, skip=generated_paths())

    for rel in sorted(set(engine) | set(committed)):
        if rel not in committed:
            errors.append(f"snapshot integrity: {rel} is in the engine but missing from record/")
        elif rel not in engine:
            errors.append(f"snapshot integrity: record/{rel} is not in the engine at this commit")
        elif engine[rel] != committed[rel]:
            errors.append(
                f"snapshot integrity: record/{rel} differs from the engine at the pinned commit — "
                f"re-run `tools/snapshot_record.sh`; if the bytes changed on purpose, that is a "
                f"record bump and belongs in record.lock"
            )

    # Only what was observed. Whether that counts as a pass is `status()`'s call, derived from the
    # errors above — this function no longer gets to characterise its own run.
    return f"verified — {len(committed)} files byte-for-byte"


def check_record(manifest: Dict[str, object], errors: List[str]) -> str:
    """The record contract: the right repository, the pinned commit, the declared files, present.

    Three things must hold before any quotation is trusted:

    1. `record.lock` names a repository and a full commit id;
    2. its path list is exactly what `edition.json` and the chapters depend on, so the lock cannot
       quietly under-declare the footprint it is pinning; and
    3. the committed snapshot at `record/` carries every cited path, and is stamped with that commit.

    Note what is *not* here any more: engine access. Quotations are checked against `record/`, which
    every clone has, so the gate holds on a machine that has never seen the engine. Proving the
    snapshot still equals the engine is `check_snapshot_integrity`'s job, and it is separate
    precisely because it is the half that cannot always run.
    """
    lock = load_lock()
    if not lock:
        errors.append(
            "record.lock is missing or empty — this edition quotes another repository and must "
            "pin the commit it quotes"
        )
        return "unpinned"

    repo = (lock.get("repo") or ["?"])[0]
    sha = (lock.get("sha") or [""])[0]
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        errors.append(f"record.lock: sha must be a full 40-character commit id, not {sha!r}")

    declared = declared_record_paths(manifest)
    listed = sorted(set(lock.get("path", [])))
    if listed != declared:
        missing = [p for p in declared if p not in listed]
        extra = [p for p in listed if p not in declared]
        errors.append(
            "record.lock's path list is not what edition.json depends on — "
            f"missing {missing!r}, stale {extra!r}"
        )

    if not RECORD_DIR.exists():
        errors.append(
            f"the record snapshot is absent: {RECORD_DIR.name}/ is not in this repository. It is "
            f"committed, so this is not a fetch — restore it, or re-derive it with "
            f"`tools/fetch_record.sh && tools/snapshot_record.sh`"
        )
        return f"{repo}@{sha[:12]} (NO SNAPSHOT)"

    stamp = RECORD_DIR / SNAPSHOT_STAMP
    stamped = stamp.read_text(encoding="utf-8").strip() if stamp.exists() else ""
    if stamped != sha:
        errors.append(
            f"the snapshot is stamped {stamped or 'nothing'} but record.lock pins {sha} — "
            f"re-run `tools/fetch_record.sh && tools/snapshot_record.sh`. Bumping the pin without "
            f"re-snapshotting would leave the book quoting one commit and citing another"
        )

    for entry in declared:
        if not (RECORD_DIR / entry).exists():
            errors.append(f"the snapshot is missing a cited path: {entry}")

    # The symlink is load-bearing, not decoration: it is how mdBook carries the snapshot into the
    # built book, and therefore how a record link resolves on the published site.
    link = EDITION_DIR / "chapters" / RECORD_DIR.name
    if not link.is_symlink():
        errors.append(
            "chapters/record is not a symlink to ../record — without it mdBook cannot copy the "
            "snapshot into the built book and every record link is dead on the published site"
        )

    return f"{repo}@{sha[:12]}"


def reading_order(errors: List[str]) -> List[str]:
    """The chapter slugs, in reading order, **from `chapters/SUMMARY.md` and nowhere else**.

    SUMMARY.md is mdBook's own table of contents, so it is the one file that cannot be wrong without
    the book being visibly wrong. Making it the sole ordering authority is what lets an insertion be a
    one-line diff: filenames carry no positions, `edition.json` is keyed by slug and stores none, and
    the appendix's displayed section numbers are derived here rather than written down anywhere.
    """
    summary = SUMMARY_PATH.read_text(encoding="utf-8")
    slugs = [Path(target).stem for target in SUMMARY_LINK.findall(summary)]
    if not slugs:
        errors.append("chapters/SUMMARY.md lists no chapters — it is the reading order")
        return []
    appendix_slug = Path(APPENDIX_FILE).stem
    if slugs[-1] != appendix_slug:
        errors.append(
            f"chapters/SUMMARY.md must end with the appendix ({appendix_slug!r}); it ends with "
            f"{slugs[-1]!r}"
        )
    duplicates = [x for i, x in enumerate(slugs) if x in slugs[:i]]
    if duplicates:
        errors.append(f"chapters/SUMMARY.md lists a chapter twice: {duplicates!r}")
    return slugs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rendered",
        action="store_true",
        help="also check the output produced by `mdbook build`",
    )
    args = parser.parse_args()

    manifest = load_manifest()
    chapters: Dict[str, object] = dict(manifest["chapters"])
    sections: Dict[str, object] = dict(manifest["appendix"]["sections"])
    forbidden = list(manifest["forbidden_chapter_phrases"])
    forbidden_patterns = list(manifest.get("forbidden_chapter_patterns", []))
    errors: List[str] = []

    # The record contract first, and it short-circuits: with no snapshot every declared entry, gate,
    # figure and quotation source is "missing", and a hundred errors saying that would bury the one
    # that explains why.
    _status_self_test(errors)
    pin = status(errors, "record", lambda: check_record(manifest, errors))
    if not RECORD_DIR.exists():
        return report(errors, [], {}, manifest, args)

    # Layer 2. Reported on its own line, always — including when it could not run, because a reader
    # of this output should never have to guess which half of the contract was checked.
    status(
        errors,
        "snapshot integrity",
        lambda: check_snapshot_integrity(declared_record_paths(manifest), errors),
    )

    # The engine contract, the record's mirror image: the record is what the book quotes, the
    # engine is what it runs. Two lines, the same split — what every clone can check, and what only
    # a machine with the private engine on it can. The second says `unverified` rather than passing.
    status(errors, "engine", lambda: check_engine(errors))
    status(errors, "engine integrity", lambda: check_engine_integrity(errors))

    # The guard is tested before it is trusted, on every run — not only under --self-test.
    self_test(manifest, errors)

    # So is the napkin arithmetic. Reported on its own line: "computed while this page was built" is
    # a promise about every build, so the check that keeps it should be visible in every run.
    status(errors, "napkin self-test", lambda: check_napkin_determinism(errors))

    # The captions are prose too, and until 2026-09-02 they were the only prose in the book that
    # nothing measured — the grain band reads the source, where a token is one word.
    status(errors, "napkin captions", lambda: check_napkin_captions(errors))

    # And the chapter's own sentences must not contradict the tokens they sit next to. Every other
    # check here reads what the tool wrote; this one reads what the author wrote.
    status(errors, "napkin contradictions", lambda: check_napkin_contradictions(errors))

    # And so is the canonical labeling. `CANON.md` promises the book draws the tetrahedron one way,
    # derived from the napkin; this is the line that makes drift between the two fail the build
    # rather than reach a reader as a second, differently-labelled picture of the same object.
    status(errors, "canon self-test", lambda: check_canon(errors))

    # And the demos, which run chapters 1–5 on the vendored engine in the reader's browser. Three
    # lines, because three different things can be wrong: the Python that used to be the engine can
    # stop reproducing it, the generated step scaffolding can fall behind a renumber, and a page can
    # render a number the engine never produced. The last says `unverified` rather than passing when
    # node is not installed.
    status(errors, "napkin export", lambda: check_napkin_export(errors))
    if not args.rendered:
        status(errors, "demo steps", lambda: check_demo_steps(errors))
        status(errors, "demo cross-check", lambda: check_demo_cross_check(errors))
        status(errors, "demo attacks", lambda: check_demo_attacks(errors))
        status(errors, "beat attacks", lambda: check_beat_attacks(errors))

    appendix_file = str(manifest["appendix"]["file"])
    if appendix_file != APPENDIX_FILE:
        errors.append(
            f"the appendix path is wired into this checker as {APPENDIX_FILE!r}; "
            f"edition.json says {appendix_file!r}"
        )

    order = reading_order(errors)
    narrative = [slug for slug in order if slug != Path(APPENDIX_FILE).stem]
    if not narrative:
        return report(errors, [], {}, manifest, args)

    on_disk = sorted(
        path.stem
        for path in (EDITION_DIR / "chapters").glob("*.md")
        if path.name != "SUMMARY.md"
    )
    if sorted(order) != on_disk:
        errors.append(
            "the files on disk and chapters/SUMMARY.md disagree: "
            f"{on_disk!r} != {sorted(order)!r}"
        )
    if sorted(chapters) != sorted(narrative):
        errors.append(
            "edition.json's chapters and chapters/SUMMARY.md disagree: "
            f"{sorted(chapters)!r} != {sorted(narrative)!r}"
        )
    if sorted(sections) != sorted(narrative):
        errors.append(
            "every chapter needs an appendix section, and only chapters may have one: "
            f"{sorted(sections)!r} != {sorted(narrative)!r}"
        )
    if errors:
        return report(errors, narrative, sections, manifest, args)

    # The displayed section number is the chapter's position in the reading order — derived, never
    # stored, so an insertion renumbers the appendix and nothing else.
    numbers = {slug: f"{i:02d}" for i, slug in enumerate(narrative)}

    check_appendix(manifest, numbers, narrative, forbidden, forbidden_patterns, errors)
    check_retired_phrasings(manifest, narrative, errors)

    for index, slug in enumerate(narrative):
        check_chapter(
            slug,
            dict(chapters[slug]),
            dict(sections[slug]),
            numbers[slug],
            set(narrative),
            forbidden,
            forbidden_patterns,
            index == len(narrative) - 1,
            errors,
        )

    if args.rendered:
        check_rendered(order, sections, errors)
        # Each on its own line, because each is a promise made to a reader rather than to a
        # maintainer: that the link beside a heading opens a note about *that* heading, that opening
        # a page of this book contacts nobody but this site, and that the demos are actually there.
        status(errors, "reader-note links", lambda: check_note_links(order, errors))
        status(errors, "external assets", lambda: check_no_external_assets(order, errors))
        status(errors, "demos published", lambda: check_demos_published(errors))
        status(errors, "engine published", lambda: check_engine_published(errors))

    return report(errors, narrative, sections, manifest, args)

    check_appendix(manifest, forbidden, forbidden_patterns, errors)

    for index, entry in enumerate(entries):
        check_chapter(
            entry,
            sections[index],
            forbidden,
            forbidden_patterns,
            index == len(entries) - 1,
            errors,
        )

    if args.rendered:
        check_rendered(list(entries) + [{"file": appendix_file}], errors)

    return report(errors, entries, sections, manifest, args)


def report(
    errors: List[str],
    entries: Sequence[Dict[str, object]],
    sections: Sequence[Dict[str, object]],
    manifest: Dict[str, object],
    args: argparse.Namespace,
) -> int:
    # Last thing before the verdict: audit the status lines this run printed. `check_status_discipline`
    # can itself add errors, so it runs before they are counted — a checker that could not police its
    # own output would be an odd one to trust about a book's.
    check_status_discipline(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"Our Bubble edition check failed with {len(errors)} error(s).", file=sys.stderr)
        return 1

    quote_count = sum(
        len(dict(section).get("record_quotes", [])) for section in dict(sections).values()
    )
    print(
        f"Our Bubble edition check passed: {len(entries)} chapters + the appendix, "
        f"{quote_count} record quotations anchored in the appendix, "
        f"{len(list(manifest.get('forbidden_probe_texts', [])))} exclusion probes refused, "
        f"{len(list(manifest.get('retired_phrasings', [])))} retired phrasings absent from every "
        f"chapter in any wrapping, markup or punctuation — they are matched on their words, and a "
        f"rewording is not refused — each proved by the probe declared beside it, "
        f"all links, hand-offs, slug bridges and derived section numbers valid"
        f"{' in source and rendered output' if args.rendered else ''}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
