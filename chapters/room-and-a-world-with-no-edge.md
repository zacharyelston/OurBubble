# Room, and a world with no edge

> **Scope.** The object in this chapter is a **toy** — a structure we built, not a description of
> space. The construction is exact inside the toy. It is not evidence that physical space is
> discrete, and the object we end up with is a choice rather than a discovery.

<!-- NOTE(figure): two studies wanted here; the Illustration lane owns drawing them. -->
<!-- NOTE(figure): (a) the wedge — caption: "Analogy — not data. Five tetrahedra packed around one shared edge, and the gap the sixth cannot fill. The measured angles are in the appendix." -->
<!-- NOTE(figure): (a) alt — "Five identical tetrahedra fanned around a common edge, nearly closing a full turn, with the narrow remaining wedge picked out so it is visibly too thin to hold a sixth." -->
<!-- NOTE(figure): (a) brief — the near-miss is the whole point, so the wedge must read as thin-but-real at a glance. Show the shared edge end-on. Do not exaggerate the gap; if it looks roomy the picture lies. -->
<!-- NOTE(figure): (b) one cube, its four kept corners, and the hole beside it — caption: "Analogy — not data. Colour a cube's corners so neighbours never match, keep one colour, and the four you kept are a tetrahedron. Stack cubes and the gaps between the tetrahedra are octahedra, each centred on a corner you threw away." -->
<!-- NOTE(figure): (b) alt — "One cube with its eight corners two-coloured; the four corners of a single colour joined by face diagonals into a tetrahedron; and beside it the eight-sided hole that appears between such tetrahedra once the cubes are stacked, with a discarded corner at its centre." -->
<!-- NOTE(figure): (b) brief — the two-colouring must read as a rule rather than a decoration: a reader should be able to re-derive which corners are kept. Distinguish kept from discarded by more than hue, and make the hole's centre visibly one of the discarded corners, because that identification is the beat. -->

The last chapter left you stuck. One tetrahedron has no room in it, so it cannot have a ripple, so
it cannot answer the only question you actually wanted to ask.

The fix seems obvious. If one tetrahedron is too small, use a lot of them, stacked together, the way
a floor is tiled with triangles.

Do they stack?

## They do not stack

No, and the way they fail is one of the better stories in mathematics.

Aristotle wrote that tetrahedra all of one size and shape will fill space, and the mistake stood for
something like eighteen centuries before anyone checked properly. They come *very close*, and very
close is the whole story.

Stack them around one shared line, like slices of a cake meeting at the spine. The angle at which
two faces of a tetrahedron meet along the line they share is **70.5288°**, so closing a full turn of
360° would take **5.1043** of them. Five fit. The sixth has **7.3561°** of room and needs the full
70°-odd. What is left is a thin wedge that nothing can fill.

Which raises a fair question: why insist on tetrahedra at all?

## What a square can do that a triangle cannot

Because triangles are rigid and squares are not, and rigidity is the property you cannot do without.

Pin the four corners of a square and it can still flex. It leans over into a diamond without any
corner leaving its pin, because nothing fixes the diagonals. A triangle cannot do that. Fix its
three corners and the triangle is finished — it is the smallest patch that holds its own shape. One
step up, the tetrahedron is rigid for the same reason.

A building block that can quietly change shape is not a building block; it is a source of errors you
will never find. So: tetrahedra, and the wedge, and no perfect answer.

If there is no perfect answer, what did we choose?

## The compromise we chose

Every tetrahedral world is a compromise, and a compromise is a *choice* — which has consequences,
which can be measured.

Here is ours, with a pencil. Colour a cube's eight corners in two colours so that **no two corners
joined by an edge ever share a colour**. There is exactly one way, and you will find it in seconds:
opposite corners of each face match, neighbouring ones never do.

Now throw half away. **Keep one colour, discard the other.** The four you kept are joined to one
another by diagonals across the cube's faces, so all six gaps between them are equal — which makes
them one regular tetrahedron. One cube, one tetrahedron.

Stack the cubes, keeping the same colour throughout. The tetrahedra never meet face to face, and the
gaps between them are not thin wedges any more: each is shaped like an octahedron, and each is
centred on one of the corners you threw away.

