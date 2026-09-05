// The chapters' data-true figures, rendered by the demo code that draws them on screen.
//
// FIREWALL: these drawings are of a toy DEC lattice. Nothing in them is a claim about nature.
// See ../FIREWALL.md.
//
//   node tools/figures.mjs            write chapters/assets/*.svg
//   node tools/figures.mjs --check    refuse if what is committed is not what the code emits
//
// WHY THIS EXISTS. `chapters/assets/` used to hold hand-drawn SVG studies — editorial analogy
// pictures of what a chapter was about. The owner called them slop, and R10 says the sim IS the
// graphic. So the pictures of the object are now the demo's own drawings: every stroke here is an
// edge the vendored engine exported and every dot one of its vertices, drawn by `demos/draw.mjs`
// and stamped by `demos/core.mjs`'s `stillFrom` — the same function behind the "still" button a
// reader presses on the demo pages. Nothing in this file draws anything.
//
// THE PAPERTETRA LESSON, which is the reason for `--check`: a figure that is generated once and
// then committed is a figure that drifts. The bytes in `chapters/assets/` must be exactly what this
// code emits today, so `make check` runs `--check` and goes red the moment a drawing changes and
// the asset does not — or the asset is touched and the drawing did not. Neither direction is
// allowed to be silent.
//
// AND THE SET, not only the bytes. `FIGURES` says what this code draws; the chapters say what the
// reader is shown; `--check` insists those are the same set. Without that, a figure the book
// actually shows could be hand-drawn — drop its row here, paint the SVG, and a byte-identity check
// over the rows that remain goes green. A reviewer did exactly that, on this file, before this
// paragraph existed.
//
// AND ITS OWN MUTATIONS, in the same file, because a guard nobody has watched fail is a guard
// nobody has tested (DEMOS.md, standing rule). `--check` finishes by attacking itself twice, and
// the line it prints at the end is built from what the run counted rather than written in advance.

import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath, pathToFileURL } from "node:url";
import path from "node:path";

// `fileURLToPath`, not `new URL(...).pathname`: the second leaves a checkout path containing a
// space or a `#` percent-encoded, and every read below would then quietly miss.
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(HERE, "..");
const DEMOS = path.join(ROOT, "demos");
const ENGINE_DIR = path.join(ROOT, "engine");
const ASSETS = path.join(ROOT, "chapters", "assets");

const load = (file) => import(pathToFileURL(path.join(DEMOS, file)).href);

const { Engine } = await load("engine.mjs");
const { drawings } = await load("draw.mjs");
const { chapterSteps } = await load("steps.mjs");
const { joinSteps, initialState, stillFrom } = await load("core.mjs");

const glue = await import(pathToFileURL(path.join(ENGINE_DIR, "napkin.js")).href);
await glue.default({ module_or_path: readFileSync(path.join(ENGINE_DIR, "napkin_bg.wasm")) });

const engine = new Engine(
  glue,
  JSON.parse(readFileSync(path.join(ENGINE_DIR, "napkin.json"), "utf8")),
  JSON.parse(readFileSync(path.join(ENGINE_DIR, "rows.json"), "utf8")),
);
const draw = drawings(engine);
const scaffold = JSON.parse(readFileSync(path.join(DEMOS, "steps.json"), "utf8"));
const definitions = chapterSteps(engine, draw);

/**
 * The figures the chapters carry, each named by the step it is a still of.
 *
 * A figure is a **chapter section's own step**, in a **named state**, and nothing else: no camera,
 * no crop, no arrangement chosen here. `anchor` is the chapter section the step covers, which is
 * how `demos/core.mjs` addresses a step everywhere else, so a renumbered beat is a failure here
 * rather than a figure of the wrong thing.
 *
 * `at` may only reach for a control's own numbers — never a typed one — which is the same rule
 * `core.test.mjs` holds `steps.mjs` to. The opening state is `initialState`'s; anything else is
 * that state with a count the step itself declares.
 */
