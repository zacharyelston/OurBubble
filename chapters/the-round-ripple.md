# Is it round?

> **Scope.** The ripple in this chapter is a pattern in a **toy** computation. *Light cone*, *speed*
> and *isotropy* name properties of that pattern and of fits to its output — not real light, not a
> measurement of the speed of anything, and not a claim about space.

<figure class="chapter-illustration">
  <img src="assets/round-ripple.svg" alt="A pulse spreads from one point as solid teal rings, with a dashed coral diamond overlaid to suggest the grid pulling the ring away from roundness.">
  <figcaption><strong>Analogy — not data.</strong> Solid is what was observed; dashed is what a badly chosen sense of size does to it. The measured difference is in the figure linked below.</figcaption>
</figure>

<!-- beat the-round-ripple.1 -->

You have the object and you have the question: poke it, and see whether the front travels at the
same speed in every direction.

Speed is a distance divided by a time. Look at what you are actually holding, and one of those two
is in your hand and the other is not.

Which half is missing?

## The half you do not have

<!-- beat the-round-ripple.1 -->

Time you have. Ticks, all the same size, and you can count them — that is what the clock was for.

Distance you do not have. Not because it is hard to measure, but because nothing in the object has
ever been given a length. The dial exists; you met it on one tetrahedron, six lines and six
settings, and you have already turned one of them and watched the rhythm change. But nobody has
ever set it from anything real. It has been a knob with no reading on it.

So before the world can be asked how fast, somebody has to say how far.

Doesn't counting steps already do that?

## A step is not a distance

<!-- beat the-round-ripple.2 -->

It is worth sitting with why not, because "count the lines you crossed" sounds exactly like a ruler.

Go back to how the object was built: the eight corners of a cube, sorted odd and even. Some of the
lines in the finished thing run along the edges of those cubes. Others cut across their diagonals.
And a diagonal is longer than an edge — you can see that on the cube in front of you.

But to the *counting*, both are one line. One step along an edge and one step across a diagonal are
both "one step". So a front that has crossed four lines might have gone four edges or four
diagonals, and those are not the same distance, and nothing has told the object which.

That is the dial's whole job: to say what each line is worth. Which means the answer to *is it
round* depends on a setting, and the setting has not been chosen yet.

So choose the obvious one, and guess what happens.

## ✎ Before we look

<!-- beat the-round-ripple.3 -->

The obvious setting is to give every line the same weight. It feels like the neutral choice — the
one that assumes nothing, that plays no favourites among the lines.

**Write your guess down now** — and the useful half is not whether it comes out round. You have just
been told an edge and a diagonal differ in length and the counting cannot tell, so *not round* is
the easy call.

The live question is **which way**: along the cube's edges, or across its diagonals? One line is
enough. Commit to a direction.

This is the ritual for the rest of the book, and it is not a teaching trick. Once you have read a
number it is very hard to remember not having known it.

## The obvious setting

<!-- beat the-round-ripple.4 -->

Set every line to the same weight and the ring comes out **lopsided**.

It runs faster across the cube's diagonals than along its edges — so if you guessed the diagonals,
you were right, and for the reason the last section gave: the counting treats a long step and a
short one alike, so the long one covers more ground per tick. What ought to be a circle is stretched
along the diagonals, and anything you aimed in this world would drift.

Notice what happened. Weighting all the lines equally *looked* like assuming nothing; it was a
strong assumption, quietly made — that an edge and a diagonal are the same length. The object never
said that. We did, by choosing the setting that felt neutral.

The number is what makes this more than a story, so here it is. Send a pulse from the middle, time
its arrival along an edge direction, time its arrival along a diagonal, and compare the two speeds.
If the ring were round they would be equal. They differ by **22.4%**.

What if the dial is set from the shape instead?

## The same dial, set from the geometry

<!-- beat the-round-ripple.5 -->

Measure the pieces of the object and weight each line by what it actually is. Same dial, same
settings, no new machinery — a reading taken from the thing rather than assumed.

The two speeds now differ by **2.2%**: about ten times less.

Both predictions were written down before either run — that the naive setting would be *obviously*
uneven, and that the geometric one would at least halve it. That matters more than the numbers do,
and it is the step people skip.

**[Open the data-true isotropy figure](record/lab/warp-1-move/0115-lattice-matched-isotropy/figures/isotropy.html)**
— the two rings side by side, dots measured, a dashed circle for reference.

But 2.2% is not zero. What is it?

## Coarse, or broken?

<!-- beat the-round-ripple.6 -->

