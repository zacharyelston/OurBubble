// The engine door — the only place a number gets into these pages.
//
// FIREWALL: the engine computes a toy DEC lattice. Dot, line, face, inside, tick, slosh, poke,
// crossing, stella, world name features of that lattice, never claims about nature. See
// ../FIREWALL.md.
//
// The owner's decision, 2026-09-02: **there is one engine for the book and its demos** — UniForge's
// `napkin` crate, vendored at ../engine/ and pinned by ../engine.lock. Before this module existed,
// `demos/core.mjs` carried some seven hundred lines of exact rational arithmetic — a second
// implementation of the book's numbers, written in JavaScript, cross-checked against the first. Two
// implementations is two places the book can disagree with itself, and the cross-check existed only
// because of that. Both are gone.
//
// So: **the pages do no arithmetic.** Every number on them arrives through this file, from one of
// two places, and nowhere else:
//
//   * the compiled engine, ../engine/napkin.js — six entry points, strings in and strings out, so
//     no rational type and no float crosses the boundary; and
//   * the vendored data, ../engine/napkin.json and ../engine/rows.json, whose every rational is an
//     exact "n/d" string.
//
// Even the *printing* is the engine's: `print()` asks `number_json` how a napkin writes a value, and
// gets back either the short decimal or the refusal. The page formats — a plus sign in front of a
// difference, a name beside a value — and never computes.
//
// Everything this door hands out is also remembered, in `emitted`. That set is what
// `core.test.mjs` holds the rendered pages to: a numeric token on a page that is not in it is a
// number the engine did not produce, wherever it was typed.

/** Every entry point the demos use, and the objects each will answer for. */
export const ENTRY_POINTS = ["census_json", "cut_json", "loops_json", "slosh_json",
  "certificate_json", "number_json"];

const NUMERIC_STRING = /^[-−+]?\d+(?:[./]\d+)?$/;

/**
 * A parsed engine answer, walked for everything a page could show off it.
 *
 * Three kinds of thing go in: every scalar leaf (the values themselves, as the engine wrote them);
 * every list's **length** (a count a page reads off a list rather than being told); and every
 * **ordinal** into a list (a page saying "face 3 of 8" is indexing, not computing). That is the same
 * three-part rule the first cross-check used, and its one known weakness is unchanged and stated in
 * DEMOS.md: a value the engine did produce, printed in the wrong place, is invisible to it. What
 * closes most of that hole is the second gate, in `core.test.mjs`: **no digit may be typed into a
 * step's source at all**, so a number cannot be put anywhere by hand in the first place.
 */
function absorb(value, into) {
  if (value === null || value === undefined) return;
  if (typeof value === "boolean") return;
  if (typeof value === "number") { into.add(String(value)); return; }
  if (typeof value === "string") {
    if (NUMERIC_STRING.test(value)) into.add(value);
    return;
  }
  if (Array.isArray(value)) {
    into.add(String(value.length));
    for (let index = 0; index <= value.length; index += 1) into.add(String(index));
    for (const item of value) absorb(item, into);
    return;
  }
  for (const item of Object.values(value)) absorb(item, into);
}

/** One vendored payload plus one compiled engine, with a memory of everything it has said. */
export class Engine {
  constructor(glue, payload, rows) {
    this.glue = glue;
    this.payload = payload;
    this.rows = rows;
    this.emitted = new Set();
    // Nothing, in the engine's own words, taken off a row it computed. It is what every other slot
    // is set to when one slot is asked about — see `contribution` below.
    this.nothing = payload.poke.history[0][1];
    this.calls = [];
    this.cache = new Map();
    absorb(payload, this.emitted);
    absorb(rows, this.emitted);
  }

  /** Ask the compiled engine one question, once, and remember the answer. */
  ask(entry, ...args) {
    if (!ENTRY_POINTS.includes(entry)) throw new Error(`${entry} is not an engine entry point`);
    const key = `${entry}(${JSON.stringify(args)})`;
    if (this.cache.has(key)) return this.cache.get(key);
    const answer = JSON.parse(this.glue[entry](...args));
    absorb(answer, this.emitted);
    this.calls.push(key);
    this.cache.set(key, answer);
    return answer;
  }

