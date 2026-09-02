#!/usr/bin/env python3
"""Validate the Our Bubble reader edition against its current evidence sources."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


EDITION_DIR = Path(__file__).resolve().parent

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


def check_rendered(order: Sequence[str], errors: List[str]) -> None:
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

    drifted = 0
    for rel in sorted(set(engine) | set(committed)):
        if rel not in committed:
            errors.append(f"snapshot integrity: {rel} is in the engine but missing from record/")
            drifted += 1
        elif rel not in engine:
            errors.append(f"snapshot integrity: record/{rel} is not in the engine at this commit")
            drifted += 1
        elif engine[rel] != committed[rel]:
            errors.append(
                f"snapshot integrity: record/{rel} differs from the engine at the pinned commit — "
                f"re-run `tools/snapshot_record.sh`; if the bytes changed on purpose, that is a "
                f"record bump and belongs in record.lock"
            )
            drifted += 1

    # The status line has to be the *outcome*, not the fact that the comparison happened. A tamper
    # test caught this reading "verified — 150 files byte-for-byte" on the same run that reported
    # drift: the errors were correct and the headline contradicted them, which is the one thing a
    # status line must never do.
    if drifted:
        return f"FAILED — {drifted} of {len(committed)} files differ from the engine"
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
    pin = check_record(manifest, errors)
    print(f"record: {pin}", flush=True)
    if not RECORD_DIR.exists():
        return report(errors, [], {}, manifest, args)

    # Layer 2. Reported on its own line, always — including when it could not run, because a reader
    # of this output should never have to guess which half of the contract was checked.
    integrity = check_snapshot_integrity(declared_record_paths(manifest), errors)
    print(f"snapshot integrity: {integrity}", flush=True)

    # The guard is tested before it is trusted, on every run — not only under --self-test.
    self_test(manifest, errors)

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
        check_rendered(order, errors)

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
