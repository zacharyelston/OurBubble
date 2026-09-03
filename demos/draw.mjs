// The drawings: three conventions, and no fourth.
//
// FIREWALL: these are pictures of a toy DEC lattice. Nothing in them is a claim about nature. See
// ../FIREWALL.md.
//
// Nothing here computes a number a reader is shown. What it computes is **where ink goes**, and
// SVG coordinates are the one place in these pages a float is allowed to exist — stated in
// DEMOS.md, and checked from the other side: `core.test.mjs` scans every piece of text every
// drawing emits and refuses any numeric token the engine did not produce, so a coordinate that
// leaked into a label would fail.
//
// The structure the drawings are drawings *of* is the engine's, not this file's. The net's panels,
// segments and nineteen label positions are `engine/napkin.json`'s `net` block, which is
// `tools/canon.py`'s own arithmetic; the six middles, their twelve lines, their eight faces and the
// three opposite pairs are its `cut` block; the fourteen dots and thirty-six lines of the threaded
// pair are its `stella` block. This file reads them and places them.
//
//   * **the net** — CANON.md's flat unfolded tetrahedron, and chapter 1's triangle framed to the
//     net's own central panel, so nothing is learned twice;
//   * **the ring** — the octahedron's six middles on two concentric circles, so that *opposite* is
//     literally straight through the middle;
//   * **the wireframe** — the threaded pair, orthographic, turnable, because flat it is a hairball.
//
// The third is new, and it is the owner's call on the live pages that forced it: *"42 — what have I
// got now? Is funny. If those lines are drawn from the code we're doomed."* They were: thirty-six
// lines flat lay strokes across dots they never touch.

const SVG_NS = "http://www.w3.org/2000/svg";

/** How much clear paper a drawing keeps outside everything it has drawn. */
const MARGIN = 18;

/**
 * Refit a finished drawing's `viewBox` to what it actually contains, plus a fixed margin.
 *
 * The label search grew the canvas about a third, because each frame was sized for the widest the
 * search *could* reach rather than where it went — so the figures ended up floating in a box far
 * bigger than themselves. Rather than guess a frame before placing anything, the drawing is
 * emitted, every mark in it is measured, and the box is fitted to the result. That way the frame is
 * a fact about the drawing instead of a prediction about it.
 *
 * Only the marks are measured, never the `viewBox` itself, so this is idempotent.
 */
function refit(svg) {
  const xs = [];
  const ys = [];
  const note = (x, y) => { xs.push(x); ys.push(y); };
  for (const found of svg.matchAll(/<line[^>]*x1="([-\d.]+)" y1="([-\d.]+)" x2="([-\d.]+)" y2="([-\d.]+)"/g)) {
    note(+found[1], +found[2]);
    note(+found[3], +found[4]);
  }
  for (const found of svg.matchAll(/<circle[^>]*cx="([-\d.]+)" cy="([-\d.]+)" r="([\d.]+)"/g)) {
    const r = +found[3];
    note(+found[1] - r, +found[2] - r);
    note(+found[1] + r, +found[2] + r);
  }
  for (const found of svg.matchAll(/<polygon[^>]*points="([^"]+)"/g)) {
    for (const pair of found[1].trim().split(/\s+/)) {
      const [x, y] = pair.split(",").map(Number);
      if (Number.isFinite(x) && Number.isFinite(y)) note(x, y);
    }
  }
  for (const found of svg.matchAll(/<text([^>]*)>([^<]*)<\/text>/g)) {
    const at = /x="([-\d.]+)" y="([-\d.]+)"/.exec(found[1]);
    const size = /font-size="([\d.]+)"/.exec(found[1]);
    if (!at || !size || !found[2].trim()) continue;
    const box = textBox(+at[1], +at[2], found[2], +size[1]);
    note(box.x0, box.y0);
    note(box.x1, box.y1);
  }
  if (!xs.length) return svg;
  const minX = Math.min(...xs) - MARGIN;
  const minY = Math.min(...ys) - MARGIN;
  const width = (Math.max(...xs) + MARGIN) - minX;
  const height = (Math.max(...ys) + MARGIN) - minY;
  return svg.replace(/viewBox="[^"]*"/,
    `viewBox="${d2(minX)} ${d2(minY)} ${d2(width)} ${d2(height)}"`);
}

