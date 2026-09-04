// The mutations, one per guard — so that "the check catches this" is a thing the repository runs
// rather than a thing a commit message says.
//
// FIREWALL: these pages run a toy DEC lattice. Nothing here is a claim about nature. See
// ../FIREWALL.md.
//
//   node demos/attacks.mjs                 · run every mutation
//   node demos/attacks.mjs --baseline      · rewrite attacks.baseline.json from a green run
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
// produce. Per mutation, `demos/` and `engine/` are copied into a fresh directory under the
// system's temp directory, the mutation is applied **to the copy**, `core.test.mjs` is run from the
// copy, its output is required to contain that phrase, and the copy is deleted. A mutation whose
// needle is not found fails too: that is how a refactor tells you an attack has gone stale instead
// of quietly passing. So does a needle that occurs more than once — an ambiguous needle mutates
// whichever copy comes first, which is not a test of anything in particular.
//
// **Nothing here writes to the working tree.** The previous version did: it edited the real
// `demos/` and `engine/` — hash-pinned `engine/napkin.json` included — and restored them afterwards
// from an in-memory copy, with the restore hung on `process.on("exit")`. Two readers made the same
// finding: the whole loop is synchronous, so a killed run has no opportunity to run that handler,
// and it exits with the tree mutated. Worse than dirty, invisibly dirty — a mutation of a vendored
// artifact can look like a legitimate re-export. A suite whose job is to prove the checks bite must
// not be the thing that corrupts what they check. So it refuses to start on a dirty `demos/` or
// `engine/`, mutates only copies, and asks git afterwards whether it kept its word. The worst a
// killed run can now leave behind is a directory under the system temp directory.
//
// And the coverage, which is the number that says how much of this is real: every place in
// `core.test.mjs` that can complain is enumerated from its own source, and counting mutations says
// nothing about how many of them any mutation reaches. The first census found about a third — with
// a label drawn across a stroke and a label on a dot's ink, two of the three most important guards
// on the most visual pages, in the unreached majority. Every run now reports the sites it reached,
// `attacks.baseline.json` records the split, and a run that reaches fewer than the baseline's floor
// fails. As it stands every site has a mutation, which is the standing rule arriving at its own
// conclusion: a guard nothing has made fire is a guard nobody has tested. Two of them earned their
// place by finding holes rather than demonstrating guards — a wireframe drawing no dots crashed the
// check instead of failing it, and a net stroke left out entirely passed everything, because the
// count rule iterated the drawing's marks and a name drawn nowhere is not among them.

import { cpSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { pathToFileURL } from "node:url";
import os from "node:os";
import path from "node:path";

const HERE = path.dirname(new URL(import.meta.url).pathname);
const ROOT = path.join(HERE, "..");
const BASELINE_AT = path.join(HERE, "attacks.baseline.json");

// The net's own middle mark, quoted once.
const MID_CIRCLE = '        body.push(`    <circle data-middle="${esc(segment.line)}" cx="${d2(x)}" '
  + 'cy="${d2(y)}" r="9"/>`);';

// The net's own arrowhead, quoted once: two attacks below aim at this line.
const ARROW = '        body.push(`    <polygon class="head" data-walk="${esc(lineName([a, b]))}" '
  + 'points="${d2(tipX)},${d2(tipY)} ${d2(baseX - uy * 9)},${d2(baseY + ux * 9)} '
  + '${d2(baseX + uy * 9)},${d2(baseY - ux * 9)}"/>`);';

// The wireframe's own dot, quoted once: four attacks below aim at this one line, and a needle
// repeated four times by hand is a needle that goes stale in three places.
const WIRE_CIRCLE = '      body.push(`    <circle class="${middle ? "middle" : "tip"}${strong.has(name) '
  + '? " strong" : ""}" data-dot="${esc(name)}" cx="${d2(at[index][0])}" cy="${d2(at[index][1])}" '
  + 'r="${middle ? 7 : 6}"/>`);';

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
    from: 'const cornerTable = (values) => table("the corners", ["dot", "number"],',
    to: 'const cornerTable = (values) => table("the 7 corners", ["dot", "number"],',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a digit in a column heading", file: "steps.mjs",
    from: 'const cornerTable = (values) => table("the corners", ["dot", "number"],',
    to: 'const cornerTable = (values) => table("the corners", ["dot", "number of 8"],',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a beat number typed into a step", file: "steps.mjs",
    from: 'act: "Turn it."', to: 'act: "Turn it. (beat 45)"',
    expect: "types a digit into the string" },
  { guard: "gate 3 · a digit in a drawing's own words", file: "draw.mjs",
    from: "An orthographic wireframe of two", to: "An orthographic wireframe of 3",
    expect: "carry a digit" },
  { guard: "gate 3 · a digit typed into a page's own HTML", file: "two-dots-and-a-line.html",
    from: '<blockquote class="scope">',
    to: '<blockquote class="scope">\n  <p>Step 4 of 9.</p>',
    expect: "has a digit in its own text" },

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

  // ── gate 4b: the wireframe's own counts, which a reader is invited to check by counting ───────
  { guard: "gate 4b · the wireframe one dot short of the census", file: "draw.mjs",
    from: "      if (!drawnDots.has(index)) return;\n      const middle = index < stella.middles;",
    to: "      if (!drawnDots.has(index) || index === 1) return;\n      const middle = index < stella.middles;",
    expect: "dots; the engine has" },
  { guard: "gate 4b · the wireframe one stroke short of the census", file: "draw.mjs",
    from: "        if (family[index] !== kind) return;",
    to: "        if (family[index] !== kind || index === 0) return;",
    expect: "strokes; the engine has" },

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
  // The wireframe's vertical negated is not a view of anything: it is P(yaw, pitch + π), which the
  // search's pitch range excludes, so no view in the sweep fits the drawing and the fit reports the
  // distortion it can measure — the scales. This entry used to be called "the wireframe's vertical
  // flipped" while expecting the word "stretched", which vouched for the FLIPPED verdict on the
  // strength of a different message. It is named for what it demonstrates now, and the FLIPPED
  // verdict has its own entry above, on the net, where the vertical is a fixed convention.
  { guard: "position · the wireframe's vertical negated, matching no view in the sweep",
    file: "draw.mjs",
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

  // ── the mirror-and-flip reasoning itself ─────────────────────────────────────────────────────
  // The wireframe's exemption for a mirrored view and its refusal of a flipped one rest on two
  // facts, and both are now checked rather than asserted. These two mutations are aimed at the
  // check's own arithmetic, which is the only place those facts live.
  { guard: "mirror · the swept pitch range widened past a half turn", file: "core.test.mjs",
    from: "const PITCH_SPAN = Math.PI;", to: "const PITCH_SPAN = Math.PI * 2;",
    expect: "flip guard requires exactly" },
  // A term in the horizontal that does not turn with the yaw is exactly what breaks the identity:
  // the mirror is the view half a turn away only because half a turn negates the horizontal.
  // (Merely flipping a sign in the formula does not break it — both sides of the identity move
  // together — which is worth knowing about this guard: it holds the projection to a symmetry, not
  // to a particular arithmetic.)
  { guard: "mirror · a projection term that does not turn with the yaw", file: "core.test.mjs",
    from: "  return [cy * x - sy * z, -(sy * sp * x + cp * y + cy * sp * z)];",
    to: "  return [cy * x - sy * z + x / 2, -(sy * sp * x + cp * y + cy * sp * z)];",
    expect: "mirroring a view's horizontal is supposed to BE" },

  // ── gate 5: the steps are the outline's ──────────────────────────────────────────────────────
  { guard: "gate 5 · a step dropping a chapter section", file: "steps.mjs",
    from: 'anchors: ["the-surprise", "what-the-machine-is-handed-and-what-comes-back"]',
    to: 'anchors: ["the-surprise"]',
    expect: "no step covers" },
  { guard: "gate 5 · a step with no table of its own", file: "steps.mjs",
    from: "          tables: [\n            table(\"this world\", [\"what\", \"how many\"], censusRows(1)),\n"
      + "            table(\"the number on it\", [\"dot\", \"number\"], [[corners[0], show(state.numbers[0])]]),\n          ],",
    to: "          tables: [],",
    expect: "a step with no table" },
  { guard: "gate 5 · a step with no drawing of its own", file: "steps.mjs",
    from: "          drawing: draw.drawTriangle({\n            dots: 1, showLine: false, "
      + "values: { [corners[0]]: show(state.numbers[0]) },\n"
      + "            title: \"One dot, holding one number\",\n          }),",
    to: '          drawing: "",',
    expect: "a step with no drawing" },

  // ── gate 6: the word budget ──────────────────────────────────────────────────────────────────
  { guard: "gate 6 · a page talked over its word budget", file: "steps.mjs",
    from: '        act: "Put a number on the dot.",',
    to: '        act: "Put a number on the dot." + " and another word".repeat(200),',
    expect: "reader-facing words, and the budget is" },

  // ── gate 7: a table says what its numbers mean ───────────────────────────────────────────────
  { guard: "gate 7 · a total that is not its terms", file: "steps.mjs",
    from: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),',
    to: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[edges.map(signed).join("  "), show(walk.sum)]], { total: 1 }),',
    expect: "and they do not" },
  { guard: "gate 7 · a wrong total reachable only by typing", file: "steps.mjs",
    from: '                [[inside.terms.map(signed).join("  "), show(inside.sum)]], { total: 1 }),',
    to: '                [[inside.terms.map(signed).join("  "),\n'
      + '                  show(state.numbers[3] === arrows[3] ? inside.sum : loops.loops[0])]],\n'
      + '                { total: 1 }),',
    expect: "and they do not" },
  { guard: "gate 7 · a total-shaped caption over a column", file: "steps.mjs",
    from: 'const cornerTable = (values) => table("the corners", ["dot", "number"],',
    to: 'const cornerTable = (values) => table("the corners, summed", ["dot", "number"],',
    expect: "captioned as a total" },
  { guard: "gate 7 · a total in the first column", file: "steps.mjs",
    from: 'const cornerTable = (values) => table("the corners", ["dot", "number"],',
    to: 'const cornerTable = (values) => table("the corners", ["added up", "number"],',
    expect: "where nothing precedes it" },

  { guard: "gate 7 · a table of several numbers that declares nothing", file: "steps.mjs",
    from: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),',
    to: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[walk.terms.map(signed).join("  "), show(walk.sum)]]),',
    expect: "does not say whether the last is their total" },
  { guard: "gate 7 · a table declaring its first column the total", file: "steps.mjs",
    from: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),',
    to: '              table("what the whole walk comes to", ["the three terms, as the walk uses them",\n'
      + '                "added up"],\n'
      + '                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 0 }),',
    expect: "declares column 0 as its total" },

  // ── gate 8: nothing is struck through, nothing touches ───────────────────────────────────────
  //
  // The three label rules — a label across a stroke, a label on a dot's ink, two labels touching —
  // had **no mutation at all** until a coverage census said so, on the two most visual pages, and
  // they are the guards a reader most directly relies on. Each of the four tests in the placement's
  // one candidate filter is dropped here in turn, and each has to produce its own complaint.
  { guard: "gate 8 · the stroke test dropped from the label search", file: "draw.mjs",
    from: "  if (obstacles.segments.some(([a, b]) => boxMeetsSegment(box, a, b))) return null;",
    to: "  if (false) return null;",
    expect: "is drawn across a stroke" },
  { guard: "gate 8 · the dot-ink test dropped from the label search", file: "draw.mjs",
    from: "  if (obstacles.dots.some((dot) => boxMeetsDot(box, dot))) return null;",
    to: "  if (false) return null;",
    expect: "overlaps the ink of a dot" },
  { guard: "gate 8 · the label-versus-label test dropped from the label search", file: "draw.mjs",
    from: "  if (taken.some((other) => boxesOverlap(box, other, LABEL_GAP))) return null;",
    to: "  if (false) return null;",
    expect: "px of each other" },
  // A name parked nearer a stranger's dot **without** a leader, which is what the proximity rule is
  // for. The entry that used to claim this forced every label onto the leader path instead, and its
  // needle was the leader cap's message — so the proximity rule could be deleted outright with the
  // suite still green. That entry is below, named for the cap it actually tests.
  { guard: "gate 8 · a name parked nearer a stranger's dot, no leader", file: "draw.mjs",
    from: "  if (owner && obstacles.dots.some((dot) =>\n"
      + "    Math.hypot(dot[0] - x, dot[1] - y) < Math.hypot(owner[0] - x, owner[1] - y) - 0.01)) {\n"
      + "    return null;\n  }",
    to: "  if (false) {\n    return null;\n  }",
    expect: "a name has to be nearest the mark it names" },
  { guard: "gate 8 · the label gap lowered", file: "draw.mjs",
    from: "export const LABEL_GAP = 3;", to: "export const LABEL_GAP = 1;",
    expect: "will not go below" },
  { guard: "gate 8 · the clearance from a label's own dot lowered", file: "draw.mjs",
    from: "export const DOT_CLEARANCE = 17;", to: "export const DOT_CLEARANCE = 2;",
    expect: "will not go below" },
  { guard: "gate 8 · every label forced onto the leader path", file: "draw.mjs",
    from: "  const nearest = placeClear(anchor, ray, text, size, obstacles, taken, from, anchor);",
    to: "  const nearest = null;",
    expect: "needed a leader" },
  { guard: "gate 8 · a leader that does not reach its label", file: "draw.mjs",
    from: 'x2="${d2(dot[0] + (run[0] / length) * stop)}" y2="${d2(dot[1] + (run[1] / length) * stop)}"',
    to: 'x2="${d2(dot[0] - (run[0] / length) * stop)}" y2="${d2(dot[1] - (run[1] / length) * stop)}"',
    expect: "from the label it names" },
  { guard: "gate 8 · a class the still's stylesheet does not paint", file: "draw.mjs",
    from: 'body.push(\'  <g class="dots">\');\n    for (const name of MID) {',
    to: 'body.push(\'  <g class="dots unpainted">\');\n    for (const name of MID) {',
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
  // And the other direction: the sweep itself moved, with the prose left alone. These are the
  // assertions that hold the paragraph's figures to what the shipped code computes — a reader found
  // that nothing had ever made one of them fire.
  { guard: "gate 9 · the opening view chosen by a reversed tie-break", file: "draw.mjs",
    from: "        || (cost.lies === best.lies && cost.nearest > best.nearest)) {",
    to: "        || (cost.lies === best.lies && cost.nearest < best.nearest)) {",
    expect: "the opening view's yaw is" },
  { guard: "gate 9 · the sweep's pitch offset by a hair", file: "draw.mjs",
    from: "      const pitch = (b / VIEW_GRID) * Math.PI - Math.PI / 2;\n      const cost = viewCost(points, edges, yaw, pitch);",
    to: "      const pitch = (b / VIEW_GRID) * Math.PI - Math.PI / 2 + 0.02;\n      const cost = viewCost(points, edges, yaw, pitch);",
    expect: "the opening view's pitch is" },
  { guard: "gate 9 · the score's dot-on-a-line term zeroed", file: "draw.mjs",
    from: "    lies: invented + 4 * hidden + 12 * flattened,",
    to: "    lies: invented + 0 * hidden + 12 * flattened,",
    expect: "the cheapest views are" },
  { guard: "gate 9 · crossings stopped being counted", file: "draw.mjs",
    from: "      if (segmentsCross(flat[a], flat[b], flat[c], flat[d])) invented += 1;",
    to: "      if (segmentsCross(flat[a], flat[b], flat[c], flat[d])) invented += 0;",
    expect: "directions have no crossings" },
  { guard: "gate 9 · the sweep coarsened under the prose", file: "draw.mjs",
    from: "export const VIEW_GRID = 72;", to: "export const VIEW_GRID = 36;",
    expect: "directions per angle and DEMOS.md says" },

  // ── 9b: DEMOS.md's own beat numbers ─────────────────────────────────────────────────────────
  { guard: "gate 9b · a stale beat range in the page table", file: "DEMOS.md",
    from: "| 13–22 |", to: "| 13–23 |",
    expect: "and steps.json derives" },
  { guard: "gate 9b · a page dropped out of the page table", file: "DEMOS.md",
    from: "| [`two-worlds-threaded.html`](two-worlds-threaded.html) | Two worlds threaded | 48–53 | 5 |",
    to: "| Two worlds threaded | 48–53 | 5 |",
    expect: "has no page-table row for" },
  { guard: "gate 9b · a page table row with its beats written out in words", file: "DEMOS.md",
    from: "| [`two-worlds-threaded.html`](two-worlds-threaded.html) | Two worlds threaded | 48–53 | 5 |",
    to: "| [`two-worlds-threaded.html`](two-worlds-threaded.html) | Two worlds threaded | forty-eight to fifty-three | 5 |",
    expect: "states no beat range" },
  { guard: "gate 9b · a beat named by number in the prose", file: "DEMOS.md",
    from: "the poke step's table still said", to: "beat 42's table still said",
    expect: "outside its page table" },
  // A beat number in a sentence that also names a page. The scan used to skip **any** line
  // containing ".html" — the page table's own shape — so the likeliest sentence anyone would write
  // was the one it could not see.
  { guard: "gate 9b · a beat number in a sentence that names a page", file: "DEMOS.md",
    from: "### The renumber that proved the rule, on this file",
    to: "### The renumber that proved the rule, on this file\n\n"
      + "The poke step on two-worlds-threaded.html is beat 99.",
    expect: "outside its page table" },

  // ── gate 10: every still stands on its own ───────────────────────────────────────────────────
  { guard: "gate 10 · a still shipped without the firewall", file: "core.mjs",
    from: "    + `in it is a claim about nature. -->`;",
    to: "    + `in it is a claim about the lattice. -->`;",
    expect: "the still has no the firewall line" },
  { guard: "gate 10 · a still shipped without its own stylesheet", file: "core.mjs",
    from: "    (_match, attributes) => `${stamp}\\n<svg${attributes}>\\n  <style>${SVG_STILL_STYLE_TEXT}</style>`,",
    to: "    (_match, attributes) => `${stamp}\\n<svg${attributes}>`,",
    expect: "the still has no its own stylesheet, inlined" },
  { guard: "gate 10 · a still shipped without a description", file: "draw.mjs",
    from: '<desc>${esc(desc || "An orthographic wireframe',
    to: '<desc-x>${esc(desc || "An orthographic wireframe',
    expect: "the still has no a description" },


  // ── the guards a coverage census found nothing had ever made fire ─────────────────────────────
  //
  // A reviewer gutted eight of these to `if (false)` with every mutation still red and the coverage
  // number unmoved, which is the standing rule's own argument arriving from outside: a guard with no
  // mutation is a guard nobody has tested. These are the ones a reader relies on most — the ring's
  // twelve lines and its no-crossings claim, the wireframe's dot identity, and the wiring between
  // the steps and `steps.json` that catches a renumber the demos have not followed.
  { guard: "gate 4a · the ring drawing eleven of the engine's twelve lines", file: "draw.mjs",
    from: "  const MID_LINES = cut.mid_lines;", to: "  const MID_LINES = cut.mid_lines.slice(1);",
    expect: "and the shape between has" },
  { guard: "gate 4a · the ring's inner circle pushed out until the lines cross", file: "draw.mjs",
    from: "const RING_INNER = 63;", to: "const RING_INNER = 150;",
    expect: "the ring is degenerate" },
  { guard: "gate 4a · the outside face's tip put below the ring instead of above it",
    file: "draw.mjs",
    from: "      if (index === outside) return { at: [0, -TIP_ABOVE], inside: false };",
    to: "      if (index === outside) return { at: [0, TIP_ABOVE], inside: false };",
    expect: "the convention says seven" },
  { guard: "gate 4a · the tips that sit in their own face no longer saying so", file: "draw.mjs",
    from: "      if (radius >= TIP_CLEARANCE) return { at: centre, inside: true };",
    to: "      if (radius >= TIP_CLEARANCE) return { at: centre, inside: false };",
    expect: "the convention says four" },
  { guard: "gate 4b · a wireframe dot under a name the engine has not got", file: "draw.mjs",
    from: WIRE_CIRCLE,
    to: WIRE_CIRCLE.replace('data-dot="${esc(name)}"', 'data-dot="Q${esc(name)}"'),
    expect: "which the engine has not got" },
  { guard: "gate 4b · every wireframe dot drawn twice", file: "draw.mjs",
    from: WIRE_CIRCLE, to: `${WIRE_CIRCLE}
${WIRE_CIRCLE}`,
    expect: "the wireframe drew a dot twice" },
  { guard: "gate 4b · no dot drawn at all under thirty-six strokes", file: "draw.mjs",
    from: WIRE_CIRCLE, to: "      void middle;",
    expect: "and no dots at all" },
  { guard: "gate 4b · a wireframe stroke that does not say which edge it is", file: "draw.mjs",
    from: '<line class="edge${heavy ? " strong" : ""}" data-edge="',
    to: '<line class="edge${heavy ? " strong" : ""}" data-of="',
    expect: "does not say which edge it is" },
  { guard: "gate 8 · a leader pointing at a dot with no label of that name", file: "draw.mjs",
    from: '<line class="leader" data-leader="${esc(name)}"',
    to: '<line class="leader" data-leader="Q${esc(name)}"',
    expect: "and there is no label of that name" },
  { guard: "gate 9 · the crossings paragraph renamed out from under its own gate",
    file: "DEMOS.md",
    from: "**The default view is chosen by counting.**",
    to: "**The default view is chosen by counting:**",
    expect: "no longer has the crossings paragraph" },
  { guard: "gate 5 · a chapter with no demo behind its slug", file: "steps.mjs",
    from: '    "the-shape-between": chapterFour,', to: '    "the-shape-betwen": chapterFour,',
    expect: "there is no demo for the chapter" },
  { guard: "gate 5 · the steps handed back in the wrong order", file: "core.mjs",
    from: "  const joined = steps.map((step) => {",
    to: "  const joined = [...steps].reverse().map((step) => {",
    expect: "the steps claim beats" },
  { guard: "gate 5 · a step's own section text drifting from steps.json", file: "core.mjs",
    from: "      return section;",
    to: "      return { ...section, question: `${section.question} ` };",
    expect: "does not agree with steps.json" },

  { guard: "gate 4 · a mark with an identity and no position", file: "draw.mjs",
    from: "    body.push('  <g class=\"dots\">');\n    names.forEach((name, index) => {",
    to: "    body.push('  <g class=\"dots\">');\n    body.push('    <circle data-dot=\"A\"/>');\n"
      + "    names.forEach((name, index) => {",
    expect: "with no position" },
  { guard: "gate 4 · an arrow marking a walk along a line the drawing has not drawn",
    file: "draw.mjs",
    from: ARROW, to: ARROW.replace('data-walk="${esc(lineName([a, b]))}"', 'data-walk="AZ"'),
    expect: "and does not draw that line" },
  { guard: "gate 4 · an arrowhead off the line it belongs to", file: "draw.mjs",
    from: ARROW, to: ARROW.replace('points="${d2(tipX)},${d2(tipY)}', 'points="${d2(tipX + 40)},${d2(tipY + 40)}'),
    expect: "is not on that line" },
  { guard: "ring · the two lower middles swapped left for right", file: "draw.mjs",
    from: "const RING_ANGLES = { AB: 90, AC: 210, AD: 330 };",
    to: "const RING_ANGLES = { AB: 90, AC: 330, AD: 210 };",
    expect: "to the right of" },

  // This one found a hole rather than demonstrating a guard: a whole stroke of the net left out
  // passed everything, because the count rule iterated the drawing's own marks and a name drawn
  // nowhere is not among them. The check now iterates the engine's list as well.
  { guard: "gate 4 · one of the net's strokes not drawn at all", file: "draw.mjs",
    from: "    for (const segment of segments) {\n      const [x1, y1] = netAt(segment.from);",
    to: "    for (const segment of segments.slice(1)) {\n      const [x1, y1] = netAt(segment.from);",
    expect: "nowhere, and the engine puts it in" },
  { guard: "position · the convention's own coordinates collapsed to a point", file: "draw.mjs",
    from: "        const at = [x, u * SQRT3];", to: "        const at = [0, 0];",
    expect: "gives neither axis any spread" },

  { guard: "gate 4 · a net middle drawn twice over", file: "draw.mjs",
    from: MID_CIRCLE, to: `${MID_CIRCLE}\n${MID_CIRCLE}`,
    expect: "time(s), and the engine puts it in" },

  // ── gate 11: the five the engine answers now, asked rather than remembered ───────────────────
  //
  // Every one of these is a page that looks right. None of them prints a number the engine did not
  // produce, so gate 2 sees nothing; none of them types a digit, so gate 3 sees nothing. They are
  // the shapes the five gaps take once the engine can answer them, and they are why gate 11 exists.
  { guard: "gate 11 · a wrong weight silently accepted by the dial", file: "steps.mjs",
    from: "          const run = engine.sloshWeighted(\"tetrahedron\", tetraCorners, state.numbers, k, ticks);",
    to: "          const run = engine.sloshWeighted(\"tetrahedron\", tetraCorners,\n"
      + "            LINES.map(() => plainWeight), k, ticks);",
    expect: "two different dials" },
  { guard: "gate 11 · a running sum read off the terms instead of the engine", file: "steps.mjs",
    from: "                  signed(walk.terms[index]), show(walk.running[index]),",
    to: "                  signed(walk.terms[index]), show(walk.terms[index]),",
    expect: "and the terms above it come to something else" },
  { guard: "gate 11 · a walk table that does not say which column is its running sum",
    file: "steps.mjs",
    from: '                ]), { runs: [3, 4] }, "walk-running"),',
    to: '                ]), null, "walk-running"),',
    expect: "does not say which of its columns is the walk" },
  { guard: "gate 11 · the tetrahedron's certificate under the triangle's title", file: "steps.mjs",
    from: '          const certificate = engine.certificate("triangle", chosen);',
    to: '          const certificate = engine.certificate("tetrahedron", chosen);',
    expect: "is not the engine's for the triangle" },
  { guard: "gate 11 · a driven step's table with its tag taken off", file: "steps.mjs",
    from: '              runTable("every tick", run.history, run.totals, NAMES, "dial-run"),',
    to: '              runTable("every tick", run.history, run.totals, NAMES),',
    expect: "no table tagged" },
  { guard: "gate 11 · a driven step's anchor renamed out from under the gate", file: "steps.mjs",
    from: '        anchors: ["coming-home-on-eight-faces"],',
    to: '        anchors: ["coming-home-on-eight-face"],',
    expect: "is one of the five the engine was extended for" },
  { guard: "gate 11 · the two-dot answer hard-coded instead of asked", file: "steps.mjs",
    from: "          const closed = engine.loops(TWO_DOTS, [ZERO], 1);",
    to: "          const closed = { closed_walks: 0 };",
    expect: "never asked loops_json about the two-dots" },
  { guard: "gate 11 · the eight-face walk taken from the payload instead of asked", file: "steps.mjs",
    from: '          const fs = engine.faceSum("octahedron", faceArrows);',
    to: "          const fs = { ...P.face_sum, cycle_names: R.gaps.outward_face_sum.cycle_names,\n"
      + "            running: R.gaps.outward_face_sum.running,\n"
      + "            orientation: R.gaps.outward_face_sum.orientation };",
    expect: "never asked face_sum_json about the octahedron" },

  // ── the engine itself ────────────────────────────────────────────────────────────────────────
  // The engine's hashes are `check_edition.py`'s business, not this file's. What THIS check owns is
  // that the two vendored artifacts are one engine, so the mutation is aimed at that. It is also
  // the mutation that made the in-place version unacceptable: a stray edit to a hash-pinned
  // vendored artifact left in the tree does not look like damage, it looks like a re-export.
  { guard: "gate 1 · the vendored JSON edited away from the wasm", file: "../engine/napkin.json",
    from: '"-1",\n            "1",\n            "-1",\n            "1"',
    to: '"-1",\n            "1",\n            "-1",\n            "9"',
    expect: "disagree about the census" },
];

