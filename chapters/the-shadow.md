# The shadow

> **Scope.** This is a book about a **toy**: a small world built inside a computer, and what happened
> when we pointed real tests at it. Nothing here is a claim about nature. Where a chapter uses a word
> like *vacuum* or *light cone*, the word names a pattern in the model.

<figure class="chapter-illustration">
  <img src="assets/shadow-question.svg" alt="A child and a small post cast long shadows across a curved field toward a glowing question mark: a visible shadow standing in for the unseen thing that cast it.">
  <figcaption><strong>Analogy — not data.</strong> A shadow is not evidence of its source — it is an invitation to build a test. That move, not the shadow, is what this book is about.</figcaption>
</figure>

A child notices that her shadow is short at noon and long in the evening.

It is worth stopping on that, because it is the move the rest of this book keeps making, and it is
smaller than it looks. She has noticed that something changed. She could leave it there, and most of
us do. Or she could do one more ordinary thing: push a stick into the ground, scratch a mark where
the shadow ends, and come back in an hour to scratch another.

Now there are two marks. The gap between them is a number, and the number came from the world rather
than from her. That is a measurement. It does not need an instrument or a talent — only something
that changes, and the decision to write down by how much.

The two marks do not tell her what they mean. A measurement on its own is a number with a time
attached, and nothing more. What happens next is a separate question, and a harder one.

## What Eratosthenes did next

Around 240 BCE a man in Alexandria did the next thing, starting from almost exactly this.

Eratosthenes of Cyrene was the chief librarian there — he ran the largest collection of books in the
world, and he had the job because he was already eminent. A mathematician, a geographer, a poet.
Nobody was waiting on him to prove himself. That is part of why it makes a good first example: you
would not have needed to be him. The measurement takes no new mathematics, and the arithmetic at the
end of it is one multiplication.

What he had was a story about a well. At Syene, far to the south, at noon on the longest day of the
year, sunlight was said to fall straight down a deep well and light the water at the bottom.
Straight down. An upright post standing beside that well threw no shadow at all.

In Alexandria, on the same day and at the same hour, an upright post *did* throw a shadow. A short
one, but a real one.

Two upright posts. Same day, same hour, same Sun. One casts a shadow; the other does not.

On a flat world that cannot happen. Upright posts on a flat world, lit by a far-off Sun, all lean
their shadows the same way by the same amount — so if one of them has no shadow, none of them do.
The ground between the two towns is therefore not flat. It curves.

Then comes the step that turns an observation into a measurement: he asked *how much* it curves. He
measured the angle of the Alexandria shadow, and it came out at about a fiftieth of a full turn.
That angle is doing all the work, because it is also the angle between the two towns seen from the
centre of the Earth. If a fiftieth of the circle separates them, the circle is fifty times the
distance between them.

He still needed that distance, and here the story is more ordinary than people expect. He did not
work it out; he looked it up. The figure in use for Alexandria to Syene was around five thousand
stadia. Where that figure came from, no ancient source says — the usual guess is the bematists,
professional pacers paid to walk between places and count their steps, because pacing was how a
kingdom knew its own size.

Fifty times five thousand. One multiplication, and he had a size for the Earth.

He was close. That is not the interesting part.

## The interesting part is the order he did things in

Notice what he did *not* do. He did not begin with a beautiful idea about spheres and then hunt for
shadows that fitted it. He began with a discrepancy he could not explain, proposed the smallest
shape that would explain it, and then committed to a number — a number that could have come out
absurd, and would have taken his shape down with it.

That order is the whole method:

1. Notice something you cannot explain.
2. Propose the smallest structure that would explain it.
3. Say, in advance, what result would prove the proposal wrong.
4. Check. Keep the answer, especially when it is no.

Step three is the one people skip. It is uncomfortable, it slows everything down, and it is the only
step that makes the other three worth anything. Without it you have a story that fits — and stories
that fit are cheap, because you can always find one after you know the answer.

## What we are doing here

We built a small world inside a computer. Not a model of this world — a world of its own, and
smaller than you are probably picturing.

It has places to keep a number. It has lines joining each place to its neighbours. And it has one
rule, which says how a number changes when the numbers beside it change. That is all of it. The
parts fit on the back of an envelope, and that is usually where they start.

Then we asked the little world questions. Does a ripple spread out evenly in every direction, or
does it run faster along the lines? What does it cost to push a region of it around? Can a patch be
emptied? What happens between two walls? Can it hand back a number that nobody put into it?

For each question we wrote down first what we expected, and what would count as failure. Then we ran
it. Some answers came back yes and some came back no. One came back yes for months, and then turned
out to be an artefact of how we had drawn the grid — that one has a chapter to itself.

Each chapter ends with an italic line pointing at the files where its run lives: the question as it
was registered, the test that re-runs it, the figure drawn from its own output. The last chapter,
[cast your own shadow](cast-your-own-shadow.md), is about going and looking.

## What the word "bubble" means here

This edition is called *Our Bubble*, and the word has one job in it. A bubble is a bounded region of
the little world: a patch we push on, measure, and hand back. Wherever the word appears, that patch
is what it names.

## Back to the child

Go back to her, and to the two marks in the ground. She is one step away from Eratosthenes, and it
is not a large step. She has something that changed and a number for how much it changed. What she
does not have yet is a reason to expect one answer rather than another — and building that reason,
not noticing the shadow, is the hard part.

That is what the rest of this book does. It builds the smallest world we could manage, writes down
what the world should do before it does it, and then lets it answer. The arithmetic stays about as
hard as fifty times five thousand.

*What this chapter cites — and what it does not:
[the simulations](the-simulations.md#s-the-shadow).*

**Next:** [A few thousand years of sharper shadows](a-few-thousand-years-of-sharper-shadows.md)—the
same method, and the two thousand years it took for the instruments to catch up with it.