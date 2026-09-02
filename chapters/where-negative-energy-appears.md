# Can a gap be emptier than empty?

> **Scope.** A **toy** computation of a Casimir-like effect. The negative value is a difference between
> two baselines inside that computation — not a reservoir of usable energy, and not evidence that
> anything can be built. *Vacuum* here names the lowest state of a discrete model.

<figure class="chapter-illustration">
  <img src="assets/vacuum-boundaries.svg" alt="Many wave shapes fill the space around two gold plates, while only a few fit in the gap between them, and a baseline marker between the plates sits lower than the one outside.">
  <figcaption><strong>Analogy — not data.</strong> Fewer shapes fit inside than outside, so the baseline between the plates differs from the baseline beyond them. What the difference actually measures is in the figure linked below.</figcaption>
</figure>

<!-- beat 69 -->

Three noes now, all at the same barrier. A shaped push wants something below the floor. Ordinary
fields cannot go below the floor. Walling a region off does not change what resistance is, and aimed
fields cannot empty a volume.

So the honest question is no longer *how do we get the sign* but: does established physics put a
real negative difference anywhere at all?

It does, and the place is a surprise. It is not in the fields. It is in what is left when you take
the fields away — an effect Hendrik Casimir worked out in 1948, and which has since been measured in
the laboratory.

What is left when you take the fields away, though? Isn't that nothing?

## What "empty" contains

<!-- beat 70 -->

Not nothing. This is the one piece of quantum theory the book needs, and it is one sentence long.

A field does not sit perfectly still, even in its lowest state. Every shape it could possibly
vibrate in carries a little irreducible activity — not because anything excited it, but because
perfect stillness is not among the options. Add up that little bit over every available shape and
you have the baseline of empty space.

So "empty" is not featureless. It is a very long list of possible vibrations, each contributing a
trace, and the total is a number.

Which means the list can be interfered with. Put two walls close together, and ask what stops
fitting.

## The long shapes stop fitting

<!-- beat 71 -->

The long ones.

A vibration whose natural length is wider than the gap simply cannot exist in there — the same
reason a long note cannot exist on a short guitar string. Between the walls, the set of available
shapes is smaller than the set available outside them. Some possibilities have been removed, and
removed is the operative word: nothing was added anywhere.

So there are now two baselines, one inside the gap and one outside it, computed from two different
lists.

Which is lower, and why?

## Inside, because we took things away

<!-- beat 72 -->

Inside. And you can get there without any calculation at all.

The baseline is a sum of contributions, every one of them a little bit of something rather than a
little bit of nothing. The inside list is the outside list with entries missing. A sum over fewer
positive contributions is smaller. So the inside sits below the outside.

That is the whole mechanism, and it is worth noticing how little it needs. No exotic material, no
new law, no energy from anywhere. Just boundaries, and the ordinary fact that boundaries exclude
possibilities.

Now: we can build that in the little world. Before we do, commit to something.

## ✎ Before we look

<!-- beat 73 -->

**Write down your guess.** As the two walls are brought closer together, does the difference between
inside and outside grow, or shrink?

There is a real argument each way and it is worth feeling both. Closer walls exclude more shapes, so
perhaps the difference deepens. But a narrower gap holds less of everything, so perhaps there is
less of a difference to have. Pick one, and note in half a sentence which way you think it goes.

And a second guess, because the chapter turns on it: if the difference deepens as the gap narrows,
what does that mean the walls will *do*?

## What the little world did

<!-- beat 74 -->

We built the one-dimensional version. Two walls in the lattice, the allowed vibration shapes
computed directly from the object's own operator, the common bulk contribution subtracted off, and
then the question: what is left?

Every measured value sits below the free-space line. And as the walls move closer, it goes further
down.

Which answers the second guess, and this is the part worth pausing on. A quantity that drops as a
gap narrows is a quantity that would rather the gap were narrower — so the walls are pulled
together. The attraction is not an extra ingredient. It is the same fact, read as a tendency instead
of as a number.

That is the sign three attempts had been unable to reach, appearing on its own.

## A sign is easy

<!-- beat 75 -->

Which is exactly why a sign is not enough, and this is the sceptical beat of the chapter.

Half the ways of getting this calculation wrong hand you a negative number. If all we had was "it
came out below the line", we would have almost no evidence that we had reproduced Casimir's effect
rather than made a sign error with good taste.

What would settle it is the *shape* of the answer. Casimir's calculation gives a law for how the
effect scales with the gap, and that law comes with a specific coefficient — a coefficient with a π
in it. Reproduce the scaling *and* land on the coefficient, and you are no longer looking at a sign.
You are looking at the phenomenon.

Neither of those can be guessed. So: did the machine find them without being told?

## What came back

<!-- beat 76 -->

It did.

We swept the gap over a range of separations and handed the results to the same blind fitter from
[is it round?](the-round-ripple.md) — told nothing about what it was looking at, picking from a menu
written down beforehand.

It came back with the scaling law: the exponent it found was **−0.9997** against a true value of −1,
with a fit quality of six nines. It separated out the contribution from the two wall edges and got
essentially exactly the right value for that too. And it returned a coefficient of **−0.13099**
where the exact answer is **−π/24 = −0.13090** — a match to **0.07%**.

Nobody typed π into the fitter. Nobody typed the exponent in. It was not told what to look for.

**[Open the data-true Casimir figure](record/lab/warp-4-vacuum/0400-casimir-negative-energy/figures/casimir.html)**

## Two things it is not

<!-- beat 76 -->

Two things this is not, and both matter. **It is not a power source** — the negative number is a
difference between two baselines, there is nothing to draw on, and arranging boundaries costs more
than the difference is worth. **It does not rescue the shaped push** — that wants a particular
amount of the sign, in a particular place, at a particular scale, and what we have is the sign in a
tiny gap at a magnitude set by the gap. The distance between those is enormous and this chapter does
not shrink it by a step. It establishes only that the sign is not forbidden, which is a much smaller
thing than a solution.

Something else changed in this chapter, though, and it is quieter than the physics.

## What quietly changed

<!-- beat 77 -->

Up to now, a person set up each experiment, ran it, and read off the answer.

Here the *machine* swept a parameter, fitted the results, chose between candidate laws, and reported
a coefficient — and a person only checked its working afterwards. Read the two paragraphs above
again with that in mind: the exponent and the coefficient were not confirmed by us, they were
*found*, by something that could not have wanted them.

That is a different kind of instrument, and it changes what the next question can be. Once you have
something that can find a law it was not told, you can point it at a place where nobody knows the
answer and see what it says.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-where-negative-energy-appears).*

**Next:** [Can it tell me something I didn't tell it?](a-number-without-the-answer-key.md)—the
difference between a number you looked up and a number you earned.