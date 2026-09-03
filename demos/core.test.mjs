// The cross-check: what the pages render is what the engine emitted, and nothing else.
//
// FIREWALL: this checks pages that run a toy DEC lattice. Nothing here is a claim about nature. See
// ../FIREWALL.md.
//
//   node demos/core.test.mjs
//
// **This check has changed its meaning, and the change is the point of step three-B.** It used to
// compare two implementations of the same arithmetic — `core.mjs`'s exact rationals in JavaScript
// against the napkin's in Python — because there were two. There is one now: the vendored engine.
// So what is checked is no longer *do the two agree* but **does the page show what the engine said**.
//
// Six gates, in the order of what they would catch:
//
//   1. **the engine is the engine.** The vendored wasm answers the census question with the
//      vendored JSON's own bytes, so the two artifacts under `engine/` are one engine.
//   2. **every rendered number is the engine's.** Every step of every chapter is rendered in every
//      state a reader can drive it into, and every numeric token on every surface she meets — a
//      table's cells, its caption, its column headings, the step's title, its one instruction, every
//      control's label, and every piece of text inside every drawing including the SVG `<desc>` — is
//      a value the engine returned in this run, that value negated, the length of one of its lists,
//      or an index into one. Nothing else.
//   3. **no number was typed.** `steps.mjs`'s own source is read and **any digit inside any string
//      literal is refused**, in any quote style, with `${…}` cut out because that is code. A count
//      arrives as an engine value or it does not arrive. The same rule is held over the pages' HTML:
//      no digit in any text a reader sees.
//   4. **the drawing is the census.** Every segment the wireframe draws is an edge the engine
//      exported and every dot one of its vertices, by name, both ways round; and the ring draws its
//      twelve lines with none crossing another.
//   5. **the steps are the outline's.** Every step maps onto exactly one marked chapter section,
//      every marked section is covered, and the beat numbers and questions are `steps.json`'s.
//   6. **the words are under budget.** Every reader-facing word on each page is counted and held
//      under the owner's limit, and the count is printed whether or not it passes.
//
// What no check here can catch is unchanged, and `DEMOS.md` says so in the same words: **a number
// computed correctly and then put in the wrong place.** Gate 3 is what shrinks that hole — a wrong
// number cannot be typed anywhere — but a value read out of the wrong field of the right answer is
// still invisible to a machine. Only reading the page catches that, which is what the proof-reader
// pass is for.

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const HERE = path.dirname(new URL(import.meta.url).pathname);
const ROOT = path.join(HERE, "..");
const ENGINE_DIR = path.join(ROOT, "engine");

const { Engine } = await import(pathToFileURL(path.join(HERE, "engine.mjs")).href);
const { drawings } = await import(pathToFileURL(path.join(HERE, "draw.mjs")).href);
const { chapterSteps } = await import(pathToFileURL(path.join(HERE, "steps.mjs")).href);
const { joinSteps, statesOf } = await import(pathToFileURL(path.join(HERE, "core.mjs")).href);

const failures = [];
const fail = (message) => failures.push(message);

// ── 1 · the engine is the engine ──────────────────────────────────────────────────────────────────

const glue = await import(pathToFileURL(path.join(ENGINE_DIR, "napkin.js")).href);
await glue.default({ module_or_path: readFileSync(path.join(ENGINE_DIR, "napkin_bg.wasm")) });

const payloadText = readFileSync(path.join(ENGINE_DIR, "napkin.json"), "utf8");
const payload = JSON.parse(payloadText);
const rows = JSON.parse(readFileSync(path.join(ENGINE_DIR, "rows.json"), "utf8"));

{
  // The census of the complete complex on four dots is chapters 1 and 2's whole object, and the
  // vendored JSON carries it. Byte for byte, not value for value: a tolerance here would be exactly
  // the seam the one-engine decision closes.
  const fromWasm = JSON.parse(glue.census_json(4));
  const fromJson = payload.complexes["4"];
  if (JSON.stringify(fromWasm) !== JSON.stringify(fromJson)) {
    fail("the vendored wasm and the vendored JSON disagree about the census on four dots");
  }
}

const engine = new Engine(glue, payload, rows);
const draw = drawings(engine);
const scaffold = JSON.parse(readFileSync(path.join(HERE, "steps.json"), "utf8"));
const definitions = chapterSteps(engine, draw);
const view = draw.wireDefaultView();

// ── 4a · the ring's own claim ─────────────────────────────────────────────────────────────────────

