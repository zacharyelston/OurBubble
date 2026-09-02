#!/usr/bin/env python3
"""Generate the record snapshot's HTML view layer.

Called by `tools/snapshot_record.sh`; not meant to be run on its own.

Two kinds of page, and both exist for the same narrow reason — **so the appendix's links land on
something when the book is published**:

* `record/<path>.html` beside every `record/<path>.md`. mdBook rewrites every relative `*.md` link
  to `*.html` (all 53 of the appendix's, including the ones that leave the book) and does not copy
  `.md` files out of `src` at all. So the rewrite is not fought, it is *aimed*: the page is put
  exactly where it points.
* `index.html` in every directory the record cites. A lab entry is cited as a folder, and a folder
  with no index is a 404 on a static host.

The views show the file's bytes in a `<pre>`, not rendered Markdown. That is deliberate on two
counts: no Markdown renderer to install in the build, and what the reader sees is exactly what the
checker verified. The verbatim file stays on disk next to its view for the repository browser and
for the byte-for-byte integrity check.

Nothing here is part of the record. The views are derived, regenerated on every snapshot, and the
integrity check ignores them.
"""

from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "record"
LOCK = ROOT / "record.lock"

# Text we are willing to show inline. Anything else (a `.html` figure, an image) is already
# something a browser can open, or is not ours to reinterpret.
TEXT_SUFFIXES = {".md", ".txt", ".toml", ".json", ".csv", ".rs", ".py", ".sh", ".yml", ".yaml"}

