// The cross-check: the browser's arithmetic against the napkin's, value by value.
//
//   node demos/core.test.mjs
//
// The demos recompute chapters 1–4 in the reader's browser rather than displaying numbers Python
// worked out. That is the whole point of them and it is also the whole risk: two implementations of
// the same arithmetic are two places the book can disagree with itself. So this runs the demos'
// core under node and holds it to `demos/data/napkin.json`, which `tools/napkin_export.py` derives
// from `tools/napkin.py` and `tools/octahedron.py` on every build.
//
// **What is checked, exactly.** Three things, and then one that is deliberately not.
//
//   1. **Every value the core computes equals the napkin's** — compared as exact rational strings,
//      never as floats with a tolerance. This is the check that carries the weight.
//   2. **No number appears on any surface that the export does not contain.** Every numeric token in
//      every table cell, table heading, table caption, step title, step prose, step note and piece
//      of text inside every drawing — at every tick of every step of every chapter.
//   3. **No digit is typed into a step at all.** The source of the step definitions is read, and any
//      string literal containing a digit fails, in any quote style, with a template's `${…}` cut out
//      first because that is code. A count arrives as `String(cut.dots)` or it does not arrive.
//      Exactly three numbers on these pages are not values of the object; they are named constants
//      above the step region, and this file holds the same three.
//
//   4. **What this cannot catch, and does not claim to:** a number computed correctly from the
//      object and then *put in the wrong place* — `cut.octDots` printed in the "lines" column, or
//      `cut.dots + 1` where `cut.dots` belongs. Every such value is one the export contains, so no
//      scan over the numbers can see it; only reading the page can. That is what the proof-reader
//      pass is for, and `demos/DEMOS.md` says so in the same words.
//
// A failure prints the chapter, the beat, the tick, the surface and the text.

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

import {
  CHAPTERS, Frac, MID_ARROWS, MID_NAMES, MID_POINTS, NAMES, TETRA_LINES, TICKS, TICK_K,
  ceiling, census, cellName, fracText, midFaces, midLines, midpointCut, numberText,
  octahedronFaceSum, octahedronPoke, secondTetrahedron, signedText, simplices, stellaCensus,
  stellaLines, stellaPoints, stellaRunaway, stellaSmallerTicks, sum, tetraRuns, tetrahedron,
  netSegments, netLabels, thousands, ringPlanarity, drawRing, REPEAT_SEARCH_TICKS,
} from "./core.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const EXPORT = JSON.parse(readFileSync(join(HERE, "data", "napkin.json"), "utf8"));

let failures = 0;
let checks = 0;

function fail(message) {
  failures += 1;
  console.error(`  FAIL ${message}`);
}

/** Assert two exact values agree, compared as the strings `napkin_export.py` writes. */
function same(label, computed, expected) {
  checks += 1;
  const got = computed instanceof Frac ? computed.toString() : String(computed);
  const want = String(expected);
  if (got !== want) fail(`${label}: the browser computed ${got}, the napkin exported ${want}`);
}

function sameList(label, computed, expected) {
  checks += 1;
  if (computed.length !== expected.length) {
    fail(`${label}: ${computed.length} values, the napkin exported ${expected.length}`);
    return;
  }
  computed.forEach((value, index) => same(`${label}[${index}]`, value, expected[index]));
}

function sameRows(label, computed, expected) {
  checks += 1;
  if (computed.length !== expected.length) {
    fail(`${label}: ${computed.length} rows, the napkin exported ${expected.length}`);
    return;
  }
  computed.forEach((row, index) => sameList(`${label}[${index}]`, row, expected[index]));
}

function section(name) {
  console.log(name);
}

// The three numbers these pages write that are not values of the object at all, each with its
// reason. `core.mjs` declares the same three as named constants, the two sides are checked against
// each other below, and no step may write any other bare number.
const STRUCTURAL = new Map([
  ["0", "how many exceptions, edges, clocks, lengths and assumptions there are"],
  ["1", "how many rules the law has"],
  ["2", "the two coming-home facts, and the two shapes chapter 4 ends with"],
]);

/**
 * Every string literal in `source`, with a template's `${…}` cut out, and comments skipped.
 *
 * A regex over quotes is not enough for this and was not: `["dots", 0], ["lines", 1]` contains the
 * two-character span `", "` between two array literals, and a naive pattern reads that as a string
 * holding a digit. So the source is walked once, character by character, tracking what it is inside.
 */
