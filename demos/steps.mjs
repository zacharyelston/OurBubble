// The steps: what the reader **does**, and what she sees change.
//
// FIREWALL: these steps run a toy DEC lattice. Nothing they show is a claim about nature. See
// ../FIREWALL.md.
//
// The owner, on the first version of these pages (2026-09-02): *"It feels forced. Like just
// repeating slop recitation of text without understanding it."* He was right, and the diagnosis was
// specific: every step carried a paraphrased paragraph of its own chapter, so a reader met the same
// sentence twice — once written well in the book, once written worse beside it — and did nothing in
// between.
//
// So the rule this file is written under:
//
//   **THE WORDS BELONG TO THE BOOK. THE DEMO IS THE SIM.**
//
// A step is exactly three things. Its **title** is the outline's own question, and it is not written
// here — `tools/demo_steps.py` reads it off `OUTLINE.md` and the chapter's `<!-- beat N -->` marker,
// so no beat number and no question is ever typed into a demo and the preface can renumber the whole
// book without touching this file. Its **`act`** is one short line telling her what to do. And its
// **`render`** is what the object does about it: a drawing and a table, and nothing else. There is no
// field for prose, because a step that wanted to explain itself would have to add one.
//
// A beat with nothing for her to do is not a step. It is **folded into its neighbour**, whose
// `anchors` then names both sections; the fold keeps the question of the beat whose action the step
// performs, and the page prints the range. Seven pairs are folded here, each named at its step.
//
// And no number in this file is a number. Every value comes off the engine — `engine/napkin.json`,
// `engine/rows.json`, or the compiled wasm — and `core.test.mjs` reads this file's own source and
// **refuses any digit inside any string literal in it**. A count arrives as an engine value or it
// does not arrive.

/**
 * A table: a caption, column headings, rows, and what its numbers mean to each other.
 *
 * That last part is `shape`, and it is not optional for a table whose rows carry three or more
 * numbers. Either `{ total: i }` — column `i` is the sum of the numbers before it, and
 * `core.test.mjs` adds them up on every row of every state and holds the two together — or
 * `{ notASum: true }`, which says the numbers in a row are simply several numbers.
 *
 * It is declared by **column index** rather than found by reading the headings, because a
 * proof-reader silenced the first version of that check by renaming a column from "added up" to
 * "the total" in the same edit that broke the arithmetic under it. A guard a caption can switch off
 * is not a guard.
 */
const table = (caption, head, rows, shape = null) => ({ caption, head, rows, shape });