Octahedra are easy. Pick a long diagonal, cut along it, and one falls into four tetrahedra. Do that
to every hole and space is filled entirely with tetrahedra — not all the same shape, which is the
compromise, and no wedge left anywhere.

## Is any dot special?

Before poking anything, one question worth settling, because the next chapter depends on the answer.

You threw away half the corners, cut the holes along diagonals, and did all of it by recipe. It
would be easy to end up with a lopsided thing — some dots in the thick of it, others out on a limb,
a few sitting on seams where the recipe changed its mind. If that were so, poking one dot and poking
another would not be the same experiment, and no comparison between directions would mean anything.

It is not so. Every dot in this world sees the same arrangement around it: the same lines, going the
same ways, to neighbours the same distance off. There is no special place, no centre and no seam.

That is exactly what a fair test of a ripple needs, and you now have it. So poke a dot in the middle
of a great many, and watch.

Now you have room. So: poke a dot in the middle of a great many, and watch.

## The pond

There is a ring.

A big number on one dot, and on the next tick it has moved to that dot's immediate neighbours, and
on the tick after that to theirs. There is now a front — a place the disturbance has reached — with
untouched quiet ahead of it and, behind it, water still moving. Exactly the pond.

Nothing new was added to get this. The rule is the same sentence as before, unchanged — each dot
pushed toward its neighbours by the differences on its lines, carrying forward the motion it has
built up. The carrying is what makes a front: a dot set moving keeps moving after the push has
passed it, which is exactly the water still going behind the ring.

All that changed is that a dot now has neighbours it is not joined to directly, and reaching them
takes ticks. You can count how many lines the front has crossed. Whether that count is a *distance*
is a separate question, and not one this chapter answers.

Watch it a little longer, though, and it does something a pond in a field does not.

## It hits the edge

It reaches the outermost dots and comes back.

Of course it does. Our stack of tetrahedra stops somewhere, and the dots at the boundary have fewer
lines than the ones inside, so the rule does something different to them. The ripple bounces, the
reflection runs back inward, and it collides with the ripple still going out. What you are now
watching is not a ripple; it is a ripple plus an echo. You can still measure cleanly if you finish
before the echo gets back — but that caps how long any experiment may run, and the bigger the thing
you want to watch, the worse the cap.

You could build a bigger box, but a bigger box has the same problem further away. What you want is a
world with no edge at all — and there is a cheap trick for that.

## Wrap it

Glue the far side to the near side.

Say a dot on the extreme right has no right-hand neighbour. Give it one: the dot on the extreme
left. Do that in every direction. Now no dot is on a boundary, because there is no boundary — every
dot has exactly the neighbours every other dot has.

You have seen this. It is the old arcade screen where a ship leaving the right edge reappears on the
left, unbothered, still flying. The screen is not infinite; it is finite and it has nowhere to fall
off.

The arcade screen wraps in two directions, and mathematicians call that shape a **torus** — the same
word they use for a doughnut, because rolling the screen into a tube and bending the tube round to
meet itself gives you one. Ours wraps in three directions rather than two, so it is the same trick
done once more, and the name comes along for the ride. What matters is not the word but why we live
there from here on: with no walls, nothing bounces, so the ring is only ever the ring.

Which means the question you have been unable to ask is finally available.

## The object, and the only question left

You can now ask the stopwatch question. Poke a dot, count the ticks, and see how far the front has
gone — and then do it again in a different direction and compare.

Take stock, because the list is short and all but one item was forced. Dots, because a number needs
somewhere to sit. Lines, because change lives between. A triangle, because it was the first thing
that closed. A tetrahedron, because that is the triangle one dimension up — and, once stacking came
up, because it holds its shape where a cube does not. A clock and one rule, because nothing could
happen. Many tetrahedra, because one had no room. The two-colouring and the discarded half, because
tetrahedra will not stack alone. A wrap, because edges echo.

The exception is the dial — the only thing anybody chose. Nothing has forced a setting yet.

That is the object. Everything from here is this one thing, asked a different question — and the
first question is whether the ring it makes is actually round.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-room-and-a-world-with-no-edge).*

**Next:** [Is it round?](the-round-ripple.md)—the dial gets set, twice, and one of the settings is
wrong in a way you can see.