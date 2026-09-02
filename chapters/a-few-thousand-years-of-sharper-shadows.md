# A few thousand years of sharper shadows

> **Scope.** This chapter is history, and it is told as history: real measurements of the real world,
> by people whose names we know. It contains no lattice, no simulation and no result of ours. What
> carries over into the rest of the book is the **method** — measure, state how well you can measure,
> and let a finer instrument overturn you — never the discoveries.

<figure class="chapter-illustration">
  <img src="assets/sharper-shadows.svg" alt="Three panels of the same triangulation: a wide angle that is easy to read and gives the right answer; a star's yearly shift too small to read, its two candidate lines lying on top of each other; and that very same shift separated at last by a finer instrument, seventeen centuries later.">
  <figcaption><strong>Analogy — not data.</strong> The same geometry three times over, and the middle and right panels are the same measurement. What changes between them is not the reasoning but how finely the angle can be read — which is the whole of this chapter.</figcaption>
</figure>

Eratosthenes did not stop at the Earth.

Having worked out the size of the thing he was standing on, the obvious next question is how far
away the Sun is. It was not a new question even then — it was older than his answer to the first
one — and nobody got it for another two thousand years. The reason is the most useful thing in
this chapter, so it is worth being precise about: **it was not for lack of the idea.**

## The gap between knowing how and being able

Aristarchus of Samos, working a generation or so earlier, had the method exactly right. At half
moon the Sun, the Moon and the Earth stand at a right angle — you can see the geometry in the
shape of the lit half. Measure the *other* angle, the one at the Earth between the Moon and the
Sun, and the shape of that triangle is fixed: two angles and the side between them are enough to
give you how much further away the Sun is than the Moon. That is triangulation, and it is the only
piece of geometry this chapter needs.

Aristarchus measured that angle at about 87 degrees, and concluded the Sun was around twenty times
further away than the Moon.

It is about four hundred times further.

Now look at where the error came from, because it is not where you would guess. The true angle is
about 89.85 degrees — that is, **nine minutes of arc short of a right angle**, less than a third
of the Sun's own width in the sky. Aristarchus read it as three degrees short. He was not sloppy:
nine minutes of arc is far below what anyone could read off an instrument made of wood and
sightlines, and the whole answer hangs on it. Push the angle a hair closer to 90 and the distance
runs off toward infinity; back it off a little and the Sun comes far too close. The calculation
amplifies a small angular error savagely — which is exactly the kind of thing you want to know
*before* you publish a number.

So: right method, wrong answer, and the fault is neither in the geometry nor in the man. **The
fault is in the resolution**, and the resolution is a property of the instrument rather than of
the idea.

That distinction — between being wrong and being unable to see yet — is the one this whole book
turns on.

## What the same method could reach

It is worth noticing how much *did* work with sticks and shadows and patience, because the point
is not that early measurement was feeble.

Within a century, Hipparchus of Nicaea used the Earth's own shadow — the round bite it takes out
of the Moon during an eclipse — to get the Moon's distance. That answer was very nearly right, and
it has stayed right. The difference from the Sun attempt is not cleverness; it is that the
geometry of that particular measurement does not sit on a knife edge. Nothing amplifies a small
angular error into a factor of twenty.

The same method, the same era, the same tools: one measurement lands, the other cannot. What
decides it is whether the quantity you want is *resolvable* with what you have.

## A failure that was read the wrong way round

About three centuries after Hipparchus the interesting question was not a measurement but what to
make of one that kept coming back empty.

If the Earth really moves around the Sun, a nearby star should shift slightly against the far ones
as we swing from one side of our orbit to the other — the way a near tree shifts against a distant
hill when you move your head. Nobody could see any such shift.

That nothing could mean one of two things. Either the Earth does not move — or the stars are so
far away that the shift is too small to see.

Both readings were available in antiquity. Aristarchus of Samos — the same man whose Sun had come
out twenty times too close — had proposed a moving Earth, and Archimedes records the enormous
sphere of fixed stars that came with it. Claudius Ptolemy's *Almagest*, around 150 CE, came down
the other way and argued that the Earth stands still. That reading held for well over a thousand
years.