// ── the runner ────────────────────────────────────────────────────────────────────────────────────

/** What git says about the two directories this suite is forbidden to touch. */
function treeState() {
  return execFileSync("git", ["status", "--porcelain", "--", "demos", "engine"],
    { cwd: ROOT, encoding: "utf8" }).trim();
}

const live = new Set();

/** A private copy of `demos/` and `engine/`, which is the only thing a mutation is applied to. */
function copyOfTheTree() {
  const at = mkdtempSync(path.join(os.tmpdir(), "ourbubble-attack-"));
  live.add(at);
  cpSync(path.join(ROOT, "demos"), path.join(at, "demos"), { recursive: true });
  cpSync(path.join(ROOT, "engine"), path.join(at, "engine"), { recursive: true });
  return at;
}

function discard(at) {
  live.delete(at);
  rmSync(at, { recursive: true, force: true });
}

/** Run the cross-check inside one copy, asking it to report which of its fail sites it reached. */
function runCheck(at, census = false) {
  const check = path.join(at, "demos", "core.test.mjs");
  try {
    return execFileSync(process.execPath, [check], {
      encoding: "utf8", stdio: "pipe",
      env: { ...process.env, DEMO_FAIL_SITES: census ? "all" : "1" },
    });
  } catch (failure) {
    return `${failure.stdout || ""}${failure.stderr || ""}`;
  }
}

