# proof-reader — consume an edition as its reader, render comments

Use when an edition (Our Bubble, The Container, a synthesis page, a chapter draft) needs a
reading pass. The proofreader is a READER, not a writer, and not a checker: the mechanical
truth of the text is the lint/checker layer's job (needles, anchors, the legacy-claims guard);
this skill's job is what only a reading catches — flow, pace, confusion, tone. **The
proofreader never edits the text.** Comments go out; the Rewrite lane (or the author) decides.

## 0 · Establish the reader before reading

Every edition declares (or implies) its reader — Our Bubble: a curious person with no physics;
the synthesis slow-ramp: same; the full synthesis page: a skeptic with a terminal; The
Container: a study-guide reader. Name the persona at the top of your report and hold it for
the whole pass. If the edition doesn't declare its reader, that is finding #1.

## 1 · Read end-to-end, in order, once — before any commenting

The first read is the honest one: note where YOU stumbled, re-read, or skimmed. A comment
invented on a second pass about a spot that read fine the first time is editing taste, not
proofreading. Mark stumble points with their location; classify afterward.

## 2 · The house failure modes (check each, in this order)

Learned across the 2026-08/09 content passes — each of these shipped once and was caught by a
reader, not a checker.

**Two kinds, and the second is not reading.** Modes 1–10 are what a *reading* catches: read as the
persona and they surface. Modes 11–12 are what only an *attack* catches — a page that is honest
today over a guard that would let it lie tomorrow. A pass that only reads finds none of the second
kind, so §2b is a separate sweep with its own method, not a harder read.

### 2a · What a reading catches

1. **Light-speed jumps.** A beat/section that introduces two or more new ideas, or a concept
   (waves, speed, geometry) that was never built. The fix is always more baby steps, never a
   longer paragraph. (The ramp went 6 → 8 → 11 beats this way.)
2. **Unexplained mode changes.** Every section boundary must answer the reader's "why are we
   changing subject?" in its first sentence — explanation → catalogue → methodology →
   limitation → reproduction each need a stated purpose. (The Codex five-point review.)
3. **Jargon before it is earned.** A term used before the plain-words idea it names. In-jargon
   asides are the house pattern; a term in running prose before its aside is a finding.
4. **Numbers without meaning.** A figure the reader can't do anything with ("7.2%/14.7%") or a
   control result that reads as an error ("89° scatter" — actually a win). Every number either
   carries its meaning in the sentence or belongs in the appendix.
5. **Dangling and skipping references.** "Section 6 below" that skips section 5; a pointer to
   a section by the wrong name; a promise the page never keeps.
6. **Voice breaks.** The register set by the opening must hold; CSV column names, internal
   vocabulary ("bench strip", "rung log"), and repo-speak in reader-facing prose are breaks.
7. **Firewall drift on a naive read.** Read each physics-adjacent sentence as someone who
   skipped the scope box: does it claim nature? Negation is not protection ("this is not a
   claim that X" still plants X — reword findings, don't add disclaimers). Bridges from real
   history to the toy claim the METHOD, never the discoveries.
8. **People without names.** A real discoverer referred to only by epithet ("the man with the
   two posts") is uncredited. The device is a hook, not a credit: the name lands within a
   sentence, verified (person, place, date) — a wrong attribution is worse than an epithet.
   (Caught by the owner, 2026-09-01, Our Bubble history arc: "we need to name these people.
   they deserve that.")
9. **Provenance grandstanding.** The integrity machinery described as a threat ("every number
   is checked or the build fails") instead of a capability ("a living document that computes
   its own numbers when it is built") — or described more than once per surface. The full
   mechanism is stated once, positively, in its natural home; everywhere else the text is
   simply, quietly correct. Never confuse this with the science's own exactness language
   (d²=0 as integers), which stays. (Caught by the owner, 2026-09-01, reading Our Bubble.)
10. **Illustration fit.** Does each figure illustrate its chapter's question (not decorate),
   does the alt text describe the relationship, is the "Analogy — not data." caption present
   and true?

### 2b · What only an attack catches

Both were found in one pass by mutating the guards rather than by re-reading the prose, and both are
findings **even when the page is currently correct** — the finding is the licence to be wrong, not
the wrongness.

11. **Numbers the reader can out-check.** Prose that states the *book's own* tolerance as the
   *reader's* capability: "the row after this one cannot be put on a napkin at all", where the
   engine's actual rule is two decimal places and she works out 3.125 with a pencil in the
   paragraph asking her to stop. Not mode 4 — the number is meaningful; it is the invitation to
   check that turns the overstatement into a falsehood. Tell her the rule she is being held to, or
   show the thing falling apart instead of asserting a wall. Method: wherever the text says she
   cannot, do it. (Caught 2026-09-02, Our Bubble tranche D, chapter 3.)
12. **Checked, not refused.** Attack the guards, not only the prose. Every check that asks whether
   the right number is *present* passes a page that also says the wrong thing beside it — a caption
   contradicting the verdict its own token asserted, a value correct but placed against the wrong
   noun, a refused phrase split across a newline the browser renders intact. Three mutations found
   all three; the reading found none. Method: edit a rendered literal; swap two values between
   their names; contradict a caption while keeping every word it pinned; break a refused phrase
   with whitespace; weaken an assertion; alter a vendored value and re-hash the lock. Report
   whether the guard fails **by name**, and revert everything. The fix is the writing contract's
   rule 4 — checking asks whether the computed number is present, refusing asks whether the wrong
   thing is absent, and only refusing survives a builder that gets rewritten along with its own
   check. (Caught 2026-09-02, Our Bubble tranche D.)

## 3 · Render the comments

- **Verdict line first** (house style): READS CLEAN for <persona> / N findings (X blockers).
- One table: location (chapter/section/beat, with a quotable anchor phrase) → what the reader
  experiences → severity → suggested direction (one line, not a rewrite).
- Severities: **blocker** (a reader is lost or misled) · **bump** (a stumble; re-read needed) ·
  **nit** (polish). A pass with zero findings states what was read and as whom — silence is
  not a verdict.
- **Delivery:** on the edition's open PR as a review with inline comments where the diff
  allows, else one structured comment; no PR → a tracker issue titled
  "proofread: <edition> <date>". Never push commits.

## 4 · Grow this skill

When a reader (the owner, a visitor, a future pass) catches a failure mode not in §2's list,
add it — one line, dated, with the edition that shipped it, under §2a if a reading catches it
and §2b if only an attack does. A §2b entry carries its **method**: the recipe that found it,
so the next pass can run it rather than reinvent it. This list is the skill's value; it grows
the same way lab/LESSONS.md does.

FIREWALL: editions describe a toy lattice; the proofread checks the prose honors that.