function stringLiterals(source) {
  const out = [];
  let line = 1;
  let i = 0;
  while (i < source.length) {
    const c = source[i];
    if (c === "\n") { line += 1; i += 1; continue; }
    if (c === "/" && source[i + 1] === "/") {
      while (i < source.length && source[i] !== "\n") i += 1;
      continue;
    }
    if (c === "/" && source[i + 1] === "*") {
      i += 2;
      while (i < source.length && !(source[i] === "*" && source[i + 1] === "/")) {
        if (source[i] === "\n") line += 1;
        i += 1;
      }
      i += 2;
      continue;
    }
    if (c !== '"' && c !== "'" && c !== "`") { i += 1; continue; }
    const quote = c;
    const startedAt = line;
    let text = "";
    let depth = 0;
    i += 1;
    while (i < source.length) {
      const d = source[i];
      if (d === "\\") { i += 2; continue; }
      if (d === "\n") { line += 1; }
      if (quote === "`" && d === "$" && source[i + 1] === "{") { depth += 1; i += 2; continue; }
      if (depth > 0) {
        if (d === "{") depth += 1;
        else if (d === "}") depth -= 1;
        else if (d === "\n") { /* counted above */ }
        i += 1;
        continue;
      }
      if (d === quote) { i += 1; break; }
      text += d;
      i += 1;
    }
    out.push({ text, line: startedAt });
  }
  return out;
}

// ── 1 · the object, and the two coming-home facts ─────────────────────────────────────────────────

section("the complex, from the same ascending-simplex rule");
for (const size of [1, 2, 3, 4]) {
  const c = census(size);
  const expected = EXPORT.complexes[String(size)];
  for (let k = 0; k < size; k += 1) {
    same(`census(${size}).cells[${k}].length`, c.cells[k].length, expected.cells[String(k)].length);
    c.cells[k].forEach((cell, index) => {
      same(`census(${size}).cells[${k}][${index}]`, cell.join(","),
        expected.cells[String(k)][index].join(","));
    });
  }
  for (let k = 0; k + 1 < size; k += 1) {
    const rows = c.boundaries[k].map((row) => row.map(String));
    sameRows(`census(${size}).coboundary[${k}]`, rows, expected.coboundary[String(k)]);
  }
}

section("the triangle's walk, and the same walk on other numbers");
{
  const walk = (values) => {
    const v = values.map((text) => Frac.parse(text));
    const steps = [[0, 1], [1, 2], [2, 0]].map(([a, b]) => v[b].sub(v[a]));
    return { steps, total: sum(steps) };
  };
  for (const which of ["chapter", "another"]) {
    const expected = EXPORT.triangle[which];
    const got = walk(expected.values);
    sameList(`triangle.${which}.differences`, got.steps,
      expected.steps.map((step) => step.difference));
    same(`triangle.${which}.sum`, got.total, expected.sum);
  }
}

section("the tetrahedron: differences, face loops, arrows, the inside sum");
{
  const t = tetrahedron();
  const e = EXPORT.tetrahedron;
  same("tetrahedron.dots", t.dots.length, e.counts.dots);
  same("tetrahedron.lines", t.lines.length, e.counts.lines);
  same("tetrahedron.faces", t.faces.length, e.counts.faces);
  same("tetrahedron.insides", t.insides.length, e.counts.insides);
  sameList("tetrahedron.names", NAMES, e.names);
  sameList("tetrahedron.line_names", t.lineNames, e.line_names);
  sameList("tetrahedron.face_names", t.faceNames, e.face_names);
  sameList("tetrahedron.corners", t.corners, e.corners);
  sameList("tetrahedron.differences", t.differences, e.differences);
  sameList("tetrahedron.face_loops", t.faceLoops, e.face_loops);
  sameList("tetrahedron.arrows", t.arrows, e.arrows);
  sameList("tetrahedron.face_numbers", t.faceNumbers, e.face_numbers);
  sameList("tetrahedron.outward_face_numbers", t.outward, e.outward_face_numbers);
  same("tetrahedron.inside_sum", t.insideSum, e.inside_sum);
  sameList("tetrahedron.inside_incidence", t.insideIncidence.map(String),
    e.inside_incidence.map(String));
}

