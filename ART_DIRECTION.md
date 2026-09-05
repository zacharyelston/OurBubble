# Our Bubble illustration direction

This repository draws **two kinds of picture**, and a reader can tell them apart from the caption
alone.

A **study** is an editorial analogy image: a gentle visual ramp into a chapter, not a plot, a
measurement, or a depiction of physical reality. Its caption opens `Analogy — not data.`

A **figure** is a picture of the object itself — a still of a drawing the engine's own numbers
produced, or the record's own render. Its caption opens with no warning, because there is nothing to
warn about, and it carries the way into the running thing with an explicit `Open the data-true…`
label. **A figure is never hand-drawn**, and a study is never the thing a claim rests on.

Which kind a chapter may use is not a taste question. Where the demo code can draw the object, the
picture is the drawing (R10 — the sim IS the graphic). A study is what a chapter gets when there is
nothing to draw yet.

## Shared language

- **Format:** 1200 × 600 responsive SVG, readable in light and dark mdBook themes.
- **Shape:** soft fields, rounded panels, generous empty space, one visual question per chapter.
- **Palette:** midnight `#101a2c`, ink `#20314a`, paper `#f4ead8`, teal `#55c7be`, coral `#f28c78`,
  and gold `#f4c95d`.
- **Line:** rounded caps and joins; solid lines for the object being noticed, dashed lines for a
  proposal, comparison, or expectation.
- **Status:** the studies still in use are stamped `ILLUSTRATION STUDY` in the artwork itself — a
  composition suitable for reading now and straightforward to replace later without touching the
  chapter that hosts it. The table below is the list; a row that says *replaced* is a chapter that
  now carries figures instead, and its study file is gone rather than orphaned.
- **Accessibility:** the HTML `alt` text explains the conceptual *relationship*, not the drawing's
  decoration; each SVG additionally carries a native `<title>` and `<desc>` for readers who open
  the asset directly.
- **Wiring:** one block per chapter, placed immediately after the Source trail so the image is the
  reader's first impression and the evidence trail is still above it:

  ```html
  <figure class="chapter-illustration">
    <img src="assets/NN-slug.svg" alt="the conceptual relationship, in words">
    <figcaption><strong>Analogy — not data.</strong> one sentence on what the picture asks,
    and a pointer to the data-true figure that answers it.</figcaption>
  </figure>
  ```

  The `Analogy — not data.` opener is **required** and is styled by
  [`theme/our-bubble.css`](theme/our-bubble.css) (`.chapter-illustration`), which `book.toml`
  loads through `additional-css`. A chapter's illustration must never be the thing a claim rests
  on; the linked data-true figure always is.

- **Wiring a figure:** the same shape, a different class, and no warning in the caption — because
  the picture *is* the data:

  ```html
  <figure class="chapter-figure">
    <img src="assets/slug.svg" alt="what is actually in the drawing, in words">
    <figcaption>one or two sentences on what the reader is looking at.
    <strong><a href="demos/chapter.html">Open the data-true drawing and …
    yourself</a></strong></figcaption>
  </figure>
  ```

  A figure may go where its beat is rather than only at the top, because it is part of the argument
  rather than an overture to it. `.chapter-figure` carries its own light card in every theme: a
  still is drawn in one dark ink on the demo page's own paper, and on mdBook's dark themes an
  untreated one would be ink on ink.

  **The bytes are the code's.** Every figure under `chapters/assets/` that is a still is emitted by
  [`tools/figures.mjs`](tools/figures.mjs), which drives the demo modules under node and writes what
  `stillFrom` produces. `make figures` rewrites them; `make check` refuses a committed figure that is
  not what the code emits today, and refuses itself if that comparison stops biting. A figure is
  therefore never touched by hand, and never edited into agreement with a chapter — the drawing
  changes, or the chapter does.

  **A figure may also be a page rather than an image.** The record's own renders are interactive
  HTML, snapshotted into `record/` and pinned by `record.lock`; a chapter puts one in front of the
  reader as a bold `Open the data-true…` link with a sentence saying what is in it. That link is a
  declaration: it is what puts the file in the book's footprint of the engine.

