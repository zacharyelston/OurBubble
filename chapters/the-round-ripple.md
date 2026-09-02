# The round ripple

> **Scope.** The ripple in this chapter is a pattern in a **toy** computation. *Light cone*, *speed*
> and *isotropy* name properties of that pattern and of fits to its output — not real light, not a
> measurement of the speed of anything, and not a claim about space.

<figure class="chapter-illustration">
  <img src="assets/round-ripple.svg" alt="A pulse spreads from one point as solid teal rings, with a dashed coral diamond overlaid to suggest the grid pulling the ring away from roundness.">
  <figcaption><strong>Analogy — not data.</strong> Solid is what was observed; dashed is what a badly chosen sense of size does to it. The measured difference is in the figure linked below.</figcaption>
</figure>

Drop a stone in a pond and the ripple goes out as a circle. It does not matter which way you face.
That evenness is so ordinary that it takes an effort to see it as a fact about the world rather than a
property of ponds.

The last chapter left us needing it. We had a ring spreading through the little world and no way to
ask how fast it was going, because nothing in the object knew how long a line was. Size had to be put
in by hand, through exactly one place.

This chapter is about that one place, and about what happens when you get it wrong.

## The dial

There is a single component whose entire job is to say how big things are — how much each line counts
for, how much each small patch of surface counts for. Set it, and the object has a geometry. Set it
differently, and the object has a *different* geometry.

It is a dial, and it is the only dial.

The obvious setting is to give every line the same weight. It feels like the neutral choice, the one
that assumes nothing — and it is in fact a strong assumption, because the lines in this object are not
alike. Some run along the edges of the underlying cubes and some cut across their diagonals, and a
diagonal is longer. Weighting them equally is a claim that they are the same length, quietly made.

Set the dial that way and the ring comes out **lopsided**. It runs faster along some directions than
others. What ought to be a circle is a squashed thing, and if you tried to aim anything in this world,
it would drift.

Set the dial from the actual geometry of the object instead — measure the pieces and weight them by
what they are — and the ring comes back round.

## What round is worth measuring against

That is a satisfying story and it would be worthless without a number, because "rounder" is exactly
the kind of judgement that a person hoping for a result will make on a picture.

So we measured it: send a pulse out from the middle, time its arrival along an edge direction, time
its arrival along a diagonal, and compare the two speeds. If the ring were perfectly round they would
be equal.

With every line weighted the same, the two speeds differ by **22.4%**. With the dial set from the
geometry, they differ by **2.2%** — about ten times less. Both predictions were written down before
the run: that the naive setting would be *obviously* uneven, and that the geometric one would at least
halve it.

**[Open the data-true isotropy figure](../.record/lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html)** —
the two rings side by side, dots measured, a dashed circle for reference.

## Making the claim harder to fake

A single comparison along two directions is thin, and the residual 2.2% is a number a sceptic should
push on. Is that the object still being slightly uneven, or is it just a coarse grid?

There is a clean way to tell them apart, and it does not require trusting anyone's eye. A coarse grid
gets better as you use bigger, gentler ripples — the wavelength stops noticing the graininess. A
genuine unevenness does not; it is there at every scale.

So we ran the sweep again, in five directions at once, and handed the results to a fitting program
that was told nothing about what it was looking at — not the expected law, not which arm was which. It
had to pick a law from a fixed menu written down beforehand and report how far ahead of the runner-up
its choice finished.

It picked the straight-line law, in all five directions, and returned a speed that agrees across
directions to within a couple of percent — a spread that *shrinks* as the ripples get gentler, which
is the signature of a coarse grid rather than a defect.

Then the same pipeline, unchanged, on the naive setting. The spread there is **33.2%** — and it does
not shrink. That is the difference between a grid that is merely coarse and a geometry that is wrong.

The control is what makes the first answer worth anything. A test that only ever agrees with you has
measured nothing.

## The part where we were the problem

Now the uncomfortable one, and it belongs here rather than in a footnote.

This project has a public demonstration page: a ripple going through two gaps, making the fringes you
would expect. It ran for months. It was quietly, visibly wrong — about **3.8×** brighter on one side
of the screen than the other.

It looked like optics. Nobody had built any asymmetry into the scene; the two gaps were identical and
the source was centred. If you wanted to read something profound into it, the material was there.

It was the grid. When you cut a square region into triangles, you have to choose which way the
diagonals lean, and if they all lean the same way, the mesh itself has a handedness — a left and a
right that are not mirror images. The ripple was faithfully reporting the shape of the thing it was
travelling on.

The fix is embarrassing in its simplicity: alternate the diagonals, so that mirroring the mesh maps it
onto itself. Same scene, same solver, same everything else. The asymmetry drops to the level where the
computer's own arithmetic runs out — about fifteen decimal places down, which is another way of saying
*exactly*, as far as the machine can tell.

**[Open the data-true mesh-repair figure](../.record/lab/warp-3-shield/0305-doubleslit-mirror/figures/doubleslit_mirror.html)** ·
**[open the demo and turn it on and off yourself](../.record/viz/doubleslit.html)**

That last link is the one worth clicking. The demo carries a switch between the two meshes, so you can
watch a real defect in this project's own published work appear and disappear. A lattice can be wrong.
The honest thing is to show you where, and to leave the switch in.

## What this chapter actually established

Not that the little world has light in it. It does not.

What it established is that **one setting inside the machine controls whether the world behaves the
same way in every direction**, that the effect is large enough to see and large enough to measure,
that we can tell a coarse grid from a broken geometry by whether the error shrinks, and that when we
got it wrong in public the same reasoning found it.

Everything after this depends on that. A world that steers untrue is a world where no measurement
means what it appears to mean.

*The simulations behind this chapter: [the simulations](the-simulations.md#s-the-round-ripple).*

**Next:** [The bubble and its bill](the-bubble-and-its-bill.md)—now that the world behaves evenly,
we push a region of it around and ask what that costs.
