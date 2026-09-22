//! Gate for lab/bridge/0803-netlist (rung 8.3, R1) — the netlist / SPICE view.
//!
//! Export the stella graph as a real SPICE netlist (resistor per edge) and verify an independent
//! modified-nodal-analysis (MNA) solve — the SPICE formulation — reproduces our effective_resistance.
//! Makes "the circuit computes it" literal; ties the electrical view (8.2) to analog/crossbar computing.
//!
//! Run: cargo test -p uniforge --release --test uf8_3_netlist_gate -- --nocapture   (~1 s)
//!
//! FIREWALL (R3): a resistor network of a TOY 14-regular graph — a computer for the toy's graph math,
//! never a physical realization of the warp analogy. Dimensionless; c=1.

use kinematics::views::{commute_time, effective_resistance, mna_resistance, to_spice_netlist};
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

const DIFFS_N: [[i64; 3]; 3] = [[1, -1, 0], [0, 1, -1], [-1, 0, 1]];
const LONG_N: [[i64; 3]; 3] = [[1, -1, 1], [1, 1, -1], [-1, 1, 1]];
fn stella_hops(tau: usize) -> Vec<[i64; 3]> {
    let mut h = Vec::with_capacity(14);
    for d in [[1i64, 0, 0], [0, 1, 0], [0, 0, 1]] { h.push(d); h.push([-d[0], -d[1], -d[2]]); }
    for d in DIFFS_N { h.push(d); h.push([-d[0], -d[1], -d[2]]); }
    let sc = (2 * tau) % 3;
    h.push(LONG_N[(sc + 1) % 3]);
    let b = LONG_N[(sc + 2) % 3];
    h.push([-b[0], -b[1], -b[2]]);
    h
}
/// rule-built 14-regular stella torus: (n_nodes, edge list, dense Laplacian).
fn stella_torus(m: usize) -> (usize, Vec<(usize, usize)>, Vec<Vec<f64>>) {
    let mm = m as i64;
    let idx = |a: i64, b: i64, c: i64| (a.rem_euclid(mm) * mm * mm + b.rem_euclid(mm) * mm + c.rem_euclid(mm)) as usize;
    let n = m * m * m;
    let mut set = std::collections::BTreeSet::new();
    let mut l = vec![vec![0.0f64; n]; n];
    for a in 0..mm { for b in 0..mm { for c in 0..mm {
        let tau = ((a + b + c) % 3) as usize;
        let i = idx(a, b, c);
        for d in stella_hops(tau) {
            let j = idx(a + d[0], b + d[1], c + d[2]);
            l[i][i] += 1.0; l[i][j] -= 1.0;
            set.insert((i.min(j), i.max(j)));
        }
    }}}
    (n, set.into_iter().collect(), l)
}
fn cube_edges() -> Vec<(usize, usize)> {
    (0..8usize).flat_map(|u| (0..3).map(move |b| (u, u ^ (1 << b))).filter(|&(u, v)| u < v)).collect()
}

