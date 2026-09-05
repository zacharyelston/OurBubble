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
 *
 * A walk's table adds `{ runs: [terms, running] }` — column `terms` holds each step's own number and
 * column `running` holds the engine's sum after that step, so the check can hold the second to the
 * first down the rows. Both come off `walk_json`; neither is added up here.
 *
 * And `tag` is the name the cross-check knows a table by. It is not shown to anybody: it is how the
 * gate that says *this step's numbers are this entry point's answer* finds the table it is written
 * against, so that renaming a caption moves nothing and deleting the tag is a failure rather than a
 * quiet exemption.
 */
const table = (caption, head, rows, shape = null, tag = null) =>
  ({ caption, head, rows, shape, tag });

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
    // The world of the second and third beats, by the name the engine answers to for it.
    const TWO_DOTS = "two-dots";
    const first = P.triangle.chapter.values;
    const second = P.triangle.another.values;
    const corners = NAMES.slice(0, count(first));
    // The first row of the triangle's run at the tetrahedron's tick that a napkin cannot write
    // down — the engine's own count of how far it gets says which row that is.
    const atBook = R.triangle_motion.at_the_book_tick;
    const unprintable = atBook.history[atBook.printable_rows][0];

    /** The three differences the object works out from three corner numbers, and their walk. */
    const differencesOf = (values) => {
      const edges = engine.loops("triangle", values, 0).loops;
      // The walk round the face, from the engine: which lines it takes and in which order, what
      // each step costs, the sum after each step, and the total. A proof-reader caught the first
      // version printing each line's own difference in the walk column, so that three terms were
      // shown adding to a total they visibly did not make: +3, −1, −4 under "added up: 0". The
      // walk uses AC the other way and its term is +1 — the engine's answer, not a sign flipped
      // here, and now its running column as well, so the total is watched being made.
      return { edges, walk: engine.walk("triangle", 1, 0, edges) };
    };

    const triangleLines = LINES.filter((name) => !name.includes(NAMES[3]));

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
          // Two dots and a line is a world the engine answers for in its own right now, so the
          // difference on `AB` is asked of THAT world rather than read off a triangle with the
          // third corner set to nothing. It is the same line and the same coboundary either way —
          // and asking the world she is looking at is what the engine could not do before.
          const values = state.numbers;
          const held = engine.loops(TWO_DOTS, values, 0);
          const name = triangleLines[0];
          return {
            drawing: draw.drawTriangle({
              dots: 2, emphasis: [name],
              values: {
                [corners[0]]: show(values[0]), [corners[1]]: show(values[1]),
                [name]: signed(held.loops[0]),
              },
              title: "Two dots, and the change between them",
            }),
            tables: [
              table("the two numbers", ["dot", "number"],
                corners.slice(0, 2).map((dot, index) => [dot, show(values[index])])),
              table("what the line holds", ["line", "from these two", "difference"],
                [[name, `${show(values[1])} − ${show(values[0])}`, signed(held.loops[0])]],
                null, "two-dots-difference"),
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
          // Why nothing comes home, from the world itself: the engine counts the closed walks two
          // dots and a line has, and the count is none. This used to be a sentence the page was
          // trusted on, because the browser surface had no such world to ask.
          const closed = engine.loops(TWO_DOTS, [ZERO], 1);
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
              table("what closes here", ["walks that close", "so does anything come home"],
                [[closed.closed_walks === 0 ? "none" : String(closed.closed_walks),
                  closed.closed_walks === 0 ? "no" : "yes"]],
                null, "two-dots-closed"),
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
                  closed ? count(rung(3, KINDS[2])) : "none"]], { notASum: true }),
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
          const { edges, walk } = differencesOf(state.numbers);
          // The cycle is the engine's too: the dots of the face it walks, in the order it walks
          // them, so the arrows on the drawing and the steps in the table are one list.
          const cycle = walk.cell_dots.map((from, index) =>
            [from, walk.cell_dots[(index + 1) % walk.cell_dots.length]]);
          const taken = cycle.slice(0, state.tick);
          const home = state.tick >= cycle.length;
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, arrows: taken,
              values: netValues(state.numbers, edges),
              title: home ? "Home, and holding nothing" : "The walk round the triangle",
            }),
            tables: [
              // Every column here is the engine's answer to one question. Which line each step
              // takes and which way round it goes are the walk's own `steps` and `signs` — the page
              // does not work out that AC is walked against itself, and it does not flip a sign to
              // suit. What the step costs is that term. And the sum so far is the walk's running
              // column, so a reader watches the total being made instead of being handed it: the
              // engine had no such column until now, and the page may not add up.
              table("the walk, step by step",
                ["step", "line", "walked", "what it costs you", "what you are holding"],
                taken.map(([from, to], index) => [
                  `${corners[from]} → ${corners[to]}`, walk.steps[index],
                  walk.signs[index] > 0 ? "the way it points" : "the other way",
                  signed(walk.terms[index]), show(walk.running[index]),
                ]), { runs: [3, 4] }, "walk-running"),
              table("what the whole walk comes to",
                ["what the steps so far cost you", "the whole way round"],
                [[walk.terms.slice(0, state.tick).map(signed).join("  ") || "nothing yet",
                  home ? show(walk.sum) : "not home yet"]],
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
          const { edges, walk } = differencesOf(values);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, values: netValues(values, edges),
              title: "Other numbers, the same nothing",
            }),
            tables: [
              cornerTable(values),
              // The terms the walk uses, not each line's own difference. The unprintable-corner
              // step already printed
              // these; here the two tables sat side by side — AC as −1 in one and +1 in the packed
              // row of the other — with nothing on the page reconciling the sign.
              table("the terms the walk uses, and what it holds on the way",
                ["line", "its term", "what you are holding"],
                walk.steps.map((name, index) =>
                  [name, signed(walk.terms[index]), show(walk.running[index])]),
                { runs: [1, 2] }, "walk-running"),
              table("what the whole walk comes to", ["the three terms, as the walk uses them",
                "added up"],
                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),
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
          const { edges, walk } = differencesOf(values);
          const printed = values.map((value) => engine.print(value));
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true, values: netValues(values, edges),
              title: state.pressed ? "A number the napkin will not print" : "Three plain numbers",
            }),
            tables: [
              table("the corners", ["dot", "number", "does a napkin print it"],
                corners.map((name, index) =>
                  [name, printed[index].text, printed[index].refused ? "no" : "yes"])),
              // The terms the walk uses, not each line's own difference. A reader found the old
              // version listing +3, −1, −4 and then "added up 0" — two tables making one wrong
              // claim between them. Every table on these pages that prints a total now prints the
              // terms of THAT total beside it.
              table("the terms the walk uses, and what it holds on the way",
                ["line", "its term", "does a napkin print it", "what you are holding"],
                walk.steps.map((name, index) => {
                  const term = engine.signed(walk.terms[index]);
                  return [name, term.text, term.refused ? "no" : "yes",
                    show(walk.running[index])];
                }), { runs: [1, 3] }, "walk-running"),
              table("what the whole walk comes to",
                ["the three terms, as the walk uses them", "added up"],
                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),
            ],
          };
        },
      },
      {
        // The two folded here — "what you never used" and "nothing at all" — have nothing of
        // their own to do, and the one action
        // that answers both is taking every number away. What is left is the world, which is what
        // both beats are about — no length was ever used, and nothing was ever assumed.
        anchors: ["what-you-never-used", "nothing-at-all"],
        titleFrom: "nothing-at-all",
        act: "Take every number away.",
        controls: [{ kind: "press", label: "clear" }],
        render: (state) => {
          const values = state.pressed ? corners.map(() => ZERO) : first;
          const { edges, walk } = differencesOf(values);
          return {
            drawing: draw.drawTriangle({
              dots: 3, showFace: true,
              values: state.pressed ? {} : netValues(values, edges),
              title: state.pressed ? "The world, with nothing on it" : "The world, with numbers on it",
            }),
            tables: state.pressed ? [
              table("what is still here", ["what", "how many"], censusRows(3)),
              table("what it has never had", ["a length", "a direction", "a clock"],
                [["none", "none", "none"]]),
              // No numbers, so no walk. It used to print "0 0 0 → 0" here — three differences that
              // came out at nothing — beside a drawing showing nothing at all. The claim of the
              // beat is that the world is complete with nothing on it, which is the census above.
              table("what there is to add up", ["numbers on it", "differences"],
                [["none", "none"]]),
            ] : [
              table("what is still here", ["what", "how many"], censusRows(3)),
              table("what it has never had", ["a length", "a direction", "a clock"],
                [["none", "none", "none"]]),
              table("what the walk comes to",
                ["the three terms, as the walk uses them", "added up"],
                [[walk.terms.map(signed).join("  "), show(walk.sum)]], { total: 1 }),
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
        // Folded: the count is what adding the dot shows, so there is one action.
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
              // The corners she typed and the zero each face comes to — which is the question. The
              // six differences are in the table immediately under the drawing; putting them here
              // as well made thirty-eight labels on one small frame, and a drawing nobody can read
              // is not more honest for carrying more.
              //
              // And the six line NAMES come off too, not just their numbers. A reader pointed out
              // that leaving them made the drawing carry six empty slots exactly where a value
              // would go, so it read as having lost its numbers rather than never having carried
              // them — with the title promising six differences right above it. The table beneath
              // names every line.
              lines: false,
              values: Object.fromEntries([
                ...NAMES.map((name, index) => [name, show(state.numbers[index])]),
                ...FACES.map((name, index) => [name, show(loops.loops[index])]),
              ]),
              title: "Four corner numbers, and what each face comes to",
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
          // The walk round the inside, from the engine: the four faces in the order it takes them,
          // what each one costs, and the sum after each — the coming-home built in front of her
          // rather than announced under four numbers.
          const inside = engine.walk("tetrahedron", 2, 0, loops.loops);
          return {
            drawing: draw.drawNet({
              lines: false,
              values: Object.fromEntries(
                FACES.map((name, index) => [name, show(loops.loops[index])])),
              title: "The four face-numbers, walked round the inside",
            }),
            tables: [
              table("each face's number", ["face", "how much goes round it"],
                FACES.map((name, index) => [name, show(loops.loops[index])])),
              // The same fix as chapter 1's walk, one rung up: the walk round the inside uses each
              // face in a direction, and two of the four the other way. The terms it actually adds
              // are asked of the engine, so that four numbers and their total are one arithmetic a
              // reader can do herself — and the sum is shown building, face by face, which is the
              // running column the engine had nothing to answer with before.
              table("the inside, face by face",
                ["face", "its term", "what you are holding"],
                inside.steps.map((name, index) =>
                  [name, signed(inside.terms[index]), show(inside.running[index])]),
                { runs: [1, 2] }, "walk-running"),
              table("the inside, walked round",
                ["the four terms, as the walk uses them", "added up"],
                [[inside.terms.map(signed).join("  "), show(inside.sum)]], { total: 1 }),
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
        // Folded: the dial is the action, and "is this a complete world" is what the
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
    // Where the dial starts: the weights the register ran the dialled row at, one line counted for
    // more than the rest. Plain is what every other line is worth, and what turning one back to
    // gives the run with no dial in it at all.
    const plainWeight = ONE;
    const dialed = P.motion.dialed_line;
    // The triangle's own ceiling, asked of the engine rather than written down here — it is the
    // third tick the reader can try, and the one the certificate refuses.
    const triangleCeiling = engine.certificate("triangle", k).bound;
    const triangleNames = NAMES.slice(0, count(triangleCorners));
    const hops = R.no_room.hops;

    const runTable = (caption, history, totals, names, tag = null) =>
      table(caption, ["tick", ...names, "added up"],
        history.map((row, tick) => [String(tick), ...row.map(show), show(totals[tick])]),
        { total: names.length + 1 }, tag);

    const printableRow = (history, printable) => table("how far a napkin gets",
      ["rows it can write", "rows there are"], [[String(printable), count(history)]]);

    return [
      {
        // Folded: one action answers both — press the clock and watch nothing happen,
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
              [[String(state.tick), "none"]]),
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
        // Folded: "is that really the whole law" is answered by there being one
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
              table("the tick it runs at", ["tick"], [[show(run.k)]], { notASum: true }),
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
        act: "Run it at another tick.",
        controls: [{
          kind: "choose",
          // The ticks label themselves, in the engine's own printing of them. A word here would be
          // a word explaining what the number already says. The third of them is the triangle's own
          // ceiling, which the engine now answers for this shape: at it, the certificate does not
          // hold, and the refusal she gets is the engine's rather than a sentence about one.
          options: [atShape.k, atBook.k, triangleCeiling].map((tick) =>
            ({ label: show(tick), value: tick })),
        }],
        render: (state) => {
          const chosen = state.choice.value;
          const run = engine.slosh("triangle", triangleCorners, chosen, ticks);
          // The certificate for THIS shape at THIS tick. `certificate_json` used to panic on the
          // triangle rather than answer, so the beat where the ceiling belongs to the shape could
          // only show the two runs and let a reader infer the ceiling from them.
          const certificate = engine.certificate("triangle", chosen);
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
              // The ceiling, and the two integers that certify it: the shape's stiffest number and
              // the eigenvector a reader can multiply out on the napkin herself. No eigensolver and
              // no floating point anywhere in it.
              table("is this tick inside the shape's ceiling",
                ["tick", "the shape's stiffest", "the numbers it is stiffest on", "the ceiling",
                  "inside it"],
                [[show(certificate.k), show(String(certificate.eigenvalue)),
                  certificate.eigenvector.map((value) => show(String(value))).join("  "),
                  show(certificate.bound), certificate.holds ? "yes" : "no"]],
                { notASum: true }, "triangle-certificate"),
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
                  show(certificate.bound), certificate.holds ? "yes" : "no"]],
                { notASum: true }, "tetrahedron-certificate"),
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
              // Captioned for what it shows rather than "the total": the three numbers in this row
              // are not a sum of one another, and a caption that reads like one invites the
              // addition a reader was right to try.
              table("the whole of it, then and now",
                ["at the start", "at this tick", "ticks apart"],
                [[show(run.totals[0]), show(run.totals[state.tick]), String(state.tick)]], { notASum: true }),
            ],
          };
        },
      },
      {
        anchors: ["turn-the-dial"],
        act: `Count ${dialed} double.`,
        controls: [
          // Every line worth the same, which is where the rule has been all chapter. The dial is
          // hers to turn from there: a reader who opens on a dial already turned has been shown
          // the answer and has nothing to change, and cannot see the rhythm move at all.
          // …and the register's own dialled position among the states this is driven into, so that
          // the state the beat is about is one the checks walk rather than one only a reader
          // reaches. Every line the same is a dial nobody has turned.
          { kind: "numbers", names: LINES, initial: LINES.map(() => plainWeight),
            also: [R.gaps.dial.weights] },
          { kind: "tick", count: ticks, noun: "tick" },
        ],
        render: (state) => {
          // The dial is a question now, not two answers. It used to offer the two runs the engine
          // had computed and vendored — every line the same, and AB counted double — because the
          // browser surface ran the rule with one weight for every line and could not be asked
          // anything else. It can: she sets a weight per line and the run is re-run from them.
          const run = engine.sloshWeighted("tetrahedron", tetraCorners, state.numbers, k, ticks);
          const turned = LINES.filter((name, index) => state.numbers[index] !== plainWeight);
          return {
            drawing: draw.drawNet({
              emphasis: turned,
              values: Object.fromEntries(NAMES.map((name, index) =>
                [name, show(run.history[state.tick][index])])),
              // What the title may say is that they are no longer all the same. It said "a line
              // counted for more", which is a claim about a direction the dial does not have: she
              // can count a line for less, and she can turn five and leave one.
              title: turned.length === 0
                ? "Every line, counted the same"
                : "The lines, no longer all counted the same",
            }),
            tables: [
              // What the dial is set to, which is what the run below was asked with.
              table("what each line is worth", ["line", "worth"],
                LINES.map((name, index) => [name, show(state.numbers[index])]),
                null, "dial-weights"),
              runTable("every tick", run.history, run.totals, NAMES, "dial-run"),
              // How far a napkin gets, as every other run in this chapter says it — a dial she can
              // turn to a weight of her own can send the run past what a napkin will write, and a
              // run that does that says so here rather than only in its own rows.
              printableRow(run.history, run.printable_rows),
              // What the dial changed and what it did not, both off the same run: the total is the
              // number it was at the start — printed beside itself, which is the claim — and the
              // rhythm is the engine's period.
              table("what the dial changed, and what it did not",
                ["back where it started every", "the total at the start", "the total now"],
                [[run.period === 0 ? "never" : String(run.period),
                  show(run.totals[0]), show(run.totals[state.tick])]], { notASum: true }),
            ],
          };
        },
      },
      {
        // Folded: the poke is the action, and "what can I not ask here" is what the
        // hop table under it says — every dot is one line from every other, so there is no further.
        anchors: ["where-is-the-ring", "the-question-this-world-cannot-answer"],
        act: `Poke ${NAMES[0]}.`,
        controls: [{ kind: "tick", count: ticks, noun: "tick" }],
        render: (state) => {
          const run = engine.slosh("tetrahedron", unit(count(NAMES)), k, ticks);
          // Dots that are not at nothing — which is not "dots that moved by this tick", the
          // heading this used to carry. The engine's browser surface gives no tick-to-tick
          // difference, so rather than compute one here the column says what the number is; the
          // difference is asked for as a gap.
          const notAtNothing = run.history[state.tick]
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
                ["the furthest apart two dots are", "other dots not at nothing"],
                [[String(R.no_room.diameter), notAtNothing.length === 0 ? "none"
                  : String(notAtNothing.length)]]),
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
    // The arrow set the outward walk is asked about, from the engine's own payload.
    const faceArrows = P.face_sum.arrows;
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
              [[count(LINES), state.pressed ? String(cut.middles) : "none"]]),
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
              [[String(cut.corners), String(cut.octahedra), String(cut.dots)]], { notASum: true }),
            // The two shares print differently because the engine's rule prints one and refuses the
            // other — an eighth is not a short decimal, a half is. Side by side with nothing said,
            // 1/8 beside 0.5 looks like two kinds of carelessness rather than one rule, so the row
            // says which is which.
            table("and how much of the original each one is",
              ["each of the tips", "a napkin prints it", "how many tips",
                "the shape between", "a napkin prints it"],
              [[show(cut.tip_share), engine.print(cut.tip_share).refused ? "no" : "yes",
                String(cut.corners),
                show(cut.core_share), engine.print(cut.core_share).refused ? "no" : "yes"]],
              { notASum: true }),

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
              [[String(cut.oct_dots), String(cut.oct_lines), String(cut.oct_faces)]], { notASum: true }),
            table("every dot's neighbours", ["dot", "lines out of it", "dots it is not joined to"],
              MID.map((name) => [name, String(cut.oct_degree),
                count(cut.opposite_pairs.filter((pair) => pair.includes(name)))])),
            ...(state.pressed ? [table("the pairs joined by nothing",
              ["one", "the other", "lines between them"],
              // "none", not a nought. A zero in a column of counts reads as a measurement that
              // came out at nothing; what this says is that there is nothing there to measure.
              cut.opposite_pairs.map(([a, b]) => [a, b, "none"]))] : []),
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
                  show(certificate.bound), certificate.holds ? "yes" : "no"]],
                { notASum: true }, "octahedron-certificate"),
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
          // The outward walk, asked of the engine. The vendored `face_sum` carried the eight
          // numbers and their total and nothing else, so the page could show which faces had been
          // walked and not what the walk was doing: `face_sum_json` answers per face — the cycle of
          // lines each one takes, the orientation it took them in, and the sum building face by
          // face — which is what this beat is about.
          const fs = engine.faceSum("octahedron", faceArrows);
          // One count, and everything reads off it. The walker used to say "faces walked 0" beside
          // a table listing one, all the way up to "7 of 8" beside a table listing eight — two
          // counters of the same thing disagreeing at eight of nine states. The tick IS the number
          // walked: none at the start, the last of them at the end.
          const walked = fs.face_numbers.slice(0, state.tick);
          const last = walked.length === cut.oct_faces;
          const face = state.tick === 0 || last ? null : state.tick - 1;
          return {
            drawing: last
              ? draw.drawRing({
                tips: atATip.map((entry) => entry.index),
                title: "Four faces looking at a tip, and four left bare",
              })
              : draw.drawRing({
                face,
                // The title reads off the count. It said a face had been walked at the state where
                // none had — and a still carries its title into the downloaded file and a screen
                // reader reads it aloud, so a false title is worse there than on the page.
                title: walked.length === 0
                  ? "The shape between, before the walk"
                  : "One face, walked round",
              }),

            tables: [
              table("the arrows on the lines", ["line", "arrow"],
                cut.mid_lines.map(([a, b], index) =>
                  [`${MID[a]} → ${MID[b]}`, signed(fs.arrows[index])])),
              // Each face named by the walk that goes round it — the engine's own cycle, in the
              // order it takes the three dots, which is what "outward" means on this face. Then
              // what that face comes to and the sum after it. All three are the same answer.
              table("each face, walked",
                ["face, in the order it is walked", "what goes round it", "what you are holding"],
                walked.length === 0
                  ? [["none yet", "none yet", "none yet"]]
                  : walked.map((value, index) => [
                    fs.cycle_names[index].join(" → "),
                    signed(value), show(fs.running[index]),
                  ]), { runs: [1, 2] }, "face-walk"),

              // The terms and the total in one table, so the check can add them up. They were in
              // two, which is the other way a proof-reader silenced this guard.
              table("all of them added up",
                ["the faces walked so far", "added up"],
                [[walked.map(signed).join("  ") || "none yet",
                  last ? show(fs.sum) : "not all walked yet"]], { total: 1 }),
              table("how far round it has got",
                ["faces walked", "faces there are", "lines walked, each way once",
                  "which way round"],
                [[count(walked), String(cut.oct_faces),
                  last ? String(fs.lines_walked_each_way) : "not all walked yet",
                  fs.orientation]],
                { notASum: true }, "face-count"),
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
            title: state.tick === 0
              ? "Four faces looking at a tip, and four still bare"
              : (state.tick === flat.length
                ? "A tip on each face that was bare"
                : "Tips going on, one face at a time"),

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
                ["tick", "the biggest number", "at least this big"],
                runaway.look.slice(0, state.tick + 1).map((entry, index) => [
                  String(entry.tick), engine.print(entry.biggest).text,
                  String(runaway.floors[index].floor),
                ]), { notASum: true }),
              // The total of all fourteen, at a tick, beside the one dot the poke started on.
              // The fourteen are not printed here, so this is a figure reported rather than a sum
              // the page shows — which the check is told, so that it neither adds two numbers that
              // are not terms nor lets a real sum hide behind the same words.
              table("at this tick", ["tick", "the poked dot", "everything, added up"],
                [[String(look.tick), engine.print(row[0]).text, show(run.totals[look.tick])]],
                { notASum: true }),
              table("is this tick inside the shape's ceiling",
                ["tick", "the shape's stiffest", "the ceiling", "inside it"],
                [[show(certificate.k), show(String(certificate.eigenvalue)),
                  show(certificate.bound), certificate.holds ? "yes" : "no"]],
                { notASum: true }, "stella-certificate"),
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
                  String(tried.printable), tried.period === 0 ? "never" : String(tried.period)]],
                { notASum: true }, "stella-tried"),
            ],
          };
        },
      },
      {
        // Folded: trying every writable tick at once is the action, and what it hands
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
                : [["none tried yet", "none tried yet", "none tried yet"]]),

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
