#!/usr/bin/env python3
"""Validate the Our Bubble reader edition against its current evidence sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


EDITION_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(EDITION_DIR / "tools"))

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
        rendered = napkin.render(name)
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
        rendered = napkin.render(name)
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
    all computed from `napkin.simplices`. Derived is only worth something if the derivation is
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
        f"all links, hand-offs, slug bridges and derived section numbers valid"
        f"{' in source and rendered output' if args.rendered else ''}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