#[test]
fn uf8_3_netlist_gate() {
    rec!("=== rung 8.3 — the netlist / SPICE view (the circuit computes) ===");
    rec!("FIREWALL: a resistor network of a TOY graph — a computer for its math, not nature.");

    // ---- P0: MNA controls (closed forms) ----
    let series = [(0usize, 1usize), (1, 2)];
    let parallel = [(0usize, 1usize), (0, 1)];
    let cube = cube_edges();
    let r_series = mna_resistance(&to_spice_netlist(&series, 0, 2));
    let r_parallel = mna_resistance(&to_spice_netlist(&parallel, 0, 1));
    let r_cube = mna_resistance(&to_spice_netlist(&cube, 0, 7));
    rec!("[P0] series={r_series:.9} (2)  parallel={r_parallel:.9} (0.5)  cube-diag={r_cube:.9} (5/6={:.9})", 5.0 / 6.0);
    let p0 = (r_series - 2.0).abs() < 1e-9 && (r_parallel - 0.5).abs() < 1e-9 && (r_cube - 5.0 / 6.0).abs() < 1e-9;

    // ---- stella torus M=3 ----
    let (n, edges, l) = stella_torus(3);
    let ne = edges.len();
    rec!("[stella] M=3: {n} nodes, {ne} edges");

    // ---- P1: netlist-MNA == effective_resistance (membership gate) ----
    let mut p1 = true;
    let mut p1_worst = 0.0f64;
    let mut rows = Vec::new();
    for (a, b) in [(0usize, 1usize), (0, 13), (5, 20), (2, 25)] {
        let r_mna = mna_resistance(&to_spice_netlist(&edges, a, b));
        let r_eff = effective_resistance(&l, a, b);
        let d = (r_mna - r_eff).abs();
        p1 &= d < 1e-9;
        p1_worst = p1_worst.max(d);
        rec!("[P1] pair {a},{b}: MNA={r_mna:.9} R_eff={r_eff:.9} |Δ|={d:.1e}");
        rows.push(format!("{a}-{b},{r_mna:.9},{r_eff:.9}"));
    }

    // ---- P2: walks↔circuits via the netlist ----
    let mut p2 = true;
    let mut p2_worst = 0.0f64;
    let mut wrows = Vec::new();
    for (a, b) in [(0usize, 1usize), (5, 20)] {
        let elec = 2.0 * ne as f64 * mna_resistance(&to_spice_netlist(&edges, a, b));
        let walk = commute_time(&l, a, b);
        let d = (elec - walk).abs();
        p2 &= d < 1e-9;
        p2_worst = p2_worst.max(d);
        rec!("[P2] pair {a},{b}: 2E·R(netlist)={elec:.6} commute={walk:.6} |Δ|={d:.1e}");
        wrows.push(format!("{a}-{b},{elec:.6},{walk:.6}"));
    }

    // ---- P3: portable artifact ----
    let cir = to_spice_netlist(&edges, 0, 1);
    let n_r = cir.lines().filter(|l| l.starts_with('R')).count();
    let well_formed = n_r == ne && cir.contains("V1 ") && cir.contains(".op") && cir.contains(".end");
    rec!("[P3] emitted .cir: {n_r} R-lines (edges={ne}), V1/.op/.end present = {well_formed}");
    let p3 = well_formed;

    // ---- emit data (R10): the netlist artifact + the agreement tables ----
    let dir = std::path::PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/bridge/0803-netlist/data"));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("stella.cir"), &cir).unwrap();
    let write = |name: &str, header: &str, rows: &[String]| {
        let mut f = std::fs::File::create(dir.join(name)).unwrap();
        writeln!(f, "{header}").unwrap();
        for r in rows { writeln!(f, "{r}").unwrap(); }
    };
    write("resistance.csv", "pair,mna_netlist,effective_resistance", &rows);
    write("walks_circuits.csv", "pair,elec_2ER_netlist,walk_commute", &wrows);
    write("summary.csv", "quantity,value", &[
        format!("cube_diagonal,{r_cube:.9}"),
        format!("n_edges,{ne}"),
        format!("netlist_vs_reff_worst,{p1_worst:.2e}"),
    ]);

    rec!("--------------------------------------------------------------------");
    rec!("[VERDICT] P0(MNA controls)={p0} P1(netlist==R_eff, worst={p1_worst:.1e})={p1} P2(walks↔circuits, worst={p2_worst:.1e})={p2} P3(portable .cir)={p3}");
    rec!("[FIREWALL] the stella .cir is a runnable resistor network for a TOY graph's math (analog/");
    rec!("           crossbar lineage) — a circuit that computes the lattice's resistances, not nature.");
    assert!(p0, "P0 failed: MNA closed-form controls");
    assert!(p1, "P1 failed: netlist MNA ≠ effective_resistance (export unfaithful / view fails membership)");
    assert!(p2, "P2 failed: 2E·R(netlist) ≠ commute time");
    assert!(p3, "P3 failed: emitted .cir malformed");
}