section("the one rule: ten ticks, plain and dialled");
{
  const runs = tetraRuns();
  const e = EXPORT.motion;
  same("motion.k", TICK_K, e.k);
  same("motion.ticks", TICKS, e.ticks);
  same("motion.dialed_line", runs.dialedLine, e.dialed_line);
  sameRows("motion.plain.history", runs.plain, e.plain.history);
  sameList("motion.plain.totals", runs.plain.map(sum), e.plain.totals);
  same("motion.plain.period", runs.period, e.plain.period);
  sameRows("motion.dialed.history", runs.dialed, e.dialed.history);
  sameList("motion.dialed.totals", runs.dialed.map(sum), e.dialed.totals);
}

// ── 2 · the shape between ─────────────────────────────────────────────────────────────────────────

section("the midpoint cut");
{
  const cut = midpointCut();
  const e = EXPORT.cut;
  for (const field of ["dots", "corners", "middles", "tips", "octahedra"]) {
    same(`cut.${field}`, cut[field], e[field]);
  }
  same("cut.tip_share", cut.tipShare, e.tip_share);
  same("cut.tip_side", cut.tipSide, e.tip_side);
  same("cut.core_share", cut.coreShare, e.core_share);
  same("cut.oct_dots", cut.octDots, e.oct_dots);
  same("cut.oct_lines", cut.octLines, e.oct_lines);
  same("cut.oct_faces", cut.octFaces, e.oct_faces);
  same("cut.oct_degree", cut.octDegree, e.oct_degree);
  sameRows("cut.opposite_pairs", cut.oppositePairs, e.opposite_pairs);
  sameList("cut.faces_at_a_tip", cut.facesAtATip, e.faces_at_a_tip);
  sameList("cut.faces_in_a_face", cut.facesInAFace, e.faces_in_a_face);
  sameList("cut.mid_names", MID_NAMES, e.mid_names);
  sameRows("cut.mid_points", MID_POINTS, e.mid_points);
  sameRows("cut.mid_lines", midLines().map((l) => l.map(String)),
    e.mid_lines.map((l) => l.map(String)));
  sameRows("cut.mid_faces", midFaces().map((f) => f.map(String)),
    e.mid_faces.map((f) => f.map(String)));
}

section("the eight-face sum");
{
  const faceSum = octahedronFaceSum();
  const e = EXPORT.face_sum;
  sameList("face_sum.arrows", MID_ARROWS.map(String), e.arrows);
  sameList("face_sum.face_numbers", faceSum.faceNumbers, e.face_numbers);
  same("face_sum.sum", faceSum.total, e.sum);
  same("face_sum.lines_walked_each_way", faceSum.linesWalkedEachWay, e.lines_walked_each_way);
}

section("the poke: crossing, home, and the repeat");
{
  const poke = octahedronPoke();
  const e = EXPORT.poke;
  same("poke.k", poke.k, e.k);
  same("poke.poked", poke.poked, e.poked);
  same("poke.opposite", poke.opposite, e.opposite);
  same("poke.crossing_ticks", poke.crossingTicks, e.crossing_ticks);
  same("poke.home_ticks", poke.homeTicks, e.home_ticks);
  same("poke.period", poke.period, e.period);
  sameRows("poke.history", poke.history, e.history);
  sameList("poke.totals", poke.history.map(sum), e.totals);
}

section("the two, threaded");
{
  const stella = stellaCensus();
  const twin = secondTetrahedron();
  const e = EXPORT.stella;
  same("stella.dots", stella.dots, e.dots);
  same("stella.lines", stella.lines, e.lines);
  same("stella.middles", stella.middles, e.middles);
  same("stella.tips", stella.tips, e.tips);
  same("stella.pieces", stella.pieces, e.pieces);
  same("stella.middle_degree", stella.middleDegree, e.middle_degree);
  same("stella.tip_degree", stella.tipDegree, e.tip_degree);
  same("stella.in_tetrahedra", stella.inTetrahedra, e.in_tetrahedra);
  same("stella.in_its_cube", stella.inItsCube, e.in_its_cube);
  sameRows("stella.points", stellaPoints(), e.points);
  sameRows("stella.edges", stellaLines().map((l) => l.map(String)),
    e.edges.map((l) => l.map(String)));
  sameList("stella.apex_names", twin.apexNames, e.apex_names);
  same("stella.apex_share", twin.apexShare, e.apex_share);
  same("stella.added", twin.added, e.added);
  same("stella.hull", stella.hull, e.hull);
}