  /** The census and coboundaries of the complete complex on `dots` dots. */
  census(dots) { return this.ask("census_json", dots); }

  /** The midpoint cut and the threaded pair, with their exact shares. */
  cut() { return this.ask("cut_json"); }

  /**
   * The coboundary of one degree applied to one set of numbers.
   *
   * Degree 0 on the corner numbers is the differences on the lines — the arithmetic the object does
   * for you, and chapter 1's whole subject. Degree 1 on the line numbers is the loop round each
   * face. Degree 2 on the face numbers is the walk round the inside. One entry point, three rungs.
   */
  loops(object, values, degree) { return this.ask("loops_json", object, values, degree); }

  /** A run of the one rule: the history, the totals, the period, and how much of it is printable. */
  slosh(object, initial, k, ticks) {
    return this.ask("slosh_json", object, initial, k, ticks);
  }

  /**
   * What one number contributes to one walk — the engine's answer, not a sign flipped here.
   *
   * A walk round a face uses each of its lines in a direction, and a line walked against the way it
   * points contributes the opposite of what it holds. The page must not work that out: a proof-reader
   * caught the first version printing a line's own difference in a walk column, so that three terms
   * were shown adding to a total they visibly did not make.
   *
   * So it is asked. Everything but one slot is set to nothing and the walk is run: what comes back
   * is exactly that line's contribution to it, with the orientation the object gives it, computed
   * where every other number on these pages is computed.
   */
  contribution(object, values, degree, index) {
    const alone = values.map((value, at) => (at === index ? value : this.nothing));
    return this.loops(object, alone, degree).loops;
  }

  /** Whether a tick is inside an object's ceiling, and the bound it is being held to. */
  certificate(object, k) { return this.ask("certificate_json", object, k); }

  /** How a napkin writes one exact value — or the refusal, which is a finding and not a fallback. */
  number(value) { return this.ask("number_json", value); }

  /**
   * One value as a page prints it: the engine's own short form, or the exact fraction it refused.
   *
   * The refusal is chapter 5's finding and chapter 3's, so it is returned as a flag rather than
   * swallowed: a caller can mark it, and the pages do.
   */
  print(value) {
    const answer = this.number(value);
    // The engine writes a minus as U+2212 when it prints a number and as a hyphen inside a fraction
    // it refused. Two shapes of minus in one column is a typographic tell that the column is coming
    // from two places; it is coming from one, so the sign is normalised on the way out. The digits
    // are untouched.
    return answer.refused
      ? { text: answer.fraction.replace(/^-/, "−"), refused: true }
      : { text: answer.printed, refused: false };
  }

  /** The same, as a bare string. */
  text(value) { return this.print(value).text; }

  /**
   * The same with a sign always in front, for a number that is a step along a line.
   *
   * A difference of three and a difference of minus three are the same line walked two ways, and a
   * column of them reads wrong without the plus. The sign is punctuation the page adds; the digits
   * are the engine's.
   */
  signed(value) {
    const { text, refused } = this.print(value);
    const negative = text.startsWith("-") || text.startsWith("−");
    const zero = new Set(["0", "-0", "−0"]).has(text);
    return { text: negative || zero ? text : `+${text}`, refused };
  }
}

/** Where the engine sits, seen from a page in demos/. */
export const ENGINE_DIR = "../engine";

/**
 * Open the engine in a browser: the same wasm the reader's own copy of the book serves.
 *
 * `wasm-bindgen --target web` glue fetches `napkin_bg.wasm` beside itself, and GitHub Pages serves
 * `.wasm` as `application/wasm`, which is what `instantiateStreaming` needs; the glue falls back to
 * `arrayBuffer()` if some other host ever does not. Nothing else is loaded from anywhere.
 */
export async function openEngine() {
  const glue = await import(`${ENGINE_DIR}/napkin.js`);
  await glue.default();
  const [payload, rows] = await Promise.all([
    fetch(`${ENGINE_DIR}/napkin.json`).then((answer) => answer.json()),
    fetch(`${ENGINE_DIR}/rows.json`).then((answer) => answer.json()),
  ]);
  return new Engine(glue, payload, rows);
}