function esc(text) {
  return String(text).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/** Two decimal places by integer arithmetic — the same shape as `canon.py`'s `_decimal`. */
function d2(value) {
  const hundredths = Math.round(value * 100);
  const whole = Math.trunc(Math.abs(hundredths) / 100);
  const part = Math.abs(hundredths) % 100;
  const sign = hundredths < 0 ? "-" : "";
  return part === 0 ? `${sign}${whole}` : `${sign}${whole}.${String(part).padStart(2, "0")}`;
}

/**
 * One of the engine's exact `"n/d"` strings as a coordinate.
 *
 * This is the only division in the demos, and it exists because a screen has pixels. Its output
 * goes into an SVG attribute and never into a piece of text — which is not a promise, it is what
 * `core.test.mjs` checks.
 */
function coord(value) {
  const [top, bottom] = String(value).split("/");
  return bottom === undefined ? Number(top) : Number(top) / Number(bottom);
}

const sub = (p, q) => [p[0] - q[0], p[1] - q[1]];
const add = (p, q) => [p[0] + q[0], p[1] + q[1]];
const scale = (p, t) => [p[0] * t, p[1] * t];
const mid = (p, q) => scale(add(p, q), 0.5);
const centroid = (points) => scale(points.reduce(add, [0, 0]), 1 / points.length);

function stepToward(from, to, distance) {
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const length = Math.hypot(dx, dy) || 1;
  return [from[0] + (dx / length) * distance, from[1] + (dy / length) * distance];
}

// ── the net ───────────────────────────────────────────────────────────────────────────────────────

const NET_SCALE = 100;
const VERTEX_INSET = 0.25;

// ── the ring ──────────────────────────────────────────────────────────────────────────────────────

const RING_OUTER = 170;

// The inner radius is the one number in the ring that can be got wrong, and it was: at exactly half
// the outer radius each inner dot lands *on* the outer triangle's edge, because that edge's midpoint
// is at half the radius in exactly that direction. The twelve lines then draw as six segments, and
// the drawing quietly stops showing which lines the object has. `ringPlanarity()` turns that from a
// thing to remember into a thing that fails.
const RING_INNER = 63;

const RING_ANGLES = { AB: 90, AC: 210, AD: 330 };

const TIP_CLEARANCE = 17;
const TIP_DOT_CLEARANCE = 3;
const TIP_OUTSIDE = RING_OUTER + 62;
const TIP_ABOVE = RING_OUTER + 132;

/**
 * Does a piece of text's box touch a line, or a dot, or another piece of text?
 *
 * Exported because `core.test.mjs` re-runs it on the emitted SVG rather than trusting that this
 * file ran it. A label is a rectangle roughly six tenths of its font size wide per character and one
 * font size tall; that is generous, which is the direction to be generous in.
 */
export function textBox(x, y, text, size) {
  const width = String(text).length * size * 0.62;
  return { x0: x - width / 2, x1: x + width / 2, y0: y - size * 0.6, y1: y + size * 0.6 };
}

/**
 * How much clear paper two labels must have between them.
 *
 * Not overlapping is not enough. The first version of this test asked only whether two boxes
 * intersected, and passed a drawing whose closest pair of labels had four tenths of a pixel between
 * them — which on a screen is two numbers touching, and reads as one token, which was the whole
 * complaint. So the boxes are inflated by this much before they are compared, on both sides: here,
 * and in `core.test.mjs`, which imports it rather than choosing its own.
 */
export const LABEL_GAP = 3;

/**
 * How much clear paper a label keeps from the dot it belongs to.
 *
 * The biggest dot any of these drawings puts down has a radius of thirteen, and a label that starts
 * at twenty was sitting three pixels off it — legible, and reading as attached to the mark rather
 * than beside it. This is the dot plus a little air; the ladder adds half the label's own height on
 * top, because a label is measured from its middle.
 */
export const DOT_CLEARANCE = 17;

const inflate = (box, by) => ({
  x0: box.x0 - by, x1: box.x1 + by, y0: box.y0 - by, y1: box.y1 + by,
});

export const boxesOverlap = (a, b, gap = 0) => {
  const one = inflate(a, gap);
  return one.x0 < b.x1 && b.x0 < one.x1 && one.y0 < b.y1 && b.y0 < one.y1;
};

/** Does a box meet a segment? Corners in, or the segment crossing any of its four sides. */
/**
 * Does a label's box reach a dot's **ink** — its radius, and the clearance the drawing keeps?
 *
 * The test used to ask whether the dot's CENTRE fell inside the box, which let a name overlap a
 * circle by nine pixels: a reader counted forty-five such overlaps across the pages. A dot is a
 * disc, so it is treated as one.
 */
export function boxMeetsDot(box, dot) {
  const [x, y, r = 0] = dot;
  const nearestX = Math.max(box.x0, Math.min(x, box.x1));
  const nearestY = Math.max(box.y0, Math.min(y, box.y1));
  return Math.hypot(x - nearestX, y - nearestY) < r + LABEL_GAP;
}

export function boxMeetsSegment(box, from, to) {
  const inside = ([x, y]) => x >= box.x0 && x <= box.x1 && y >= box.y0 && y <= box.y1;
  if (inside(from) || inside(to)) return true;
  const sides = [
    [[box.x0, box.y0], [box.x1, box.y0]], [[box.x1, box.y0], [box.x1, box.y1]],
    [[box.x1, box.y1], [box.x0, box.y1]], [[box.x0, box.y1], [box.x0, box.y0]],
  ];
  return sides.some(([a, b]) => segmentsCross(from, to, a, b));
}

/**
 * Where a label goes: the first candidate place that touches nothing.
 *
 * The ring's labels used to be placed by a rule — outward from the centre by a fixed step, and the
 * value straight under the name — and a proof-reader counted four of six values struck through by a
 * stroke or sitting on their own dot across three rounds of "fixes". A rule that has to be right
 * everywhere on a drawing with twelve lines through it is a rule that will be wrong somewhere.
 *
 * So the placement is searched instead of asserted: a fixed ladder of candidates out along the ray
 * and swung to either side of it, tried in order, and the first that collides with no stroke, no
 * dot and no label already placed is taken. The ladder is fixed and the order is fixed, so the
 * drawing is the same every time — and `core.test.mjs` checks the result on the emitted SVG, so a
 * ladder too short to find a clear spot fails rather than shipping a struck-through number.
 */
function placeClear(anchor, ray, text, size, obstacles, taken, from = 20, owner = null) {
  const angle = Math.atan2(ray[1], ray[0]);
  // A name may not sit hard against the dot it names: the nearest rung of the ladder has to clear
  // the dot's own mark and half the label's height, or the two touch even though nothing overlaps.
  const clearance = Math.max(from, DOT_CLEARANCE + size * 0.6);
  for (const out of [20, 25, 30, 36, 42, 50, 58, 68, 80, 94].filter((d) => d >= clearance)) {
    for (const swing of [0, 0.3, -0.3, 0.6, -0.6, 0.9, -0.9, 1.25, -1.25, 1.6, -1.6,
      2.0, -2.0, 2.5, -2.5, Math.PI]) {
      const theta = angle + swing;
      const x = anchor[0] + Math.cos(theta) * out;
      const y = anchor[1] + Math.sin(theta) * out;
      const box = textBox(x, y, text, size);
      if (obstacles.segments.some(([a, b]) => boxMeetsSegment(box, a, b))) continue;
      if (obstacles.dots.some((dot) => boxMeetsDot(box, dot))) continue;
      if (taken.some((other) => boxesOverlap(box, other, LABEL_GAP))) continue;
      // And it must be nearest the dot it belongs to. Clearing every stroke is not enough: two
      // readers found a name parked nearer a different dot than its own, which is the wrong-noun
      // defect drawn instead of printed. A candidate a stranger's dot is closer to is not a place
      // for this label, however much clear paper is there.
      if (owner && obstacles.dots.some((dot) =>
        Math.hypot(dot[0] - x, dot[1] - y) < Math.hypot(owner[0] - x, owner[1] - y) - 0.01)) {
        continue;
      }
      taken.push(box);
      return [x, y];
    }
  }

  // Last resort: a ring-by-ring sweep outward from the anchor, every ten degrees, out to a distance
  // that covers any of these drawings. A refused fraction like −15/8 is a much wider box than a
  // two-character name, and the ladder above — which is shaped for names — could not seat one of
  // them on chapter 1's triangle. The sweep is still deterministic and still ordered nearest-first,
  // so the drawing does not move; it just has somewhere left to look.
  for (let out = 90; out <= 260; out += 10) {
    for (let step = 0; step < 36; step += 1) {
      // Alternating either side of the ray, so the nearest-to-the-ray clear spot wins.
      const swing = (step % 2 === 0 ? 1 : -1) * Math.ceil(step / 2) * (Math.PI / 18);
      const theta = angle + swing;
      const x = anchor[0] + Math.cos(theta) * out;
      const y = anchor[1] + Math.sin(theta) * out;
      const box = textBox(x, y, text, size);
      if (obstacles.segments.some(([a, b]) => boxMeetsSegment(box, a, b))) continue;
      if (obstacles.dots.some((dot) => boxMeetsDot(box, dot))) continue;
      if (taken.some((other) => boxesOverlap(box, other, LABEL_GAP))) continue;
      // And it must be nearest the dot it belongs to. Clearing every stroke is not enough: two
      // readers found a name parked nearer a different dot than its own, which is the wrong-noun
      // defect drawn instead of printed. A candidate a stranger's dot is closer to is not a place
      // for this label, however much clear paper is there.
      if (owner && obstacles.dots.some((dot) =>
        Math.hypot(dot[0] - x, dot[1] - y) < Math.hypot(owner[0] - x, owner[1] - y) - 0.01)) {
        continue;
      }
      taken.push(box);
      return [x, y];
    }
  }
  return null;
}

/**
 * A leader: a thin line from a dot to a label that could not be put beside it.
 *
 * Requiring a name to be nearest its own dot is right and is not always possible — a dot buried in
 * the middle of a dense projection has some other dot nearer to *every* clear spot on the paper,
 * and tightening the search only moved the failure: the name then had nowhere clear to go at all.
 * So where proximity cannot carry the association, the drawing states it: one thin mark from the
 * dot to its name, stopping short of the glyphs. It is what a draughtsman does, it carries its own
 * identity so the census holds it to a real dot, and it is the only mark in these drawings that
 * exists to say which label belongs to what.
 */
function leaderGroup(leaders) {
  if (!leaders.length) return "";
  const out = ['  <g class="leaders">'];
  for (const [name, dot, label] of leaders) {
    const run = [label[0] - dot[0], label[1] - dot[1]];
    const length = Math.hypot(...run) || 1;
    const stop = Math.max(0, length - 14);
    out.push(`    <line class="leader" data-leader="${esc(name)}" x1="${d2(dot[0])}" y1="${d2(dot[1])}" x2="${d2(dot[0] + (run[0] / length) * stop)}" y2="${d2(dot[1] + (run[1] / length) * stop)}"/>`);
  }
  out.push("  </g>");
  return out.join("\n");
}

/** A label's place, and whether it needed a leader to say which dot it belongs to. */
function placeLabelled(anchor, ray, text, size, obstacles, taken, from = 20) {
  const nearest = placeClear(anchor, ray, text, size, obstacles, taken, from, anchor);
  if (nearest) return { at: nearest, leader: false };
  const anywhere = placeClear(anchor, ray, text, size, obstacles, taken, from);
  return anywhere ? { at: anywhere, leader: true } : null;
}

/**
 * Where a **number** goes: past its own name, on the far side of it from the dot.
 *
 * Anchored at the **dot**, not at the name, and started from beyond where the name sits. Anchoring
 * at the name and searching from there took the nearest clear spot, which was always hard against
 * the name's shoulder — every value came out looking like a superscript. Going out from the dot
 * along the same ray puts the number where a reader's eye is already travelling: dot, name, number.
 */
function placeValue(dot, name, ray, text, size, obstacles, taken) {
  const reach = Math.hypot(name[0] - dot[0], name[1] - dot[1]);
  return placeClear(dot, ray, text, size, obstacles, taken, reach + size * 1.15, dot);
}

function incircle(points) {
  const [a, b, c] = points;
  const side = (p, q) => Math.hypot(p[0] - q[0], p[1] - q[1]);
  const la = side(b, c);
  const lb = side(a, c);
  const lc = side(a, b);
  const perimeter = la + lb + lc;
  const area = Math.abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2;
  return {
    radius: (2 * area) / perimeter,
    centre: [
      (la * a[0] + lb * b[0] + lc * c[0]) / perimeter,
      (la * a[1] + lb * b[1] + lc * c[1]) / perimeter,
    ],
  };
}

function segmentsCross(a, b, c, d) {
  const side = (p, q, r) => Math.sign((q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]));
  if ([a, b].some((p) => [c, d].some((q) => Math.hypot(p[0] - q[0], p[1] - q[1]) < 0.001))) {
    return false;  // they share an end: meeting there is what a drawing of a graph is made of
  }
  const near = (p, q, r) => side(p, q, r) === 0
    && Math.min(p[0], q[0]) - 0.001 <= r[0] && r[0] <= Math.max(p[0], q[0]) + 0.001
    && Math.min(p[1], q[1]) - 0.001 <= r[1] && r[1] <= Math.max(p[1], q[1]) + 0.001;
  if (near(a, b, c) || near(a, b, d) || near(c, d, a) || near(c, d, b)) return true;
  return side(a, b, c) !== side(a, b, d) && side(c, d, a) !== side(c, d, b);
}