{
  const bare = draw.ringPlanarity({ tips: false });
  if (bare.lines !== payload.cut.oct_lines) {
    fail(`the ring drew ${bare.lines} lines, and the shape between has ${payload.cut.oct_lines}`);
  }
  if (bare.crossings !== 0 || bare.dotsOnLines !== 0) {
    fail(`the ring is degenerate: ${bare.crossings} crossing(s), ${bare.dotsOnLines} dot(s) on a line`);
  }
  const withTips = draw.ringPlanarity({ tips: true });
  if (withTips.amongTheTwelve !== 0 || withTips.dotsOnTheTwelve !== 0) {
    fail("adding the tips broke the twelve lines' own claim");
  }
  // The seven crossings are the outside tip's, and the number is pinned so that a change to the
  // layout has to be looked at rather than shipped.
  if (withTips.crossings !== 7) {
    fail(`the tips' lines cross ${withTips.crossings} times; the convention says seven`);
  }
  if (withTips.tipsInsideTheirFace !== 4) {
    fail(`${withTips.tipsInsideTheirFace} tips sit inside their own face; the convention says four`);
  }
}

// ── 4b · the wireframe is the census ──────────────────────────────────────────────────────────────

{
  const wire = draw.wireframe();
  const drawn = draw.drawWire({ yaw: view.yaw, pitch: view.pitch });
  const segments = [...drawn.matchAll(/data-edge="([^"]+)"/g)].map((found) => found[1]);
  const dots = [...drawn.matchAll(/data-dot="([^"]+)"/g)].map((found) => found[1]);

  if (segments.length !== payload.stella.lines) {
    fail(`the wireframe drew ${segments.length} segments; the engine has ${payload.stella.lines}`);
  }
  if (dots.length !== payload.stella.dots) {
    fail(`the wireframe drew ${dots.length} dots; the engine has ${payload.stella.dots}`);
  }
  const census = new Set(wire.edges.map(([a, b]) =>
    [wire.names[a], wire.names[b]].sort().join("|")));
  for (const segment of segments) {
    const key = segment.split("|").sort().join("|");
    if (!census.has(key)) fail(`the wireframe drew ${segment}, which is not an edge of the census`);
  }
  const drawnKeys = new Set(segments.map((s) => s.split("|").sort().join("|")));
  for (const key of census) {
    if (!drawnKeys.has(key)) fail(`the census has the edge ${key}, and the wireframe did not draw it`);
  }
  const names = new Set(wire.names);
  for (const dot of dots) {
    if (!names.has(dot)) fail(`the wireframe drew a dot called ${dot}, which the engine has not got`);
  }
  if (new Set(dots).size !== dots.length) fail("the wireframe drew a dot twice");
}

// ── 3 · no number was typed ───────────────────────────────────────────────────────────────────────