A sceptic should push on the residual, and there are exactly two things it could be: the world
really is slightly uneven, or the grid is too coarse to draw a smooth circle on.

Those sound like the same complaint. They are not, and telling them apart needs no judgement.

A coarse grid gets *better* as you use bigger, gentler ripples: a long, lazy wave stops noticing the
graininess underneath it, the way a wide boat stops noticing small chop. A genuine unevenness does
nothing of the kind — it is there at every scale, because it is a property of the geometry rather
than of the resolution.

So the test writes itself. Make the ripples gentler and see whether the disagreement shrinks. Could
a machine run that test without anyone's thumb on the scale?

## Hand it to something that cannot hope

<!-- beat the-round-ripple.7 -->

It can, and this is where the book acquires the instrument it uses for the rest of its length.

Run the sweep again in five directions at once and hand the timings to a blind fitter: a program
told nothing about what it is looking at — not the expected law, not which arm was which. It picks
from a menu written down beforehand and reports how far ahead of the runner-up it finished.

It picked the straight-line law in all five directions, and by a wide margin: its score beat the
runner-up — a square-root law — by about a quarter every time, which for a fit quality is a rout.
The speed it returned agrees across directions to within a couple of percent, and that spread
*shrinks* as the ripples get gentler. Which is the signature of a coarse grid.

**[Open the data-true fit figure](record/lab/warp-1-move/0117-dispersion-isotropy/figures/discovery.html)**
— the chosen law, the runner-up, and the gap between them, per direction.

Then the same pipeline, unchanged, on the naive setting. The spread there is **33.2%**, and it does
not shrink. Coarse and broken, told apart, by something with no opinion.

Could a picture be lopsided because of the instrument itself?

## An interlude: the shadow of the mesh

<!-- beat the-round-ripple.8 -->

It could, and it was — on a page of ours anyone could open. A detour, then, before the chapter
closes, because it is the child in the yard with the stick turned around on us.

There is a public demonstration page: a ripple through two gaps, making bands on the far side. It
ran that way for months. The scene is mirror-symmetric by construction — two identical gaps, one
centred source, nothing in it that prefers a side — so the halves of the picture should have
matched. One came out **3.8×** brighter than the other.

That is a mark, in the sense her two scratches in the dirt were marks: a number nobody chose, that
the thing itself put there. And like hers it is mute. Two readings fit it equally well. Either what
the ripple does at the gaps really is lopsided, or the thing doing the measuring is, and the picture
is faithfully reporting the shape of what it travelled on rather than the shape of the question.

Which one? The readings differ, so a test can tell them apart.

## Mirror the mesh

<!-- beat the-round-ripple.8 -->

Cutting a square into triangles means choosing which way the diagonals lean. Lean them all the same
way, then flip the scene about the axis through the source and between the gaps: the scene lands on
itself and the mesh does not. So the mesh is the suspect: it had been asserting a left-right
difference nothing in the question asserted.

Note what this is *not*: not the object's own three-way grain, whose symmetry carries each kind of
place onto the others. This was a drawing choice in one demo that broke a mirror the experiment
needed.

The correction is as small as the suspicion: alternate the diagonals, so mirroring the mesh lands on
itself. Same scene, same solver, nothing else touched. The two halves now disagree by **5×10⁻¹⁵** of
themselves — numerical noise. Suspect confirmed, by a run and not a story.

**[Open the data-true mesh-repair figure](record/lab/warp-3-shield/0305-doubleslit-mirror/figures/doubleslit_mirror.html)**
— the same scene on both meshes, measured, side by side.

The switch between the two meshes was left in [the demo page](record/viz/doubleslit.html) rather
than quietly removed. Which is why roundness and mirrors get tested before later results are read.

So what did the chapter settle?

## What this chapter settled

<!-- beat the-round-ripple.9 -->

Not that the little world has light in it. It does not.

Two things, and everything after this depends on both.
**One setting decides whether the world behaves the same way in every direction** — and that setting
is a choice somebody makes, not a fact the object hands over. And
**we can tell a coarse grid from a broken geometry**, by whether the disagreement shrinks when the
ripples get gentler.

Go and look at your guess now. Whichever way it went, you know something about the dial that you
could not have known by being told.

Which is what calibrating an instrument means: not a world with nothing left in it, but one whose
remaining unevenness has been measured, and whose symmetries have been checked rather than assumed.
This one steers true enough to measure with — so measure with it.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-the-round-ripple).*

**Next:** [What does pushing on it cost?](the-bubble-and-its-bill.md)—move a piece of the world,
contents and all, and read the bill.
