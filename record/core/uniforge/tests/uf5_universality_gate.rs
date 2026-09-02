//! lab/0500 — Warp-5.0: universality — the lattice measures the Ising central charge and exponents.
//!
//! The graduation swing (see PREDICTIONS.md): a toy stops being a toy when it outputs a dimensionless number
//! of NATURE it wasn't built to know, with zero tuning. Universality delivers exactly that — at a critical
//! point the central charge c and exponents ν, z are identical for this toy, the 2-D classical Ising model,
//! and real Ising-class materials. We extract them from raw finite-size data of the critical transverse-field
//! Ising chain (free-fermion solvable, built on the same 2−2cos k lattice-Laplacian spectrum used in ch. 4):
//!   • c = 1/2 from the 1/L² correction to the ground-state energy (v MEASURED from the dispersion),
//!   • ν = 1 from the correlation length, z = 1 from the critical gap (both via kinematics::power_law_fit).
//! Nothing is tuned: 1/2, 1, 1 emerge from the data.
//!
//! Run: `cargo test -p uniforge --release --test uf5_universality_gate -- --nocapture`
//!
//! FIREWALL (R3): universal invariants of a TOY quantum spin chain's critical point (shared with the 2-D
//! Ising class and real Ising-class systems). Not a claim the warp/DEC engine is a magnet; no spacetime
//! claim. Dimensionless; c = 1 (speed).

use kinematics::power_law_fit;
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

/// Free-fermion dispersion of the transverse-field Ising chain: ε(k,h) = 2√(1 + h² − 2h cos k).
fn eps(k: f64, h: f64) -> f64 {
    2.0 * (1.0 + h * h - 2.0 * h * k.cos()).max(0.0).sqrt()
}

/// Ground-state energy of the critical (h=1) chain of L sites, Neveu–Schwarz sector:
/// E₀ = −½ Σ_{m=0}^{L−1} ε(π(2m+1)/L, 1).
fn e0_critical(l: usize) -> f64 {
    -0.5 * (0..l).map(|m| eps(std::f64::consts::PI * (2 * m + 1) as f64 / l as f64, 1.0)).sum::<f64>()
}

/// 3-parameter least squares E₀/L = e∞ + b/L² + d/L⁴ → returns (e∞, b).
fn fss_fit(ls: &[usize]) -> (f64, f64) {
    let basis = |l: f64| [1.0, 1.0 / (l * l), 1.0 / (l * l * l * l)];
    let ys: Vec<f64> = ls.iter().map(|&l| e0_critical(l) / l as f64).collect();
    let b: Vec<[f64; 3]> = ls.iter().map(|&l| basis(l as f64)).collect();
    let mut m = [[0.0f64; 3]; 3];
    let mut v = [0.0f64; 3];
    for (row, &y) in b.iter().zip(&ys) {
        for i in 0..3 {
            v[i] += row[i] * y;
            for j in 0..3 {
                m[i][j] += row[i] * row[j];
            }
        }
    }
    // solve 3x3 by Gaussian elimination
    let mut a = [[m[0][0], m[0][1], m[0][2], v[0]], [m[1][0], m[1][1], m[1][2], v[1]], [m[2][0], m[2][1], m[2][2], v[2]]];
    for i in 0..3 {
        let p = a[i][i];
        for k in i..4 {
            a[i][k] /= p;
        }
        for r in 0..3 {
            if r != i {
                let f = a[r][i];
                for k in i..4 {
                    a[r][k] -= f * a[i][k];
                }
            }
        }
    }
    (a[0][3], a[1][3]) // (e∞, b)
}

