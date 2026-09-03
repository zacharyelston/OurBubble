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
//   4. **the drawing is the census.** The wireframe may emit only seven element names — a
//      whitelist, not a search — every one of its strokes is an edge the engine exported and every
//      dot one of its vertices, thirty-six and fourteen, both ways round, and the pair each stroke
//      is held to is taken from **where its ends actually are** rather than from what it says about
//      itself. The ring is held separately to drawing its twelve lines with none crossing another.
//      And a drawing's own sentences — its `<title>` and `<desc>` — carry no digit at all.
//   5. **the steps are the outline's.** Every step maps onto exactly one marked chapter section,
//      every marked section is covered, and the beat numbers and questions are `steps.json`'s.
//   6. **the words are under budget.** Every reader-facing word on each page is counted and held
//      under the owner's limit, and the count is printed whether or not it passes.
//   7. **a table says what its numbers mean, and a total is a total.** Every table whose rows carry
//      three or more numbers declares itself — `{ total: i }` or `{ notASum: true }` — and a
//      declared total is added up here, on the digits a reader sees, on every row of every state.
//      The declaration is by **column index** rather than by heading, because the first version of
//      this gate read the column headed "added up" and was switched off twice: once by renaming
//      that column in the same edit that broke the arithmetic under it, once by moving the terms
//      into a second table. This is the one part of the "right value, wrong place" hole a machine
//      *can* close, and the hole was not hypothetical: this pass shipped two walks whose printed
//      terms did not add to their printed total, and a fresh reader found both by doing the
//      arithmetic the page invites her to do.
//   8. **no label is struck through.** Every piece of text in every drawing, at every state, has
//      its box tested against every stroke and every dot in that drawing — from the emitted SVG,
//      not from the placement code's own opinion of where it put things. This one exists because
//      three rounds of "fixed" label rules were not: a rule that has to be right everywhere on a
//      drawing with twelve or thirty-six lines through it will be wrong somewhere, so the placement
//      searches for a clear spot and this is what says it found one.
//   9. **the numbers DEMOS.md quotes about the sweep are the sweep's.** The crossings paragraph is
//      the only quantitative prose in this lane that no gate held, and it carried a wrong measured
//      figure in three consecutive rounds. Every number it now quotes is asserted here, so the
//      paragraph cannot drift from the code again — and the rule that came with it is that the
//      paragraph quotes *only* numbers this gate asserts.
//  10. **every still stands on its own.** The still button is the reason the drawing code exists —
//      those files are the intended replacement for the chapters' illustration studies — and it is
//      the one surface a reader reaches by downloading rather than by looking, so a proof-reader
//      could not exercise it at all. Every step, in every state, is rendered to its still, and the
//      still is held to carrying its own stylesheet, its own title and description, and the
//      firewall.
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
const { drawings, viewCost, VIEW_GRID, project3d, textBox, boxMeetsSegment, boxesOverlap,
  LABEL_GAP } = await import(pathToFileURL(path.join(HERE, "draw.mjs")).href);
