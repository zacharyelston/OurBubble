// The mutations, one per guard — so that "the check catches this" is a thing the repository runs
// rather than a thing a commit message says.
//
// FIREWALL: these pages run a toy DEC lattice. Nothing here is a claim about nature. See
// ../FIREWALL.md.
//
//   node demos/attacks.mjs
//
// **Standing rule (2026-09-03): no new guard lands without its mutation here, in the same commit.**
// Five rounds running, a guard written to close a hole was found on the next read to have a hole of
// its own — a census that checked identity and not geometry, a sum check keyed to a word, a
// paragraph rule whose window excluded the very figures it was written for, a dot test measuring
// centres instead of ink, a step enumerator that never typed anything. Every one of those was
// "tested" by an attack run once in a shell and thrown away. An attack you cannot re-run is a claim,
// not a test.
//
// How it works: each entry names a file, a needle, its replacement, and the phrase the check must
// produce. The mutation is applied, `core.test.mjs` is run, the output is required to contain that
// phrase, and the file is restored — from a copy taken before anything is touched, so an interrupted
// run cannot leave the tree dirty. A mutation whose needle is not found fails too: that is how a
// refactor tells you an attack has gone stale instead of quietly passing.

import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";

const HERE = path.dirname(new URL(import.meta.url).pathname);