const sitesIn = (output, what) => [...output.matchAll(new RegExp(`^core\\.test\\.mjs: ${what} (.*)$`, "gm"))]
  .map((found) => found[1]);

/**
 * What a baseline says about a run, as a list of complaints. Pure, and exported, so that every rule
 * in it can be shown to fire — see `SELF_TEST` below.
 *
 * The rules, and what each is for:
 *
 *   · coverage under the floor — the floor is the highest coverage this suite has ever had;
 *   · the floor under the file's own `reached` list — a reviewer walked coverage down by deleting a
 *     mutation, moving its site into `uncovered`, and setting the floor to 0, all three in the file
 *     the run is compared against, and the suite went green. The floor may not sit below what the
 *     baseline itself records as covered, so lowering it means deleting those entries too, one line
 *     each, in a diff that says what was dropped. A file is evidence a reviewer reads, not a lock;
 *     what this buys is that walking coverage down cannot be done quietly;
 *   · `sites` disagreeing with the census — an unread number in a checked-in file is a status
 *     nobody verified;
 *   · a missing floor — the one number a rewrite cannot lower on its own;
 *   · a covered site gone unreached, and a site with no mutation and no entry in the uncovered
 *     list: the standing rule, mechanised;
 *   · and a baseline behind its own run, because a coverage file out of date is one more status
 *     that lies.
 */
