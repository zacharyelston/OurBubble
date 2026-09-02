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
#   3. build the book — which regenerates the appendix from the record
#   4. check the built pages, including that every record link resolves
#
# The build can legitimately rewrite `chapters/the-simulations.md`, so the last thing this does is
# ask git whether it did: a dirty tree after a build means the record moved and the committed
# appendix had not caught up.
#
# Usage:  tools/check.sh          (or: make check)

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1m== %s\033[0m\n' "$1"; }

step "1/4 · fetch the pinned engine (for the integrity layer)"
# Soft on purpose. The engine is private; most readers cannot reach it, and the quotation gate does
# not need it. What is NOT soft is pretending the integrity layer ran — `check_edition.py` prints
# its own status line either way, and says "unverified" when it could not.
if tools/fetch_record.sh; then
  :
else
  echo "check: the engine is not reachable — snapshot integrity will report as unverified." >&2
  echo "       Quotations are still gated, against the committed record/ snapshot." >&2
fi

step "2/4 · check the edition (snapshot integrity + quotations)"
python3 check_edition.py

step "3/4 · build the book"
command -v mdbook >/dev/null 2>&1 || {
  echo "check: mdbook is not installed — see the README (cargo install mdbook, or a release tarball)" >&2
  exit 1
}
mdbook build

step "4/4 · check the rendered pages and every record link"
python3 check_edition.py --rendered

step "the generated appendix is in step with the record"
if ! git diff --quiet -- chapters/the-simulations.md; then
  echo "check: the build regenerated chapters/the-simulations.md — the record moved." >&2
  echo "       Review the diff and commit it; that is the appendix catching up, not a failure." >&2
  git --no-pager diff --stat -- chapters/the-simulations.md >&2
  exit 1
fi

printf '\n\033[1mtier 0 green.\033[0m\n'