/** Every guard, and the smallest change that should make it complain. */
export const ATTACKS = [
  // ── gate 2: every rendered number is the engine's ────────────────────────────────────────────
  { guard: "gate 2 · a number computed in JavaScript", file: "steps.mjs",
    from: "[[corners[0], show(state.numbers[0])]]",
    to: "[[corners[0], String(state.numbers.length + 998)]]",
    expect: "the engine did not produce it" },
  { guard: "gate 2 · a number in a drawing's title", file: "steps.mjs",
    from: 'title: "The two tetrahedra, threaded",',
    to: 'title: "The two tetrahedra (777)",',
    expect: "the engine did not produce it" },

  // ── gate 3: no number was typed ──────────────────────────────────────────────────────────────
  { guard: "gate 3 · a digit in a caption", file: "steps.mjs",
    from: 'table("the corners", ', to: 'table("the 7 corners", ',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a digit in a column heading", file: "steps.mjs",
    from: '["dot", "number"]', to: '["dot", "number of 8"]',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a beat number typed into a step", file: "steps.mjs",
    from: 'act: "Turn it."', to: 'act: "Turn it. (beat 45)"',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a digit in a drawing's own words", file: "draw.mjs",
    from: "An orthographic wireframe of two", to: "An orthographic wireframe of 3",
    expect: "carry a digit" },

  // ── gate 4: every drawing is its own census ──────────────────────────────────────────────────
  { guard: "gate 4 · a stroke naming an edge the engine has not got", file: "draw.mjs",
    from: 'data-edge="${esc(names[i])}|${esc(names[j])}"', to: 'data-edge="A|B"',
    expect: "which the engine's census has not got" },
  { guard: "gate 4 · every wire line pointed at the wrong dot", file: "draw.mjs",
    from: 'x2="${d2(at[j][0])}" y2="${d2(at[j][1])}"',
    to: 'x2="${d2(at[(j + 1) % at.length][0])}" y2="${d2(at[(j + 1) % at.length][1])}"',
    expect: "and drew" },
  { guard: "gate 4 · the ring's strokes halved, identities honest", file: "draw.mjs",
    from: 'data-line="${esc(a)}|${esc(b)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"',
    to: 'data-line="${esc(a)}|${esc(b)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2((x1 + x2) / 2)}" y2="${d2((y1 + y2) / 2)}"',
    expect: "do not meet anywhere" },
  { guard: "gate 4 · the net's strokes halved", file: "draw.mjs",
    from: 'data-panel="${esc(segment.panel)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"',
    to: 'data-panel="${esc(segment.panel)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2((x1 + x2) / 2)}" y2="${d2((y1 + y2) / 2)}"',
    expect: "do not meet anywhere" },
  { guard: "gate 4 · a stray stroke the drawing does not name", file: "draw.mjs",
    from: "    if (midpoints) {",
    to: '    body.push(`    <line x1="5" y1="5" x2="40" y2="40"/>`);\n    if (midpoints) {',
    expect: "does not say what it is" },
  { guard: "gate 4 · a stroke drawn as a polygon", file: "draw.mjs",
    from: "    if (midpoints) {",
    to: '    body.push(`    <polygon data-region="ABC" points="5,5 60,60"/>`);\n    if (midpoints) {',
    expect: "a region has three" },
  { guard: "gate 4 · a region at coordinates the object has not got", file: "draw.mjs",
    from: "    if (midpoints) {",
    to: '    body.push(`    <polygon data-region="ABC" points="5,5 60,60 5,60"/>`);\n    if (midpoints) {',
    expect: "where no stroke of the object ends" },
  { guard: "gate 4 · a mark of a kind the drawing may not emit", file: "draw.mjs",
    from: "    body.push('  <g class=\"absent\">');",
    to: '    body.push(`    <polyline points="0,0 9,9"/>`);\n    body.push(\'  <g class="absent">\');',
    expect: "may only emit" },
  { guard: "gate 4 · the ring drawing four of its six dots", file: "draw.mjs",
    from: "    for (const name of MID) {\n      const [x, y] = place(at[name]);",
    to: "    for (const name of MID.slice(0, 4)) {\n      const [x, y] = place(at[name]);",
    expect: "and this convention draws all" },
  { guard: "gate 4 · lines to a tip with no dot at the end of them", file: "draw.mjs",
    from: "    for (const index of shown) {\n      const [x, y] = place(places[index].at);",
    to: "    for (const index of shown.slice(1)) {\n      const [x, y] = place(places[index].at);",
    expect: "and no dot there" },

  // ── gate 4's position half ───────────────────────────────────────────────────────────────────
  { guard: "position · the net mirrored, every mark together", file: "draw.mjs",
    from: "    (point[0] - frame.xMin + frame.pad) * NET_SCALE,",
    to: "    (frame.width - frame.pad - (point[0] - frame.xMin)) * NET_SCALE,",
    expect: "MIRRORED" },
  { guard: "position · the net flipped top to bottom", file: "draw.mjs",
    from: "    (frame.yMax + frame.pad - point[1] * SQRT3) * NET_SCALE,",
    to: "    (frame.pad + point[1] * SQRT3) * NET_SCALE,",
    expect: "FLIPPED" },
  { guard: "position · the net stretched on one axis", file: "draw.mjs",
    from: "    (point[0] - frame.xMin + frame.pad) * NET_SCALE,",
    to: "    (point[0] - frame.xMin + frame.pad) * NET_SCALE * 1.4,",
    expect: "stretched" },
  { guard: "position · the wireframe's vertical flipped", file: "draw.mjs",
    from: "    -(sy * sp * x + cp * y + cy * sp * z),",
    to: "    (sy * sp * x + cp * y + cy * sp * z),",
    expect: "stretched" },
  { guard: "ring · the inner dots off their partners' rays", file: "draw.mjs",
    from: "      at[opposite[name]] = [-RING_INNER * Math.cos(theta), RING_INNER * Math.sin(theta)];",
    to: "      const off = theta + (20 * Math.PI) / 180;\n      at[opposite[name]] = [-RING_INNER * Math.cos(off), RING_INNER * Math.sin(off)];",
    expect: "through the centre" },
  { guard: "ring · the three outer radii made unequal", file: "draw.mjs",
    from: "      at[name] = [RING_OUTER * Math.cos(theta), -RING_OUTER * Math.sin(theta)];",
    to: '      const R = RING_OUTER + (name === "AB" ? -20 : 0);\n      at[name] = [R * Math.cos(theta), -R * Math.sin(theta)];',
    expect: "two circles" },
  { guard: "ring · the whole ring rotated", file: "draw.mjs",
    from: "      const theta = (RING_ANGLES[name] * Math.PI) / 180;",
    to: "      const theta = ((RING_ANGLES[name] + 12) * Math.PI) / 180;",
    expect: "straight above" },

  // ── gate 5: the steps are the outline's ──────────────────────────────────────────────────────
  { guard: "gate 5 · a step dropping a chapter section", file: "steps.mjs",
    from: 'anchors: ["the-surprise", "what-the-machine-is-handed-and-what-comes-back"]',
    to: 'anchors: ["the-surprise"]',
    expect: "no step covers" },

  // ── gate 7: a table says what its numbers mean ───────────────────────────────────────────────
  { guard: "gate 7 · a total that is not its terms", file: "steps.mjs",
    from: '[[walkTerms(edges).map(signed).join("  "), show(loop)]], { total: 1 })',
    to: '[[edges.map(signed).join("  "), show(loop)]], { total: 1 })',
    expect: "and they do not" },
  { guard: "gate 7 · a wrong total reachable only by typing", file: "steps.mjs",
    from: "                  show(inside.loops[0])]], { total: 1 }),",
    to: "                  show(state.numbers[3] === arrows[3] ? inside.loops[0] : loops.loops[0])]],\n                { total: 1 }),",
    expect: "and they do not" },
  { guard: "gate 7 · a total-shaped caption over a column", file: "steps.mjs",
    from: 'table("the corners", ["dot", "number"],',
    to: 'table("the corners, summed", ["dot", "number"],',
    expect: "captioned as a total" },
  { guard: "gate 7 · a total in the first column", file: "steps.mjs",
    from: 'table("the corners", ["dot", "number"],',
    to: 'table("the corners", ["added up", "number"],',
    expect: "where nothing precedes it" },

  // ── gate 8: nothing is struck through, nothing touches ───────────────────────────────────────
  { guard: "gate 8 · the label gap lowered", file: "draw.mjs",
    from: "export const LABEL_GAP = 3;", to: "export const LABEL_GAP = 1;",
    expect: "will not go below" },
  { guard: "gate 8 · the clearance from a label's own dot lowered", file: "draw.mjs",
    from: "export const DOT_CLEARANCE = 17;", to: "export const DOT_CLEARANCE = 2;",
    expect: "will not go below" },
  { guard: "gate 8 · a name parked nearer a stranger's dot", file: "draw.mjs",
    from: "  const nearest = placeClear(anchor, ray, text, size, obstacles, taken, from, anchor);",
    to: "  const nearest = null;",
    expect: "needed a leader" },
  { guard: "gate 8 · a leader that does not reach its label", file: "draw.mjs",
    from: 'x2="${d2(dot[0] + (run[0] / length) * stop)}" y2="${d2(dot[1] + (run[1] / length) * stop)}"',
    to: 'x2="${d2(dot[0] - (run[0] / length) * stop)}" y2="${d2(dot[1] - (run[1] / length) * stop)}"',
    expect: "from the label it names" },
  { guard: "gate 8 · a class the still's stylesheet does not paint", file: "draw.mjs",
    from: 'body.push(\'  <g class="dots">\');',
    to: 'body.push(\'  <g class="dots unpainted">\');',
    expect: "painted by nothing" },

  // ── gate 9: the sweep figures are the sweep's ────────────────────────────────────────────────
  { guard: "gate 9 · a figure in the prose the sweep does not assert", file: "DEMOS.md",
    from: "**12** of the directions", to: "**37** of the directions",
    expect: "which SWEEP does not" },
  { guard: "gate 9 · an unemphasised figure smuggled in", file: "DEMOS.md",
    from: "It opens at", to: "It opens at, after 4242 tries,",
    expect: "which SWEEP does not" },
  { guard: "gate 9 · the opening view's own yaw falsified", file: "DEMOS.md",
    from: "yaw 5.585", to: "yaw 5.999",
    expect: "which SWEEP does not" },

  // ── the engine itself ────────────────────────────────────────────────────────────────────────
  // The engine's hashes are `check_edition.py`'s business, not this file's. What THIS check owns is
  // that the two vendored artifacts are one engine, so the mutation is aimed at that.
  { guard: "gate 1 · the vendored JSON edited away from the wasm", file: "../engine/napkin.json",
    from: '"-1",\n            "1",\n            "-1",\n            "1"',
    to: '"-1",\n            "1",\n            "-1",\n            "9"',
    expect: "disagree about the census" },
];