// ── the wireframe ─────────────────────────────────────────────────────────────────────────────────

/** How many directions each of the two angles is swept in when the opening view is chosen. */
export const VIEW_GRID = 72;

const WIRE_BOX = 480;
const WIRE_RADIUS = 176;

/**
 * The record's own rotation: yaw about the upright axis, then pitch, with the vertical up the page.
 *
 * Taken from UniForge's `lab/primer/0116-tetoct-primer/figures/tetoct-render.template.html`, which
 * is the record's existing data-true 3-D render of this very lattice, so that the book's picture of
 * the threaded pair turns the way the record's does. Its perspective divide is dropped and nothing
 * replaces it: the charter reserves 3-D for the simplest possible **orthographic** wireframe, and a
 * perspective camera would put a foreshortening into a picture whose whole job is letting a reader
 * count lines.
 */
export function project3d(point, yaw, pitch) {
  const [x, y, z] = point.map(coord);
  const cy = Math.cos(yaw);
  const sy = Math.sin(yaw);
  const cp = Math.cos(pitch);
  const sp = Math.sin(pitch);
  return [
    cy * x - sy * z,
    -(sy * sp * x + cp * y + cy * sp * z),
  ];
}

/**
 * What a view costs: how much of what the flat page says about the object is not true.
 *
 * Three kinds of lie, and they are not equally bad, which is what the weights say. A **crossing**
 * between two lines that do not share an end costs one: a reader sees two lines pass and reads on. A
 * **dot sitting on a line it does not end** costs four, because it looks like a join that is not
 * there. A **line that has projected to a point** costs twelve, because it has taken an edge out of
 * a picture whose whole job is to let her count them.
 */
export function viewCost(points, edges, yaw, pitch) {
  const flat = points.map((p) => project3d(p, yaw, pitch));
  const spread = Math.max(...flat.map(([x]) => x)) - Math.min(...flat.map(([x]) => x)) || 1;
  let invented = 0;
  for (let i = 0; i < edges.length; i += 1) {
    for (let j = i + 1; j < edges.length; j += 1) {
      const [a, b] = edges[i];
      const [c, d] = edges[j];
      if (a === c || a === d || b === c || b === d) continue;
      if (segmentsCross(flat[a], flat[b], flat[c], flat[d])) invented += 1;
    }
  }
  let hidden = 0;
  let nearest = Infinity;
  for (let dot = 0; dot < flat.length; dot += 1) {
    for (const [a, b] of edges) {
      if (dot === a || dot === b) continue;
      const [px, py] = flat[dot];
      const dx = flat[b][0] - flat[a][0];
      const dy = flat[b][1] - flat[a][1];
      const length = Math.hypot(dx, dy);
      if (length < 1e-9) continue;
      const along = ((px - flat[a][0]) * dx + (py - flat[a][1]) * dy) / (length * length);
      if (along <= 0 || along >= 1) continue;
      const across = Math.abs((px - flat[a][0]) * dy - (py - flat[a][1]) * dx) / length / spread;
      nearest = Math.min(nearest, across);
      if (across < 0.02) hidden += 1;
    }
  }
  const flattened = edges.filter(([a, b]) =>
    Math.hypot(flat[a][0] - flat[b][0], flat[a][1] - flat[b][1]) / spread < 0.02).length;
  return {
    invented, hidden, flattened,
    lies: invented + 4 * hidden + 12 * flattened,
    nearest: Number.isFinite(nearest) ? nearest : 1,
  };
}

/**
 * The view the wireframe opens in: **chosen by counting**, not by taste.
 *
 * A fixed sweep of directions, the cheapest kept. Ties go to the view that pushes the closest
 * unrelated dot-and-line furthest apart, because a picture with no crossings but a dot a hair off a
 * line reads as a crossing anyway — and the first version of this sweep, ranking on crossings
 * alone, picked a view straight down an axis: no crossings at all, and dots stacked on lines
 * everywhere. The sweep is fixed and the arithmetic deterministic, so it returns the same view every
 * time and `DEMOS.md` can name it.
 */
export function bestView(points, edges) {
  let best = null;
  for (let a = 0; a < VIEW_GRID; a += 1) {
    for (let b = 0; b < VIEW_GRID; b += 1) {
      const yaw = (a / VIEW_GRID) * Math.PI * 2;
      const pitch = (b / VIEW_GRID) * Math.PI - Math.PI / 2;
      const cost = viewCost(points, edges, yaw, pitch);
      if (best === null || cost.lies < best.lies
        || (cost.lies === best.lies && cost.nearest > best.nearest)) {
        best = { yaw, pitch, ...cost };
      }
    }
  }
  return best;
}

// ── the three conventions, bound to one engine ────────────────────────────────────────────────────

/**
 * The drawing kit for one engine: everything below reads the object off `engine.payload`.
 *
 * Bound to the engine rather than importing it, so that under node the same functions draw from the
 * same vendored bytes the browser gets, and `core.test.mjs` can scan what they emit.
 */
