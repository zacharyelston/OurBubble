# Build with UniForge — demos & directions

For a software engineer, no physics required. UniForge is a **deterministic field-simulation engine**
you drive over ordinary interfaces; it hands you the raw numbers of a live run on a lattice, and you
build the app. This page turns the [README's "What can you build?"](../README.md#what-can-you-build-with-it)
table into working recipes.

> **Firewall.** Everything here simulates fields **on a lattice** — *photon, wave, fringe, energy*
> name features of a discrete computation, never claims about nature. See [`../FIREWALL.md`](../FIREWALL.md).
> Build cool things; don't ship them as statements about reality.

## Prerequisites (build the two binaries once)

```bash
cd core
cargo build --release -p uniforge --features server --bin serve   # the /sim streaming server
cargo build --release -p uniforge-mcp                              # the MCP server (for scripting)
```

The static demo pages need only a file server (any will do) — **serve the repo root, not `viz/`**:

```bash
python3 -m http.server 8080          # from the repo root; the gallery is at /viz/index.html
```

The gallery and both synthesis pages link *out* of `viz/` (`../lab/**/figures/*.html` for the
data-true figures, `../core/uniforge/tests/*.rs` for the gates), so a server rooted at `viz/` answers
404 for every one of those — ~90 links across the two pages. Root the server at the repo and they
all resolve. The repo's [`.claude/launch.json`](../.claude/launch.json) has ready `sim-server` +
`viz-gallery` entries (the gallery one is rooted at the repo) if you use a launcher that reads it.

---

## Demo 0 — the skeptic's test (check the record before you trust the demos)

Everything below this section is a thing to *build*. This one is a thing to *check*: three commands
that take the repo's claim — every committed number is the output of a re-runnable gate — and try to
break it. It is the script the closing section of both synthesis pages prints, and the
generator asserts each command below appears **verbatim** on this page, so the two can never drift.

**1 · Re-run a gate for record.** Not a smoke test — the real 64³ dispersion sweep, which overwrites
the committed CSVs the synthesis page and the Discovery Bench quote:

```bash
cd core
cargo test -p uniforge --release --test uf1_7_dispersion_isotropy_gate -- --nocapture
```

It rewrites all five files in `lab/warp-1-move/0117-dispersion-isotropy/data/`
(`dispersion_directions.csv`, `discovery.csv`, `candidates.csv`, `isotropy.csv`, `answer_key.csv`)
from scratch, and prints the blind law selection as it goes.

**2 · Check that nothing moved.**

```bash
cd ..
git status --porcelain lab/
```

**This must print nothing.** The gate just regenerated committed data from scratch; if any number on
the pages had been fitted after the fact, tuned to taste, or hand-edited, a diff appears here. A
clean `lab/` is the claim, and this is the one command that tests it.

**3 · Walk the pages the way a visitor does.** Serve the **repo root** (see Prerequisites — the
pages link out of `viz/`), optionally with the engine up so the live demos stream:

```bash
cargo build --release -p uniforge --features server --bin serve
python3 -m http.server 8080
```

Open <http://localhost:8080/viz/synthesis-slow-ramp.html> — the front door, with every link
resolving into the repo — then <http://localhost:8080/viz/synthesis.html> for the complete edition of
the same record, and <http://localhost:8080/viz/index.html> for the gallery.

---

## Demo 1 — See it in 2 minutes (the double-slit)

```bash
# terminal 1: the engine's WebSocket server (prints ws://localhost:4100/sim)
core/target/release/serve

# terminal 2: serve the gallery — from the REPO ROOT (see Prerequisites)
python3 -m http.server 8080
```

Open **http://localhost:8080/viz/doubleslit.html**. A plane wave hits a wall with two slits; the
wavelets interfere. The header reads `⬤ connected to uniforge`. Drag **wavelength**, **slit
separation**, **slit width**, toggle one-vs-two slits — every control re-drives the engine live. The
browser computes *no* physics; it renders frames the server sends. That's the whole idea: **the
engine simulates, your page renders.**

Skip terminal 1 and the page still works: with no server the header reads `⬤ snapshot
(viz/doubleslit_data.js)` and it replays the same solver's committed export (written by
`core/viz gen_doubleslit`), taking the live stream over the moment one appears. The sliders are the
part that needs a server — there is nothing to re-drive in a snapshot, so they grey out.

