# Our Bubble illustration direction

The illustrations are a gentle visual ramp into each chapter. They are **editorial analogy images**,
not plots, measurements, or depictions of physical reality. Data-true figures remain linked in the
body with an explicit `Open the data-true…` label.

## Shared language

- **Format:** 1200 × 600 responsive SVG, readable in light and dark mdBook themes.
- **Shape:** soft fields, rounded panels, generous empty space, one visual question per chapter.
- **Palette:** midnight `#101a2c`, ink `#20314a`, paper `#f4ead8`, teal `#55c7be`, coral `#f28c78`,
  and gold `#f4c95d`.
- **Line:** rounded caps and joins; solid lines for the object being noticed, dashed lines for a
  proposal, comparison, or expectation.
- **Status:** all nine assets exist and every chapter carries one. Each is stamped
  `ILLUSTRATION STUDY` in the artwork itself—a composition suitable for reading now and
  straightforward to replace later without touching the chapter that hosts it.
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

## Chapter concepts

| chapter | visual question | asset |
|---|---|---|
| 00 · The shadow | How can a visible shadow invite a test about its unseen source? | [`shadow-question.svg`](chapters/assets/shadow-question.svg) |
| 01 · Sharper shadows | How does a finer instrument change what the same measurement can tell you? | [`sharper-shadows.svg`](chapters/assets/sharper-shadows.svg) |
| 01 · Build the object | How do point, line, patch, and volume grow from one another? | [`build-object.svg`](chapters/assets/build-object.svg) |
| 02 · The round ripple | Does the constructed grid steer a pulse away from roundness? | [`round-ripple.svg`](chapters/assets/round-ripple.svg) |
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
