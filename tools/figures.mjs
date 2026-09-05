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
  const out = drawing.replace(/\s*Drag it,[^.]*\./, "");
  // A strip that has quietly become a no-op is invisible: the sentence comes back, the committed
  // bytes are regenerated to match, and the check is green over a file that lies to the one reader
  // it is written for. So the removal is required to remove something whenever there is something
  // to remove. Found by a reviewer, who moved the sentence off the end of the description.
  if (out === drawing && /Drag it,/.test(drawing)) {
    throw new Error("the drawing still invites an interaction and the strip did not fire");
  }
  return out;
}

/**
 * What is on disk, or nothing at all — and a count of how often this file was actually opened.
 *
 * The count is the honest half. A reviewer changed one token at the comparison's call site so that
 * the emitted bytes were compared with themselves, and the run printed "byte-for-byte what demos/
 * draws" over a hand-painted SVG with every counter adding up. A counter that counts iterations
 * counts nothing. This one counts reads, and the pass below refuses to print unless there is one
 * per figure.
 */
let readsFromDisk = 0;
function committed(file) {
  try {
    const bytes = readFileSync(path.join(ASSETS, file), "utf8");
    readsFromDisk += 1;
    return bytes;
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
    for (const block of markdown.matchAll(/<figure\b([^>]*)>([\s\S]*?)<\/figure>/g)) {
      if (!classesOf(block[1]).includes("chapter-figure")) continue;
      for (const image of block[2].matchAll(/<img\b[^>]*>/g)) {
        const source = attribute(image[0], "src");
        if (source === null) continue;
        const asset = /^\.?\/?assets\/(.+)$/.exec(source);
        if (asset) shown.set(asset[1], name);
      }
    }
  }
  return shown;
}

/**
 * One attribute of one tag, in either quote style.
 *
 * The first version of the two functions above matched `class="chapter-figure"` and `src="assets/`
 * as literal strings. A reviewer walked past all of it three ways without changing a pixel of the
 * page: `class="chapter-figure wide"` (the stylesheet still matches), `src="./assets/…"`, and
 * `src='assets/…'` — and shipped a hand-painted SVG into the built book with every check green.
 * An attribute is a thing with a shape; matching the shape is the fix, and the same reading is what
 * lets `classesOf` treat the class as the token list it is.
 */
function attribute(tag, name) {
  const found = new RegExp(`\\b${name}\\s*=\\s*("([^"]*)"|'([^']*)')`).exec(tag);
  if (!found) return null;
  return found[2] !== undefined ? found[2] : found[3];
}

/** The class attribute of a tag, as the list of names it is. */
function classesOf(tag) {
  return (attribute(`<x ${tag}>`, "class") || "").trim().split(/\s+/).filter(Boolean);
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

/**
 * Compare every figure against what `read` hands back — the one place a figure is ever compared.
 *
 * The seam is the point. Both self-attacks below run through this function rather than calling
 * `drift` beside it, so an attack has to break the path the real run takes; the previous version
 * called `drift` directly and stayed green while the loop it was standing in for compared the
 * emitted bytes with themselves.
 */
function compareAll(read) {
  const problems = [];
  let matched = 0;
  let bytes = 0;
  for (const figure of rendered) {
    const onDisk = read(figure.file);
    const found = drift(figure.file, figure.bytes, onDisk);
    if (found) problems.push(found);
    else { matched += 1; bytes += onDisk.length; }
  }
  return { problems, matched, bytes };
}

if (process.argv.includes("--check")) {
  // Every check below records what it actually did, and the pass line at the end is built from
  // these and from nothing else. A headline a check writes about itself can be true while the check
  // is switched off — `check_edition.py`'s `status()` exists for the same reason.
  const real = compareAll(committed);
  const problems = [...real.problems];
  const refused = [];

  const shown = shownByTheChapters();
  const drawn = new Set(FIGURES.map((figure) => figure.file));
  let matchedToChapters = 0;
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
  // Both go through `compareAll`, which is the path the real run above took.
  const [first] = rendered;

  // 1 · a changed byte in a committed file is seen. The reader is the real one, wrapped.
  const flipped = compareAll(
    (file) => (file === first.file ? `${committed(file).slice(0, -1)} ` : committed(file)),
  );
  if (!flipped.problems.some((problem) => problem.startsWith(first.file))) {
    process.stderr.write(
      "figures: the comparison passed a figure whose committed bytes had just been altered — the "
      + "guard is not guarding, and no number of green runs would have said so\n",
    );
    process.exit(1);
  }
  refused.push("a figure whose committed bytes were altered");

  // 2 · what is compared really came out of the drawing code. A second figure's step is rendered
  // under the first one's name, and it has to come out different. If `render()` has been made to
  // read the committed file, the two are identical and this says so.
  const other = FIGURES.find((figure) => figure.file !== first.file);
  if (render({ ...other, file: first.file }) === first.bytes) {
    process.stderr.write(
      "figures: two different steps rendered to the same bytes — what this file compares is not "
      + "coming from the drawing code, so the comparison proves nothing about the figures\n",
    );
    process.exit(1);
  }
  refused.push("bytes that did not come from the drawing code");

  // The pass line is refused unless the run did what it would have claimed: one comparison per
  // figure, one file opened per comparison in each of the two passes, every figure a chapter shows
  // accounted for, and both attacks refused.
  const expectedReads = rendered.length * 2;
  if (real.matched !== FIGURES.length || matchedToChapters !== shown.size
    || readsFromDisk !== expectedReads || refused.length !== 2) {
    process.stderr.write(
      `figures: the run did not do what the pass line would have claimed — ${real.matched} `
      + `compared, ${matchedToChapters} matched to a chapter, ${readsFromDisk} file(s) opened `
      + `against ${expectedReads} expected, ${refused.length} attack(s) refused\n`,
    );
    process.exit(1);
  }
  process.stdout.write(
    `figures.mjs: ${real.matched} chapter figure(s), ${real.bytes} bytes read off disk and `
    + `byte-for-byte what demos/ draws; ${matchedToChapters} of them shown by a chapter and `
    + `nothing else shown as one; and this run refused ${refused.join(" and ")}\n`,
  );
} else {
  for (const { file, bytes } of rendered) {
    writeFileSync(path.join(ASSETS, file), bytes);
    process.stdout.write(`figures: wrote chapters/assets/${file} (${bytes.length} bytes)\n`);
  }
}
