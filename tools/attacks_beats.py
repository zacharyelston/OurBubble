#!/usr/bin/env python3
"""The mutations for the beat-id contract — one for each rule that can be broken by an edit.

FIREWALL: this is tooling for a book about a toy DEC lattice. Nothing here is a claim about nature.

**Standing rule (2026-09-03): no new guard lands without its mutation, in the same commit.** The
demos have had that since `demos/attacks.mjs`; the Python checks had nothing, so the beat contract
gets its own suite here rather than a paragraph in a commit message claiming the check bites.

How it works, and it is `attacks.mjs`'s shape on purpose: per mutation, the repository is copied
into a fresh directory under the system temp directory, the mutation is applied **to the copy**,
`tools/beat_coverage.py` is run from the copy, its output is required to contain the phrase named
here, and the copy is deleted. The working tree is never written to. A mutation whose needle is not
found fails too — that is how a refactor says an attack has stopped testing anything — and so does a
needle that occurs more than once, because an ambiguous needle mutates whichever copy comes first,
which is not a test of anything in particular.

    python3 tools/attacks_beats.py

**And the count of the guard's complaint sites is pinned**, the way `demos/attacks.baseline.json`
pins the demos'. A rule added to `beat_coverage.py` moves that number, and the suite then fails
asking for the mutation — which is the standing rule mechanised on this side too, rather than
remembered. Two sites have no mutation and are named in `UNCOVERED` with the reason: both need a
file to be *deleted*, and a mutation here is a substitution.

Exit 0 and every mutation went red by name; exit 1 and one of them did not, which means the check
would have let it through.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, NamedTuple

ROOT = Path(__file__).resolve().parent.parent

# What a copy needs to run the coverage tool: the contract, the prose, the tools and the checker it
# imports its word counter from. Not `book/`, `record/` or `engine/` — none of them is read.
COPIED = ("OUTLINE.md", "CONTINUUM.md", "chapters", "tools", "check_edition.py", "gen_appendix.py",
          "preprocessor.py", "demos/DEMOS.md", "edition.json", "book.toml", "README.md",
          "EDITION_STANDARD.md", "notes", ".claude")

# Every place `tools/beat_coverage.py` can complain, counted from its own source. Pinned, so a rule
# that lands without a mutation moves the number and this suite says so.
SITES = 18
COMPLAINT = re.compile(r'^\s*(?:problems\.append\(|return \[f")', re.M)

# The sites with no mutation, and why. Both want a file deleted, and every mutation here is a
# substitution on a copy — a suite that started deleting files from a tree it also verifies it did
# not touch would be trading one guarantee for another.
UNCOVERED = (
    "a chapter heading in OUTLINE.md with no beat lines under it at all",
    "one of the SCANNED files missing from the tree",
)


class Attack(NamedTuple):
    guard: str
    file: str
    frm: str
    to: str
    expect: str


# One chapter's markers, quoted once each, so a needle cannot drift without this file noticing.
SHAPE_2 = "<!-- beat the-shape-between.2 -->"
SHAPE_3 = "<!-- beat the-shape-between.3 -->"
SHAPE_5 = "<!-- beat the-shape-between.5 -->"

ATTACKS: tuple[Attack, ...] = (
    # ── the ids a chapter's markers claim ────────────────────────────────────────────────────────
    Attack(
        "a beat claimed twice, apart — a section moved or relabelled, not a split",
        "chapters/the-shape-between.md", SHAPE_5, SHAPE_2,
        "are claimed again after a later beat",
    ),
    Attack(
        "a gap in the markers: a beat no section claims",
        "chapters/the-shape-between.md", SHAPE_3, "<!-- beat the-shape-between.9 -->",
        "no section claims beat(s) ['the-shape-between.3']",
    ),
    Attack(
        "a marker in the wrong chapter's file",
        "chapters/the-shape-between.md", SHAPE_3, "<!-- beat make-it-move.3 -->",
        "name another chapter, in this chapter's file",
    ),
    Attack(
        "a thirteenth beat's marker",
        "chapters/the-shape-between.md", SHAPE_5, "<!-- beat the-shape-between.13 -->",
        "past the cap of 12 beats in a chapter",
    ),
    Attack(
        "a thirteenth beat in the outline itself",
        "OUTLINE.md",
        "5. Put an arrow on each of its twelve lines",
        "5. Put an arrow on each of its twelve lines and walk its eight outside faces: what?\n"
        "6. A sixth\n7. A seventh\n8. An eighth\n9. A ninth\n10. A tenth\n11. An eleventh\n"
        "12. A twelfth\n13. A thirteenth",
        "and a chapter is capped at 12",
    ),
    Attack(
        "a section that carries no marker at all",
        "chapters/the-shape-between.md", SHAPE_3 + "\n", "",
        "carry no `<!-- beat the-shape-between.n -->` marker",
    ),
    # ── the numbering the contract itself carries ────────────────────────────────────────────────
    Attack(
        "a hole in one chapter's outline numbering",
        "OUTLINE.md", "3. Count the new shape", "9. Count the new shape",
        "the outline's beat numbering has",
    ),
    Attack(
        "a chapter whose outline beats start at two",
        "OUTLINE.md", "1. Before I go and fetch more tetrahedra", "2. Before I go and fetch more",
        "the outline's beats start at 2, not 1",
    ),
    # ── the book-wide form, refused wherever it is written ───────────────────────────────────────
    Attack(
        "a stale book-wide beat number in OUTLINE.md",
        "OUTLINE.md", "So beat what-you-will-have.1 is the moves themselves",
        "So beat 35 is the moves themselves",
        "writes 'beat 35'",
    ),
    Attack(
        "a stale book-wide beat number in DEMOS.md's prose",
        "demos/DEMOS.md", "**The words belong to the book. The demo is the sim.**",
        "**The words belong to the book. The demo is the sim.** See beat 35.",
        "demos/DEMOS.md",
    ),
    Attack(
        "a stale book-wide beat number in CONTINUUM.md",
        "CONTINUUM.md", "## Active lanes", "## Active lanes\n\nSee beats 44–49.\n",
        "CONTINUUM.md",
    ),
    Attack(
        "a stale book-wide beat number in a chapter's prose",
        "chapters/the-shape-between.md", "Adding is not the only way to get something bigger.",
        "Adding is not the only way to get something bigger. See beat 43.",
        "chapters/the-shape-between.md",
    ),
    Attack(
        # A reviewer's (2026-09-04): the first version of the scan read the file line by line, and
        # a space pattern matches a newline, so this shape went green in four files at once.
        "a book-wide number hard-wrapped away from its own word",
        "chapters/the-shape-between.md", "Adding is not the only way to get something bigger.",
        "Adding is not the only way to get something bigger. It is beat\n43 of the book.",
        "writes 'beat 43'",
    ),
    Attack(
        "the marker schema `beat N` copied into a chapter's prose",
        "chapters/the-shape-between.md", "Adding is not the only way to get something bigger.",
        "Adding is not the only way to get something bigger. Write a beat N marker.",
        "writes 'beat N'",
    ),
    # ── an id that names nothing ─────────────────────────────────────────────────────────────────
    Attack(
        "a cross-reference to a beat its chapter has not got",
        "tools/oracle.py", "This is beat two-dots-and-a-line.10's move",
        "This is beat two-dots-and-a-line.87's move",
        "names two-dots-and-a-line.87, and two-dots-and-a-line has 10 beat(s)",
    ),
    Attack(
        "a cross-reference to a chapter the book has not got",
        "tools/oracle.py", "This is beat two-dots-and-a-line.10's move",
        "This is beat no-such-chapter.1's move",
        "chapters/SUMMARY.md has no chapter no-such-chapter",
    ),
    # ── the pairing of the reading order and the outline ─────────────────────────────────────────
    Attack(
        # The half-finished state of adding a chapter: the file and the SUMMARY line first. A
        # reviewer walked a whole extra chapter, markers and all, past the first version.
        "a chapter in the reading order with no block in the outline",
        "OUTLINE.md", "## 5 · The shape between", "## 55 · The shape between",
        "OUTLINE.md has no `## 5 · ` block for it",
    ),
    Attack(
        "a reading-order entry whose chapter file does not exist",
        "chapters/SUMMARY.md", "(the-shape-between.md)", "(the-shape-betwen.md)",
        "the-shape-betwen.md does not exist",
    ),
    # ── the markers' own order and grain ─────────────────────────────────────────────────────────
    Attack(
        "markers that stop ascending",
        "chapters/the-shape-between.md", SHAPE_2, "<!-- beat the-shape-between.5 -->",
        "which does not ascend",
    ),
    Attack(
        "a marker numbered with a leading zero",
        "chapters/the-shape-between.md", SHAPE_3, "<!-- beat the-shape-between.03 -->",
        "carry no `<!-- beat the-shape-between.n -->` marker",
    ),
    Attack(
        "a section grown past the hard ceiling",
        "chapters/the-shape-between.md", "Adding is not the only way to get something bigger.",
        "Adding is not the only way to get something bigger. " + ("word " * 240),
        "over the 220-word hard ceiling",
    ),
)


def copy_of_the_tree(at: Path) -> None:
    for name in COPIED:
        source = ROOT / name
        target = at / name
        target.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, target)
        else:
            shutil.copy2(source, target)


def run_coverage(at: Path) -> tuple[int, str]:
    finished = subprocess.run(  # noqa: S603 - a fixed argv, no shell
        [sys.executable, "-B", str(at / "tools" / "beat_coverage.py")],
        capture_output=True, text=True, cwd=at, timeout=300, check=False,
    )
    return finished.returncode, (finished.stdout or "") + (finished.stderr or "")


def apply(attack: Attack, at: Path) -> List[str]:
    """Mutate the copy, or say why the mutation is stale. **Never touches the working tree.**"""
    path = at / attack.file
    text = path.read_text(encoding="utf-8")
    found = text.count(attack.frm)
    if found == 0:
        return [f"{attack.guard}: the needle is not in {attack.file} any more — this attack has "
                f"gone stale and is testing nothing"]
    if found > 1:
        return [f"{attack.guard}: the needle occurs {found} times in {attack.file}; an ambiguous "
                f"needle mutates whichever copy comes first, which is not a test"]
    path.write_text(text.replace(attack.frm, attack.to), encoding="utf-8")
    return []


def tree_state() -> str:
    return subprocess.run(  # noqa: S603 - a fixed argv, no shell
        ["git", "status", "--porcelain", "--", *COPIED],
        capture_output=True, text=True, cwd=ROOT, check=False,
    ).stdout.strip()


def site_problems() -> List[str]:
    """The guard's complaint sites, counted from its source against the pin. **Reads one file.**"""
    source = (ROOT / "tools" / "beat_coverage.py").read_text(encoding="utf-8")
    found = len(COMPLAINT.findall(source))
    if found == SITES:
        return []
    return [f"tools/beat_coverage.py has {found} place(s) that can complain and this suite is "
            f"pinned to {SITES}. A rule lands with the mutation that proves it bites, and with this "
            f"number, in the same commit — or, if it genuinely cannot be mutated, with a line in "
            f"UNCOVERED saying which and why"]