const { chapterSteps } = await import(pathToFileURL(path.join(HERE, "steps.mjs")).href);
const { joinSteps, statesOf, stillFrom } = await import(
  pathToFileURL(path.join(HERE, "core.mjs")).href);

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

  // The dots first, with where each one actually is on the paper.
  const dots = [...drawn.matchAll(
    /<circle[^>]*data-dot="([^"]+)"[^>]*cx="([-\d.]+)"[^>]*cy="([-\d.]+)"/g)]
    .map((found) => ({ name: found[1], x: Number(found[2]), y: Number(found[3]) }));
  const names = new Set(wire.names);
  if (dots.length !== payload.stella.dots) {
    fail(`the wireframe drew ${dots.length} dots; the engine has ${payload.stella.dots}`);
  }
  for (const dot of dots) {
    if (!names.has(dot.name)) {
      fail(`the wireframe drew a dot called ${dot.name}, which the engine has not got`);
    }
  }
  if (new Set(dots.map((dot) => dot.name)).size !== dots.length) {
    fail("the wireframe drew a dot twice");
  }

  // And now the lines, **by where their ends are**, not by what they say about themselves. A
  // proof-reader pointed every line at the wrong dot while leaving its `data-edge` attribute honest
  // and this gate stayed green — while the step's own table invites a reader to count the lines off
  // the picture. So each end is resolved to the nearest drawn dot, and the pair that comes back is
  // what is held to the census. The attribute is then checked against the geometry as well, so the
  // two can no longer disagree in either direction.
  const nearestDot = (x, y) => dots.reduce((best, dot) => {
    const distance = Math.hypot(dot.x - x, dot.y - y);
    return best === null || distance < best.distance ? { dot, distance } : best;
  }, null);
  // EVERY mark, of every kind. Two versions of this gate have now been walked past: the first
  // matched only lines carrying a `data-edge`, so an unlabelled stroke joining nothing to nothing
  // rode into a commit while the count stayed at thirty-six; the second matched only `<line>`, so
  // the same stroke came back as a `<path>`. A drawing does not get to decide which of its own
  // marks are up for checking, and it does not get to decide by choosing an element name either.
  // So the wireframe is held to a **whitelist**: these tags and no others.
  const WIRE_TAGS = ["svg", "title", "desc", "g", "line", "circle", "text"];
  for (const found of drawn.matchAll(/<([a-zA-Z][\w-]*)/g)) {
    if (!WIRE_TAGS.includes(found[1])) {
      fail(`the wireframe drew a <${found[1]}>, and it may only draw `
        + `${WIRE_TAGS.join(", ")} — every mark in it has to be a line of the census or a dot`);
    }
  }
  const strokes = [...drawn.matchAll(/<line\b[^>]*>/g)].map((found) => found[0]);
  if (strokes.length !== payload.stella.lines) {
    fail(`the wireframe drew ${strokes.length} strokes; the engine has ${payload.stella.lines} `
      + `lines — every stroke in this drawing has to be one of them`);
  }
  const lines = strokes.map((stroke) => {
    const edge = /data-edge="([^"]+)"/.exec(stroke);
    const at = /x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/.exec(stroke);
    if (!edge || !at) {
      fail(`the wireframe drew a stroke that does not say which edge it is: ${stroke}`);
      return null;
    }
    return [stroke, edge[1], at[1], at[2], at[3], at[4]];
  }).filter((line) => line !== null);
  const census = new Set(wire.edges.map(([a, b]) =>
    [wire.names[a], wire.names[b]].sort().join("|")));
  const drawnKeys = new Set();
  for (const line of lines) {
    const claimed = line[1].split("|").sort().join("|");
    const from = nearestDot(Number(line[2]), Number(line[3]));
    const to = nearestDot(Number(line[4]), Number(line[5]));
    // A stroke must actually start and end on a dot, not merely near one: half a dot's radius is
    // the whole tolerance, so a line stopping short of where it claims to go fails here.
    if (from.distance > 4 || to.distance > 4) {
      fail(`the wireframe's segment ${line[1]} does not end on a dot `
        + `(${from.distance.toFixed(1)}, ${to.distance.toFixed(1)} away)`);
      continue;
    }
    const geometric = [from.dot.name, to.dot.name].sort().join("|");
    if (geometric !== claimed) {
      fail(`the wireframe says it drew ${line[1]} and drew ${geometric}`);
    }
    if (!census.has(geometric)) {
      fail(`the wireframe drew ${geometric}, which is not an edge of the census`);
    }
    drawnKeys.add(geometric);
  }
  for (const key of census) {
    if (!drawnKeys.has(key)) {
      fail(`the census has the edge ${key}, and the wireframe did not draw it`);
    }
  }
}

// ── 9 · the numbers DEMOS.md quotes about the sweep ───────────────────────────────────────────────
//
// This is the paragraph that has been wrong three rounds running: the crossings count of the
// wireframe's opening view and what the sweep around it looks like. It is the only quantitative
// prose in this lane that no gate held, and prose no gate holds is prose that drifts. So every
// figure it is allowed to quote is asserted here, and the rule in DEMOS.md is the other half of the
// arrangement: **the paragraph quotes only numbers this gate asserts, and any other figure is
// deleted rather than corrected.**
//
// The sweep asserted is the 72×72 one the shipped code actually runs — the one that chooses the view
// a reader opens on — not a finer one quoted for effect.

const SWEEP = {
  directions: 5184,       // VIEW_GRID squared
  floor: 20,              // the lowest score any direction reaches
  atFloor: 200,           // how many reach it
  shape: "20/0/0",        // and every one of them has this shape: crossings / dots-on-lines / lost
  noCrossings: 12,        // directions with no crossings at all
  lostThere: 6,           // every one of which loses this many of the thirty-six edges
  touchingDownAnAxis: 228,
  touchingAtTheOpeningView: 48,
};

