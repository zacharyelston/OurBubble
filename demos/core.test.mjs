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
//      paragraph quotes *only* numbers this gate asserts — and a figure of its own found wrong is
//      deleted rather than corrected, which is how two of them left it.
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

// `LABEL_GAP` is imported from `draw.mjs` rather than chosen here, so that the placement and the
// check cannot drift apart — but importing it means one edit to that constant would relax the
// placement AND the check that enforces it, in the same line. A reader spotted that. So the check
// keeps a floor of its own: the shared constant may be raised, never lowered.
const GAP_FLOOR = 3;
if (LABEL_GAP < GAP_FLOOR) {
  fail(`draw.mjs sets LABEL_GAP to ${LABEL_GAP}, and this check will not go below ${GAP_FLOOR}: `
    + `two labels that close read as one token, which is the whole reason the gap exists`);
}

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

}

// ── 4 · every drawing is its own census ───────────────────────────────────────────────────────────

/**
 * What each kind of drawing may emit, and what every mark in it must be.
 *
 * Built from the engine's own data, once, and consulted for every drawing of every step. The names
 * are the engine's: the tetrahedron's four dots and six lines, the six middles and the twelve lines
 * between them, the threaded pair's fourteen and thirty-six.
 */
const DRAWINGS = (() => {
  const P = payload;
  const NAMES = P.tetrahedron.names;
  const MID = P.cut.mid_names;
  const tetraLines = new Set(P.tetrahedron.line_names);
  const midLines = new Set(P.cut.mid_lines
    .map(([i, j]) => [MID[i], MID[j]].sort().join("|")));
  const absences = new Set(P.cut.opposite_pairs.map((pair) => [...pair].sort().join("|")));
  const tipNames = new Set(draw.tipNames());
  const stellaNames = new Set(P.stella.names);
  const stellaEdges = new Set(P.stella.edges
    .map(([i, j]) => [P.stella.names[i], P.stella.names[j]].sort().join("|")));
  const two = (attribute) => (value) => [...String(value).split("|")].sort().join("|");
  void two;
  return {
    net: {
      tags: ["svg", "title", "desc", "g", "polygon", "line", "circle", "text"],
      line: (value) => tetraLines.has(value),
      middle: (value) => tetraLines.has(value),
      dot: (value) => NAMES.includes(value),
    },
    ring: {
      tags: ["svg", "title", "desc", "g", "polygon", "line", "circle", "text"],
      line: (value) => midLines.has(value.split("|").sort().join("|")),
      absent: (value) => absences.has(value.split("|").sort().join("|")),
      "tip-line": (value) => {
        const [tip, middle] = value.split("|");
        return tipNames.has(tip) && MID.includes(middle);
      },
      dot: (value) => MID.includes(value) || tipNames.has(value),
    },
    wire: {
      tags: ["svg", "title", "desc", "g", "line", "circle", "text"],
      edge: (value) => stellaEdges.has(value.split("|").sort().join("|")),
      dot: (value) => stellaNames.has(value),
    },
  };
})();