export function baselineProblems({ known, reached, covered, uncovered, baseline }) {
  const problems = [];
  const floor = Number.isFinite(baseline.floor) ? baseline.floor : 0;
  const lost = (baseline.reached || []).filter((key) => known.includes(key) && !reached.has(key));
  const grown = uncovered.filter((key) => !(baseline.uncovered || []).includes(key));
  if (covered.length < floor) {
    problems.push(`this run covers ${covered.length} fail site(s) and the baseline's floor is `
      + `${floor}. The floor is the highest coverage this suite has had; it is lowered by hand, `
      + `in a commit, or not at all`);
  }
  if (floor < (baseline.reached || []).length) {
    problems.push(`the baseline's floor is ${floor} and it records `
      + `${(baseline.reached || []).length} covered fail site(s). The floor is not allowed below `
      + `what the file itself says is covered: lower it and the sites it drops come out with it`);
  }
  if (Number.isFinite(baseline.sites) && baseline.sites !== known.length) {
    problems.push(`the baseline says core.test.mjs has ${baseline.sites} fail sites and it has `
      + `${known.length}`);
  }
  if (!Number.isFinite(baseline.floor)) {
    problems.push("the baseline has no coverage floor, and the floor is the one number in it "
      + "that a rewrite cannot lower on its own");
  }
  if (lost.length) {
    problems.push(`${lost.length} fail site(s) the baseline says are covered were not reached by `
      + `any mutation:\n  ${lost.join("\n  ")}`);
  }
  if (uncovered.length) {
    problems.push(`${uncovered.length} fail site(s) have no mutation:\n  `
      + `${uncovered.join("\n  ")}\nEvery site in the check had one when this rule was written, so `
      + `the list being empty is the invariant rather than the aspiration — and walking coverage `
      + `down has to put a site back into it, which is this. A guard that genuinely cannot be `
      + `mutated is a reason to change this rule, in a commit that says which guard and why`);
  }
  if (grown.length) {
    problems.push(`${grown.length} fail site(s) have no mutation and are not in the baseline's `
      + `uncovered list. The standing rule is that a guard lands with the mutation that proves `
      + `it bites; if this one genuinely cannot be mutated, say so by listing it, in the same `
      + `commit:\n  ${grown.join("\n  ")}`);
  }
  const behind = [...new Set([
    ...covered.filter((key) => !(baseline.reached || []).includes(key)),
    ...(baseline.uncovered || []).filter((key) => !uncovered.includes(key)),
    ...(baseline.reached || []).filter((key) => !known.includes(key)),
  ])];
  if (behind.length && !lost.length && !grown.length) {
    problems.push(`the baseline is behind this run at ${behind.length} site(s) — coverage went `
      + `up or a site was renamed. Rewrite it with \`node demos/attacks.mjs --baseline\` in this `
      + `commit, so the file keeps saying something true:\n  ${behind.join("\n  ")}`);
  }
  return problems;
}

