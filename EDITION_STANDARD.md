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

## Numbers computed while the page is built

Chapters 1–5 live on one triangle, one tetrahedron, and the two shapes that tetrahedron is made of,
and every number in them is finger-countable — or, in the one case where it stops being, visibly
stops being, which is that chapter's point. Quoting such a number from the record would be theatre:
the reader can check it on a napkin, so the book does the arithmetic in front of her instead of
citing itself.

**Write a token; the build replaces it.** In chapter prose:

```
{{napkin:triangle_loop_example}}
```

The mdBook preprocessor substitutes generated Markdown for it on every build. An unknown token name
fails the build, and a token that somehow survives into a built page fails the checker — the reader
is never shown a brace-literal where a number belongs.

| token | what it computes |
|---|---|
| `tetra_counts` | the tetrahedron's census — dots, lines, faces, inside — and that `d∘d = 0` on both rungs |
| `triangle_loop_example` | corner values 2, 5, 1 on a triangle; the three oriented differences and their sum |
| `tetra_face_loops` | corner values 2, 5, 1, 4; the six differences; each of the four faces' loop sums |
| `tetra_inside_sum` | six freely chosen line-numbers, the four non-zero face-numbers they give, and their oriented sum around the inside |
| `triangle_slosh_table` | ten ticks of the engine's rule on a triangle at the triangle's own tick, from the corners 2, 5, 2 — whole numbers throughout, and back to the pair it started from every four ticks |
| `tick_belongs_to_shape` | the same three numbers at the tetrahedron's tick: the total still conserved, three rows printable, no return — and the tick size the four-dot shape must stay under |
| `slosh_table` | ten ticks of the engine's rule on one tetrahedron, every line counting the same, with a conserved total |
| `slosh_table_dialed` | the same ten ticks with one line counted double — the dial, in miniature |
| `no_room` | the hops from each dot of the tetrahedron to each other dot: one line, every time, so its diameter is 1 |
| `vertex_classes` | the tiling built on a wrapped world, and how many kinds of place its cut rule leaves — with the control that cuts every hole alike |
| `octa_cut` | one tetrahedron cut at the middles of its six lines: four tips at an eighth each, and one eight-faced shape that is exactly half |
| `octa_counts` | that shape's census against the tetrahedron's, its dots' names, and the three pairs of dots no line joins |
| `octa_poke_table` | the same rule and tick on it: the whole poke crosses to the opposite dot in two ticks and is home in three |
| `octa_face_sum` | twelve freely chosen arrows on it, the eight face-numbers they give, and their sum walked from outside |
| `stella_counts` | the two tetrahedra threaded through one another, counted — and that the second's own middles are the same middles |
| `stella_refusal` | the tick size each of the three objects must stay under, and the run that runs away when one is exceeded |

Three properties are guaranteed, and each is enforced rather than intended:

1. **Exact and short.** Rational arithmetic throughout, no floating point; a value that will not
   write down exactly in a couple of decimal places fails the build rather than being rounded into
   the table.
2. **Deterministic.** Every token is recomputed twice on every check and must come out identical.
   "Computed while this page was built" is a promise about *every* build.
3. **Self-asserting.** Each token proves its own claim before it renders — the loop sums are zero,
   the inside sum is zero, the total is conserved, the average does not move. A napkin that quietly
   printed a non-zero loop sum would be worse than no napkin.

Every rendered block ends with one line: *computed while this page was built — <what>.*

**Three rules the captions and the prose around them answer to**, each of them a defect that shipped
once and was caught by a reader rather than a check (2026-09-02):

1. **A caption is a caption.** `tools/napkin.py` refuses one over 70 words as it renders, and the
   checker refuses a chapter whose captions come to more than 300 words between them, printing both
   numbers on every run. The grain band reads a chapter's *source*, where a token is one word, so
   without this the captions were the only reader-facing prose in the book that nothing measured —
   and one of them reached 118 words and took over the following section's argument.
2. **A claim is checked where it is made.** A token asserts that its rendered block contains the
   values it computed, and separately that its *caption* contains the ones the caption claims. A
   number present in the table does not license a caption that contradicts it.
3. **A chapter may not say what its own tokens disprove.** `napkin.REFUSED_IN_PROSE` lets a token
   name the phrasings its arithmetic refuses; the checker looks for them in the chapter's prose, not
   in the token. It also refuses, in every chapter, the readings the record's own computation
   refuted — those belong to the appendix. This is the only check in the repository that reads what
   the *author* wrote rather than what the tool wrote, and it exists because a corrected table sat
   two paragraphs above prose still making the disproved claim.

### The exemption, and exactly how far it reaches

A napkin's numbers are **not** in the appendix, and must not be: they are computed, not quoted. So
inside a napkin block, the rule that an emphasised number must be anchored in the chapter's appendix
section does not apply.

**The exemption is bounded by the block and nothing else.** The preprocessor fences each rendered
token with `<!-- napkin:NAME -->` … `<!-- /napkin:NAME -->`, and the checker excises exactly those
spans before applying the anchoring rule to the built page. An emphasised number one paragraph
outside a block is governed exactly as before — a computed `0` inside a napkin licenses nothing
outside it. (Verified by mutation: the same bold value passes inside a span and fails outside it.)

### Lane boundary

The Rewrite lane writes tokens in `chapters/` and never edits the backend. The Repository lane owns
`preprocessor.py`, `tools/napkin.py` and `check_edition.py` and never edits a chapter's prose. A new
token is a Repository-lane change; using one is a Rewrite-lane change.

The Repository lane was retired complete on 2026-09-01, so the six `octa_*`/`stella_*` tokens were
added by the Rewrite lane on the coordinator's instruction (2026-09-02, issue #34) rather than
across the boundary. The boundary itself stands: the arithmetic went into `tools/`, the prose into
`chapters/`, and neither commit touched the other's business.

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
