# The bubble and its bill

> **Scope.** The "bubble" here is a shaped region inside a **toy** computation, and its "energy" is a
> number a formula returns about that shape. Nothing here is a spacetime, a propulsion system, or a
> claim that any of this could be built. Negative in this chapter means *below a baseline*, not a
> supply of anything.

<figure class="chapter-illustration">
  <img src="assets/bubble-bill.svg" alt="A calm teal interior surrounded by a bright coral belt, with a small balance pointing at the boundary rather than at the middle.">
  <figcaption><strong>Analogy — not data.</strong> The interesting question about a shaped change is not how large the cost is but where it sits. The measured answer is in the figure linked below.</figcaption>
</figure>

Here is a question you can ask a world once it behaves evenly: what would it cost to move a piece of
it?

Not to move something *through* it. To take a region — a bubble — and shift it along, carrying
whatever is inside. Miguel Alcubierre wrote the version this project measures itself against in
1994, and the answer it gives is that the thing would cost you something strange. The energy
involved has to be negative, it has to sit in the bubble's *wall* rather than its middle, and it has
to form a ring around the bubble's waist rather than spreading evenly over the surface.

Three specific, awkward properties, and all three fall out of Alcubierre's own metric. The
interesting thing about them is that they are *predictions* about a situation nobody can build.
Which makes them an unusually good test of a toy: if we hand our little world a shaped push and read
off what our own formula says, do those three properties come back on their own?

We did not put them in. That is the whole point of asking.

## First, the control that should cost nothing

Before shaping anything, push the whole thing.

Take every point in the little world and shift it by the same amount, uniformly, in the same
direction. That is not a bubble; that is just moving the coordinate you are describing things in,
and it should be free. If our formula charges anything for it, the formula is measuring the
machinery rather than the physics, and every number after this is noise.

It charges exactly zero. Not nearly zero — the value the machine returns is zero, with nothing left
over.

That is the most boring result in this chapter and it is also the one that licenses the rest.
Because the uniform push is free, whatever we are charged next is being charged for the *shaping*,
and not for having a grid, a boundary, or a floating-point number.

## Now shape it

Make the push non-uniform: strong inside a region, fading to nothing outside it, with a transition
between the two. That transition is the wall.

Three things came back.

**All of it is negative.** Every single point where the formula returns anything at all returns a
value below the baseline — not most of them, not on average. That is the first of the three properties,
and nobody wrote it into the setup.

**All of it is at the wall.** The calm interior is nearly free, the far exterior is nearly free, and
the energy piles up in the transition. At the wall it is a few hundred times what sits in the quiet
middle and over a thousand times the far field. Whatever a shaped push costs, you pay it at the edge.

**It is a ring, not a shell.** Around the bubble's waist — the band perpendicular to the direction of
travel — the value is about six times what it is at the front and back, and it falls off smoothly
between the two. The nose and the tail are comparatively cheap.

**[Open the data-true energy figure](record/lab/warp-2-energy/0200-shaped-shift-energy/figures/energy_structure.html)**

Every one of those three was written down as a prediction, with a threshold, before the run.

## What "negative" is and is not

The number our formula returns splits cleanly into two competing parts. One of them cares about
whether the region is being stretched or compressed. The other cares about whether it is being
*sheared* — pulled unevenly, so that different directions are treated differently. In a shaped push
the shearing part wins, and the sign of the total follows from that.

So "negative" here is a statement about the geometry of a shape. It says: this configuration sits
below the reference value, and it does so because of how the shape twists rather than how it grows.
It is not a reservoir. There is no energy here to extract, store, or spend, because there is no
energy here at all — there is a lattice, a formula, and a number.

What is genuinely notable is narrower and, I think, more interesting: **we did not tell it any of
this.** We wrote down a purely geometric quantity, handed it a shaped push, and the three properties
Alcubierre derived for this problem came back out. Not approximately. On their own.

## And here is the barrier we walked into

There is a temptation at this point, and this project felt it. If a shaped push produces negative
values by itself, perhaps you could arrange ordinary fields to supply them and have the thing for
real.

You cannot. The energy in an ordinary classical field adds up to zero or more, everywhere, no matter
how you arrange the sources. You can move it around, concentrate it, cancel it at a point — and the
total never goes below the floor. A shaped push *asks* for something below the floor. Ordinary
fields cannot answer.

That barrier is not a gap in the toy. It is the shape of the actual problem, and running into it is
how you learn where it sits in your own machinery.

Which forces the next move, and it is not *only* a cleverer arrangement of fields. If the fields
cannot supply the sign, stop asking them — and ask instead whether the *other* half of the problem
is softer than it looks. Not what a push costs, but the resistance it is pushing against.

*The simulations behind this chapter: [the simulations](the-simulations.md#s-the-bubble-and-its-bill).*

**Next:** [The wall that worked, and didn't](the-wall-that-worked-and-didnt.md)—one experiment,
one yes and one no.
