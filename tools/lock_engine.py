#!/usr/bin/env python3
"""Rewrite `engine.lock`'s pin and its hash block from what `tools/build_engine.sh` just produced.

Split out of the shell script for one reason: the hash block is the lock's evidence, and evidence
written by a `for` loop with a `>>` in it is evidence nobody can read back. Here it is derived from
the directory, sorted, and written in one pass, and the same module is what `check_edition.py` reads
the lock with — so the file cannot be written in a form the checker parses differently.

Everything above the hash block is left exactly as it is, including the header. The header is the
contract a person reads; only the values change.

FIREWALL: this file moves hashes about. Nothing here is a claim about nature.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple

# The line the hash block begins under. Everything from here to the end of the file is rewritten.
MARKER = "# The vendored files, and what they hashed to when they were built."


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def vendored(directory: Path) -> List[Tuple[str, str]]:
    """Every built file under `engine/`, as `(relative path, sha256)`, sorted.

    Every one of them, not a list of interesting ones — a lock that names only some of the files it
    covers can be satisfied by deleting the rest. Two exclusions, both narrow:

    * **dot-files**, which are build leavings (`wasm-bindgen --target web` writes a `.gitignore`,
      and `build_engine.sh` removes the one it knows about); anything else beginning with a dot has
      no business being vendored, and the checker catches it as unlocked.
    * **`.md`**, which is `PROVENANCE.md` and nothing else. It is the one hand-written file in the
      directory, and hashing prose would mean a typo fix could only be made on a machine with the
      private engine on it. `check_edition.py` holds it to the thing that matters instead: it must
      name the commit `engine.lock` pins.
    """
    files = [
        item for item in sorted(directory.rglob("*"))
        if item.is_file() and not item.name.startswith(".") and item.suffix != ".md"
    ]
    return [(str(item.relative_to(directory.parent)), digest(item)) for item in files]


def parse(text: str) -> Dict[str, List[str]]:
    """`key = value` lines, `#` comments, repeated keys accumulating — `record.lock`'s own format."""
    out: Dict[str, List[str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        out.setdefault(key.strip(), []).append(value.strip())
    return out


def hashes(lock: Dict[str, List[str]]) -> Dict[str, str]:
    """The lock's `sha256 = <hex>  <path>` lines, as `{path: hex}`."""
    out: Dict[str, str] = {}
    for entry in lock.get("sha256", []):
        parts = entry.split()
        if len(parts) != 2:
            raise ValueError(f"engine.lock: malformed sha256 line {entry!r} — expected '<hex>  <path>'")
        out[parts[1]] = parts[0]
    return out


def rewrite(lock_path: Path, directory: Path, values: Dict[str, str]) -> str:
    text = lock_path.read_text(encoding="utf-8")
    if MARKER not in text:
        raise SystemExit(f"{lock_path}: the hash block marker is missing — refusing to guess where "
                         f"it goes. The marker line is:\n{MARKER}")
    head = text.split(MARKER, 1)[0]

    lines = []
    for line in head.splitlines():
        stripped = line.strip()
        if "=" in stripped and not stripped.startswith("#"):
            key = stripped.split("=", 1)[0].strip()
            if key in values:
                pad = " " * max(1, 14 - len(key))
                lines.append(f"{key}{pad}= {values[key]}")
                continue
        lines.append(line)

    body = [MARKER, "#",
            "# Every file, not a list of interesting ones: a lock naming only some of them is",
            "# satisfied by deleting the rest. `check_edition.py` compares this block against the",
            "# directory in both directions on every run.",
            ""]
    for rel, hexed in vendored(directory):
        body.append(f"sha256 = {hexed}  {rel}")

    return "\n".join(lines).rstrip("\n") + "\n\n" + "\n".join(body) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", required=True)
    parser.add_argument("--dir", required=True)
    parser.add_argument("--sha", required=True)
    parser.add_argument("--rustc", required=True)
    parser.add_argument("--wasm-bindgen", required=True)
    parser.add_argument("--crate-version", required=True)
    args = parser.parse_args()

    lock_path = Path(args.lock)
    directory = Path(args.dir)
    text = rewrite(lock_path, directory, {
        "sha": args.sha,
        "rustc": args.rustc,
        "wasm_bindgen": args.wasm_bindgen,
        "crate_version": args.crate_version,
    })
    changed = text != lock_path.read_text(encoding="utf-8")
    lock_path.write_text(text, encoding="utf-8")
    count = len(vendored(directory))
    print(f"engine.lock: {'rewritten' if changed else 'unchanged'} — {count} file(s) hashed at "
          f"{args.sha[:7]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