def main() -> int:
    before = tree_state()
    problems: List[str] = site_problems()

    # The unmutated tree first: an attack suite that cannot tell red from red proves nothing.
    with tempfile.TemporaryDirectory(prefix="ourbubble-beats-") as scratch:
        at = Path(scratch)
        copy_of_the_tree(at)
        code, output = run_coverage(at)
    if code != 0:
        print(output)
        print("PROBLEM: the unmutated copy already fails beat_coverage.py, so no mutation below "
              "would mean anything. Nothing else was run.")
        return 1
    print("  the unmutated copy passes")

    for attack in ATTACKS:
        with tempfile.TemporaryDirectory(prefix="ourbubble-beats-") as scratch:
            at = Path(scratch)
            copy_of_the_tree(at)
            stale = apply(attack, at)
            if stale:
                problems += stale
                print(f"  STALE  {attack.guard}")
                continue
            code, output = run_coverage(at)
        if code == 0:
            problems.append(f"{attack.guard}: beat_coverage.py exited 0 — the check let it through")
            print(f"  GREEN  {attack.guard}")
        elif attack.expect not in output:
            problems.append(f"{attack.guard}: beat_coverage.py failed, but not by name — it never "
                            f"printed {attack.expect!r}")
            print(f"  WRONG  {attack.guard}")
        else:
            print(f"  red    {attack.guard}")

    after = tree_state()
    if after != before:
        problems.append("this suite changed the working tree, which it must never do: "
                        f"{after!r}")

    if problems:
        print("\n" + "\n".join("PROBLEM: " + p for p in problems))
        return 1
    print(f"\nbeat attacks: {len(ATTACKS)} mutation(s), every one refused by name; "
          f"tools/beat_coverage.py's {SITES} complaint site(s) counted from its own source, "
          f"{len(UNCOVERED)} of them named as having no mutation and why; and the working tree "
          f"untouched.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
