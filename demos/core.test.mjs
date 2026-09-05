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
// The gates, in the order of what they would catch — numbered for reference, not counted here,
// because a count of them is one more figure to go stale, and this one already had:

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
//      every marked section is covered, and the beat ids and questions are `steps.json`'s. A beat's
//      id is its own chapter's — `make-it-move.3` — and a step is labelled by its place on this
//      page, "step 3 of 9", so no number a reader meets here counts anything outside her page.
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
const { drawings, viewCost, VIEW_GRID, textBox, boxMeetsSegment, boxesOverlap,
  boxMeetsDot, LABEL_GAP, DOT_CLEARANCE } = await import(
  pathToFileURL(path.join(HERE, "draw.mjs")).href);
const { chapterSteps } = await import(pathToFileURL(path.join(HERE, "steps.mjs")).href);
const { joinSteps, statesOf, stillFrom, SVG_STILL_STYLE_TEXT } = await import(
  pathToFileURL(path.join(HERE, "core.mjs")).href);

// ── which of this file's own fail sites a run reached ─────────────────────────────────────────────
//
// A guard nothing has ever made fire is a guard nobody has tested, and counting the mutations in
// `attacks.mjs` does not say how many guards they cover: every place in this file that can
// complain is one of them, the census below counts them rather than this comment, and
// the first census of what the suite actually reached found about a third of them. Two of the three
// most important — a label drawn across a stroke, a label on a dot's ink — were among the rest.
//
// So every `fail(` site here is enumerated from this file's own source, every call records the site
// it came from, and with `DEMO_FAIL_SITES` set the run prints which ones it reached. `attacks.mjs`
// unions that over every mutation and compares it against a committed baseline, so coverage
// shrinking is a failure rather than a thing somebody notices.
const failures = [];

