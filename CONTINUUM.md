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
- **A reading that is under review is not a chapter's to make in either direction** (owner,
  2026-09-02). Where the owner has sent a question back to the engine, the *edition* says nothing
  about it — not as a claim, not as history, and not as a verdict, however the narrow computation
  came out. The lane notes and the code keep their negatives, because negatives are first-class
  (R5); what they gain is scope. A computed negative is quoted with the reading it tested, never as
  a verdict on the wider claim, and the wider claim's review is named where the negative is written
  down. The readings currently under review are the octahedron-and-time group (issue #51; the note's
  own provenance banner and UniForge `lab/napkin/0002` carry the scope).
- **A beat is named `slug.n`, and a chapter holds at most twelve** (2026-09-04, issue #77). A beat's
  id is its chapter's slug and its place inside that chapter — `make-it-move.3` — so inserting a
  beat renumbers only that chapter and moving a chapter renumbers nothing. `OUTLINE.md` numbers each
  chapter's beats from 1 under its heading; the reading order lives in `chapters/SUMMARY.md`. A
  book-wide beat number is nobody's name any more and is refused in this file, in `OUTLINE.md`, in
  `demos/DEMOS.md` and in every chapter — the numbering went stale three times in two weeks, which
  is what ended it. Where a row below recorded a beat *range*, the range was replaced by the count
  of beats that chapter had **when the row was written** — the migration could not translate a
  numbering that no longer exists, and a count as of a date is checkable against the PR the row
  names. Those counts are not the chapter's today, for the same reason the chapter-number rule
  below gives.
- **A chapter number in this file is as of the row that wrote it.** The lanes below record what was
  merged when it merged, and chapter positions move: the front door (issue #56) put a chapter 0 at
  the head of the reading order, so every position named in a completed row is one lower than the
  book's today. The rows are not rewritten to hide that — a ledger that renumbers its own history
  cannot be checked against the PRs it names. Positions that must be current are named by chapter
  *title*, and the reading order itself lives in `chapters/SUMMARY.md`.
- **The record is pinned, never followed.** A lane that needs newer evidence bumps `record.lock`
  deliberately — fetch, re-snapshot, checker, one commit (see the README). No lane tracks the
  engine's `main`.
- **`record/` is derived, never edited.** It is a verbatim copy of the engine at the pinned commit,
  and the integrity layer diffs it byte for byte whenever the engine is reachable. Editing a file
  there to make a quotation fit is the one failure this repository is built to catch.

> **Handover (2026-09-03).** This work moved from a local decision session to cloud sessions. The epic with the state, the operating rules and the open work is https://github.com/zacharyelston/OurBubble/issues/67 — read it before this file.

## Active lanes

| lane | role | territory | delivery | state |
|---|---|---|---|---|
| **Structure** | owner + the decision session (Fable): section architecture, ordering, merges, scope calls | decisions; merges; this file | this ledger + merge verdicts | active |
| **Rewrite** | content agent: prose voice, pacing, baby-step pedagogy across the edition | `chapters/`, `edition.json`, `theme/`, `ART_DIRECTION.md`, `EDITION_STANDARD.md` | one PR per pass | active — tranche A (chapters 0–4, the minimal universe) MERGED 2026-09-02 as PR #8 after seven proof-reader rounds, owner: "very good"; tranche B (the record chapters, *Room, and a world with no edge* through the history chapter) on PR #23, first read HOLD (3 blockers), fixes in progress; **tranche C — the octahedron** (issue #34, PR #35): a new chapter 4, *The shape between*, of eleven beats as it landed, with the outline and every later beat renumbered by `tools/renumber_beats.py` — **MERGED 2026-09-02 as PR #35** (`e8ecfc5`) on the owner's word after three proof-reader rounds; first reader notes through the form (#41, #42) applied as PR #43; **tranche D — time is two rows** (issue #51, decisions in #48): chapter 3 slowed to twelve beats with the triangle running before the tetrahedron and the tick made a beat of its own, chapter 4 closed at the eight-face zero, and a new chapter 5, *Two worlds threaded*, taking six beats as it landed — every later beat +3 and every later chapter +1, in one `tools/renumber_beats.py` pass; **the preface — the front door** (issue #56): a new chapter 0, *What you will have*, four beats and no figure, naming discrete exterior calculus once and then setting it aside — every beat in the book +4 and every chapter +1, in one `tools/renumber_beats.py` pass |
| **Repository** | bootstrap and infrastructure: the move out of UniForge, the record contract, the engine contract, the committed record snapshot (reader click-through), tier 0, CI, Pages | `record.lock`, `record/`, `engine.lock`, `engine/`, `TOKENS.md`, `tools/`, `Makefile`, `.github/`, `check_edition.py`, `gen_appendix.py`, `README.md`, `FIREWALL.md`, `PROVENANCE.md` | the bootstrap commit + the snapshot PR | complete 2026-09-01; reopened 2026-09-02 for canonical labeling (#30, `CANON.md`, `tools/canon.py`), bytecode-free tier 0 (#32), the octahedron computation (#33), reader notes (#38), and **the napkin engine vendored and pinned** (#49, step three-A: `engine.lock`, `engine/`, `tools/build_engine.sh`, the tokens rendering from the engine and the Python kept as the guard) |
| **Demos** | the napkin world in the browser, one page per chapter following the beats; exact rationals, no float; every shown number cross-checked under node in tier 0 against the vendored engine's payload; stills to replace the SVG studies (owner-judged, later) | `demos/`, `tools/napkin_export.py`, the demo lines in `check_edition.py` and `tools/check.sh`, `chapters/demos` symlink | one PR per pass | active — prototype chapters 1–4 MERGED 2026-09-02 as PR #40 (issue #36); owner's first note: the stella is a hairball in 2-D → 3-D wireframe for the threaded pair (issue filed 2026-09-02). **The pages' beats are behind the outline** since tranche D moved every beat from the old 36 on by three and added a chapter, and the front door then moved every beat in the book by four and every chapter by one; step three-B renumbers them and adds the fifth page — `demos/DEMOS.md` states it rather than implying the pages are in step |
| **Reader notes** | a "Leave a note on this section" link under every section heading, prefilled GitHub issue form, label `reader-note`; the owner and non-git-native readers file notes; Structure routes them as notes rounds | `tools/reader_note.py`, the reader-note pass in `preprocessor.py`, `.github/ISSUE_TEMPLATE/reader-note.yml` | notes → small PRs | live 2026-09-02 (PR #38); needs a free GitHub account — stated to the reader |

## Dormant / registered lanes (no agent assigned)

| lane | charter | tracked |
|---|---|---|
| Illustration | replace the placeholder SVG studies with stronger art, under `ART_DIRECTION.md`'s contract (concept, alt text, "Analogy — not data." caption, firewall) | — |
| Record bumps | advance `record.lock` as the engine's evidence advances — fetch, re-snapshot, checker, one commit | — |

FIREWALL: this file coordinates work on a book about a toy DEC lattice; nothing here is a claim
about nature.