const CHECK = path.join(HERE, "core.test.mjs");

function run() {
  try {
    return execFileSync(process.execPath, [CHECK], { encoding: "utf8", stdio: "pipe" });
  } catch (failure) {
    return `${failure.stdout || ""}${failure.stderr || ""}`;
  }
}

const touched = [...new Set(ATTACKS.map((attack) => attack.file))];
const saved = new Map(touched.map((file) => {
  const at = path.join(HERE, file);
  return [file, { at, was: readFileSync(at, "utf8") }];
}));
const restore = () => { for (const { at, was } of saved.values()) writeFileSync(at, was); };
process.on("exit", restore);

let red = 0;
const failures = [];
for (const attack of ATTACKS) {
  const { at, was } = saved.get(attack.file);
  if (!was.includes(attack.from)) {
    failures.push(`${attack.guard}: its needle is not in ${attack.file} any more — the attack has `
      + `gone stale, and a stale attack passes without testing anything`);
    continue;
  }
  writeFileSync(at, was.replace(attack.from, attack.to));
  const output = run();
  writeFileSync(at, was);
  if (output.includes(attack.expect)) red += 1;
  else {
    failures.push(`${attack.guard}: the check did NOT complain of "${attack.expect}". Either the `
      + `guard has a hole or the mutation no longer produces the defect — find out which`);
  }
}

restore();
process.stdout.write(`attacks.mjs: ${red} of ${ATTACKS.length} mutations turned the check red\n`);
if (failures.length) {
  for (const failure of failures) process.stderr.write(`${failure}\n`);
  process.exit(1);
}