/**
 * One case per rule in `baselineProblems`, each a walk-down somebody actually tried.
 *
 * The rest of this file proves the CHECK's guards bite by mutating the modules under it. These
 * rules are in the suite itself, where a mutation of the check cannot reach them — and the standing
 * rule does not care where a guard lives. So each is handed the edit it exists to refuse, and is
 * required to say so.
 */
const SELF_TEST = [
  // Each case sits at the rule's **boundary** — the smallest edit it must refuse — because a case
  // two or eight steps past the boundary lets the rule be relaxed by one and still pass its own
  // test. A reviewer found both of those by weakening every numeric rule by one.
  { case: "a floor one below what the same file records as covered",
    known: ["one", "two"], covered: ["one"], uncovered: ["two"],
    baseline: { sites: 2, floor: 1, reached: ["one", "two"], uncovered: [] },
    say: "not allowed below" },
  { case: "coverage one under the floor",
    known: ["one", "two"], covered: ["one"], uncovered: ["two"],
    baseline: { sites: 2, floor: 2, reached: ["one"], uncovered: ["two"] },
    say: "The floor is the highest coverage" },
  { case: "a covered site no mutation reaches any more",
    known: ["one", "two"], covered: ["two"], uncovered: ["one"],
    baseline: { sites: 2, floor: 1, reached: ["one"], uncovered: ["two"] },
    say: "the baseline says are covered were not reached" },
  { case: "a new fail site with no mutation and no entry",
    known: ["one", "two"], covered: ["one"], uncovered: ["two"],
    baseline: { sites: 2, floor: 1, reached: ["one"], uncovered: [] },
    say: "have no mutation and are not in the baseline's" },
  { case: "the census count edited by one",
    known: ["one"], covered: ["one"], uncovered: [],
    baseline: { sites: 2, floor: 1, reached: ["one"], uncovered: [] },
    say: "fail sites and it has 1" },
  { case: "a baseline with no floor at all",
    known: ["one"], covered: ["one"], uncovered: [],
    baseline: { sites: 1, reached: ["one"], uncovered: [] },
    say: "has no coverage floor" },
  { case: "a baseline behind a run that covers more",
    known: ["one", "two"], covered: ["one", "two"], uncovered: [],
    baseline: { sites: 2, floor: 2, reached: ["one", "two"], uncovered: ["two"] },
    say: "is behind this run" },
  { case: "a site with no mutation at all",
    known: ["one", "two"], covered: ["one"], uncovered: ["two"],
    baseline: { sites: 2, floor: 1, reached: ["one"], uncovered: ["two"] },
    say: "the list being empty is the invariant" },
  { case: "a run that matches its baseline exactly",
    known: ["one", "two"], covered: ["one", "two"], uncovered: [],
    baseline: { sites: 2, floor: 2, reached: ["one", "two"], uncovered: [] },
    say: null },
];

