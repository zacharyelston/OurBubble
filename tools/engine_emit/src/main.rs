//! `engine/rows.json` — the three register rows `napkin-export` does not carry.
//!
//! FIREWALL: the engine computes a toy DEC lattice. *World, place, hole, cut, room, tick* name
//! features of that lattice, never claims about nature. See `../../FIREWALL.md`.
//!
//! `napkin-export` emits `emit::payload()`, and that payload's shape is pinned **byte for byte** to
//! `tools/napkin_export.py`'s output, so nothing may be added to it. Three of the register's 23 rows
//! fall outside it:
//!
//! * **R07** — the one rule on the *triangle*, at a tick that is not dyadic. It is the row that
//!   proves the arithmetic is exact rather than merely lucky in halves: `k = 2/3` has no float, and
//!   the run comes home every four ticks anyway. Both ticks the register names are run here.
//! * **R10** — the tetrahedron has no room. Hops from every dot, and a diameter of one: the fact
//!   chapter 4 needs before it is allowed to cut anything.
//! * **R19** — how many kinds of place there are on a `6³` wrapped world, and the control that makes
//!   that number mean something. A chapter-5 row, and the one the book's `vertex_classes` token
//!   renders today.
//!
//! Every value is computed by the engine's own public functions — `napkin::slosh`, `Complex::hops`,
//! `napkin::kinds_of_place` — and written in the engine's own canonical form (`napkin::Json`), so
//! `rows.json` and `napkin.json` are the same shape by construction rather than by agreement. This
//! crate contains no arithmetic of its own; if it ever needs some, the answer is a register row in
//! UniForge, not a line here.

use napkin::{Complex, Json, Q};

/// The book's smallest wrapped world: parity (mod 2) and the cut rule (mod 3) must both close under
/// the wrap, and ±2 hops must stay distinct.
const SIDE: usize = 6;
/// A bigger one, to confirm the smallest was not showing us its own wrap.
const BIGGER: usize = 12;

fn kinds(n: usize, screw: bool) -> Json {
    let counted = napkin::kinds_of_place(n, screw);
    Json::object(vec![
        ("degree", Json::Int(counted.degree as i128)),
        ("kinds", Json::Int(counted.kinds as i128)),
        ("side", Json::Int(n as i128)),
        ("sizes", Json::ints(counted.sizes.iter().map(|size| *size as i128))),
    ])
}

/// R19 — the wrapped world, its control, and the bigger world that confirms it.
fn world() -> Json {
    Json::object(vec![
        ("bigger", kinds(BIGGER, true)),
        ("bigger_dots", Json::Int((BIGGER * BIGGER * BIGGER / 2) as i128)),
        ("control", kinds(SIDE, false)),
        ("dots", Json::Int((SIDE * SIDE * SIDE / 2) as i128)),
        ("screw", kinds(SIDE, true)),
    ])
}

/// R07 — three numbers sloshing on the triangle, at both of the register's ticks.
///
/// `2/3` is the point of the row: it is not a dyadic rational, so no float represents it, and the
/// table still comes home exactly. The chapters' own `1/2` is run beside it because the contrast is
/// the result — at `1/2` the same three numbers do not repeat within the ticks computed.
fn triangle_motion() -> Json {
    let corners = [Q::int(2), Q::int(5), Q::int(2)];
    Json::object(vec![
        ("corners", Json::strings(corners.iter().map(|value| value.to_exact_string()))),
        ("at_two_thirds", napkin::emit::slosh_payload("triangle", &corners, Q::new(2, 3), 10)),
        ("at_the_book_tick", napkin::emit::slosh_payload("triangle", &corners, Q::new(1, 2), 10)),
    ])
}

/// R10 — the tetrahedron has no room: every dot is one hop from every other, so there is no ring to
/// go round and no direction to go in.
fn no_room() -> Json {
    let tetra = Complex::complete(&[0, 1, 2, 3]).expect("the tetrahedron is a complex");
    let dots = tetra.census().dots;
    let mut rows = Vec::new();
    let mut diameter = 0usize;
    for source in 0..dots {
        let hops = tetra.hops(source);
        diameter = diameter.max(hops.iter().copied().max().unwrap_or(0));
        rows.push(Json::ints(hops.iter().map(|hop| *hop as i128)));
    }
    Json::object(vec![
        ("diameter", Json::Int(diameter as i128)),
        ("dots", Json::Int(dots as i128)),
        ("hops", Json::List(rows)),
    ])
}

fn main() -> std::io::Result<()> {
    let payload = Json::object(vec![
        ("no_room", no_room()),
        ("triangle_motion", triangle_motion()),
        ("world", world()),
    ]);
    let text = payload.canonical();
    match std::env::args().nth(1) {
        Some(path) => std::fs::write(path, text),
        None => {
            use std::io::Write;
            std::io::stdout().write_all(text.as_bytes())
        }
    }
}