#[test]
fn uf5_universality_gate() {
    let e_inf_exact = -4.0 / std::f64::consts::PI;
    rec!("\n######## lab/0500 — Warp-5.0: universality — the Ising central charge and exponents ########");
    rec!("FIREWALL (R3): universal invariants of a TOY Ising critical point, shared with real Ising-class systems.");
    rec!("  Targets (exact, Onsager/Pfeuty/BCN): c=1/2, ν=1, z=1, e∞=−4/π={e_inf_exact:.6}.\n");

    // measure the velocity v = dε/dk|₀ from the dispersion (NOT assumed)
    let k_small = 2.0 * std::f64::consts::PI / 8192.0;
    let v = eps(k_small, 1.0) / k_small;

    // P0 + P1 — finite-size scaling → e∞ and the central charge
    let ls: [usize; 6] = [16, 32, 64, 128, 256, 512];
    let (e_inf, b) = fss_fit(&ls);
    let c = -6.0 * b / (std::f64::consts::PI * v);
    rec!("[measure] velocity v = ε(k→0)/k = {v:.6} (exact 2)");
    rec!("[P0/P1] finite-size scaling E₀/L = e∞ + b/L²:");
    for &l in &ls {
        rec!("     L={l:>4} | E₀/L = {:.9}", e0_critical(l) / l as f64);
    }
    rec!("     e∞ = {e_inf:.9} (−4/π = {e_inf_exact:.9});  b = {b:.9} (−π/6 = {:.9})", -std::f64::consts::PI / 6.0);
    rec!("     central charge c = −6b/(πv) = {c:.9}  (target 1/2)");

    // P2 — correlation-length exponent ν: ξ(h) = v/Δ(h), Δ = ε(0,h) = 2|1−h|
    let dhs = [0.2, 0.1, 0.05, 0.02, 0.01, 0.005];
    let xis: Vec<f64> = dhs.iter().map(|&dh| v / eps(0.0, 1.0 - dh)).collect();
    let nu = -power_law_fit(&dhs, &xis).exponent; // ξ ~ |h−h_c|^{−ν}
    rec!("\n[P2] correlation length ξ = v/Δ vs |h−h_c| → ν = {nu:.6} (target 1)");

    // P3 — dynamic exponent z: critical finite-size gap Δ(L) = ε(π/L, 1) ~ L^{−z}
    let lz: Vec<f64> = ls.iter().map(|&l| l as f64).collect();
    let gaps: Vec<f64> = ls.iter().map(|&l| eps(std::f64::consts::PI / l as f64, 1.0)).collect();
    let z = -power_law_fit(&lz, &gaps).exponent; // Δ ~ L^{−z}
    rec!("[P3] critical finite-size gap Δ(L) = ε(π/L,1) vs L → z = {z:.6} (target 1)");
    rec!("\n[note] β = 1/8 (Pfeuty exact M=(1−h²)^{{1/8}}) — the magnetization exponent of the same class (cited).");

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-5-universality/0500-ising-universality/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let mut fss = String::from("L,e0_over_L\n");
    for &l in &ls {
        fss.push_str(&format!("{l},{:.9}\n", e0_critical(l) / l as f64));
    }
    std::fs::write(format!("{dir}/fss.csv"), fss).expect("write fss.csv");
    let mut nucsv = String::from("dh,xi\n");
    for (dh, xi) in dhs.iter().zip(&xis) {
        nucsv.push_str(&format!("{dh},{xi:.6}\n"));
    }
    std::fs::write(format!("{dir}/nu.csv"), nucsv).expect("write nu.csv");
    let exps = format!(
        "quantity,measured,target\ncentral_charge_c,{c:.6},0.5\nnu,{nu:.6},1.0\nz,{z:.6},1.0\n\
         e_inf,{e_inf:.6},{e_inf_exact:.6}\nvelocity_v,{v:.6},2.0\nbeta_cited,0.125,0.125\n"
    );
    std::fs::write(format!("{dir}/exponents.csv"), exps).expect("write exponents.csv");

    // verdicts
    let p0 = (e_inf - e_inf_exact).abs() < 1e-4;
    let p1 = (c - 0.5).abs() < 1e-3;
    let p2 = (nu - 1.0).abs() < 0.02;
    let p3 = (z - 1.0).abs() < 0.02;

    let verdict = if p0 && p1 && p2 && p3 {
        format!("THE TOY MEASURES NATURE'S ISING NUMBERS — PARAMETER-FREE (R10). From raw finite-size data of the \
             critical Ising chain, with the velocity v={v:.3} MEASURED not assumed, the lattice returns the \
             universal invariants of the 2-D Ising class: central charge c = {c:.5} (target ½), correlation-length \
             exponent ν = {nu:.4} (target 1), dynamic exponent z = {z:.4} (target 1), on the exact critical energy \
             density e∞ = {e_inf:.5} = −4/π. Nothing was tuned — ½, 1, 1 emerged from the E₀(L) scaling. These are \
             the SAME numbers measured in real Ising-class materials (universality): the toy reproduced a piece of \
             nature it was not built to know. (Honest scope: c=½ here is a postdiction of a solvable model — the \
             machinery is validated; the novel prediction is an unsolved model's exponents, the next rung.) \
             FIREWALL (R3): universality-class membership, not a spacetime claim.")
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; c={c:.5} ν={nu:.4} z={z:.4} e∞={e_inf:.5} v={v:.4}. FIREWALL (R3).")
    };
    rec!("\n[lab/0500 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} c={c:.6} nu={nu:.6} z={z:.6} e_inf={e_inf:.6} v={v:.6} b={b:.6}]");

    assert!(p0, "P0: the critical ground-state energy density is −4/π");
    assert!(p1, "P1: the central charge c = 1/2 emerges from finite-size scaling (parameter-free)");
    assert!(p2, "P2: the correlation-length exponent ν = 1");
    assert!(p3, "P3: the dynamic exponent z = 1");
}