{
  const { points, edges } = draw.wireframe();
  if (VIEW_GRID * VIEW_GRID !== SWEEP.directions) {
    fail(`the sweep is ${VIEW_GRID}×${VIEW_GRID} and DEMOS.md quotes ${SWEEP.directions} directions`);
  }
  let floor = Infinity;
  let atFloor = 0;
  const shapes = new Set();
  let noCrossings = 0;
  const lostThere = new Set();
  for (let a = 0; a < VIEW_GRID; a += 1) {
    for (let b = 0; b < VIEW_GRID; b += 1) {
      const yaw = (a / VIEW_GRID) * Math.PI * 2;
      const pitch = (b / VIEW_GRID) * Math.PI - Math.PI / 2;
      const cost = viewCost(points, edges, yaw, pitch);
      if (cost.lies < floor) { floor = cost.lies; atFloor = 0; shapes.clear(); }
      if (cost.lies === floor) {
        atFloor += 1;
        shapes.add(`${cost.invented}/${cost.hidden}/${cost.flattened}`);
      }
      if (cost.invented === 0) { noCrossings += 1; lostThere.add(cost.flattened); }
    }
  }
  if (floor !== SWEEP.floor) fail(`the sweep's score floor is ${floor}, and DEMOS.md says ${SWEEP.floor}`);
  if (atFloor !== SWEEP.atFloor) {
    fail(`${atFloor} directions reach the floor, and DEMOS.md says ${SWEEP.atFloor}`);
  }
  if (shapes.size !== 1 || !shapes.has(SWEEP.shape)) {
    fail(`the cheapest views are ${[...shapes]}, and DEMOS.md says every one is ${SWEEP.shape}`);
  }
  if (noCrossings !== SWEEP.noCrossings) {
    fail(`${noCrossings} directions have no crossings, and DEMOS.md says ${SWEEP.noCrossings}`);
  }
  if (lostThere.size !== 1 || !lostThere.has(SWEEP.lostThere)) {
    fail(`the crossing-free views lose ${[...lostThere]} edges, and DEMOS.md says ${SWEEP.lostThere}`);
  }

  // And the touching pairs, which is the figure that tells a degenerate view from a usable one. It
  // is asserted at a spread of tolerances, because the whole point of quoting it is that it does
  // NOT move with the tolerance — unlike a degenerate view's crossing count, which does.
  const touching = (yaw, pitch, epsilon) => {
    const flat = points.map((point) => project3d(point, yaw, pitch));
    const spread = Math.max(...flat.map(([x]) => x)) - Math.min(...flat.map(([x]) => x)) || 1;
    const side = (p, q, r) => {
      const area = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
      return Math.abs(area) / (spread * spread) < epsilon ? 0 : Math.sign(area);
    };
    let met = 0;
    for (let i = 0; i < edges.length; i += 1) {
      for (let j = i + 1; j < edges.length; j += 1) {
        const [a, b] = edges[i];
        const [c, d] = edges[j];
        if (a === c || a === d || b === c || b === d) continue;
        const turns = [side(flat[a], flat[b], flat[c]), side(flat[a], flat[b], flat[d]),
          side(flat[c], flat[d], flat[a]), side(flat[c], flat[d], flat[b])];
        if (turns.some((turn) => turn === 0)) met += 1;
      }
    }
    return met;
  };
  const opening = draw.wireDefaultView();
  for (const epsilon of [1e-12, 1e-9, 1e-6, 1e-4]) {
    const axis = touching(0, 0, epsilon);
    const best = touching(opening.yaw, opening.pitch, epsilon);
    if (axis !== SWEEP.touchingDownAnAxis) {
      fail(`down an axis ${axis} pairs of lines touch at tolerance ${epsilon}, and DEMOS.md says `
        + `${SWEEP.touchingDownAnAxis}`);
    }
    if (best !== SWEEP.touchingAtTheOpeningView) {
      fail(`at the opening view ${best} pairs touch at tolerance ${epsilon}, and DEMOS.md says `
        + `${SWEEP.touchingAtTheOpeningView}`);
    }
  }
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

/**
 * A drawing's own sentences — its `<title>` and its `<desc>` — carry **no digit at all**.
 *
 * The `<desc>` is the whole of what a screen-reader user is given for a picture, so it is prose, and
 * prose about this object counts in words: *thirty-six lines*, not *36 lines*. That makes the rule
 * checkable, and it closes the one hole an attack found: "an orthographic wireframe of 3 tetrahedra"
 * slipped through the numeric scan, because three is a number the engine does produce — somewhere
 * else, about something else. Every actual value belongs in a `<text>` element or in a table, where
 * the scan can hold it to the engine.
 */
function sentencesOf(svg) {
  return [...svg.matchAll(/<(title|desc)[^>]*>([\s\S]*?)<\/\1>/g)].map((found) => found[2]);
}

const wordsOf = (text) => text.split(/\s+/).filter((word) => /[a-z]/i.test(word)).length;

/**
 * One printed cell as an exact fraction, or null when the cell is not a number at all.
 *
 * It reads what a **reader** sees — the engine's own printing, decimals and all — rather than the
 * value behind it. That is the point of gate 7: this is the arithmetic she would do with a pencil,
 * done the way she would have to do it, on the digits actually on the page.
 */
function exact(cell) {
  const text = String(cell).trim().replace(/[−–]/g, "-").replace(/^\+/, "");
  let found = /^(-?\d+)\/(\d+)$/.exec(text);
  if (found) return [BigInt(found[1]), BigInt(found[2])];
  found = /^(-?)(\d+)\.(\d+)$/.exec(text);
  if (found) {
    const bottom = 10n ** BigInt(found[3].length);
    const top = BigInt(found[2]) * bottom + BigInt(found[3]);
    return [found[1] ? -top : top, bottom];
  }
  return /^-?\d+$/.test(text) ? [BigInt(text), 1n] : null;
}

const report = [];
let sums = 0;
let stills = 0;
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
      for (const sentence of sentencesOf(rendered.drawing)) {
        if (/\d/.test(sentence)) {
          fail(`${slug} ${step.label}: the drawing's own words carry a digit — "${sentence}". A `
            + `title and a description are prose, and prose about this object counts in words; `
            + `every value goes in the drawing's text or in a table, where it is held to the engine`);
        }
      }
      // Gate 7: a table says what its numbers mean, and if it says "total" the total is right.
      //
      // Keyed on the table's **declaration**, not on its headings. The first version read the
      // column headed "added up", and a proof-reader turned it off by renaming that column to "the
      // total" in the same edit that broke the arithmetic under it — and turned it off again by
      // moving the terms into a separate table. So now: any row carrying three or more numbers must
      // be declared, one way or the other, and a heading that reads like a total must sit on the
      // declared column. A table cannot go quiet by being edited; it can only go quiet by having
      // its declaration deleted, which is a line a reviewer sees removed.
      for (const table of rendered.tables) {
        const shape = table.shape || null;
        const numericRun = (row) => row.slice(1).filter((cell) => exact(cell) !== null).length;
        const carriesNumbers = table.rows.some((row) => numericRun(row) >= 3);
        if (carriesNumbers && shape === null) {
          fail(`${slug} ${step.label}: "${table.caption}" puts three or more numbers in a row and `
            + `does not say whether the last is their total. Declare { total: i } or `
            + `{ notASum: true }`);
          continue;
        }
        // A heading that reads like a total has to BE the declared total — but only when there are
        // at least two printed numbers beside it for it to be the total of. A lone reported figure
        // ("the total, at this tick", over numbers the table does not print) is not a sum this check
        // could do, and demanding a declaration for it would teach the habit of declaring things
        // that are not true.
        // Per **column** as well as per row. A proof-reader got the original defect past the row
        // version by spreading the four terms one to a row — so no row held three numbers — and
        // leaving the total on its own row under an "added up" heading. Two or more numbers down a
        // column under a total-shaped heading is the same claim standing up instead of lying down.
        const looksLikeTotal = table.head.findIndex((head, index) => {
          if (index < 1) return false;
          if (!/\b(added up|the whole way round|total|altogether|sum|comes to)\b/i
            .test(String(head))) return false;
          const acrossARow = table.rows.some((row) => {
            const packed = String(row[index - 1]).trim().split(/\s+/);
            const before = packed.length > 1 && packed.every((term) => exact(term) !== null)
              ? packed.length
              : row.slice(1, index).filter((cell) => exact(cell) !== null).length;
            return before >= 2;
          });
          // The column BEFORE the total is where terms stood up in a column live; counting the
          // total's own column instead found one number (the total) and never fired. A proof-reader
          // walked the original defect past exactly that: one term per row, so no row held three
          // numbers, and the total alone under an "added up" heading.
          const downTheColumn = table.rows
            .filter((row) => exact(row[index - 1]) !== null).length >= 2;
          return acrossARow || downTheColumn;
        });
        if (looksLikeTotal >= 0 && (!shape || shape.total !== looksLikeTotal)) {
          fail(`${slug} ${step.label}: "${table.caption}" has a column headed `
            + `"${table.head[looksLikeTotal]}", which reads as a total, and the table does not `
            + `declare it as one`);
        }
        if (!shape || shape.total === undefined) continue;
        const at = shape.total;
        for (const row of table.rows) {
          const total = exact(row[at]);
          if (total === null) continue;
          const packed = String(row[at - 1]).trim().split(/\s+/);
          const terms = packed.length > 1 && packed.every((term) => exact(term) !== null)
            ? packed.map(exact)
            : row.slice(1, at).map(exact).filter((term) => term !== null);
          if (terms.length < 2) continue;
          sums += 1;
          let running = [0n, 1n];
          for (const [top, bottom] of terms) {
            running = [running[0] * bottom + top * running[1], running[1] * bottom];
          }
          if (running[0] * total[1] !== total[0] * running[1]) {
            fail(`${slug} ${step.label}: "${table.caption}" prints ${terms.length} numbers and says `
              + `they come to ${row[at]}, and they do not — the row is ${row.join(" · ")}`);
          }
        }
      }

      // Gate 8: nothing in the drawing is struck through. Read off the emitted SVG.
      {
        const svg = rendered.drawing;
        const strokes = [...svg.matchAll(
          /<line[^>]*x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/g)]
          .map((found) => [[+found[1], +found[2]], [+found[3], +found[4]]]);
        const marks = [...svg.matchAll(/<circle[^>]*cx="([-\d.]+)" cy="([-\d.]+)"/g)]
          .map((found) => [+found[1], +found[2]]);
        const boxes = [];
        for (const found of svg.matchAll(/<text([^>]*)>([^<]*)<\/text>/g)) {
          const at = /x="([-\d.]+)" y="([-\d.]+)"/.exec(found[1]);
          const size = /font-size="([\d.]+)"/.exec(found[1]);
          if (!at || !size || !found[2].trim()) continue;
          const box = textBox(+at[1], +at[2], found[2], +size[1]);
          if (strokes.some(([a, b]) => boxMeetsSegment(box, a, b))) {
            fail(`${slug} ${step.label}: the label "${found[2]}" is drawn across a stroke`);
          }
          if (marks.some(([x, y]) => x >= box.x0 && x <= box.x1 && y >= box.y0 && y <= box.y1)) {
            fail(`${slug} ${step.label}: the label "${found[2]}" is drawn on top of a dot`);
          }
          boxes.push({ ...box, text: found[2] });
        }

        // And against **each other**, which is the half this gate did not have. A proof-reader found
        // "0" and "−1" rendering as the single token "0−1" on chapter 2's net, twice: the numbers
        // were dodging every stroke and landing on the names, because the names were never in the
        // placement's record of what it had already put down. Two numbers touching is the
        // wrong-noun defect in visual form — a reader cannot tell which belongs to which name — so
        // no two labels may overlap at all, a name and its own number included. They have to read
        // as two things.
        for (let i = 0; i < boxes.length; i += 1) {
          for (let j = i + 1; j < boxes.length; j += 1) {
            const a = boxes[i];
            const b = boxes[j];
            // The same gap the placement keeps, imported rather than chosen here, so the two cannot
            // drift apart. Merely not intersecting is not enough: a drawing whose closest pair had
            // four tenths of a pixel between them passed the first version of this test, and four
            // tenths of a pixel on a screen is two numbers touching.
            if (boxesOverlap(a, b, LABEL_GAP)) {
              fail(`${slug} ${step.label}: the labels "${a.text}" and "${b.text}" are within `
                + `${LABEL_GAP}px of each other — on the page they read as one token, and a reader `
                + `cannot tell which is which`);
            }
          }
        }
      }

      // Gate 10: the still of this exact state.
      const still = stillFrom(rendered.drawing, {
        chapter: slug, beat: step.beats.join("–"), title: `${chapter.title} — ${step.label}`,
      });
      for (const [pattern, what] of [
        [/^<!-- Our Bubble demo still/, "the comment naming the beat it came from"],
        [/nothing in it is a claim about nature/, "the firewall line"],
        [/<svg[^>]*>\n  <style>/, "its own stylesheet, inlined"],
        [/<title>[^<]+<\/title>/, "a title"],
        [/<desc>[^<]+<\/desc>/, "a description"],
      ]) {
        if (!pattern.test(still)) {
          fail(`${slug} ${step.label}: the still has no ${what} — a still has to stand on its own, `
            + `because it is meant to end up in a chapter`);
        }
      }
      stills += 1;

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
    "theme", "light", "dark", "straighten it", "undo"]) {
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
  + `${payload.stella.lines} strokes the census's, ${sums} printed sums that add up, `
  + `${stills} stills standing on their own, at most ${totalWords} words on a page\n`,
);