/** Every line of this file that can complain, keyed by the line's own text rather than its number. */
function failSites(source) {
  const sites = new Map();
  const seen = new Map();
  source.split("\n").forEach((text, index) => {
    const bare = text.trim();
    if (bare.startsWith("//") || bare.startsWith("*") || bare.startsWith("/*")) return;
    if (/const fail = /.test(text)) return;                      // the definition, not a site
    if (!/(^|[^\w.])fail\(/.test(text)) return;
    const key = bare.replace(/\s+/g, " ");
    const before = seen.get(key) || 0;
    seen.set(key, before + 1);
    sites.set(index + 1, before ? `${key} #${before + 1}` : key);
  });
  return sites;
}

const FAIL_SITES = failSites(readFileSync(path.join(HERE, "core.test.mjs"), "utf8"));
const REACHED = new Set();

const fail = (message) => {
  // The caller's line, off the stack: frame 0 is the `Error` header, frame 1 is this function.
  const frame = (new Error().stack || "").split("\n")[2] || "";
  const at = /core\.test\.mjs:(\d+):\d+/.exec(frame);
  REACHED.add(at ? Number(at[1]) : 0);
  failures.push(message);
};

/**
 * What this run reached, for `attacks.mjs` to union — printed only when it asks.
 *
 * `DEMO_FAIL_SITES=all` also prints the whole census, which is how the suite learns the names of
 * the sites nothing reached without reimplementing the enumeration above. One enumeration, one
 * file: two copies of it would drift, and a coverage census that has drifted is worse than none.
 */
function printFailSites() {
  if (!process.env.DEMO_FAIL_SITES) return;
  process.stdout.write(`core.test.mjs: fail-site-census ${FAIL_SITES.size}\n`);
  if (process.env.DEMO_FAIL_SITES === "all") {
    for (const key of FAIL_SITES.values()) {
      process.stdout.write(`core.test.mjs: fail-site-known ${key}\n`);
    }
  }
  for (const line of [...REACHED].sort((a, b) => a - b)) {
    const key = FAIL_SITES.get(line);
    process.stdout.write(`core.test.mjs: fail-site ${key || `UNKNOWN SITE at line ${line}`}\n`);
  }
}

// `LABEL_GAP` is imported from `draw.mjs` rather than chosen here, so that the placement and the
// check cannot drift apart — but importing it means one edit to that constant would relax the
// placement AND the check that enforces it, in the same line. A reader spotted that. So the check
// keeps a floor of its own: the shared constant may be raised, never lowered.
const GAP_FLOOR = 3;
if (LABEL_GAP < GAP_FLOOR) {
  fail(`draw.mjs sets LABEL_GAP to ${LABEL_GAP}, and this check will not go below ${GAP_FLOOR}: `
    + `two labels that close read as one token, which is the whole reason the gap exists`);
}
// And the same for the clearance a label keeps from the dot it names. A reader pointed out that a
// constant only the placement consults is a standard nothing enforces: dropping it to nothing made
// no visible overlap, because the ink test catches those — but it would have let a name sit against
// its mark again the moment that test moved.
const CLEARANCE_FLOOR = 12;
if (DOT_CLEARANCE < CLEARANCE_FLOOR) {
  fail(`draw.mjs sets DOT_CLEARANCE to ${DOT_CLEARANCE}, and this check will not go below `
    + `${CLEARANCE_FLOOR}: the biggest dot these drawings put down has a radius of thirteen, and a `
    + `name that starts inside it reads as attached to the mark rather than beside it`);
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
  // A title, because the drawings no longer supply a default one — and this check was the caller
  // that had been leaning on it. The fallback strings were unreachable from any step, and an attack
  // on one of them "escaped" the whole suite until it was shown to be code nothing renders; dead
  // code that looks like a safety net is a place a wrong number can sit unexamined, so it is gone
  // and the drawings now refuse to draw without a title.
  const drawn = draw.drawWire({
    yaw: view.yaw, pitch: view.pitch, title: "The threaded pair, for the census check",
  });

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
  // Every stroke, labelled or not — except a leader, which is a pointer at the object rather than a
  // piece of it, and is counted and checked separately by the census gate.
  const strokes = [...drawn.matchAll(/<line\b[^>]*>/g)].map((found) => found[0])
    .filter((mark) => !/data-leader=/.test(mark));
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
    // A drawing with no dots at all has nothing to resolve an end to, and that is reported by the
    // dot census above and by the drawing's own census — not by this loop crashing, which is what
    // it did when a mutation stopped the wireframe drawing dots.
    if (!from || !to) continue;
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
  grid: 72,               // directions swept in each of the two angles
  directions: 5184,       // VIEW_GRID squared
  floor: 20,              // the lowest score any direction reaches
  atFloor: 200,           // how many reach it
  shape: "20/0/0",        // and every one of them has this shape: crossings / dots-on-lines / lost
  noCrossings: 12,        // directions with no crossings at all
  lostThere: 6,           // every one of which loses this many of the thirty-six edges
  // And the opening view itself, which the paragraph quotes and nothing checked: a reader falsified
  // the yaw, the pitch, the degree conversions and the view's own 20/0/0 and every gate stayed
  // green, because the window started after the blockquote they sit in.
  yaw: "5.585",
  pitch: "−0.654",
  yawDegrees: 320,
  pitchDegrees: "−37.5",
  openingCrossings: 20,
  openingHidden: 0,
  openingLost: 0,
};

// ── the two facts the wireframe's mirror-and-flip verdict rests on ────────────────────────────────
//
// The position census below exempts a **mirrored** wireframe and refuses a **flipped** one, and for
// three rounds this file gave the wrong reason for the first: that the threaded pair is centrally
// symmetric, so every point has its negative in the set. That is true of this object and it is not
// the reason. Mirroring the horizontal of this projection is
//
//     M ∘ P(yaw, pitch) ≡ P(yaw + π, −pitch)
//
// which is an identity of the projection for **any** set of points whatever — central symmetry
// never enters it. A reader who spotted that also spotted what it means for the guard: the property
// the old check was watching was irrelevant to the verdict, so it was a tripwire on the wrong wire.
//
// The flip is refused for a reason of the same kind. Negating the vertical is P(yaw, pitch + π) —
// also a view of the same object, in the same sense — and it is caught for one reason only: the
// search that recovers a drawing's view sweeps pitch over **[−π/2, π/2)**, and pitch + π is not in
// it. That is a fact about the sweep, not about the object, so widening the sweep would quietly
// admit every flipped drawing. Both facts are now checked here.
const PITCH_FROM = -Math.PI / 2;
const PITCH_SPAN = Math.PI;
const sweptYaw = (a) => (a / VIEW_GRID) * Math.PI * 2;
const sweptPitch = (b) => PITCH_FROM + (b / VIEW_GRID) * PITCH_SPAN;

{
  if (PITCH_FROM !== -Math.PI / 2 || PITCH_SPAN !== Math.PI) {
    fail(`the view search sweeps pitch from ${PITCH_FROM} over a span of ${PITCH_SPAN}, and the `
      + `flip guard requires exactly [−π/2, π/2): a flipped drawing is the view at pitch + π, so a `
      + `sweep any wider than a half turn matches it and the FLIPPED verdict silently stops `
      + `happening`);
  }
  // And the mirror identity itself, at an arbitrary view — checked rather than argued, because it
  // is the whole justification for letting a mirrored wireframe pass.
  const yaw = 1.1;
  const pitch = 0.37;
  const mirrored = payload.stella.points
    .map((point) => ownProject3d(point, yaw, pitch))
    .map(([x, y]) => [-x, y]);
  const elsewhere = payload.stella.points
    .map((point) => ownProject3d(point, yaw + Math.PI, -pitch));
  const worst = Math.max(...mirrored.map((one, index) =>
    Math.hypot(one[0] - elsewhere[index][0], one[1] - elsewhere[index][1])));
  if (worst > 1e-9) {
    fail(`mirroring a view's horizontal is supposed to BE the view at yaw + π and −pitch, and it `
      + `comes out ${worst.toExponential(2)} away. The position census lets a mirrored wireframe `
      + `pass on the strength of that identity, so if it does not hold the exemption is unearned`);
  }
}

{
  const { points, edges } = draw.wireframe();
  if (VIEW_GRID !== SWEEP.grid) {
    fail(`the sweep is ${VIEW_GRID} directions per angle and DEMOS.md says ${SWEEP.grid}`);
  }
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
      const yaw = sweptYaw(a);
      const pitch = sweptPitch(b);
      const cost = viewCost(points, edges, yaw, pitch);
      if (cost.lies < floor) { floor = cost.lies; atFloor = 0; shapes.clear(); }
      if (cost.lies === floor) {
        atFloor += 1;
        shapes.add(`${cost.invented}/${cost.hidden}/${cost.flattened}`);
      }
      if (cost.invented === 0) { noCrossings += 1; lostThere.add(cost.flattened); }
    }
  }
  // The opening view, from the same call the page makes.
  const opening = draw.wireDefaultView();
  const openingCost = viewCost(points, edges, opening.yaw, opening.pitch);
  const round3 = (value) => value.toFixed(3).replace("-", "−");
  const degrees = (value) => Math.round((value * 180) / Math.PI * 10) / 10;
  if (round3(opening.yaw) !== SWEEP.yaw) {
    fail(`the opening view's yaw is ${round3(opening.yaw)}, and DEMOS.md says ${SWEEP.yaw}`);
  }
  if (round3(opening.pitch) !== SWEEP.pitch) {
    fail(`the opening view's pitch is ${round3(opening.pitch)}, and DEMOS.md says ${SWEEP.pitch}`);
  }
  if (Math.round(degrees(opening.yaw)) !== SWEEP.yawDegrees) {
    fail(`the opening yaw is ${degrees(opening.yaw)}°, and DEMOS.md says ${SWEEP.yawDegrees}°`);
  }
  if (String(degrees(opening.pitch)).replace("-", "−") !== SWEEP.pitchDegrees) {
    fail(`the opening pitch is ${degrees(opening.pitch)}°, and DEMOS.md says ${SWEEP.pitchDegrees}°`);
  }
  for (const [what, got, said] of [
    ["crossings", openingCost.invented, SWEEP.openingCrossings],
    ["dots on lines", openingCost.hidden, SWEEP.openingHidden],
    ["lost edges", openingCost.flattened, SWEEP.openingLost],
  ]) {
    if (got !== said) {
      fail(`the opening view has ${got} ${what}, and DEMOS.md says ${said}`);
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

{
  // The other half of the paragraph's rule, which until now was kept by hand: not only must every
  // figure it quotes be one `SWEEP` asserts, but **nothing** in it may be a figure `SWEEP` does not
  // assert. Checked by reading the paragraph out of DEMOS.md and pulling every emphasised number.
  // This found a fifth wrong number the moment it was written — the sentence claiming how many
  // figures the paragraph had.
  const doc = readFileSync(path.join(HERE, "DEMOS.md"), "utf8");
  // From the paragraph's FIRST line — which is where the opening view's own figures sit, inside a
  // blockquote. The window used to start below it, so a reader falsified the yaw, the pitch, both
  // degree figures and the view's 20/0/0 and nothing noticed.
  const from = doc.indexOf("**The default view is chosen by counting.**");
  const to = doc.indexOf("That is the argument for leaving the plane");
  if (from < 0 || to < 0) {
    fail("DEMOS.md no longer has the crossings paragraph this gate is written against");
  } else {
    const asserted = new Set(Object.values(SWEEP).map((value) => String(value)));
    for (const value of Object.values(SWEEP)) {
      for (const part of String(value).split("/")) asserted.add(part);
    }
    // EVERY digit-run in the paragraph, not only the emphasised ones. A reader smuggled an
    // unbolded figure through the bold-spans-only version, and the rule was never about typography.
    // A few word-shapes are not figures about the sweep: a rule number, a heading's own count of
    // terms. Those are listed rather than pattern-matched, so adding one is a decision.
    // A handful of shapes in the window are not figures about the sweep: the three weights the
    // score is built from, which the sentence explains in words, and nothing else. Listed rather
    // than pattern-matched, so adding one is a decision somebody makes on purpose.
    const NOT_A_SWEEP_FIGURE = new Set(["1", "4", "12"]);
    const plain = (text) => text.replace(/[−–]/g, "-");
    // Thousands written with a space are one figure, so they are joined before scanning; otherwise
    // "5 184" reads as a 5 and a 184.
    const window = doc.slice(from, to).replace(/(\d)[\u202f\u00a0 ](\d{3})\b/g, "$1$2");
    const wanted = new Set([...asserted].map(plain));
    for (const found of window.matchAll(/[−-]?\d[\d.]*\d|[−-]?\d/g)) {
      const bare = plain(found[0]);
      if (wanted.has(bare) || wanted.has(bare.replace(/^-/, ""))) continue;
      if (NOT_A_SWEEP_FIGURE.has(bare)) continue;
      fail(`DEMOS.md's crossings paragraph contains the figure ${found[0]}, which SWEEP does not `
        + `assert. Its own rule: delete it, do not correct it`);
    }
  }
}

// ── 9b · DEMOS.md names no beat by a number it typed ──────────────────────────────────────────────
//
// The demos hold no beat numbers because a renumber would strand them — that is the whole reason
// `steps.json` is generated. **This file did not extend that discipline to its own prose**, and the
// preface's renumber proved it: every beat in the book moved by four, and nine hand-written "beat
// N" references in DEMOS.md went silently wrong while the pages themselves were fine.
//
// Four rules, and between them the family cannot come back. The page table's **counts** must be
// `steps.json`'s — how many beats a chapter has and how many steps its page walks them in — so they
// are checked rather than remembered. The ranges that column used to carry are gone with the
// book-wide numbering they were written in (issue #77). Every `slug.n` written anywhere in the file
// must be a beat `steps.json` carries, and the folded pairs it lists must be **the** folds, because
// the first version of that list was a hand-written list of numbers and went stale exactly as the
// prose did — a reviewer replaced one pair with a beat that does not exist and this file stayed
// green. And everywhere else a beat is named by **what it is** — the poke step, the walk step, the
// dial step — because a name does not need renumbering.
const tableSteps = new Map();
const docFolds = [];
{
  const doc = readFileSync(path.join(HERE, "DEMOS.md"), "utf8");
  // The rows the loop below actually checks, and nothing else, are what the prose scan skips. It
  // used to skip **any** line containing ".html", which is a much bigger hole than it looks: a
  // sentence naming a page and a beat in the same breath — the likeliest sentence to write — went
  // straight through. A reader found it by writing one.
  const tableRows = new Set();
  // The step counts the table states, read here and held to the steps themselves further down,
  // where the chapters are joined — this block has the scaffolding but not the step definitions.
  for (const [slug, chapter] of Object.entries(scaffold.chapters)) {
    const row = doc.split("\n").find((line) => line.includes(`${slug}.html`));
    if (row) tableRows.add(row);
    if (!row) {
      fail(`DEMOS.md has no page-table row for ${slug}`);
      continue;
    }
    const found = /\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*$/.exec(row);
    if (!found) {
      fail(`DEMOS.md's row for ${slug} states no beat count and step count`);
    } else if (Number(found[1]) !== chapter.beats) {
      fail(`DEMOS.md says ${slug} has ${found[1]} beats, and steps.json derives `
        + `${chapter.beats} from OUTLINE.md and the chapter's markers`);
    } else {
      tableSteps.set(slug, Number(found[2]));
    }
  }
  // The stale-number scan runs over the WHOLE text, with the page-table rows blanked out — not
  // line by line. `\s` matches a newline, so a sentence hard-wrapped between the word and its
  // number reads as a beat number to any reader and as nothing at all to a line-by-line scan; a
  // reviewer wrapped one and it went green (2026-09-04). The rows are blanked rather than skipped
  // so the line numbers still count.
  const lines = doc.split("\n");
  const scanned = lines.map((line) => (tableRows.has(line) ? "" : line)).join("\n");
  const lineOf = (offset) => scanned.slice(0, offset).split("\n").length;
  for (const found of scanned.matchAll(/\b[Bb]eats?\s+(?:\d+|N\b)/g)) {
    fail(`DEMOS.md:${lineOf(found.index)} writes "${found[0].replace(/\s+/g, " ")}" outside its `
      + `page table. A book-wide beat number is nobody's name any more — a beat is slug.n, like `
      + `make-it-move.3 — and in prose it goes stale the next time the chapter is renumbered. Name `
      + `the beat by what it is instead: the poke step, the walk step`);
  }

  // Every beat id the file writes down, resolved against steps.json — including the folded pairs,
  // which are collected here and compared against the steps themselves further down.
  for (const found of doc.matchAll(/(?<![\w-])([a-z][a-z0-9]*(?:-[a-z0-9]+)+)\.(\d+)(?:\+(\d+))?/g)) {
    const [, slug, first, second] = found;
    const chapter = scaffold.chapters[slug];
    if (!chapter) continue;              // not a demo chapter: nothing here to check it against
    for (const n of second === undefined ? [first] : [first, second]) {
      if (Number(n) < 1 || Number(n) > chapter.beats) {
        fail(`DEMOS.md names ${slug}.${n}, and steps.json says ${slug} has ${chapter.beats} beats`);
      }
    }
    if (second !== undefined) docFolds.push(`${slug}.${first}+${second}`);
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
  const key = (value) => String(value).split("|").sort().join("|");

  // How many times each of the net's dots appears on the paper, from the engine's own label list —
  // which is where "one dot in three places" is a fact rather than a remark.
  const netDotPlaces = {};
  for (const label of P.net.labels) {
    if (label.kind !== "dot") continue;
    netDotPlaces[label.text] = (netDotPlaces[label.text] || 0) + 1;
  }
  // And how many strokes carry each line's name, likewise.
  const netLinePlaces = {};
  for (const segment of P.net.segments) {
    netLinePlaces[segment.line] = (netLinePlaces[segment.line] || 0) + 1;
  }

  const tetraLines = new Set(P.tetrahedron.line_names);
  const triangleLines = new Set(P.tetrahedron.line_names
    .filter((name) => !name.includes(NAMES[3])));
  const midLines = new Set(P.cut.mid_lines.map(([i, j]) => key(`${MID[i]}|${MID[j]}`)));
  const absences = new Set(P.cut.opposite_pairs.map((pair) => key(pair.join("|"))));
  const tipNames = new Set(draw.tipNames());
  const stellaNames = new Set(P.stella.names);
  const stellaEdges = new Set(P.stella.edges
    .map(([i, j]) => key(`${P.stella.names[i]}|${P.stella.names[j]}`)));
  const faceNames = new Set(P.tetrahedron.face_names);
  const ringRegions = new Set(P.cut.mid_faces
    .map((face) => key(face.map((i) => MID[i]).join("|"))));

  // For each kind: what elements it may emit, what each `data-` identity has to be, how many marks
  // of each name it may put down, and — the part this was missing — how many separate PLACES a dot
  // of a given name is allowed to occupy.
  return {
    triangle: {
      tags: ["svg", "title", "desc", "g", "polygon", "line", "circle", "text"],
      identity: {
        leader: (value) => NAMES.slice(0, 3).includes(value),
        line: (value) => triangleLines.has(value),
        dot: (value) => NAMES.slice(0, 3).includes(value),
        region: (value) => faceNames.has(value),
        walk: (value) => triangleLines.has(value),
      },
      // Every line and dot it draws, it draws once; a dot sits in one place.
      places: () => 1,
      once: ["line", "dot", "leader"],
      // Whatever dots the step shows, each of its lines must end on two of them. A reader found the
      // triangle drawing NO dots at all and passing, because only the wireframe had a count.
      endsOnDots: true,
    },
    net: {
      tags: ["svg", "title", "desc", "g", "polygon", "line", "circle", "text"],
      identity: {
        leader: (value) => Object.keys(netDotPlaces).includes(value),
        line: (value) => tetraLines.has(value),
        middle: (value) => tetraLines.has(value),
        dot: () => false,          // the net draws no dots of its own
        region: (value) => faceNames.has(value),
      },
      places: (attribute, value) => (attribute === "dot"
        ? (netDotPlaces[value] || 0)
        : (netLinePlaces[value] || 0)),
      counted: { line: netLinePlaces, middle: netLinePlaces },
    },
    ring: {
      tags: ["svg", "title", "desc", "g", "polygon", "line", "circle", "text"],
      identity: {
        leader: (value) => MID.includes(value) || tipNames.has(value),
        line: (value) => midLines.has(key(value)),
        absent: (value) => absences.has(key(value)),
        "tip-line": (value) => {
          const [tip, middle] = value.split("|");
          return tipNames.has(tip) && MID.includes(middle);
        },
        dot: (value) => MID.includes(value) || tipNames.has(value),
        region: (value) => ringRegions.has(key(value)),
      },
      places: () => 1,
      once: ["line", "absent", "tip-line", "dot", "leader"],
      exactly: { line: midLines.size, dot: null },
      // The ring's six middles are always drawn, and a tip is drawn only with its own lines: a
      // reader found it drawing four of six dots, and drawing tip lines to a tip with no dot.
      dotsAtLeast: MID,
      tipsHaveDots: true,
    },
    wire: {
      tags: ["svg", "title", "desc", "g", "line", "circle", "text"],
      identity: {
        leader: (value) => stellaNames.has(value),
        edge: (value) => stellaEdges.has(key(value)),
        dot: (value) => stellaNames.has(value),
      },
      places: () => 1,
      once: ["edge", "dot", "leader"],
      exactly: { edge: stellaEdges.size, dot: stellaNames.size },
      endsOnDots: true,
    },
  };
})();

const NEARBY = 2;
const near = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]) <= NEARBY;

