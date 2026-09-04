# `engine/` — the vendored napkin engine

> **FIREWALL.** The engine computes a **toy** DEC lattice. *Dot, line, face, inside, tick, slosh,
> poke, crossing, stella, world* name features of that lattice and its discretisation, never claims
> about nature. [`../FIREWALL.md`](../FIREWALL.md) is the long version.

**Nothing in this directory except this note is written by hand, and nothing in it should be
edited** — including this note's table, whose numbers are the lock's. It is built by
[`../tools/build_engine.sh`](../tools/build_engine.sh) from a checkout of the UniForge engine at the
commit [`../engine.lock`](../engine.lock) pins, and every byte of it is hashed there.

## Where it comes from

| | |
|---|---|
| source | `github.com/zacharyelston/UniForge` — **private** |
| commit | `f8f07ebb79c21aa60407c47b4bb9d7cc4a8729c9` — UniForge `napkin/engine`, the head of PR #362. **Not yet on UniForge `main`**: see `../engine.lock`'s header, and the pin must move to that PR's merge commit. |
| crate | `core/napkin` v0.1.2 — UniForge Layer 3 |
| register | `lab/napkin/0001-napkin-engine-register` — 23 registered computations, all implemented; and `lab/napkin/0003-engine-gaps` — five more (G01–G05), all implemented |
| toolchain | rustc 1.97.1, `wasm32-unknown-unknown`, wasm-bindgen 0.2.127 |

The crate is the engine for the book **and** its demos (owner's decision, 2026-09-02). Python and
JavaScript are renderers of what it computes; they no longer compute it.

## What is here

| file | what it is |
|---|---|
| `napkin.json` | the canonical payload — every token's underlying data, and none of its prose. **Byte-identical** to `tools/napkin_export.py`'s output, which is the bar the build script refuses to vendor without. |
| `rows.json` | register rows **R07**, **R10** and **R19** — the rule on the triangle at a tick no float represents, the tetrahedron's want of room, and how many kinds of place there are on a `6³` wrapped world with the control beside it — and, under `gaps`, **G01–G05**, the five the demos asked for. Emitted separately because `napkin.json`'s shape is pinned to the Python oracle's and nothing may be added to it. |
| `napkin_bg.wasm` | the engine compiled for the browser — the reader's own copy of the arithmetic |
| `napkin.js` | the wasm-bindgen glue: nine entry points, strings in and strings out, so no rational type and no float crosses the boundary. None of them panics — an unknown object, a value that is not an exact rational, a walk that does not exist all come back as a refusal object, because a panic here is an unrecoverable trap that would take the page with it. |
| `napkin.d.ts`, `napkin_bg.wasm.d.ts` | the types wasm-bindgen wrote beside them |

## Why it is committed

Our Bubble is public and UniForge is private. A book whose pages could only be built by someone with
a key to the engine would be a book with a private dependency — the shape this repository was split
out to avoid. So the artifact is vendored: **every clone builds the book and runs the demos with no
access to UniForge at all**, and `engine.lock` is what makes the vendored copy evidence rather than
a copy.

## Licence

The `napkin` crate is published by UniForge under **MIT OR Apache-2.0** (`core/Cargo.toml`,
`license = "MIT OR Apache-2.0"`). These files are that crate's output, built unmodified from the
commit above, and they carry that licence with them. This directory adds nothing of its own.
