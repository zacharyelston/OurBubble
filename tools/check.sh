#!/usr/bin/env bash
#
# Tier 0 for this repository — the pass to run before every push.
#
# The order matters, and it is the order of trust:
#
#   1. fetch the pinned engine, if it is reachable at all  (soft: no engine access is not a failure)
#   2. check the edition — the record's two layers, the ENGINE's three, plus the demos:
#        · snapshot integrity, when step 1 succeeded: `record/` is the engine at the pinned commit,
#          byte for byte. This is what makes the committed copy evidence rather than a copy.
#        · quotations, always: every declared number verbatim in `record/`. Needs no engine access,
#          so a clean clone and the published site are gated exactly as strongly as a dev box.
#        · the engine, in two lines: every file under `engine/` hashes to what `engine.lock` says
#          and the vendored wasm answers the census question with the vendored JSON's own bytes
#          (always, in any clone); and, when UNIFORGE_SRC points at a UniForge checkout at the
#          pinned commit, a fresh export from it reproduces the vendored bytes. The second reads
#          "unverified" rather than passing when the private engine is not on the machine.
#        · the demos, in three lines: `demos/data/napkin.json` is what the napkin now exports;
#          `demos/steps.json` is what OUTLINE.md and the chapters' beat markers now derive, so a
#          renumber the demos have not caught up with is red rather than a page quoting last week's
#          ids; and every number the demo pages RENDER, on every surface, at every state of
#          every step, is one the vendored engine produced. That last check changed its meaning when
#          the engine was vendored: there is one implementation now, so it no longer compares two —
#          it holds the page to the engine. It needs node; without it that line reads "unverified"
#          rather than passing. It also prints each page's reader-facing word count, which is the
#          owner's budget and the thing most likely to drift back.
#        · and the demos' ATTACKS: every guard in that cross-check, with the mutation that proves it
#          bites. Standing rule (2026-09-03): no new guard lands without its mutation, in the same
#          commit. Five rounds running, a guard written to close a hole was found on the next read
#          to have a hole of its own, and every one of those had been "tested" by an attack run once
#          in a shell and thrown away. Each mutation is applied to a PRIVATE COPY of demos/ and
#          engine/ under the system temp directory, the cross-check is run from the copy and
#          required to complain BY NAME, and the copy is deleted: the working tree is never
#          written, and git is asked afterwards whether that held. It also reports how many of the
#          cross-check's own fail sites the mutations reached, against a committed baseline whose
#          floor it may not fall below and which may not be edited down without dropping the sites
#          it lists, so coverage cannot be walked down quietly. A mutation whose needle has gone stale fails too, which is
#          how a refactor says an attack has stopped testing anything. The suite refuses to run on
#          a dirty demos/ or engine/ and that line then reads "unverified" rather than failing. See
#          demos/DEMOS.md and demos/attacks.mjs.
#        · and the BEAT CONTRACT's attacks (`tools/attacks_beats.py`), the same arrangement in
#          Python for `tools/beat_coverage.py`: a beat claimed twice apart, a gap, a marker in the
#          wrong chapter's file, a thirteenth beat, and a book-wide beat number left in the outline,
#          in CONTINUUM.md, in DEMOS.md's prose or in a chapter — each applied to a private copy and
#          required to go red by name. The Python checks had no mutations at all until this.
#   3. the guards the edition check does not reach — `tools/engine_check.py` (the Python
#      oracle recomputes the whole payload and must reproduce the vendored engine's bytes exactly),
#      `tools/octahedron.py`'s own assertions (the geometry the octahedron chapter's appendix note
#      rests on), `tools/beat_coverage.py` (the prose against OUTLINE.md's beats, chapter by
#      chapter, capped at twelve, with no book-wide beat number left anywhere it scans), and
#      `tools/figures.mjs --check` (every figure a chapter shows is byte-for-byte the still the
#      demo code emits for that step, and the run refuses an altered byte, bytes that did not come
#      from the drawing code, and a page showing a figure nothing draws — before printing a line
#      claiming it did any of that).
#   4. build the book — which regenerates the appendix from the record
#   5. check the built pages, including that every record link resolves, that the built site
#      actually carries demos/ — the one piece of wiring nothing else would notice breaking — and
#      that every figure a BUILT page shows is one `tools/figures.mjs` drew. The built page is where
#      that is settled: a chapter can write an image half a dozen ways, and mdBook makes them all
#      the same `<img>` only here.
#
# The build can legitimately rewrite `chapters/the-simulations.md`, so the last thing this does is
# ask git whether it did: a dirty tree after a build means the record moved and the committed
# appendix had not caught up.
#
# Usage:  tools/check.sh          (or: make check)

set -euo pipefail