/** Every rule in `baselineProblems` handed the edit it refuses, and required to refuse it. */
function selfTestProblems() {
  const out = [];
  for (const one of SELF_TEST) {
    const said = baselineProblems({
      known: one.known,
      reached: new Set(one.covered),
      covered: one.covered,
      uncovered: one.uncovered,
      baseline: one.baseline,
    });
    if (one.say === null) {
      if (said.length) {
        out.push(`the baseline comparison complains about "${one.case}", which is the case it is `
          + `supposed to pass: ${said.join(" / ")}`);
      }
    } else if (!said.some((problem) => problem.includes(one.say))) {
      out.push(`the baseline comparison does NOT complain of "${one.say}" for "${one.case}" — `
        + `that rule has stopped biting, and a coverage file nothing holds is a status that lies`);
    }
  }
  return out;
}

function main() {
  const argument = process.argv[2];
  if (argument !== undefined && argument !== "--baseline") {
    process.stderr.write(`attacks.mjs: ${argument} is not an option this takes: `
      + `--baseline, or nothing\n`);
    process.exit(2);
  }
  const writeBaseline = argument === "--baseline";

  // Refuse to start on a dirty tree. Not for tidiness: this suite's whole claim is that it does not
  // write to `demos/` or `engine/`, and the only way to CHECK that claim afterwards is for git to
  // have had nothing to say before.
  const before = treeState();
  if (before) {
    process.stderr.write("attacks.mjs: demos/ or engine/ has uncommitted changes, and this suite "
      + "verifies afterwards that it left the tree exactly as it found it — which it cannot do from "
      + "a dirty start. Commit or stash first:\n");
    process.stderr.write(`${before}\n`);
    // 3, not 1: a dirty tree means this suite could not run, which is not the same as a guard
    // having a hole. `check_edition.py` reads that code and reports the line as unverified, so an
    // uncommitted demo edit does not make the rest of tier 0 unrunnable — which is exactly when a
    // reader would be running it.
    process.exit(3);
  }

  // The needle audit, before anything is copied. An attack whose needle is missing tests nothing;
  // an attack whose needle occurs twice mutates whichever comes first, which is a test of something
  // nobody chose.
  const stale = [...selfTestProblems()];
  const source = new Map();
  for (const attack of ATTACKS) {
    const at = path.resolve(HERE, attack.file);
    if (!source.has(at)) source.set(at, readFileSync(at, "utf8"));
    const text = source.get(at);
    const count = text.split(attack.from).length - 1;
    if (count === 0) {
      stale.push(`${attack.guard}: its needle is not in ${attack.file} any more — the attack has `
        + `gone stale, and a stale attack passes without testing anything`);
    } else if (count > 1) {
      stale.push(`${attack.guard}: its needle occurs ${count} times in ${attack.file}, so the `
        + `mutation lands on whichever copy comes first — anchor it on something that occurs once`);
    }
    if (attack.from === attack.to) {
      stale.push(`${attack.guard}: its mutation changes nothing`);
    }
    // A mutation of the check itself may not move the check's own lines, because the fail-site
    // census is enumerated from that file and reported by line.
    if (path.basename(attack.file) === "core.test.mjs"
      && attack.from.split("\n").length !== attack.to.split("\n").length) {
      stale.push(`${attack.guard}: it mutates core.test.mjs and changes its line count, which `
        + `moves every fail site below it`);
    }
  }

  // A guard whose condition is a literal cannot complain, and a coverage census cannot see the
  // difference: a reviewer turned eight uncovered guards into `if (false) {` with every mutation
  // still red and the coverage number unmoved. The site is still there, still enumerated, still
  // listed as uncovered — and dead. So the commonest spellings of it are refused outright, here and
  // in the three modules the check is written against. This is belt and braces, not the defence:
  // the same reviewer gutted four guards in spellings this does not match — `if (0)`,
  // `x !== x`, `&& 0`, `!!0` — and coverage caught all four, four ways over. A regex cannot
  // enumerate the ways to write `false`; a mutation per site does not have to.
  for (const file of ["core.test.mjs", "draw.mjs", "steps.mjs", "core.mjs"]) {
    const text = readFileSync(path.join(HERE, file), "utf8");
    // Aimed at CONDITIONS, not at values: `Math.hypot(...) || 1` is a sensible default and there
    // are several, so the short-circuit halves match the word literals only.
    for (const found of text.matchAll(
      /if \(\s*!*(?:false|true|[01])\s*[)&|]|&&\s*false\b|\|\|\s*true\b|(?<![\w.])([\w.]+)\s*[!=]==\s*\1(?![\w.])/g)) {
      stale.push(`${file} contains "${found[0]}", which is how a guard is turned off without `
        + `removing it: the site stays in the census and stops being able to complain. Delete the `
        + `guard if it is going, and let the diff say so`);
    }
  }

  // One run of the unmutated copy, which does two things: it says the copy is faithful (a green
  // check in it), and it is where the name of every fail site comes from.
  const pristine = copyOfTheTree();
  const first = runCheck(pristine, true);
  const known = sitesIn(first, "fail-site-known");
  const clean = sitesIn(first, "fail-site");
  discard(pristine);
  const problems = [...stale];
  if (!known.length) {
    problems.push("the unmutated copy printed no fail-site census, so coverage cannot be measured "
      + "— has core.test.mjs's DEMO_FAIL_SITES reporting gone?");
  }
  if (clean.length) {
    problems.push(`the unmutated copy is already red at ${clean.length} site(s), so every `
      + `mutation below would be measured against a failing check`);
  }

  let red = 0;
  const reached = new Set();
  for (const attack of ATTACKS) {
    if (stale.some((line) => line.startsWith(`${attack.guard}:`))) continue;
    const at = copyOfTheTree();
    const file = path.resolve(at, "demos", attack.file);
    const was = readFileSync(file, "utf8");
    writeFileSync(file, was.replace(attack.from, attack.to));
    const output = runCheck(at);
    discard(at);
    for (const site of sitesIn(output, "fail-site")) reached.add(site);
    if (output.includes(attack.expect)) red += 1;
    else {
      problems.push(`${attack.guard}: the check did NOT complain of "${attack.expect}". Either the `
        + `guard has a hole or the mutation no longer produces the defect — find out which`);
    }
  }

  // Did it keep its word? The tree is the thing this suite must never be the one to damage.
  const after = treeState();
  if (after) {
    problems.push(`this suite wrote to the working tree, which is the one thing it may not do:\n`
      + `${after}`);
  }

  const covered = known.filter((key) => reached.has(key));
  const uncovered = known.filter((key) => !reached.has(key));
  const strayed = [...reached].filter((key) => !known.includes(key));
  for (const key of strayed) {
    problems.push(`a run reached the fail site \`${key}\`, which the census does not know about — `
      + `a mutation of core.test.mjs has moved its own lines`);
  }

  // What the baseline says, and what this run says. Computed BEFORE the --baseline branch, so
  // rewriting the file has to name what it is dropping rather than dropping it silently.
  let baseline = null;
  try {
    baseline = JSON.parse(readFileSync(BASELINE_AT, "utf8"));
  } catch (failure) {
    if (!writeBaseline) {
      problems.push(`attacks.baseline.json cannot be read (${failure.message}), and it is what `
        + `says whether this run covers as much as the last one did`);
    }
  }
  const lost = baseline
    ? (baseline.reached || []).filter((key) => known.includes(key) && !reached.has(key))
    : [];
  const grown = baseline
    ? uncovered.filter((key) => !(baseline.uncovered || []).includes(key))
    : [];
  // The ratchet. Every other comparison here is against a file in the same commit, so a mutation
  // deleted **and** its site moved into the baseline's uncovered list passes — a reviewer did
  // exactly that. This is the one number `--baseline` may not lower on its own: it keeps the
  // highest coverage the suite has ever had, and lowering it is a deliberate one-line diff with a
  // reviewer looking at it.
  const floor = baseline && Number.isFinite(baseline.floor) ? baseline.floor : 0;

  if (writeBaseline) {
    if (problems.length) {
      for (const problem of problems) process.stderr.write(`${problem}\n`);
      process.stderr.write("attacks.mjs: refusing to write a baseline from a run that is not "
        + "green — the coverage it recorded would not be the coverage the suite has\n");
      process.exit(1);
    }
    for (const key of lost) {
      process.stdout.write(`attacks.mjs: dropping a covered fail site from the baseline — ${key}\n`);
    }
    for (const key of grown) {
      process.stdout.write(`attacks.mjs: recording a fail site with no mutation — ${key}\n`);
    }
    if (covered.length < floor) {
      process.stderr.write(`attacks.mjs: this run covers ${covered.length} fail site(s) and the `
        + `baseline's floor is ${floor}. --baseline does not lower the floor: cover the sites `
        + `again, or lower "floor" by hand in a commit a reviewer can see\n`);
      process.exit(1);
    }
    writeFileSync(BASELINE_AT, `${JSON.stringify({
      note: "Which of core.test.mjs's fail sites the mutations in attacks.mjs reach. Regenerate "
        + "with `node demos/attacks.mjs --baseline`, in the same commit as the guard or the "
        + "mutation that changed it. A run that reaches fewer of them than this fails.",
      sites: known.length,
      floor: Math.max(floor, covered.length),
      reached: covered,
      uncovered,
    }, null, 2)}\n`);
    process.stdout.write(`attacks.mjs: baseline written — ${covered.length} of ${known.length} `
      + `fail sites reached\n`);
    return;
  }

  // A guard can be added, a mutation deleted, and the mutation count stay at "all of them red".
  // Coverage is the number that notices; `baselineProblems` is where that comparison lives, and it
  // is a pure function so the self-test above can hold each of its rules to firing.
  if (baseline) {
    problems.push(...baselineProblems({ known, reached, covered, uncovered, baseline }));
  }

  process.stdout.write(`attacks.mjs: ${red} of ${ATTACKS.length} mutations turned the check red · `
    + `fail sites reached: ${covered.length} of ${known.length}\n`);
  if (problems.length) {
    for (const problem of problems) process.stderr.write(`${problem}\n`);
    process.exit(1);
  }
}

// Importing `ATTACKS` runs nothing. A reader pointed out that the previous version took its
// snapshot of the tree at import time and mutated files in a top-level loop, so `import { ATTACKS }`
// — the obvious way to write a test ABOUT this list — ran the whole suite as a side effect.
if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  try {
    main();
  } finally {
    for (const at of [...live]) discard(at);
  }
}