/** The chapters, in the book's order, each a list of steps. */
export function chapterSteps(engine, draw) {
  const P = engine.payload;
  const R = engine.rows;

  // The engine's own words for one and nothing, taken off a row it computed rather than typed. Every
  // "poke one dot" start in the book is this: one at the first dot, nothing anywhere else.
  const ONE = P.poke.history[0][0];
  const ZERO = P.poke.history[0][1];
  const unit = (size) => Array.from({ length: size }, (_, index) => (index === 0 ? ONE : ZERO));

  const NAMES = P.tetrahedron.names;
  const LINES = P.tetrahedron.line_names;
  const FACES = P.tetrahedron.face_names;
  const MID = P.cut.mid_names;

  const show = (value) => engine.text(value);
  const signed = (value) => engine.signed(value).text;
  const count = (list) => String(list.length);

  // The four rungs, by name. The engine keys its census by degree, and a degree written as a
  // string literal would be a digit typed into this file — which is the one thing it may not do — so
  // the names carry the numbering and `String()` turns it back into the engine's key.
  const KINDS = ["dots", "lines", "faces", "inside"];

  /** One rung of one census: the cells of that kind, or none, if the world has not got that far. */
  const rung = (dots, kind) => engine.census(dots).cells[String(KINDS.indexOf(kind))] || [];

  /** The rungs of one census, as a table: how many of each kind of piece this world has. */
  const censusRows = (dots) => KINDS.map((kind) => [kind, count(rung(dots, kind))]);

  // ── 1 · Two dots, a line, and the first thing that closes ─────────────────────────────────────

  const chapterOne = () => {
    const first = P.triangle.chapter.values;
    const second = P.triangle.another.values;
    const corners = NAMES.slice(0, count(first));
    // The first row of the triangle's run at the tetrahedron's tick that a napkin cannot write
    // down — the engine's own count of how far it gets says which row that is.
    const atBook = R.triangle_motion.at_the_book_tick;
    const unprintable = atBook.history[atBook.printable_rows][0];

    /** The three differences the object works out from three corner numbers, and their loop. */
    const differencesOf = (values) => {
      const edges = engine.loops("triangle", values, 0).loops;
      const loop = engine.loops("triangle", edges, 1);
      return { edges, loop: loop.loops[0] };
    };

    const triangleLines = LINES.filter((name) => !name.includes(NAMES[3]));

    // What each line contributes to the walk round the face — the engine's answer, one line at a
    // time, not a sign flipped here. A proof-reader caught the first version printing each line's
    // own difference in this column, so that three terms were shown adding to a total they visibly
    // did not make: +3, −1, −4 under the heading "added up: 0". The walk uses AC the other way, and
    // its contribution is +1. The engine is asked for that rather than the page working it out.
    const walkTerms = (edges) =>
      triangleLines.map((name, index) =>
        engine.contribution("triangle", edges, 1, index)[0]);

    const cornerTable = (values) => table("the corners", ["dot", "number"],
      corners.map((name, index) => [name, show(values[index])]));

    const differenceTable = (values, edges) => table("what the object worked out",
      ["line", "from these two", "difference"],
      triangleLines.map((name, index) => {
        const [from, to] = [...name].map((letter) => corners.indexOf(letter));
        return [name, `${show(values[to])} − ${show(values[from])}`, signed(edges[index])];
      }));

    const netValues = (values, edges) => Object.fromEntries([
      ...corners.map((name, index) => [name, show(values[index])]),
      ...triangleLines.map((name, index) => [name, signed(edges[index])]),
    ]);

    return [
      {
        anchors: ["somewhere-to-put-a-number"],
        act: "Put a number on the dot.",
        controls: [{ kind: "numbers", names: [corners[0]], initial: [first[0]] }],
        render: (state) => ({
          drawing: draw.drawTriangle({
            dots: 1, showLine: false, values: { [corners[0]]: show(state.numbers[0]) },
            title: "One dot, holding one number",
          }),
          tables: [
            table("this world", ["what", "how many"], censusRows(1)),
            table("the number on it", ["dot", "number"], [[corners[0], show(state.numbers[0])]]),
          ],
        }),
      },
      {
        anchors: ["change-lives-between"],
        act: "Put a number on the other dot.",
        controls: [{ kind: "numbers", names: corners.slice(0, 2), initial: first.slice(0, 2) }],
        render: (state) => {
          // The difference on `AB` is asked of the triangle, and read off `AB` alone. The engine's
          // browser surface answers for the book's objects, and two dots and a line is not one of
          // them — a gap listed on the PR. It is the same line and the same coboundary either way:
          // `AB`'s difference does not depend on what else the complex contains.
          const values = [...state.numbers, ZERO];
          const edges = engine.loops("triangle", values, 0).loops;
          const name = triangleLines[0];
          return {
            drawing: draw.drawTriangle({
              dots: 2, emphasis: [name],
              values: {
                [corners[0]]: show(values[0]), [corners[1]]: show(values[1]),
                [name]: signed(edges[0]),
              },
              title: "Two dots, and the change between them",
            }),
            tables: [
              table("the two numbers", ["dot", "number"],
                corners.slice(0, 2).map((dot, index) => [dot, show(values[index])])),
              table("what the line holds", ["line", "from these two", "difference"],
                [[name, `${show(values[1])} − ${show(values[0])}`, signed(edges[0])]]),
            ],
          };
        },
      },
      {
        anchors: ["nothing-closes-yet"],
        act: "Walk on from the second dot.",
        controls: [{ kind: "tick", count: 2, noun: "step" }],
        render: (state) => {
          const walked = corners.slice(0, Math.min(state.tick + 1, 2));
          const stuck = state.tick >= 2;
          return {
            drawing: draw.drawTriangle({
              dots: 2, arrows: state.tick >= 1 ? [[0, 1]] : [],
              title: stuck ? "Nowhere left to walk" : "Two dots and one line",
            }),
            tables: [
              table("this world", ["what", "how many"], censusRows(2)),
              // One row per step taken, so "standing at B" is not asked and answered twice with
              // two different answers, which is what the first version did.
              table("the walk", ["step", "standing at", "a line out of it you have not used"],
                [[String(state.tick), stuck ? corners[1] : walked[walked.length - 1],
                  state.tick === 0 ? "yes" : "no"]]),
              table("its one line", ["line"],
                rung(2, KINDS[1]).map((_, index) => [triangleLines[index]])),
            ],
          };
        },
      },
      {
        anchors: ["the-triangle"],
        act: "Draw the lines, one at a time.",
        controls: [{ kind: "tick", count: 3, noun: "line" }],
        render: (state) => {
          // One line per press, and the count is a count of what is on the paper. The first version
          // drew the third dot and two lines on one press and told her the world had a line in it
          // before it had drawn one.
          const drawn = triangleLines.slice(0, state.tick);
          const closed = drawn.length === triangleLines.length;
          return {
            drawing: draw.drawTriangle({
              dots: state.tick >= 2 ? 3 : 2, lines: drawn, showFace: closed,
              title: closed ? "The first thing that closes" : "Not closed yet",
            }),
            tables: [
              table("what is on the paper", ["dots", "lines", "faces"],
                [[count(rung(state.tick >= 2 ? 3 : 2, KINDS[0])), count(drawn),
                  closed ? count(rung(3, KINDS[2])) : show(ZERO)]]),
              table("its lines, in the one order", ["line", "drawn"],
                triangleLines.map((name, index) =>
                  [name, index < state.tick ? "yes" : "not yet"])),
            ],
          };
        },
      },
      {
        anchors: ["three-corners-three-differences"],
        act: "Put a number on each corner.",
        controls: [{ kind: "numbers", names: corners, initial: first }],
        render: (state) => {
          const { edges } = differencesOf(state.numbers);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, values: netValues(state.numbers, edges),
              title: "Three corner numbers, three differences",
            }),
            tables: [
              cornerTable(state.numbers),
              differenceTable(state.numbers, edges),
            ],
          };
        },
      },
      {
        anchors: ["walk-it-and-add"],
        act: "Walk it.",
        controls: [
          { kind: "numbers", names: corners, initial: first },
          { kind: "tick", count: 3, noun: "step" },
        ],
        render: (state) => {
          const { edges, loop } = differencesOf(state.numbers);
          const walk = [[0, 1], [1, 2], [2, 0]];
          const taken = walk.slice(0, state.tick);
          const home = state.tick >= walk.length;
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, arrows: taken,
              values: netValues(state.numbers, edges),
              title: home ? "Home, and holding nothing" : "The walk round the triangle",
            }),
            tables: [
              // The difference on a line is the engine's, in the line's own direction, and the
              // walk is told which way it is going rather than being handed a negated copy. Nothing
              // on this page changes the sign of anything: the walk's own total is asked of the
              // engine one rung up, and it is the zero the beat is about.
              table("the walk, step by step",
                ["step", "line", "walked", "what it costs you"],
                taken.map(([from, to]) => {
                  const name = [corners[from], corners[to]].sort().join("");
                  const index = triangleLines.indexOf(name);
                  return [
                    `${corners[from]} → ${corners[to]}`, name,
                    name[0] === corners[from] ? "the way it points" : "the other way",
                    signed(walkTerms(edges)[index]),
                  ];
                })),
              table("what the whole walk comes to",
                ["what the steps so far cost you", "the whole way round"],
                [[taken.map(([from, to]) => signed(walkTerms(edges)[
                  triangleLines.indexOf([corners[from], corners[to]].sort().join(""))]))
                  .join("  ") || "nothing yet", home ? show(loop) : "not home yet"]],
                { total: 1 }),
            ],
          };
        },
      },
      {
        anchors: ["any-three-numbers-at-all"],
        act: "Swap in three other numbers.",
        controls: [{
          kind: "choose",
          options: [
            { label: "the first three", value: first },
            { label: "three others", value: second },
          ],
        }],
        render: (state) => {
          const values = state.choice.value;
          const { edges, loop } = differencesOf(values);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, values: netValues(values, edges),
              title: "Other numbers, the same nothing",
            }),
            tables: [
              cornerTable(values),
              differenceTable(values, edges),
              table("what the whole walk comes to", ["the three terms, as the walk uses them",
                "added up"],
                [[walkTerms(edges).map(signed).join("  "), show(loop)]], { total: 1 }),
            ],
          };
        },
      },
      {
        anchors: ["why-it-is-exact-and-not-approximate"],
        act: "Make one corner unprintable.",
        controls: [{ kind: "press", label: "swap it in" }],
        render: (state) => {
          const values = state.pressed ? [...first.slice(0, 2), unprintable] : first;
          const { edges, loop } = differencesOf(values);
          const printed = values.map((value) => engine.print(value));
          const edgePrints = edges.map((value) => engine.signed(value));
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, values: netValues(values, edges),
              title: state.pressed ? "A number the napkin will not print" : "Three plain numbers",
            }),
            tables: [
              table("the corners", ["dot", "number", "does a napkin print it"],
                corners.map((name, index) =>
                  [name, printed[index].text, printed[index].refused ? "no" : "yes"])),
              table("the differences", ["line", "difference", "does a napkin print it"],
                triangleLines.map((name, index) =>
                  [name, edgePrints[index].text, edgePrints[index].refused ? "no" : "yes"])),
              table("what the whole walk comes to", ["added up", "exactly"],
                [[show(loop), show(loop) === show(P.triangle.chapter.sum) ? "yes" : "no"]]),
            ],
          };
        },
      },
      {
        // Beats 17 and 18 fold together: neither has anything of its own to do, and the one action
        // that answers both is taking every number away. What is left is the world, which is what
        // both beats are about — no length was ever used, and nothing was ever assumed.
        anchors: ["what-you-never-used", "nothing-at-all"],
        titleFrom: "nothing-at-all",
        act: "Take every number away.",
        controls: [{ kind: "press", label: "clear" }],
        render: (state) => {
          const values = state.pressed ? corners.map(() => ZERO) : first;
          const { edges, loop } = differencesOf(values);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: state.pressed ? {} : netValues(values, edges),
              title: state.pressed ? "The world, with nothing on it" : "The world, with numbers on it",
            }),
            tables: [
              table("what is still here", ["what", "how many"], censusRows(3)),
              table("what it has never had", ["a length", "a direction", "a clock"],
                [["none", "none", "none"]]),
              table("what the walk still comes to", ["added up"], [[show(loop)]],
                { notASum: true }),
            ],
          };
        },
      },
    ];
  };

  // ── 2 · One tetrahedron is a whole world ──────────────────────────────────────────────────────

  const chapterTwo = () => {
    const corners = P.tetrahedron.corners;
    const arrows = P.tetrahedron.arrows;
    const weight = P.motion.dialed_weight;
    const dialed = P.motion.dialed_line;
    const plainWeight = ONE;

    const differencesOf = (values) => engine.loops("tetrahedron", values, 0).loops;
    const faceLoopsOf = (edges) => engine.loops("tetrahedron", edges, 1);

    return [
      {
        // Beats 19 and 20 fold: the count is what adding the dot shows, so there is one action.
        anchors: ["four-dots-and-everything-you-can-draw-between-them", "the-whole-inventory"],
        act: "Add the fourth dot.",
        controls: [{ kind: "tick", count: 1, noun: "dot" }],
        render: (state) => ({
          drawing: state.tick === 0
            ? draw.drawTriangle({ dots: 3, showFace: true, title: "Three dots, and their inside" })
            : draw.drawNet({ title: "Four dots, unfolded flat" }),
          tables: [
            table("this world", ["what", "how many"], censusRows(state.tick === 0 ? 3 : 4)),
            table("its lines, in the one order", ["line"],
              (state.tick === 0 ? LINES.filter((name) => !name.includes(NAMES[3])) : LINES)
                .map((name) => [name])),
            table("its faces", ["face"],
              (state.tick === 0 ? [FACES[0]] : FACES).map((name) => [name])),
          ],
        }),
      },
      {
        anchors: ["four-numbers-on-the-corners-four-faces-four-zeros"],
        act: "Put a number on each corner.",
        controls: [{ kind: "numbers", names: NAMES, initial: corners }],
        render: (state) => {
          const edges = differencesOf(state.numbers);
          const loops = faceLoopsOf(edges);
          return {
            drawing: draw.drawNet({
              values: Object.fromEntries([
                ...NAMES.map((name, index) => [name, show(state.numbers[index])]),
                ...LINES.map((name, index) => [name, signed(edges[index])]),
                ...FACES.map((name, index) => [name, show(loops.loops[index])]),
              ]),
              title: "Four corner numbers, six differences, four zeros",
            }),
            tables: [
              table("the corners", ["dot", "number"],
                NAMES.map((name, index) => [name, show(state.numbers[index])])),
              table("what the object worked out", ["line", "difference"],
                LINES.map((name, index) => [name, signed(edges[index])])),
              table("each face, walked round", ["face", "its loop"],
                FACES.map((name, index) => [name, show(loops.loops[index])])),
            ],
          };
        },
      },
      {
        anchors: ["what-if-the-lines-came-first"],
        act: "Put an arrow on each line.",
        controls: [{ kind: "numbers", names: LINES, initial: arrows }],
        render: (state) => {
          const loops = faceLoopsOf(state.numbers);
          return {
            drawing: draw.drawNet({
              values: Object.fromEntries([
                ...LINES.map((name, index) => [name, signed(state.numbers[index])]),
                ...FACES.map((name, index) => [name, show(loops.loops[index])]),
              ]),
              title: "Six arrows, and what goes round each face",
            }),
            tables: [
              table("the arrows", ["line", "arrow"],
                LINES.map((name, index) => [name, signed(state.numbers[index])])),
              table("each face, walked round", ["face", "how much goes round it"],
                FACES.map((name, index) => [name, show(loops.loops[index])])),
            ],
          };
        },
      },
      {
        anchors: ["round-the-inside"],
        act: "Change an arrow.",
        controls: [{ kind: "numbers", names: LINES, initial: arrows }],
        render: (state) => {
          const loops = faceLoopsOf(state.numbers);
          const inside = engine.loops("tetrahedron", loops.loops, 2);
          return {
            drawing: draw.drawNet({
              values: Object.fromEntries([
                ...LINES.map((name, index) => [name, signed(state.numbers[index])]),
                ...FACES.map((name, index) => [name, show(loops.loops[index])]),
              ]),
              title: "The four face-numbers, walked round the inside",
            }),
            tables: [
              table("each face's number", ["face", "how much goes round it"],
                FACES.map((name, index) => [name, show(loops.loops[index])])),
              // The same fix as chapter 1's walk, one rung up: the walk round the inside uses each
              // face in a direction, and two of the four the other way. The terms it actually adds
              // are asked of the engine, so that four numbers and their total are one arithmetic a
              // reader can do herself.
              table("the inside, walked round",
                ["the four terms, as the walk uses them", "added up"],
                [[FACES.map((name, index) =>
                  signed(engine.contribution("tetrahedron", loops.loops, 2, index)[0])).join("  "),
                  show(inside.loops[0])]], { total: 1 }),
            ],
          };
        },
      },
      {
        anchors: ["four-kinds-and-that-is-all-there-will-ever-be"],
        act: "Ask for the next kind.",
        controls: [{ kind: "press", label: "ask" }],
        render: (state) => {
          const census = engine.census(4);
          const rungs = Object.keys(census.cells).sort();
          const kinds = ["dots", "lines", "faces", "inside"];
          const rows = rungs.map((rung) => [kinds[Number(rung)], count(census.cells[rung])]);
          return {
            drawing: draw.drawNet({
              title: state.pressed ? "Four kinds, and no fifth" : "The whole world, on one napkin",
            }),
            tables: [
              table("every kind of number this world has", ["kind", "how many places"],
                state.pressed ? [...rows, ["one more kind", "none"]] : rows),
            ],
          };
        },
      },
      {
        // Beats 25 and 26 fold: the dial is the action, and "is this a complete world" is what the
        // table under it already answers — every kind of number, both coming-home zeros, one dial.
        anchors: ["the-one-choice-what-a-line-is-worth", "enough-for-a-world"],
        act: `Count ${dialed} double.`,
        controls: [{ kind: "press", label: "turn the dial" }],
        render: (state) => {
          const edges = differencesOf(corners);
          const loops = faceLoopsOf(edges);
          const arrowLoops = faceLoopsOf(arrows);
          const inside = engine.loops("tetrahedron", arrowLoops.loops, 2);
          return {
            drawing: draw.drawNet({
              emphasis: state.pressed ? [dialed] : [],
              values: Object.fromEntries(LINES.map((name, index) =>
                [name, `${signed(edges[index])} · ${show(state.pressed && name === dialed
                  ? weight : plainWeight)}`])),
              title: state.pressed ? `${dialed}, counted double` : "Every line, counted the same",
            }),
            tables: [
              // Every line carries two numbers now, and the dial moves one of them. The first
              // version turned the dial and changed a single cell in a table, which is a beat asking
              // its question and not answering it.
              table("what each line holds, and what it is worth",
                ["line", "difference", "worth"],
                LINES.map((name, index) => [name, signed(edges[index]),
                  show(state.pressed && name === dialed ? weight : plainWeight)])),
              table("the whole world, on a napkin",
                ["dots", "lines", "faces", "inside", "every face's loop", "round the inside"],
                [[
                  ...KINDS.map((kind) => count(rung(4, kind))),
                  show(loops.sum),
                  show(inside.loops[0]),
                ]], { notASum: true }),
            ],
          };
        },
      },
    ];
  };

  // ── 3 · Make it move ──────────────────────────────────────────────────────────────────────────

  const chapterThree = () => {
    const triangleCorners = R.triangle_motion.corners;
    const atShape = R.triangle_motion.at_two_thirds;
    const atBook = R.triangle_motion.at_the_book_tick;
    const tetraCorners = P.tetrahedron.corners;
    const k = P.motion.k;
    const ticks = P.motion.ticks;
    const dialed = P.motion.dialed_line;
    const triangleNames = NAMES.slice(0, count(triangleCorners));
    const hops = R.no_room.hops;

    const runTable = (caption, history, totals, names) =>
      table(caption, ["tick", ...names, "added up"],
        history.map((row, tick) => [String(tick), ...row.map(show), show(totals[tick])]),
        { total: names.length + 1 });

    const printableRow = (history, printable) => table("how far a napkin gets",
      ["rows it can write", "rows there are"], [[String(printable), count(history)]]);

    return [
      {
        // Beats 27 and 28 fold: one action answers both — press the clock and watch nothing happen,
        // because a clock on its own is not a rule.
        anchors: ["a-clock", "ticks-all-the-same"],
        act: "Tick.",
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => ({
          drawing: draw.drawTriangle({
            dots: 3, showFace: true,
            values: Object.fromEntries(triangleNames.map((name, index) =>
              [name, show(triangleCorners[index])])),
            title: "A clock, and no rule for it to drive",
          }),
          tables: [
            table("the numbers, at this tick", ["tick", ...triangleNames],
              [[String(state.tick), ...triangleCorners.map(show)]], { notASum: true }),
            table("what moved", ["ticks so far", "numbers that changed"],
              [[String(state.tick), show(ZERO)]]),
          ],
        }),
      },
      {
        anchors: ["then-and-now"],
        act: "Give it a second row.",
        controls: [{ kind: "press", label: "add a row" }],
        render: (state) => {
          const run = engine.slosh("triangle", triangleCorners, atShape.k, ticks);
          // Both rows are the row it starts on. At rest, *then* and *now* are the same numbers, and
          // that is the point: the second row is not a tick already taken — running one is the next
          // beat's button — it is the second half of a state the rule cannot read without.
          const start = run.history[0];
          const rows = state.pressed ? [start, start] : [start];
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: Object.fromEntries(triangleNames.map((name, index) =>
                [name, show(rows[rows.length - 1][index])])),
              title: state.pressed ? "Then, and now" : "Now, and nothing before it",
            }),
            tables: [
              table("the state", ["which row", ...triangleNames],
                rows.map((row, index) => [
                  rows.length === 1 ? "now" : (index === 0 ? "then" : "now"),
                  ...row.map(show),
                ]), { notASum: true }),
              table("can the rule write the next row", ["rows it has", "rows it needs"],
                [[count(rows), count(run.history.slice(0, 2))]]),
            ],
          };
        },
      },
      {
        // Beats 30 and 31 fold: "is that really the whole law" is answered by there being one
        // button, and it does the same thing every time.
        anchors: ["what-one-tick-does", "nothing-else-ever"],
        act: "Tick, once.",
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("triangle", triangleCorners, atShape.k, ticks);
          const from = Math.max(state.tick - 1, 0);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: Object.fromEntries(triangleNames.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "One rule, one tick",
            }),
            tables: [
              table("what the rule read, and what it wrote",
                ["which row", ...triangleNames, "added up"],
                [
                  ["then", ...run.history[from].map(show), show(run.totals[from])],
                  ["now", ...run.history[state.tick].map(show), show(run.totals[state.tick])],
                ], { total: triangleNames.length + 1 }),
              table("the tick it ran at", ["tick"], [[show(run.k)]], { notASum: true }),
            ],
          };
        },
      },
      {
        anchors: ["three-numbers-first"],
        act: "Run it.",
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("triangle", triangleCorners, atShape.k, ticks);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: Object.fromEntries(triangleNames.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "Three numbers, sloshing",
            }),
            tables: [
              runTable("every tick so far", run.history.slice(0, state.tick + 1),
                run.totals, triangleNames),
              table("what came back", ["tick", "back where it started every"],
                [[show(run.k), String(run.period)]]),
            ],
          };
        },
      },
      {
        anchors: ["the-tick-belongs-to-the-shape"],
        act: "Run it at the other tick.",
        controls: [{
          kind: "choose",
          // The two ticks label themselves, in the engine's own printing of them. A word here would
          // be a word explaining what the number already says.
          options: [atShape, atBook].map((run) => ({ label: show(run.k), value: run })),
        }],
        render: (state) => {
          const chosen = state.choice.value;
          const run = engine.slosh("triangle", triangleCorners, chosen.k, ticks);
          const printable = run.printable_rows;
          // Marked row by row, rather than announced in a summary above a table that then writes
          // every row anyway. A reader who is told "rows it can write: 3" over eleven written rows
          // has been told two things.
          const writable = (tick) => (tick < printable ? "yes" : "no");
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: Object.fromEntries(triangleNames.map((name, index) =>
                // The last row a napkin can still write down, which at one of the two ticks is the
                // last row there is and at the other is the third.
                [name, show(run.history[printable - 1][index])])),
              title: "The tick belongs to the shape",
            }),
            tables: [
              table("every tick", ["tick", ...triangleNames, "added up",
                "can a napkin write this row"],
                run.history.map((row, tick) => [String(tick), ...row.map(show),
                  show(run.totals[tick]), writable(tick)]),
                { total: triangleNames.length + 1 }),
              printableRow(run.history, printable),
              table("does it come home", ["tick", "back where it started every"],
                [[show(run.k), run.period === 0 ? "never" : String(run.period)]]),
            ],
          };
        },
      },
      {
        anchors: ["now-the-tetrahedron"],
        act: "Tick.",
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("tetrahedron", tetraCorners, k, ticks);
          const certificate = engine.certificate("tetrahedron", k);
          return {
            drawing: draw.drawNet({
              values: Object.fromEntries(NAMES.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "Four numbers, sloshing",
            }),
            tables: [
              runTable("every tick so far", run.history.slice(0, state.tick + 1),
                run.totals, NAMES),
              table("is this tick inside the shape's ceiling",
                ["tick", "the shape's stiffest", "the ceiling", "inside it"],
                [[show(certificate.k), show(String(certificate.eigenvalue)),
                  show(certificate.bound), certificate.holds ? "yes" : "no"]]),
            ],
          };
        },
      },
      {
        anchors: ["the-total-never-moves"],
        act: "Change a starting number.",
        controls: [
          { kind: "numbers", names: NAMES, initial: tetraCorners },
          { kind: "tick", count: ticks, noun: "tick" },
        ],
        render: (state) => {
          const run = engine.slosh("tetrahedron", state.numbers, k, ticks);
          return {
            drawing: draw.drawNet({
              values: Object.fromEntries(NAMES.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "The total, at every tick",
            }),
            tables: [
              runTable("every tick", run.history, run.totals, NAMES),
              table("the total", ["at the start", "at this tick", "ticks apart"],
                [[show(run.totals[0]), show(run.totals[state.tick]), String(state.tick)]]),
            ],
          };
        },
      },
      {
        anchors: ["turn-the-dial"],
        act: `Count ${dialed} double.`,
        controls: [
          {
            kind: "choose",
            options: [
              { label: "every line the same", value: P.motion.plain },
              { label: `${dialed} counted double`, value: P.motion.dialed },
            ],
          },
          { kind: "tick", count: ticks, noun: "tick" },
        ],
        render: (state) => {
          // The dial is the one place these pages cannot ask the engine a fresh question: its
          // browser surface runs the rule with every line counted the same, so the dialled run is
          // the one the engine computed and vendored. A gap listed on the PR.
          const run = state.choice.value;
          const turned = state.choice.index === 1;
          return {
            drawing: draw.drawNet({
              emphasis: turned ? [dialed] : [],
              values: Object.fromEntries(NAMES.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: turned ? `${dialed}, counted double` : "Every line, counted the same",
            }),
            tables: [
              runTable("every tick", run.history, run.totals, NAMES),
              table("what the dial changed", ["back where it started every", "the total"],
                [[run.period === 0 ? "never" : String(run.period), show(run.totals[state.tick])]]),
            ],
          };
        },
      },
      {
        // Beats 37 and 38 fold: the poke is the action, and "what can I not ask here" is what the
        // hop table under it says — every dot is one line from every other, so there is no further.
        anchors: ["where-is-the-ring", "the-question-this-world-cannot-answer"],
        act: `Poke ${NAMES[0]}.`,
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("tetrahedron", unit(count(NAMES)), k, ticks);
          const moved = run.history[state.tick]
            .filter((value, index) => index > 0 && value !== ZERO);
          return {
            drawing: draw.drawNet({
              emphasis: [NAMES[0]],
              values: Object.fromEntries(NAMES.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "One dot poked, and every other one line away",
            }),
            tables: [
              runTable("every tick so far", run.history.slice(0, state.tick + 1),
                run.totals, NAMES),
              table("how many lines from one dot to another", ["from", ...NAMES],
                hops.map((row, index) => [NAMES[index], ...row.map(String)]), { notASum: true }),
              table("how far away anything is",
                ["the furthest apart two dots are", "dots that moved by this tick"],
                [[String(R.no_room.diameter), String(moved.length)]]),
            ],
          };
        },
      },
    ];
  };

  // ── 4 · The shape between ─────────────────────────────────────────────────────────────────────

  const chapterFour = () => {
    const cut = P.cut;
    const poke = P.poke;
    const faceSum = P.face_sum;
    const tipNames = draw.tipNames();
    const atATip = tipNames
      .map((name, index) => ({ name, index }))
      .filter((entry) => !entry.name.endsWith("′"));
    const stillBare = tipNames
      .map((name, index) => ({ name, index }))
      .filter((entry) => entry.name.endsWith("′"));

    return [
      {
        anchors: ["divide-it-instead-of-adding-to-it"],
        act: "Mark the middle of every line.",
        controls: [{ kind: "press", label: "mark them" }],
        render: (state) => ({
          drawing: draw.drawNet({
            midpoints: state.pressed,
            title: state.pressed ? "A mark in the middle of every line" : "The tetrahedron, whole",
          }),
          tables: [
            table("what is inside it already", ["lines", "middles marked"],
              [[count(LINES), state.pressed ? String(cut.middles) : show(ZERO)]]),
            table("the middles, which keep their lines' names", ["middle"],
              MID.map((name) => [name])),
          ],
        }),
      },
      {
        anchors: ["what-falls-out"],
        act: "Cut.",
        controls: [{ kind: "press", label: "cut" }],
        render: (state) => ({
          drawing: state.pressed
            ? draw.drawRing({ title: "The shape left between the tips" })
            : draw.drawNet({ midpoints: true, medials: true, title: "Where the blade goes" }),
          tables: state.pressed ? [
            table("what fell out", ["pieces at the tips", "shapes between them", "dots in all"],
              [[String(cut.corners), String(cut.octahedra), String(cut.dots)]]),
            table("and how much of the original each one is",
              ["each of the tips", "how many tips", "the shape between"],
              [[show(cut.tip_share), String(cut.corners), show(cut.core_share)]]),
          ] : [
            // Nothing has fallen out yet, so nothing is counted yet. The first version printed the
            // answer above the button that produces it.
            table("where the blade goes", ["lines", "middles it passes through"],
              [[count(LINES), String(cut.middles)]]),
          ],
        }),
      },
      {
        anchors: ["six-dots-and-the-first-two-that-are-not-neighbours"],
        act: "Look for what joins the opposite dots.",
        controls: [{ kind: "press", label: "look" }],
        render: (state) => ({
          drawing: draw.drawRing({
            absences: state.pressed,
            emphasis: state.pressed ? cut.opposite_pairs.flat() : [],
            title: state.pressed ? "Three pairs, joined by nothing" : "The shape between",
          }),
          tables: [
            table("count it", ["dots", "lines", "faces"],
              [[String(cut.oct_dots), String(cut.oct_lines), String(cut.oct_faces)]]),
            table("every dot's neighbours", ["dot", "lines out of it", "dots it is not joined to"],
              MID.map((name) => [name, String(cut.oct_degree),
                count(cut.opposite_pairs.filter((pair) => pair.includes(name)))])),
            ...(state.pressed ? [table("the pairs joined by nothing",
              ["one", "the other", "lines between them"],
              cut.opposite_pairs.map(([a, b]) => [a, b, show(ZERO)]))] : []),
          ],
        }),
      },
      {
        anchors: ["it-takes-two-ticks-to-cross"],
        act: `Poke ${poke.poked}.`,
        controls: [{ kind: "tick", count: poke.period, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("octahedron", poke.history[0], poke.k, poke.period);
          const certificate = engine.certificate("octahedron", poke.k);
          return {
            drawing: draw.drawRing({
              emphasis: [poke.poked, poke.opposite],
              values: Object.fromEntries(MID.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              title: "One dot poked, and a there to cross to",
            }),
            tables: [
              table("every tick so far", ["tick", ...MID, "added up"],
                run.history.slice(0, state.tick + 1).map((row, tick) =>
                  [String(tick), ...row.map(show), show(run.totals[tick])]),
                { total: MID.length + 1 }),
              // What has happened, not what is going to. Printing "ticks to cross 2" beside a
              // drawing at tick 0 hands her the answer before she has walked to it.
              table("where the poke has got to",
                ["poked", "its opposite", "arrived at the opposite", "home again"],
                [[poke.poked, poke.opposite,
                  state.tick >= poke.crossing_ticks ? String(poke.crossing_ticks) : "not yet",
                  state.tick >= poke.home_ticks ? String(poke.home_ticks) : "not yet"]]),
              table("is this tick inside the shape's ceiling",
                ["tick", "the shape's stiffest", "the ceiling", "inside it"],
                [[show(certificate.k), show(String(certificate.eigenvalue)),
                  show(certificate.bound), certificate.holds ? "yes" : "no"]]),
            ],
          };
        },
      },
      {
        anchors: ["coming-home-on-eight-faces"],
        act: "Walk each face.",
        // "face 0 of 8" reads as a face that does not exist. The counter counts what she has done.
        controls: [{ kind: "tick", count: cut.oct_faces, noun: "faces walked" }],
        render: (state) => {
          // One count, and everything reads off it. The walker used to say "faces walked 0" beside
          // a table listing one, all the way up to "7 of 8" beside a table listing eight — two
          // counters of the same thing disagreeing at eight of nine states. The tick IS the number
          // walked: none at the start, the last of them at the end.
          const walked = faceSum.face_numbers.slice(0, state.tick);
          const last = walked.length === cut.oct_faces;
          const face = state.tick === 0 || last ? null : state.tick - 1;
          return {
            drawing: last
              ? draw.drawRing({
                tips: atATip.map((entry) => entry.index),
                title: "Four faces looking at a tip, and four left bare",
              })
              : draw.drawRing({ face, title: "One face, walked round" }),
            tables: [
              table("the arrows on the lines", ["line", "arrow"],
                cut.mid_lines.map(([a, b], index) =>
                  [`${MID[a]} → ${MID[b]}`, signed(faceSum.arrows[index])])),
              table("each face, walked the outward way", ["face", "what goes round it"],
                walked.map((value, index) => [
                  cut.mid_faces[index].map((i) => MID[i]).join(" · "), signed(value),
                ])),
              // The terms and the total in one table, so the check can add them up. They were in
              // two, which is the other way a proof-reader silenced this guard.
              table("all of them added up",
                ["the faces walked so far", "added up"],
                [[walked.map(signed).join("  ") || "none yet",
                  last ? show(faceSum.sum) : "not all walked yet"]], { total: 1 }),
              table("how far round it has got",
                ["faces walked", "faces there are", "lines walked, each way once"],
                [[count(walked), String(cut.oct_faces),
                  last ? String(faceSum.lines_walked_each_way) : "not all walked yet"]],
                { notASum: true }),
              table("what is on each face now", ["faces looking at a tip", "faces still bare"],
                [[count(atATip), count(stillBare)]]),
            ],
          };
        },
      },
    ];
  };

  // ── 5 · Two worlds threaded ───────────────────────────────────────────────────────────────────

  const chapterFive = () => {
    const cut = P.cut;
    const stella = P.stella;
    const refusal = P.refusal;
    const runaway = refusal.runaway;
    const tipNames = draw.tipNames();
    const flat = tipNames
      .map((name, index) => ({ name, index }))
      .filter((entry) => entry.name.endsWith("′"));
    const atATip = tipNames
      .map((name, index) => ({ name, index }))
      .filter((entry) => !entry.name.endsWith("′"));

    return [
      {
        anchors: ["four-faces-spare"],
        act: "Add a tip on a bare face.",
        controls: [{ kind: "tick", count: flat.length, noun: "tip" }],
        render: (state) => ({
          drawing: draw.drawRing({
            tips: [...atATip.map((entry) => entry.index),
              ...flat.slice(0, state.tick).map((entry) => entry.index)],
            emphasis: state.tick > 0 ? [flat[state.tick - 1].name] : [],
            title: "A tip on each face that was bare",
          }),
          tables: [
            table("the eight faces", ["face", "what is on it"],
              cut.mid_faces.map((face, index) => [
                face.map((i) => MID[i]).join(" · "),
                atATip.some((entry) => entry.index === index)
                  ? tipNames[index]
                  : (flat.slice(0, state.tick).some((entry) => entry.index === index)
                    ? tipNames[index] : "bare"),
              ])),
            // Named in the order the drawing adds them, not in the engine's own listing order. A
            // proof-reader watched D′ land on the paper while this table said A′: every value was
            // right and the nouns were wrong, which is the one defect no scan over numbers can see.
            table("the corners the second one brought", ["corner", "how much of the original"],
              flat.slice(0, state.tick).map((entry) =>
                [entry.name, show(stella.apex_share)])),
            table("how many are on now", ["tips added", "faces that were bare"],
              [[String(state.tick), String(flat.length)]]),
          ],
        }),
      },
      {
        anchors: ["two-tetrahedra-threaded"],
        act: "Turn it.",
        controls: [{ kind: "turn" }],
        render: (state) => ({
          drawing: draw.drawWire({
            yaw: state.yaw, pitch: state.pitch,
            title: "The two tetrahedra, threaded",
          }),
          tables: [
            table("count it", ["dots", "lines", "tips", "middles"],
              [[String(stella.dots), String(stella.lines), String(stella.tips),
                String(stella.middles)]], { notASum: true }),
            table("how many lines leave each kind of dot",
              ["out of a tip", "out of a middle"],
              [[String(stella.tip_degree), String(stella.middle_degree)]]),
            table("what the drawing put on the paper",
              ["lines drawn", "lines the engine has", "dots drawn", "dots the engine has"],
              [[count(draw.wireframe().edges), String(stella.lines),
                count(draw.wireframe().points), String(stella.dots)]], { notASum: true }),
            table("no two tips are joined", ["lines that join one tip to another"],
              [[count(draw.wireframe().edges
                .filter(([a, b]) => a >= stella.middles && b >= stella.middles))]]),
          ],
        }),
      },
      {
        anchors: ["the-tick-that-stops-working"],
        act: "Tick.",
        controls: [
          { kind: "tick", count: runaway.look.length - 1, noun: "look" },
          { kind: "turn" },
        ],
        render: (state) => {
          const look = runaway.look[state.tick];
          const run = engine.slosh("stella", unit(stella.dots), runaway.k, runaway.ticks);
          const certificate = engine.certificate("stella", runaway.k);
          const row = run.history[look.tick];
          return {
            drawing: draw.drawWire({
              yaw: state.yaw, pitch: state.pitch,
              emphasis: [stella.names[0]],
              title: "The tick that stops working",
            }),
            tables: [
              table("the biggest number anywhere, tick by tick",
                ["tick", "the biggest number", "how many digits before the point"],
                runaway.look.slice(0, state.tick + 1).map((entry, index) => [
                  String(entry.tick), engine.print(entry.biggest).text,
                  String(runaway.floors[index].floor),
                ])),
              table("at this tick", ["tick", "the poked dot", "added up"],
                [[String(look.tick), engine.print(row[0]).text, show(run.totals[look.tick])]]),
              table("is this tick inside the shape's ceiling",
                ["tick", "the shape's stiffest", "the ceiling", "inside it"],
                [[show(certificate.k), show(String(certificate.eigenvalue)),
                  show(certificate.bound), certificate.holds ? "yes" : "no"]]),
              table("how far a napkin gets", ["rows it can write", "rows there are"],
                [[String(run.printable_rows), count(run.history)]]),
              table("does it come back", ["ticks run", "back where it started every"],
                [[String(runaway.ticks), run.period === 0 ? "never" : String(run.period)]]),
            ],
          };
        },
      },
      {
        anchors: ["the-smaller-tick-does-not-save-it"],
        act: "Pick a smaller tick.",
        controls: [{
          kind: "choose",
          options: runaway.stable_tried.map((tried) => ({
            label: engine.print(tried.k).text, value: tried,
          })),
        }],
        render: (state) => {
          const tried = state.choice.value;
          const certificate = engine.certificate("stella", tried.k);
          return {
            drawing: draw.drawWire({ title: "A tick inside the ceiling, and still no table" }),
            tables: [
              table("the tick you picked",
                ["tick", "the ceiling", "inside it", "rows a napkin can write",
                  "back where it started every"],
                [[show(tried.k), show(certificate.bound), certificate.holds ? "yes" : "no",
                  String(tried.printable), tried.period === 0 ? "never" : String(tried.period)]]),
            ],
          };
        },
      },
      {
        // Beats 48 and 49 fold: trying every writable tick at once is the action, and what it hands
        // the machine is the table it leaves behind.
        anchors: ["the-surprise", "what-the-machine-is-handed-and-what-comes-back"],
        act: "Try every tick at once.",
        controls: [{ kind: "press", label: "try them" }],
        render: (state) => ({
          drawing: draw.drawWire({ title: "The smallest world with room in it" }),
          tables: [
            table("every tick that holds, and what it gives you",
              ["tick", "rows a napkin can write", "back where it started every"],
              state.pressed
                ? runaway.stable_tried.map((tried) => [
                  show(tried.k), String(tried.printable),
                  tried.period === 0 ? "never" : String(tried.period),
                ])
                : []),
            // The tick is in this table, and the product of tick and stiffness is not. It used to
            // be the other way round, and a proof-reader read the two adjacent columns as the
            // comparison the verdict was making — which they are not, and under which two of the
            // three rows come out the other way. The comparison is the tick against the ceiling.
            table("the three objects, and the ceiling each one has",
              ["dots", "the shape's stiffest", "the tick", "the ceiling", "inside it"],
              refusal.ceilings.map((ceiling) => [
                String(ceiling.dots), show(ceiling.stiffest), show(refusal.tick),
                show(ceiling.bound), ceiling.holds ? "yes" : "no",
              ]), { notASum: true }),
            table("how long the search for a repeat ran",
              ["ticks searched", "ticks that came home"],
              [[String(runaway.repeat_search_ticks),
                count(runaway.stable_tried.filter((tried) => tried.period !== 0))]]),
          ],
        }),
      },
    ];
  };

  return {
    "two-dots-and-a-line": chapterOne,
    "one-tetrahedron-is-a-whole-world": chapterTwo,
    "make-it-move": chapterThree,
    "the-shape-between": chapterFour,
    "two-worlds-threaded": chapterFive,
  };
}