# No bytecode cache, anywhere in this pass. Python invalidates a .pyc on source mtime+size only, so a
# same-size edit landing in the same clock second is read from stale bytecode — a checker importing
# napkin.py or canon.py could then pass against a module the tree no longer contains (issue #31).
# Exported, so the preprocessor mdbook spawns in step 3 inherits it too.
export PYTHONDONTWRITEBYTECODE=1

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1m== %s\033[0m\n' "$1"; }

step "1/5 · fetch the pinned engine (for the integrity layer)"
# Soft on purpose. The engine is private; most readers cannot reach it, and the quotation gate does
# not need it. What is NOT soft is pretending the integrity layer ran — `check_edition.py` prints
# its own status line either way, and says "unverified" when it could not.
if tools/fetch_record.sh; then
  :
else
  echo "check: the engine is not reachable — snapshot integrity will report as unverified." >&2
  echo "       Quotations are still gated, against the committed record/ snapshot." >&2
fi

step "2/5 · check the edition (snapshot integrity + quotations)"
python3 -B check_edition.py

step "3/5 · the guards the edition check does not reach"
# Why these are here (a proofreader, 2026-09-02): both were run by nothing automated, and both
# back claims the book makes. `octahedron.py` asserts the geometry the octahedron chapter's
# appendix note rests on — the 1:1 face pairing, one line in seven, 13/7×, "never comes home" —
# and eight of its audit functions could be gutted with tier 0 staying green, because
# `check_edition.py` only reaches the seven functions the napkin tokens call. `beat_coverage.py`
# is the only thing that checks the prose against OUTLINE.md's beats at all, and it is what
# caught a double-applied renumbering that `renumber_beats.py`'s own self-check waved through.
# Together they cost under a second.
# `engine_check.py` is the first of them and the newest (2026-09-02): the book has ONE engine now,
# UniForge's `napkin` crate, vendored under `engine/`. The Python that used to be the engine is kept
# as an independent recomputation of it, and this is where the two are required to agree byte for
# byte. Two implementations sharing no code, no arithmetic library and no language, agreeing on
# 22 969 bytes, is what makes a number on a page a fact about the object rather than about a program.
python3 -B tools/engine_check.py
python3 -B tools/octahedron.py > /dev/null
# The guard's own last line, printed rather than restated: a hardcoded echo beside a discarded
# pass line is a status nobody verified, and this one named the cap and the ordering while omitting
# the two halves the beat contract is actually about (a reviewer, 2026-09-04).
echo "octahedron.py: every audit asserted"
python3 -B tools/beat_coverage.py | tail -1
# And the chapters' figures, which are stills of the demo's own drawings rather than pictures anyone
# drew: the committed SVG has to be byte-for-byte what `demos/` emits today. A figure generated once
# and then committed is a figure that drifts from the code it claims to be a picture of, and the
# drift is invisible — the page still shows something plausible. `--check` also mutates one of its
# own emitted figures by a byte and requires its comparison to catch that, so this line cannot go
# green with the comparison switched off. Without node it says so and the pass goes on, the same way
# the demo cross-check does.
if command -v node >/dev/null 2>&1; then
  node tools/figures.mjs --check
else
  echo "figures.mjs: unverified — node is not installed"
fi

step "4/5 · build the book"
command -v mdbook >/dev/null 2>&1 || {
  echo "check: mdbook is not installed — see the README (cargo install mdbook, or a release tarball)" >&2
  exit 1
}
mdbook build

step "5/5 · check the rendered pages and every record link"
python3 -B check_edition.py --rendered
# And the figures a reader is actually served. The source-side half of this ran in step 3; this is
# the one that decides, and it asks what each built page REACHES FOR rather than which tag reached:
# two reviewers between them got a hand-painted SVG in front of a reader a dozen ways past scans
# that looked at tags — an unquoted attribute, an uppercase tag, a nested figure, a `data-src`
# decoy, a Markdown image, `srcset`, `<picture>`, `<object>`, a CSS background, a subdirectory. So
# every `assets/…` file a page reaches for has to be a figure the code drew or a study
# ART_DIRECTION.md names.
if command -v node >/dev/null 2>&1; then
  node tools/figures.mjs --check-rendered
else
  echo "figures.mjs: unverified — node is not installed"
fi

step "the generated appendix is in step with the record"
if ! git diff --quiet -- chapters/the-simulations.md; then
  echo "check: the build regenerated chapters/the-simulations.md — the record moved." >&2
  echo "       Review the diff and commit it; that is the appendix catching up, not a failure." >&2
  git --no-pager diff --stat -- chapters/the-simulations.md >&2
  exit 1
fi

printf '\n\033[1mtier 0 green.\033[0m\n'
