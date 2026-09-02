# CONTINUUM — the agent-lane ledger

One row per active lane of agent work, so parallel lanes stay disjoint by construction and nobody
has to reconstruct "who is doing what" from scrollback. The coordinator (the decision session)
maintains this file; lanes report to it. Mirrored as a tracker issue so the state survives any one
session — **update both on every lane change** (start, handoff, retire).

This is the book's ledger. The engine's is in UniForge's own `CONTINUUM.md`, and the two are
disjoint by repository: a lane here never edits the record, and a lane there never edits the prose.

Rules of the ledger:
- **One lane → one territory (paths) → one delivery branch/PR.** Two lanes never edit the same
  path; a lane that needs another lane's file asks the coordinator, not the file.
- A lane idle past the branch TTL (7 days) is a stale lane: hand off or retire — no third state.
- Lanes run **tier 0 before every push** — `make check` — and land daily. Content drafts are merged
  under the owner's judgment; everything else merges under the standing review bar.
- **Standing order (owner, 2026-09-01): every owner-judged edition draft gets a proof-reader
  pass before it reaches the owner.** The pass runs the [`.claude/skills/proof-reader`](.claude/skills/proof-reader)
  loop, is performed by a FRESH agent (the reader must not be the writer — no author context), and
  its comments render on the draft PR. The author addresses or disputes findings on the PR; only
  then does the coordinator present the draft. The owner's reading time goes to judgment, not
  stumble-hunting.
- **One voice across the forge, the object, and the book** (owner, 2026-09-01): plain words first, honest about limits, and aspiring to inspire — a reader should leave wanting to build a test, not believing a claim.
- **The record is pinned, never followed.** A lane that needs newer evidence bumps `record.lock`
  deliberately — fetch, re-snapshot, checker, one commit (see the README). No lane tracks the
  engine's `main`.
- **`record/` is derived, never edited.** It is a verbatim copy of the engine at the pinned commit,
  and the integrity layer diffs it byte for byte whenever the engine is reachable. Editing a file
  there to make a quotation fit is the one failure this repository is built to catch.

## Active lanes

| lane | role | territory | delivery | state |
|---|---|---|---|---|
| **Structure** | owner + the decision session (Fable): section architecture, ordering, merges, scope calls | decisions; merges; this file | this ledger + merge verdicts | active |
| **Rewrite** | content agent: prose voice, pacing, baby-step pedagogy across the edition | `chapters/`, `edition.json`, `theme/`, `ART_DIRECTION.md`, `EDITION_STANDARD.md` | one PR per pass | idle — last delivery: the whole-book pass + provenance tone pass (UniForge #347, merged 2026-09-01, before the move); awaiting next charter |
| **Repository** | bootstrap and infrastructure: the move out of UniForge, the record contract, the committed record snapshot (reader click-through), tier 0, CI, Pages | `record.lock`, `record/`, `tools/`, `Makefile`, `.github/`, `check_edition.py`, `gen_appendix.py`, `README.md`, `FIREWALL.md`, `PROVENANCE.md` | the bootstrap commit + the snapshot PR | complete 2026-09-01 |

## Dormant / registered lanes (no agent assigned)

| lane | charter | tracked |
|---|---|---|
| Illustration | replace the placeholder SVG studies with stronger art, under `ART_DIRECTION.md`'s contract (concept, alt text, "Analogy — not data." caption, firewall) | — |
| Record bumps | advance `record.lock` as the engine's evidence advances — fetch, re-snapshot, checker, one commit | — |

FIREWALL: this file coordinates work on a book about a toy DEC lattice; nothing here is a claim
about nature.
