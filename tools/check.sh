#!/usr/bin/env bash
#
# Tier 0 for this repository — the pass to run before every push.
#
# Four steps, in the only order that makes sense: get the record the book quotes, check the source
# against it, build the book (which regenerates the appendix from the record), then check the built
# pages. The build can legitimately rewrite `chapters/the-simulations.md`, so the last thing this
# does is ask git whether it did — a dirty tree after a build means the record moved and the
# committed appendix had not caught up.
#
# Usage:  tools/check.sh          (or: make check)

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

step() { printf '\n\033[1m== %s\033[0m\n' "$1"; }

step "1/4 · fetch the pinned record"
tools/fetch_record.sh

step "2/4 · check the edition against the record"
python3 check_edition.py

step "3/4 · build the book"
command -v mdbook >/dev/null 2>&1 || {
  echo "check: mdbook is not installed — see the README (cargo install mdbook, or a release tarball)" >&2
  exit 1
}
mdbook build

step "4/4 · check the rendered pages"
python3 check_edition.py --rendered

step "the generated appendix is in step with the record"
if ! git diff --quiet -- chapters/the-simulations.md; then
  echo "check: the build regenerated chapters/the-simulations.md — the record moved." >&2
  echo "       Review the diff and commit it; that is the appendix catching up, not a failure." >&2
  git --no-pager diff --stat -- chapters/the-simulations.md >&2
  exit 1
fi

printf '\n\033[1mtier 0 green.\033[0m\n'
