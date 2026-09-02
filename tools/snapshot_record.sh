#!/usr/bin/env bash
#
# Populate the committed record snapshot in `record/` from the fetched `.record/`.
#
# WHY THIS EXISTS. The engine repository is private and stays that way, so a reader on the public
# site — or anyone with a clean clone and no engine access — could see which file every number came
# from and never open it. The snapshot fixes that: the cited files travel *with* the book, verbatim.
#
# The snapshot is DERIVED, never hand-edited. It is copied out of `.record/`, which is itself a
# checkout of the one commit `record.lock` pins, so "what the snapshot says" and "what the engine
# said at that commit" cannot drift without `check_edition.py` reporting it byte for byte.
#
# Usage:  tools/snapshot_record.sh
#
# Refresh it only by bumping the record: edit `record.lock`, re-fetch, re-snapshot, re-run the
# checker, commit the lot together. See record.lock's header.

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOCK="record.lock"
FETCHED=".record"
DEST="record"

[ -f "$LOCK" ] || { echo "snapshot: no record.lock" >&2; exit 1; }

if [ ! -d "$FETCHED" ]; then
  echo "snapshot: .record/ is absent — run tools/fetch_record.sh first (it needs engine access)" >&2
  exit 1
fi

SHA="$(sed -e 's/#.*//' "$LOCK" | awk '
  index($0, "=") == 0 { next }
  { k = substr($0, 1, index($0, "=") - 1); v = substr($0, index($0, "=") + 1)
    gsub(/^[ \t]+|[ \t\r]+$/, "", k); gsub(/^[ \t]+|[ \t\r]+$/, "", v)
    if (k == "sha") { print v; exit } }')"
STAMP="$FETCHED/.fetched-sha"
[ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$SHA" ] || {
  echo "snapshot: .record/ is not at the pinned $SHA — re-run tools/fetch_record.sh" >&2
  exit 1
}

# Deliberately no `mapfile`/`readarray` anywhere in this file: stock macOS still ships bash 3.2, and
# a bootstrap script that only runs on a Homebrew bash is a trap for the next person.
paths_from_lock() {
  sed -e 's/#.*//' "$LOCK" | awk '
    index($0, "=") == 0 { next }
    { k = substr($0, 1, index($0, "=") - 1); v = substr($0, index($0, "=") + 1)
      gsub(/^[ \t]+|[ \t\r]+$/, "", k); gsub(/^[ \t]+|[ \t\r]+$/, "", v)
      if (k == "path") print v }'
}

count=$(paths_from_lock | wc -l | tr -d ' ')
[ "$count" -gt 0 ] || { echo "snapshot: record.lock declares no paths" >&2; exit 1; }

echo "snapshot: copying $count cited paths from .record/ (@ ${SHA:0:12}) into $DEST/"

rm -rf "$DEST"
mkdir -p "$DEST"

paths_from_lock | while IFS= read -r p; do
  [ -n "$p" ] || continue
  src="$FETCHED/$p"
  if [ ! -e "$src" ]; then
    echo "snapshot: cited path missing from the pinned engine checkout: $p" >&2
    exit 1
  fi
  mkdir -p "$DEST/$(dirname "$p")"
  # -R over a directory, plain copy over a file; either way the bytes are the engine's.
  cp -R "$src" "$DEST/$p"
done

printf '%s\n' "$SHA" > "$DEST/.snapshot-sha"

# The directory says what it is, in the book's voice, next to the evidence itself.
sed -e "s/@SHA@/$SHA/g" tools/record_readme.md > "$DEST/README.md"

# ── The view layer ────────────────────────────────────────────────────────────────────────────────
#
# Everything above is verbatim. Everything below is generated, and it exists for one reason: to make
# the links land on the published site.
#
# mdBook rewrites every relative `*.md` link to `*.html` — all 53 of the appendix's, including the
# ones that leave the book — and it does not copy `.md` files out of `src` at all. So a snapshot of
# Markdown alone would be linked as `.html` and served as nothing. Rather than fight the rewrite,
# this puts a page exactly where the rewrite points: `record/x.md` (verbatim, for the repository
# browser and for the checker) gets a sibling `record/x.html` that shows the same bytes.
#
# The view is a `<pre>` of the file, not rendered Markdown: no renderer to install, no rendering to
# be wrong about, and what the reader sees is what the checker checked.
python3 tools/make_record_views.py

# `chapters/record` is a symlink to `../record`, which is what carries the snapshot into the built
# book: mdBook copies non-Markdown files out of `src`, follows this link, and lands them at
# `book/record/**`. One prefix — `record/…` — therefore resolves in the repository browser, in the
# local render, and on the published site.
if [ ! -L "chapters/record" ]; then
  rm -rf "chapters/record"
  ln -s ../record "chapters/record"
  echo "snapshot: created the chapters/record symlink"
fi

files=$(find "$DEST" -type f | wc -l | tr -d ' ')
size=$(du -sh "$DEST" | cut -f1)
echo "snapshot: $DEST/ ready — $files files, $size, pinned at ${SHA:0:12}"
