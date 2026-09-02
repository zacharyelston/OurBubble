# Room, and a world with no edge

> **Scope.** The object in this chapter is a **toy** — a structure we built, not a description of
> space. The construction is exact inside the toy. It is not evidence that physical space is
> discrete, and the object we end up with is a choice rather than a discovery.

<!-- NOTE(figure): two studies wanted here; the Illustration lane owns drawing them. -->
<!-- NOTE(figure): (a) the wedge — caption: "Analogy — not data. Five tetrahedra packed around one shared edge, and the gap the sixth cannot fill. The measured angles are in the appendix." -->
<!-- NOTE(figure): (a) alt — "Five identical tetrahedra fanned around a common edge, nearly closing a full turn, with the narrow remaining wedge picked out so it is visibly too thin to hold a sixth." -->
<!-- NOTE(figure): (a) brief — the near-miss is the whole point, so the wedge must read as thin-but-real at a glance. Show the shared edge end-on. Do not exaggerate the gap; if it looks roomy the picture lies. -->
<!-- NOTE(figure): (b) the two families — caption: "Analogy — not data. A cube's eight corners sorted by whether their coordinates add up odd or even: two tetrahedra threaded through each other, sharing no line." -->
<!-- NOTE(figure): (b) alt — "A cube with its eight corners two-coloured, the four of one colour joined into one tetrahedron and the four of the other into a second, the two interpenetrating without any line in common." -->
<!-- NOTE(figure): (b) brief — the two-colouring must read as a rule rather than a decoration: a reader should be able to re-derive which corner belongs to which family. Distinguish the families by more than hue. -->

The last chapter left you stuck. One tetrahedron has no room in it, so it cannot have a ripple, so it
cannot answer the only question you actually wanted to ask.

The fix seems obvious. If one tetrahedron is too small, use a lot of them, stacked together, the way
a floor is tiled with triangles.

Do they stack?

## They do not stack

No, and the way they fail is one of the better stories in mathematics.

Aristotle wrote that regular tetrahedra fill space, and the mistake stood for something like eighteen
centuries before anyone checked properly. They come *very close*, and very close is the whole story.

Stack them around one shared edge, like slices of a cake meeting at the spine. The angle at which two
faces of a tetrahedron meet along an edge is **70.5288°**, so closing a full turn of 360° would take
**5.1043** of them. Five fit. The sixth has **7.3561°** of room and needs seventy. What is left is a
thin wedge that nothing can fill.

Which raises a fair question: why insist on tetrahedra at all?

## What a square can do that a triangle cannot

Because triangles are rigid and squares are not, and rigidity is the property you cannot do without.

Pin the four corners of a square and it can still flex. It leans over into a diamond without any
corner leaving its pin, because nothing fixes the diagonals. A triangle cannot do that. Fix its three
corners and the triangle is finished — it is the smallest patch that holds its own shape. One step up,
the tetrahedron is rigid for the same reason.

A building block that can quietly change shape is not a building block; it is a source of errors you
will never find. So: tetrahedra, and the wedge, and no perfect answer.

If there is no perfect answer, what did we choose?

## The compromise we chose

Every tetrahedral world is a compromise. That matters more than it sounds, because a compromise is a
*choice*, a choice has consequences, and consequences can be measured.

Here is ours. Take the eight corners of a cube and sort them into two groups by whether their
coordinates add up to an even number or an odd one. Each group of four spans a regular tetrahedron.
The two tetrahedra pass through each other and never share a single line.

Tile that, and the wedge shows up honestly — as gaps between the tetrahedra, each filled in its turn
by splitting into four more. Nothing is hidden and nothing is fudged; the near-miss is still there,
just carried by the structure instead of pretended away.

And the choice handed us something we did not pay for.

## Handedness, for free

The two families are mirror images of each other.

Look at what that means. Nobody added handedness to this object. Nobody wrote a rule that says left
and right behave differently. It is a consequence of sorting eight corners by odd and even — which
is to say, it is present in the object before a single number is stored on it.

That is the kind of thing worth watching for, and it is a good reason to build a world from the
smallest pieces you can rather than assembling it from features you want. You get told things. This
one keeps coming up later.

Now you have room. So: poke a dot in the middle of a great many, and watch.

## The pond

There is a ring.

A big number on one dot, and on the next tick it has moved to that dot's immediate neighbours, and on
the tick after that to theirs. There is now a front — a place the disturbance has reached — with
quiet ahead of it and settled water behind. Exactly the pond.

Nothing new was added to get this. The rule is the same sentence from the last chapter, unchanged:
each dot moves toward its neighbours by the differences on its lines. All that changed is that a dot
now has neighbours it is not directly joined to, and reaching them takes ticks. Distance in this
world is just how many lines you have to cross, and a ripple is what that looks like from outside.

Watch it a little longer, though, and it does something a pond in a field does not.

## It hits the edge

It reaches the outermost dots and comes back.

Of course it does. Our stack of tetrahedra stops somewhere, and the dots at the boundary have fewer
lines than the ones inside, so the rule does something different to them. The ripple bounces, the
reflection runs back inward, and it collides with the ripple still going out. What you are now
watching is not a ripple; it is a ripple plus an echo, and no measurement you make can cleanly tell
you which is which.

You could build a bigger box, but a bigger box has the same problem further away. What you want is a
world with no edge at all — and there is a cheap trick for that.

## Wrap it

Glue the far side to the near side.

Say a dot on the extreme right has no right-hand neighbour. Give it one: the dot on the extreme left.
Do that in every direction. Now no dot is on a boundary, because there is no boundary — every dot has
exactly the neighbours every other dot has.

You have seen this. It is the old arcade screen where a ship leaving the right edge reappears on the
left, unbothered, still flying. The screen is not infinite; it is finite and it has nowhere to fall
off. That shape has a name — a **torus** — and it is where this book lives from here on, for one
reason and one only: with no walls, nothing bounces, so the ring is only ever the ring.

Which means the question you have been unable to ask is finally available.

## The object, and the only question left

You can now ask the stopwatch question. Poke a dot, count the ticks, and see how far the front has
gone — and then do it again in a different direction and compare.

Take stock of what it took to get here, because the list is short and every item on it was forced.
Dots, because a number needs somewhere to sit. Lines, because change lives between. A triangle,
because it was the first thing that closed. A tetrahedron, because the triangle's rigidity is what
survives one dimension up. A clock and one rule, because nothing could happen. Many tetrahedra,
because one had no room. The odd-even sort, because tetrahedra will not stack. A wrap, because edges
echo.

That is the object. Everything from here is this one thing, asked a different question — and the
first question is whether the ring it makes is actually round.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-room-and-a-world-with-no-edge).*

**Next:** [Is it round?](the-round-ripple.md)—the dial gets set, twice, and one of the settings is
wrong in a way you can see.