STYLE = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body { margin: 0; padding: 2rem 1.25rem 4rem;
       font: 15px/1.6 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       background: #fbfaf8; color: #1c1b19; }
main { max-width: 62rem; margin: 0 auto; }
a { color: #7a4b1e; }
h1 { font-size: 1.15rem; margin: 0 0 .35rem; font-weight: 650; word-break: break-all; }
.kicker { font-size: .78rem; letter-spacing: .08em; text-transform: uppercase;
          color: #8a8377; margin: 0 0 1.25rem; }
.scope { border-left: 3px solid #c9a227; background: #fdf8e8; padding: .8rem 1rem;
         margin: 0 0 1.5rem; font-size: .9rem; }
.scope strong { font-weight: 650; }
pre { background: #fff; border: 1px solid #e4e0d8; border-radius: 3px; padding: 1rem;
      overflow-x: auto; font: 12.5px/1.55 ui-monospace, SFMono-Regular, Menlo, monospace;
      white-space: pre; }
ul { padding-left: 1.15rem; }
li { margin: .2rem 0; font: 13px/1.5 ui-monospace, SFMono-Regular, Menlo, monospace; }
footer { margin-top: 2rem; font-size: .82rem; color: #8a8377; }
@media (prefers-color-scheme: dark) {
  body { background: #171614; color: #e8e4dc; }
  a { color: #d9a866; }
  .scope { background: #241f12; border-left-color: #c9a227; }
  pre { background: #1f1e1b; border-color: #35322c; }
}
"""


def scope_block(up: str) -> str:
    # Links "the book" rather than the book's FIREWALL.md: that file lives at the repository root,
    # outside the mdBook, so it has no address on the published site — and `record/FIREWALL.md` is
    # the *engine's* firewall, a different document. The book's own scope box is on its first page.
    return (
        '<div class="scope"><strong>Scope.</strong> This file is part of the record of a '
        "<strong>toy</strong>: a small world built inside a computer. Nothing in it is a claim about "
        "nature. Words such as <em>vacuum</em>, <em>photon</em> and <em>light cone</em> name patterns "
        f'in the model — see <a href="{up}../index.html">Our Bubble</a>.</div>'
    )


def page(title: str, kicker: str, body: str, up: str, sha: str) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)} · Our Bubble record</title>"
        f"<style>{STYLE}</style></head><body><main>"
        f"<h1>{html.escape(title)}</h1>"
        f'<p class="kicker">{kicker}</p>'
        f"{scope_block(up)}"
        f"{body}"
        f'<footer>A verbatim copy from the UniForge engine at commit <code>{html.escape(sha)}</code>, '
        f'carried with the book so it can be read without engine access. '
        f'<a href="{up}README.html">What this directory is</a>.</footer>'
        "</main></body></html>\n"
    )


def up_to_root(path: Path) -> str:
    """`../` × the depth of `path` below the snapshot root."""
    depth = len(path.relative_to(SNAPSHOT).parts) - 1
    return "../" * depth


def cited_paths() -> list[str]:
    out = []
    for line in LOCK.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if "=" not in line:
            continue
        key, value = (part.strip() for part in line.split("=", 1))
        if key == "path":
            out.append(value)
    return out


def main() -> int:
    if not SNAPSHOT.is_dir():
        print("make_record_views: record/ is absent", file=sys.stderr)
        return 1
    sha_file = SNAPSHOT / ".snapshot-sha"
    sha = sha_file.read_text(encoding="utf-8").strip() if sha_file.exists() else "unknown"

    # Everything on disk right now is verbatim record — the snapshot script has just copied it and
    # nothing has been generated yet. Capturing that set first is what guarantees a view can never
    # overwrite a real record file (a figure's `.html` sitting beside a `.md` of the same stem).
    verbatim = {path for path in SNAPSHOT.rglob("*") if path.is_file()}

    views = 0

    # 1 · a view beside every text file, at the path mdBook's rewrite points to.
    for path in sorted(verbatim):
        if path.suffix not in TEXT_SUFFIXES:
            continue
        target = path.with_suffix(".html")
        if target in verbatim:
            continue
        rel = path.relative_to(SNAPSHOT).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        body = f"<pre>{html.escape(text)}</pre>"
        target.write_text(
            page(rel, "verbatim from the record — shown as the file's own bytes",
                 body, up_to_root(path), sha),
            encoding="utf-8",
        )
        views += 1

    # 2 · an index in every directory the record cites, so a folder link is not a 404.
    indexes = 0
    for cited in cited_paths():
        directory = SNAPSHOT / cited
        if not directory.is_dir():
            continue
        entries = []
        # Only the record's own files are listed — the generated views and indexes are scaffolding,
        # not evidence, and a reader should not have to tell them apart. Each entry is named by the
        # real file and points at whichever of the two a browser can actually display.
        for child in sorted(p for p in verbatim if directory in p.parents):
            if child.name.startswith("."):
                continue
            rel = child.relative_to(directory).as_posix()
            view = child.with_suffix(".html")
            href = view if (child.suffix in TEXT_SUFFIXES and view.exists()) else child
            entries.append(
                f'<li><a href="{html.escape(href.relative_to(directory).as_posix())}">'
                f"{html.escape(rel)}</a></li>"
            )
        body = "<ul>" + "".join(entries) + "</ul>" if entries else "<p>No files.</p>"
        (directory / "index.html").write_text(
            page(cited, "a lab entry from the record — its own files, verbatim",
                 body, up_to_root(directory / "index.html"), sha),
            encoding="utf-8",
        )
        indexes += 1

    # 3 · say exactly what was generated.
    #
    # The integrity check has to tell record from scaffolding, and it used to do it by guessing from
    # file names — skip `index.html`, skip an `.html` with a text sibling, skip dotfiles. An audit
    # caught that guess excluding thirteen real engine files (`data/.gitkeep`) from the comparison:
    # not a wrong answer, but thirteen files nobody was checking. A list beats a heuristic.
    manifest = sorted(
        path.relative_to(SNAPSHOT).as_posix()
        for path in SNAPSHOT.rglob("*")
        if path.is_file() and path not in verbatim
    )
    (SNAPSHOT / ".generated").write_text("\n".join(manifest) + "\n", encoding="utf-8")

    print(f"make_record_views: {views} file views, {indexes} directory indexes, "
          f"{len(manifest)} generated files listed in record/.generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
