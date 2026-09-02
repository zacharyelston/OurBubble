# FIREWALL — what this book claims, and what it does not

> **Scope.** This is a book about a **toy**: a small world built inside a computer, and what happened
> when we pointed real tests at it. Nothing here is a claim about nature. Where a chapter uses a word
> like *vacuum* or *light cone*, the word names a pattern in the model.

That box opens every chapter, and this page is the long version of it. If you read only one thing
here, read the box.

## The one sentence

**Everything in this book happened inside a computer, in a world we built on purpose.**

We wrote down a small structure — points, lines, patches, a rule for how a ripple crosses them —
and then we asked it questions the way you would ask a laboratory: state what you expect *before*
you look, run it, and keep the answer whether or not you liked it. The answers are real answers.
They are answers **about the thing we built**.

## What the words mean here

The book uses ordinary physics words, because they are the shortest names for the shapes involved.
Every one of them names a feature of the model:

| the word | what it names in this book |
|---|---|
| *light cone* | how fast a disturbance can spread across the structure we built |
| *vacuum* | the model's lowest-energy state, with nothing added to it |
| *material*, *permittivity* | numbers we set on the structure to stand in for a substance |
| *bubble* | a bounded region inside the model — and the shared viewpoint of you and us, standing inside one experiment |
| *Ising*, *universality* | a pattern of numbers this model shares with a family of well-studied models |

None of them is being used to say something about the world outside the computer.

## Three things this book is not

1. **It is not evidence that space is made of little pieces.** We built something out of little
   pieces because that is what a computer can hold. The building is a choice, not a discovery.
2. **It is not a proposal for a technology.** A chapter about a bubble and its energy bill is
   arithmetic inside a toy. It does not describe anything anyone could build.
3. **It is not a theory of constants, forces, or the shape of the universe.** An older manuscript in
   this project's history reached in that direction. That programme is excluded here, deliberately
   and mechanically: the edition checker refuses a set of specific claims and paraphrases of them,
   and it is tested on sentences it must refuse before it is allowed to check the book.

## Why you can check us anyway

A toy result can still be honest or dishonest, and the difference is whether you can go and look.
So every number the book leans on is quoted from a record kept in another repository, the **UniForge**
engine, pinned to one commit in [`record.lock`](record.lock) — and the appendix tells you which file
carries it. The book cannot be built without that record present; a quotation that stopped being
true stops the build and names itself.

That is the whole guarantee, and it is worth being precise about its size. It says: *the book
faithfully reports what the experiment recorded.* It does not say the experiment was about nature.
It was not.

## What we do claim

That the method is worth having. Notice something. Propose the smallest shape that would explain it.
Say in advance what would prove you wrong. Check, keep the negative, and let the next question come
from what actually came back.

That part is not a toy.