section("the ceilings, certified without an eigensolver, and the runaway");
{
  const e = EXPORT.refusal;
  const objects = [
    ceiling(4, TETRA_LINES),
    ceiling(6, midLines()),
    ceiling(14, stellaLines()),
  ];
  same("refusal.tick", TICK_K, e.tick);
  objects.forEach((row, index) => {
    const expected = e.ceilings[index];
    same(`refusal.ceilings[${index}].dots`, row.size, expected.dots);
    same(`refusal.ceilings[${index}].stiffest`, row.stiffest, expected.stiffest);
    same(`refusal.ceilings[${index}].bound`, row.bound, expected.bound);
    same(`refusal.ceilings[${index}].book_tick_product`, row.product, expected.book_tick_product);
    same(`refusal.ceilings[${index}].holds`, row.holds, expected.holds);
  });

  const runaway = stellaRunaway();
  same("refusal.runaway.k", runaway.k, e.runaway.k);
  same("refusal.runaway.ticks", runaway.ticks, e.runaway.ticks);
  same("refusal.runaway.printable_rows", runaway.printableRows, e.runaway.printable_rows);
  same("refusal.runaway.push_at_a_middle", runaway.pushAtAMiddle, e.runaway.push_at_a_middle);
  sameList("refusal.runaway.look", runaway.look.map((entry) => entry.biggest),
    e.runaway.look.map((entry) => entry.biggest));
  sameList("refusal.runaway.look.ticks", runaway.look.map((entry) => String(entry.tick)),
    e.runaway.look.map((entry) => String(entry.tick)));

  same("refusal.runaway.repeat_search_ticks", REPEAT_SEARCH_TICKS, e.runaway.repeat_search_ticks);
  const smaller = stellaSmallerTicks();
  sameList("refusal.runaway.stable_tried.k", smaller.map((row) => row.k),
    e.runaway.stable_tried.map((row) => row.k));
  sameList("refusal.runaway.stable_tried.printable",
    smaller.map((row) => String(row.printable)),
    e.runaway.stable_tried.map((row) => String(row.printable)));
  sameList("refusal.runaway.stable_tried.period",
    smaller.map((row) => String(row.period)),
    e.runaway.stable_tried.map((row) => String(row.period)));
}

section("the canonical net: nine segments, nineteen labels, in canon.py's positions");
{
  const e = EXPORT.net;
  const segments = netSegments();
  same("net.segments.length", segments.length, e.segments.length);
  segments.forEach((segment, index) => {
    same(`net.segments[${index}].line`, cellName(segment.line), e.segments[index].line);
  });
  const labels = netLabels();
  same("net.labels.length", labels.length, e.labels.length);
  // The label positions are compared as the two-place decimals a drawing actually uses: the browser
  // works in doubles here (SVG coordinates are the one place a float is allowed) and `canon.py` works
  // in exact rationals, so agreement to the drawn precision is the honest claim to make.
  const round2 = (value) => (Math.round(value * 100) / 100).toFixed(2);
  const byName = new Map(e.labels.map((label) => [`${label.kind}:${label.text}:${label.panel}`, label]));
  labels.forEach((label, index) => {
    const candidates = e.labels.filter((other) => other.kind === label.kind && other.text === label.text);
    checks += 1;
    if (!candidates.length) {
      fail(`net.labels[${index}]: the napkin exported no ${label.kind} label named ${label.text}`);
      return;
    }
    const wanted = candidates.map((other) => other.at.map((text) => round2(Frac.parse(text).toApprox())).join(","));
    const got = label.at.map(round2).join(",");
    if (!wanted.includes(got)) {
      fail(`net.labels[${index}] ${label.kind} ${label.text}: drawn at ${got}, canon.py puts it at ${wanted.join(" or ")}`);
    }
  });
  void byName;
}

// ── 3 · the beats, and the rule that no step shows a number the napkin did not compute ────────────

