// The napkin world, computed in the browser.
//
// This is the whole of the demos' code: the arithmetic, the drawings, the steps, and the little
// machine that walks a reader through them. One module, no framework, no dependency, nothing
// fetched from anywhere.
//
// Two rules govern every line of it.
//
//   1. **The browser computes.** Nothing here reads a number out of `data/napkin.json` and prints
//      it. The complex, the loop sums, the leapfrog, the cut, the crossing, the eight-face sum, the
//      spectrum and the runaway are all worked out here from the same rules `tools/napkin.py` and
//      `tools/octahedron.py` hold. The export exists so that `core.test.mjs` can check this file
//      against them, value by value — not so that this file can quote them.
//
//   2. **Exact, or refused.** Every number is a rational over `BigInt`. There is no floating point
//      in any displayed value, and `numberText` refuses anything it cannot write down exactly and
//      briefly — which is chapter 4's whole finding, arriving in the one place it cannot be argued
//      with. Floats appear only where geometry is drawn, in SVG coordinates, and never in a number
//      a reader is asked to check.
//
// FIREWALL: this computes a toy. Nothing it draws is a claim about nature.

// ── exact rationals ───────────────────────────────────────────────────────────────────────────────

function gcd(a, b) {
  a = a < 0n ? -a : a;
  b = b < 0n ? -b : b;
  while (b) { const t = a % b; a = b; b = t; }
  return a;
}

/** A rational over BigInt, always in lowest terms with a positive denominator. */
export class Frac {
  constructor(numerator, denominator = 1n) {
    let n = BigInt(numerator);
    let d = BigInt(denominator);
    if (d === 0n) throw new Error("a rational with denominator zero");
    if (d < 0n) { n = -n; d = -d; }
    const g = gcd(n, d) || 1n;
    this.n = n / g;
    this.d = d / g;
  }

  /** `"3"`, `"1/2"`, `"-1/2"` — the form `tools/napkin_export.py` writes. */
  static parse(text) {
    const [n, d] = String(text).split("/");
    return new Frac(BigInt(n), d === undefined ? 1n : BigInt(d));
  }

  static of(value) {
    return value instanceof Frac ? value : new Frac(BigInt(value));
  }

  add(other) { const o = Frac.of(other); return new Frac(this.n * o.d + o.n * this.d, this.d * o.d); }
  sub(other) { const o = Frac.of(other); return new Frac(this.n * o.d - o.n * this.d, this.d * o.d); }
  mul(other) { const o = Frac.of(other); return new Frac(this.n * o.n, this.d * o.d); }
  div(other) { const o = Frac.of(other); return new Frac(this.n * o.d, this.d * o.n); }
  neg() { return new Frac(-this.n, this.d); }
  abs() { return this.n < 0n ? this.neg() : this; }
  get sign() { return this.n < 0n ? -1 : (this.n === 0n ? 0 : 1); }
  isZero() { return this.n === 0n; }
  cmp(other) { const o = Frac.of(other); const l = this.n * o.d, r = o.n * this.d; return l < r ? -1 : (l > r ? 1 : 0); }
  eq(other) { return this.cmp(other) === 0; }
  lt(other) { return this.cmp(other) < 0; }
  gt(other) { return this.cmp(other) > 0; }

  /** The exact string, and the only serialisation this module ever compares against the export. */
  toString() { return this.d === 1n ? String(this.n) : `${this.n}/${this.d}`; }

  /** A double, for SVG coordinates ONLY. Never for a number a reader is asked to check. */
  toApprox() { return Number(this.n) / Number(this.d); }
}

export const ZERO = new Frac(0n);
export const ONE = new Frac(1n);
export const HALF = new Frac(1n, 2n);

export function sum(values) {
  return values.reduce((total, value) => total.add(value), ZERO);
}

// ── writing a number down ─────────────────────────────────────────────────────────────────────────

/**
 * The denominators `napkin.number()` will print, and no others.
 *
 * The refusal is the point, and it is chapter 4's finding rather than a formatting rule: a value
 * that needs more than a couple of exact decimal places is not badly formatted, it is a sign the
 * arithmetic has left the napkin. The demos show the refusal where the book shows it.
 */
export const NAPKIN_DENOMINATORS = [1n, 2n, 4n, 5n, 10n, 20n, 100n];

export class NotOnANapkin extends Error {}

/** An exact, short decimal — or a refusal. Mirrors `napkin.number()`, minus sign included. */
export function numberText(value) {
  const v = Frac.of(value);
  const sign = v.n < 0n ? "−" : "";
  const magnitude = v.abs();
  if (magnitude.d === 1n) return `${sign}${magnitude.n}`;
  if (!NAPKIN_DENOMINATORS.includes(magnitude.d)) {
    throw new NotOnANapkin(
      `${v} is not finger-countable (denominator ${magnitude.d}). The napkin tables stay exact and `
      + `short; change the tick size rather than the formatting.`
    );
  }
  // Exact two-place decimal by integer arithmetic: the denominator divides 100.
  const hundredths = (magnitude.n * 100n) / magnitude.d;
  const whole = hundredths / 100n;
  const part = hundredths % 100n;
  if (part === 0n) return `${sign}${whole}`;
  const text = `${part}`.padStart(2, "0").replace(/0$/, "");
  return `${sign}${whole}.${text}`;
}

/** `+3` / `−4` — `numberText` with an explicit plus on the non-negatives. */
export function signedText(value) {
  const v = Frac.of(value);
  return v.sign >= 0 ? `+${numberText(v)}` : numberText(v);
}

/** An exact fraction as a fraction — `1/8`, `2/5` — for the values `numberText` rightly refuses. */
export function fracText(value) {
  const v = Frac.of(value);
  const minus = v.n < 0n ? "−" : "";
  const m = v.abs();
  return m.d === 1n ? `${minus}${m.n}` : `${minus}${m.n}/${m.d}`;
}

/** `numberText`, or the honest admission that it cannot be written. */
export function numberOrRefusal(value) {
  try {
    return { text: numberText(value), printable: true };
  } catch (failure) {
    if (!(failure instanceof NotOnANapkin)) throw failure;
    return { text: "cannot be written in halves", printable: false };
  }
}

/** `value` floored to two significant digits — a round number honestly below it. */
export function floorToTwoDigits(value) {
  const v = Frac.of(value);
  if (v.lt(ONE)) throw new Error("floorToTwoDigits wants a value of at least one");
  const whole = v.n / v.d;
  const digits = String(whole).length;
  const unit = 10n ** BigInt(Math.max(digits - 2, 0));
  const floored = (whole / unit) * unit;
  if (new Frac(floored).gt(v)) throw new Error(`${floored} is not below ${v}`);
  return floored;
}

