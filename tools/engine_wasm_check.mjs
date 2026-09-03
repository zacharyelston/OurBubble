// Load the vendored WebAssembly engine and ask it the census question.
//
// FIREWALL: the engine computes a toy DEC lattice. Nothing it answers is a claim about nature.
// See ../FIREWALL.md.
//
// This is the third of `engine.lock`'s three integrity layers, and the only one that proves the two
// vendored artifacts are the *same* engine. The hashes prove `engine/napkin.json` and
// `engine/napkin_bg.wasm` are the bytes that were built; a fresh export proves the JSON came from
// the pinned commit. Neither says a word about the wasm's arithmetic. So the module is loaded and
// asked one question whose answer the JSON already carries — the census of the complete complex on
// four dots, which is chapters 1 and 2's whole object — and the answer must match **byte for byte**,
// not value for value. A tolerance here would be the exact seam the one-engine decision closes.
//
// It writes the module's answer to stdout and nothing else, so the comparison is made in
// `check_edition.py`, where the failure can be reported by name alongside the others.
//
//   node tools/engine_wasm_check.mjs [engine-dir]

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import path from "node:path";

const here = path.dirname(new URL(import.meta.url).pathname);
const dir = process.argv[2] ?? path.join(here, "..", "engine");

// `wasm-bindgen --target web` writes glue that reaches for `fetch` when it is given a URL. Node has
// the bytes on disk, so they are handed over directly — the same module the browser would load, from
// the same file, with nothing between it and the check.
const glue = await import(pathToFileURL(path.join(dir, "napkin.js")).href);
await glue.default({ module_or_path: readFileSync(path.join(dir, "napkin_bg.wasm")) });

process.stdout.write(glue.census_json(4));