const FIGURES = [
  {
    file: "four-faces-spare.svg",
    slug: "two-worlds-threaded",
    anchor: "four-faces-spare",
    at: () => ({}),
  },
  {
    file: "a-tip-on-every-face.svg",
    slug: "two-worlds-threaded",
    anchor: "four-faces-spare",
    at: (step) => ({ tick: step.controls[0].count }),
  },
  {
    file: "the-threaded-pair.svg",
    slug: "two-worlds-threaded",
    anchor: "two-tetrahedra-threaded",
    at: () => ({}),
  },
];

/** Render one figure to the exact bytes that belong in `chapters/assets/`. */
function render(figure) {
  const { steps } = joinSteps(figure.slug, definitions[figure.slug](), scaffold);
  const step = steps.find((candidate) => candidate.anchors.includes(figure.anchor));
  if (!step) {
    throw new Error(`${figure.file}: ${figure.slug} has no step covering "${figure.anchor}"`);
  }
  const view = draw.wireDefaultView();
  const state = { ...initialState(step, view), ...figure.at(step) };
  const drawing = step.render(state).drawing;
  // The drawing's own title, kept rather than replaced: it is the sentence the demo says about
  // this exact state, and a figure that retitled itself here would be a caption nothing checks.
  const title = (/<title>([^<]*)<\/title>/.exec(drawing) || [])[1];
  if (!title) throw new Error(`${figure.file}: the drawing carries no title to keep`);
  return `${stillFrom(withoutTheInvitation(drawing), {
    chapter: figure.slug, step: step.label, title,
  })}\n`;
}

/**
 * The one sentence this file takes out of a drawing, and why.
 *
 * The wireframe's own `<desc>` ends by inviting the reader to drag it and to read the numbers in
 * the table below — true on the demo page, and false in a committed book asset, where there is
 * nothing to drag and no table under it. A reader who opens the file directly is the one person
 * that sentence is written for, so leaving it is not harmless. Nothing is written in its place:
 * this removes a sentence, it does not author one, and what is left is byte-checked like the rest.
 */
function withoutTheInvitation(drawing) {
  return drawing.replace(/\s*Drag it,[^.]*\.(?=<\/desc>)/, "");
}

/** What is on disk, or nothing at all. */
function committed(file) {
  try {
    return readFileSync(path.join(ASSETS, file), "utf8");
  } catch {
    return null;
  }
}

/**
 * Every asset a chapter shows inside a `chapter-figure` block, read off the chapters themselves.
 *
 * This is the other half of the guard: `FIGURES` is what the code draws, this is what the reader is
 * shown, and neither may contain something the other does not.
 */
function shownByTheChapters() {
  const shown = new Map();
  const dir = path.join(ROOT, "chapters");
  for (const name of readdirSync(dir).filter((file) => file.endsWith(".md"))) {
    const markdown = readFileSync(path.join(dir, name), "utf8");
    for (const block of markdown.matchAll(/<figure class="chapter-figure">([\s\S]*?)<\/figure>/g)) {
      for (const image of block[1].matchAll(/<img[^>]*\bsrc="assets\/([^"]+)"/g)) {
        shown.set(image[1], name);
      }
    }
  }
  return shown;
}

/**
 * Compare one figure's bytes against the file, and say what is wrong in the reader's terms.
 *
 * Separated from the checks below so the self-attacks can call the same function: a check whose
 * mutation exercises a different code path is not that check's mutation.
 *
 * The message names the first character that differs rather than the two lengths. It used to print
 * the lengths, which on a same-length change read as a contradiction — "6615 committed, 6615
 * emitted" — and told whoever hit it nothing about what had moved.
 */
function drift(file, emitted, onDisk) {
  if (onDisk === null) return `${file} is not committed, and the code emits it`;
  if (onDisk === emitted) return null;
  let at = 0;
  while (at < onDisk.length && at < emitted.length && onDisk[at] === emitted[at]) at += 1;
  return `${file} is not what the code emits — first difference at character ${at}: `
    + `committed ${JSON.stringify(onDisk.slice(at, at + 30))}, `
    + `emitted ${JSON.stringify(emitted.slice(at, at + 30))}`;
}

