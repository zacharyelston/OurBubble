# Cast your own shadow

> **Scope.** The checks below inspect a computational-physics **toy** and the repository that holds
> its record. A reproducible toy result is still a toy result: reproducibility is evidence about what
> the code did, not about anything outside the firewall.

<figure class="chapter-illustration">
  <img src="assets/walk-the-trail.svg" alt="Four stops joined by a path — the registered question, the figure drawn from the run, the recorded verdict, the project ledger — with a reader walking it, and the page you are reading drawn faintly off to one side, off the path.">
  <figcaption><strong>Analogy — not data.</strong> Every stop on that walk is a file in the repository. This page is not one of them — the trail runs through the record rather than through the book.</figcaption>
</figure>

<!-- beat cast-your-own-shadow.1 -->

So what did we actually do? One sentence, and it should be the honest one rather than the warm one.

We did not measure the universe. We inspected one object we had built, and we watched its measuring
tools do seven things: recover laws that were already known, tell controls apart from results,
produce a number nobody supplied, state a limit in advance and then hit it, keep the negatives in
the record at full size, find that two published failures had been our own analysis rather than the
world — and refuse a law we proposed ourselves.

That is a smaller claim than a theory of everything, and considerably more useful, because it is the
kind of claim that could have come out false — and you can go and check whether it did.

Which raises the only question left in the book: can you check it without taking anyone's word,
including mine?

## Follow one result without running anything

<!-- beat cast-your-own-shadow.2 -->

Take the refusal from the last chapter — the exponent that came out a little over half the expected
steepness. Four files, ten minutes, no build required.

1. **Read the question before you know the answer.** Open that experiment's
   [`spec.md`](record/lab/dna-thz/0001-dna-permittivity-shift-law/spec.md). Find the expected
   exponent and the band that was going to decide it. Notice the date on it.
2. **Look at the data.** Open the
   [data-true figure](record/lab/dna-thz/0001-dna-permittivity-shift-law/figures/shift_law.html) and
   compare the measured line against the rejected square root. The picture is drawn from the run's own
   output; there is no illustration in it.
3. **Read the verdict.** Open
   [`eval.md`](record/lab/dna-thz/0001-dna-permittivity-shift-law/eval.md) and check whether the
   negative appears in the conclusion — or whether it has been softened into a partial success on the
   way to the summary.
4. **Check the summary tells the same story.** Find the same result in
   [`PREDICTIONS.md`](record/PREDICTIONS.md). The public page, the chapter you just read, and the
   project's own ledger should agree. If they do not, the chapter is the thing that is wrong.

That walk tests something narrow and important: that the order was question, then data, then
verdict, then summary — and not the other order, which is how most disappointing results become
encouraging ones.

## What travels with the book

<!-- beat cast-your-own-shadow.3 -->

The chapters you have read carry no experiment numbers and no quotations. That was a choice, and the
provenance did not go missing — it moved to the appendix.

And it travels with the book. Clone it — `github.com/zacharyelston/OurBubble` — and everything the
book quotes is already in `record/`: the registered questions, the verdicts, the tests, the figures,
copied out of the engine at the one commit `record.lock` names. Nothing here needs access to
anything but the clone you just made. Then, from its root:

```sh
python3 check_edition.py
mdbook build
python3 check_edition.py --rendered
```

The first is the book reading itself against that record; the second rebuilds it, which regenerates
the appendix, so if the record has moved the page changes under you and `git status` says so; the
third re-reads the built pages and follows every link in them. None of it computes any physics. It
checks that the story and the record still say the same thing.

What exactly each one promises is written down in the appendix rather than here, because the useful
question at this point is the other one.

## And exactly which sentences no program has read

<!-- beat cast-your-own-shadow.3 -->

A fair amount of this book. It is worth knowing which.

**Checked, verbatim:** every figure the appendix lists with a file beside it, and every number a
chapter sets in digits and puts in bold — that one has to be declared in its own appendix section,
so a number cannot be emphasised into your eye without a counterpart in the record. The retired
claims are checked too: if any of them reappear, in any wording the guard recognises, the book is
refused, and the guard is itself tested against sentences it must refuse.

**Not checked:** the prose, including some of the appendix. When a chapter says the energy at the
wall is a few hundred times what sits in the calm middle, or a signal arrives about half a million
times weaker, no program has read that sentence. Those are numbers we wrote, from runs whose figures
are linked and whose experiments the appendix names.

**Checkable, but not against us:** the history chapter. No file is named beside the 89.85 degrees or
the third of a second of arc, because none of it is ours — those you can check against the world
instead, which is a better guarantee than any program here can give.

## The check that would actually catch us

<!-- beat cast-your-own-shadow.4 -->

The commands above verify bookkeeping. Here is the one that verifies the science, and it is the
reason this project can make the claims it does.

Pick a result. Re-run its test — the real one, at full size, and let it
**overwrite the committed data this book quotes**. Then ask git whether anything changed.

Nothing should change. If any number in these chapters had been nudged after the fact, tuned to
taste, or typed in by hand, that is where it appears.

Every appendix section with a result of its own carries the command that re-runs it — the early
chapters and the history chapter have none, because they have no run. Start with one whose runtime
suits your machine, and read what the section says before you run anything.

## ✎ Before you press Return

<!-- beat cast-your-own-shadow.5 -->

**Write down what you expect.**

Not "it should pass" — that is not a prediction, it is a hope. Write the thing that would tell you
something: whether `git status` comes back empty, and if it does not, which file you expect to have
moved and why. Then press Return.

You have now done, on your own machine, the thing this whole book has been about. Somebody wrote
down what should happen before they looked. That somebody is you.

If the regenerated files do differ, do not explain it away. Stop and find it. A changed seed, a
changed dependency, a changed tolerance, a changed piece of machinery: each of those is part of the
result's history and worth more than the result.

## What we carry out of the bubble

<!-- beat cast-your-own-shadow.6 -->

The shadow was never proof of a sphere. It was an invitation to build a test.

The ripple was not light. It exposed a directional bias, and the one setting that shrank it tenfold.
The shaped push was not a drive; it located a sign and the classical obstruction standing in front
of it. The wall genuinely isolated and genuinely did not make what was inside easier to push. The
attempt to empty a volume failed. The vacuum recovered a known law without being told it.
Universality gave up its answer key and kept its limits. The lump in the cavity refused the easy
exponent.

## What it adds up to

<!-- beat cast-your-own-shadow.6 -->

Put together, those do not add up to a discovery. They add up to a method:

1. Notice something you cannot explain.
2. Propose the smallest structure that would explain it.
3. Say, in advance, what would prove the proposal wrong.
4. Check — and keep the answer, especially when it is no.

The Container is the object we examined — named back where you finished building it. The bubble is
the patch of it we pushed on, and measured, and handed back. Neither of them asks for belief, and
this book has tried hard not to either.

So: where is the next shadow?

There is one wherever something changes and nobody has written down what it would take to be
surprised. It does not have to be a lattice. It has to be small enough to hold in your head, and
specific enough to be wrong.

Find it. Then write down what would prove you wrong — before you look.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-cast-your-own-shadow).*