This is the failure worth dwelling on, and it is not a failure of measurement. The observation was
fine and the null was real. What went wrong was the *interpretation of a null*. Treating "I cannot
see it" as "it is not there" — rather than "it is smaller than I can resolve, and here is how
small that is" — is an error available to anyone who does not state their resolution.

A null result is not an absence of information. It is a bound — and a bound is only meaningful if
you state how tight it is.

## The centuries, and what filled them

Then the long stretch, and this is where the shape of the story shows.

What changed over the next two thousand years was not the reasoning. Nobody improved on the
triangle. What arrived was instruments: a telescope, then better telescopes, then clocks good
enough to carry a time across an ocean.

And then the questions that had been unanswerable began falling, one after another, in the order
of how much precision they needed.

**That light takes time to travel** — Ole Rømer, 1676 — from the fact that Jupiter's moon Io kept
slipping out of schedule depending on where the Earth happened to be. Rømer put the slippage at
about twenty-two minutes across the width of our orbit; it is nearer seventeen. He gave the delay,
not a speed; Christiaan Huygens turned it into one, and because the delay was long the speed came
out about a quarter low — a real number, honestly out by a knowable amount, and out for a reason
you can point at.

**The distance to the Sun**, at last, in the 1760s — two thousand years after Aristarchus tried.
Not by measuring that impossible angle but by sidestepping it, in a scheme Edmond Halley had set
out decades before anyone could use it: watch Venus cross the face of the Sun from two places far
apart on the Earth, and time the crossings. Different vantage points, slightly different timings,
and the difference gives you the scale. It took telescopes, marine chronometers and expeditions —
James Cook to Tahiti in 1769, others to Siberia and northern Norway — to be in the right place on
the right day.

**The distance to a star** — Friedrich Bessel, 1838 — and with it the answer to that ancient null,
seventeen centuries late. The shift was there. For 61 Cygni, the star Bessel finally caught, it is
about a third of a second of arc — the width of a coin seen from fifteen kilometres away. The
stars had never been still. They had been outside the resolution.

**A ruler for what parallax could not reach** — Henrietta Swan Leavitt, 1912 — who noticed that a
certain kind of variable star pulses more slowly when it is intrinsically brighter. Turn a pattern
into a rule and you have a way to judge distance far past the reach of any triangle.

Each of those is the same move as the two posts. Each of them needed the resolution to catch up
first.

## The lesson, stated plainly

Here is the pattern, and it is the reason this chapter is in a book about a computer program.

- **The geometry was known from the start.** In the case of the Sun's distance, known for two thousand
years before anyone could execute it.
- **What changed was the resolution.** Not the ideas — the instruments.
- **Twice, a finer instrument overturned a published answer.** The Sun was not twenty times further
away. The stars were not fixed. Both of those had been in print, by careful people, reasoning
correctly from what they could see.
- **And that is not a scandal. It is the mechanism.** A field where finer measurement never overturns
anything is a field where nobody stated a number precisely enough to be caught.

The last point is the one worth carrying. Being overturned by better resolution is not the failure
mode of measurement; it is measurement working. The failure mode is the other thing — a claim
stated so loosely that no instrument could ever contradict it.

## Which is why the rest of this book keeps talking about how well it can see

We are about to build a small world and start measuring things in it. It is a toy, and nothing it
produces is a fact about nature. But the *method* in this chapter is not about nature either — it
is about how to hold a measurement honestly — and that part transfers exactly.

So watch for these three things in the chapters ahead, because they are the same three:

**A stated resolution.** Every experiment in this book says, before it runs, how well it expects
to be able to see. One of them writes down in advance that a particular quantity is beyond the
resolution it can afford, and predicts which way it will fail. It fails that way.

**A null read as a bound.** When something comes back "no", the chapters say how tight the no is.
A region could not be emptied. A wall did not change inertia. Those are bounds with numbers
attached, not shrugs.

**And once — this is the one to wait for — two published misses that turned out to be the project's own
bookkeeping rather than facts about the lattice.** They sat in the record as failures for a long time,
and then stopped being failures, without anyone re-running them.

When you reach that chapter, you will have met the move already. It is the star that was never
fixed.

*What this chapter cites — and what it does not: [the simulations](the-simulations.md#s-a-few-thousand-years-of-sharper-shadows).*

**Next:** [Build the object](build-the-object.md)—the fewest parts you need before anything can
happen at all.