{
  const source = readFileSync(path.join(HERE, "steps.mjs"), "utf8");
  // Every string literal in the file, in all three quote styles, with a template's `${…}` cut out
  // because that is code and not text. Comments are stripped first: they are for a reader of the
  // source, and this rule is about what reaches a reader of the page.
  const stripped = source
    .replace(/\/\*[\s\S]*?\*\//g, " ")
    .replace(/(^|[^:])\/\/[^\n]*/g, "$1 ");
  const literals = [
    ...stripped.matchAll(/"((?:[^"\\\n]|\\.)*)"/g),
    ...stripped.matchAll(/'((?:[^'\\\n]|\\.)*)'/g),
    ...stripped.matchAll(/`((?:[^`\\]|\\.)*)`/g),
  ].map((found) => found[1].replace(/\$\{[^}]*\}/g, ""));
  for (const literal of literals) {
    if (/\d/.test(literal)) {
      fail(`steps.mjs types a digit into the string ${JSON.stringify(literal)} — every number on `
        + `these pages has to come off the engine`);
    }
  }
}

// ── 6 (part) and 3 (part) · the pages' own HTML ───────────────────────────────────────────────────

const PAGES = [
  "index.html",
  ...Object.keys(scaffold.chapters).map((slug) => `${slug}.html`),
];

/** The text a reader meets in a page's HTML: tags, scripts, styles and comments taken out. */
function readerText(html) {
  return html
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<head[\s\S]*?<\/head>/i, " ")
    .replace(/<[^>]+>/g, " ")
    .replace(/&[a-z]+;/gi, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const pageText = new Map();
for (const name of PAGES) {
  const html = readFileSync(path.join(HERE, name), "utf8");
  const text = readerText(html);
  pageText.set(name, text);
  if (/\d/.test(text)) {
    fail(`${name} has a digit in its own text — the beat numbers and every count come from the `
      + `engine and from steps.json at run time, so nothing numeric is written into a page`);
  }
}

// ── 2 · every rendered number is the engine's ─────────────────────────────────────────────────────

const NUMERIC_TOKEN = /[-−+]?\d+(?:[./]\d+)?/g;

/** Is this token something the engine said, or a plain restatement of it? */
function known(token) {
  const bare = token.replace(/^[-−+]/, "");
  const negated = `-${bare}`;
  return engine.emitted.has(token)
    || engine.emitted.has(bare)
    || engine.emitted.has(negated)
    || engine.emitted.has(token.replace(/^−/, "-").replace(/^\+/, ""));
}

/** Every piece of text a drawing puts on the paper, including what a screen reader is given. */
function drawingText(svg) {
  const out = [];
  for (const found of svg.matchAll(/<(title|desc|text)[^>]*>([\s\S]*?)<\/\1>/g)) {
    out.push(found[2]);
  }
  return out;
}

const wordsOf = (text) => text.split(/\s+/).filter((word) => /[a-z]/i.test(word)).length;

const report = [];
for (const [slug, chapter] of Object.entries(scaffold.chapters)) {
  const build = definitions[slug];
  if (!build) { fail(`there is no demo for the chapter ${slug}`); continue; }
  let joined;
  try {
    joined = joinSteps(slug, build(), scaffold);
  } catch (failure) {
    fail(`${slug}: ${failure.message}`);
    continue;
  }

  // ── 5 · the steps are the outline's ─────────────────────────────────────────────────────────
  const claimed = joined.steps.flatMap((step) => step.beats);
  const marked = chapter.sections.map((section) => section.beat);
  if (JSON.stringify(claimed) !== JSON.stringify(marked)) {
    fail(`${slug}: the steps claim beats ${claimed.join(", ")} and the chapter's markers say `
      + `${marked.join(", ")}`);
  }
  for (const step of joined.steps) {
    for (const section of step.sections) {
      const found = chapter.sections.find((entry) => entry.anchor === section.anchor);
      if (!found || found.beat !== section.beat || found.question !== step.sections
        .find((s) => s.anchor === section.anchor).question) {
        fail(`${slug}: the step for "${section.anchor}" does not agree with steps.json`);
      }
    }
  }

  // ── 2 and 6 · render everything, scan everything, count the words ───────────────────────────
  const words = new Set();
  words.add(pageText.get(`${slug}.html`));
  words.add(chapter.title);
  let surfaces = 0;
  let tokens = 0;

  for (const step of joined.steps) {
    words.add(step.title);
    words.add(step.act);
    words.add(step.label);
    for (const control of step.controls) {
      if (control.noun) words.add(control.noun);
      if (control.label) words.add(control.label);
      if (control.names) for (const name of control.names) words.add(name);
      if (control.options) for (const option of control.options) words.add(option.label);
    }
    for (const state of statesOf(step, view)) {
      let rendered;
      try {
        rendered = step.render(state);
      } catch (failure) {
        fail(`${slug} ${step.label}: rendering threw — ${failure.message}`);
        continue;
      }
      // The step's own label — "beat 41", "beats 37–38" — is the one place a number on the page is
      // not the engine's, and it is not typed either: it is `steps.json`'s, derived from the
      // chapter's markers, and gate 5 above holds it to them. Everything else is scanned.
      const surfacesHere = [
        step.title, step.act,
        ...step.controls.flatMap((control) => [
          control.noun, control.label,
          ...(control.names || []),
          ...(control.options || []).map((option) => option.label),
        ]).filter((text) => text !== undefined),
        ...drawingText(rendered.drawing),
        ...rendered.tables.flatMap((table) =>
          [table.caption, ...table.head, ...table.rows.flat()]),
      ];
      surfaces += surfacesHere.length;
      for (const surface of surfacesHere) {
        for (const token of String(surface).match(NUMERIC_TOKEN) || []) {
          tokens += 1;
          if (!known(token)) {
            fail(`${slug} ${step.label}: the number ${token} appears in "${surface}", and the `
              + `engine did not produce it`);
          }
        }
      }
      if (!rendered.tables.length) {
        fail(`${slug} ${step.label}: a step with no table — every number has to be readable as text`);
      }
      if (!/^<svg/.test(rendered.drawing)) {
        fail(`${slug} ${step.label}: a step with no drawing`);
      }
    }
  }

  // The controls the page always draws, counted once per page rather than per step.
  for (const word of ["back", "on", "play", "stop", "again", "still", "download", "read it",
    "theme", "light", "dark", "straighten it"]) {
    words.add(word);
  }
  const count = [...words].reduce((total, text) => total + wordsOf(text), 0);
  report.push({ slug, steps: joined.steps.length, beats: chapter.sections.length, words: count });
}

// ── 6 · the budget ────────────────────────────────────────────────────────────────────────────────

const BUDGET = 250;
for (const line of report) {
  if (line.words > BUDGET) {
    fail(`${line.slug}: ${line.words} reader-facing words, and the budget is ${BUDGET}`);
  }
}

// ── the verdict ───────────────────────────────────────────────────────────────────────────────────

for (const line of report) {
  process.stdout.write(`core.test.mjs: ${line.slug} — ${line.steps} steps over ${line.beats} `
    + `beats, ${line.words} words\n`);
}

if (failures.length) {
  for (const failure of failures) process.stderr.write(`${failure}\n`);
  process.exit(1);
}

const totalWords = report.reduce((total, line) => Math.max(total, line.words), 0);
const totalSteps = report.reduce((total, line) => total + line.steps, 0);
process.stdout.write(
  `core.test.mjs: ${report.length} chapters, ${totalSteps} steps, every rendered number the `
  + `engine's, no digit typed, ${engine.calls.length} engine calls, the wireframe's `
  + `${payload.stella.lines} segments the census's, at most ${totalWords} words on a page\n`,
);