/** Hold one emitted drawing to its kind: its elements, and the identity of every mark in it. */
function censusOf(svg, where) {
  const kind = (/class="(net|ring|wire)"/.exec(svg) || [])[1];
  if (!kind) {
    fail(`${where}: the drawing does not say which convention it is drawn in`);
    return;
  }
  const rules = DRAWINGS[kind];

  for (const found of svg.matchAll(/<([a-zA-Z][\w-]*)/g)) {
    if (!rules.tags.includes(found[1])) {
      fail(`${where}: the ${kind} drawing emitted a <${found[1]}>, and it may only emit `
        + `${rules.tags.join(", ")} — every mark in it has to be a piece of the object`);
    }
  }

  // Every stroke and every dot names itself, and what it names is the engine's.
  for (const [element, plural] of [["line", "stroke"], ["circle", "dot"]]) {
    for (const found of svg.matchAll(new RegExp(`<${element}\\b[^>]*>`, "g"))) {
      const mark = found[0];
      const named = [...mark.matchAll(/data-([\w-]+)="([^"]*)"/g)]
        .filter(([, , ], index) => true)
        .map((m) => [m[1], m[2]])
        .filter(([attribute]) => attribute in rules);
      if (!named.length) {
        fail(`${where}: the ${kind} drawing emitted a ${plural} that does not say what it is: `
          + `${mark}`);
        continue;
      }
      for (const [attribute, value] of named) {
        if (!rules[attribute](value)) {
          fail(`${where}: the ${kind} drawing's ${plural} claims to be the ${attribute} `
            + `"${value}", which the engine's census has not got`);
        }
      }
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
      // Gate 7: a table says what its numbers mean, and a total is a total.
      //
      // Three versions of this gate have been walked past, each by a narrower trick than the last:
      // reading the column *headed* "added up" (renaming it silenced it); counting numbers across a
      // row (one term per row silenced it); counting numbers down the total's own column (which
      // holds one number, the total). What defeats all three is to stop looking for a shape and
      // insist the table **say** what it is — by column index, which no caption edit reaches.
      //
      // Two things this version adds, both from a reader's findings. A **packed** cell — several
      // numbers in one string, "+3  +1  −4" — counts as its numbers, wherever it sits, so moving
      // terms into one cell escapes nothing. And **every** column is considered, including the
      // first, because a total was found sitting in column 0 where the old scan began at 1.
      for (const table of rendered.tables) {
        const shape = table.shape || null;
        const numbersIn = (cell) => {
          const packed = String(cell).trim().split(/\s+/).filter((part) => part !== "");
          const parsed = packed.map(exact);
          return parsed.every((value) => value !== null) && parsed.length > 0 ? parsed : [];
        };
        const rowNumbers = (row) => row.flatMap((cell) => numbersIn(cell));
        const carriesNumbers = table.rows.some((row) => rowNumbers(row).length >= 3);
        if (carriesNumbers && shape === null) {
          fail(`${slug} ${step.label}: "${table.caption}" puts three or more numbers in a row and `
            + `does not say whether the last is their total. Declare { total: i } or `
            + `{ notASum: true }`);
          continue;
        }

        // A heading that reads like a total must BE the declared total — checked over every column,
        // with packed cells counted as their numbers, and with a total in the first column refused
        // outright because it has no terms in front of it to be the total of.
        const totalish = (head) =>
          /\b(added up|the whole way round|total|altogether|sum|comes to)\b/i.test(String(head));
        table.head.forEach((head, index) => {
          if (!totalish(head)) return;
          if (index === 0) {
            fail(`${slug} ${step.label}: "${table.caption}" puts a column headed "${head}" first, `
              + `where nothing precedes it. A total goes after the numbers it is the total of`);
            return;
          }
          const before = table.rows.some((row) =>
            row.slice(0, index).some((cell) => numbersIn(cell).length >= 2));
          const down = table.rows
            .filter((row) => row.slice(0, index).some((cell) => numbersIn(cell).length >= 1))
            .length >= 2;
          if (!(before || down)) return;
          if (!shape || shape.total !== index) {
            fail(`${slug} ${step.label}: "${table.caption}" has a column headed "${head}", which `
              + `reads as a total of the numbers beside it, and the table does not declare it as one`);
          }
        });

        if (!shape || shape.total === undefined) continue;
        const at = shape.total;
        if (at === 0) {
          fail(`${slug} ${step.label}: "${table.caption}" declares column 0 as its total, and a `
            + `total goes after the numbers it is the total of`);
          continue;
        }
        for (const row of table.rows) {
          const total = exact(row[at]);
          if (total === null) continue;
          // The terms. **Any** cell before the total that holds several numbers is a packed terms
          // cell, wherever it sits — the nearest such cell to the total wins — and column 0 is
          // included, because a reader put the terms there with a note in between and the first
          // version of this scan, which looked only at the cell immediately before, saw nothing.
          // Failing that, the cells between the row's own label and the total, which is where an
          // ordinary run table keeps them; column 0 is excluded from *that* case because there it
          // holds the row's label — a tick number, not a term.
          const packedAt = row.slice(0, at)
            .map((cell, index) => ({ index, numbers: numbersIn(cell) }))
            .filter((cell) => cell.numbers.length > 1)
            .pop();
          const terms = packedAt
            ? packedAt.numbers
            : row.slice(1, at).flatMap((cell) => numbersIn(cell));
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

      // Gate 4, for EVERY drawing. It used to hold the wireframe alone — the drawing a reader was
      // invited to count off — and left the other three to be trusted, which is the same mistake in
      // a different place: the triangle, the net and the ring all put strokes and dots on paper that
      // are supposed to be the object's and nothing else.
      //
      // So every drawing declares its own kind, every mark in it says what it is, and both are held
      // to the engine: an element the drawing may not emit, a stroke that names nothing, or a stroke
      // naming something the engine's census has not got, all fail. What each kind is allowed is
      // `DRAWINGS` below.
      censusOf(rendered.drawing, `${slug} ${step.label}`);

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