/**
 * The orthographic projection, **written here** rather than imported from `draw.mjs`.
 *
 * This is the one place in the check that reimplements something the drawing does, and it has to.
 * The first version asked `draw.mjs`'s own `project3d` where the dots belonged, so mirroring that
 * function moved the drawing and the expectation together and both of a reader's mirrors passed —
 * the same weakness the ring has, and the reason the ring is checked against its convention's
 * *words* instead. The wireframe has an independent definition available: yaw about the upright
 * axis, then pitch, the vertical up the page, which is the record's own render and what DEMOS.md
 * describes. So the check does that arithmetic itself, and a change to the drawing's projection is
 * a disagreement rather than a shared move.
 */
function ownProject3d(point, yaw, pitch) {
  const [x, y, z] = point.map((value) => {
    const [top, bottom] = String(value).split("/");
    return bottom === undefined ? Number(top) : Number(top) / Number(bottom);
  });
  const cy = Math.cos(yaw);
  const sy = Math.sin(yaw);
  const cp = Math.cos(pitch);
  const sp = Math.sin(pitch);
  return [cy * x - sy * z, -(sy * sp * x + cp * y + cy * sp * z)];
}

/**
 * Which view a wireframe was drawn at, recovered from the drawing itself.
 *
 * The wireframe turns, so its expected positions depend on where it is pointing — and the check may
 * not simply ask the drawing "what yaw did you use?", because a mirrored drawing would answer
 * honestly and still be mirrored. So the view is **searched for**: the yaw and pitch, over the same
 * fixed grid `bestView` uses, whose projection of the engine's own points best matches the dots
 * actually drawn. If the drawing is a mirror of some view, no view in the sweep matches it and the
 * scale test below is what says so.
 */
function wireViewOf(svg) {
  const drawn = [...svg.matchAll(
    /<circle[^>]*data-dot="([^"]+)"[^>]*cx="([-\d.]+)" cy="([-\d.]+)"/g)]
    .map((found) => ({ name: found[1], at: [+found[2], +found[3]] }));
  if (drawn.length < 3) return null;
  const names = payload.stella.names;
  const points = payload.stella.points;
  let best = null;
  for (let a = 0; a < VIEW_GRID; a += 1) {
    for (let b = 0; b < VIEW_GRID; b += 1) {
      const yaw = sweptYaw(a);
      const pitch = sweptPitch(b);
      const flat = points.map((point) => ownProject3d(point, yaw, pitch));
      // Compare shapes, not sizes: each set is centred and scaled to its own spread first, so a
      // resizing of the drawing is not mistaken for a distortion of it.
      const cost = shapeDistance(drawn, names, flat);
      if (best === null || cost < best.cost) best = { yaw, pitch, cost };
    }
  }
  return best;
}

/** Where the threaded pair's dots belong at one view, by this check's own arithmetic. */
function ownWireDots(view) {
  if (!view) return {};
  const out = {};
  payload.stella.names.forEach((name, index) => {
    out[name] = [ownProject3d(payload.stella.points[index], view.yaw, view.pitch)];
  });
  return out;
}

/** How far two point sets are from being the same shape, once centred and scaled. */
function shapeDistance(drawn, names, flat) {
  const mine = drawn.map((dot) => flat[names.indexOf(dot.name)]).filter(Boolean);
  if (mine.length !== drawn.length) return Infinity;
  const centre = (points) => points.reduce((sum, one) =>
    [sum[0] + one[0] / points.length, sum[1] + one[1] / points.length], [0, 0]);
  const spread = (points, mid) => Math.max(...points
    .map((one) => Math.hypot(one[0] - mid[0], one[1] - mid[1]))) || 1;
  const aMid = centre(drawn.map((dot) => dot.at));
  const bMid = centre(mine);
  const aSize = spread(drawn.map((dot) => dot.at), aMid);
  const bSize = spread(mine, bMid);
  let worst = 0;
  drawn.forEach((dot, index) => {
    const one = [(dot.at[0] - aMid[0]) / aSize, (dot.at[1] - aMid[1]) / aSize];
    const two = [(mine[index][0] - bMid[0]) / bSize, (mine[index][1] - bMid[1]) / bSize];
    worst = Math.max(worst, Math.hypot(one[0] - two[0], one[1] - two[1]));
  });
  return worst;
}

/**
 * Hold one emitted drawing to its kind — its elements, what every mark CLAIMS, and **where it is**.
 *
 * The geometry half is the one this gate was missing, and a proof-reader walked six mutations
 * through the gap: every stroke on the ring halved with its `data-line` left honest (a visibly
 * broken drawing, twelve strokes reaching none of the dots they name); the same on the net; a stray
 * stroke placed nowhere near the line it claimed, on each; a stroke drawn as a `<polygon>`, which
 * the whitelist allowed for the panels and the identity loop never looked at; and a second dot
 * called `D` at an arbitrary point, which passed because `D` legitimately appears three times.
 *
 * Identity alone is not a census. Three things are checked here, and the first two are new:
 *
 *   1. **Marks that name a dot in common, in the same panel, meet at a point.** That is what makes a
 *      halved stroke fail: its far end no longer coincides with the other strokes at that dot. It
 *      needs no external truth — the drawing is held to its own claims about itself.
 *   2. **A dot occupies as many places as the engine says.** One, everywhere, except on the flat net
 *      where `D` occupies exactly three, from the engine's own label list.
 *   3. **Every mark's identity is the engine's**, and every stroke-bearing element is looked at —
 *      `polygon` included, with its own region name and its own point count.
 */
