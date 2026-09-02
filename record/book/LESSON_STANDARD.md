# The lesson standard

*How a chapter is built, and what makes a figure a data-true infographic of **The Container**. This is the contract every
chapter follows so the public book and the study guide stay in lock-step and every picture is
honest. Copy [`templates/LESSON_TEMPLATE.md`](templates/LESSON_TEMPLATE.md) to start one.*

> **FIREWALL.** Every chapter is about a toy lattice computation. Naming is literal solver/geometry
> vocabulary; nothing is a claim about nature. The firewall line is **mandatory** and appears on the
> page and on every infographic.

---

## 1. The two-voice rule

Each chapter is authored **once** but read **two ways**:

- **Public voice** — plain language, no equations required, carried by the hero infographic. Answers
  *what is this, and why is it interesting?*
- **Study-guide voice** — the rigorous companion in the same chapter: the prediction, the gate, the
  numbers, the caveats, the reproduce-it commands, the exercises.

Authoring once keeps them from drifting. A chapter is **not done** until both voices are present and
its figures regenerate from the committed data.

## 2. Anatomy of a chapter (the required sections)

1. **Title + one-line concept** — the single idea the chapter teaches.
2. **Firewall scope line** — what the words mean here; what is *not* claimed.
3. **Source** — the `lab/NNNN/` run(s) and the `tests/…_gate.rs` gate(s) this chapter is built on.
4. **The hook** *(public)* — the question, in human terms.
5. **The prediction** *(study guide)* — what we expected and the gate that decides it, registered
   **before** the run (R1/P1). State a null/negative outright if that's what happened.
6. **The figure(s)** — the data-true infographic(s) (see §3), each with a traceable caption.
7. **What happened** — the result in both voices: the plain-language takeaway *and* the numbers with
   tolerances. **Negatives are first-class** (R5) — a "this doesn't work" chapter is a real chapter.
8. **Reproduce** — the exact commands (the gate + the viz export) that regenerate the data and the
   figures, pinned to a commit.
9. **Try it / exercises** *(study guide)* — a parameter to change, a prediction to make, a knob on
   the live infographic.

## 3. The infographic standard (R10++)

R10 is the rule: **the sim IS the graphic.** These are the specifics that make a figure publishable.

**Data-true (non-negotiable).**
- Every value shown is read from the run's real output (`lab/NNNN/data/…`), never hand-drawn,
  faked, or "illustrative." If it's not in the data, it's not in the figure.
- The figure is produced by a **viz exporter** (`viz`, #8) + a renderer (the viz app, #9) —
  the same "browser/page computes no physics, it renders the engine's export" discipline as the
  `A → F → E/B` viewer.
- **Traceable caption:** every figure cites its `lab/NNNN`, the data file, and the gate, so a reader
  can diff the picture against the numbers.

**Self-contained.**
- One file, no external fonts / CDNs / network (CSP-safe) — inline CSS/JS, embed assets as data URIs.
  (The `A → F → E/B` viewer is the reference build.)

**Consistent visual language.**
- The shared palette and ramp (carried from the viz gallery): background `#0b0e13`, ink `#e6edf5`,
  and the field ramp `#1e3a8a → #06b6d4 → #eab308 → #ef4444`; gold `#eab308` for the photon `A`,
  violet/amber for the B/E split, green for the `d²=0` / null state.
- A standing **firewall banner** and, where scale is shown, the **scale-free note** (the toy carries
  no intrinsic length).
- A legend for every layer; units or "dimensionless (firewall)" stated.

**Honest.**
- Show the negative result as plainly as the positive (R5). If a quantity is an artifact (e.g. a
  lattice-anisotropy term), label it as such — don't smooth it away.
- No decorative axes, no implied precision beyond the tolerance.

**Accessible.**
- Honor `prefers-reduced-motion`; keep contrast legible; don't rely on color alone (pair color with
  label/shape).

## 4. Naming & layout

```
book/chapters/NN-slug/
  chapter.md        # the authored chapter (both voices, from the template)
  figures/          # the self-contained infographic(s) + the data snapshot they render
  PROVENANCE.md     # commands + commit that produced the data and figures
```

`NN` orders the chapter; `slug` is the concept (e.g. `03-the-light-cone`). The chapter index lives in
[`chapters/README.md`](chapters/README.md).

## 5. Definition of done (per chapter)

- [ ] Both voices present (public hook + study-guide rigor); one source.
- [ ] Firewall scope line on the page and on every figure.
- [ ] Every figure data-true, self-contained, with a traceable caption (lab + gate + data file).
- [ ] Prediction registered before the run (R1); result reported honestly, negatives included (R5).
- [ ] `PROVENANCE.md` regenerates the data and figures from a pinned commit.
