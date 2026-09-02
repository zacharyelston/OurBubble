#!/usr/bin/env bash
#
# Check the record out at the commit `record.lock` pins.
#
# The book's evidence lives in the UniForge engine repository and stays there. This script brings a
# read-only copy of exactly one commit of it into the ignored `.record/` directory, so the edition
# checker can verify every quotation against a commit that is written down rather than against
# whatever happened to be on someone's disk.
#
# Cheap on purpose: a bare-ish shallow fetch of the single pinned commit, not a clone of the
# history. Re-running when `.record/` is already at the pinned commit does nothing.
#
# Usage:  tools/fetch_record.sh [--force]
#
# Authentication: UniForge is a private repository. This uses your existing git credentials over
# SSH by default. In CI (or anywhere without an SSH key) set RECORD_TOKEN to a token with read
# access and the script switches to HTTPS. The token is never written to disk or to the remote
# config — it is passed for the length of one fetch.

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LOCK="$ROOT/record.lock"
DEST="$ROOT/.record"

[ -f "$LOCK" ] || { echo "fetch_record: no record.lock at $LOCK" >&2; exit 1; }

# record.lock is `key = value` lines with `#` comments; take the first value of each key we need.
lock_value() {
  sed -e 's/#.*//' "$LOCK" \
    | awk -v k="$1" '
        index($0, "=") == 0 { next }
        {
          key = substr($0, 1, index($0, "=") - 1)
          val = substr($0, index($0, "=") + 1)
          gsub(/^[ \t]+|[ \t\r]+$/, "", key)
          gsub(/^[ \t]+|[ \t\r]+$/, "", val)
          if (key == k) { print val; exit }
        }'
}

REPO="$(lock_value repo)"
SHA="$(lock_value sha)"
[ -n "$REPO" ] && [ -n "$SHA" ] || { echo "fetch_record: record.lock must set both 'repo' and 'sha'" >&2; exit 1; }

case "$REPO" in
  github.com/*) SLUG="${REPO#github.com/}" ;;
  *) echo "fetch_record: only github.com records are supported, got '$REPO'" >&2; exit 1 ;;
esac

FORCE="${1:-}"
STAMP="$DEST/.fetched-sha"
if [ "$FORCE" != "--force" ] && [ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$SHA" ]; then
  echo "record: $REPO@${SHA:0:12} already fetched"
  exit 0
fi

if [ -n "${RECORD_TOKEN:-}" ]; then
  URL="https://x-access-token:${RECORD_TOKEN}@github.com/${SLUG}.git"
  SHOWN="https://github.com/${SLUG}.git"
else
  URL="git@github.com:${SLUG}.git"
  SHOWN="$URL"
fi

echo "record: fetching $SLUG@${SHA:0:12} into .record/ (from $SHOWN)"

rm -rf "$DEST"
mkdir -p "$DEST"
git -C "$DEST" init -q
# The remote is added with the sanitised URL so a token never lands in .record/.git/config; the
# real URL is only ever an argument to the one fetch below.
git -C "$DEST" remote add origin "$SHOWN"
if ! git -C "$DEST" fetch -q --depth 1 "$URL" "$SHA"; then
  echo "" >&2
  echo "fetch_record: could not fetch $SLUG at $SHA." >&2
  echo "  - the record repository is private: you need SSH access, or RECORD_TOKEN set" >&2
  echo "  - a shallow fetch by SHA needs the commit to still be reachable on the remote" >&2
  rm -rf "$DEST"
  exit 1
fi
git -C "$DEST" checkout -q FETCH_HEAD

# The stamp is what `check_edition.py` reads: it survives the checkout being copied, cached or
# restored without its .git directory, which a CI cache will do sooner or later.
printf '%s\n' "$SHA" > "$STAMP"

echo "record: $SLUG@${SHA:0:12} ready in .record/"