## Chapter concepts

| chapter | visual question — or, for a replaced study, what the reader gets instead | asset |
|---|---|---|
| 00 · The shadow | How can a visible shadow invite a test about its unseen source? | [`shadow-question.svg`](chapters/assets/shadow-question.svg) |
| 01 · Sharper shadows | How does a finer instrument change what the same measurement can tell you? | [`sharper-shadows.svg`](chapters/assets/sharper-shadows.svg) |
| 01 · Build the object | How do point, line, patch, and volume grow from one another? | [`build-object.svg`](chapters/assets/build-object.svg) |
| 02 · Is it round? | **replaced.** The question is answered by the run, so the chapter shows the run: the record's two rings at *The obvious setting* — the equal-weight dial beside the geometric one, each ring the measured speed in every direction it was timed in. `round-ripple.svg` is deleted. | [record 0115](record/lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html) · [record 0117](record/lab/warp-1-move/0117-dispersion-isotropy/figures/discovery.html) |
| 02b · Two worlds threaded | **replaced before it was drawn.** Three stills of the demo's own drawings, in the chapter's own order: the shape between with four faces bare, the same with a tip on every face, and the threaded pair as an orthographic wireframe. Plus the record's turnable render of the pair tiled. | [`four-faces-spare.svg`](chapters/assets/four-faces-spare.svg) · [`a-tip-on-every-face.svg`](chapters/assets/a-tip-on-every-face.svg) · [`the-threaded-pair.svg`](chapters/assets/the-threaded-pair.svg) · [record 0116](record/lab/primer/0116-tetoct-primer/figures/tetoct-render.html) |
| 03 · The bubble and its bill | Where does a shaped change place its cost? | [`bubble-bill.svg`](chapters/assets/bubble-bill.svg) |
| 04 · The wall | Can isolation work while the hoped-for inertial effect does not? | [`wall-two-answers.svg`](chapters/assets/wall-two-answers.svg) |
| 05 · Negative energy | How do boundaries change which vacuum modes fit? | [`vacuum-boundaries.svg`](chapters/assets/vacuum-boundaries.svg) |
| 06 · No answer key | Can a blind measuring process recover a class and keep its miss? | [`blind-class-and-its-miss.svg`](chapters/assets/blind-class-and-its-miss.svg) |
| 07 · Expected law fails | What happens when the observed trend is gentler than the proposed one? | [`gentler-than-proposed.svg`](chapters/assets/gentler-than-proposed.svg) |
| 08 · Your shadow | Can a reader walk from question to record without trusting the page? | [`walk-the-trail.svg`](chapters/assets/walk-the-trail.svg) |

Study 01 uses the same grammar for a chapter with no data in it: the same triangulation drawn three
times, solid for the reading that succeeds and dashed for the candidate that cannot be separated from
it, with a dashed span standing for the centuries between the second panel and the third. Nothing in
it is a measurement; it is the shape of the argument.

Studies 07–09 answer their chapter's question with the same grammar the earlier six use: **solid for
what was observed, dashed for what was proposed.** 06 puts the known-key panel beside the no-key
panel and draws the shortfall *inside a band that was drawn first*. 07 lets the steep dashed guess
and the gentle solid measurement leave one shared origin, and crosses out the guess. 08 draws the
trail as four repository stops with the page itself faint and deliberately off it.

## Replacement rule

Replace one asset at a time under the same filename, or update its `edition.json` declaration in the
same commit. Do not insert decorative numbers or realistic machinery: an illustration should help a
novice ask the chapter's question, while the data-true figure answers it.

**Retiring a study altogether** — which is what happens when the demo code, or the record, can draw
the thing — is the same edit plus two more: mark the row *replaced* in the table above, and delete
the file once nothing references it. A study left in `chapters/assets/` that no chapter shows is a
picture nobody has judged, waiting to be picked up by the next person who needs one.