section("the ring convention draws every line once, and none of them crosses");
{
  // The ring's whole claim to a reader is that she can count the object's lines off the picture. So
  // the two things that would break that are checked: an inner dot landing on an outer line (which
  // is what happens at exactly half the outer radius, and did), and any crossing at all.
  const bare = ringPlanarity({});
  same("ring.lines", bare.lines, midLines().length);
  same("ring.dots_sitting_on_a_line_they_do_not_end", bare.dotsOnLines, 0);
  same("ring.crossings", bare.crossings, 0);
  // With the tips shown, four of the eight cannot sit inside their own face — three of those faces
  // are slivers and the eighth face is the outside of the paper — so they sit outside the ring and
  // their lines in do cross each other. That is stated on the page and pinned here: what may never
  // happen is a crossing among the twelve lines of the shape itself, or a dot on a line it does not
  // end. The total is pinned too, so a change to the layout has to be looked at rather than shipped.
  const threaded = ringPlanarity({ tips: true });
  same("ring(tips).lines", threaded.lines, stellaLines().length);
  same("ring(tips).dots_sitting_on_a_line_they_do_not_end", threaded.dotsOnLines, 0);
  same("ring(tips).crossings_among_the_twelve", threaded.amongTheTwelve, 0);
  same("ring(tips).tips_inside_their_own_face", threaded.tipsInsideTheirFace, 4);
  same("ring(tips).crossings_among_the_tips_own_lines", threaded.crossings, 7);
  // And the drawings themselves must emit: both assert the above before they draw a stroke.
  checks += 1;
  try { drawRing({}); drawRing({ tips: true }); } catch (failure) {
    fail(`the ring refused to draw: ${failure.message}`);
  }
}

section("the steps are the outline's beats, in order");
{
  const expected = {
    "two-dots-and-a-line": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18],
    "one-tetrahedron-is-a-whole-world": [19, 20, 21, 22, 23, 24, 25, 26],
    "make-it-move": [27, 28, 29, 30, 31, 32, 33, 34, 35],
    "the-shape-between": [36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46],
  };
  sameList("the chapters", Object.keys(CHAPTERS).sort(), Object.keys(expected).sort());
  for (const [slug, beats] of Object.entries(expected)) {
    const steps = CHAPTERS[slug].steps();
    sameList(`${slug}: the beats`, steps.map((step) => String(step.beat)), beats.map(String));
    checks += 1;
    if (steps.some((step) => !step.title || !step.body || typeof step.render !== "function")) {
      fail(`${slug}: a step has no title, no body, or nothing to render`);
    }
  }
}

section("no step shows a number the napkin did not compute — on any surface");
{
  // Every exact value the export carries, in every form a demo is allowed to write it in: the exact
  // string, `numberText`'s short decimal (with the typeset minus), `signedText`'s explicit plus,
  // `fracText`'s fraction, that value negated (a line walked the other way round), and a big whole
  // number with its group separators.
  const allowed = new Set();
  const offer = (text) => {
    const trimmed = String(text).trim();
    if (!/^-?\d+(?:\/\d+)?$/.test(trimmed)) return;
    const value = Frac.parse(trimmed);
    for (const form of [value, value.neg()]) {
      allowed.add(form.toString());
      allowed.add(fracText(form));
      try { allowed.add(numberText(form)); allowed.add(signedText(form)); } catch { /* refused */ }
    }
    allowed.add(String(value.n));
    if (value.d !== 1n) allowed.add(String(value.d));
    if (value.d === 1n) allowed.add(thousands(value.n));
  };
  const walkExport = (node) => {
    if (typeof node === "string" || typeof node === "number") { offer(node); return; }
    if (typeof node === "boolean" || node === null) return;
    if (Array.isArray(node)) { node.forEach(walkExport); return; }
    for (const [k, v] of Object.entries(node)) { offer(k); walkExport(v); }
  };
  walkExport(EXPORT);

  // Every whole number the export's own structure makes countable, and no others: the length of a
  // list it carries, and every index into one. A tick number in the first column of a run's table is
  // an index into that run; a count of dots is a length. What this deliberately does NOT do is allow
  // every small whole number — an earlier version allowed everything up to sixty, and a page could
  // then have shown eleven dots over an export that said ten.
  const offerIndices = (node) => {
    if (Array.isArray(node)) {
      offer(String(node.length));
      for (let index = 0; index < node.length; index += 1) offer(String(index));
      node.forEach(offerIndices);
      return;
    }
    if (node && typeof node === "object") Object.values(node).forEach(offerIndices);
  };
  offerIndices(EXPORT);
  for (const value of STRUCTURAL.keys()) allowed.add(value);

  // A group-separated integer is one token, not three: `8,500` is one number.
  const TOKEN = /[−-]?\d{1,3}(?:,\d{3})+|[−-]?\d+(?:\.\d+)?(?:\/\d+)?/g;
  const TEXT_NODE = /<(?:text|title|desc)\b[^>]*>([^<]*)<\/(?:text|title|desc)>/g;

  // EVERY surface a reader meets, not only the table cells. The first version of this scanned the
  // cells alone, and a fresh reviewer walked a wrong number straight through a table's caption, a
  // step's own title, its prose, its notes, the drawing, and the SVG description a screen reader
  // reads out. A number is a number wherever the page prints it.
  const surfaces = (slug, step, tick, rendered) => {
    const out = [
      ["the step's title", step.title],
      ["the step's prose", step.body],
    ];
    rendered.notes.forEach((note, i) => out.push([`note ${i + 1}`, note]));
    for (const spec of rendered.tables) {
      out.push([`the caption of "${spec.caption}"`, spec.caption]);
      for (const row of [spec.head, ...spec.rows]) {
        for (const cell of row) out.push([`a cell of "${spec.caption}"`, String(cell)]);
      }
    }
    for (const match of rendered.drawing.matchAll(TEXT_NODE)) {
      out.push(["the drawing", match[1]]);
    }
    void slug; void tick;
    return out;
  };

  for (const [slug, chapter] of Object.entries(CHAPTERS)) {
    for (const step of chapter.steps()) {
      const ticks = step.ticks ? step.ticks + 1 : 1;
      for (let tick = 0; tick < ticks; tick += 1) {
        const rendered = step.render(tick);
        for (const [where, text] of surfaces(slug, step, tick, rendered)) {
          for (const token of String(text).match(TOKEN) || []) {
            checks += 1;
            if (!allowed.has(token)) {
              fail(`${slug} beat ${step.beat} tick ${tick}: ${where} shows ${token}, which the `
                + `napkin did not compute — in ${JSON.stringify(String(text).slice(0, 90))}`);
            }
          }
        }
        // And a step must put its numbers in a table, not only in the drawing: a reader who ignores
        // the picture entirely has to be able to read every value.
        checks += 1;
        if (!rendered.tables.length) {
          fail(`${slug} beat ${step.beat}: nothing but a drawing — every number must also be text`);
        }
      }
    }
  }
}