export function drawings(engine) {
  const payload = engine.payload;
  const net = payload.net;
  const cut = payload.cut;
  const stella = payload.stella;
  const NAMES = payload.tetrahedron.names;
  const MID = cut.mid_names;
  const MID_LINES = cut.mid_lines;
  const MID_FACES = cut.mid_faces;
  const OPPOSITE_PAIRS = cut.opposite_pairs;
  const SQRT3 = coord(net.sqrt3);

  // The net's positions live in the exact ring `canon.py` works in — a pair `(x, u)` standing for
  // `(x, u·√3)`. The second coordinate is multiplied out here, once, on the way to the page.
  const ringPoint = (pair) => [coord(pair[0]), coord(pair[1])];
  const panels = net.panels.map((panel) => ({
    face: panel.face, positions: panel.positions.map(ringPoint),
  }));
  const segments = net.segments.map((segment) => ({
    line: segment.line, panel: segment.panel,
    from: ringPoint(segment.from), to: ringPoint(segment.to),
  }));
  const panelCentre = new Map(panels.map((panel) => [panel.face, centroid(panel.positions)]));
  const labels = net.labels.map((label) => ({
    kind: label.kind, text: label.text, panel: label.panel, at: ringPoint(label.at),
    panelCentre: panelCentre.get(label.panel),
  }));

  function frameOf(positions, pad) {
    const xs = positions.map((p) => p[0]);
    const us = positions.map((p) => p[1]);
    const xMin = Math.min(...xs);
    const yMin = Math.min(...us) * SQRT3;
    const yMax = Math.max(...us) * SQRT3;
    return {
      xMin, yMax, pad,
      width: (Math.max(...xs) - xMin) + 2 * pad,
      height: (yMax - yMin) + 2 * pad,
    };
  }

  const NET_FRAME = frameOf(panels.flatMap((panel) => panel.positions), coord(net.pad));
  const project = (frame, point) => [
    (point[0] - frame.xMin + frame.pad) * NET_SCALE,
    (frame.yMax + frame.pad - point[1] * SQRT3) * NET_SCALE,
  ];
  const netAt = (point) => project(NET_FRAME, point);

  /**
   * The canonical net, with whatever numbers this step puts on it.
   *
   * `values` maps a piece's name to the text written under that piece's own name, so a number sits
   * where the thing it belongs to sits and **the name has not moved**. `emphasis` is the drawing's
   * one highlight: names drawn heavier. There is no second colour, because CANON.md's rule 5 leaves
   * none spare.
   */
  function drawNet({ values = {}, emphasis = [], showPanels = true, midpoints = false,
    medials = false, lines = true, title = "", desc = "" } = {}) {
    const strong = new Set(emphasis);
    const body = [];
    body.push(`<svg xmlns="${SVG_NS}" viewBox="0 0 ${d2(NET_FRAME.width * NET_SCALE)} ${d2(NET_FRAME.height * NET_SCALE)}" role="img" class="net" data-drawing="net">`);
    if (!title) throw new Error("a net drawing was asked for without a title");
    body.push(`  <title>${esc(title)}</title>`);
    body.push(`  <desc>${esc(desc || "The four faces of one tetrahedron laid out flat: the triangle ABC in the middle, with the three others folded out from its sides. Every dot, line and face carries its name. The dot D appears three times, because flat paper puts one corner of the solid in three places. All four triangles are drawn identically: nothing in the drawing means anything beyond the shape.")}</desc>`);

    if (showPanels) {
      body.push('  <g class="panel">');
      for (const panel of panels) {
        const points = panel.positions.map((p) => netAt(p).map(d2).join(",")).join(" ");
        body.push(`    <polygon data-region="${esc(panel.face)}" points="${points}"/>`);
      }
      body.push("  </g>");
    }

    body.push('  <g class="stroke">');
    for (const segment of segments) {
      const [x1, y1] = netAt(segment.from);
      const [x2, y2] = netAt(segment.to);
      const heavy = strong.has(segment.line) ? ' class="strong"' : "";
      body.push(`    <line${heavy} data-line="${esc(segment.line)}" data-panel="${esc(segment.panel)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
    }
    if (medials) {
      // The cut, on the flat paper: each panel's medial triangle is where the blade goes, and the
      // three corner triangles it leaves are three faces of that panel's tips.
      body.push('    <g class="cut">');
      for (const panel of panels) {
        const middles = [[0, 1], [1, 2], [2, 0]]
          .map(([a, b]) => mid(panel.positions[a], panel.positions[b]));
        body.push(`      <polygon data-region="${esc(panel.face)}" data-cut="yes" points="${middles.map((p) => netAt(p).map(d2).join(",")).join(" ")}"/>`);
      }
      body.push("    </g>");
    }
    body.push("  </g>");

    if (midpoints) {
      body.push('  <g class="middle">');
      for (const segment of segments) {
        const [x, y] = netAt(mid(segment.from, segment.to));
        body.push(`    <circle data-middle="${esc(segment.line)}" cx="${d2(x)}" cy="${d2(y)}" r="9"/>`);
      }
      body.push("  </g>");
    }

    // **The names do not move.** CANON.md's rule 4 forbids putting a label wherever it fits, and
    // the net's nineteen positions are the engine's. What is not CANON's is where a *number* goes
    // beside a name, and that used to take a fixed step — into the panel for a dot, straight down
    // for a line — which a proof-reader found sitting across a stroke two dozen times. So the names
    // are fixed obstacles and the numbers are searched around them.
    const netObstacles = {
      segments: segments.map((segment) => [netAt(segment.from), netAt(segment.to)]),
      dots: midpoints
        ? segments.map((segment) => [...netAt(mid(segment.from, segment.to)), 9])
        : [],
    };
    const netLeaders = [];
    const netTaken = labels.map((label) => {
      const [x, y] = netAt(label.at);
      const size = label.kind === "dot" ? 34 : (label.kind === "face" ? 28 : 24);
      return textBox(x, y, label.text, size);
    });

    body.push('  <g class="labels">');
    // When the middles are marked, a line's name belongs to its **middle** rather than to the line:
    // CANON puts a line's name a quarter of the way in from the midpoint, which is close enough
    // that its box lies over the mark, and a reader counted all six overlapping. The middles are
    // what those beats are about, so the name goes to the mark and is searched clear of it.
    const nameTheMiddles = midpoints;
    labels.forEach((label, index) => {
      // A step that carries no number on the lines carries no line names either: six names with
      // nothing under them read as six numbers the drawing has lost.
      if ((!lines || nameTheMiddles) && label.kind === "line") return;
      const [x, y] = netAt(label.at);
      const [cx, cy] = netAt(label.panelCentre);
      const size = label.kind === "dot" ? 34 : (label.kind === "face" ? 28 : 24);
      const value = values[label.text];
      const heavy = strong.has(label.text) ? ' class="strong"' : "";
      const weight = label.kind === "dot" ? ' font-weight="700"' : "";
      body.push(`    <text${heavy}${weight} x="${d2(x)}" y="${d2(y)}" font-size="${size}" text-anchor="middle" dominant-baseline="central">${esc(label.text)}</text>`);
      if (value !== undefined) {
        // Searched from the name, biased toward the middle of the panel the name belongs to, which
        // is where the paper is emptiest — except for a FACE's number, which goes straight down.
        // A face's name sits at the panel's own middle, so "toward the middle" points nowhere, and
        // on the central panel that put one zero of four above its name while the others sat below.
        const ray = label.kind === "face" ? [0, 1] : [cx - x || 0.001, cy - y || 0.001];
        // `netTaken` is passed as itself, not as a filtered copy. It used to be
        // `netTaken.filter(…)`, which built a new array on every call — so `placeClear`'s record of
        // what it had already placed went into a throwaway and every number was positioned as
        // though it were the first. A proof-reader found "0−1" rendering as one token in two places
        // on chapter 2's net, which is the wrong-noun defect in visual form.
        //
        // A number also avoids its OWN name's box, not just the others': the two have to read as
        // two things.
        const spot = placeValue(netAt(label.at), [x, y], ray, value, size * 0.85,
          netObstacles, netTaken);
        const [vx, vy] = spot === null
          ? (label.kind === "dot" ? stepToward([x, y], [cx, cy], size * 0.95) : [x, y + size * 1.05])
          : spot;
        if (spot === null) netTaken.push(textBox(vx, vy, value, size * 0.85));
        body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="${d2(size * 0.85)}" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
      }
    });
    if (nameTheMiddles) {
      for (const segment of segments) {
        const dot = netAt(mid(segment.from, segment.to));
        const centre = netAt(panelCentre.get(segment.panel));
        const ray = [dot[0] - centre[0] || 0.001, dot[1] - centre[1] || 0.001];
        const spot = placeLabelled(dot, ray, segment.line, 22, netObstacles, netTaken);
        if (spot === null) continue;
        if (spot.leader) netLeaders.push([segment.line, dot, spot.at]);
        body.push(`    <text x="${d2(spot.at[0])}" y="${d2(spot.at[1])}" font-size="22" text-anchor="middle" dominant-baseline="central">${esc(segment.line)}</text>`);
      }
    }
    body.push("  </g>");
    body.push(leaderGroup(netLeaders));
    body.push("</svg>");
    return refit(body.join("\n"));
  }

  /**
   * Chapter 1's world: one dot, two dots and a line, or the triangle.
   *
   * The net's own central panel, framed to the part it uses, so the triangle fills the picture
   * rather than sitting in the corner of a frame shaped for four panels. When the fourth dot
   * arrives in the next chapter this triangle is already where the net puts `ABC`.
   */
  function drawTriangle({ dots = 3, values = {}, showLine = true, showFace = false, lines = null,
    arrows = [], emphasis = [], title = "", desc = "" } = {}) {
    const central = panels[0];
    const used = central.positions.slice(0, dots);
    const strong = new Set(emphasis);
    const frame = frameOf(dots === 1 ? [[-1, -0.5], [1, 0.5]] : used, 0.7);
    const at = (point) => project(frame, point);
    const lineName = ([a, b]) => [NAMES[a], NAMES[b]].sort().join("");
    const all = dots === 2 ? [[0, 1]] : (dots >= 3 ? [[0, 1], [1, 2], [0, 2]] : []);
    // `lines` names the lines this step has actually drawn, when a step is adding them one at a
    // time. Without it every line the dots allow is drawn, which is what every other step wants.
    const pairs = lines === null ? all : all.filter((pair) => lines.includes(lineName(pair)));
    const middle = centroid(used.length >= 3 ? used : central.positions);

    const body = [];
    body.push(`<svg xmlns="${SVG_NS}" viewBox="0 0 ${d2(frame.width * NET_SCALE)} ${d2(frame.height * NET_SCALE)}" role="img" class="net" data-drawing="triangle">`);
    if (!title) throw new Error("a triangle drawing was asked for without a title");
    body.push(`  <title>${esc(title)}</title>`);
    body.push(`  <desc>${esc(desc || `${dots === 1 ? "One dot" : dots === 2 ? "Two dots joined by one line" : "Three dots joined by three lines, with an inside"}, drawn where the tetrahedron's flat net will later put them: AB horizontal, A on the left, C above. Nothing in the drawing means anything beyond the shape.`)}</desc>`);

    if (dots >= 3 && showFace) {
      body.push(`  <g class="panel"><polygon data-region="${esc(payload.tetrahedron.face_names[0])}" points="${used.map((p) => at(p).map(d2).join(",")).join(" ")}"/></g>`);
    }

    body.push('  <g class="stroke">');
    if (showLine) {
      for (const pair of pairs) {
        const [x1, y1] = at(used[pair[0]]);
        const [x2, y2] = at(used[pair[1]]);
        const heavy = strong.has(lineName(pair)) ? ' class="strong"' : "";
        body.push(`    <line${heavy} data-line="${esc(lineName(pair))}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
      }
    }
    body.push("  </g>");

    // Chapter 1's dots are drawn as dots, and the net's are not. That is not an inconsistency to be
    // tidied away: in the net a corner is where lines meet, and there is always a line. In the
    // chapter's first beat there is not — the question is *where could you put a number*, and its
    // answer needs something to point at.
    body.push('  <g class="middle">');
    used.forEach((point, index) => {
      const [x, y] = at(point);
      body.push(`    <circle data-dot="${esc(NAMES[index])}" cx="${d2(x)}" cy="${d2(y)}" r="10"/>`);
    });
    body.push("  </g>");

    if (arrows.length) {
      body.push('  <g class="walk">');
      for (const [a, b] of arrows) {
        const [x1, y1] = at(used[a]);
        const [x2, y2] = at(used[b]);
        const length = Math.hypot(x2 - x1, y2 - y1);
        const ux = (x2 - x1) / length;
        const uy = (y2 - y1) / length;
        const tipX = x1 + ux * length * 0.74;
        const tipY = y1 + uy * length * 0.74;
        const baseX = tipX - ux * 26;
        const baseY = tipY - uy * 26;
        // The head says which step of the walk it marks, so the check can hold it to the line it
        // sits on rather than trusting that it is somewhere sensible.
        body.push(`    <polygon class="head" data-walk="${esc(lineName([a, b]))}" points="${d2(tipX)},${d2(tipY)} ${d2(baseX - uy * 9)},${d2(baseY + ux * 9)} ${d2(baseX + uy * 9)},${d2(baseY - ux * 9)}"/>`);
      }
      body.push("  </g>");
    }

    // The names keep the canonical inset; the numbers are searched around them, the same way the
    // net's and the ring's are. Chapter 1 is where a reader learns to read a number off a picture,
    // so a difference sitting across the line it belongs to is the worst place to have one.
    const triObstacles = {
      segments: pairs.map((pair) => [at(used[pair[0]]), at(used[pair[1]])]),
      dots: used.map((point) => [...at(point), 10]),
    };
    const triTaken = [];
    if (dots >= 3 && showFace) {
      const faceName = payload.tetrahedron.face_names[0];
      const [fx, fy] = at(centroid(used));
      triTaken.push(textBox(fx, fy - (values[faceName] === undefined ? 0 : 12), faceName, 28));
      if (values[faceName] !== undefined) {
        triTaken.push(textBox(fx, fy + 18, values[faceName], 26));
      }
    }
    const nameSpots = [];
    used.forEach((point, index) => {
      const [dx, dy] = at(point);
      const [ax, ay] = dots === 1
        ? [dx, dy - 34]
        : at(add(point, scale(sub(middle, point), VERTEX_INSET)));
      nameSpots.push([ax, ay]);
      triTaken.push(textBox(ax, ay, NAMES[index], 34));
    });
    if (showLine) {
      for (const pair of pairs) {
        const midpoint = mid(used[pair[0]], used[pair[1]]);
        const [x, y] = at(add(midpoint, scale(sub(middle, midpoint), VERTEX_INSET)));
        triTaken.push(textBox(x, y, lineName(pair), 24));
      }
    }

    body.push('  <g class="labels">');
    used.forEach((point, index) => {
      const value = values[NAMES[index]];
      const [ax, ay] = nameSpots[index];
      body.push(`    <text font-weight="700" x="${d2(ax)}" y="${d2(ay)}" font-size="34" text-anchor="middle" dominant-baseline="central">${esc(NAMES[index])}</text>`);
      if (value !== undefined) {
        const [mx, my] = at(middle);
        const ray = [mx - ax || 0.001, my - ay || 0.001];
        const spot = placeValue(at(point), [ax, ay], ray, value, 30, triObstacles, triTaken);
        const [vx, vy] = spot === null ? stepToward([ax, ay], at(middle), 32) : spot;
        if (spot === null) triTaken.push(textBox(vx, vy, value, 30));
        body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="30" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
      }
    });
    if (showLine) {
      for (const pair of pairs) {
        const name = lineName(pair);
        const midpoint = mid(used[pair[0]], used[pair[1]]);
        const [x, y] = at(add(midpoint, scale(sub(middle, midpoint), VERTEX_INSET)));
        const value = values[name];
        body.push(`    <text${strong.has(name) ? ' class="strong"' : ""} x="${d2(x)}" y="${d2(y)}" font-size="24" text-anchor="middle" dominant-baseline="central">${esc(name)}</text>`);
        if (value !== undefined) {
          const [mx, my] = at(middle);
          const ray = [mx - x || 0.001, my - y || 0.001];
          const spot = placeValue(at(midpoint), [x, y], ray, value, 24, triObstacles, triTaken);
          const [vx, vy] = spot === null ? [x, y + 26] : spot;
          if (spot === null) triTaken.push(textBox(vx, vy, value, 24));
          body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="24" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
        }
      }
    }
    if (dots >= 3 && showFace) {
      const [x, y] = at(centroid(used));
      const value = values[payload.tetrahedron.face_names[0]];
      const name = payload.tetrahedron.face_names[0];
      body.push(`    <text x="${d2(x)}" y="${d2(y + (value === undefined ? 0 : -12))}" font-size="28" text-anchor="middle" dominant-baseline="central">${esc(name)}</text>`);
      if (value !== undefined) {
        body.push(`    <text class="value" x="${d2(x)}" y="${d2(y + 18)}" font-size="26" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
      }
    }
    body.push("  </g>");
    body.push("</svg>");
    return refit(body.join("\n"));
  }

  // ── the ring ────────────────────────────────────────────────────────────────────────────────────

  /** Where each middle sits, and which middle each is opposite. Derived from the engine's pairs. */
  function ringLayout() {
    const outer = Object.keys(RING_ANGLES);
    const opposite = Object.fromEntries(OPPOSITE_PAIRS.flatMap(([a, b]) => [[a, b], [b, a]]));
    const at = {};
    for (const name of outer) {
      const theta = (RING_ANGLES[name] * Math.PI) / 180;
      at[name] = [RING_OUTER * Math.cos(theta), -RING_OUTER * Math.sin(theta)];
      at[opposite[name]] = [-RING_INNER * Math.cos(theta), RING_INNER * Math.sin(theta)];
    }
    return { at, outer, inner: outer.map((name) => opposite[name]), opposite };
  }

  /** Which face is the outside of the paper: the one all of whose dots are on the rim. */
  function ringOuterFace(at) {
    const rim = (RING_OUTER + RING_INNER) / 2;
    const index = MID_FACES.findIndex((face) =>
      face.every((i) => Math.hypot(...at[MID[i]]) > rim));
    if (index < 0) throw new Error("no face of the ring is the outside of the paper");
    return index;
  }

  /**
   * Where the tip over each face is drawn, and whether it sits inside that face.
   *
   * The outside face is forced out first, and that is not an optimisation: its three dots are the
   * rim of the drawing, so its triangle *looks* like the roomiest of the eight when it is the one
   * region with no inside at all — everything else is in there.
   */
  function tipPlaces(at) {
    const outside = ringOuterFace(at);
    return MID_FACES.map((face, index) => {
      const points = face.map((i) => at[MID[i]]);
      if (index === outside) return { at: [0, -TIP_ABOVE], inside: false };
      const { radius, centre } = incircle(points);
      if (radius >= TIP_CLEARANCE) return { at: centre, inside: true };
      const mean = centroid(points);
      const away = Math.hypot(...mean);
      return { at: [(mean[0] / away) * TIP_OUTSIDE, (mean[1] / away) * TIP_OUTSIDE], inside: false };
    });
  }

  /**
   * How many drawn lines cross, and whether a dot sits on a line it does not end.
   *
   * The ring's whole claim is that it draws all twelve of the octahedron's lines separately and none
   * of them crosses another, so a reader can count the lines off the picture. That is checked here
   * rather than eyeballed, before a stroke is emitted, and it is checked because it was once false.
   */
  function ringPlanarity({ tips = false } = {}) {
    const { at } = ringLayout();
    const outerFace = ringOuterFace(at);
    const places = tips ? tipPlaces(at) : null;
    const drawn = MID_LINES.map(([i, j]) => ({ from: at[MID[i]], to: at[MID[j]], tip: null }));
    if (tips) {
      MID_FACES.forEach((face, index) => {
        for (const i of face) drawn.push({ from: places[index].at, to: at[MID[i]], tip: index });
      });
    }
    const dots = MID.map((name) => at[name])
      .concat(tips ? places.map((place) => place.at) : []);

    let crossings = 0;
    let amongTheTwelve = 0;
    for (let i = 0; i < drawn.length; i += 1) {
      for (let j = i + 1; j < drawn.length; j += 1) {
        if (!segmentsCross(drawn[i].from, drawn[i].to, drawn[j].from, drawn[j].to)) continue;
        crossings += 1;
        if (drawn[i].tip === null && drawn[j].tip === null) amongTheTwelve += 1;
      }
    }
    let dotsOnLines = 0;
    let dotsOnTheTwelve = 0;
    for (const dot of dots) {
      for (const line of drawn) {
        const ends = [line.from, line.to]
          .some((p) => Math.hypot(p[0] - dot[0], p[1] - dot[1]) < 0.001);
        if (ends) continue;
        const cross = (line.to[0] - line.from[0]) * (dot[1] - line.from[1])
          - (line.to[1] - line.from[1]) * (dot[0] - line.from[0]);
        const length = Math.hypot(line.to[0] - line.from[0], line.to[1] - line.from[1]);
        const along = ((dot[0] - line.from[0]) * (line.to[0] - line.from[0])
          + (dot[1] - line.from[1]) * (line.to[1] - line.from[1])) / (length * length);
        if (Math.abs(cross / length) >= TIP_DOT_CLEARANCE || along <= 0 || along >= 1) continue;
        dotsOnLines += 1;
        if (line.tip === null) dotsOnTheTwelve += 1;
      }
    }
    return {
      lines: drawn.length, crossings, amongTheTwelve, dotsOnLines, dotsOnTheTwelve, outerFace,
      tipsInsideTheirFace: places ? places.filter((place) => place.inside).length : 0,
    };
  }

  /** The name of the tip over each face: a shared letter, or the corner pushed through the middle. */
  function tipNames() {
    const apexes = stella.apex_names;
    return MID_FACES.map((face) => {
      const letters = face.map((i) => new Set(MID[i]));
      const shared = [...letters[0]].filter((l) => letters[1].has(l) && letters[2].has(l));
      if (shared.length === 1) return shared[0];
      const spanned = new Set(face.flatMap((i) => [...MID[i]]));
      const missing = NAMES.find((name) => !spanned.has(name));
      const apex = apexes.find((name) => name.startsWith(missing));
      if (apex === undefined) throw new Error(`no pushed-through corner over the face ${face}`);
      return apex;
    });
  }

  /**
   * The octahedron on the ring — or the octahedron with the four or eight tips over its faces.
   *
   * `tips` takes the number of tips to draw. Four is the step where the tetrahedron's own corners
   * are back: the octahedron plus the four tips, and **not** the whole threaded pair, which is the
   * owner's note on #44. Eight is the full set of tips, drawn once before the wireframe takes over.
   */
  function drawRing({ values = {}, emphasis = [], face = null, tips = [], absences = true,
    title = "", desc = "" } = {}) {
    const { at } = ringLayout();
    const strong = new Set(emphasis);
    const outerFace = ringOuterFace(at);
    const shown = [...tips];
    const wantTips = shown.length > 0;
    const places = tipPlaces(at);
    const names = tipNames();
    for (const index of shown) {
      if (!(index >= 0 && index < MID_FACES.length)) {
        throw new Error(`the ring was asked for a tip over face ${index}, which it has not got`);
      }
    }

    // The twelve lines' own claim is checked with every tip in place, which is the strictest case:
    // a layout that is planar with four tips and not with eight is one that will fail later.
    const planar = ringPlanarity({ tips: wantTips });
    if (planar.dotsOnTheTwelve) {
      throw new Error(`${planar.dotsOnTheTwelve} dot(s) sit on one of the twelve lines without `
        + `ending it — the ring is degenerate and those twelve lines would draw as fewer`);
    }
    if (planar.amongTheTwelve) {
      throw new Error(`${planar.amongTheTwelve} of the twelve lines cross each other; the ring's `
        + `whole claim is that none of them does`);
    }

    // The frame is taken from what the drawing puts on the paper with all eight tips, so the ring is
    // the same size whether four are shown or eight — a reader is looking at one object.
    const everything = [
      ...MID.flatMap((name) => {
        const away = Math.hypot(...at[name]) || 1;
        // The widest the label search can reach, so the frame holds whatever it finds.
        const label = at[name].map((v) => v + (v / away) * 110);
        return [at[name], label, [label[0], label[1] + 24], [label[0], label[1] - 24]];
      }),
      ...(wantTips ? places.map((entry) => entry.at) : []),
    ];
    const pad = 42;
    const xs = everything.map((point) => point[0]);
    const ys = everything.map((point) => point[1]);
    const minX = Math.min(...xs) - pad;
    const minY = Math.min(...ys) - pad;
    const frame = {
      minX, minY,
      width: (Math.max(...xs) - minX) + pad,
      height: (Math.max(...ys) - minY) + pad,
    };
    const place = (point) => [point[0] - frame.minX, point[1] - frame.minY];

    const body = [];
    body.push(`<svg xmlns="${SVG_NS}" viewBox="0 0 ${d2(frame.width)} ${d2(frame.height)}" role="img" class="ring" data-drawing="ring">`);
    if (!title) throw new Error("a ring drawing was asked for without a title");
    body.push(`  <title>${esc(title)}</title>`);
    body.push(`  <desc>${esc(desc || (wantTips
      ? "The six middles on two concentric circles, with a tip drawn over each of the faces that looks at one, joined to that face's three middles. No two tips are joined to each other."
      : "The six middles on two concentric circles: each sits on the same line through the centre as the one middle no line joins it to, so opposite means straight through the middle. All twelve lines are drawn once and none crosses another."))}</desc>`);

    if (face !== null && face !== outerFace) {
      const points = MID_FACES[face].map((i) => place(at[MID[i]]).map(d2).join(",")).join(" ");
      body.push(`  <g class="panel"><polygon data-region="${MID_FACES[face].map((i) => esc(MID[i])).join("|")}" points="${points}"/></g>`);
    }

    body.push('  <g class="stroke">');
    for (const [i, j] of MID_LINES) {
      const a = MID[i];
      const b = MID[j];
      const heavy = (face !== null && MID_FACES[face].includes(i) && MID_FACES[face].includes(j))
        || strong.has(`${a}–${b}`) || strong.has(`${b}–${a}`);
      const [x1, y1] = place(at[a]);
      const [x2, y2] = place(at[b]);
      body.push(`    <line${heavy ? ' class="strong"' : ""} data-line="${esc(a)}|${esc(b)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
    }
    for (const index of shown) {
      const [tx, ty] = place(places[index].at);
      for (const i of MID_FACES[index]) {
        const [x, y] = place(at[MID[i]]);
        body.push(`    <line class="tip-line" data-tip-line="${esc(names[index])}|${esc(MID[i])}" x1="${d2(tx)}" y1="${d2(ty)}" x2="${d2(x)}" y2="${d2(y)}"/>`);
      }
    }
    body.push("  </g>");

    // The three pairs no line joins, drawn as what they are: nothing. A faint mark straight through
    // the centre says where a line would have been, and it is the only mark in either drawing that
    // stands for an absence.
    body.push('  <g class="absent">');
    for (const [a, b] of (absences ? OPPOSITE_PAIRS : [])) {
      const [x1, y1] = place(at[a]);
      const [x2, y2] = place(at[b]);
      body.push(`    <line data-absent="${esc(a)}|${esc(b)}" x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
    }
    body.push("  </g>");

    body.push('  <g class="dots">');
    for (const name of MID) {
      const [x, y] = place(at[name]);
      body.push(`    <circle${strong.has(name) ? ' class="strong"' : ""} data-dot="${esc(name)}" cx="${d2(x)}" cy="${d2(y)}" r="13"/>`);
    }
    for (const index of shown) {
      const [x, y] = place(places[index].at);
      body.push(`    <circle class="tip" data-dot="${esc(names[index])}" cx="${d2(x)}" cy="${d2(y)}" r="10"/>`);
    }
    body.push("  </g>");

    // Everything a label must miss: every stroke actually drawn, and every dot.
    const obstacles = {
      segments: [
        ...MID_LINES.map(([i, j]) => [place(at[MID[i]]), place(at[MID[j]])]),
        // The three marks standing for an absence are faint, but they are ink on the paper and a
        // number sitting across one still reads as struck through.
        ...(absences ? OPPOSITE_PAIRS.map(([a, b]) => [place(at[a]), place(at[b])]) : []),
        ...shown.flatMap((index) => MID_FACES[index]
          .map((i) => [place(places[index].at), place(at[MID[i]])])),
      ],
      dots: [
        ...MID.map((name) => [...place(at[name]), 13]),
        ...shown.map((index) => [...place(places[index].at), 10]),
      ],
    };
    const taken = [];
    const leaders = [];

    // **A dot's name and its number are one label**, placed as one unit.
    //
    // Searching for them separately worked — nothing was struck through — and produced a worse
    // drawing: the six numbers ended up wherever there was room, one far left, one far right, one
    // below the rim, and which number belonged to which dot stopped being obvious. On a drawing
    // whose whole point is *which number is on which dot*, that is the wrong thing to trade a
    // collision for. Written as one string they cannot come apart, and the search has one box to
    // place instead of two that must both be clear and adjacent.
    //
    // This is not CANON.md's convention and does not contradict it: CANON governs the tetrahedron,
    // where the name is fixed and must not move. Here nothing is fixed, so the pair travels.
    body.push('  <g class="labels">');
    for (const name of MID) {
      const dot = place(at[name]);
      const ray = [at[name][0], at[name][1]];
      const value = values[name];
      const text = value === undefined ? name : `${name} ${value}`;
      const spot = placeLabelled(dot, ray, text, 19, obstacles, taken);
      if (spot === null) throw new Error(`the ring found nowhere clear to put ${text}`);
      const [lx, ly] = spot.at;
      if (spot.leader) leaders.push([name, dot, [lx, ly]]);
      body.push(`    <text${strong.has(name) ? ' class="strong"' : ""} font-weight="700" x="${d2(lx)}" y="${d2(ly)}" font-size="19" text-anchor="middle" dominant-baseline="central">${esc(text)}</text>`);
    }
    for (const index of shown) {
      const dot = place(places[index].at);
      const ray = places[index].at[0] === 0 && places[index].at[1] === 0
        ? [0, -1]
        : [places[index].at[0], places[index].at[1]];
      const value = values[names[index]];
      const text = value === undefined ? names[index] : `${names[index]} ${value}`;
      const spot = placeLabelled(dot, ray, text, 15, obstacles, taken);
      const [x, y] = spot === null ? [dot[0], dot[1] - 22] : spot.at;
      if (spot === null) taken.push(textBox(x, y, text, 15));
      else if (spot.leader) leaders.push([names[index], dot, [x, y]]);
      body.push(`    <text class="tip" x="${d2(x)}" y="${d2(y)}" font-size="15" text-anchor="middle" dominant-baseline="central">${esc(text)}</text>`);
    }
    body.push("  </g>");
    body.push(leaderGroup(leaders));
    body.push("</svg>");
    return refit(body.join("\n"));
  }

  // ── the wireframe ───────────────────────────────────────────────────────────────────────────────

  /**
   * The threaded pair's fourteen dots, thirty-six lines, and which family each line belongs to.
   *
   * The three families are **derived from what each line joins**, not declared: a line between two
   * middles is the octahedron's, a line from a middle to one of the four corners we cut is the first
   * tetrahedron's, and to one of the four the second brought, the second's. Twelve each.
   */
  function wireframe() {
    const points = stella.points;
    const edges = stella.edges;
    const names = stella.names;
    if (points.length !== stella.dots) throw new Error("the wireframe has the wrong dot count");
    if (edges.length !== stella.lines) throw new Error("the wireframe has the wrong line count");
    const family = edges.map(([i, j]) => {
      const high = Math.max(i, j);
      if (high < stella.middles) return "octahedron";
      return names[high].endsWith("′") ? "second" : "first";
    });
    const counts = { octahedron: 0, first: 0, second: 0 };
    for (const kind of family) counts[kind] += 1;
    const each = edges.length / Object.keys(counts).length;
    if (Object.values(counts).some((count) => count !== each)) {
      throw new Error(`the three families came out ${JSON.stringify(counts)}, not ${each} each`);
    }
    return { points, edges, family, names, counts };
  }

  /** The view the wireframe opens in, computed once from the census and reused. */
  let opening = null;
  function wireDefaultView() {
    const { points, edges } = wireframe();
    if (opening === null) opening = bestView(points, edges);
    return opening;
  }

  /**
   * The threaded pair, turned to `yaw` and `pitch`, as a plain orthographic wireframe.
   *
   * Every line carries the two dot names it joins and every dot its own name, in the drawing itself,
   * so `core.test.mjs` can check that what is drawn **is** the census rather than a picture of it:
   * thirty-six lines, fourteen dots, and every line an edge the engine exported.
   */
  function drawWire({ yaw, pitch, values = {}, emphasis = [], families = null,
    title = "", desc = "" } = {}) {
    const { points, edges, family, names } = wireframe();
    const strong = new Set(emphasis);
    const view = wireDefaultView();
    const useYaw = yaw === undefined ? view.yaw : yaw;
    const usePitch = pitch === undefined ? view.pitch : pitch;
    const wanted = families === null ? ["octahedron", "second", "first"] : families;
    const flat = points.map((p) => project3d(p, useYaw, usePitch));
    const spread = Math.max(...flat.flatMap(([x, y]) => [Math.abs(x), Math.abs(y)])) || 1;
    const at = flat.map(([x, y]) => [
      WIRE_BOX / 2 + (x / spread) * WIRE_RADIUS,
      WIRE_BOX / 2 + (y / spread) * WIRE_RADIUS,
    ]);
    const drawnDots = new Set();
    for (let index = 0; index < edges.length; index += 1) {
      if (!wanted.includes(family[index])) continue;
      drawnDots.add(edges[index][0]);
      drawnDots.add(edges[index][1]);
    }

    const body = [];
    body.push(`<svg xmlns="${SVG_NS}" viewBox="0 0 ${WIRE_BOX} ${WIRE_BOX}" role="img" class="wire" data-drawing="wire" tabindex="0">`);
    if (!title) throw new Error("a wireframe was asked for without a title");
    body.push(`  <title>${esc(title)}</title>`);
    body.push(`  <desc>${esc(desc || "An orthographic wireframe of two tetrahedra threaded through one another, sharing the shape between them. The first tetrahedron's lines are the full stroke, the second's lighter, and the octahedron's lie between them. Every dot carries its name. No shading and no perspective. Drag it, or use the arrow keys, to turn it; the numbers are all in the table below.")}</desc>`);

    for (const kind of ["octahedron", "second", "first"]) {
      if (!wanted.includes(kind)) continue;
      body.push(`  <g class="stroke ${kind}">`);
      edges.forEach(([i, j], index) => {
        if (family[index] !== kind) return;
        const heavy = strong.has(`${names[i]}–${names[j]}`) || strong.has(`${names[j]}–${names[i]}`);
        body.push(`    <line class="edge${heavy ? " strong" : ""}" data-edge="${esc(names[i])}|${esc(names[j])}" x1="${d2(at[i][0])}" y1="${d2(at[i][1])}" x2="${d2(at[j][0])}" y2="${d2(at[j][1])}"/>`);
      });
      body.push("  </g>");
    }

    body.push('  <g class="dots">');
    names.forEach((name, index) => {
      if (!drawnDots.has(index)) return;
      const middle = index < stella.middles;
      body.push(`    <circle class="${middle ? "middle" : "tip"}${strong.has(name) ? " strong" : ""}" data-dot="${esc(name)}" cx="${d2(at[index][0])}" cy="${d2(at[index][1])}" r="${middle ? 7 : 6}"/>`);
    });
    body.push("  </g>");

    // Searched, like the ring's. A dot near the middle of the projection has almost no outward
    // direction to be pushed along, so a fixed radial step put every one of the fourteen names
    // across a stroke; the halo kept them legible and left them in the way.
    const wireObstacles = {
      segments: edges.filter((_, index) => wanted.includes(family[index]))
        .map(([i, j]) => [at[i], at[j]]),
      dots: [...drawnDots].map((index) =>
        [...at[index], index < stella.middles ? 7 : 6]),
    };
    const wireTaken = [];
    const wireLeaders = [];

    body.push('  <g class="labels">');
    names.forEach((name, index) => {
      if (!drawnDots.has(index)) return;
      const away = Math.hypot(flat[index][0], flat[index][1]) || 1;
      const ray = [flat[index][0] / away, flat[index][1] / away];
      const value = values[name];
      const text = value === undefined ? name : `${name} ${value}`;
      const spot = placeLabelled(at[index], ray, text, 15, wireObstacles, wireTaken);
      const [lx, ly] = spot === null
        ? [at[index][0] + ray[0] * 24, at[index][1] + ray[1] * 24]
        : spot.at;
      if (spot === null) wireTaken.push(textBox(lx, ly, text, 15));
      else if (spot.leader) wireLeaders.push([name, at[index], [lx, ly]]);
      body.push(`    <text${strong.has(name) ? ' class="strong"' : ""} x="${d2(lx)}" y="${d2(ly)}" font-size="15" text-anchor="middle" dominant-baseline="central">${esc(text)}</text>`);
    });
    body.push("  </g>");
    body.push(leaderGroup(wireLeaders));
    body.push("</svg>");
    return refit(body.join("\n"));
  }

  /**
   * Where each named dot belongs, in each flat convention's own drawn coordinates.
   *
   * Exposed because "the drawing agrees with itself" is not the same as "the drawing is the
   * object". A proof-reader mirrored the net left-to-right, moving every mark together: every
   * identity still honest, every stroke still meeting its neighbours at a point, and `A` and `B`
   * swapped sides — which `CANON.md` forbids outright and which breaks the continuity this file
   * claims across chapters ("the triangle is already where the net puts ABC").
   *
   * The net's and the triangle's come from the engine's own panel positions; the ring's from the
   * convention `DEMOS.md` states, which is the only definition it has. Both are the same source the
   * drawing draws from, so what the check catches is not a disagreement between two computations
   * but a **transformation applied after** either of them.
   */
  function whereDotsBelong(kind) {
    if (kind === "ring") {
      const { at } = ringLayout();
      return Object.fromEntries(Object.entries(at).map(([name, point]) => [name, [point]]));
    }
    const wanted = kind === "triangle" ? panels.slice(0, 1) : panels;
    const out = {};
    for (const panel of wanted) {
      [...panel.face].forEach((letter, index) => {
        const [x, u] = panel.positions[index];
        (out[letter] = out[letter] || []).push([x, u * SQRT3]);
      });
    }
    return out;
  }

  return {
    drawNet, drawTriangle, drawRing, drawWire,
    ringLayout, ringPlanarity, ringOuterFace, tipNames, tipPlaces,
    wireframe, wireDefaultView, whereDotsBelong,
  };
}
