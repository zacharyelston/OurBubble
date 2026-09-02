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
reader, not a checker:

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
add it — one line, dated, with the edition that shipped it. This list is the skill's value;
it grows the same way lab/LESSONS.md does.

FIREWALL: editions describe a toy lattice; the proofread checks the prose honors that.
