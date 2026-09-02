#!/usr/bin/env bash
#
# Tier 0 for this repository — the pass to run before every push.
#
# The order matters, and it is the order of trust:
#
#   1. fetch the pinned engine, if it is reachable at all  (soft: no engine access is not a failure)
#   2. check the edition — two layers in one run:
#        · snapshot integrity, when step 1 succeeded: `record/` is the engine at the pinned commit,
#          byte for byte. This is what makes the committed copy evidence rather than a copy.
#        · quotations, always: every declared number verbatim in `record/`. Needs no engine access,
#          so a clean clone and the published site are gated exactly as strongly as a dev box.
#   3. the two guards the edition check does not reach — `tools/octahedron.py`'s own assertions
#      (the geometry the octahedron chapter's appendix note rests on) and `tools/beat_coverage.py`
#      (the prose against OUTLINE.md's beats). Both were previously run by hand only.
#   4. build the book — which regenerates the appendix from the record
#   5. check the built pages, including that every record link resolves
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

step "3/5 · the two guards the edition check does not reach"
# Why these are here (a proofreader, 2026-09-02): both were run by nothing automated, and both
# back claims the book makes. `octahedron.py` asserts the geometry the octahedron chapter's
# appendix note rests on — the 1:1 face pairing, one line in seven, 13/7×, "never comes home" —
# and eight of its audit functions could be gutted with tier 0 staying green, because
# `check_edition.py` only reaches the seven functions the napkin tokens call. `beat_coverage.py`
# is the only thing that checks the prose against OUTLINE.md's beats at all, and it is what
# caught a double-applied renumbering that `renumber_beats.py`'s own self-check waved through.
# Together they cost under a second.
python3 -B tools/octahedron.py > /dev/null
python3 -B tools/beat_coverage.py > /dev/null
echo "octahedron.py: every audit asserted · beat_coverage.py: every beat claimed, in order"

step "4/5 · build the book"
command -v mdbook >/dev/null 2>&1 || {
  echo "check: mdbook is not installed — see the README (cargo install mdbook, or a release tarball)" >&2
  exit 1
}
mdbook build

step "5/5 · check the rendered pages and every record link"
python3 -B check_edition.py --rendered

step "the generated appendix is in step with the record"
if ! git diff --quiet -- chapters/the-simulations.md; then
  echo "check: the build regenerated chapters/the-simulations.md — the record moved." >&2
  echo "       Review the diff and commit it; that is the appendix catching up, not a failure." >&2
  git --no-pager diff --stat -- chapters/the-simulations.md >&2
  exit 1
fi

printf '\n\033[1mtier 0 green.\033[0m\n'
