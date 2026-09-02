# Our Bubble — the beat outline

*One line per beat. Each line is the question a curious reader is asking at that moment; the next
beat is the one she can't help asking next. Prose is drafted to this, not the other way round.
Bracketed notes say what evidence a beat lands on — they are for the drafters, not the reader.*

**The goal (owner, 2026-09-02): reduce complex ideas to simple ones.** The test of *simple*, applied
to every beat: she can hold the whole object in her head at that moment, and check the idea with her
own hands. The difficulty is in the world, never in the vocabulary.

**The scope rule (owner, 2026-09-02): stay in the smallest universe until a question forces us out.**
One triangle, then one tetrahedron, for as long as they can carry the idea. Every expansion — to many
tetrahedra, to a world with no edge — is the answer to something she just asked, never a change of
subject. By the time the first result appears, she owns the whole vocabulary from a napkin.

**The grain, decided once (2026-09-02):** a beat is 100–200 words, hard ceiling 220, no hard floor. Any section over 200 is listed in the PR with its one-idea reason; the excess does not migrate between chapters. **✎ beats are exempt from the band by design** — a prompt to write your guess down is supposed to be short. Any other section under 100 is listed with its reason the same way. Every `##` section carries a `<!-- beat N -->` marker. A chapter's opening prose carries one only when it is the prose that answers a beat — `tools/beat_coverage.py` reads a marker there as a declared excusal and otherwise skips the preamble, so nothing is ever inferred from a count.

**Two rules for reading this:** mark any beat that arrives before its predecessor has earned it —
that is the only kind of "too fast" there is. And mark any beat whose question you would not
actually ask — that is a chapter narrating us instead of her.

**The ritual.** From chapter 6 on, every chapter that runs an experiment has one beat marked ✎ *Before
we look*: the reader writes her guess. (Chapters 0–5 run no registered experiment — their numbers are
worked out on the page — and the history chapter, 12, runs none either: no ✎ in any of them, by
design.) Then the look, then the comparison. The book's whole method, performed by the
reader every time instead of explained to her once.

---

## 0 · The shadow

1. Why is my shadow short at noon and long in the evening?
2. If I scratch a mark where it ends and come back in an hour — what do I have?  *(two marks: a number from the world, not from me)*
3. So what is a measurement, exactly, and why is it not yet an answer?
4. Who first did the next thing with a shadow — and did you have to be a genius?  *(Eratosthenes: he ran the library at Alexandria; the measurement used none of it — one multiplication)*
5. Two posts, same noon, one shadow: what does that rule out?  *(a flat world)*
6. And how much does the ground curve — what did he actually do, step by step?  *(a fiftieth of a turn; the looked-up distance; fifty times five thousand)*
7. What was the order he did things in — and which step do people skip?  *(notice · smallest shape · say what would prove it wrong · check, keep the no)*
8. Back to her two marks: what is she still missing?  *(a reason to expect one answer rather than another — the hard part, and the book)*

## 1 · Two dots, a line, and the first thing that closes

9. Where could you put a number?  *(a dot)*
10. Where does *change* live — is it at a place?  *(between two places: a line)*
11. Two dots and a line — can anything come back to where it started?  *(no: nothing closes yet)*
12. Add a third dot. What is the smallest thing that closes?  *(a triangle: three dots, three lines — and an inside)*
13. Put a number on each corner — how many differences do I have?  *(three, one per line)*
14. Walk around the triangle adding the differences — what do I get?  *(2 → 5 → 1 → 2: +3, −4, +1 = 0)*
15. Would any three numbers do that?  *(every time — because I came home)*
16. Why *exactly* zero and not nearly?  *(plus and minus signs cancel the way integers do)*
17. What did I never use?  *(length — no line has one. And giving the lines lengths later will not disturb the zero: it comes from coming home, not from size)*
18. What have I assumed so far?  *(nothing: no distance, no direction, no time — a complete little world, not a sketch of a better one)*

