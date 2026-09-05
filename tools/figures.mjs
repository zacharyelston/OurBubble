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
// AND ITS OWN MUTATION, in the same file, because a guard nobody has watched fail is a guard nobody
// has tested (DEMOS.md, standing rule): `--check` finishes by feeding itself a single altered byte
// and requiring its own comparison to report the difference. If that self-attack comes back clean,
// this exits non-zero saying so.

import { readFileSync, writeFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const HERE = path.dirname(new URL(import.meta.url).pathname);
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
  const { chapter, steps } = joinSteps(
    figure.slug, definitions[figure.slug](), scaffold,
  );
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
  return `${stillFrom(drawing, { chapter: figure.slug, step: step.label, title })}\n`;
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
 * Compare one figure's bytes against the file, and say what is wrong in the reader's terms.
 *
 * Separated from the loop below so the self-attack can call the same function on altered bytes:
 * a check whose mutation exercises a different code path is not that check's mutation.
 */
function drift(file, emitted, onDisk) {
  if (onDisk === null) return `${file} is not committed, and the code emits it`;
  if (onDisk !== emitted) {
    return `${file} is not what the code emits — ${onDisk.length} byte(s) committed, `
      + `${emitted.length} emitted`;
  }
  return null;
}

const rendered = FIGURES.map((figure) => ({ file: figure.file, bytes: render(figure) }));

if (process.argv.includes("--check")) {
  const problems = [];
  for (const { file, bytes } of rendered) {
    const found = drift(file, bytes, committed(file));
    if (found) problems.push(found);
  }
  if (problems.length) {
    for (const problem of problems) process.stderr.write(`figures: ${problem}\n`);
    process.stderr.write(
      "figures: the committed figures are not what demos/ draws. Run `make figures` and commit "
      + "the result, or put back the drawing that changed.\n",
    );
    process.exit(1);
  }
  // The mutation. One byte of one emitted figure is altered and the same comparison is asked
  // again; a check that cannot see that has stopped checking anything, and says so here rather
  // than on the day a drawing changes.
  const [first] = rendered;
  const altered = `${first.bytes.slice(0, -1)} `;
  if (drift(first.file, altered, first.bytes) === null) {
    process.stderr.write(
      "figures: the byte-identity check passed a figure it had just altered — the guard is not "
      + "guarding, and no number of green runs would have said so\n",
    );
    process.exit(1);
  }
  const total = rendered.reduce((sum, one) => sum + one.bytes.length, 0);
  process.stdout.write(
    `figures.mjs: ${rendered.length} chapter figure(s), ${total} bytes, byte-for-byte what `
    + `demos/ draws — and the same comparison refused a figure with one byte changed\n`,
  );
} else {
  for (const { file, bytes } of rendered) {
    writeFileSync(path.join(ASSETS, file), bytes);
    process.stdout.write(`figures: wrote chapters/assets/${file} (${bytes.length} bytes)\n`);
  }
}
