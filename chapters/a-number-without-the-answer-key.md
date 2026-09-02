# A number without the answer key

> **Scope.** *Ising model*, *critical point* and *universality* name lattice models and the
> dimensionless properties they share with some measured systems. This is a **toy**; agreement with a
> universality class says nothing about spacetime.

<figure class="chapter-illustration">
  <img src="assets/blind-class-and-its-miss.svg" alt="Two panels. On the left, measured markers sit on a dashed line that marks an answer already known. On the right the dashed line is gone, the markers still form the same trend, and one marker sits outside a band that was drawn before the measurement was taken.">
  <figcaption><strong>Analogy — not data.</strong> An instrument earns trust on a case whose answer is known, then works where no answer exists — and keeps the one shortfall it said in advance it would have. The numbers are in the figures linked below.</figcaption>
</figure>

There is a way to make a toy look profound, and this project used to do it.

You take a famous constant of nature. You build formulas out of whatever your model happens to contain
— counts of faces, powers of π, small integers — and you keep going until one of them lands close. Then
you write it up.

It always works, and it never means anything, because a target you already know the value of will
attract formulas indefinitely. Closeness is not evidence when you were free to keep searching.

So: what would count instead?

## The shape of an honest version

You need a number the method was not built to know, with no dial available to tune it toward the
answer — and, crucially, you need to be unable to check it until after you have committed.

Critical points hand you exactly that.

When a magnet is on the verge of losing its magnetism, or a fluid is approaching the ridge where
liquid and gas stop being different things, something strange happens: the microscopic details stop
mattering. Systems made of completely different stuff — different atoms, different forces, different
everything — start behaving identically in the ways that count. The numbers describing *how* they
behave near that edge come out the same.

That is called universality, and it is one of the better facts in physics.

For a toy it is a gift, because it means our little world does not have to pretend to be a real
magnet. It only has to belong to the same class. And which class a thing belongs to is decided by a
handful of dimensionless numbers that can be measured — by us, and independently, in a laboratory, on
actual matter.

## First, make the instrument earn it

Before pointing an instrument at something unknown, point it at something known and see whether it
lies.

So the first run used a two-dimensional case that has an exact solution — Lars Onsager's, from 1944,
one of the results that made universality believable in the first place. The answers are known
precisely, and they were not given to the machinery. The pipeline saw finite-size data and nothing
else, and had to produce the class numbers itself.

It got them, to six and seven digits.

That is not a discovery. It is a calibration. An instrument that cannot recover a known answer has no
business reporting an unknown one.

**[Open the data-true universality figure](record/lab/warp-5-universality/0500-ising-universality/figures/universality.html)**

## Then take the answer key away

The three-dimensional version of the same model has no closed-form solution. Nobody has one. It is not
that it is hard to look up — it does not exist.

The pipeline ran there unchanged. It reproduced the solved two-dimensional numbers first, as a
built-in check, and then went to three dimensions and reported what it found.

It came back with two exponents that agree with the values measured *in real matter* — at the liquid–gas
critical point, and in uniaxial magnets — to within a few percent. Nobody fitted those targets. There
was no parameter in which they could have entered.

Not a formula that lands
near a famous number, but a computation that produces a number nobody supplied and then agrees with
measurement.

There is a dependency here, and it belongs in the same breath. This stage was handed two ingredients
rather than measuring them: the temperature at which the transition happens, and one of the class
numbers itself. So the agreement is real, and it rests on two things it was given.

## Then take the ingredients away too

A later run removed them. It located the critical point from crossings in its own data, and measured
the rest from scratch — the full blind version, with nothing supplied but the model.

It found the critical temperature to within about four parts in ten thousand of the published value.

And it missed one quantity, in exactly the direction it had said it would.

That last sentence is the one worth slowing down for. Before the run, the team wrote down that this
particular quantity was the one the affordable lattice sizes could not pin down, and that its estimate
would come out *too high*. It came out too high — a prediction the experiment made about its own
limits, and then met.

An experiment that announces its own ceiling in advance is doing something different from one that
explains a shortfall afterwards.

## The part where the mistake was ours

There is one more lesson in this chapter and it is the least comfortable.

Two other measurements in the same body of work had been recorded as negatives: quantities that came
out outside their registered bands. They sat in the record as failures for a long time.

Then the two were re-analysed, and both misses turned out to come from the same thing — and it was not
the little world. It was us. The location of the critical point carries its own uncertainty, and that
uncertainty had not been propagated through into the quantities that depend on it. Once it was, both
"failures" fell inside their bands.

**This is the same move as the star that was never fixed.** Ptolemy looked with the instrument he had,
recorded honestly that there was nothing to see, and the record stood for seventeen centuries — until
Bessel's finer instrument found the shift had been there all along. The difference here, and it is the whole difference, is that
the uncertainty which dissolved these two misses had *already been published*. It was sitting in the
record, correct, and simply never carried through into the numbers that depended on it. Nobody needed
a better telescope. They needed to propagate a number they already had.

The original rows are still in the record. They were not deleted and rewritten; they carry a note
saying what later work found, so the original miss is still there to read.

So the method has now shown four things, and the fourth is the rarest: it can recover a known answer,
work where no answer exists, state its own limits in advance and hit them — and find that a failure it
had published was its own measuring error rather than a fact about the world.

One ability is still missing, and it is the one that decides whether any of the above counts.

It has to be able to tell us we were wrong.

*The simulations behind this chapter: [the simulations](the-simulations.md#s-a-number-without-the-answer-key).*

**Next:** [When the expected law fails](when-the-expected-law-fails.md)—the obvious answer, refused.
