#!/usr/bin/env bash
#
# Build the vendored engine — `engine/` — from a UniForge checkout at the commit `engine.lock` pins.
#
# This is the only thing that may write `engine/`, and it is the counterpart of
# `tools/snapshot_record.sh`: the record is *quoted* from a pinned commit, the engine is *run* from
# one, and both arrive in this repository as committed bytes with a lock file over them so a reader
# with no access to UniForge can build the book and run the demos.
#
#   Usage:  tools/build_engine.sh                    (UniForge at ../uniforge)
#           UNIFORGE_SRC=~/src/uniforge tools/build_engine.sh
#
# What it does, in the order of trust:
#
#   1. check the source is a UniForge checkout AT THE PINNED COMMIT — a build from any other commit
#      is refused rather than silently vendored under the wrong sha;
#   2. run the crate's emitter → `engine/napkin.json`, and **assert byte equality with
#      `tools/napkin_export.py`'s output**. That comparison is the whole reason this step is
#      allowed: the Python oracle is the arithmetic the book has been shipping, and one engine may
#      replace two only when it reproduces the other to the byte. Any difference stops the script
#      before anything is vendored.
#   3. run `tools/engine_emit` → `engine/rows.json`, the three register rows (R07, R10, R19) the
#      crate's own emitter does not carry, because its payload's shape is pinned to the oracle's and
#      nothing may be added to it — see that crate's `Cargo.toml` and `src/main.rs`;
#   4. build the WebAssembly artifact and run `wasm-bindgen --target web` over it;
#   5. rewrite the `sha256 =` block in `engine.lock` from what was actually produced.
#
# The toolchain is not installed here and not guessed: UniForge pins it in `core/rust-toolchain.toml`
# (1.97.1, with `wasm32-unknown-unknown` in the pin), so `cargo` run inside that checkout uses
# exactly it, and this script only records what it saw. `wasm-bindgen` is the one tool that is not
# pinned by the checkout — its version is checked against `engine.lock` and a mismatch is refused,
# because the glue and the module are built by it in matching pairs.

set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

LOCK="$ROOT/engine.lock"
OUT="$ROOT/engine"
SRC="${UNIFORGE_SRC:-$ROOT/../uniforge}"

lock_value() {  # the whole value of a single-valued key in engine.lock — versions carry spaces
  awk -v key="$1" '$1 == key && $2 == "=" { sub(/^[^=]*=[ \t]*/, ""); print; exit }' "$LOCK"
}

PINNED_SHA="$(lock_value sha)"
PINNED_TOOLCHAIN="$(lock_value rustc)"
PINNED_BINDGEN="$(lock_value wasm_bindgen)"
CRATE_VERSION="$(lock_value crate_version)"

step() { printf '\n\033[1m== %s\033[0m\n' "$1"; }

# ── 1 · the source, at the pinned commit ─────────────────────────────────────────────────────────

step "1/5 · the engine source"

if [ ! -d "$SRC/core/napkin" ]; then
  echo "build_engine: $SRC is not a UniForge checkout (no core/napkin/)." >&2
  echo "              Set UNIFORGE_SRC to one, or clone it beside this repository as ../uniforge." >&2
  exit 1
fi
SRC="$(cd -- "$SRC" && pwd)"

HEAD_SHA="$(git -C "$SRC" rev-parse HEAD)"
if [ "$HEAD_SHA" != "$PINNED_SHA" ]; then
  echo "build_engine: $SRC is at $HEAD_SHA, and engine.lock pins $PINNED_SHA." >&2
  echo "              Check that commit out, or bump the pin deliberately — see engine.lock's header." >&2
  exit 1
fi
if [ -n "$(git -C "$SRC" status --porcelain -- core/napkin core/geom)" ]; then
  echo "build_engine: the engine source has uncommitted changes under core/napkin or core/geom." >&2
  echo "              A vendored artifact must be reproducible from the pinned commit alone." >&2
  exit 1