section("no digit is typed into a step, in any quote");
{
  // The scan above catches a number no arithmetic on this object produces. It cannot catch a small
  // whole number swapped for another, because a page that legitimately shows a twelfth tick makes 11
  // a number the export contains. So the typed number is closed from the other side, at the source:
  // **inside the step definitions, no string literal may contain a digit at all** — double-quoted,
  // single-quoted, or a template's text (a template's `${…}` is code, and is cut out before the
  // check). A count therefore has to arrive as `String(cut.dots)`, and the difference between that
  // and `"10"` is visible in a diff.
  //
  // A reviewer got past the first version of this with a backtick, with a single quote, and with a
  // digit in a caption; all three now fail here. The three exceptions are declared above the step
  // region as named constants, so the allowlist is three identifiers rather than three digits.
  const source = readFileSync(join(HERE, "core.mjs"), "utf8");
  const from = source.indexOf("// ── the steps ");
  const to = source.indexOf("/** Every chapter's steps, keyed by");
  checks += 1;
  if (from < 0 || to < 0 || to < from) {
    fail("no digit typed: could not find the step definitions in core.mjs");
  } else {
    for (const [name, digits] of [["NONE", "0"], ["ONLY", "1"], ["PAIR", "2"]]) {
      checks += 1;
      if (!new RegExp(`^const ${name} = "${digits}";`, "m").test(source.slice(0, from))) {
        fail(`no digit typed: core.mjs does not declare ${name} as "${digits}" above the step `
          + `definitions, so the two sides of the allowlist have come apart`);
      }
      if (!STRUCTURAL.has(digits)) {
        fail(`no digit typed: core.mjs declares ${name} = "${digits}", which this test does not `
          + `allow as a structural number`);
      }
    }
    for (const found of stringLiterals(source.slice(from, to))) {
      if (!/\d/.test(found.text)) continue;
      checks += 1;
      fail(`no digit typed: line ${found.line} of the step definitions writes a digit in `
        + `${JSON.stringify(found.text.slice(0, 70))} — compute it, or name it the way NONE, ONLY `
        + `and PAIR are named`);
    }
  }
}

// ── the verdict ───────────────────────────────────────────────────────────────────────────────────

console.log("");
if (failures) {
  console.error(`core.test.mjs: FAILED — ${failures} of ${checks} checks`);
  process.exit(1);
}
console.log(`core.test.mjs: ${checks} checks, every number equal to the napkin's export`);