## 2 · One tetrahedron is a whole world

19. What is the triangle's shape one dimension up?  *(the tetrahedron: four dots, six lines, four triangles, one inside)*
20. Count everything on it — can I hold the whole thing in my head?  *(4 · 6 · 4 · 1 — yes)*
21. Four numbers on the corners, six differences on the lines: what does each face say?  *(walk around it: zero — four faces, four zeros)*
22. What if the six line-numbers came *first* — six arrows, not six differences?  *(then a face's loop sum needn't be zero: a number that belongs to the face — how much goes round it)*
23. And the four face-numbers around the inside — add them up the same way?  *(zero again: the outside of the inside closes. Coming home, one rung up)*
24. So how many kinds of number does this world have?  *(on dots, on lines, on faces, on the inside — and that is all there ever will be)*
25. Still nothing has a length. Now give the six lines lengths — is a long line worth the same as a short one?  *(a choice, not a fact: how much each line counts. The dial, in miniature, on six lines you can see)*
26. Is this really a complete world?  *(every kind of number, both coming-home facts, and one dial — on a napkin)*

## 3 · Make it move

27. What is still missing before anything can happen?  *(a clock)*
28. What is the least a clock needs?  *(ticks, all the same)*
29. What should one tick *do*?  *(one rule: each dot's number is pushed toward its neighbours' by the differences on its lines — and carries forward the motion it has already built up. The push sets the change in the change, not the change; that one word is the difference between a wave and a leak)*
30. Is that really the whole law — nothing else, ever?  *(yes; every result in the book is that sentence, run)*
31. Run it on the tetrahedron — four numbers, tick by tick: what do they do?  *(they slosh back and forth — and every four ticks they are exactly back where they started; nothing leaks)*  [table: four numbers, ten ticks — computed at build]
32. Add the four up at every tick — what happens to the total?  *(it never changes: coming home, in time)*
33. Turn the dial — count one line for more — what changes?  *(the rhythm along that line; the total, and the average, never move)*
34. Now poke one dot hard and watch. Is there a ring?  *(no — every dot is every other dot's neighbour; there is no room, and no direction)*
35. So what question can I *not* ask in this world?  *(the stopwatch question: how fast, and is it the same every way)*

## 4 · The shape between

36. Before I go and fetch more tetrahedra — is there any room inside the one I already have?  *(divide it instead of adding to it: mark the middle of each of its six lines, and cut)*
37. Cut at those six middles — what falls out?  *(four half-size tetrahedra, one at each tip, and one new shape between them, with eight faces. Nothing was added: the four tips are an eighth each and the new shape is exactly half)*  [napkin token `octa_cut`, computed at build — not a record quotation]
38. Count the new shape — and is there room in it?  *(six dots, twelve lines, eight faces. Its dots are the six middles, so they keep the lines' names — and three pairs of them are joined by nothing at all: the first two places in this book that are not neighbours)*  [napkin token `octa_counts`]
39. Same rule, same tick, one dot poked: what happens?  *(the whole poke crosses to the opposite dot in two ticks and is home in three. A here and a there at last — and the total still never moves)*  [napkin token `octa_poke_table`]
40. Put an arrow on each of its twelve lines and walk its eight outside faces: what do they add to?  *(zero, always, whatever the arrows — every line is walked twice, once each way. The same coming-home she proved on four faces, now on eight, and still no length anywhere in it)*  [napkin token `octa_face_sum`]
41. Four of the eight faces look at a tip; the other four lie flat in the faces of the tetrahedron I cut. What fits on those?  *(one tetrahedron each, the same size as the tips — and their four new corners are the old four pushed through the middle and out the other side)*
42. So what have I got now?  *(two tetrahedra of the same size threaded through one another, sharing the shape between them: fourteen dots, thirty-six lines, and no two tips joined, so nothing crosses from tip to tip without going through the middle)*  [napkin token `stella_counts`]
43. Make it move, at the tick that has worked all along.  *(it will not. The tick is too big for this object, and instead of sloshing the numbers run away — past a hundred million by tick twenty)*  [napkin token `stella_refusal`]
44. Then pick a smaller tick?  *(you can, and then the table cannot be written down: every tick that does hold gives two rows at most, and at no tick that can be written as a fraction does this world ever come home)*
45. So what is the surprise?  *(the smallest world with room in it is already too big for a napkin. Two shapes and one rule, and arithmetic no hand can do — which is why everything after this runs on a machine)*
46. What do I hand the machine, and what comes back?  *(a rule for where the next shape goes — that is the next chapter. What comes back is this world's shadow, and it is not ours to invent: we point a test at it and keep whatever it says)*

## 5 · Room, and a world with no edge

47. Many of them, then — do tetrahedra fill space the way triangles fill a floor?  *(no — Aristotle said yes and was wrong for eighteen centuries; five leave a wedge)*  [picture: the wedge]
48. Why tetrahedra at all — what can a square do that a triangle cannot?  *(flex: pin its corners and it still leans; the triangle is finished)*
49. So every tetrahedral world is a compromise — which did we choose?  *(take a cube and colour the eight corners so that no two joined by an edge share a colour, and keep one colour — they make one regular tetrahedron, its edges the cube's face diagonals. Stack cubes: the tetrahedra never meet face to face, and between them sits **the same shape she just cut out of one tetrahedron** — an octahedron, on every corner she did not keep. Cut each one into four tetrahedra along a long diagonal, the way she cut hers, and space is all tetrahedra)*  [picture: one cube, its four kept corners, the hole beside it]
50. Now poke a dot in the middle of many — is there a ring?  *(yes: the pond)*
51. It reached the edge of our world and bounced back — how do I have no edge?  *(wrap it: the far side *is* the near side, like a screen where walking off the right returns you on the left)*
52. What is that wrapped world called, and why do we live there from now on?  *(a torus — no walls to bounce off, so the ring is only ever the ring)*
53. Now that the world has no edge — is any dot special?  *(none is singled out — but the rule for cutting the holes twists as it goes, so there are three kinds of place. They are copies of one another: turn one a third of the way round and step it over, and it lands exactly on the next kind. Counted while the page was built: three kinds, in exact thirds. The world has a grain — remember that when a ripple comes out lopsided, because a grain is one place lopsidedness can hide)*  [anchor: napkin token `vertex_classes`, computed at build — not a record quotation]
54. Can I ask the stopwatch question now?  *(yes — and this is the object: everything from here is this one thing, asked a different question)*

## 6 · Is it round?

55. Speed is distance over time — which half do I still not have?  *(distance: the dial has not been set)*
56. Doesn't counting steps give me distance?  *(a step along a cube's edge and a step across its diagonal are both "one step" — until the dial says otherwise)*
57. ✎ *Before we look:* if I give every line the same weight, will the ring be round?
58. What does the ring do on the "obvious" setting?  *(lopsided: 22.4% between directions)*  [picture: the two rings]
59. What if I weight the lines by their real geometry — the same dial, set from the shape?  *(round to 2.2%)*
60. Is 2.2% the world being slightly uneven, or my grid being coarse — how could I tell?  *(a coarse grid improves with gentler ripples; a wrong geometry does not)*
61. Could a machine decide that without my thumb on the scale?  *(hand it the timings and a written menu of laws; it picks, and says by how much)*  [picture: the fit, the runner-up]
62. Did we ever get this wrong in public?  *(the demo lopsided 3.8× for months — the mesh, not the optics; the switch is still on the page)*  [demo]
63. What did this chapter actually settle?  *(one dial decides whether the world behaves the same every way; and we can tell coarse from broken)*

## 7 · What does pushing on it cost?

64. Now that it behaves evenly — what would it cost to move a *piece* of it, contents and all?  *(the bubble)*
65. ✎ *Before we look:* what should moving the *whole* world cost?  *(nothing — it is just renaming positions)*
66. Did it charge us for that?  *(exactly zero — and why that boring number licenses everything after)*
67. Now shape the push — what came back, and did we put any of it in?  *(three things, all pre-registered)*
68. Where does the cost sit?  *(at the wall, not the middle)*  [picture: the belt]
69. Is it a shell or a ring?  *(a ring around the waist — six times the front and back)*
70. What does "negative" mean here — and what does it *not* mean?  *(below a baseline because of how the shape twists; not a reservoir)*
71. Could ordinary fields supply that sign?  *(no — they never go below the floor; the barrier, and where it sits in our own machinery)*

## 8 · Can you wall a piece off?

72. If fields can't supply the sign — is the other half of the problem softer? Is resistance to being pushed a private property, or a relationship?  *(Mach's question)*
73. ✎ *Before we look:* if I cut a region off from everything else, will what's inside get easier to push?
74. First: does the wall even isolate?  *(half a million times weaker inside)*  [picture: the fading wave]
75. How do I know I didn't just build a machine that damps everything?  *(the outside-to-outside path barely touched: 0.86)*
76. Now the blob inside — does it move differently?  *(exactly as far as before)*
77. Why not — where does a wall live in the equations?  *(at its own location, as a potential; nothing for it to change in the middle)*
78. What is that no worth?  *(under standard physics, cutting the information does not cut the inertia — a bound, not a shrug)*
79. One more way at the same barrier: can aimed fields *empty* a volume?  *(no — energies add; a point yes, a surface yes, a volume never)*  [picture: the null]

## 9 · Can a gap be emptier than empty?

80. Three noes at one barrier — is there anywhere established physics puts a real negative difference?  *(not in the fields: in what is left when you take them away)*
81. What does "empty" contain?  *(every shape a field could vibrate in, each carrying a little; the sum is the baseline)*
82. Put two walls close — what stops fitting?  *(the long shapes)*
83. So which baseline is lower, inside or outside — and why?  *(inside; we removed possibilities)*
84. ✎ *Before we look:* as the walls approach, should the difference grow or shrink?
85. What did the little world do?  *(below the line everywhere, deeper as the gap narrows — the walls pull together)*  [picture: the curve]
86. A sign is easy — what would make this the phenomenon and not a sign?  *(the scaling law and its coefficient with a π in it)*
87. Did the machine find them without being told?  *(−0.9997 vs −1; −0.13099 vs −π/24; nobody typed π)*
88. What quietly changed in this chapter?  *(the machine swept and fitted — the exponent free, the coefficient never assumed — and reported; a person only checked afterwards. The instrument that picks a law from a written menu is the ripple's, not this one's)*

## 10 · Can it tell me something I didn't tell it?

89. There is a way to make a toy look profound — what is it, and why does it never mean anything?  *(formulas hunting a known constant)*
90. What would count instead?  *(a number the method wasn't built to know, no dial to tune, checkable only after committing)*
91. Where does nature hand you such numbers?  *(critical points; universality — details stop mattering, classes share numbers)*
92. ✎ *Before we look:* should I trust an instrument on the unknown before it has recovered a known?
93. Point it at the solved case — what comes back?  *(Onsager's numbers, to six and seven digits — a calibration, not a discovery)*  [picture: markers on the known line]
94. Now take the answer key away — the case nobody has solved?  *(exponents agreeing with real matter to a few percent; no parameter they could have entered through)*
95. What was it still handed, and what happened when that was taken away too?  *(the transition temperature and one class number; the fully blind run found T_c to four parts in ten thousand)*
96. Did it miss anything — and had it said so first?  *(one quantity, too high, in exactly the direction registered in advance)*  [no figure in the record for this one (0503 has none) — the band and the miss are stated in the appendix]
97. What is left for an instrument to prove?  *(that it can tell us we were wrong)*

## 11 · When the world you built says no

98. What is the simplest kind of prediction to get wrong?  *(a law you are sure of)*
99. Put a denser lump in a resonating cavity — the pitch drops; by how much, as it gets denser?
100. ✎ *Before we look:* the whole-cavity rule is a square root — should a partial lump obey it too?  *(we registered p = −½)*
101. What came back?  *(p = −0.2753 — not a near miss; the law is refused)*  [picture: the two slopes]
102. Why — and why is the explanation written as a *new* prediction rather than an excuse?  *(the lump is a fraction of the volume; if that is the reason, a bigger lump moves p toward −½ — a new commitment)*
103. What does a refusal tell us, coming from the same kind of instrument — a fitter told nothing — that found the ripple's law, the vacuum's coefficient and the class numbers?  *(that its yeses meant something. Not the same code each time; the same discipline: no answer supplied)*

## 12 · A few thousand years of sharper shadows

104. Eratosthenes sized the Earth — why did the Sun take two thousand more years?  *(not for lack of the idea)*
105. Aristarchus had the right triangle — how could the right method give the wrong answer?  *(87° read for 89.85°: the resolution, not the man)*  [picture: the knife-edge angle]
106. What is the difference between being wrong and being unable to see yet?
107. When nobody could see the stars shift, what were the two readings — and which one held for a thousand years?  *(the null read as absence, not as a bound)*
108. What finally changed — the idea, or the instrument?  *(Rømer, the transit of Venus, Bessel's third of an arcsecond)*
109. Now look back at our two "failures" — what did they turn out to be?  *(the locator's own margin, never carried through; both landed inside their bands once it was; nothing re-run, nothing in the world changed)*
110. Why is that the star that was never fixed — and why is it the rarest thing an instrument can do?  *(find that a published miss was its own bookkeeping, and say so on the record)*

## 13 · Cast your own shadow

111. What did we actually do — in one honest sentence?  *(inspected one object we built, and watched its tools do seven things)*
112. Can I follow one result without running anything?  *(four files, ten minutes: question → data → verdict → summary, in that order)*
113. What travels with the book, and what does the book promise about it?  *(the record, verbatim, checked on every build — and exactly which sentences no program has read)*
114. What is the check that would actually catch us?  *(re-run a test at full size, let it overwrite the data the book quotes, ask git)*
115. ✎ Before you press Return — what do you expect?
116. Where is the next shadow?

---

*Appendix · The Simulations — unchanged: every number in the chapters above, its source file, its
test, its regenerate command. The chapters stay free of it; it stays complete.*

*Drafter's note on chapters 1–4: every number there is finger-countable, so the book should compute
them at build time (the counts, the loop sums, the ten-tick table, the octahedron's crossing and the
threaded pair's refusal) the way the synthesis page recomputes its own — "checked while this page was
built" — rather than quoting them. Whether the napkin examples also become tiny registered rungs in
the engine is a Structure-lane decision.*

*Drafter's note on chapter 4 (owner, 2026-09-02): the geometry of the finding is just this — a
tetrahedron reduces to four smaller tetrahedra at the tips and an octahedron between them; that same
octahedron has room for four more tetrahedra, and their numbers are a surprise world with an
interesting shadow. The frame for the clock is **information transfer**: "time" in this book is only
ever the ticks we count. And the shadow is the reader's forward question, never a claim — the book's
shadows are the record's results, so beat 46 asks what this world's shadow will look like and hands
her on. What chapter 4 may and may not say is settled in [`notes/octahedron-crossing.md`](notes/octahedron-crossing.md):
the three refuted readings — that a tick is a trip round the octahedron, that gathering there saves
work, that it finishes a calculation first — stay out of the prose and live in the appendix.*
