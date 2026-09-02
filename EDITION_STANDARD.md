# Our Bubble edition standard

This is the contract for the reader edition. This repository's own [`FIREWALL.md`](FIREWALL.md) is
binding, and so are the engine's stricter rules where they apply — `AGENTS.md` and
`book/LESSON_STANDARD.md` in the record, readable at
[`.record/AGENTS.md`](.record/AGENTS.md) and
[`.record/book/LESSON_STANDARD.md`](.record/book/LESSON_STANDARD.md) once `tools/fetch_record.sh`
has run.

## One record, a different pace

Our Bubble may change sequence, framing, examples, and vocabulary. It may not change the result.
Every load-bearing number must be quoted from a current Container chapter and declared in
`edition.json`. Figures are linked from the existing `lab/**/figures/` output; analogy art and
hand-drawn result graphics are out of scope.

## What every chapter carries

1. A concrete opening a curious non-specialist can picture.
2. A visible `Scope` block that says the work is a toy lattice computation.
3. A `Source trail` block linking to the canonical Container chapter and record.
4. Plain words before jargon; jargon only when it helps the reader follow a source or figure.
5. A negative or limitation wherever the record supplies one.
6. A purposeful `Next` hand-off explaining why the following question is now natural.

The epilogue closes the sequence and therefore does not need a `Next` hand-off.

## Illustration contract

Every chapter begins with one editorial illustration study. It must:

1. make the chapter's next question visible without pretending to display a result;
2. carry meaningful alt text and a plain-language caption;
3. say explicitly that it is an analogy image, not simulation data;
4. remain visually distinct from links labeled `data-true`; and
5. be declared in `edition.json`, so the checker can verify both source and rendered output.

The current SVG studies are replaceable placeholders. A replacement may be more expressive, but it
must preserve the concept, alt-text intent, caption distinction, and firewall.

## The revised shadow method

The legacy manuscript used four beats: get data, give it shape, check, repeat. The current project
adds the protection that keeps “give it shape” from becoming a post-hoc pattern hunt:

1. **Notice a shadow.** Start with an observation or question.
2. **Propose a shape.** Name the smallest mechanism that might explain it.
3. **Say what would prove it wrong.** Register the prediction and its control before the record run.
4. **Check and repeat.** Keep the negative, reproduce the result, and let the next question arise
   from what the check actually returned.

## Meaning of “our bubble”

Two words, two jobs. **Bubble** has one deliberately modest meaning: the bounded region being
shaped, shielded, or measured inside the toy. **Our** names who builds it — the book is written
together with its reader.

*Bubble* used to carry a second meaning as well, the shared viewpoint of author and reader. That one
is retired per owner note 5 on PR #3 (2026-09-01/02 UTC), applied on the coordinator's call, because
a title word that means two things means neither of them reliably.

It never means that the stella octangula is the universe, that its combinatorics derive constants of
nature, or that a toy result establishes a physical technology.