function censusOf(svg, where) {
  const kind = (/data-drawing="([a-z]+)"/.exec(svg) || [])[1];
  if (!kind || !DRAWINGS[kind]) {
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

  // Every mark that can carry ink, with what it claims and where it is.
  const marks = [];
  for (const found of svg.matchAll(/<(line|circle|polygon)\b([^>]*)>/g)) {
    const [, element, attributes] = found;
    const named = [...attributes.matchAll(/data-([\w-]+)="([^"]*)"/g)]
      .map((m) => [m[1], m[2]])
      .filter(([attribute]) => attribute in rules.identity);
    let points = [];
    if (element === "line") {
      const at = /x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/.exec(attributes);
      if (at) points = [[+at[1], +at[2]], [+at[3], +at[4]]];
    } else if (element === "circle") {
      const at = /cx="([-\d.]+)" cy="([-\d.]+)"/.exec(attributes);
      if (at) points = [[+at[1], +at[2]]];
    } else {
      points = (/points="([^"]+)"/.exec(attributes)?.[1] || "").trim().split(/\s+/)
        .map((pair) => pair.split(",").map(Number))
        .filter(([x, y]) => Number.isFinite(x) && Number.isFinite(y));
    }
    if (!named.length) {
      fail(`${where}: the ${kind} drawing emitted a <${element}> that does not say what it is: `
        + `${found[0]}`);
      continue;
    }
    if (!points.length) {
      fail(`${where}: the ${kind} drawing emitted a <${element}> with no position`);
      continue;
    }
    if (element === "polygon" && points.length < 3 && !/data-walk=/.test(attributes)) {
      fail(`${where}: the ${kind} drawing emitted a <polygon> of ${points.length} point(s) — a `
        + `region has three, and a stroke is a <line>`);
    }
    const panel = /data-panel="([^"]*)"/.exec(attributes)?.[1] || "";
    for (const [attribute, value] of named) {
      if (!rules.identity[attribute](value)) {
        fail(`${where}: the ${kind} drawing's <${element}> claims to be the ${attribute} `
          + `"${value}", which the engine's census has not got`);
      }
    }
    marks.push({ element, named, points, panel, source: found[0] });
  }

  // ── 1 · marks naming a dot in common, in the same panel, meet at a point ────────────────────
  const dotsNamedBy = (mark) => mark.named.flatMap(([attribute, value]) => {
    if (attribute === "region") return [];
    if (attribute === "dot") return [value];
    if (attribute === "middle") return [];      // a middle is a point, not a pair of dots
    if (attribute === "walk") return [];        // an arrowhead sits ALONG a line, not at a dot
    if (attribute === "leader") return [value];  // a leader starts AT the dot it names
    return value.includes("|") ? value.split("|") : [...value];
  });
  const strokes = marks.filter((mark) => mark.element !== "polygon");
  for (let i = 0; i < strokes.length; i += 1) {
    for (let j = i + 1; j < strokes.length; j += 1) {
      const a = strokes[i];
      const b = strokes[j];
      if (a.panel !== b.panel) continue;
      const shared = dotsNamedBy(a).filter((name) => dotsNamedBy(b).includes(name));
      if (!shared.length) continue;
      const meets = a.points.some((one) => b.points.some((two) => near(one, two)));
      if (!meets) {
        fail(`${where}: the ${kind} drawing's ${a.source.slice(0, 60)}… and `
          + `${b.source.slice(0, 60)}… both name ${shared.join(", ")} and do not meet anywhere. `
          + `Two marks at the same dot are at the same point, or one of them is in the wrong place`);
      }
    }
  }

  // A region's corners are corners of the object, not points of their own. Without this, a polygon
  // of three arbitrary points with an honest `data-region` is a stroke — or a whole shape — that
  // nothing checks: a reader got a two-point one past the count test's ancestor, and a three-point
  // one past this gate's first draft. Every vertex has to be somewhere a stroke already ends.
  for (const region of marks.filter((mark) => mark.element === "polygon"
    && mark.named.some(([attribute]) => attribute === "region"))) {
    const ends = strokes.filter((mark) => mark.panel === region.panel || region.panel === "")
      .flatMap((mark) => mark.points);
    // A cut's medial triangle has its corners at the middles of the strokes, not at their ends.
    const middles = strokes.flatMap((mark) => (mark.points.length === 2
      ? [[(mark.points[0][0] + mark.points[1][0]) / 2, (mark.points[0][1] + mark.points[1][1]) / 2]]
      : []));
    const anchors = [...ends, ...middles];
    for (const corner of region.points) {
      if (!anchors.some((anchor) => near(anchor, corner))) {
        fail(`${where}: the ${kind} drawing's region "${region.named
          .find(([a]) => a === "region")[1]}" has a corner at `
          + `${corner.map((v) => v.toFixed(1)).join(",")}, where no stroke of the object ends`);
      }
    }
  }

  // An arrowhead is not at a dot, so the meeting test above passes over it — instead it has to sit
  // ON the line it says it marks. Without this a walk could point along a line it does not name.
  for (const head of marks.filter((mark) => mark.named.some(([a]) => a === "walk"))) {
    const named = head.named.find(([a]) => a === "walk")[1];
    const line = strokes.find((mark) => mark.named.some(([a, v]) => a === "line" && v === named));
    if (!line) {
      fail(`${where}: the ${kind} drawing marks a walk along "${named}" and does not draw that line`);
      continue;
    }
    const middle = head.points
      .reduce((sum, [x, y]) => [sum[0] + x / head.points.length, sum[1] + y / head.points.length],
        [0, 0]);
    const [from, to] = line.points;
    const run = [to[0] - from[0], to[1] - from[1]];
    const length = Math.hypot(...run) || 1;
    const across = Math.abs((middle[0] - from[0]) * run[1] - (middle[1] - from[1]) * run[0])
      / length;
    const along = ((middle[0] - from[0]) * run[0] + (middle[1] - from[1]) * run[1])
      / (length * length);
    if (across > 6 || along < 0 || along > 1) {
      fail(`${where}: the ${kind} drawing's arrowhead for "${named}" is not on that line `
        + `(${across.toFixed(1)} away, ${along.toFixed(2)} along it)`);
    }
  }

  // ── 2 · a dot occupies as many places as the engine says ─────────────────────────────────────
  const placesOf = new Map();
  for (const mark of strokes) {
    for (const name of dotsNamedBy(mark)) {
      if (!placesOf.has(name)) placesOf.set(name, []);
      const clusters = placesOf.get(name);
      for (const point of mark.points) {
        if (!clusters.some((seen) => near(seen, point))) clusters.push(point);
      }
    }
  }
  for (const [name, clusters] of placesOf) {
    // A stroke names two dots and has two ends, and nothing here says which is which, so each
    // stroke offers both. The floor is therefore the number of places the engine allows; what this
    // catches is a drawing offering MORE places than the object has, which is what a halved stroke
    // or a displaced mark does.
    const allowed = rules.places("dot", name);
    const strokesNaming = strokes.filter((mark) => dotsNamedBy(mark).includes(name)).length;
    const ceiling = Math.max(allowed, 1) + strokesNaming;
    if (clusters.length > ceiling) {
      fail(`${where}: the ${kind} drawing puts marks naming ${name} at ${clusters.length} `
        + `different points, and the object has it in ${Math.max(allowed, 1)}`);
    }
  }

  // ── 2b · and every mark is where the convention PUTS it ──────────────────────────────────────
  //
  // Identity is checked; internal consistency is checked. What both miss is a **consistent**
  // distortion: move every mark together and the drawing still agrees with itself. A reader
  // mirrored the net left-to-right — every identity honest, every stroke still meeting its
  // neighbours — and `A` and `B` swapped sides, which CANON.md forbids outright and which breaks
  // this repository's own continuity claim that chapter 1's triangle is already where the net puts
  // `ABC`. A top-to-bottom flip passed too, and so did one dot displaced eighty-one pixels with its
  // three strokes following it.
  //
  // So the drawn positions are held to the convention's own: the same scale on both axes, the
  // orientation the convention fixes, and every dot where it belongs. A mirror makes the x-scale
  // negative, a flip makes the y-scale the wrong sign, and a displacement fits nothing.
  // The wireframe is in this list now; it was exempt, which a reader was right to call out. What it
  // is held to is the same as the flat conventions: **one scale on both axes**, against the engine's
  // own points projected — by this check's own arithmetic — at the view the drawing best matches.
  //
  // One correction to the finding, measured rather than argued. A **flip** of the projection's
  // vertical is a distortion and is caught. A **mirror of its horizontal is not a defect at all**:
  // the threaded pair is centrally symmetric — every point has its negative in the set, which this
  // check verifies from the engine's own coordinates — so the mirror image of any view *is* another
  // view of the same object. Mirroring the opening view's x gives, to a residual of 0.000000, the
  // projection at yaw 2.443 / pitch 0.654. Every dot stays correctly named and the picture stays a
  // true orthographic projection, so there is nothing there to fail. The guard discriminates
  // between distorting the object and looking at it from somewhere else, which is the distinction
  // worth having.
  // `project3d` already returns a screen-oriented pair — it negates the vertical itself — and
  // `drawWire` scales it without a further flip, so the wireframe's vertical scale is positive
  // where the flat conventions' is negative. Measured, not assumed: it comes out at +106.60.
  const ORIENTATION = { net: -1, triangle: -1, ring: 1, wire: 1 };
  if (kind in ORIENTATION) {
    // For the wireframe, the check projects the engine's own points itself — see `ownProject3d`.
    const belong = kind === "wire"
      ? ownWireDots(wireViewOf(svg))
      : draw.whereDotsBelong(kind);
    const dotMarks = marks.filter((mark) => mark.element === "circle"
      && mark.named.some(([attribute]) => attribute === "dot"));
    const drawnByName = {};
    for (const mark of dotMarks) {
      const name = mark.named.find(([attribute]) => attribute === "dot")[1];
      (drawnByName[name] = drawnByName[name] || []).push(mark.points[0]);
    }
    // The net draws no dots of its own, so a corner has to be found: it is the point the strokes
    // naming it, in one panel, have in common. Pooling both ends of every stroke instead — which an
    // earlier draft did — hands back every dot's position for every name and fits nothing.
    if (!dotMarks.length) {
      const panels = [...new Set(strokes.map((mark) => mark.panel))];
      for (const panel of panels) {
        const here = strokes.filter((mark) => mark.panel === panel);
        const named = new Set(here.flatMap((mark) => dotsNamedBy(mark)));
        for (const name of named) {
          const touching = here.filter((mark) => dotsNamedBy(mark).includes(name));
          if (touching.length < 2) continue;
          const shared = touching[0].points.find((point) =>
            touching.every((mark) => mark.points.some((other) => near(other, point))));
          if (!shared) continue;
          const found = (drawnByName[name] = drawnByName[name] || []);
          if (!found.some((point) => near(point, shared))) found.push(shared);
        }
      }
    }

    // Fit from the names the convention puts in exactly one place, which is every name but `D` on
    // the flat net.
    const anchors = Object.keys(belong)
      .filter((name) => belong[name].length === 1 && (drawnByName[name] || []).length === 1)
      .map((name) => ({ name, from: belong[name][0], to: drawnByName[name][0] }));
    // A drawing with fewer than two locatable dots — chapter 1's opening beat has one — cannot be
    // fitted and cannot meaningfully be mirrored either. The counts and the identity checks still
    // hold it; there is simply no orientation to test.
    if (anchors.length >= 2) {
      const spread = (axis) => anchors.reduce((best, one) => anchors.reduce((inner, two) =>
        (Math.abs(one.from[axis] - two.from[axis]) > Math.abs(inner.a.from[axis] - inner.b.from[axis])
          ? { a: one, b: two } : inner), best), { a: anchors[0], b: anchors[1] });
      const scales = [0, 1].map((axis) => {
        const { a, b } = spread(axis);
        const run = a.from[axis] - b.from[axis];
        return Math.abs(run) < 1e-9 ? null : (a.to[axis] - b.to[axis]) / run;
      });
      const [sx, sy] = scales;
      // A step that draws two dots on one horizontal line gives the vertical axis no spread to fit
      // — chapter 1's first two beats are exactly that — and there is nothing to flip in a line, so
      // that axis is simply not tested rather than treated as a failure. The axis that HAS spread
      // is still tested, and a two-dot drawing can still be mirrored.
      if (sx === null && sy === null) {
        fail(`${where}: the ${kind} drawing gives neither axis any spread to check`);
      } else if (sx !== null && sx <= 0) {
        fail(`${where}: the ${kind} drawing is MIRRORED — its horizontal scale is ${sx.toFixed(2)}. `
          + `CANON.md: the diagram is never rotated or mirrored`);
      } else if (sy !== null && Math.sign(sy) !== ORIENTATION[kind]) {
        fail(`${where}: the ${kind} drawing is FLIPPED top to bottom — its vertical scale is `
          + `${sy.toFixed(2)}, and this convention's is ${ORIENTATION[kind] > 0 ? "positive" : "negative"}`);
      } else if (sx !== null && sy !== null
        && Math.abs(Math.abs(sx) - Math.abs(sy)) > 0.01 * Math.abs(sx)) {
        fail(`${where}: the ${kind} drawing is stretched — ${Math.abs(sx).toFixed(2)} across and `
          + `${Math.abs(sy).toFixed(2)} down. One scale, or the shape is not the object's`);
      } else {
        const anchor = anchors[0];
        // Where an axis had no spread, the other axis's scale stands in — the two are equal by the
        // test above wherever both are measurable.
        const ax = sx === null ? Math.abs(sy) : sx;
        const ay = sy === null ? Math.abs(sx) * ORIENTATION[kind] : sy;
        const place = (point) => [
          anchor.to[0] + (point[0] - anchor.from[0]) * ax,
          anchor.to[1] + (point[1] - anchor.from[1]) * ay,
        ];
        for (const [name, wanted] of Object.entries(belong)) {
          const drawn = drawnByName[name] || [];
          if (!drawn.length) continue;             // this step does not draw that dot
          for (const one of wanted) {
            const to = place(one);
            if (!drawn.some((point) => Math.hypot(point[0] - to[0], point[1] - to[1]) <= 1.5)) {
              fail(`${where}: the ${kind} drawing puts ${name} where the convention does not — `
                + `nothing of that name is at ${to.map((v) => v.toFixed(0)).join(",")}`);
            }
          }
        }
      }
    }
  }

  // ── 2b(ii) · the ring's stated orientation ────────────────────────────────────────────────────
  //
  // The ring has no coordinates in the engine — DEMOS.md's convention is its only definition — so
  // the fit above compares it against `ringLayout`, which is the same function that draws it. A
  // reader mirrored that function and both sides moved together. What CAN be held independently is
  // what the convention says in words: the middle of `AB` on the outside at the top, `AC` to the
  // lower left, `AD` to the lower right. Those three sentences are the check.
  if (kind === "ring") {
    // The ring's convention is four sentences, and this used to be three inequalities. A reader
    // rotated the inner dots twenty degrees off their partners' rays and it passed — while the poke
    // step's
    // table still says *poked AB · its opposite CD* and DEMOS.md's stated reason for the whole
    // convention is that "opposite is literally straight through the middle, which is what the poke
    // beat needs a reader to see". She was being told to look at a thing the drawing had stopped
    // showing. Unequal radii and a twelve-degree rotation passed too.
    //
    // So the sentences are the check: six dots on two circles about their common centre, three on
    // each; every opposite pair straight through that centre; AB's middle on the vertical above it.
    const at = {};
    for (const mark of marks.filter((m) => m.element === "circle")) {
      const named = mark.named.find(([attribute]) => attribute === "dot");
      if (named && payload.cut.mid_names.includes(named[1])) at[named[1]] = mark.points[0];
    }
    const middles = payload.cut.mid_names.filter((name) => at[name]);
    if (middles.length === payload.cut.mid_names.length) {
      // The centre: three dots at a hundred and twenty degrees sum to it on each circle, so the
      // middle of all six is the common centre whatever the two radii are.
      const centre = middles.reduce((sum, name) =>
        [sum[0] + at[name][0] / middles.length, sum[1] + at[name][1] / middles.length], [0, 0]);
      const radius = (name) => Math.hypot(at[name][0] - centre[0], at[name][1] - centre[1]);
      const radii = middles.map(radius);

      // Two circles, three dots on each.
      const rings = [];
      for (const r of radii) {
        const seen = rings.find((one) => Math.abs(one.r - r) <= 1);
        if (seen) seen.count += 1;
        else rings.push({ r, count: 1 });
      }
      if (rings.length !== 2 || rings.some((one) => one.count !== 3)) {
        fail(`${where}: the ring's six dots do not sit three and three on two circles — the radii `
          + `are ${radii.map((r) => r.toFixed(0)).join(", ")}. DEMOS.md: six dots on two `
          + `concentric circles`);
      }

      // Every opposite pair straight through the centre.
      for (const [one, other] of payload.cut.opposite_pairs) {
        if (!at[one] || !at[other]) continue;
        const a = [at[one][0] - centre[0], at[one][1] - centre[1]];
        const b = [at[other][0] - centre[0], at[other][1] - centre[1]];
        const lengthA = Math.hypot(...a) || 1;
        const lengthB = Math.hypot(...b) || 1;
        const off = Math.abs(a[0] * b[1] - a[1] * b[0]) / lengthB;   // centre's distance from the line
        const cosine = (a[0] * b[0] + a[1] * b[1]) / (lengthA * lengthB);
        if (off > 1.5 || cosine > -0.999) {
          const degrees = (Math.acos(Math.max(-1, Math.min(1, cosine))) * 180) / Math.PI;
          fail(`${where}: ${one} and ${other} are ${degrees.toFixed(1)}° apart through the centre, `
            + `${off.toFixed(1)}px off a straight line through it. They are the pair joined by `
            + `nothing, and the convention exists so that opposite is literally straight through `
            + `the middle — which is what the poke beat asks her to see`);
        }
      }

      // AB's middle on the vertical, above the centre.
      const ab = at[payload.cut.mid_names[0]];
      if (Math.abs(ab[0] - centre[0]) > 1.5 || ab[1] >= centre[1]) {
        fail(`${where}: the ring does not put ${payload.cut.mid_names[0]}'s middle straight above `
          + `the centre — it is ${(ab[0] - centre[0]).toFixed(1)}px to the side. The drawing is `
          + `rotated, and the convention fixes it`);
      }
      // And which way round the other two go, which is what a mirror changes.
      const [ac, ad] = [payload.cut.mid_names[1], payload.cut.mid_names[2]].map((name) => at[name]);
      if (ac && ad && !(ac[0] < ad[0])) {
        fail(`${where}: the ring puts ${payload.cut.mid_names[1]} to the right of `
          + `${payload.cut.mid_names[2]}; the convention has one lower left and the other lower `
          + `right — the drawing is mirrored`);
      }
    }
  }

  // ── 2c · a label is nearer the mark it names than any other ──────────────────────────────────
  //
  // The sharpest form of the same family: displace a dot and let its strokes follow, and the label
  // stays at its old position while the mark it names has moved a hundred pixels away. Nothing said
  // a name had to be near its own dot. Two readers found this independently, one by moving a mark
  // and one by finding `A′` eighteen pixels from `B` and eighty from `A′`.
  {
    const positions = new Map();
    for (const mark of marks.filter((m) => m.element === "circle")) {
      const named = mark.named.find(([attribute]) => attribute === "dot"
        || attribute === "middle");
      if (named) positions.set(named[1], [...(positions.get(named[1]) || []), mark.points[0]]);
    }
    for (const [name, clusters] of placesOf) {
      if (!positions.has(name)) positions.set(name, clusters);
    }
    const names = [...positions.keys()].sort((a, b) => b.length - a.length);
    // A label a leader runs to has been told which dot it belongs to in ink, which is a stronger
    // statement than being near it. Those are exempt from the proximity rule and not from anything
    // else — the leader itself is a mark, held to a real dot and to starting at it.
    const led = new Set([...svg.matchAll(/data-leader="([^"]*)"/g)].map((m) => m[1]));
    // A leader is the exception, so it has to stay exceptional. One drawing needing a leader for
    // half its names is a placement that has given up, and every one of those labels would then be
    // exempt from the proximity rule — which is how a reader made the whole rule vanish by forcing
    // the leader path. Two is the ceiling: the ring needs one and the wireframe needs one.
    // A leader has to REACH the label it names. Reversing one leaves it starting exactly on its dot
    // — so the meet test passes — with its far end seventy pixels from the label, pointing into
    // empty space the opposite way, and the label keeps its proximity exemption. The exemption's
    // whole justification is that the association is stated in ink; this is what checks the ink
    // arrives.
    const labelAt = new Map();
    for (const found of svg.matchAll(/<text([^>]*)>([^<]*)<\/text>/g)) {
      const at = /x="([-\d.]+)" y="([-\d.]+)"/.exec(found[1]);
      if (!at) continue;
      const text = found[2].trim();
      const owner = [...led].find((name) => text === name || text.startsWith(`${name} `));
      if (owner) labelAt.set(owner, [+at[1], +at[2]]);
    }
    for (const found of svg.matchAll(/<line\b[^>]*data-leader="([^"]*)"[^>]*>/g)) {
      const name = found[1];
      const ends = /x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/.exec(found[0]);
      const label = labelAt.get(name);
      if (!ends) continue;
      if (!label) {
        fail(`${where}: a leader claims the dot ${name} and there is no label of that name for it `
          + `to reach`);
        continue;
      }
      const reach = Math.min(
        Math.hypot(+ends[1] - label[0], +ends[2] - label[1]),
        Math.hypot(+ends[3] - label[0], +ends[4] - label[1]),
      );
      if (reach > 20) {
        fail(`${where}: the leader for ${name} stops ${reach.toFixed(1)}px from the label it names. `
          + `A leader is what earns that label its exemption from being nearest its own dot, and a `
          + `leader that does not arrive earns nothing`);
      }
    }
    if (led.size > 2) {
      fail(`${where}: ${led.size} labels needed a leader. A leader is for the dot proximity cannot `
        + `reach; when most of them need one, the placement has failed and the proximity rule has `
        + `quietly stopped applying to anything`);
    }
    for (const found of svg.matchAll(/<text([^>]*)>([^<]*)<\/text>/g)) {
      const at = /x="([-\d.]+)" y="([-\d.]+)"/.exec(found[1]);
      if (!at) continue;
      const text = found[2].trim();
      const mine = names.find((name) => text === name || text.startsWith(`${name} `));
      if (!mine || led.has(mine)) continue;
      const here = [+at[1], +at[2]];
      const away = (name) => Math.min(...positions.get(name)
        .map((point) => Math.hypot(point[0] - here[0], point[1] - here[1])));
      const nearer = names.filter((name) => name !== mine && away(name) < away(mine));
      if (nearer.length) {
        fail(`${where}: the label "${text}" is ${away(mine).toFixed(0)}px from ${mine} and `
          + `${away(nearer[0]).toFixed(0)}px from ${nearer[0]} — a name has to be nearest the mark `
          + `it names`);
      }
    }
  }

  // ── 3 · counts, per name and in total ────────────────────────────────────────────────────────
  const tally = {};
  for (const mark of marks) {
    for (const [attribute, value] of mark.named) {
      tally[attribute] = tally[attribute] || {};
      const at = attribute === "region" ? value : (value.includes("|")
        ? value.split("|").sort().join("|") : value);
      tally[attribute][at] = (tally[attribute][at] || 0) + 1;
    }
  }
  for (const attribute of rules.once || []) {
    for (const [value, count] of Object.entries(tally[attribute] || {})) {
      if (count !== 1) {
        fail(`${where}: the ${kind} drawing draws the ${attribute} "${value}" ${count} times, and `
          + `the object has one of it`);
      }
    }
  }
  for (const [attribute, expected] of Object.entries(rules.counted || {})) {
    const drawn = tally[attribute] || {};
    const total = Object.values(drawn).reduce((sum, count) => sum + count, 0);
    if (total === 0) continue;                  // this step does not draw them at all
    for (const [value, count] of Object.entries(drawn)) {
      if (count !== expected[value]) {
        fail(`${where}: the ${kind} drawing draws the ${attribute} "${value}" ${count} time(s), `
          + `and the engine puts it in ${expected[value] ?? "no"} place(s)`);
      }
    }
    // And the other direction, which the loop above cannot reach: a value drawn **nowhere** is not
    // a key of `drawn`, so it was invisible. One of the net's twelve strokes simply left out — a
    // whole line of the object missing from the picture — passed every gate; a mutation written for
    // the count rule found it. Iterating the engine's list instead of the drawing's is the fix.
    //
    // The constraint that buys, stated because it is real: a drawing of a convention with counted
    // marks shows **every** one of them or none at all — all 65 net drawings do today, and a step
    // that wanted to show a partial net would have to say so here rather than read as a bug.
    for (const [value, wanted] of Object.entries(expected)) {
      if (!drawn[value]) {
        fail(`${where}: the ${kind} drawing draws the ${attribute} "${value}" nowhere, and the `
          + `engine puts it in ${wanted} place(s)`);
      }
    }
  }
  for (const [attribute, expected] of Object.entries(rules.exactly || {})) {
    if (expected === null) continue;
    const total = Object.values(tally[attribute] || {}).reduce((sum, count) => sum + count, 0);
    if (total !== expected) {
      fail(`${where}: the ${kind} drawing put down ${total} ${attribute} mark(s); the engine `
        + `has ${expected}`);
    }
  }

  // Every dot the convention always shows is shown.
  for (const name of rules.dotsAtLeast || []) {
    if (!(tally.dot || {})[name]) {
      fail(`${where}: the ${kind} drawing has no dot for ${name}, and this convention draws all `
        + `of them`);
    }
  }

  // A tip that has lines drawn to it has a dot at the end of them.
  if (rules.tipsHaveDots) {
    for (const value of Object.keys(tally["tip-line"] || {})) {
      const tip = value.split("|")[0];
      if (!(tally.dot || {})[tip]) {
        fail(`${where}: the ${kind} drawing draws lines to the tip ${tip} and no dot there`);
      }
    }
  }

  // And every stroke ends on a dot the drawing actually put down.
  if (rules.endsOnDots) {
    const dotPoints = marks.filter((mark) => mark.element === "circle"
      && mark.named.some(([attribute]) => attribute === "dot"))
      .map((mark) => mark.points[0]);
    if (!dotPoints.length && strokes.length) {
      fail(`${where}: the ${kind} drawing drew ${strokes.length} stroke(s) and no dots at all`);
    }
    for (const stroke of strokes) {
      if (stroke.named.some(([attribute]) => attribute === "leader")) continue;
      for (const end of stroke.points) {
        if (!dotPoints.some((point) => near(point, end))) {
          fail(`${where}: the ${kind} drawing's ${stroke.source.slice(0, 50)}… ends at `
            + `${end.map((v) => v.toFixed(0)).join(",")}, where it has drawn no dot`);
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
// ── 11 · the five the engine answers now, and the steps that ask it ───────────────────────────────
//
// UniForge's `lab/napkin/0003` closed the five places where a step wanted something the browser
// surface could not be asked, and this is what holds the pages to *asking*. Every one of the five
// has a shape a page could fake: a dialled run vendored as one fixed answer, a walk's running
// column read off its own terms, a certificate borrowed from another shape, a "no closed walk"
// sentence nobody computed. None of those is a wrong number, so the numeric scan cannot see any of
// them — which is exactly the "right value, wrong place" hole this file says it cannot close in
// general. It can be closed **here**, because for these five the question is known.
//
// The first version of this gate had all of that and was walked through five times in one read, and
// every escape was the same mistake in a different place: **it asked whether the page agreed with
// itself.** It re-asked the engine using the tick the table printed, the weights the table printed,
// and it checked nothing at all about the cells whose whole content was an answer. So a certificate
// pinned to its own printed tick agreed with itself in every state, a weight written as a word
// disarmed the dial leg through a `null` check, and the two-dot answer could simply be typed.
//
// So this version rebuilds what the page must show **from the step's own inputs** — the state the
// check itself drove the step into — and holds the cells to that:
//
//   · **the question was asked at all.** Each driven step is rebuilt against an engine door of its
//     own, rendered in every state, and the calls that door recorded must include the one the step
//     owes, matched on the entry point *and the arguments this gate pins* — the object, and for a
//     walk its degree and index, so the right entry point asked a different question is caught.
//   · **the cells are the answer.** Every driven table's rows are computed here from the engine and
//     the state, and compared cell by cell (a `null` means this gate does not speak for that cell).
//   · **the running column is the sum building**, added up in exact arithmetic on the digits a
//     reader sees — and a declared running column that holds no number on a row that has numbers is
//     refused, because pointing the declaration at two prose columns exempted a whole walk table.
//   · **and every leg ran.** Each of these checks counts, and a leg that never fired on any state of
//     any step is reported: all five legs failed *open* in the first version, which is the shape of
//     defect this repository has met most often — a guard that stops applying rather than fails.
//
// A step names the tables this gate reads by `tag`, which is not shown to anybody, so a caption may
// be rewritten freely and deleting the tag is a failure rather than a quiet exemption.
const oracle = new Engine(glue, payload, rows);

const TWO_DOTS = "two-dots";
const NOTHING = payload.poke.history[0][1];
const CORNER_NAMES = payload.tetrahedron.names;
const LINE_NAMES = payload.tetrahedron.line_names;
const FIRST_THREE = payload.triangle.chapter.values;
const AT_BOOK = rows.triangle_motion.at_the_book_tick;
// The corner a napkin will not write, which is the one that step swaps in — the engine's own count
// of how far it gets says which row it comes off, exactly as the step derives it.
const UNPRINTABLE = AT_BOOK.history[AT_BOOK.printable_rows][0];

const printed = (value) => oracle.text(value);
const signedText = (value) => oracle.signed(value).text;

/** What a certificate's own answer puts in the columns a table gives it; `null` is not spoken for. */
function certificateCells(object, k, at) {
  const answer = oracle.certificate(object, k);
  const say = {
    k: () => printed(answer.k),
    bound: () => printed(answer.bound),
    eigenvalue: () => printed(String(answer.eigenvalue)),
    eigenvector: () => answer.eigenvector.map((value) => printed(String(value))).join("  "),
    holds: () => (answer.holds ? "yes" : "no"),
  };
  return at.map((field) => (field === null ? null : say[field]()));
}

/** One walk's terms and its running column, as the engine gives them for these inputs. */
function walkNumbers(object, degree, index, values, take) {
  const walk = oracle.walk(object, degree, index, values);
  const upto = take === null ? walk.terms.length : take;
  return {
    terms: walk.terms.slice(0, upto).map(signedText),
    running: walk.running.slice(0, upto).map(printed),
  };
}

/** The differences on the triangle's lines, from three corner numbers. */
const triangleEdges = (values) => oracle.loops("triangle", values, 0).loops;

const DRIVEN = {
  // Two dots and a line: the difference on its one line, and its own count of closed walks.
  "change-lives-between": {
    asks: ["loops_json", TWO_DOTS],
    tables: {
      "two-dots-difference": (state) => [[
        LINE_NAMES[0],
        `${printed(state.numbers[1])} − ${printed(state.numbers[0])}`,
        signedText(oracle.loops(TWO_DOTS, state.numbers, 0).loops[0]),
      ]],
    },
  },
  "nothing-closes-yet": {
    asks: ["loops_json", TWO_DOTS],
    // The answer is the same in every state — two dots and a line close nothing, whatever she
    // types — so the comparison above cannot tell a cell that READ that answer from a cell that
    // was written to agree with it. This is what tells them apart: the engine is made to answer
    // differently, and the cells that come off the field it changed must say something else.
    //
    // **Per cell, one perturbation per field.** A reviewer typed a verdict word into one column of
    // a driven table and left its neighbour honest, and a whole-table comparison passed it: the
    // honest cell moved, so the table moved. A cell is what a reader reads.
    reads: [
      { change: (answer) => ({ ...answer, closed_walks: answer.closed_walks + 1 }),
        tag: "two-dots-closed", cells: [[0, 0], [0, 1]] },
    ],
    tables: {
      "two-dots-closed": () => {
        const closed = oracle.loops(TWO_DOTS, [NOTHING], 1);
        const walks = closed.closed_walks;
        // "none", not a nought — the page's convention, stated here so that the cell is the
        // engine's answer rendered one fixed way rather than a word anybody may type.
        return [[walks === 0 ? "none" : String(walks), walks === 0 ? "no" : "yes"]];
      },
    },
  },

  // The walks, with the sum building term by term.
  "walk-it-and-add": {
    asks: ["walk_json", "triangle", 1, 0],
    walk: { tag: "walk-running",
      of: (state) => walkNumbers("triangle", 1, 0, triangleEdges(state.numbers), state.tick) },
  },
  "any-three-numbers-at-all": {
    asks: ["walk_json", "triangle", 1, 0],
    walk: { tag: "walk-running",
      of: (state) => walkNumbers("triangle", 1, 0, triangleEdges(state.choice.value), null) },
  },
  "why-it-is-exact-and-not-approximate": {
    asks: ["walk_json", "triangle", 1, 0],
    walk: { tag: "walk-running",
      of: (state) => walkNumbers("triangle", 1, 0, triangleEdges(state.pressed
        ? [...FIRST_THREE.slice(0, 2), UNPRINTABLE] : FIRST_THREE), null) },
  },
  "round-the-inside": {
    asks: ["walk_json", "tetrahedron", 2, 0],
    walk: { tag: "walk-running",
      of: (state) => walkNumbers("tetrahedron", 2, 0,
        oracle.loops("tetrahedron", state.numbers, 1).loops, null) },
  },

  // The dial, run at the weights the reader has left it at.
  "turn-the-dial": {
    asks: ["slosh_weighted_json", "tetrahedron"],
    turned: true,
    tables: {
      "dial-weights": (state) => LINE_NAMES.map((name, index) => [name, printed(state.numbers[index])]),
      "dial-run": (state) => {
        const answer = oracle.sloshWeighted("tetrahedron", payload.tetrahedron.corners,
          state.numbers, payload.motion.k, payload.motion.ticks);
        return answer.history.map((row, tick) =>
          [String(tick), ...row.map(printed), printed(answer.totals[tick])]);
      },
    },
  },

  // The eight faces, walked outward, per face — and the counter that says how far she has got,
  // which is held to the rows the walk table actually lists. Two counters of the same thing
  // disagreeing is a defect this step has had once already.
  "coming-home-on-eight-faces": {
    asks: ["face_sum_json", "octahedron"],
    reads: [
      { change: (answer) => ({ ...answer, running: [...answer.running].reverse() }),
        tag: "face-walk", cells: [[1, 2]] },
      // The orientation is a word, and the same word in every state, so nothing but this says the
      // page read it rather than agreed with it. DEMOS.md claims it is the engine's own word.
      { change: (answer) => ({ ...answer, orientation: answer.object }),
        tag: "face-count", cells: [[0, 3]] },
      { change: (answer) => ({ ...answer, lines_walked_each_way: answer.lines_walked_each_way + 1 }),
        tag: "face-count", cells: [[0, 2]] },
    ],
    walk: { tag: "face-walk",
      of: (state) => {
        const answer = oracle.faceSum("octahedron", payload.face_sum.arrows);
        return {
          terms: answer.face_numbers.slice(0, state.tick).map(signedText),
          running: answer.running.slice(0, state.tick).map(printed),
        };
      } },
    counter: { tag: "face-count", column: 0, of: "face-walk" },
  },

  // Every certificate on the pages, not only the one this pass rewired: the triangle's is the new
  // answer, and the other four were rendered by the same code and held by nothing.
  "the-tick-belongs-to-the-shape": {
    asks: ["certificate_json", "triangle"],
    reads: [
      { change: (answer) => ({ ...answer, eigenvalue: answer.eigenvalue + 1 }),
        tag: "triangle-certificate", cells: [[0, 1]] },
      { change: (answer) => ({ ...answer, eigenvector: [...answer.eigenvector].reverse() }),
        tag: "triangle-certificate", cells: [[0, 2]] },
      { change: (answer) => ({ ...answer, bound: answer.eigenvector.length.toString() }),
        tag: "triangle-certificate", cells: [[0, 3]] },
      { change: (answer) => ({ ...answer, holds: !answer.holds }), tag: "triangle-certificate", cells: [[0, 4]] },
    ],
    tables: {
      "triangle-certificate": (state) => [certificateCells("triangle", state.choice.value,
        ["k", "eigenvalue", "eigenvector", "bound", "holds"])],
    },
  },
  "now-the-tetrahedron": {
    asks: ["certificate_json", "tetrahedron"],
    reads: [
      { change: (answer) => ({ ...answer, eigenvalue: answer.eigenvalue + 1 }),
        tag: "tetrahedron-certificate", cells: [[0, 1]] },
      { change: (answer) => ({ ...answer, bound: answer.eigenvector.length.toString() }),
        tag: "tetrahedron-certificate", cells: [[0, 2]] },
      { change: (answer) => ({ ...answer, holds: !answer.holds }), tag: "tetrahedron-certificate", cells: [[0, 3]] },
    ],
    tables: {
      "tetrahedron-certificate": () => [certificateCells("tetrahedron", payload.motion.k,
        ["k", "eigenvalue", "bound", "holds"])],
    },
  },
  "it-takes-two-ticks-to-cross": {
    asks: ["certificate_json", "octahedron"],
    reads: [
      { change: (answer) => ({ ...answer, eigenvalue: answer.eigenvalue + 1 }),
        tag: "octahedron-certificate", cells: [[0, 1]] },
      { change: (answer) => ({ ...answer, bound: answer.eigenvector.length.toString() }),
        tag: "octahedron-certificate", cells: [[0, 2]] },
      { change: (answer) => ({ ...answer, holds: !answer.holds }), tag: "octahedron-certificate", cells: [[0, 3]] },
    ],
    tables: {
      "octahedron-certificate": () => [certificateCells("octahedron", payload.poke.k,
        ["k", "eigenvalue", "bound", "holds"])],
    },
  },
  "the-tick-that-stops-working": {
    asks: ["certificate_json", "stella"],
    reads: [
      { change: (answer) => ({ ...answer, eigenvalue: answer.eigenvalue + 1 }),
        tag: "stella-certificate", cells: [[0, 1]] },
      { change: (answer) => ({ ...answer, bound: answer.eigenvector.length.toString() }),
        tag: "stella-certificate", cells: [[0, 2]] },
      { change: (answer) => ({ ...answer, holds: !answer.holds }), tag: "stella-certificate", cells: [[0, 3]] },
    ],
    tables: {
      "stella-certificate": () => [certificateCells("stella", payload.refusal.runaway.k,
        ["k", "eigenvalue", "bound", "holds"])],
    },
  },
  "the-smaller-tick-does-not-save-it": {
    asks: ["certificate_json", "stella"],
    reads: [
      { change: (answer) => ({ ...answer, bound: answer.eigenvector.length.toString() }),
        tag: "stella-tried", cells: [[0, 1]] },
      { change: (answer) => ({ ...answer, holds: !answer.holds }),
        tag: "stella-tried", cells: [[0, 2]] },
    ],
    tables: {
      // The last two columns are the run's rather than the certificate's, and a reviewer swapped
      // them — `never · 1` where the page means `1 · never` — with every other gate silent. So they
      // are taken from the vendored run this step offers, found by the tick rather than by reading
      // them off the choice the page happens to be holding.
      "stella-tried": (state) => {
        const tried = payload.refusal.runaway.stable_tried
          .find((one) => one.k === state.choice.value.k);
        return [[...certificateCells("stella", state.choice.value.k, ["k", "bound", "holds"]),
          String(tried.printable), tried.period === 0 ? "never" : String(tried.period)]];
      },
    },
  },
};

/** Every leg that must fire at least once, and how often it did. */
const legsRan = new Map();
const ran = (anchor, leg) => legsRan.set(`${anchor} · ${leg}`,
  (legsRan.get(`${anchor} · ${leg}`) || 0) + 1);
for (const [anchor, spec] of Object.entries(DRIVEN)) {
  for (const tag of Object.keys(spec.tables || {})) legsRan.set(`${anchor} · ${tag}`, 0);
  if (spec.walk) legsRan.set(`${anchor} · ${spec.walk.tag}`, 0);
  if (spec.counter) legsRan.set(`${anchor} · ${spec.counter.tag}`, 0);
  if (spec.turned) legsRan.set(`${anchor} · a dial turned off the plain`, 0);
  if (spec.reads) legsRan.set(`${anchor} · the answer is read, not agreed with`, 0);
}

/** Which entry points, with which pinned arguments, one engine door has actually been asked. */
function questionsAsked(door) {
  const asked = [];
  for (const key of door.calls) {
    const found = /^([a-z_]+)\((.*)\)$/s.exec(key);
    if (!found) continue;
    try { asked.push([found[1], ...JSON.parse(found[2])]); } catch { /* not a call this gate reads */ }
  }
  return asked;
}

/** Does any call match this pin — the entry point and the leading arguments named with it? */
const wasAsked = (asked, pins) => asked.some((call) =>
  pins.every((pin, index) => JSON.stringify(call[index]) === JSON.stringify(pin)));

/** Does this row carry a number anywhere in it? */
const hasNumbers = (row) => row.some((cell) => exact(cell) !== null);

/** Hold one rendered state of one driven step to the engine's answer for that state's own inputs. */
function drivenBy(step, rendered, state, where) {
  const anchor = step.anchors.find((one) => DRIVEN[one]);
  if (!anchor) return;
  const spec = DRIVEN[anchor];
  // Exactly one table per tag. `find` took the first, so a second table carrying a tag already
  // used was unheld by this gate and its numbers were the engine's — two ceiling tables on one
  // step, disagreeing, and every gate green. A reviewer built exactly that.
  const find = (tag) => {
    const found = rendered.tables.filter((table) => table.tag === tag);
    if (found.length !== 1) {
      fail(`${where}: ${found.length} tables are tagged "${tag}", and this gate speaks for exactly `
        + `one. That tag is how it finds the table whose numbers are ${spec.asks[0]}'s answer: `
        + `lose it and nothing holds the table to the engine, repeat it and the copy is unheld`);
      return null;
    }
    return found[0];
  };

  // Every cell this gate speaks for, against the engine's answer for this state's own inputs.
  for (const [tag, expect] of Object.entries(spec.tables || {})) {
    const shown = find(tag);
    if (!shown) continue;
    const wanted = expect(state);
    ran(anchor, tag);
    if (shown.rows.length !== wanted.length) {
      fail(`${where}: the table tagged "${tag}" prints ${shown.rows.length} row(s) and the engine's `
        + `answer for this step's own inputs has ${wanted.length}`);
      continue;
    }
    wanted.forEach((row, index) => {
      row.forEach((cell, at) => {
        if (cell === null) return;
        if (String(shown.rows[index][at]) !== cell) {
          fail(`${where}: the table tagged "${tag}" prints "${shown.rows[index][at]}" where the `
            + `engine answers "${cell}" for this step's own inputs — the row is `
            + `${shown.rows[index].join(" · ")}`);
        }
      });
    });
  }

  // The walk's terms and its running column, likewise — read off the columns the table itself
  // declares, so a declaration pointed anywhere else disagrees with the engine here.
  if (spec.walk) {
    const shown = find(spec.walk.tag);
    const runs = shown && shown.shape && shown.shape.runs;
    if (shown && !runs) {
      fail(`${where}: the table tagged "${spec.walk.tag}" does not say which of its columns is the `
        + `walk's running sum. Declare { runs: [terms, running] } — a running column nothing adds `
        + `up is a column a reader is asked to trust`);
    }
    if (shown && runs) {
      const wanted = spec.walk.of(state);
      const terms = [];
      const running = [];
      for (const row of shown.rows) {
        if (!hasNumbers(row)) continue;                 // a "none yet" row holds no walk
        if (exact(row[runs[0]]) === null || exact(row[runs[1]]) === null) {
          fail(`${where}: the table tagged "${spec.walk.tag}" declares columns ${runs.join(" and ")} `
            + `as its terms and its running sum, and on a row that carries numbers one of them `
            + `holds none — a declaration pointed at prose exempts the whole table`);
          continue;
        }
        terms.push(String(row[runs[0]]));
        running.push(String(row[runs[1]]));
      }
      ran(anchor, spec.walk.tag);
      if (JSON.stringify([terms, running]) !== JSON.stringify([wanted.terms, wanted.running])) {
        fail(`${where}: the walk printed in "${spec.walk.tag}" is not the engine's for this step's `
          + `own inputs — the page walks ${terms.join(" ")} / ${running.join(" ")} and the engine `
          + `answers ${wanted.terms.join(" ")} / ${wanted.running.join(" ")}`);
      }
    }
  }

  // And a counter about a walk is held to the walk it counts.
  if (spec.counter) {
    const shown = find(spec.counter.tag);
    const walked = rendered.tables.find((table) => table.tag === spec.counter.of);
    if (shown && walked) {
      const listed = walked.rows.filter(hasNumbers).length;
      ran(anchor, spec.counter.tag);
      if (!shown.rows.length) {
        fail(`${where}: the table tagged "${spec.counter.tag}" has no rows at all, so it counts `
          + `nothing — which is a table that has stopped saying anything rather than one that says `
          + `something wrong`);
      } else if (String(shown.rows[0][spec.counter.column]) !== String(listed)) {
        fail(`${where}: the table tagged "${spec.counter.tag}" says `
          + `${shown.rows[0][spec.counter.column]} walked and the walk above it lists ${listed}. `
          + `Two counters of the same thing disagreeing is how this step shipped last time`);
      }
    }
  }

  if (spec.turned && new Set(state.numbers).size > 1) ran(anchor, "a dial turned off the plain");
}

const report = [];
// The narrowest gap between any two labels, anywhere. Not a rule — the rule is `LABEL_GAP`, and it
// is enforced — but a **headroom** figure, printed on every run because a reader noticed it had
// narrowed from 9.96px to 3.60px against a 3px rule between two rounds. Nothing was wrong: two
// labels six pixels apart read as two labels. What had changed was that the placement was working
// near its limit instead of comfortably inside it, and that is the kind of thing a project
// remembers for one round and then forgets. Printed, it is observable instead.
let tightest = Infinity;
let tightestAt = "";
let sums = 0;
let runningSums = 0;
const taggedTables = new Set();
let stills = 0;
// The folded pairs the pages actually have, against the list DEMOS.md prints — see gate 9b.
const actualFolds = [];
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
  // Every id is its own chapter's, and it says which chapter it is — the one thing that makes a
  // beat's name survive a chapter moving.
  for (const beat of marked) {
    if (!new RegExp(`^${slug}\\.\\d+$`).test(String(beat))) {
      fail(`${slug}: the beat id "${beat}" is not this chapter's slug and a number. A beat is `
        + `slug.n — a book-wide number is nobody's name`);
    }
  }
  // And a step is labelled by its place on THIS page. A label carrying a beat number is the defect
  // that stranded nine references the last time the book was renumbered.
  joined.steps.forEach((step, index) => {
    const wanted = `step ${index + 1} of ${joined.steps.length}`;
    if (step.label !== wanted) {
      fail(`${slug}: step ${index + 1} is labelled "${step.label}" and this page's own count says `
        + `"${wanted}". A step's label counts this page's steps and nothing outside the page`);
    }
  });
  for (const step of joined.steps) {
    if (step.beats.length > 1) {
      actualFolds.push(step.beats.map((beat, index) => (index ? beat.split(".")[1] : beat))
        .join("+"));
    }
  }
  if (tableSteps.has(slug) && tableSteps.get(slug) !== joined.steps.length) {
    fail(`DEMOS.md says ${slug}'s page walks ${tableSteps.get(slug)} steps and it walks `
      + `${joined.steps.length}`);
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
  // The furniture: captions, column headings and a drawing's own sentences. It is NOT in the budget
  // — DEMOS.md has said so since the budget existed, and a reader still meets every word of it —
  // and until now nothing said how much of it there was, so a pass could hold the budget steady
  // while the page grew. It is counted here and printed beside the budget: observable, not capped.
  const furniture = new Set();
  words.add(pageText.get(`${slug}.html`));
  words.add(chapter.title);
  let surfaces = 0;
  let tokens = 0;

  for (const step of joined.steps) {
    words.add(step.title);
    words.add(step.act);
    // The label is one phrase — "step n of N" — with this page's own counter in it, so it is
    // counted once for the page rather than once per step. DEMOS.md's own counting rule: a button
    // labelled the same way on nine steps is one label, not nine. Under the book-wide numbering
    // every label was a different text and was counted nine times.
    words.add(step.label.replace(/\d+/g, "n"));
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
      // The step's own label — "step 3 of 9" — is the one place a number on the page is not the
      // engine's, and it is not typed either: it counts the steps this page joined, and gate 5
      // above holds it to that count exactly. Everything else is scanned.
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
      for (const table of rendered.tables) {
        furniture.add(table.caption);
        for (const head of table.head) furniture.add(head);
      }
      for (const sentence of sentencesOf(rendered.drawing)) furniture.add(sentence);
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
        // Word-stems, not whole words. "summed" slipped past `\bsum\b` — the boundary was doing the
        // attacker's work for it.
        const totalish = (head) =>
          /\b(add(ed|s|ing)? up|the whole way round|total\w*|altogether|sum\w*|comes? to)\b/i
            .test(String(head));
        // The caption counts as a heading. A reader moved a total-shaped phrase from a column head
        // into the caption and the check stopped looking; a reader does not read them differently.
        // Across a row **or** down a column: a caption saying "summed" over a column of three
        // numbers claims a total as plainly as one saying it over a row, and the first version of
        // this rule only looked across.
        const anyRow = table.rows.some((row) => rowNumbers(row).length >= 2);
        const anyColumn = table.head.some((_, index) =>
          table.rows.filter((row) => numbersIn(row[index]).length >= 1).length >= 2);
        if (totalish(table.caption) && (anyRow || anyColumn)
          && (!shape || shape.total === undefined)) {
          fail(`${slug} ${step.label}: "${table.caption}" is captioned as a total over numbers `
            + `and the table does not declare which column that total is`);
        }
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

      // Gate 11's arithmetic half, over every table anywhere that declares a running column: the
      // engine's partial sums, added up here on the digits a reader sees, down the rows. A walk's
      // running column is the one number on these pages a reader can check by eye against the
      // column beside it, and the page is not allowed to make it — so this is what says the column
      // the engine handed over is the column that got printed.
      for (const table of rendered.tables) {
        const runs = table.shape && table.shape.runs;
        if (!runs) continue;
        const [termAt, runningAt] = runs;
        let building = [0n, 1n];
        for (const row of table.rows) {
          const term = exact(row[termAt]);
          const shown = exact(row[runningAt]);
          if (term === null || shown === null) continue;
          building = [building[0] * term[1] + term[0] * building[1], building[1] * term[1]];
          runningSums += 1;
          if (building[0] * shown[1] !== shown[0] * building[1]) {
            fail(`${slug} ${step.label}: "${table.caption}" says the walk is holding ${row[runningAt]} `
              + `after ${row[termAt]}, and the terms above it come to something else — the row is `
              + `${row.join(" · ")}`);
          }
        }
      }

      for (const table of rendered.tables) if (table.tag) taggedTables.add(table.tag);
      // Gate 11: the five the engine answers now, asked rather than remembered.
      drivenBy(step, rendered, state, `${slug} ${step.label}`);

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
        const strokes = [...svg.matchAll(/<line\b[^>]*>/g)].map((mark) => {
          const at = /x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/.exec(mark);
          return at
            ? { ends: [[+at[1], +at[2]], [+at[3], +at[4]]],
              leaderFor: (/data-leader="([^"]*)"/.exec(mark) || [])[1] }
            : null;
        }).filter(Boolean);
        // With the radius, and with the clearance the placement claims to keep. The test used to
        // ask whether a dot's CENTRE was inside the label's box, so a name overlapping a circle's
        // ink by nine pixels passed — 45 of them across the pages.
        const marks = [...svg.matchAll(/<circle[^>]*cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"/g)]
          .map((found) => ({ at: [+found[1], +found[2]], r: +found[3] }));
        const boxes = [];
        for (const found of svg.matchAll(/<text([^>]*)>([^<]*)<\/text>/g)) {
          const at = /x="([-\d.]+)" y="([-\d.]+)"/.exec(found[1]);
          const size = /font-size="([\d.]+)"/.exec(found[1]);
          if (!at || !size || !found[2].trim()) continue;
          const box = textBox(+at[1], +at[2], found[2], +size[1]);
          // A leader is drawn TO its own label, so that one stroke may reach it; every other must
          // not.
          const mine = found[2].trim().split(" ")[0];
          if (strokes.some((stroke) => stroke.leaderFor !== mine
            && boxMeetsSegment(box, stroke.ends[0], stroke.ends[1]))) {
            fail(`${slug} ${step.label}: the label "${found[2]}" is drawn across a stroke`);
          }
          // `boxMeetsDot` is imported rather than reimplemented, so the standard the placement
          // keeps and the standard the check enforces are one function.
          const touching = marks.filter((dot) => boxMeetsDot(box, [...dot.at, dot.r]));
          if (touching.length) {
            fail(`${slug} ${step.label}: the label "${found[2]}" overlaps the ink of a dot`);
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
            const gap = Math.max(Math.max(a.x0 - b.x1, b.x0 - a.x1),
              Math.max(a.y0 - b.y1, b.y0 - a.y1));
            if (gap < tightest) {
              tightest = gap;
              tightestAt = `${slug} ${step.label}: "${a.text}" and "${b.text}"`;
            }
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
      // c1 · every class the drawing emits has a painting rule in the still's stylesheet.
      //
      // SVG's default is `stroke: none`, so a mark whose class the inlined stylesheet does not
      // mention is **invisible in the downloaded file** while looking right on screen, where the
      // page's own CSS paints it. That is exactly what happened to the leader: the one mark whose
      // job is to say which label belongs to what did not render in a single still. And a still is
      // the artefact meant to end up in a chapter, so it is the worst place for a mark to vanish.
      for (const found of rendered.drawing.matchAll(/class="([^"]+)"/g)) {
        for (const name of found[1].split(/\s+/)) {
          if (!name || name === "strong") continue;
          if (!SVG_STILL_STYLE_TEXT.includes(`.${name}`)) {
            fail(`${slug} ${step.label}: the drawing emits class "${name}" and the still's `
              + `stylesheet has no rule mentioning it — in the downloaded file that mark is `
              + `painted by nothing`);
          }
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
  const furnitureCount = [...furniture].reduce((total, text) => total + wordsOf(text), 0);
  report.push({ slug, steps: joined.steps.length, beats: chapter.sections.length, words: count,
    furniture: furnitureCount });
}

// ── 11 (part) · every one of the five was actually asked ─────────────────────────────────────────
//
// The other three ways a step can look driven without being driven: an answer copied out of the
// vendored payload, an answer left as a sentence, or the right entry point asked about the wrong
// object. None of them shows up as a wrong number. All three show up here, because the engine door
// remembers every question the pages put to it, and this is the list of the ones they owe.
//
// Asked **per step**, on an engine door of its own. A door shared between steps would let one of
// them coast on another's question — two of these steps ask the same entry point about the same
// world — and a door already warm from the run above answers out of its cache without recording
// anything. So each driven step is rebuilt against a fresh engine, rendered in every state, and
// the questions that door was put are the questions that step asked.
for (const [anchor, spec] of Object.entries(DRIVEN)) {
  const door = new Engine(glue, payload, rows);
  const built = chapterSteps(door, drawings(door));
  let found = null;
  for (const build of Object.values(built)) {
    for (const step of build()) {
      if (step.anchors.includes(anchor)) found = step;
    }
  }
  if (!found) {
    fail(`no step covers "${anchor}", and it is one of the five the engine was extended for`);
    continue;
  }
  for (const state of statesOf(found, view)) {
    try { found.render(state); } catch { /* the render gate above reports a throw */ }
  }

  // Does the step READ the answer? For a question whose answer is the same in every state — two
  // dots close nothing, a shape's ceiling does not move — comparing the cells against the engine
  // cannot tell a page that asked from a page written to agree. So the same step is built against
  // a door that answers differently, and the tables this gate names must say something else. A
  // reviewer typed the two-dot answer into the cell with the engine call left above it, and every
  // other leg of this gate passed it.
  for (const probe of spec.reads || []) {
    const deaf = new Engine(glue, payload, rows);
    const honest = new Engine(glue, payload, rows);
    const ask = deaf.ask.bind(deaf);
    deaf.ask = (entry, ...args) => {
      const answer = ask(entry, ...args);
      return entry === spec.asks[0] ? probe.change(answer) : answer;
    };
    const stepOf = (which) => {
      for (const build of Object.values(chapterSteps(which, drawings(which)))) {
        for (const step of build()) if (step.anchors.includes(anchor)) return step;
      }
      return null;
    };
    const cellsOf = (step, state) => {
      try {
        const shown = step.render(state);
        const table = shown.tables.find((one) => one.tag === probe.tag);
        return table ? probe.cells.map(([row, at]) =>
          String((table.rows[row] || [])[at])) : null;
      } catch { return null; }
    };
    const deafStep = stepOf(deaf);
    const honestStep = stepOf(honest);
    // Per cell: every cell this probe names must move when the field it comes off moves. The
    // whole-table version of this passed a typed verdict word sitting beside an honest neighbour,
    // because the neighbour moved and the table with it.
    const moved = probe.cells.map(() => false);
    for (const state of statesOf(honestStep, view)) {
      const one = cellsOf(honestStep, state);
      const other = cellsOf(deafStep, state);
      if (one === null || other === null) continue;
      one.forEach((cell, index) => { if (cell !== other[index]) moved[index] = true; });
    }
    moved.forEach((noticed, index) => {
      if (noticed) return;
      const [row, at] = probe.cells[index];
      fail(`the step for "${anchor}" prints the same cell at row ${row}, column ${at} of `
        + `"${probe.tag}" in every state whether or not ${spec.asks[0]} answers differently. The `
        + `engine may be being asked and that cell written to agree with it: a value that is the `
        + `same in every state cannot be told from a typed one any other way`);
    });
    if (moved.every(Boolean)) ran(anchor, "the answer is read, not agreed with");
  }

  if (!wasAsked(questionsAsked(door), spec.asks)) {
    fail(`the step for "${anchor}" never asked ${spec.asks[0]} with ${spec.asks.slice(1).join(", ")}, `
      + `and that question is what it is for. An answer that reaches the page without the engine `
      + `being asked is an answer somebody wrote down — and the same entry point asked a different `
      + `question is the same defect wearing the right name`);
  }
}

// Every tag a page puts on a table is claimed by a spec here. Deleting an entry from DRIVEN is
// otherwise silent — the tables it held simply stop being held — and while the mutation suite
// notices (the attacks aimed at that step stop turning the check red), the check itself said
// nothing. An orphan tag is a table that thinks it is guarded.
{
  const claimed = new Set(Object.values(DRIVEN).flatMap((spec) =>
    [...Object.keys(spec.tables || {}), ...(spec.walk ? [spec.walk.tag] : []),
      ...(spec.counter ? [spec.counter.tag] : [])]));
  for (const tag of taggedTables) {
    if (!claimed.has(tag)) {
      fail(`a table is tagged "${tag}" and no step in this gate's own list claims it. A tag is how `
        + `this gate finds a table; one nothing claims is a table that looks guarded and is not`);
    }
  }
}

// And every leg of this gate fired. All five of them failed OPEN in the first version — a value
// this gate did not speak for, a `null` cell that disarmed a comparison, a state the enumerator
// never drove — and a guard that stops applying looks exactly like a guard that passes.
for (const [leg, count] of legsRan) {
  if (count === 0) {
    fail(`gate 11's leg "${leg}" never ran on any state of any step. A leg that fires on nothing `
      + `is switched off, whether that was done to the check, to the step, or to the enumerator `
      + `that drives it`);
  }
}

// ── 9b (part) · DEMOS.md's folded pairs are the folds ─────────────────────────────────────────────

{
  const listed = [...docFolds].sort().join(", ");
  const actual = [...actualFolds].sort().join(", ");
  if (listed !== actual) {
    fail(`DEMOS.md lists the folded pairs as [${listed}] and the pages fold [${actual}]`);
  }
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
    + `beats, ${line.words} words against the budget and ${line.furniture} more in captions and `
    + `headings, which it does not count\n`);
}

// Before the verdict, and on both sides of it: a red run is exactly the run whose coverage
// `attacks.mjs` is measuring, so this cannot sit after the exit.
printFailSites();

if (failures.length) {
  for (const failure of failures) process.stderr.write(`${failure}\n`);
  process.exit(1);
}

const totalWords = report.reduce((total, line) => Math.max(total, line.words), 0);
const totalSteps = report.reduce((total, line) => total + line.steps, 0);
process.stdout.write(
  `core.test.mjs: the narrowest gap between two labels anywhere is `
  + `${tightest.toFixed(2)}px against a ${LABEL_GAP}px rule — ${tightestAt}\n`,
);
process.stdout.write(
  `core.test.mjs: ${report.length} chapters, ${totalSteps} steps, every rendered number the `
  + `engine's, no digit typed, ${engine.calls.length} engine calls, the wireframe's `
  + `${payload.stella.lines} strokes the census's, ${sums} printed sums that add up, `
  + `${runningSums} running sums that build, `
  + `${stills} stills standing on their own, at most ${totalWords} words on a page\n`,
);
