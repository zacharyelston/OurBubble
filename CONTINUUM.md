# CONTINUUM — the agent-lane ledger

One row per active lane of agent work, so parallel lanes stay disjoint by construction and nobody
has to reconstruct "who is doing what" from scrollback. The coordinator (the decision session)
maintains this file; lanes report to it. Mirrored as a tracker issue so the state survives any one
session — **update both on every lane change** (start, handoff, retire).

This is the book's ledger. The engine's is in UniForge's own `CONTINUUM.md`, and the two are
disjoint by repository: a lane here never edits the record, and a lane there never edits the prose.

Rules of the ledger:
- **The contract lives on `main`, and drafts read it from there.** `OUTLINE.md` (and any other
  document a draft is written against) is edited only on `main`; a draft branch merges `origin/main`
  before every proof-read, and the reader reads the contract from `origin/main` after a fetch — never
  from a branch's stale copy (learned 2026-09-02: a read HELD on an outline the coordinator had
  already fixed).
- **The checkout stays on `main`; every lane works in its own worktree under `/private/tmp`** — including
  the coordinator. A shared working copy is a hazard: a concurrent branch switch strands or mixes
  uncommitted work (learned 2026-09-02).
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
- **There is one engine, and it is pinned too** (owner, 2026-09-02). The book's numbers come from
  UniForge's `napkin` crate, vendored under `engine/` and pinned by `engine.lock`; `tools/napkin.py`
  renders and computes nothing, and the Python that used to compute is kept as the recomputation
  that must reproduce the vendored bytes. A lane that needs a number the engine does not emit asks
  for a register row in UniForge — it does not add arithmetic here. `TOKENS.md` says what is already
  available.
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
| **Rewrite** | content agent: prose voice, pacing, baby-step pedagogy across the edition | `chapters/`, `edition.json`, `theme/`, `ART_DIRECTION.md`, `EDITION_STANDARD.md` | one PR per pass | active — tranche A (chapters 0–4, the minimal universe) MERGED 2026-09-02 as PR #8 after seven proof-reader rounds, owner: "very good"; tranche B (chapters 6–13 in the current numbering) on PR #23, first read HOLD (3 blockers), fixes in progress; **tranche C — the octahedron** (issue #34, PR #35): a new chapter 4, *The shape between*, beats 36–46, with the outline and every later beat renumbered by `tools/renumber_beats.py` — **MERGED 2026-09-02 as PR #35** (`e8ecfc5`) on the owner's word after three proof-reader rounds; first reader notes through the form (#41, #42) applied as PR #43 |
| **Repository** | bootstrap and infrastructure: the move out of UniForge, the record contract, the engine contract, the committed record snapshot (reader click-through), tier 0, CI, Pages | `record.lock`, `record/`, `engine.lock`, `engine/`, `TOKENS.md`, `tools/`, `Makefile`, `.github/`, `check_edition.py`, `gen_appendix.py`, `README.md`, `FIREWALL.md`, `PROVENANCE.md` | the bootstrap commit + the snapshot PR | complete 2026-09-01; reopened 2026-09-02 for canonical labeling (#30, `CANON.md`, `tools/canon.py`), bytecode-free tier 0 (#32), the octahedron computation (#33), reader notes (#38), and **the napkin engine vendored and pinned** (#49, step three-A: `engine.lock`, `engine/`, `tools/build_engine.sh`, the tokens rendering from the engine and the Python kept as the guard) |
| **Demos** | the napkin world in the browser, one page per chapter following the beats; exact rationals, no float; every shown number cross-checked under node in tier 0 against the vendored engine's payload; stills to replace the SVG studies (owner-judged, later) | `demos/`, `tools/napkin_export.py`, the demo lines in `check_edition.py` and `tools/check.sh`, `chapters/demos` symlink | one PR per pass | active — prototype chapters 1–4 MERGED 2026-09-02 as PR #40 (issue #36); owner's first note: beat 42's stella is a hairball in 2-D → 3-D wireframe for beats 42–45 (issue filed 2026-09-02) |
| **Reader notes** | a "Leave a note on this section" link under every section heading, prefilled GitHub issue form, label `reader-note`; the owner and non-git-native readers file notes; Structure routes them as notes rounds | `tools/reader_note.py`, the reader-note pass in `preprocessor.py`, `.github/ISSUE_TEMPLATE/reader-note.yml` | notes → small PRs | live 2026-09-02 (PR #38); needs a free GitHub account — stated to the reader |

## Dormant / registered lanes (no agent assigned)

| lane | charter | tracked |
|---|---|---|
| Illustration | replace the placeholder SVG studies with stronger art, under `ART_DIRECTION.md`'s contract (concept, alt text, "Analogy — not data." caption, firewall) | — |
| Record bumps | advance `record.lock` as the engine's evidence advances — fetch, re-snapshot, checker, one commit | — |

FIREWALL: this file coordinates work on a book about a toy DEC lattice; nothing here is a claim
about nature.