/** A group-separated integer, for the runaway's floors. */
export function thousands(bigint) {
  return String(bigint).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// ── the object: ascending simplices, and the coboundary ───────────────────────────────────────────

/** Every ascending `size`-subset of `items`, in ascending order. */
export function combinations(items, size) {
  if (size === 0) return [[]];
  const out = [];
  const walk = (start, chosen) => {
    if (chosen.length === size) { out.push(chosen.slice()); return; }
    for (let i = start; i < items.length; i += 1) {
      chosen.push(items[i]);
      walk(i + 1, chosen);
      chosen.pop();
    }
  };
  walk(0, []);
  return out;
}

/**
 * The k-simplices of the complete complex on `vertices`, each ascending, all in ascending order.
 *
 * Ascending vertex order *is* the orientation, which is what makes the alternating signs below the
 * only convention in play — the same rule as `napkin.simplices`.
 */
export function simplices(vertices, k) {
  return combinations([...vertices].sort((a, b) => a - b), k + 1);
}

const key = (cell) => cell.join(",");

/** The matrix of `d` from k-forms on `cellsLo` to (k+1)-forms on `cellsHi`. */
export function coboundary(cellsLo, cellsHi) {
  const index = new Map(cellsLo.map((cell, i) => [key(cell), i]));
  return cellsHi.map((hi) => {
    const row = new Array(cellsLo.length).fill(0);
    for (let i = 0; i < hi.length; i += 1) {
      const face = hi.slice(0, i).concat(hi.slice(i + 1));
      row[index.get(key(face))] += (-1) ** i;
    }
    return row;
  });
}

export function applyMatrix(matrix, values) {
  return matrix.map((row) => sum(row.map((c, i) => Frac.of(values[i]).mul(new Frac(BigInt(c))))));
}

/** The census of the complete complex on `n` dots, with `d∘d = 0` checked on every rung. */
export function census(n = 4) {
  const vertices = Array.from({ length: n }, (_, i) => i);
  const cells = [];
  for (let k = 0; k < n; k += 1) cells.push(simplices(vertices, k));
  const boundaries = [];
  for (let k = 0; k + 1 < n; k += 1) boundaries.push(coboundary(cells[k], cells[k + 1]));

  // `d∘d = 0`, on every pair of consecutive rungs. It holds because the signs cancel, not because
  // a number came out small, so it is checked rather than assumed — as the napkin checks it.
  for (let k = 0; k + 1 < boundaries.length; k += 1) {
    const lower = boundaries[k];
    const upper = boundaries[k + 1];
    for (let col = 0; col < cells[k].length; col += 1) {
      const column = lower.map((row) => new Frac(BigInt(row[col])));
      const composed = applyMatrix(upper, column);
      if (composed.some((entry) => !entry.isZero())) {
        throw new Error(`d∘d ≠ 0 at rung ${k} — the object is not a complex`);
      }
    }
  }
  return { vertices, cells, boundaries };
}

export const NAMES = ["A", "B", "C", "D"];
export const cellName = (cell) => cell.map((v) => NAMES[v]).join("");

// ── the one rule ──────────────────────────────────────────────────────────────────────────────────

/** The chapters' four corner values, and their six freely chosen line-numbers. */
export const CORNERS = [2, 5, 1, 4];
export const ARROWS = [3, 1, 1, 2, 1, 1];

/** One tick: `k = c²dt²` in the engine's `step_scalar_wave`. The chapters' own size. */
export const TICK_K = HALF;
export const TICKS = 10;
export const DIALED_LINE = "AB";

/** `Δ₀ = ⋆₀⁻¹ d₀ᵀ ⋆₁ d₀` with `⋆₀ = 1`: `(Δφ)_i = Σ_j w_ij (φ_i − φ_j)`. */
export function laplacian(values, lines, weights) {
  const out = values.map(() => ZERO);
  lines.forEach(([i, j], index) => {
    const flux = Frac.of(weights[index]).mul(values[j].sub(values[i]));  // ⋆₁ d₀ φ on this line
    out[i] = out[i].sub(flux);                                           // d₀ᵀ, −1 at the low dot
    out[j] = out[j].add(flux);                                           // +1 at the high dot
  });
  return out;
}

/**
 * The engine's leapfrog scalar wave, started from rest, `ticks` times.
 *
 * Started from rest (`φ_old = φ_0`) for the reason the chapter leans on: the rows of `Δ₀` sum to
 * zero, so `Σφ` obeys `S' = 2S − S_prev`, and beginning with `S_prev = S_0` makes the total exactly
 * constant for ever. That is a property of this rule started this way, and it is checked here on
 * every run rather than described.
 */
export function slosh({ lines, weights, initial, ticks = TICKS, k = TICK_K }) {
  const w = weights ?? lines.map(() => ONE);
  let current = initial.map((v) => Frac.of(v));
  let previous = current.slice();
  const history = [current.slice()];
  for (let tick = 0; tick < ticks; tick += 1) {
    const push = laplacian(current, lines, w);
    const next = current.map((c, i) => c.mul(2).sub(previous[i]).sub(Frac.of(k).mul(push[i])));
    previous = current;
    current = next;
    history.push(current.slice());
  }
  const total = sum(history[0]);
  history.forEach((row, tick) => {
    if (!sum(row).eq(total)) {
      throw new Error(`the total changed at tick ${tick} — the step or the Laplacian is wrong`);
    }
  });
  return history;
}

/** The repeat length of a run, or 0 if it has not repeated within the ticks computed. */
export function period(history) {
  const same = (a, b) => a.length === b.length && a.every((v, i) => v.eq(b[i]));
  for (let candidate = 1; candidate < history.length; candidate += 1) {
    let holds = true;
    for (let i = 0; i < history.length; i += 1) {
      if (!same(history[i], history[i % candidate])) { holds = false; break; }
    }
    if (holds) return candidate;
  }
  return 0;
}

/** How many rows of a run `numberText` will print before it refuses. */
export function renderableTicks(history) {
  for (let tick = 0; tick < history.length; tick += 1) {
    for (const value of history[tick]) {
      try { numberText(value); } catch (failure) {
        if (failure instanceof NotOnANapkin) return tick;
        throw failure;
      }
    }
  }
  return history.length;
}

// ── the spectrum, exactly, without an eigensolver ─────────────────────────────────────────────────

export function laplacianMatrix(size, lines) {
  const matrix = Array.from({ length: size }, () => new Array(size).fill(0));
  for (const [i, j] of lines) {
    matrix[i][i] += 1; matrix[j][j] += 1;
    matrix[i][j] -= 1; matrix[j][i] -= 1;
  }
  return matrix;
}

/**
 * Is every eigenvalue of the symmetric `matrix` strictly below `bound`? Exact.
 *
 * Sylvester's criterion on `bound·I − matrix`: a symmetric matrix is positive definite exactly when
 * symmetric elimination produces a positive pivot at every step. No eigensolver, no tolerance, and
 * no floating point — which is what lets the ceiling below be stated as a fact rather than a
 * measurement.
 */
export function spectrumBelow(matrix, bound) {
  const n = matrix.length;
  const m = matrix.map((row, i) => row.map((v, j) => (i === j ? Frac.of(bound) : ZERO).sub(new Frac(BigInt(v)))));
  for (let k = 0; k < n; k += 1) {
    const pivot = m[k][k];
    if (pivot.sign <= 0) return false;
    for (let i = k + 1; i < n; i += 1) {
      if (m[i][k].isZero()) continue;
      const factor = m[i][k].div(pivot);
      for (let j = k; j < n; j += 1) m[i][j] = m[i][j].sub(factor.mul(m[k][j]));
    }
  }
  return true;
}

/**
 * The largest eigenvalue of a graph Laplacian, certified two-sidedly.
 *
 * The candidates are the whole numbers up to twice the largest degree, which is where Gershgorin
 * puts the spectrum; the one that is `λ_max` is the one the exact test rejects and rejects no
 * longer a thousandth above. On these three objects it is 4, 6 and 10 — and it is found, not typed.
 */
export function largestEigenvalue(matrix) {
  const ceiling = 2 * Math.max(...matrix.map((row, i) => row[i]));
  const nudge = new Frac(1n, 1000n);
  for (let candidate = 1; candidate <= ceiling; candidate += 1) {
    const claimed = new Frac(BigInt(candidate));
    if (!spectrumBelow(matrix, claimed) && spectrumBelow(matrix, claimed.add(nudge))) {
      return claimed;
    }
  }
  throw new Error("no whole eigenvalue ceiling was certified below twice the largest degree");
}

/** The leapfrog holds while `k · λ_max < 4`, so the tick each object must stay UNDER is `4/λ_max`. */
export const LEAPFROG_BOUND = new Frac(4n);

export function ceiling(size, lines) {
  const stiffest = largestEigenvalue(laplacianMatrix(size, lines));
  const bound = LEAPFROG_BOUND.div(stiffest);
  const product = TICK_K.mul(stiffest);
  return { size, stiffest, bound, product, holds: product.lt(LEAPFROG_BOUND) };
}

// ── the tetrahedron, and the two coming-home facts ────────────────────────────────────────────────

export function tetrahedron() {
  const c = census(4);
  const [dots, lines, faces, insides] = c.cells;
  const [d0, d1, d2] = c.boundaries;
  const corners = CORNERS.map((v) => new Frac(BigInt(v)));
  const differences = applyMatrix(d0, corners);
  const faceLoops = applyMatrix(d1, differences);
  if (faceLoops.some((loop) => !loop.isZero())) throw new Error("a face loop came out non-zero");

  const arrows = ARROWS.map((v) => new Frac(BigInt(v)));
  const faceNumbers = applyMatrix(d1, arrows);
  if (faceNumbers.some((v) => v.isZero())) {
    throw new Error("a face came out zero — the inside sum would demonstrate less than it claims");
  }
  const insideSum = applyMatrix(d2, faceNumbers);
  if (!insideSum[0].isZero()) throw new Error(`the inside sum came out ${insideSum[0]}`);

  // Each face walked the way the boundary operator takes it — outward — so the four displayed
  // numbers simply add, and the alternating-sign convention leaves the reader's side of it.
  const outward = faceNumbers.map((value, i) => value.mul(new Frac(BigInt(d2[0][i]))));
  if (!sum(outward).isZero()) throw new Error("the four outward face-numbers do not come to zero");

  return {
    dots, lines, faces, insides, d0, d1, d2,
    lineNames: lines.map(cellName),
    faceNames: faces.map(cellName),
    corners, differences, faceLoops, arrows, faceNumbers, outward,
    insideSum: insideSum[0],
    insideIncidence: d2[0],
  };
}

/** The tetrahedron's six lines as index pairs, for the rule and the spectrum. */
export const TETRA_LINES = simplices([0, 1, 2, 3], 1);

export function tetraRuns() {
  const plain = slosh({ lines: TETRA_LINES, initial: CORNERS });
  const dialedIndex = TETRA_LINES.findIndex((line) => cellName(line) === DIALED_LINE);
  const weights = TETRA_LINES.map((_, i) => (i === dialedIndex ? new Frac(2n) : ONE));
  const dialed = slosh({ lines: TETRA_LINES, weights, initial: CORNERS });
  const same = plain.every((row, t) => row.every((v, i) => v.eq(dialed[t][i])));
  if (same) throw new Error("doubling a line changed nothing — the dial is not wired up");
  const average = sum(plain[0]).div(new Frac(4n));
  dialed.forEach((row, tick) => {
    if (!sum(row).div(new Frac(4n)).eq(average)) throw new Error(`the average moved at tick ${tick}`);
  });
  return { plain, dialed, dialedLine: DIALED_LINE, average, period: period(plain) };
}

// ── the shape between: cut the one tetrahedron at its six middles ─────────────────────────────────

/**
 * The four corners on alternate corners of a cube of side 2 — the placement that makes every number
 * below a whole number: the six middles land exactly on `(±1,0,0)`, `(0,±1,0)`, `(0,0,±1)`.
 */
export const TET_CORNERS = { A: [1, 1, 1], B: [1, -1, -1], C: [-1, 1, -1], D: [-1, -1, 1] };

/** The six middles, named for the lines they halve. The names and their order are the napkin's. */
export const MID_NAMES = combinations(["A", "B", "C", "D"], 2).map((pair) => pair.join(""));

export const MID_POINTS = MID_NAMES.map((name) => {
  const u = TET_CORNERS[name[0]];
  const v = TET_CORNERS[name[1]];
  return [0, 1, 2].map((axis) => new Frac(BigInt(u[axis] + v[axis]), 2n));
});

const sharesCorner = (i, j) => [...MID_NAMES[i]].some((letter) => MID_NAMES[j].includes(letter));

/** The octahedron's twelve lines: the pairs of middles whose lines share a corner. */
export function midLines() {
  return combinations([0, 1, 2, 3, 4, 5], 2).filter(([i, j]) => sharesCorner(i, j));
}

function det3(a, b, c) {
  return a[0].mul(b[1].mul(c[2]).sub(b[2].mul(c[1])))
    .sub(a[1].mul(b[0].mul(c[2]).sub(b[2].mul(c[0]))))
    .add(a[2].mul(b[0].mul(c[1]).sub(b[1].mul(c[0]))));
}

/**
 * The octahedron's eight faces, each walked the way round it faces from OUTSIDE.
 *
 * The direction is fixed by an exact integer determinant on the face's own three corners, and then
 * "outside" is *checked*: each cycle's own normal is computed the long way and required to point
 * away from the centre. Flipping the sense would leave the boundary sum zero and every line still
 * walked once each way — consistent, and inward.
 */
export function midFaces() {
  const out = [];
  for (const triple of combinations([0, 1, 2, 3, 4, 5], 3)) {
    if (!combinations(triple, 2).every(([a, b]) => sharesCorner(a, b))) continue;
    const corners = triple.map((i) => MID_POINTS[i]);
    const turn = det3(corners[0], corners[1], corners[2]);
    if (turn.isZero()) throw new Error(`the face ${triple} is flat`);
    const cycle = turn.sign > 0 ? triple : [triple[0], triple[2], triple[1]];
    const [a, b, c] = cycle.map((i) => MID_POINTS[i]);
    const e1 = [0, 1, 2].map((i) => b[i].sub(a[i]));
    const e2 = [0, 1, 2].map((i) => c[i].sub(a[i]));
    const normal = [
      e1[1].mul(e2[2]).sub(e1[2].mul(e2[1])),
      e1[2].mul(e2[0]).sub(e1[0].mul(e2[2])),
      e1[0].mul(e2[1]).sub(e1[1].mul(e2[0])),
    ];
    const outward = sum([0, 1, 2].map((i) => normal[i].mul(a[i].add(b[i]).add(c[i]))));
    if (outward.sign <= 0) {
      throw new Error(`the face ${cycle} is walked so its own normal points back at the centre`);
    }
    out.push(cycle);
  }
  if (out.length !== 8) throw new Error(`the octahedron came out with ${out.length} faces, not 8`);
  return out;
}

function volume(cell) {
  const [a, b, c, d] = cell;
  const det = det3(
    [0, 1, 2].map((i) => b[i].sub(a[i])),
    [0, 1, 2].map((i) => c[i].sub(a[i])),
    [0, 1, 2].map((i) => d[i].sub(a[i])),
  );
  return det.abs().div(new Frac(6n));
}

function squaredLength(a, b) {
  return sum([0, 1, 2].map((i) => a[i].sub(b[i]).mul(a[i].sub(b[i]))));
}

/** Four middles round an equator, put in the order they actually touch each other. */
function ringOrder(four) {
  const ring = [four[0]];
  const remaining = four.slice(1);
  while (remaining.length) {
    const next = remaining.find((index) => sharesCorner(ring[ring.length - 1], index));
    if (next === undefined) throw new Error("the equator does not close into a ring");
    ring.push(next);
    remaining.splice(remaining.indexOf(next), 1);
  }
  if (!sharesCorner(ring[ring.length - 1], ring[0])) throw new Error("the ring does not close");
  return ring;
}

/**
 * Cut the one tetrahedron at its six middles. What falls out, counted exactly.
 *
 * The claim, stated as arithmetic: four tetrahedra at the tips and **one** octahedron between them;
 * the tips are half the side and an eighth of the whole; the octahedron is exactly half; and of its
 * eight faces, four look at a tip and four lie flat in a face of the tetrahedron that was cut.
 * Nothing here is read off a picture.
 */
export function midpointCut() {
  const corners = Object.fromEntries(
    Object.entries(TET_CORNERS).map(([n, p]) => [n, p.map((v) => new Frac(BigInt(v)))]),
  );
  const whole = volume(Object.values(corners));
  const bigSides = new Set(combinations(Object.values(corners), 2)
    .map(([u, v]) => squaredLength(u, v).toString()));
  if (bigSides.size !== 1 || !bigSides.has("8")) {
    throw new Error("the tetrahedron that was cut is not regular");
  }

  const dots = new Set([...Object.values(corners), ...MID_POINTS].map((p) => p.join(",")));
  if (dots.size !== 10) throw new Error(`the cut object has ${dots.size} dots, not 10`);

  const tips = {};
  for (const name of "ABCD") {
    const touching = MID_NAMES.map((mid, i) => [mid, i]).filter(([mid]) => mid.includes(name));
    if (touching.length !== 3) throw new Error(`the corner ${name} is on ${touching.length} lines`);
    const cell = [corners[name], ...touching.map(([, i]) => MID_POINTS[i])];
    if (!volume(cell).eq(whole.div(new Frac(8n)))) {
      throw new Error(`the tip at ${name} is not an eighth of the whole`);
    }
    const sides = new Set(combinations(cell, 2).map(([u, v]) => squaredLength(u, v).toString()));
    if (sides.size !== 1 || !sides.has("2")) throw new Error(`the tip at ${name} is not regular`);
    tips[name] = cell;
  }

  const lines = midLines();
  if (lines.length !== 12) throw new Error(`the middles are joined by ${lines.length} lines, not 12`);
  const degrees = MID_NAMES.map((_, i) => lines.filter((line) => line.includes(i)).length);
  if (new Set(degrees).size !== 1 || degrees[0] !== 4) {
    throw new Error("the middles do not all have four lines");
  }
  const oppositePairs = combinations([0, 1, 2, 3, 4, 5], 2)
    .filter(([i, j]) => !sharesCorner(i, j))
    .map(([i, j]) => [MID_NAMES[i], MID_NAMES[j]]);
  if (oppositePairs.length !== 3) throw new Error("there are not three unjoined pairs of middles");

  const core = whole.sub(whole.div(new Frac(8n)).mul(4));
  if (!core.eq(whole.div(new Frac(2n)))) throw new Error("the shape between is not half the whole");
  // Cut the octahedron into four about one long diagonal: the volumes must still add up, which is
  // the check that "one octahedron" is the whole of what is left rather than most of it.
  const diagonal = [MID_NAMES.indexOf("AB"), MID_NAMES.indexOf("CD")];
  const equator = ringOrder([0, 1, 2, 3, 4, 5].filter((i) => !diagonal.includes(i)));
  const quarters = [0, 1, 2, 3].map((w) => [
    MID_POINTS[diagonal[0]], MID_POINTS[diagonal[1]],
    MID_POINTS[equator[w]], MID_POINTS[equator[(w + 1) % 4]],
  ]);
  if (!sum(quarters.map(volume)).eq(core)) {
    throw new Error("cutting the octahedron into four does not give back its own volume");
  }

  const faces = midFaces();
  const atATip = [];
  const inAFace = [];
  for (const face of faces) {
    const letters = face.map((i) => new Set(MID_NAMES[i]));
    const shared = [...letters[0]].filter((l) => letters[1].has(l) && letters[2].has(l));
    const spanned = new Set(face.flatMap((i) => [...MID_NAMES[i]]));
    if (shared.length === 1) {
      if (spanned.size !== 4) throw new Error("a tip face does not span four letters");
      atATip.push({ face, name: shared[0] });
    } else {
      if (spanned.size !== 3) throw new Error("a face spans neither three nor four letters");
      inAFace.push({ face, name: [...spanned].sort().join("") });
    }
  }
  if (atATip.length !== 4 || inAFace.length !== 4) {
    throw new Error(`${atATip.length} faces look at a tip and ${inAFace.length} lie flat`);
  }

  return {
    dots: dots.size, corners: 4, middles: 6, tips: 4, octahedra: 1,
    tipShare: new Frac(1n, 8n), tipSide: HALF, coreShare: HALF,
    octDots: 6, octLines: 12, octFaces: 8, octDegree: 4,
    oppositePairs,
    facesAtATip: atATip.map((e) => e.name).sort(),
    facesInAFace: inAFace.map((e) => e.name).sort(),
    lines, faces, tipCells: tips, whole, core,
  };
}

/** Twelve freely chosen arrows, one per line — arrows in their own right, not differences. */
export const MID_ARROWS = [3, 1, 4, 1, 5, 2, 6, 5, 3, 5, 8, 9];

/**
 * The eight outside faces add to exactly zero, for every set of arrows.
 *
 * Chapter 2's inside sum, one shape out. And not nearly zero: **each line is walked exactly twice,
 * once each way**, which is checked line by line here rather than argued. No length is used in it.
 */
export function octahedronFaceSum() {
  const lines = midLines();
  const faces = midFaces();
  const arrows = new Map(lines.map((line, i) => [key(line), new Frac(BigInt(MID_ARROWS[i]))]));

  const walk = (face) => {
    const terms = [];
    for (let step = 0; step < 3; step += 1) {
      const low = face[step];
      const high = face[(step + 1) % 3];
      const value = arrows.get(key([Math.min(low, high), Math.max(low, high)]));
      terms.push(low < high ? value : value.neg());
    }
    return terms;
  };

  const faceTerms = faces.map(walk);
  const faceNumbers = faceTerms.map(sum);
  if (faceNumbers.some((v) => v.isZero())) {
    throw new Error("a face came out zero — the sum below would demonstrate less than it claims");
  }
  const walked = new Map(lines.map((line) => [key(line), 0]));
  for (const face of faces) {
    for (let step = 0; step < 3; step += 1) {
      const low = face[step];
      const high = face[(step + 1) % 3];
      const k = key([Math.min(low, high), Math.max(low, high)]);
      walked.set(k, walked.get(k) + (low < high ? 1 : -1));
    }
  }
  if ([...walked.values()].some((v) => v !== 0)) {
    throw new Error("a line is not walked once each way — the sum would then be an accident");
  }
  const total = sum(faceNumbers);
  if (!total.isZero()) throw new Error(`the eight outside faces summed to ${total}`);

  // Each line lies in one face of the tetrahedron that was cut: four groups of three.
  const groups = new Map();
  lines.forEach((line, i) => {
    const letters = [...new Set([...MID_NAMES[line[0]], ...MID_NAMES[line[1]]])].sort().join("");
    if (letters.length !== 3) throw new Error(`the line ${line} does not span a face`);
    if (!groups.has(letters)) groups.set(letters, []);
    groups.get(letters).push({ line, name: `${MID_NAMES[line[0]]}–${MID_NAMES[line[1]]}`, value: arrows.get(key(line)) });
  });
  if ([...groups.values()].some((items) => items.length !== 3)) {
    throw new Error("a face of the tetrahedron does not hold three of the octahedron's lines");
  }

  return {
    lines, faces, arrows, faceTerms, faceNumbers, total,
    linesWalkedEachWay: lines.length,
    groups: [...groups.entries()].sort(([a], [b]) => (a < b ? -1 : 1)),
  };
}

/**
 * Poke one middle at the chapters' own tick. Three facts inside it are the beat: at tick 2 the whole
 * poke is on the **opposite** middle and nowhere else, at tick 3 it is home, and the pair
 * (now, before) does not repeat until 12 — which is why the table is not over at 3.
 */
export function octahedronPoke(k = TICK_K, ticks = 12) {
  const lines = midLines();
  const poked = MID_NAMES.indexOf("AB");
  const opposite = MID_NAMES.indexOf("CD");
  const initial = MID_NAMES.map((_, i) => (i === poked ? ONE : ZERO));
  const history = slosh({ lines, initial, ticks, k });

  const denominators = new Set(history.flat().map((v) => v.d));
  for (const d of denominators) {
    if (d !== 1n && d !== 2n) throw new Error(`the run left whole numbers and halves: ${d}`);
  }
  const crossed = MID_NAMES.map((_, i) => (i === opposite ? ONE : ZERO));
  if (!history[2].every((v, i) => v.eq(crossed[i]))) {
    throw new Error("tick 2 is not all on the opposite middle");
  }
  if (!history[3].every((v, i) => v.eq(initial[i]))) throw new Error("tick 3 is not home");
  if (history[1][poked].sign >= 0) {
    throw new Error("the poked middle did not go negative on the way across, so 'the whole of it "
      + "crosses' would be describing a run that never left");
  }
  const repeat = period(history);
  if (ticks >= 12 && repeat !== 12) throw new Error(`the period came out ${repeat}, not 12`);
  return {
    k, poked: MID_NAMES[poked], opposite: MID_NAMES[opposite],
    crossingTicks: 2, homeTicks: 3, period: repeat, history,
  };
}

// ── the two, threaded ─────────────────────────────────────────────────────────────────────────────

/**
 * Fill the four faces that lie flat and a second tetrahedron appears, threaded through the first.
 *
 * Each new corner is one of the original corners pushed through the middle and out the other side,
 * and the four of them are a regular tetrahedron the same size as the one that was cut, whose own
 * six middles are the *same* six middles.
 */
export function secondTetrahedron() {
  const corners = Object.fromEntries(
    Object.entries(TET_CORNERS).map(([n, p]) => [n, p.map((v) => new Frac(BigInt(v)))]),
  );
  const whole = volume(Object.values(corners));
  const apexes = {};
  for (const { face, name } of midpointCut().faces
    .map((face) => {
      const spanned = new Set(face.flatMap((i) => [...MID_NAMES[i]]));
      return { face, name: spanned.size === 3 ? [...spanned].sort().join("") : null };
    })
    .filter((entry) => entry.name)) {
    const missing = [..."ABCD"].find((letter) => !name.includes(letter));
    const apex = corners[missing].map((v) => v.neg());
    const cell = [...face.map((i) => MID_POINTS[i]), apex];
    if (!volume(cell).eq(whole.div(new Frac(8n)))) {
      throw new Error(`the tetrahedron added on ${name} is not an eighth of the whole`);
    }
    const sides = new Set(combinations(cell, 2).map(([u, v]) => squaredLength(u, v).toString()));
    if (sides.size !== 1 || !sides.has("2")) {
      throw new Error(`the tetrahedron added on ${name} is not regular`);
    }
    apexes[`${missing}′`] = { apex, over: name };
  }
  const twin = Object.values(apexes).map((e) => e.apex);
  const twinSides = new Set(combinations(twin, 2).map(([u, v]) => squaredLength(u, v).toString()));
  if (twinSides.size !== 1 || !twinSides.has("8")) {
    throw new Error("the four new corners are not a regular tetrahedron the size of the one we cut");
  }
  if (!volume(twin).eq(whole)) throw new Error("the second tetrahedron is not the same size");
  const twinMiddles = new Set(combinations(twin, 2)
    .map(([u, v]) => [0, 1, 2].map((i) => u[i].add(v[i]).div(new Frac(2n))).join(",")));
  const ours = new Set(MID_POINTS.map((p) => p.join(",")));
  if (twinMiddles.size !== ours.size || [...twinMiddles].some((p) => !ours.has(p))) {
    throw new Error("the second tetrahedron's own six middles are not the same six middles");
  }
  return { added: 4, apexes, apexNames: Object.keys(apexes).sort(), apexShare: new Frac(1n, 8n) };
}

/** The stella in the reader's own names: the six middles, the four corners, and the four new tips. */
export const STELLA_NAMES = [...MID_NAMES, ..."ABCD", ...[..."ABCD"].map((c) => `${c}′`)];

export function stellaPoints() {
  const corners = [..."ABCD"].map((c) => TET_CORNERS[c].map((v) => new Frac(BigInt(v))));
  const twin = corners.map((p) => p.map((v) => v.neg()));
  return [...MID_POINTS, ...corners, ...twin];
}

/** The stella's thirty-six lines: the shortest joins, all of squared length 2. */
export function stellaLines() {
  const points = stellaPoints();
  return combinations([...points.keys()], 2)
    .filter(([i, j]) => squaredLength(points[i], points[j]).eq(new Frac(2n)));
}

export function stellaCensus() {
  const points = stellaPoints();
  if (new Set(points.map((p) => p.join(","))).size !== 14) {
    throw new Error("the stella's dots are not 14 distinct points");
  }
  const lines = stellaLines();
  if (lines.length !== 36) throw new Error(`the stella came out with ${lines.length} lines, not 36`);
  const degree = (i) => lines.filter((line) => line.includes(i)).length;
  const middleDegrees = new Set([0, 1, 2, 3, 4, 5].map(degree));
  const tipDegrees = new Set([6, 7, 8, 9, 10, 11, 12, 13].map(degree));
  if (middleDegrees.size !== 1 || !middleDegrees.has(8)) throw new Error("a middle has not 8 lines");
  if (tipDegrees.size !== 1 || !tipDegrees.has(3)) throw new Error("a tip has not 3 lines");
  for (const [i, j] of lines) {
    if (i >= 6 && j >= 6) {
      throw new Error(`${STELLA_NAMES[i]} and ${STELLA_NAMES[j]} are joined — no two tips are`);
    }
  }

  // Both volumes are built from the fourteen points piece by piece rather than from each other:
  // eight tips as eight actual tetrahedra, the core as the four the cut makes of it, and the hull
  // cube from the spread of the tips along each axis.
  const whole = volume([6, 7, 8, 9].map((i) => points[i]));
  const tips = [];
  for (let apex = 6; apex < 14; apex += 1) {
    const touching = [0, 1, 2, 3, 4, 5]
      .filter((i) => squaredLength(points[i], points[apex]).eq(new Frac(2n)));
    if (touching.length !== 3) throw new Error("a tip touches other than three middles");
    tips.push(volume([points[apex], ...touching.map((i) => points[i])]));
  }
  const diagonal = [MID_NAMES.indexOf("AB"), MID_NAMES.indexOf("CD")];
  const ring = ringOrder([0, 1, 2, 3, 4, 5].filter((i) => !diagonal.includes(i)));
  const core = sum([0, 1, 2, 3].map((w) => volume([
    MID_POINTS[diagonal[0]], MID_POINTS[diagonal[1]],
    MID_POINTS[ring[w]], MID_POINTS[ring[(w + 1) % 4]],
  ])));
  const stella = sum(tips).add(core);
  const spread = [0, 1, 2].map((axis) => {
    const values = points.slice(6).map((p) => p[axis]);
    return values.reduce((a, b) => (a.gt(b) ? a : b)).sub(values.reduce((a, b) => (a.lt(b) ? a : b)));
  });
  const cube = spread[0].mul(spread[1]).mul(spread[2]);
  if (!whole.eq(new Frac(8n, 3n)) || !stella.eq(new Frac(4n)) || !cube.eq(new Frac(8n))) {
    throw new Error(`the volumes came out ${whole}, ${stella}, ${cube}`);
  }
  const inItsCube = stella.div(cube);
  const inTetrahedra = stella.div(whole);
  if (!inItsCube.eq(HALF)) throw new Error(`the pair fills ${inItsCube} of its cube, not a half`);
  if (!inTetrahedra.eq(new Frac(3n, 2n))) throw new Error(`the pair is ${inTetrahedra}, not 3/2`);

  return {
    dots: 14, lines: lines.length, middles: 6, tips: 8, pieces: 9,
    middleDegree: 8, tipDegree: 3, inItsCube, inTetrahedra,
    edges: lines, hull: "a cube",
  };
}

export const RUNAWAY_TICKS = 20;
export const RUNAWAY_LOOK = [0, 1, 2, 3, 10, RUNAWAY_TICKS];

/**
 * Poke the same dot on the stella at the same tick, and watch it leave the napkin twice over.
 *
 * **It runs away**: the tick is over this object's ceiling, so the biggest number in the world grows
 * without bound. **And it cannot be written down**: the first push is 8 at the poked dot and −1 at
 * each of its eight neighbours, so the halves become quarters and then eighths, and `numberText`
 * refuses the fourth row. Neither is a shortage of patience.
 */
export function stellaRunaway(k = TICK_K, ticks = RUNAWAY_TICKS) {
  const lines = stellaLines();
  const initial = STELLA_NAMES.map((_, i) => (i === 0 ? ONE : ZERO));
  const history = slosh({ lines, initial, ticks, k });
  const biggest = history.map((row) => row.map((v) => v.abs()).reduce((a, b) => (a.gt(b) ? a : b)));
  if (!biggest[0].eq(ONE)) throw new Error("the poke was not 1");
  for (const tick of [5, 10, 15, ticks].filter((t) => t <= ticks)) {
    if (!biggest[tick].gt(biggest[tick - 5])) throw new Error(`the run shrank before tick ${tick}`);
  }
  const printable = renderableTicks(history);
  if (ticks >= RUNAWAY_TICKS) {
    if (!biggest[RUNAWAY_TICKS].gt(new Frac(100000000n))) {
      throw new Error("the biggest number is not past a hundred million — the claim is overstated");
    }
    if (printable !== 3) throw new Error(`${printable} rows print, not 3`);
  }
  return {
    k, ticks, history, biggest, printableRows: printable,
    pushAtAMiddle: lines.filter((line) => line.includes(0)).length,
    look: RUNAWAY_LOOK.filter((t) => t <= ticks).map((tick) => ({ tick, biggest: biggest[tick] })),
  };
}

/** How far the search for a repeat runs before it reports that there is none. */
export const REPEAT_SEARCH_TICKS = 60;

/** Every smaller tick the chapter tries: two rows at most, and none of them ever comes home. */
export function stellaSmallerTicks() {
  const lines = stellaLines();
  const initial = STELLA_NAMES.map((_, i) => (i === 0 ? ONE : ZERO));
  const bound = new Frac(2n, 5n);
  return [
    new Frac(39n, 100n), new Frac(7n, 20n), new Frac(1n, 4n), new Frac(1n, 5n), new Frac(1n, 10n),
  ].map((k) => {
    if (!k.lt(bound)) throw new Error(`${k} is not under the ceiling`);
    const short = slosh({ lines, initial, ticks: 10, k });
    const long = slosh({ lines, initial, ticks: REPEAT_SEARCH_TICKS, k });
    const printable = renderableTicks(short);
    if (printable > 2) throw new Error(`k = ${k} printed ${printable} rows`);
    const repeat = period(long);
    if (repeat !== 0) throw new Error(`k = ${k} came home after ${repeat} steps`);
    return { k, printable, period: repeat };
  });
}

// ── the drawings ──────────────────────────────────────────────────────────────────────────────────
//
// Two conventions, and no third.
//
//   * **The tetrahedron is CANON.md's flat unfolded net** — the same six positions, the same labels
//     A B C D, one fill for all four panels, every label upright, and the diagram never rotated or
//     mirrored. The coordinates are `tools/canon.py`'s, in its own exact ring: `(x, u)` stands for
//     the plane point `(x, u·√3)`. A number belonging to a piece is written directly under that
//     piece's name, at the name's own canonical position, so CANON.md's three placement rules are
//     untouched.
//
//   * **The octahedron and the stella are drawn on the ring** — six dots on two concentric circles,
//     each dot on the same line through the centre as the one dot no line joins it to, and all
//     twelve lines drawn once with no crossing at all. `demos/DEMOS.md` states it in full and says
//     why a net was refused for this object.
//
// Nothing in either drawing means anything beyond the shape. There is one panel fill, one stroke,
// and one highlight; no colour encodes a property, and none ever will.

const SQRT3 = 1.7320508075688772935;

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

// ── the canonical net ─────────────────────────────────────────────────────────────────────────────

const NET_SIDE = 3;
const NET_ANCHOR = { 0: [0, 0], 1: [NET_SIDE, 0], 2: [NET_SIDE / 2, NET_SIDE / 2] };
const NET_SCALE = 100;
const NET_PAD = 0.45;
const VERTEX_INSET = 0.25;
const LINE_INSET = 0.25;

const ringSub = (p, q) => [p[0] - q[0], p[1] - q[1]];
const ringAdd = (p, q) => [p[0] + q[0], p[1] + q[1]];
const ringScale = (p, t) => [p[0] * t, p[1] * t];
const ringDot = (p, q) => p[0] * q[0] + 3 * p[1] * q[1];
const ringMid = (p, q) => ringScale(ringAdd(p, q), 0.5);

function ringCentroid(points) {
  return ringScale(points.reduce(ringAdd, [0, 0]), 1 / points.length);
}

/** `point` mirrored in the line through `a` and `b`. The ring is closed under this. */
function ringReflect(point, a, b) {
  const direction = ringSub(b, a);
  const offset = ringSub(point, a);
  const along = (2 * ringDot(offset, direction)) / ringDot(direction, direction);
  return ringAdd(a, ringSub(ringScale(direction, along), offset));
}

/**
 * The four triangles of the net, in face order, each as `{ face, positions }`.
 *
 * The central panel is the anchor. Each other panel shares two dots with it and folds out across
 * that shared line, so its third corner is *the reflection of the central panel's remaining corner*
 * in that line — which is what makes the four triangles congruent by construction.
 */
export function netPanels() {
  const faces = simplices([0, 1, 2, 3], 2);
  const central = faces[0];
  return faces.map((face) => {
    if (face.every((v, i) => v === central[i])) {
      return { face, positions: face.map((v) => NET_ANCHOR[v]) };
    }
    const shared = face.filter((v) => v in NET_ANCHOR);
    const opposite = central.find((v) => !shared.includes(v));
    const apex = ringReflect(NET_ANCHOR[opposite], NET_ANCHOR[shared[0]], NET_ANCHOR[shared[1]]);
    return { face, positions: face.map((v) => (v in NET_ANCHOR ? NET_ANCHOR[v] : apex)) };
  });
}

/** The nine lines the net actually draws: three once, and three twice, once on each folded panel. */
export function netSegments() {
  const panels = netPanels();
  const central = panels[0];
  const centralLines = new Set(simplices(central.face, 1).map(key));
  const out = [];
  for (const { face, positions } of panels) {
    const place = Object.fromEntries(face.map((v, i) => [v, positions[i]]));
    for (const line of simplices(face, 1)) {
      if (face !== central.face && centralLines.has(key(line))) continue;
      out.push({ line, from: place[line[0]], to: place[line[1]], panel: face });
    }
  }
  return out;
}

/** Where every name goes: nineteen labels, placed by CANON.md's three rules and nothing else. */
export function netLabels() {
  const panels = netPanels();
  const central = panels[0];
  const owners = new Map();
  const dotAt = new Map();
  for (const { face, positions } of panels) {
    face.forEach((vertex, i) => {
      const k = positions[i].join(",");
      if (!owners.has(k)) owners.set(k, []);
      owners.get(k).push(face);
      dotAt.set(k, vertex);
    });
  }
  const out = [];
  for (const { face, positions } of panels) {
    const centroid = ringCentroid(positions);
    for (const position of positions) {
      const candidates = owners.get(position.join(","));
      const chosen = candidates.includes(central.face) ? central.face : candidates[0];
      if (chosen !== face) continue;
      out.push({
        kind: "dot",
        cell: [dotAt.get(position.join(","))],
        text: NAMES[dotAt.get(position.join(","))],
        at: ringAdd(position, ringScale(ringSub(centroid, position), VERTEX_INSET)),
        panelCentre: centroid,
      });
    }
  }
  // Indexed by the panel's NAME, not by object identity: `netSegments()` builds its own panels, so
  // the two lists are equal and not the same, and identity would silently find nothing.
  const byFace = new Map(panels.map(({ face, positions }) => [cellName(face), positions]));
  for (const { line, from, to, panel } of netSegments()) {
    const positions = byFace.get(cellName(panel));
    const midpoint = ringMid(from, to);
    const centroid = ringCentroid(positions);
    out.push({
      kind: "line", cell: line, text: cellName(line),
      at: ringAdd(midpoint, ringScale(ringSub(centroid, midpoint), LINE_INSET)),
      panelCentre: centroid,
    });
  }
  for (const { face, positions } of panels) {
    out.push({
      kind: "face", cell: face, text: cellName(face),
      at: ringCentroid(positions), panelCentre: ringCentroid(positions),
    });
  }
  return out;
}

/**
 * The frame a set of net positions is drawn in: `canon.py`'s own extent arithmetic.
 *
 * Taken over the positions a drawing actually uses rather than always over the whole net, so
 * chapter 1's triangle fills its frame instead of sitting in the corner of a frame shaped for four
 * panels. The scale, the padding and the flip are the same in both, which is what keeps the
 * triangle in the place the net will later put it: `AB` horizontal, `A` on the left, `C` above.
 */
/** A fixed step of `distance` from `from` toward `to`, in projected coordinates. */
function stepToward(from, to, distance) {
  const dx = to[0] - from[0];
  const dy = to[1] - from[1];
  const length = Math.hypot(dx, dy) || 1;
  return [from[0] + (dx / length) * distance, from[1] + (dy / length) * distance];
}

function netFrame(positions, pad = NET_PAD) {
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

const NET_EXTENT = netFrame(netPanels().flatMap((p) => p.positions));

function project(frame, position) {
  return [
    (position[0] - frame.xMin + frame.pad) * NET_SCALE,
    (frame.yMax + frame.pad - position[1] * SQRT3) * NET_SCALE,
  ];
}

const netProject = (position) => project(NET_EXTENT, position);

/**
 * The canonical net, drawn, with whatever numbers this step has to put on it.
 *
 * `values` maps a piece's name to the text to write under that piece's own name — so a number sits
 * exactly where the thing it belongs to sits, and the name above it has not moved. `emphasis` is the
 * one highlight the drawing has: a set of names drawn heavier. There is no second colour.
 */
export function drawNet({ values = {}, emphasis = [], panels = true, midpoints = false,
  medials = false, title = "The tetrahedron, unfolded flat", desc = "" } = {}) {
  const strong = new Set(emphasis);
  const body = [];
  body.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d2(NET_EXTENT.width * NET_SCALE)} ${d2(NET_EXTENT.height * NET_SCALE)}" role="img" class="net">`);
  body.push(`  <title>${esc(title)}</title>`);
  body.push(`  <desc>${esc(desc || "The four faces of one tetrahedron laid out flat: the triangle ABC in the middle, with the three others folded out from its sides. Every dot, line and face carries its name. The dot D appears three times, because flat paper puts one corner of the solid in three places. All four triangles are drawn identically: nothing in the drawing means anything beyond the shape.")}</desc>`);

  if (panels) {
    body.push('  <g class="panel">');
    for (const panel of netPanels()) {
      const points = panel.positions.map((p) => netProject(p).map(d2).join(",")).join(" ");
      body.push(`    <polygon points="${points}"/>`);
    }
    body.push("  </g>");
  }

  body.push('  <g class="stroke">');
  for (const segment of netSegments()) {
    const [x1, y1] = netProject(segment.from);
    const [x2, y2] = netProject(segment.to);
    const heavy = strong.has(cellName(segment.line)) ? ' class="strong"' : "";
    body.push(`    <line${heavy} x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
  }
  if (medials) {
    // The cut, on the flat paper: each panel's medial triangle is where the blade goes, and the
    // three corner triangles it leaves are the three faces of that panel's tips.
    body.push('    <g class="cut">');
    for (const panel of netPanels()) {
      const mids = [[0, 1], [1, 2], [2, 0]].map(([a, b]) => ringMid(panel.positions[a], panel.positions[b]));
      const points = mids.map((p) => netProject(p).map(d2).join(",")).join(" ");
      body.push(`      <polygon points="${points}"/>`);
    }
    body.push("    </g>");
  }
  body.push("  </g>");

  if (midpoints) {
    body.push('  <g class="middle">');
    for (const segment of netSegments()) {
      const [x, y] = netProject(ringMid(segment.from, segment.to));
      body.push(`    <circle cx="${d2(x)}" cy="${d2(y)}" r="9"/>`);
    }
    body.push("  </g>");
  }

  body.push('  <g class="labels">');
  for (const label of netLabels()) {
    // The NAME never moves: its position is CANON.md's, and a number is not a reason to shift it.
    // The number goes a fixed step from it, into the panel the name belongs to — which is why it
    // never lands on a stroke, and why four labels on one panel do not pile onto its middle. An
    // earlier version moved the pair inward together and did exactly that.
    const [x, y] = netProject(label.at);
    const [cx, cy] = netProject(label.panelCentre);
    const size = label.kind === "dot" ? 34 : (label.kind === "face" ? 28 : 24);
    const value = values[label.text];
    const heavy = strong.has(label.text) ? ' class="strong"' : "";
    const weight = label.kind === "dot" ? ' font-weight="700"' : "";
    body.push(`    <text${heavy}${weight} x="${d2(x)}" y="${d2(y)}" font-size="${size}" text-anchor="middle" dominant-baseline="central">${esc(label.text)}</text>`);
    if (value !== undefined) {
      // A line's or a face's number goes straight under its name — a fixed drop, the same every
      // time. Stepping a line's number further into the panel put three of them on the face's name,
      // and stepping it sideways put one on the next line's name across the fold; a face's name is
      // AT the panel's middle, so there is no "further in" for it to step to at all, and the number
      // landed on top of the name. Down is none of those.
      const [vx, vy] = label.kind === "dot"
        ? stepToward([x, y], [cx, cy], size * 0.95)
        : [x, y + size * 1.05];
      body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="${size * 0.85}" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
    }
  }
  body.push("  </g>");
  body.push("</svg>");
  return body.join("\n");
}

/**
 * Chapter 1's world: one dot, two dots and a line, or the triangle.
 *
 * Drawn as the central panel of the net that is coming — same anchor, same names, same orientation
 * — but framed to the part it uses, so the triangle fills the picture rather than sitting in the
 * corner of a frame shaped for four panels. Nothing is learned twice: when the fourth dot arrives
 * in the next chapter, this triangle is already where the net puts `ABC`.
 */
export function drawTriangle({ dots = 3, values = {}, showLine = true, showFace = false,
  arrows = [], title = "" } = {}) {
  const central = netPanels()[0];
  const used = central.positions.slice(0, dots);
  const frame = netFrame(dots === 1 ? [[-1, -0.5], [1, 0.5]] : used, 0.7);
  const at = (position) => project(frame, position);
  const pairs = dots === 2 ? [[0, 1]] : (dots >= 3 ? [[0, 1], [1, 2], [0, 2]] : []);
  const lineNameOf = ([a, b]) => [NAMES[a], NAMES[b]].sort().join("");
  const centroid = ringCentroid(used.length >= 3 ? used : central.positions);

  const body = [];
  body.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d2(frame.width * NET_SCALE)} ${d2(frame.height * NET_SCALE)}" role="img" class="net">`);
  body.push(`  <title>${esc(title || "The first things you can draw")}</title>`);
  body.push(`  <desc>${esc(`${dots === 1 ? "One dot" : dots === 2 ? "Two dots joined by one line" : "Three dots joined by three lines, with an inside"}, drawn where the tetrahedron's flat net will later put them: AB horizontal, A on the left, C above. Nothing in the drawing means anything beyond the shape.`)}</desc>`);

  if (dots >= 3 && showFace) {
    body.push(`  <g class="panel"><polygon points="${used.map((p) => at(p).map(d2).join(",")).join(" ")}"/></g>`);
  }

  body.push('  <g class="stroke">');
  if (showLine) {
    for (const [a, b] of pairs) {
      const [x1, y1] = at(used[a]);
      const [x2, y2] = at(used[b]);
      body.push(`    <line x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
    }
  }
  body.push("  </g>");

  // Chapter 1's dots are drawn as dots. That reads like a triviality and is not one: the first
  // picture in the book answers "where could you put a number?", and it answered it with a letter
  // floating in an empty box, because the net this drawing borrows its positions from has no dot
  // marks — in the net a corner is where lines meet, and there is always a line. Here there is not.
  body.push('  <g class="middle">');
  for (const position of used) {
    const [x, y] = at(position);
    body.push(`    <circle cx="${d2(x)}" cy="${d2(y)}" r="10"/>`);
  }
  body.push("  </g>");

  // The walk, when a step asks for it. A small fixed-size head three-quarters of the way along each
  // step, pointing the way the walk goes — and nothing else. It says "this way round"; it does not
  // say anything about the line it sits on.
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
      body.push(`    <polygon class="head" points="${d2(tipX)},${d2(tipY)} ${d2(baseX - uy * 9)},${d2(baseY + ux * 9)} ${d2(baseX + uy * 9)},${d2(baseY - ux * 9)}"/>`);
    }
    body.push("  </g>");
  }

  body.push('  <g class="labels">');
  used.forEach((position, index) => {
    const value = values[NAMES[index]];
    // With one dot and no lines there is no inside to sit in, so the name sits above the dot; with
    // three there is, and the name takes the canonical inset. Either way the number goes a fixed
    // step further in, so neither lands on a stroke and neither lands on the dot.
    const [dx, dy] = at(position);
    const [ax, ay] = dots === 1
      ? [dx, dy - 34]
      : at(ringAdd(position, ringScale(ringSub(centroid, position), VERTEX_INSET)));
    body.push(`    <text font-weight="700" x="${d2(ax)}" y="${d2(ay)}" font-size="34" text-anchor="middle" dominant-baseline="central">${NAMES[index]}</text>`);
    if (value !== undefined) {
      const [vx, vy] = dots === 1
        ? [dx, dy + 36]
        : stepToward([ax, ay], at(centroid), 32);
      body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="30" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
    }
  });
  if (showLine) {
    for (const pair of pairs) {
      const name = lineNameOf(pair);
      const midpoint = ringMid(used[pair[0]], used[pair[1]]);
      const [x, y] = at(ringAdd(midpoint, ringScale(ringSub(centroid, midpoint), LINE_INSET)));
      const value = values[name];
      body.push(`    <text x="${d2(x)}" y="${d2(y)}" font-size="24" text-anchor="middle" dominant-baseline="central">${name}</text>`);
      if (value !== undefined) {
        const [vx, vy] = [x, y + 26];
        body.push(`    <text class="value" x="${d2(vx)}" y="${d2(vy)}" font-size="24" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
      }
    }
  }
  if (dots >= 3 && showFace) {
    const [x, y] = at(ringCentroid(used));
    const value = values.ABC;
    body.push(`    <text x="${d2(x)}" y="${d2(y + (value === undefined ? 0 : -12))}" font-size="28" text-anchor="middle" dominant-baseline="central">ABC</text>`);
    if (value !== undefined) {
      body.push(`    <text class="value" x="${d2(x)}" y="${d2(y + 18)}" font-size="26" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
    }
  }
  body.push("  </g>");
  body.push("</svg>");
  return body.join("\n");
}

// ── the ring: the one convention for the octahedron and the stella ────────────────────────────────
//
// Six dots on two concentric circles. The outer three are the middles of the three lines that leave
// A — AB, AC, AD — and the inner three are the three they are joined to nothing by, each placed on
// the same ray out of the centre as its partner and on the other side of it. So "opposite" is
// literally straight through the middle, which is the one thing beats 38 and 39 need a reader to see.
//
// All twelve lines are drawn once and none of them crosses another. Seven of the eight faces are
// regions you can point at; the eighth is the outside of the paper, and the drawing says so rather
// than pretending otherwise. `demos/DEMOS.md` has the full statement.

const RING_OUTER = 170;

// The inner radius is the one number in the ring that can be got wrong, and it was: at exactly half
// the outer radius each inner dot lands *on the outer triangle's edge*, because that edge's midpoint
// is at half the radius in exactly that direction. The twelve lines then draw as six segments — the
// outer edge and the two spokes along it become one stroke — and the drawing quietly stops showing
// which lines the object has. `ringPlanarity()` below turns that from a thing to remember into a
// thing that fails.
const RING_INNER = 63;

// Where a tip goes, by measurement rather than by hope.
//
// A tip belongs inside its own face, and four of the eight faces have room for one: the three fat
// regions of the ring and the small triangle in the middle. The other four do not. Three of them are
// thin slivers between an outer line and the inner dot facing it, and the eighth is the outside of
// the paper, which has no inside to sit in. Putting a labelled dot in a sliver anyway is how a
// drawing becomes unreadable, so those four sit outside the ring instead, each on the ray out of the
// centre through its own face — except the outside face, whose three dots average to the centre
// exactly and so names no ray. That one is placed straight above, and it is the single arbitrary
// choice in the whole convention.
const TIP_CLEARANCE = 17;          // the radius a tip's dot and its label need inside a face
const TIP_DOT_CLEARANCE = 3;       // how close a dot may come to a line it does not end
const TIP_OUTSIDE = RING_OUTER + 62;
const TIP_ABOVE = RING_OUTER + 132;

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

/** Which of the eight faces is the outside of the paper: the one all of whose dots are on the rim. */
function ringOuterFace(at, faces) {
  const rim = (RING_OUTER + RING_INNER) / 2;
  const index = faces.findIndex((f) => f.every((i) => Math.hypot(...at[MID_NAMES[i]]) > rim));
  if (index < 0) throw new Error("no face of the ring is the outside of the paper");
  return index;
}

/**
 * Where the tip over each face is drawn, and whether it sits inside that face or outside the ring.
 *
 * The outside face is forced out first, and that is not an optimisation: its three dots are the rim
 * of the drawing, so its own triangle *looks* like the roomiest of the eight when it is in fact the
 * one region with no inside at all — everything else is in there. A tip placed at that triangle's
 * middle would sit in the centre of the picture claiming to be over the outermost face.
 */
function tipPlaces(at, faces) {
  const outside = ringOuterFace(at, faces);
  return faces.map((face, index) => {
    const points = face.map((i) => at[MID_NAMES[i]]);
    if (index === outside) return { at: [0, -TIP_ABOVE], inside: false, chosen: true };
    const { radius, centre } = incircle(points);
    if (radius >= TIP_CLEARANCE) return { at: centre, inside: true };
    const mean = [0, 1].map((axis) => (points[0][axis] + points[1][axis] + points[2][axis]) / 3);
    const away = Math.hypot(...mean);
    return { at: [(mean[0] / away) * TIP_OUTSIDE, (mean[1] / away) * TIP_OUTSIDE], inside: false };
  });
}

/** Where each middle sits, and which middle each is opposite. Derived, not typed. */
export function ringLayout() {
  const outer = ["AB", "AC", "AD"];
  const angles = { AB: 90, AC: 210, AD: 330 };
  const opposite = Object.fromEntries(midpointCut().oppositePairs.flatMap(([a, b]) => [[a, b], [b, a]]));
  const at = {};
  for (const name of outer) {
    const theta = (angles[name] * Math.PI) / 180;
    at[name] = [RING_OUTER * Math.cos(theta), -RING_OUTER * Math.sin(theta)];
    const partner = opposite[name];
    at[partner] = [-RING_INNER * Math.cos(theta), RING_INNER * Math.sin(theta)];
  }
  return { at, outer, inner: outer.map((n) => opposite[n]), opposite };
}

/** The frame the ring is drawn in: everything the drawing puts on the paper, plus a margin. */
function ringFrame(points) {
  const pad = 42;
  const xs = points.map((point) => point[0]);
  const ys = points.map((point) => point[1]);
  const minX = Math.min(...xs) - pad;
  const minY = Math.min(...ys) - pad;
  return {
    minX, minY,
    width: (Math.max(...xs) - minX) + pad,
    height: (Math.max(...ys) - minY) + pad,
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

/**
 * How many of the drawn lines cross, and whether any dot is sitting on a line it does not end.
 *
 * The ring's whole claim is that it draws all twelve of the octahedron's lines separately and none
 * of them crosses another, so a reader can count the lines off the picture. That claim is checked
 * here rather than eyeballed — and `demos/core.test.mjs` holds the bare octahedron to *no* crossings
 * and the threaded pair to exactly the two the outside tip forces.
 */
export function ringPlanarity({ tips = false } = {}) {
  const { at } = ringLayout();
  const faces = midFaces();
  const outerFace = ringOuterFace(at, faces);
  const places = tips ? tipPlaces(at, faces) : null;
  const tipAt = (index) => places[index].at;
  const drawn = midLines().map(([i, j]) => ({
    from: at[MID_NAMES[i]], to: at[MID_NAMES[j]], tip: null,
  }));
  if (tips) {
    faces.forEach((face, index) => {
      for (const i of face) drawn.push({ from: tipAt(index), to: at[MID_NAMES[i]], tip: index });
    });
  }
  const dots = MID_NAMES.map((name) => at[name])
    .concat(tips ? faces.map((_, index) => tipAt(index)) : []);

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
      const ends = [line.from, line.to].some((p) => Math.hypot(p[0] - dot[0], p[1] - dot[1]) < 0.001);
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
    lines: drawn.length,
    crossings,
    amongTheTwelve,
    dotsOnLines,
    dotsOnTheTwelve,
    tipsInsideTheirFace: places ? places.filter((place) => place.inside).length : 0,
    outerFace,
  };
}

/**
 * The octahedron, or the two tetrahedra threaded through it, on the ring.
 *
 * `values` maps a dot's name to the text written beside it. `emphasis` names dots or lines drawn
 * heavier, and `face` names one of the eight faces to point at — the outside one included, which is
 * drawn as its three edges rather than as a filled region, because its region is everything else.
 */
export function drawRing({ values = {}, emphasis = [], face = null, tips = false,
  title = "", desc = "" } = {}) {
  const { at, opposite } = ringLayout();
  const lines = midLines();
  const faces = midFaces();
  const strong = new Set(emphasis);
  const twin = tips ? secondTetrahedron() : null;

  // Which tip sits over which face: the face's three middles either share one letter (and the tip
  // is that corner of the tetrahedron we cut) or span three (and the tip is the corner that was
  // pushed through the middle and out the other side).
  const tipOf = faces.map((f) => {
    const letters = f.map((i) => new Set(MID_NAMES[i]));
    const shared = [...letters[0]].filter((l) => letters[1].has(l) && letters[2].has(l));
    if (shared.length === 1) return shared[0];
    const spanned = new Set(f.flatMap((i) => [...MID_NAMES[i]]));
    return `${[..."ABCD"].find((c) => !spanned.has(c))}′`;
  });
  if (twin) {
    const expected = new Set(twin.apexNames.concat([..."ABCD"]));
    if (tipOf.length !== 8 || new Set(tipOf).size !== 8 || tipOf.some((n) => !expected.has(n))) {
      throw new Error("the eight tips are not the four corners and the four pushed-through ones");
    }
  }
  const outerFace = ringOuterFace(at, faces);

  const places = tips ? tipPlaces(at, faces) : null;
  const tipAt = (index) => places[index].at;

  // The frame is taken from what the drawing actually puts on the paper, so the ring is the same
  // size whether or not the tips are shown — a reader is looking at one object, not two — and the
  // picture has no empty margin where the tips would have been.
  const frame = ringFrame([
    ...MID_NAMES.flatMap((name) => {
      const away = Math.hypot(...at[name]) || 1;
      const label = at[name].map((v) => v + (v / away) * 26);
      return [at[name], label, [label[0], label[1] + 22], [label[0], label[1] - 22]];
    }),
    ...(places ? places.map((entry) => entry.at) : []),
  ]);
  const place = (point) => [point[0] - frame.minX, point[1] - frame.minY];

  // The claim the convention makes, checked before anything is drawn: twelve lines drawn once each,
  // no dot sitting on a line it does not end, and no crossing at all — except the two the outside
  // tip forces, when the tips are shown.
  const planar = ringPlanarity({ tips });
  if (planar.dotsOnTheTwelve) {
    throw new Error(`${planar.dotsOnTheTwelve} dot(s) sit on one of the twelve lines without ending `
      + `it — the ring is degenerate and those twelve lines would draw as fewer`);
  }
  if (planar.amongTheTwelve) {
    throw new Error(`${planar.amongTheTwelve} of the twelve lines cross each other; the ring's `
      + `whole claim is that none of them does`);
  }

  const body = [];
  body.push(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${d2(frame.width)} ${d2(frame.height)}" role="img" class="ring">`);
  body.push(`  <title>${esc(title || (tips ? "The two tetrahedra, threaded" : "The shape between the tips"))}</title>`);
  body.push(`  <desc>${esc(desc || (tips
    ? "The six middles on two circles, with a tip drawn inside each of the eight regions they make and joined to that region's three middles. No two tips are joined. One tip has to sit outside the ring, because one face is always the outside of the paper — and even so, no line in the drawing crosses another."
    : "The six middles on two circles: each sits on the same line through the centre as the one middle no line joins it to, so opposite means straight through the middle. All twelve lines are drawn once and none crosses another."))}</desc>`);

  if (face !== null && face !== outerFace) {
    const points = faces[face].map((i) => place(at[MID_NAMES[i]]).map(d2).join(",")).join(" ");
    body.push(`  <g class="panel"><polygon points="${points}"/></g>`);
  }

  body.push('  <g class="stroke">');
  for (const [i, j] of lines) {
    const a = MID_NAMES[i];
    const b = MID_NAMES[j];
    const heavy = (face !== null && faces[face].includes(i) && faces[face].includes(j))
      || strong.has(`${a}–${b}`) || strong.has(`${b}–${a}`);
    const [x1, y1] = place(at[a]);
    const [x2, y2] = place(at[b]);
    body.push(`    <line${heavy ? ' class="strong"' : ""} x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
  }
  if (tips) {
    for (let index = 0; index < faces.length; index += 1) {
      const [tx, ty] = place(tipAt(index));
      for (const i of faces[index]) {
        const [x, y] = place(at[MID_NAMES[i]]);
        body.push(`    <line class="tip-line" x1="${d2(tx)}" y1="${d2(ty)}" x2="${d2(x)}" y2="${d2(y)}"/>`);
      }
    }
  }
  body.push("  </g>");

  // The three pairs no line joins, drawn as what they are: nothing. A faint mark straight through
  // the centre says where a line would have been, and it is the only mark in the drawing that
  // stands for an absence — labelled as such in the step's own table.
  body.push('  <g class="absent">');
  for (const [a, b] of midpointCut().oppositePairs) {
    const [x1, y1] = place(at[a]);
    const [x2, y2] = place(at[b]);
    body.push(`    <line x1="${d2(x1)}" y1="${d2(y1)}" x2="${d2(x2)}" y2="${d2(y2)}"/>`);
  }
  body.push("  </g>");

  body.push('  <g class="dots">');
  for (const name of MID_NAMES) {
    const [x, y] = place(at[name]);
    body.push(`    <circle${strong.has(name) ? ' class="strong"' : ""} cx="${d2(x)}" cy="${d2(y)}" r="13"/>`);
  }
  if (tips) {
    for (let index = 0; index < faces.length; index += 1) {
      const [x, y] = place(tipAt(index));
      body.push(`    <circle class="tip" cx="${d2(x)}" cy="${d2(y)}" r="10"/>`);
    }
  }
  body.push("  </g>");

  body.push('  <g class="labels">');
  for (const name of MID_NAMES) {
    const [x, y] = place(at[name]);
    // Outward, for every middle. Inward for the inner three put their names in the middle of the
    // drawing, which is exactly where the tip over the inner face sits.
    const away = 26;
    const ux = at[name][0] === 0 ? 0 : Math.sign(at[name][0]);
    const uy = at[name][1] === 0 ? 0 : Math.sign(at[name][1]);
    const lx = x + ux * away * 0.9;
    const ly = y + uy * away * 0.9 + (uy === 0 ? -away : 0);
    const value = values[name];
    body.push(`    <text${strong.has(name) ? ' class="strong"' : ""} font-weight="700" x="${d2(lx)}" y="${d2(ly)}" font-size="19" text-anchor="middle" dominant-baseline="central">${esc(name)}</text>`);
    if (value !== undefined) {
      body.push(`    <text class="value" x="${d2(lx)}" y="${d2(ly + 19)}" font-size="17" text-anchor="middle" dominant-baseline="central">${esc(value)}</text>`);
    }
  }
  if (tips) {
    for (let index = 0; index < faces.length; index += 1) {
      const [x, y] = place(tipAt(index));
      body.push(`    <text class="tip" x="${d2(x)}" y="${d2(y + (index === outerFace ? -22 : 0))}" font-size="15" text-anchor="middle" dominant-baseline="central">${esc(tipOf[index])}</text>`);
    }
  }
  if (face !== null && face === outerFace) {
    body.push(`    <text class="note" x="${d2(frame.width / 2)}" y="${d2(frame.height - 14)}" font-size="16" text-anchor="middle">${esc(faces[face].map((i) => MID_NAMES[i]).join(" · "))} — the outside of the paper</text>`);
  }
  body.push("  </g>");
  body.push("</svg>");
  return body.join("\n");
}

// The three numbers these pages write that are not values of the object at all, each with its
// reason. They are declared HERE, above the step definitions, because the rule that governs those
// definitions is absolute: no digit may appear in any piece of text a step produces — a table cell,
// a caption, a heading, its own title, its prose, its notes, or anything it draws. Naming these
// three is what lets the rule be absolute rather than approximate. A fourth means writing down what
// it counts, here and in `core.test.mjs`, which checks that the two lists still agree.
const NONE = "0";   // how many exceptions, edges, clocks, lengths and assumptions there are: none
const ONLY = "1";   // how many rules the law has
const PAIR = "2";   // the two coming-home facts, and the two shapes chapter 4 ends with

// ── the steps ─────────────────────────────────────────────────────────────────────────────────────
//
// One entry per beat of OUTLINE.md, in the outline's order, and a step shows exactly what its own
// beat has earned — no count, no table and no shape from a beat further down the page. The title is
// the reader's question from the outline; the body is the answer in the book's one voice.
//
// Each step returns `{ drawing, tables, notes }`, and every number it shows appears in a table as
// text, not only inside a drawing.

const table = (caption, head, rows) => ({ caption, head, rows });

/** How many k-cells a complex has — including none, which is the answer chapter 1 needs twice. */
const rung = (complex, k) => (complex.cells[k] ?? []).length;

function walkRows(names, terms, totals) {
  return names.map((name, i) => [name, terms[i].map(signedText).join(" "), numberText(totals[i])]);
}

function historyTable(caption, names, history, from = 0, to = null) {
  const end = to === null ? history.length : to;
  const rows = [];
  for (let tick = from; tick < end; tick += 1) {
    rows.push([String(tick), ...history[tick].map((v) => numberText(v)), numberText(sum(history[tick]))]);
  }
  return table(caption, ["tick", ...names, "total"], rows);
}

/** Chapter 1 — Two dots, a line, and the first thing that closes. Beats 9–18. */
function chapterOne() {
  const one = census(1);
  const two = census(2);
  const three = census(3);
  const triangle = { values: [2, 5, 1].map((v) => new Frac(BigInt(v))) };
  const walk = [[0, 1], [1, 2], [2, 0]];
  triangle.steps = walk.map(([a, b]) => ({
    from: NAMES[a], to: NAMES[b], difference: triangle.values[b].sub(triangle.values[a]),
  }));
  triangle.sum = sum(triangle.steps.map((s) => s.difference));
  const another = { values: [7, 7, -2].map((v) => new Frac(BigInt(v))) };
  another.steps = walk.map(([a, b]) => ({
    from: NAMES[a], to: NAMES[b], difference: another.values[b].sub(another.values[a]),
  }));
  another.sum = sum(another.steps.map((s) => s.difference));

  return [
    {
      beat: 9,
      title: "Where could you put a number?",
      body: "On a dot. That is the whole answer, and it is the smallest thing you can start with — "
        + "somewhere for a number to be. Nothing else about it matters yet: not where it is, not how "
        + "big it is, not what is near it. There is no near.",
      render: () => ({
        drawing: drawTriangle({ dots: 1, values: { A: numberText(triangle.values[0]) }, showLine: false, title: "One dot, holding one number" }),
        tables: [table("one dot", ["what", "how many"], [
          ["dots", String(rung(one, 0))],
          ["lines", String(rung(one, 1))],
          ["faces", String(rung(one, 2))],
        ]), table("the number on it", ["dot", "number"], [["A", numberText(triangle.values[0])]])],
        notes: ["Computed here, in this page, from the same rule the book's napkin uses."],
      }),
    },
    {
      beat: 10,
      title: "Where does change live — is it at a place?",
      body: "No. A change is a difference between two numbers, so it needs two places to be a "
        + "difference between. Draw the second dot and join them: the join is where the change lives. "
        + "It is not at A and it is not at B. It is on AB.",
      render: () => {
        const values = [2, 5].map((v) => new Frac(BigInt(v)));
        const difference = values[1].sub(values[0]);
        return {
          drawing: drawTriangle({
            dots: 2,
            values: { A: numberText(values[0]), B: numberText(values[1]), AB: signedText(difference) },
            title: "Two dots and the line between them",
          }),
          tables: [table("the difference on the line", ["step", "arithmetic", "difference"], [
            ["A → B", `${numberText(values[1])} − ${numberText(values[0])}`, signedText(difference)],
          ])],
          notes: ["The line's number is not a third number anyone chose. It is what the two dots' numbers make."],
        };
      },
    },
    {
      beat: 11,
      title: "Two dots and a line — can anything come back to where it started?",
      body: "Walk from A to B. Now walk on. There is nowhere to walk on to except back the way you "
        + "came, and going back the way you came undoes the step rather than closing a loop. This "
        + "world has no loop in it at all, and that is a count you can check rather than a feeling.",
      render: () => ({
        drawing: drawTriangle({ dots: 2, title: "Two dots and a line: nothing closes" }),
        tables: [table("what the world holds", ["what", "how many"], [
          ["dots", String(rung(two, 0))],
          ["lines", String(rung(two, 1))],
          ["faces", String(rung(two, 2))],
          // Lines minus dots plus one — the number of independent loops a connected shape has, and
          // here it comes out as the answer the beat is about rather than as a claim.
          ["loops that come back", String(rung(two, 1) - rung(two, 0) + 1)],
        ])],
        notes: ["Nothing closes yet. Which is the reason for the next dot."],
      }),
    },
    {
      beat: 12,
      title: "Add a third dot. What is the smallest thing that closes?",
      body: "A triangle. Three dots, three lines — and, the moment the third line is drawn, "
        + "something new that was not there before: an inside. You did not add the inside. It arrived "
        + "because the lines closed.",
      render: () => ({
        drawing: drawTriangle({ dots: 3, showFace: true, title: "The triangle: the first thing that closes" }),
        tables: [table("the triangle", ["dots", "lines", "faces"], [[
          String(rung(three, 0)), String(rung(three, 1)), String(rung(three, 2)),
        ]]), table("its lines, in the one order", ["line"], three.cells[1].map((line) => [cellName(line)]))],
        notes: ["The names come from the dots, in ascending order, so every name is written once."],
      }),
    },
    {
      beat: 13,
      title: "Put a number on each corner — how many differences do I have?",
      body: "Three: one for each line. You chose three numbers and the world worked out three more, "
        + "and it had no choice about them. This is the first time the object does arithmetic for you.",
      render: () => ({
        drawing: drawTriangle({
          dots: 3, showFace: true,
          values: Object.fromEntries([
            ...NAMES.slice(0, 3).map((n, i) => [n, numberText(triangle.values[i])]),
            ...triangle.steps.slice(0, 2).map((s) => [[s.from, s.to].sort().join(""), signedText(s.difference)]),
            ["AC", signedText(triangle.values[2].sub(triangle.values[0]))],
          ]),
          title: "Three corner numbers, three differences",
        }),
        tables: [
          table("the corners", ["dot", "number"], NAMES.slice(0, 3).map((n, i) => [n, numberText(triangle.values[i])])),
          table("the differences", ["line", "arithmetic", "difference"], three.cells[1].map((line) => {
            const [a, b] = line;
            return [cellName(line), `${numberText(triangle.values[b])} − ${numberText(triangle.values[a])}`,
              signedText(triangle.values[b].sub(triangle.values[a]))];
          })),
        ],
        notes: [],
      }),
    },
    {
      beat: 14,
      title: "Walk around the triangle adding the differences — what do I get?",
      body: "Zero. Go A to B to C and back to A, adding what each step costs you, and you finish "
        + "holding nothing. You are back where you started, so the going-up and the coming-down have "
        + "to cancel.",
      render: () => ({
        drawing: drawTriangle({
          dots: 3, showFace: true, arrows: walk,
          values: Object.fromEntries(NAMES.slice(0, 3).map((n, i) => [n, numberText(triangle.values[i])])),
          title: "The walk round the triangle",
        }),
        tables: [table("the walk", ["step", "arithmetic", "difference"], [
          ...triangle.steps.map((s, i) => {
            const [a, b] = walk[i];
            return [`${s.from} → ${s.to}`,
              `${numberText(triangle.values[b])} − ${numberText(triangle.values[a])}`,
              signedText(s.difference)];
          }),
          ["all the way round", triangle.steps.map((s) => signedText(s.difference)).join(" "), numberText(triangle.sum)],
        ])],
        notes: [],
      }),
    },
    {
      beat: 15,
      title: "Would any three numbers do that?",
      body: "Every time. Here are three others, as unlike the first three as you like, and the walk "
        + "still finishes at nothing. It is not something about the three numbers you started with. "
        + "It is something about coming home.",
      render: () => ({
        drawing: drawTriangle({
          dots: 3, showFace: true, arrows: walk,
          values: Object.fromEntries(NAMES.slice(0, 3).map((n, i) => [n, numberText(another.values[i])])),
          title: "The same walk, on three other numbers",
        }),
        tables: [
          table("the first three, from before", ["step", "difference"],
            triangle.steps.map((s) => [`${s.from} → ${s.to}`, signedText(s.difference)])
              .concat([["all the way round", numberText(triangle.sum)]])),
          table("three others", ["step", "difference"],
            another.steps.map((s) => [`${s.from} → ${s.to}`, signedText(s.difference)])
              .concat([["all the way round", numberText(another.sum)]])),
        ],
        notes: ["Both walks are worked out here, now, from the corner numbers — not looked up."],
      }),
    },
    {
      beat: 16,
      title: "Why exactly zero and not nearly?",
      body: "Because every corner's number is added once and taken away once, and nothing else "
        + "happens. Look at the column for each dot: a plus and a minus, and the pair is gone. That "
        + "is not a small remainder. It is no remainder, the way whole numbers cancel.",
      render: () => {
        const boundary = census(3).boundaries[0];
        const rows = NAMES.slice(0, 3).map((name, dot) => {
          const appearances = boundary.map((row) => row[dot]).filter((sign) => sign !== 0);
          return [name, appearances.map((s) => (s > 0 ? "+" : "−")).join(" "),
            String(appearances.reduce((a, b) => a + b, 0))];
        });
        return {
          drawing: drawTriangle({
            dots: 3, showFace: true, arrows: walk,
            values: Object.fromEntries(NAMES.slice(0, 3).map((n, i) => [n, numberText(triangle.values[i])])),
            title: "Every corner counted once each way",
          }),
          tables: [table("how each corner's number is used", ["dot", "how it appears", "what is left of it"], rows)],
          notes: ["The signs come from the object's own bookkeeping, not from the numbers on it — which is why the answer cannot depend on them."],
        };
      },
    },
    {
      beat: 17,
      title: "What did I never use?",
      body: "Length. No line in this world has one. Nothing above measured anything, compared "
        + "anything, or needed the triangle to be any particular shape — and if you gave the "
        + "three lines lengths later, the walk would still come to zero, because the zero comes from "
        + "coming home and not from size.",
      render: () => ({
        drawing: drawTriangle({
          dots: 3, showFace: true, arrows: walk,
          values: Object.fromEntries(NAMES.slice(0, 3).map((n, i) => [n, numberText(triangle.values[i])])),
          title: "The same triangle, no lengths anywhere in it",
        }),
        tables: [table("what the walk used", ["what", "used?"], [
          ["the numbers on the corners", "yes"],
          ["which dots each line joins", "yes"],
          ["which way round the walk goes", "yes"],
          ["how long a line is", "no"],
          ["what angle two lines meet at", "no"],
          ["where any of it is", "no"],
        ])],
        notes: [],
      }),
    },
    {
      beat: 18,
      title: "What have I assumed so far?",
      body: "Nothing. Not a distance, not a direction, not a moment of time. Three dots, three "
        + "lines, an inside, and one fact that came out exact. That is not a sketch of a better "
        + "world to be filled in later. It is a small complete one.",
      render: () => ({
        drawing: drawTriangle({ dots: 3, showFace: true, title: "The whole world, so far" }),
        tables: [table("the world so far", ["what it has", "how many"], [
          ["places a number can sit", String(rung(three, 0))],
          ["places a change can sit", String(rung(three, 1))],
          ["insides", String(rung(three, 2))],
          ["assumptions", NONE],
        ])],
        notes: ["Next: the same question one dimension up."],
      }),
    },
  ];
}

/** Chapter 2 — One tetrahedron is a whole world. Beats 19–26. */
function chapterTwo() {
  const t = tetrahedron();
  const kinds = census(4).cells.length;
  const places = [0, 1, 2, 3].reduce((total, k) => total + rung(census(4), k), 0);
  const corners = Object.fromEntries(NAMES.map((n, i) => [n, numberText(t.corners[i])]));
  const differences = Object.fromEntries(t.lineNames.map((n, i) => [n, signedText(t.differences[i])]));
  const arrows = Object.fromEntries(t.lineNames.map((n, i) => [n, numberText(t.arrows[i])]));

  return [
    {
      beat: 19,
      title: "What is the triangle's shape one dimension up?",
      body: "Add a fourth dot and join it to all three. You get four dots, six lines, four triangles "
        + "— and, once the fourth triangle closes, an inside the triangle never had: a solid one. "
        + "Drawn flat, all four faces are the same size and every one of them is visible.",
      render: () => ({
        drawing: drawNet({ title: "The tetrahedron, unfolded flat" }),
        tables: [table("what closed", ["what", "the triangle", "the tetrahedron"],
          [["dots", 0], ["lines", 1], ["faces", 2], ["solid inside", 3]].map(([what, k]) =>
            [what, String(rung(census(3), k)), String(rung(census(4), k))]))],
        notes: ["The dot D is in three places on the flat paper. It is one dot; the paper puts one corner of the solid in three places."],
      }),
    },
    {
      beat: 20,
      title: "Count everything on it — can I hold the whole thing in my head?",
      body: "Four, six, four, one. You can hold that. And the two coming-home facts hold on it too "
        + "— round each face, and round the solid inside — which the next two steps do in "
        + "front of you.",
      render: () => ({
        drawing: drawNet({ title: "The census, on the net" }),
        tables: [
          table("the tetrahedron's census", ["dots", "lines", "faces", "solid inside"],
            [[0, 1, 2, 3].map((k) => String(rung(census(4), k)))]),
          table("the six lines, in the one order", ["line"], t.lineNames.map((n) => [n])),
          table("the four faces, in the one order", ["face"], t.faceNames.map((n) => [n])),
        ],
        notes: ["Every name is the dots it is made of, in ascending order, so it is written down only once."],
      }),
    },
    {
      beat: 21,
      title: "Four numbers on the corners, six differences on the lines: what does each face say?",
      body: "Zero, four times. Each face is a triangle, each triangle is a walk that comes home, and "
        + "coming home is what made the answer zero the first time. Nothing about going up a dimension "
        + "changed that.",
      render: () => ({
        drawing: drawNet({ values: { ...corners, ...differences }, title: "Corner numbers and the differences they force" }),
        tables: [
          table("the corners", ["dot", "number"], NAMES.map((n) => [n, corners[n]])),
          table("the differences they force", ["line", "difference"], t.lineNames.map((n) => [n, differences[n]])),
          table("each face, walked", ["face", "its three line-numbers", "loop, walked round"],
            t.faceNames.map((name, i) => [name,
              t.d1[i].map((sign, j) => (sign ? signedText(t.differences[j].mul(new Frac(BigInt(sign)))) : null))
                .filter(Boolean).join(" "),
              numberText(t.faceLoops[i])])),
        ],
        notes: [],
      }),
    },
    {
      beat: 22,
      title: "What if the six line-numbers came first — six arrows, not six differences?",
      body: "Then a face's walk need not come to zero, and it does not. Six numbers chosen freely are "
        + "not the differences of anything, so nothing has to cancel — and what a face's walk "
        + "comes to is a number that belongs to the face: how much goes round it.",
      render: () => ({
        drawing: drawNet({ values: arrows, title: "Six arrows in their own right" }),
        tables: [
          table("the six arrows", ["line", "arrow"], t.lineNames.map((n) => [n, arrows[n]])),
          table("what goes round each face", ["face", "its three arrows, signed", "how much goes round it"],
            t.faceNames.map((name, i) => [name,
              t.d1[i].map((sign, j) => (sign ? signedText(t.arrows[j].mul(new Frac(BigInt(sign)))) : null))
                .filter(Boolean).join(" "),
              numberText(t.faceNumbers[i])])),
        ],
        notes: ["None of the four is zero, which is the point: a zero there would demonstrate nothing."],
      }),
    },
    {
      beat: 23,
      title: "And the four face-numbers around the inside — add them up the same way?",
      body: "Zero again. Walk each face the way it faces from outside and the four numbers simply "
        + "add, because every line gets walked once in each direction by the two faces that meet along "
        + "it. Coming home, one rung up.",
      render: () => {
        const outward = Object.fromEntries(t.faceNames.map((n, i) => [n, numberText(t.outward[i])]));
        return {
          drawing: drawNet({ values: { ...arrows, ...outward }, title: "The four faces, walked from outside" }),
          tables: [
            table("each face, walked from outside", ["walked", "how much goes round it"],
              t.faceNames.map((name, i) => {
                const sign = t.insideIncidence[i];
                const letters = [...name];
                const cycle = sign > 0 ? letters : [letters[0], letters[2], letters[1]];
                return [[...cycle, cycle[0]].join(" → "), numberText(t.outward[i])];
              })),
            table("and add the four up", ["the four, added", "what is left"], [[
              t.outward.map(signedText).join(" ").replace(/^\+/, ""), numberText(t.insideSum),
            ]]),
          ],
          notes: ["Still no length anywhere in it."],
        };
      },
    },
    {
      beat: 24,
      title: "So how many kinds of number does this world have?",
      body: "Four, and there will never be a fifth. A number can sit on a dot, on a line, on a face, "
        + "or on the inside — and the object has nothing else to sit on. Each kind is turned into "
        + "the next by the same walk you have done twice.",
      render: () => ({
        drawing: drawNet({ title: "The four kinds of place" }),
        tables: [table("where a number can sit", ["kind of place", "how many", "what the walk turns it into"],
          [["a dot", "a number on each line"], ["a line", "a number on each face"],
           ["a face", "a number on the inside"], ["the inside", "nothing — there is no rung above it"]]
            .map(([kind, into], k) => [kind, String(rung(census(4), k)), into]))],
        notes: ["Both zeros above are the same sentence, one rung apart: walk twice and you get nothing."],
      }),
    },
    {
      beat: 25,
      title: "Now give the six lines lengths — is a long line worth the same as a short one?",
      body: "That is a choice, not a fact. Somewhere you have to say how much each line counts, and "
        + "nothing in the object says it for you. Here is the dial in miniature: one number per line, "
        + "six of them, and every one of them set the same until somebody moves one.",
      render: () => ({
        drawing: drawNet({
          values: Object.fromEntries(t.lineNames.map((n) => [n, numberText(ONE)])),
          title: "The dial, one number per line",
        }),
        tables: [table("how much each line counts", ["line", "counts"],
          t.lineNames.map((n) => [n, numberText(ONE)]))],
        notes: ["Nothing is moving yet, and nothing has been turned: a dial with nothing running is "
          + "just a setting. Turning one is the next chapter's business."],
      }),
    },
    {
      beat: 26,
      title: "Is this really a complete world?",
      body: "Every kind of number it can have, both coming-home facts, and one dial. On a napkin. "
        + "What it does not have is anything happening, and that is the next thing missing.",
      render: () => ({
        drawing: drawNet({ title: "One tetrahedron: a whole world" }),
        tables: [table("what the world has", ["what", "how many"], [
          ["kinds of place a number can sit", String(kinds)],
          ["places, all told", String(places)],
          ["coming-home facts, checked here", PAIR],
          ["dials", `${t.lines.length} — one per line`],
          ["lengths used", NONE],
          ["clocks", NONE],
        ])],
        notes: [`${places} places: ${[0, 1, 2, 3].map((k) => rung(census(4), k)).join(" + ")}.`],
      }),
    },
  ];
}

/** Chapter 3 — Make it move. Beats 27–35. */
function chapterThree() {
  const t = tetrahedron();
  const runs = tetraRuns();
  const places = [0, 1, 2, 3].reduce((total, k) => total + rung(census(4), k), 0);
  const corners = Object.fromEntries(NAMES.map((n, i) => [n, numberText(t.corners[i])]));

  const runStep = (beat, title, body, history, extra = []) => ({
    beat, title, body, ticks: history.length - 1,
    render: (tick = 0) => ({
      drawing: drawNet({
        values: Object.fromEntries(NAMES.map((n, i) => [n, numberText(history[tick][i])])),
        title: `Tick ${tick}`,
      }),
      tables: [
        table("this tick", ["dot", "number"], NAMES.map((n, i) => [n, numberText(history[tick][i])])
          .concat([["the four, added", numberText(sum(history[tick]))]])),
        historyTable("every tick, computed here", NAMES, history),
        ...extra,
      ],
      notes: [`Tick ${tick} of ${history.length - 1}. Nothing between the ticks: the rule has no in-between, and the drawing does not pretend it has.`],
    }),
  });

  return [
    {
      beat: 27,
      title: "What is still missing before anything can happen?",
      body: "A clock. Everything so far is a still picture: numbers sitting on places, and two facts "
        + "about them that were true the moment you wrote them down. Nothing in the object says what "
        + "happens next, because nothing in it says there is a next.",
      render: () => ({
        drawing: drawNet({ values: corners, title: "A still picture" }),
        tables: [table("what the world has", ["what", "how many"], [
          ["places", String(places)], ["numbers on them", String(t.corners.length)],
          ["clocks", NONE], ["nexts", NONE],
        ])],
        notes: [],
      }),
    },
    {
      beat: 28,
      title: "What is the least a clock needs?",
      body: "Ticks, all the same size. Not a smooth flow — a list of moments, one after another, "
        + "each the same distance from the last. That is the least, and it is all this world gets.",
      render: () => ({
        drawing: drawNet({ values: corners, title: "Before the first tick" }),
        tables: [table("the clock", ["what", "value"], [
          ["ticks, all the same size", "yes"],
          ["how much one tick counts for", fracText(TICK_K)],
          ["anything between two ticks", "nothing"],
        ])],
        notes: [`One tick counts for ${fracText(TICK_K)}. Where that number comes from is the next chapter's business; here it is a setting.`],
      }),
    },
    {
      beat: 29,
      title: "What should one tick do?",
      body: "One rule, and it is a sentence: each dot's number is pushed toward its neighbours' by "
        + "the differences on its lines, and it carries forward the motion it has already built up. "
        + "The push sets the change in the change, not the change. That one word is the difference "
        + "between a wave and a leak.",
      render: () => {
        const push = laplacian(t.corners, TETRA_LINES, TETRA_LINES.map(() => ONE));
        return {
          drawing: drawNet({
            values: { ...corners, ...Object.fromEntries(t.lineNames.map((n, i) => [n, signedText(t.differences[i])])) },
            title: "The push, worked out from the differences",
          }),
          tables: [
            table("the differences on the lines", ["line", "difference"],
              t.lineNames.map((n, i) => [n, signedText(t.differences[i])])),
            table("the push at each dot", ["dot", "number now", "the push on it"],
              NAMES.map((n, i) => [n, numberText(t.corners[i]), signedText(push[i])])),
            table("the whole rule", ["what", "value"], [
              ["how much one tick counts for", fracText(TICK_K)],
              ["the four pushes, added", numberText(sum(push))],
            ]),
          ],
          notes: ["The four pushes add to nothing, which is why nothing will leak: the rule can move a number from one dot to another and it cannot make one."],
        };
      },
    },
    {
      beat: 30,
      title: "Is that really the whole law — nothing else, ever?",
      body: "Yes. There is no second rule waiting, no correction, no special case at the edges "
        + "— there are no edges. Every result in the book is that one sentence, run.",
      render: () => ({
        drawing: drawNet({ values: corners, title: "One rule, and no other" }),
        tables: [table("the law, in full", ["what", "value"], [
          ["rules", ONLY],
          ["exceptions", NONE],
          ["edges to treat specially", NONE],
          ["how much one tick counts for", fracText(TICK_K)],
          ["how much each line counts", `${numberText(ONE)} each, until you turn the dial`],
        ])],
        notes: [],
      }),
    },
    runStep(31,
      "Run it on the tetrahedron — four numbers, tick by tick: what do they do?",
      "They slosh. Watch the four numbers on the net: they swing past each other, overshoot, and "
      + `come back — and every ${runs.period} ticks they are exactly where they started. Nothing `
      + "leaks away, because there is nowhere for it to leak to.",
      runs.plain,
      [table("the repeat", ["what", "value"], [
        ["how much one tick counts for", fracText(TICK_K)],
        ["how many ticks until it is exactly back at the start", String(runs.period)],
        ["how much every line counts", numberText(ONE)],
      ])]),
    {
      beat: 32,
      title: "Add the four up at every tick — what happens to the total?",
      body: "It never changes. Not nearly, and not on average: the same number at every tick, "
        + "computed afresh at each one. Coming home, in time — the third time this world has "
        + "given you an exact zero for the same reason.",
      ticks: runs.plain.length - 1,
      render: (tick = 0) => ({
        drawing: drawNet({
          values: Object.fromEntries(NAMES.map((n, i) => [n, numberText(runs.plain[tick][i])])),
          title: `Tick ${tick}: the total is ${numberText(sum(runs.plain[tick]))}`,
        }),
        tables: [
          historyTable("every tick, and its total", NAMES, runs.plain),
          table("the total", ["what", "value"], [
            ["the total at the first tick", numberText(sum(runs.plain[0]))],
            ["the total at the last", numberText(sum(runs.plain[runs.plain.length - 1]))],
            ["how many different totals in the whole run", String(new Set(runs.plain.map((row) => sum(row).toString())).size)],
          ]),
        ],
        notes: ["The total is worked out again at every tick rather than carried forward, so its standing still is a result and not a bookkeeping choice."],
      }),
    },
    runStep(33,
      `Turn the dial — count one line for more — what changes?`,
      `${DIALED_LINE} now counts double and every other line still counts one. The rhythm changes: `
      + `motion along ${DIALED_LINE} is quicker than the rest. What does not change is the total, or `
      + "the level the four numbers average to — the dial cannot move either.",
      runs.dialed,
      [table("the dial, and what it did not move", ["what", "value"], [
        ["the line counted double", DIALED_LINE],
        ["every other line counts", numberText(ONE)],
        ["the total, every tick", numberText(sum(runs.dialed[0]))],
        ["the level the four average to", numberText(runs.average)],
      ])]),
    {
      beat: 34,
      title: "Now poke one dot hard and watch. Is there a ring?",
      body: "No. Put everything on A and nothing anywhere else, and there is no spreading to watch: "
        + "every dot is every other dot's neighbour, so the poke arrives everywhere at the same tick. "
        + "There is no room in this world, and no direction to go in.",
      ticks: 6,
      render: (tick = 0) => {
        const initial = [ONE, ZERO, ZERO, ZERO];
        const history = slosh({ lines: TETRA_LINES, initial, ticks: 6 });
        const neighbours = NAMES.map((_, i) => TETRA_LINES.filter((line) => line.includes(i)).length);
        return {
          drawing: drawNet({
            values: Object.fromEntries(NAMES.map((n, i) => [n, numberText(history[tick][i])])),
            emphasis: ["A"],
            title: `A poke on A: tick ${tick}`,
          }),
          tables: [
            historyTable("the poke, tick by tick", NAMES, history),
            table("how far anything is from anything", ["dot", "lines on it", "dots it does not touch"],
              NAMES.map((n, i) => [n, String(neighbours[i]), String(3 - neighbours[i])])),
          ],
          notes: ["Every dot has three lines and there are only three other dots. Nothing here is far from anything."],
        };
      },
    },
    {
      beat: 35,
      title: "So what question can I not ask in this world?",
      body: "The stopwatch question. How fast does something spread, and is it the same speed in "
        + "every direction? Both need a here and a there, and a there is exactly what four dots that "
        + "all touch do not have. That missing question is what the next chapter goes looking for room "
        + "to ask.",
      render: () => ({
        drawing: drawNet({ title: "What is missing" }),
        tables: [table("what this world can and cannot be asked", ["question", "can it be asked?"], [
          ["what number is on this dot?", "yes"],
          ["what happens at the next tick?", "yes"],
          ["is the total conserved?", "yes"],
          ["how far is A from C?", "no — they touch, like every other pair"],
          ["how fast does a poke spread?", "no — it arrives everywhere at once"],
          ["is it the same speed in every direction?", "no — there are no directions"],
        ])],
        notes: [],
      }),
    },
  ];
}

/** Chapter 4 — The shape between. Beats 36–46. */
function chapterFour() {
  const cut = midpointCut();
  const faceSum = octahedronFaceSum();
  const poke = octahedronPoke();
  const twin = secondTetrahedron();
  const stella = stellaCensus();
  const runaway = stellaRunaway();
  const smaller = stellaSmallerTicks();
  const ceilings = [
    { called: "the tetrahedron", ...ceiling(4, TETRA_LINES) },
    { called: "the shape between the tips", ...ceiling(6, midLines()) },
    { called: "the two, threaded", ...ceiling(14, stellaLines()) },
  ];

  return [
    {
      beat: 36,
      title: "Before I go and fetch more tetrahedra — is there any room inside the one I already have?",
      body: "Adding is not the only way to get something bigger. Find the middle of each of the six "
        + "lines. Six new dots — and nothing has been added: those points were always halfway "
        + "along lines you already had. You have only named them.",
      render: () => ({
        drawing: drawNet({ midpoints: true, title: "The six middles, marked" }),
        tables: [table("what is on the paper now", ["what", "how many"], [
          ["dots you started with", String(cut.corners)],
          ["middles, newly named", String(cut.middles)],
          ["dots, all told", String(cut.dots)],
          ["things added to the object", NONE],
        ])],
        notes: ["Each middle keeps the name of the line it halves, so no new naming is needed. The three middles of AD, BD and CD are drawn twice, once on each panel that folded out."],
      }),
    },
    {
      beat: 37,
      title: "Cut at those six middles — what falls out?",
      body: "Four tetrahedra, one at each tip, half the side of the one you cut — and one new "
        + "shape between them, with eight faces. On the flat paper the blade goes round each panel's "
        + "middle triangle. Nothing was added and nothing thrown away: the four tips are an eighth "
        + "each, and the shape left between them is exactly half.",
      render: () => ({
        drawing: drawNet({ midpoints: true, medials: true, title: "The cut, on the flat paper" }),
        tables: [
          table("what falls out", ["what", "how many", "how big"], [
            [`dots — the ${cut.corners} corners and the ${cut.middles} middles`,
              String(cut.dots), "—"],
            ["tetrahedra, one at each tip", String(cut.tips), `half the side, ${fracText(cut.tipShare)} of the whole`],
            ["the shape left between them", String(cut.octahedra), `${fracText(cut.coreShare)} of the whole`],
          ]),
          table("and it all adds up", ["the pieces", "how much of the whole"], [
            [`${cut.tips} tips at ${fracText(cut.tipShare)}`, fracText(cut.tipShare.mul(new Frac(BigInt(cut.tips))))],
            ["the shape between", fracText(cut.coreShare)],
            ["all of it", fracText(cut.tipShare.mul(new Frac(BigInt(cut.tips))).add(cut.coreShare))],
          ]),
        ],
        notes: ["Every volume here is worked out from the four corners' positions, exactly, in this page."],
      }),
    },
    {
      beat: 38,
      title: "Count the new shape — and is there room in it?",
      body: "Six dots, twelve lines, eight faces. The dots are the six middles, so they keep the "
        + "lines' names. And three pairs of them are joined by nothing at all — the first two "
        + "places in this book that are not neighbours. There is a here and a there.",
      render: () => ({
        drawing: drawRing({ title: "The shape between the tips" }),
        tables: [
          table("the census", ["", "dots", "lines", "faces", "inside"], [
            ["the tetrahedron, from before", ...[0, 1, 2, 3].map((k) => String(rung(census(4), k)))],
            ["the shape between the tips", String(cut.octDots), String(cut.octLines),
              String(cut.octFaces), String(cut.octahedra)],
          ]),
          table("its six dots, and how many lines each has", ["dot", "lines on it"],
            MID_NAMES.map((n) => [n, String(cut.octDegree)])),
          table("joined by nothing at all", ["this dot", "and this one"],
            cut.oppositePairs.map(([a, b]) => [a, b])),
        ],
        notes: ["A new drawing, and the only other one these demos use: six dots on two circles, each on the same line through the centre as the one dot no line joins it to. All twelve lines are drawn once and none of them crosses another. The three faint lines through the middle mark the three joins that are not there."],
      }),
    },
    {
      beat: 39,
      title: "Same rule, same tick, one dot poked: what happens?",
      body: `Put ${numberText(ONE)} on ${poke.poked} and nothing anywhere else. At tick ${poke.crossingTicks} the whole `
        + `of it is on ${poke.opposite} — the dot no line joins it to — and nowhere else. At `
        + `tick ${poke.homeTicks} it is home. A here and a there at last, and the total still never `
        + "moves.",
      ticks: poke.history.length - 1,
      render: (tick = 0) => ({
        drawing: drawRing({
          values: Object.fromEntries(MID_NAMES.map((n, i) => [n, numberText(poke.history[tick][i])])),
          emphasis: [poke.poked, poke.opposite],
          title: `A poke on ${poke.poked}: tick ${tick}`,
        }),
        tables: [
          table("this tick", ["dot", "number"],
            MID_NAMES.map((n, i) => [n, numberText(poke.history[tick][i])])
              .concat([["the six, added", numberText(sum(poke.history[tick]))]])),
          historyTable("every tick, computed here", MID_NAMES, poke.history),
          table("what the run does", ["what", "value"], [
            ["poked", `${numberText(ONE)} on ${poke.poked}`],
            ["how much one tick counts for", fracText(poke.k)],
            ["the tick the whole of it is on the opposite dot", String(poke.crossingTicks)],
            ["the tick it is home", String(poke.homeTicks)],
            ["ticks until now-and-before repeat", String(poke.period)],
          ]),
        ],
        notes: [`Home at tick ${poke.homeTicks} is not the end of it: the rule remembers the tick before as well as this one, so the pair does not repeat until tick ${poke.period}.`],
      }),
    },
    {
      beat: 40,
      title: "Put an arrow on each of its twelve lines and walk its eight outside faces: what do they add to?",
      body: "Zero, whatever the arrows. Every one of the twelve lines is walked exactly twice, once "
        + "each way, by the two faces that meet along it — so the walks cancel line by line. The "
        + "same coming-home you proved on four faces, now on eight, and still no length anywhere in it.",
      ticks: faceSum.faces.length - 1,
      render: (tick = 0) => ({
        drawing: drawRing({
          values: Object.fromEntries(MID_NAMES.map((n) => [n, ""])),
          face: tick,
          title: `Face ${tick + 1} of ${faceSum.faces.length}, walked from outside`,
        }),
        tables: [
          table("the twelve arrows, grouped by the face of the tetrahedron each line lies in",
            ["the face it lies in", "its three lines, with their arrows"],
            faceSum.groups.map(([face, items]) => [face,
              items.map((item) => `${item.name} ${numberText(item.value)}`).join(" · ")])),
          table("each face, walked the way it faces from outside",
            ["walked", "its three arrows, signed", "how much goes round it"],
            walkRows(
              faceSum.faces.map((f) => [...f, f[0]].map((i) => MID_NAMES[i]).join(" → ")),
              faceSum.faceTerms, faceSum.faceNumbers,
            )),
          table("and add the eight up", ["the eight, added", "what is left"], [[
            faceSum.faceNumbers.map(signedText).join(" ").replace(/^\+/, ""), numberText(faceSum.total),
          ]]),
          table("why it is exactly zero", ["what", "value"], [
            ["lines", String(faceSum.lines.length)],
            ["times each line is walked, once each way", String(faceSum.linesWalkedEachWay)],
            ["what is left of any line after both walks", numberText(ZERO)],
          ]),
        ],
        notes: ["The eighth face is the outside of the paper. Flat paper always makes one face the outside, so when that one is walked the drawing thickens its three lines instead of filling a region."],
      }),
    },
    {
      beat: 41,
      title: "Four of the eight faces look at a tip; the other four lie flat in the faces of the tetrahedron I cut. What fits on those?",
      body: "One tetrahedron each, the same size as the tips. And their four new corners are not four "
        + "unrelated points: each is one of the old corners pushed through the middle and out the other "
        + "side.",
      render: () => ({
        drawing: drawRing({ tips: true, title: "The four flat faces filled, and the four tips they add" }),
        tables: [
          table("its eight faces divide in two", ["where the face looks", "how many", "which"], [
            ["straight at a tip", String(cut.facesAtATip.length), cut.facesAtATip.join(" · ")],
            ["flat in a face of the tetrahedron you cut", String(cut.facesInAFace.length),
              cut.facesInAFace.join(" · ")],
          ]),
          table("what fits on the flat ones", ["what", "how many", "how big"], [
            ["tetrahedra, one on each flat face", String(twin.added),
              `${fracText(twin.apexShare)} of the whole — the same as a tip`],
          ]),
          table("where each new corner came from", ["new corner", "it sits over the face", "it is this old corner, pushed through the middle"],
            twin.apexNames.map((name) => [name, twin.apexes[name].over, name.replace("′", "")])),
        ],
        notes: ["The drawing puts each tip over its own face, joined to that face's three middles. Four of the eight fit inside their face; the other four sit outside the ring, because three of those faces are slivers and the eighth is the outside of the paper. Their lines in are the only lines that cross anything — the twelve lines of the shape between still cross nothing, which is checked before the drawing is emitted rather than eyeballed."],
      }),
    },
    {
      beat: 42,
      title: "So what have I got now?",
      body: "Two tetrahedra of the same size, threaded through one another, sharing the shape between "
        + `them. ${stella.dots} dots and ${stella.lines} lines — and no two tips joined at all, so `
        + "nothing gets from one tip to another without going through the middle.",
      render: () => ({
        drawing: drawRing({ tips: true, title: "The two tetrahedra, threaded" }),
        tables: [
          table("the census", ["", "dots", "lines"], [
            ["the tetrahedron, from before", ...[0, 1].map((k) => String(rung(census(4), k)))],
            ["the shape between the tips", String(cut.octDots), String(cut.octLines)],
            ["the two tetrahedra, threaded", String(stella.dots), String(stella.lines)],
          ]),
          table("the dots divide in two", ["kind of dot", "how many", "lines on each"], [
            ["middles", String(stella.middles), String(stella.middleDegree)],
            ["tips", String(stella.tips), String(stella.tipDegree)],
          ]),
          table("how much room the pair fills", ["measured against", "how much"], [
            ["the tetrahedron you cut", fracText(stella.inTetrahedra)],
            ["the cube whose eight corners the tips are", fracText(stella.inItsCube)],
          ]),
          table("tips joined to tips", ["what", "how many"], [
            ["pairs of tips joined by a line",
              String(stella.edges.filter(([i, j]) => i >= cut.octDots && j >= cut.octDots).length)],
          ]),
        ],
        notes: [`Both volumes are built up from the ${stella.dots} dots' own positions, piece by piece, rather than one from the other.`],
      }),
    },
    {
      beat: 43,
      title: "Make it move, at the tick that has worked all along.",
      body: `It will not. The tick each object must stay under is fixed by the object, and `
        + `${fracText(TICK_K)} is over this one's. So nothing sloshes: poke one middle and the numbers `
        + "run away, past a hundred million by tick twenty. Two shapes, one rule, and the arithmetic "
        + "has left the napkin.",
      render: () => {
        const rows = runaway.look.map(({ tick, biggest }) => {
          const shown = numberOrRefusal(biggest);
          return [String(tick), shown.printable ? shown.text : `past ${thousands(floorToTwoDigits(biggest))}`];
        });
        return {
          drawing: drawRing({ tips: true, emphasis: [MID_NAMES[0]], title: "Poked at a middle, at a tick this object will not take" }),
          tables: [
            table("the tick each object must stay under", ["", "dots", "stiffest mode", "the tick it must stay under", `the book's tick, ${fracText(TICK_K)}`],
              ceilings.map((row) => [row.called, String(row.size), numberText(row.stiffest),
                fracText(row.bound), row.holds ? "holds" : "too big"])),
            table("the biggest number anywhere in the world", ["tick", "the biggest number in it"], rows),
            table("how much of the table can be written down", ["what", "value"], [
              ["rows that can be written in halves at all", String(runaway.printableRows)],
              ["the push at a poked middle — its own line count", String(runaway.pushAtAMiddle)],
              ["does it ever come back to where it started?", "no"],
            ]),
          ],
          notes: ["The stiffest mode of each object is certified here, exactly, without an eigensolver — and the runaway is run rather than argued. The rows it cannot write down are the ones this page refuses to round."],
        };
      },
    },
    {
      beat: 44,
      title: "Then pick a smaller tick?",
      body: "You can, and then the table cannot be written down. Every tick small enough to hold "
        + "gives two rows at most before the numbers stop being halves and quarters and start being "
        + "something no hand writes in a column — and at none of them does this world ever come "
        + "home.",
      render: () => ({
        drawing: drawRing({ tips: true, emphasis: [MID_NAMES[0]], title: "Every smaller tick, tried" }),
        tables: [
          table("every tick under the ceiling, tried here", ["how much one tick counts for", "rows that can be written down", "ticks until it comes home"],
            smaller.map((row) => [fracText(row.k), String(row.printable),
              row.period === 0 ? "never" : String(row.period)])),
          table("why a smaller tick is not a rescue", ["what", "value"], [
            ["the push at a poked middle", String(runaway.pushAtAMiddle)],
            ["the denominators this page will write", NAPKIN_DENOMINATORS.map(String).join(" · ")],
            ["what the denominators do each tick", "they multiply up, and leave that list"],
          ]),
        ],
        notes: [`The search for a repeat runs ${REPEAT_SEARCH_TICKS} ticks and finds none at any of these tick sizes. What stops it coming home is the object's own stiffnesses, not the patience of the search.`],
      }),
    },
    {
      beat: 45,
      title: "So what is the surprise?",
      body: "The smallest world with room in it is already too big for a napkin. Two shapes and one "
        + "rule — nothing was added that you did not watch arrive — and the arithmetic is "
        + "already past what a hand can do. Which is why everything after this runs on a machine.",
      render: () => ({
        drawing: drawRing({ tips: true, title: "The smallest world with room in it" }),
        tables: [table("where the napkin ran out", ["what", "value"], [
          ["shapes", `${PAIR} — a tetrahedron and the shape inside it`],
          ["rules", ONLY],
          ["dots", String(stella.dots)],
          ["lines", String(stella.lines)],
          ["rows of its table a hand can write", String(runaway.printableRows)],
          ["things assumed along the way", NONE],
        ])],
        notes: [],
      }),
    },
    {
      beat: 46,
      title: "What do I hand the machine, and what comes back?",
      body: "A rule for where the next shape goes — that is the next chapter, and it is the last "
        + "thing this world is missing. What comes back is this world's shadow, and it is not ours to "
        + "invent: we point a test at it and keep whatever it says.",
      render: () => ({
        drawing: drawRing({ tips: true, title: "What goes to the machine" }),
        tables: [table("what the machine is given, and what it is not", ["what", "given?"], [
          ["the shapes, and which dots each line joins", "yes"],
          ["how much each line counts", "yes"],
          ["how much one tick counts for", "yes"],
          ["the one rule", "yes"],
          ["what the answer should be", "no"],
        ])],
        notes: ["Everything on this page was computed here, in your browser, from those same four things."],
      }),
    },
  ];
}

/** Every chapter's steps, keyed by the chapter's own file name in the book. */
export const CHAPTERS = {
  "two-dots-and-a-line": {
    title: "Two dots, a line, and the first thing that closes",
    beats: "9–18",
    steps: chapterOne,
  },
  "one-tetrahedron-is-a-whole-world": {
    title: "One tetrahedron is a whole world",
    beats: "19–26",
    steps: chapterTwo,
  },
  "make-it-move": {
    title: "Make it move",
    beats: "27–35",
    steps: chapterThree,
  },
  "the-shape-between": {
    title: "The shape between",
    beats: "36–46",
    steps: chapterFour,
  },
};

// ── the page ──────────────────────────────────────────────────────────────────────────────────────

const SVG_STILL_STYLE = `
  .net .panel polygon, .ring .panel polygon { fill: #f4ead8; stroke: none; }
  .net .stroke, .ring .stroke { stroke: #20314a; stroke-width: 3; fill: none;
    stroke-linecap: round; stroke-linejoin: round; }
  .ring .stroke { stroke-width: 2; }
  .net .stroke .strong, .ring .stroke .strong { stroke-width: 6; }
  .ring .stroke .tip-line { stroke-width: 1.2; }
  .net .stroke .cut polygon { fill: none; stroke: #20314a; stroke-width: 1.5;
    stroke-dasharray: 7 6; }
  .net .walk .head { fill: #20314a; stroke: none; }
  .net .middle circle { fill: #20314a; stroke: none; }
  .ring .absent line { stroke: #20314a; stroke-width: 1; stroke-dasharray: 2 7; opacity: 0.45; }
  .ring .dots circle { fill: #20314a; stroke: none; }
  .ring .dots circle.tip { fill: none; stroke: #20314a; stroke-width: 2; }
  .net .labels, .ring .labels { fill: #20314a;
    font-family: ui-sans-serif, system-ui, "Helvetica Neue", Arial, sans-serif; }
  .ring .labels .tip { font-style: italic; }
`;

/**
 * The current drawing as a standalone SVG file — the "still".
 *
 * The stills are the point of the drawing code, not a side effect of it: they are what is meant to
 * replace the illustration studies in the chapters, one at a time, in a later PR the owner judges.
 * So a still has to stand on its own: its own stylesheet inlined, its own title and description, and
 * a line naming the beat it came from. `demos/DEMOS.md` says how the replacement will go.
 */
export function stillFrom(svgText, { chapter, beat, title }) {
  const stamp = `<!-- Our Bubble demo still · ${chapter} · beat ${beat}. Computed in the `
    + `browser from the same rules as tools/napkin.py. A drawing of a toy: nothing in it is a claim `
    + `about nature. -->`;
  return svgText.replace(
    /^<svg([^>]*)>/,
    (_match, attributes) => `${stamp}\n<svg${attributes}>\n  <style>${SVG_STILL_STYLE}</style>`,
  ).replace(/<title>[^<]*<\/title>/, `<title>${esc(title)}</title>`);
}

function element(tag, attributes = {}, children = []) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) {
    if (name === "class") node.className = value;
    else if (name === "text") node.textContent = value;
    else node.setAttribute(name, value);
  }
  for (const child of children) node.append(child);
  return node;
}

function renderTable(spec) {
  const figure = element("figure", { class: "numbers" });
  figure.append(element("figcaption", { text: spec.caption }));
  const t = element("table");
  const thead = element("thead");
  const headRow = element("tr");
  for (const cell of spec.head) headRow.append(element("th", { text: cell }));
  thead.append(headRow);
  const tbody = element("tbody");
  for (const row of spec.rows) {
    const tr = element("tr");
    row.forEach((cell, index) => {
      tr.append(element(index === 0 ? "th" : "td", { text: cell, scope: index === 0 ? "row" : undefined }));
    });
    tbody.append(tr);
  }
  t.append(thead, tbody);
  figure.append(t);
  return figure;
}

/**
 * Mount one chapter's demo into the page.
 *
 * Every number a step shows is in a table, as text, whether or not it is also in the drawing — so
 * the page is readable with the drawing ignored entirely, and by a screen reader. The step list is
 * keyboard-steppable, the theme follows the reader's system and can be overridden, and nothing on
 * the page is loaded from anywhere.
 */
export function mount(slug) {
  const chapter = CHAPTERS[slug];
  if (!chapter) throw new Error(`no demo for ${slug}`);
  const steps = chapter.steps();
  const root = document.querySelector("#demo");
  if (!root) throw new Error("the page has no #demo to mount into");

  const nav = element("nav", { class: "steps", "aria-label": "the chapter's beats" });
  const list = element("ol");
  const buttons = steps.map((step, index) => {
    const button = element("button", { type: "button", text: `${step.beat}. ${step.title}` });
    button.addEventListener("click", () => show(index));
    const item = element("li");
    item.append(button);
    list.append(item);
    return button;
  });
  nav.append(list);

  const stage = element("section", { class: "stage" });
  const heading = element("h2");
  const body = element("p", { class: "body" });
  const drawing = element("div", { class: "drawing" });
  const controls = element("div", { class: "controls" });
  const numbers = element("div", { class: "tables" });
  const notes = element("div", { class: "notes" });
  const still = element("div", { class: "still" });
  stage.append(heading, body, drawing, controls, numbers, notes, still);

  const previous = element("button", { type: "button", text: "← back", class: "walk" });
  const next = element("button", { type: "button", text: "on →", class: "walk" });
  const place = element("p", { class: "place", role: "status" });
  const footer = element("div", { class: "walkers" });
  footer.append(previous, place, next);

  root.append(nav, stage, footer);

  let current = 0;
  let tick = 0;
  let playing = null;

  function stop() {
    if (playing !== null) { clearInterval(playing); playing = null; }
  }

  function draw() {
    const step = steps[current];
    const rendered = step.render(tick);
    heading.textContent = `${step.beat}. ${step.title}`;
    body.textContent = step.body;
    drawing.innerHTML = rendered.drawing;

    controlsFor(step, rendered);

    numbers.replaceChildren(...rendered.tables.map(renderTable));
    notes.replaceChildren(...rendered.notes.map((note) => element("p", { text: note })));

    still.replaceChildren();
    const stillButton = element("button", { type: "button", text: "this step, as a still (SVG)" });
    stillButton.addEventListener("click", () => {
      const svg = stillFrom(rendered.drawing, {
        chapter: slug, beat: step.beat, title: `${chapter.title} — beat ${step.beat}`,
      });
      const blob = new Blob([`${svg}\n`], { type: "image/svg+xml" });
      const link = element("a", {
        href: URL.createObjectURL(blob),
        download: `${slug}-beat-${step.beat}${step.ticks ? `-tick-${tick}` : ""}.svg`,
        text: "download it",
      });
      const source = element("details");
      source.append(element("summary", { text: "or read the SVG" }), element("pre", { text: svg }));
      still.replaceChildren(stillButton, link, source);
    });
    still.append(stillButton);

    buttons.forEach((button, index) => {
      button.setAttribute("aria-current", index === current ? "step" : "false");
    });
    previous.disabled = current === 0;
    next.disabled = current === steps.length - 1;
    place.textContent = `beat ${step.beat} · step ${current + 1} of ${steps.length}`;
    document.title = `${chapter.title} · beat ${step.beat} · Our Bubble demo`;
  }

  function controlsFor(step, rendered) {
    controls.replaceChildren();
    if (!step.ticks) return;
    const label = element("span", { class: "tick-label" });
    label.textContent = step.beat === 40
      ? `face ${tick + 1} of ${step.ticks + 1}`
      : `tick ${tick} of ${step.ticks}`;
    const back = element("button", { type: "button", text: "←" , "aria-label": "one step back" });
    const on = element("button", { type: "button", text: "→", "aria-label": "one step on" });
    const play = element("button", { type: "button", text: playing === null ? "play" : "stop" });
    back.disabled = tick === 0;
    on.disabled = tick === step.ticks;
    back.addEventListener("click", () => { stop(); tick -= 1; draw(); });
    on.addEventListener("click", () => { stop(); tick += 1; draw(); });
    play.addEventListener("click", () => {
      if (playing !== null) { stop(); draw(); return; }
      // One tick, then a pause, then the next tick. No easing and no tweening: the rule has no
      // in-between, and a drawing that slid between two ticks would be inventing one.
      playing = setInterval(() => {
        tick = tick === step.ticks ? 0 : tick + 1;
        draw();
      }, 900);
      draw();
    });
    const reset = element("button", { type: "button", text: "back to the start" });
    reset.addEventListener("click", () => { stop(); tick = 0; draw(); });
    controls.append(back, label, on, play, reset);
    void rendered;
  }

  function show(index) {
    stop();
    current = Math.max(0, Math.min(steps.length - 1, index));
    tick = 0;
    draw();
    if (window.location.hash !== `#beat-${steps[current].beat}`) {
      window.history.replaceState(null, "", `#beat-${steps[current].beat}`);
    }
  }

  previous.addEventListener("click", () => show(current - 1));
  next.addEventListener("click", () => show(current + 1));
  document.addEventListener("keydown", (event) => {
    if (event.target instanceof HTMLElement
      && ["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(event.target.tagName)) return;
    if (event.key === "ArrowRight" || event.key === "j") { show(current + 1); event.preventDefault(); }
    if (event.key === "ArrowLeft" || event.key === "k") { show(current - 1); event.preventDefault(); }
  });

  const requested = /^#beat-(\d+)$/.exec(window.location.hash || "");
  const start = requested ? steps.findIndex((step) => step.beat === Number(requested[1])) : 0;
  show(start < 0 ? 0 : start);
  return { steps, show };
}

/** The theme switch: system by default, and the reader's choice remembered for this page only. */
export function themeSwitch(host) {
  const key = "our-bubble-demo-theme";
  let stored = null;
  try { stored = window.localStorage.getItem(key); } catch { stored = null; }
  const apply = (value) => {
    if (value === "light" || value === "dark") document.documentElement.dataset.theme = value;
    else delete document.documentElement.dataset.theme;
  };
  apply(stored);
  const select = element("select", { "aria-label": "theme" });
  for (const [value, text] of [["system", "theme: system"], ["light", "light"], ["dark", "dark"]]) {
    const option = element("option", { value, text });
    if ((stored || "system") === value) option.selected = true;
    select.append(option);
  }
  select.addEventListener("change", () => {
    apply(select.value === "system" ? null : select.value);
    try {
      if (select.value === "system") window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, select.value);
    } catch { /* a reader with storage turned off still gets the switch, just not the memory */ }
  });
  host.append(select);
}