fi

RUSTC="$(cd "$SRC/core" && rustc --version)"
BINDGEN="$(wasm-bindgen --version)"
[ "$RUSTC" = "$PINNED_TOOLCHAIN" ] || {
  echo "build_engine: rustc is '$RUSTC'; engine.lock pins '$PINNED_TOOLCHAIN'." >&2
  exit 1
}
[ "$BINDGEN" = "$PINNED_BINDGEN" ] || {
  echo "build_engine: $BINDGEN is installed; engine.lock pins '$PINNED_BINDGEN'." >&2
  echo "              cargo install -f wasm-bindgen-cli --version ${PINNED_BINDGEN##* }" >&2
  exit 1
}

echo "source $SRC at $HEAD_SHA · $RUSTC · $BINDGEN"

mkdir -p "$OUT"

# ── 2 · the canonical JSON, and the byte-for-byte bar ────────────────────────────────────────────

step "2/5 · the emitter, against the Python oracle"

( cd "$SRC/core" && cargo run --quiet --release -p napkin --bin napkin-export ) > "$OUT/napkin.json"

ORACLE="$OUT/.napkin-oracle.json"
python3 -B -c "import sys; sys.path.insert(0, 'tools'); import napkin_export; sys.stdout.write(napkin_export.text())" > "$ORACLE"

if ! cmp -s "$ORACLE" "$OUT/napkin.json"; then
  echo "build_engine: the engine's canonical JSON is NOT byte-identical to tools/napkin_export.py." >&2
  echo "              Nothing was vendored. The first differing bytes:" >&2
  cmp "$ORACLE" "$OUT/napkin.json" >&2 || true
  diff <(python3 -m json.tool "$ORACLE" 2>/dev/null) \
       <(python3 -m json.tool "$OUT/napkin.json" 2>/dev/null) | head -40 >&2 || true
  rm -f "$ORACLE" "$OUT/napkin.json"
  exit 1
fi
rm -f "$ORACLE"
echo "engine/napkin.json: $(wc -c < "$OUT/napkin.json" | tr -d ' ') bytes, byte-identical to tools/napkin_export.py"

# ── 3 · the rows the emitter does not carry ──────────────────────────────────────────────────────

step "3/5 · the remaining register rows (R07 · R10 · R19)"

ln -sfn "$SRC" "$ROOT/tools/engine_emit/uniforge"
( cd "$ROOT/tools/engine_emit" && cargo run --quiet --release ) > "$OUT/rows.json"
echo "engine/rows.json: $(wc -c < "$OUT/rows.json" | tr -d ' ') bytes"

# ── 4 · the browser artifact ─────────────────────────────────────────────────────────────────────

step "4/5 · the WebAssembly artifact"

( cd "$SRC/core" && cargo build --quiet --release -p napkin --lib --features wasm \
    --target wasm32-unknown-unknown )
wasm-bindgen --target web --out-dir "$OUT" \
  "$SRC/core/target/wasm32-unknown-unknown/release/napkin.wasm"
# `--target web` also writes a `.gitignore` into the out dir; this repository decides for itself what
# it ignores, and the whole point of `engine/` is that its contents are committed.
rm -f "$OUT/.gitignore"
ls -l "$OUT/napkin_bg.wasm" "$OUT/napkin.js" | awk '{print $NF ": " $5 " bytes"}'

# ── 5 · the lock ─────────────────────────────────────────────────────────────────────────────────

step "5/5 · engine.lock"

python3 -B tools/lock_engine.py \
  --lock "$LOCK" --dir "$OUT" \
  --sha "$HEAD_SHA" --rustc "$RUSTC" --wasm-bindgen "$BINDGEN" --crate-version "$CRATE_VERSION"

printf '\n\033[1mengine/ rebuilt from %s.\033[0m\n' "${HEAD_SHA:0:7}"
echo "Run 'make check' and commit engine/ and engine.lock together."