**The one control that only works offline** is the rung-3.5 **mirror-repaired mesh (crossed
diagonals)** checkbox: it swaps between two committed arms of the same scene, so it is enabled in
snapshot mode and greyed out when a server is streaming. Tick it and the demo's ~3.8× left/right
brightness asymmetry — a mesh artifact, not optics (rung 3.5 / #252) — goes away: same scene, same
solver, alternating diagonals. It is the shortest "the lattice can be wrong, and we show you where"
demo in the repo.

Other live pages in the gallery: `mercury.html`, `multi.html` (many views, one engine).
`mercury.html` also renders offline from its committed snapshot (`viz/mercury_data.js`, from
`core/viz gen_mercury`: the relaxed static potential *and* the test-particle orbit, integrated in
Rust — the page draws that same trajectory whether or not a server is streaming the field);
`multi.html` is the streaming-only one. Data-true (pre-computed, no server) pages: `em.html`,
`afeb.html`, `lattice.html`, and the three bubble pages `bubble.html`, `bubble3d.html`,
`bubble_live.html` (the last animates a committed export — "live" is the pulse, not a socket).
Every page carries the shared nav strip; `index.html` *is* the gallery, so it has no strip of its own.

---

## Demo 2 — Stream a sim into your own page (the `/sim` protocol)

The client library is [`viz/sim-client.js`](../viz/sim-client.js) (~90 lines, no dependencies).
Copy `viz/doubleslit.html` as a starting skeleton, or talk to the socket directly. The protocol:

**Connect:** `ws://<host>:4100/sim` (the page's own host; falls back to `localhost:4100`).

**Up — JSON commands** (`{cmd: "...", ...}`):

| cmd | purpose |
|---|---|
| `init` | start a sim: `{cmd:"init", mesh:{type:"grid3d", n:24}, solvers:["scalar_wave","em_wave"], hodge:"geometric", c:1.0, dt:0.05}` |
| `set` | live-tune `c`, `dt`, `gamma`, `fps`, `steps_per_frame` |
| `set_point_source` / `set_plane_wave_source` | inject a source: `{cmd:"set_point_source", vertex:N, wavelength:4.0, amplitude:1.0}` |
| `set_wall` / `set_damping` | Dirichlet walls / absorbing boundaries |
| `seed` | set initial `φ` values directly |
| `solve_static` | relax to the static potential and hold it |
| `pause` / `resume` / `reset` / `step` | playback control |
| `clear_boundaries` | drop all sources/walls/damping |

Mesh types: `grid2d {nx,ny}`, `grid3d {n}`, `grid3d_rect {nx,ny,nz}`. Hodge: `geometric` (metric ⋆,
isotropic) or `trivial` (⋆=I). Each connection owns its own sim — many clients, no cross-talk.

**Down — JSON then binary frames.** JSON: `{type:"mesh_info", n_vertices, n_edges, n_faces, coords,
edges, faces, ...}` (once after `init`), `{type:"ok"|"error", message}`. Binary frame (little-endian):

```
byte 0      0x01 (frame marker)
u32         frame number
f32         sim time
u16         field count
  per field:
    u8      field id   (0x00 scalar φ · 0x01 EM A · 0x02 F=dA)
    u32     length N
    N×f32   values
```

`SMClient.parseFrame(buf)` in `sim-client.js` decodes exactly this. Minimal loop:

```js
const c = new SMClient({ onMesh: m => setup(m), onFrame: f => render(f.fields[0]) });
c.connect();
c.onReady = () => { c.send({cmd:"init", mesh:{type:"grid3d", n:24}, solvers:["scalar_wave"]});
                    c.send({cmd:"set_point_source", vertex:8000, wavelength:4, amplitude:1}); };
```

Build: interactive explorables, teaching tools, generative visuals — anything that wants real field
dynamics without shipping a solver to the client.

---

## Demo 3 — Script experiments, no browser (the CLI, or the MCP tools)

The engine's two headline tools also run **straight from the command line** — no MCP client to
register, no token. Same stamped envelope either way (firewall line + full parameter echo + the
`backend` the call actually ran on), so a scripted CLI run and a `tools/call` are the same result:

```bash
cd core
cargo build --release -p uniforge-mcp

# engine_info: version, layers, and the live d²=0 handshake
cargo run -q -p uniforge-mcp -- info

# solve_em_evolve: the deterministic CPU smoke from the sample prompt
echo '{"n":4,"steps":64,"winding":1,"sample_every":8,"hodge":"trivial","backend":"cpu"}' > p.json
cargo run -q -p uniforge-mcp -- run-evolve --params p.json          # envelope to stdout
cargo run -q -p uniforge-mcp -- run-evolve --params p.json --out e.json   # …or to a file
```

The envelope is JSON on stdout, so pipe it into `jq` and you have a sweep in a shell loop
(vary `n`, `hodge`, `winding`; read `.result.energy_drift_rel`). This is the frictionless local
path — no scaffolding, no hand-rolled MCP driver.

The same engine is also **MCP tools** (see [`MCP.md`](MCP.md)). Register the server from any MCP
client (Claude Code, an IDE, your own agent); the repo's [`.mcp.json`](../.mcp.json) wires a
deployed `uniforge` server and a local `uniforge-dev` stdio binary
(`core/target/release/uniforge-mcp`).

The first prompt, verbatim from the [README](../README.md#sample-prompt):

> Using the UniForge tools, call `engine_info` and verify the live `d²=0` check … run one
> deterministic CPU smoke test with `n=4, steps=64, winding=1, sample_every=8, hodge="trivial",
> backend="cpu"`; report mesh size, initial/final energy, relative drift …

What you get back is a **stamped envelope**: the firewall line, your full parameter set echoed, the
`backend` the call actually ran on, and the result. Because every call echoes its parameters and is
deterministic, a sweep is just a loop over `solve_em_evolve` calls — plot energy drift vs. `n`, vs.
`hodge`, vs. `winding`, and you have a dashboard or a notebook figure. (MCP runs are exploratory
probes, never run-for-record — see the R1 note in the README.)

---

## Demo 4 — Ship a data-true figure (the `gen_*` pattern)

The visualization discipline is **the sim IS the graphic** (R10): a Rust exporter evaluates the real
engine and writes a data file; a self-contained HTML page renders it. No physics in the browser, no
analogy art. Worked examples you can copy:

- [`core/viz/src/bin/gen_em_pulse.rs`](../core/viz/src/bin/gen_em_pulse.rs) → `viz/em_data.js` → `viz/em.html`
  (round-vs-lopsided EM pulse). Run `--release` — the consistent stepper is heavy (see #128).
- [`core/viz/src/bin/gen_a_f_eb.rs`](../core/viz/src/bin/gen_a_f_eb.rs) → `viz/afeb_data.js` → `viz/afeb.html`
  (the `A → F=dA → E/B` chain on one tetrahedron).

```bash
cd core
cargo run --release -p viz --bin gen_em_pulse   # writes viz/em_data.js
cargo run         -p viz --bin gen_a_f_eb        # writes viz/afeb_data.js
```

Pattern to build your own: evaluate `geom`/`dec`/`solve`/`kinematics` on a mesh, serialize the fields
to a `window.YOURDATA = {...}` JS file under `viz/`, and write an HTML page that draws it. Build:
publication figures, docs explorables, anything where the picture must be *provably* the computation.

---

## Where to go next

- [`viz/README.md`](../viz/README.md) — the gallery, every page, and how to regenerate its data.
- [`MCP.md`](MCP.md) — the MCP server spec and the tool surface. (Being refreshed — issue #132.)
- [`UNIFORGE.md`](UNIFORGE.md) — the layered architecture (`geom → dec → solve → kinematics → viz → mcp`).
- [`viz/sim-client.js`](../viz/sim-client.js) — the `/sim` client, the whole streaming API in ~90 lines.
