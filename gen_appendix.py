"""Build `chapters/the-simulations.md` from `edition.json` and the order in `SUMMARY.md`.

Importable, so the mdBook preprocessor and the command line share one implementation:

    render()  -> the appendix markdown, as a string
    write()   -> writes it if it differs; returns (markdown, changed)

Run directly to regenerate the committed file. `preprocessor.py` calls `write()` on every
`mdbook build`, which is what makes the appendix a generated artifact rather than a maintained one.
"""
import json, pathlib, re

ED = pathlib.Path(__file__).resolve().parent
TARGET = ED / "chapters" / "the-simulations.md"


def render() -> str:
    m = json.load(open(ED / "edition.json"))
    summary = (ED / "chapters/SUMMARY.md").read_text()
    order = [pathlib.Path(t).stem
             for t in re.findall(r"^- \[[^\]]+\]\(([^)]+\.md)\)\s*$", summary, re.M)]
    ap_slug = pathlib.Path(m["appendix"]["file"]).stem
    narrative = [s for s in order if s != ap_slug]
    secs = m["appendix"]["sections"]
    # `record/` is the committed snapshot: the cited files, verbatim, from UniForge at the SHA
    # pinned in `record.lock`. Citing the snapshot rather than the fetched `.record/` is what lets
    # these links resolve for a reader who has no access to the engine — on the published site, and
    # in a clean clone.
    #
    # The prefix has no `../` on purpose. `chapters/record` is a symlink to it, so `record/…`
    # resolves three ways with one spelling: in the repository browser (from `chapters/`), in the
    # built book (mdBook copies the tree to `book/record/`), and on the published site.
    #
    # One wrinkle, and it is about what the browser does rather than what the link says. mdBook
    # rewrites a `*.md` link to `*.html` on its own, which lands on the generated view — good. It
    # leaves `*.rs` alone, and GitHub Pages serves `.rs` as a type browsers download instead of
    # display. The gate source is exactly what a skeptic clicks, so those point at the view page,
    # which shows the file's own bytes. `record/.generated` records that the view stands for the
    # `.rs` file, so the footprint check still sees a dependency on the gate itself.
    RENDERED_ONLY = (".rs",)

    def rel(p):
        for suffix in RENDERED_ONLY:
            if p.endswith(suffix):
                return "record/" + p[: -len(suffix)] + ".html"
        return "record/" + p

    L=["# Appendix · The Simulations\n",
    """> **Scope.** Everything on this page describes computations inside a **toy** discrete lattice. The
> rung labels, gates, figures and commands below are the project's own record; they are not claims
> about nature. Words such as *vacuum*, *material*, *light cone* and *Ising* name patterns in the
> model.
> See [`FIREWALL.md`](../FIREWALL.md).
""",
    """This appendix carries everything the narrative deliberately leaves out: which registered
experiment each chapter rests on, its gate, its data-true figure, the exact numbers the chapter
quotes and the file each one is carried by, and the commands that regenerate them.

The split is the point. A reader following the story should not have to step over a rung label to
finish a sentence; a reader checking the story should not have to hunt for the provenance.

**This book has a calculation system inside it.** It is a living document: when it is built, it goes
and reads the record. The section numbers are worked out from the table of
contents. The figures the chapters link to are drawn from their own runs' output, and are redrawn
whenever those runs are. So none of what follows was transcribed by hand once and left to drift: it is
what the record said when this copy of the book was made, and a fresh copy asks again. This page is
written by [`gen_appendix.py`](../gen_appendix.py), which the build runs before rendering; the checking
is done by [`check_edition.py`](../check_edition.py).

**Where the checking stops.** Every figure with a `read from` file beside it is checked, verbatim,
against that file. That column is the boundary. The history section below carries figures that sit
outside it deliberately, because they are not ours to check — they are checkable against the historical
record instead, which is a different and in some ways better guarantee.

Some sections cite no experiment of ours at all — the front door, the opening on method, and the
history chapter — and they say so rather than being left out, because a reader should be able to
tell *no evidence was cited* from *no evidence exists*. The closing chapter rests on commands you
run yourself.

One section per chapter, in reading order, **numbered from `00`** to match the order in
`chapters/SUMMARY.md`. Each also carries a stable anchor keyed to its chapter's name, which is what
the chapters link to.

**Leaving a note.** Every section in this book carries a small link at its heading — *Leave a note on
this section* — and it opens a short form about how that section read to you. A note is a gift and
not a test: "I lost the thread here" is a complete one, and you need not be right about any of the
maths. Sending it does need a free GitHub account, which is the honest limit of a way to write to us
that asks you for no email address and loads nothing onto the page you are reading.
"""]
    for i,slug in enumerate(narrative):
        s=secs[slug]; n=f"{i:02d}"
        L.append(f'---\n\n<a id="s-{slug}"></a>\n\n## §{n} · {s["title"]}\n')
        L.append(f"**The chapter.** [{slug}.md]({slug}.md)\n")
        if s.get('rungs'):
            L.append("**Registered rungs.**\n"); L+=[f"- {r}" for r in s['rungs']]; L.append("")
        if s.get('note'):
            L.append(s['note']+"\n")
        if s.get('history'):
            # This sentence has been rewritten twice by the chapter moving under it, so it says only
            # what is true of whatever is in the section. N8 (proofread, tranche B round 2) removed
            # "no rung, no gate and no figure corresponds to any of it" when the chapter briefly
            # carried the record's two self-corrections in its own last beats. Tranche E (issue #70)
            # moved the chapter to second in the book and left those beats behind in the chapter that
            # owns the misses, so the section is history and nothing else again — and the claim is
            # asserted from the section rather than typed, because that is the half that kept going
            # stale.
            ours = [key for key in ("rungs", "entries", "gates", "figures", "record_quotes")
                    if s.get(key)]
            L.append("**What this chapter recounts.** Measurement history, and it is not work of "
                     "ours" + (". What is ours is listed beside it." if ours else " — no rung, "
                     "gate, figure or quoted number here corresponds to any of it.") + " The "
                     "history is listed in the order the chapter tells it, so a reader can check "
                     "the chapter against the historical record rather than against us.\n")
            L+=[f"- {h}" for h in s['history']]; L.append("")
            L.append("What the book carries forward is the **method** — measure, state your resolution, let "
                     "a finer instrument overturn you — never the discoveries. The record's own two "
                     "self-corrections are set against that history much later, in the chapter that "
                     "published the misses.\n")
        for key,label in (('entries',"**Lab entries.** Each carries its own `spec.md` (the question, registered first), `eval.md` (the verdict) and `PROVENANCE.md`.\n"),
                          ('gates',"**Gates.** The tests that re-run the experiment and refuse to pass unless the answer comes back as registered.\n"),
                          ('figures',"**Data-true figures.** Rendered from the run's own committed output — no analogy art.\n"),
                          ('standards',"**Standards and record this section rests on.**\n")):
            if s.get(key):
                L.append(label); L+=[f"- [`{t}`]({rel(t)})" for t in s[key]]; L.append("")
        if s.get('record_quotes'):
            L.append("**Numbers the narrative may quote.**\n")
            if any(q.get('what') for q in s['record_quotes']):
                L.append("| value | what it is | read from |"); L.append("|---|---|---|")
                for q in s['record_quotes']:
                    L.append(f"| `{q['text']}` | {q.get('what','')} | [`{q['source']}`]({rel(q['source'])}) |")
            else:
                L.append("| value | read from |"); L.append("|---|---|")
                for q in s['record_quotes']:
                    L.append(f"| `{q['text']}` | [`{q['source']}`]({rel(q['source'])}) |")
            L.append("")
        elif s.get('history'):
            L.append("**Numbers.** None declared, and none checked here. The dates and angles in the "
                     "list above are historical: they are checkable against the historical record "
                     "rather than against this repository, which is the one guarantee this book "
                     "cannot give you itself.\n")
        elif s.get('computed'):
            # The napkin chapters quote nothing and yet are full of numbers: they recompute them
            # while the book is built. Saying "None" here is literally true and useless — a reader
            # checking the provenance of the ten-tick table would land on a section telling her
            # there is no table. Say where the numbers come from instead.
            L.append("**Numbers.** None quoted. Every number in this section's chapter is worked "
                     "out while the book is built — by [`tools/napkin.py`](../tools/napkin.py), "
                     "which holds the rule and the tables, and "
                     "[`tools/octahedron.py`](../tools/octahedron.py), which holds the shapes "
                     "larger than one tetrahedron — and re-derived on every build, so the thing to "
                     "check is not a file but the arithmetic, which the chapter shows you.\n")
        else:
            L.append("**Numbers.** None. This section's chapter carries no quoted measurement.\n")
        if s.get('commands'):
            # `cargo` commands belong to the engine, which is no longer the repository you are
            # standing in — so the instruction has to say which root it means. `.record/` is the
            # pinned checkout the fetcher makes, and is exactly the commit these numbers came from.
            root = ("the engine checkout (`.record/`, or your own UniForge clone)"
                    if any(c.startswith("cargo") for c in s['commands']) else "this repository's root")
            L.append(f"**Regenerate.** From {root}:\n"); L.append("```sh")
            if any(c.startswith("cargo") for c in s['commands']): L.append("cd core")
            L+=s['commands']; L.append("```\n")
    return "\n".join(L).rstrip() + "\n"


def write():
    """Write the appendix if it differs from what is on disk. Returns (markdown, changed)."""
    markdown = render()
    changed = (not TARGET.exists()) or TARGET.read_text() != markdown
    if changed:
        TARGET.write_text(markdown)
    return markdown, changed


if __name__ == "__main__":
    _, changed = write()
    print("appendix regenerated" if changed else "appendix already up to date")