const rendered = FIGURES.map((figure) => ({ file: figure.file, bytes: render(figure) }));

if (process.argv.includes("--check")) {
  const problems = [];
  // Every check below records what it actually did, and the pass line at the end is built from
  // these counters and from nothing else. A headline a check writes about itself can be true while
  // the check is switched off — `check_edition.py`'s `status()` exists for the same reason.
  let compared = 0;
  let matchedToChapters = 0;
  const refused = [];

  for (const { file, bytes } of rendered) {
    const found = drift(file, bytes, committed(file));
    if (found) problems.push(found);
    else compared += 1;
  }

  const shown = shownByTheChapters();
  const drawn = new Set(FIGURES.map((figure) => figure.file));
  for (const [file, chapter] of shown) {
    if (drawn.has(file)) matchedToChapters += 1;
    else {
      problems.push(`chapters/${chapter} shows assets/${file} as a data-true figure and nothing `
        + `here draws it — a figure is never hand-drawn (ART_DIRECTION.md)`);
    }
  }
  for (const file of drawn) {
    if (!shown.has(file)) {
      problems.push(`${file} is drawn here and no chapter shows it — a still no chapter has `
        + `placed is a picture nobody has judged`);
    }
  }

  if (problems.length) {
    for (const problem of problems) process.stderr.write(`figures: ${problem}\n`);
    process.stderr.write(
      "figures: the committed figures are not what demos/ draws, or are not the set the chapters "
      + "show. Run `make figures` and commit the result, or put back what changed.\n",
    );
    process.exit(1);
  }

  // ── the mutations, on this run ─────────────────────────────────────────────────────────────────
  //
  // Two, because one was not enough. A reviewer switched the comparison off by making `render()`
  // return the committed file instead of drawing it, and the byte-flip below stayed red while the
  // check as a whole went green on a hand-painted SVG.
  const [first] = rendered;

  // 1 · the comparison sees an altered byte.
  if (drift(first.file, `${first.bytes.slice(0, -1)} `, first.bytes) === null) {
    process.stderr.write(
      "figures: the byte-identity check passed a figure it had just altered — the guard is not "
      + "guarding, and no number of green runs would have said so\n",
    );
    process.exit(1);
  }
  refused.push("a figure with one byte changed");

  // 2 · what is being compared really came out of the drawing code. A second figure's step is
  // rendered under the first one's name, and it has to come out different. If `render()` has been
  // made to read the committed file, the two are identical and this says so.
  const other = FIGURES.find((figure) => figure.file !== first.file);
  if (render({ ...other, file: first.file }) === first.bytes) {
    process.stderr.write(
      "figures: two different steps rendered to the same bytes — what this file compares is not "
      + "coming from the drawing code, so the comparison proves nothing about the figures\n",
    );
    process.exit(1);
  }
  refused.push("bytes that did not come from the drawing code");

  if (compared !== FIGURES.length || matchedToChapters !== shown.size || refused.length !== 2) {
    process.stderr.write(
      `figures: the run did not do what the pass line would have claimed — ${compared} compared, `
      + `${matchedToChapters} matched to a chapter, ${refused.length} attack(s) refused\n`,
    );
    process.exit(1);
  }
  const total = rendered.reduce((sum, one) => sum + one.bytes.length, 0);
  process.stdout.write(
    `figures.mjs: ${compared} chapter figure(s), ${total} bytes, byte-for-byte what demos/ draws; `
    + `${matchedToChapters} of them shown by a chapter and nothing else shown as one; and this run `
    + `refused ${refused.join(" and ")}\n`,
  );
} else {
  for (const { file, bytes } of rendered) {
    writeFileSync(path.join(ASSETS, file), bytes);
    process.stdout.write(`figures: wrote chapters/assets/${file} (${bytes.length} bytes)\n`);
  }
}
