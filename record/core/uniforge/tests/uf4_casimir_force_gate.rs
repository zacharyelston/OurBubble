//! lab/0401 — Warp-4.1: the Casimir force — the piston, and the bench discovers a different exponent.
//!
//! Rung 4.0 needed a bulk subtraction to expose the negative Casimir energy. The FORCE needs none: a
//! movable "piston" plate in a long chain feels F = −∂E_tot/∂a, and the bulk/surface pieces cancel because
//! the total length is fixed. This is the subtraction-free confirmation the vacuum pulls the plates
//! together — and a second automated-discovery test: the bench should recover a DIFFERENT power law from
//! 4.0's (exponent −2, not −1) with coefficient π/24, proving the law-finder reads the physics.
//!
//! Run: `cargo test -p uniforge --release --test uf4_casimir_force_gate -- --nocapture`
//!
//! FIREWALL (R3): the discrete gradient of a TOY scalar field's zero-point energy ½Σℏωₖ on a TOY lattice
//! with a movable interior Dirichlet node. Standard QFT bookkeeping; not a device/spacetime/free energy. c=1.

use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

/// Zero-point energy of a fixed–fixed box of `n` interior sites: E₀ = ½Σₖ 2sin(kπ/2(n+1)).
fn e0(n: i64) -> f64 {
    if n <= 0 {
        return 0.0;
    }
    (1..=n).map(|k| (k as f64 * std::f64::consts::PI / (2.0 * (n as f64 + 1.0))).sin()).sum()
}

/// Total zero-point energy of a bath of `ntot` sites with a movable Dirichlet node at site `p`
/// (splits into boxes of p−1 and ntot−p interior sites).
fn e_tot(ntot: i64, p: i64) -> f64 {
    e0(p - 1) + e0(ntot - p)
}

/// Central-difference Casimir force on the piston at separation a = p: F = −[E(p+1) − E(p−1)]/2.
fn force(ntot: i64, a: i64) -> f64 {
    -(e_tot(ntot, a + 1) - e_tot(ntot, a - 1)) / 2.0
}

/// Slope of a simple linear regression y = m·x + b (returns m).
fn slope(xs: &[f64], ys: &[f64]) -> f64 {
    let m = xs.len() as f64;
    let (sx, sy) = (xs.iter().sum::<f64>(), ys.iter().sum::<f64>());
    let sxy: f64 = xs.iter().zip(ys).map(|(x, y)| x * y).sum();
    let sxx: f64 = xs.iter().map(|x| x * x).sum();
    (m * sxy - sx * sy) / (m * sxx - sx * sx)
}

#[test]
fn uf4_casimir_force_gate() {
    let coeff_theory = std::f64::consts::PI / 24.0; // |F|·a² → π/24
    let ntot: i64 = 4000;
    rec!("\n######## lab/0401 — Warp-4.1: the Casimir force — the piston ########");
    rec!("FIREWALL (R3): discrete gradient of a TOY scalar field's zero-point energy on a TOY lattice.");
    rec!("  bath N_tot={ntot}. Target |F|·a² → π/24 = {coeff_theory:.6}, exponent → −2. c=1.\n");

    // P0 — symmetric split: no net force
    let f_sym = force(ntot, ntot / 2);

    // sweep the piston separation
    let seps: [i64; 7] = [8, 12, 16, 24, 32, 48, 64];
    rec!("[sweep] piston separation a → force F(a):");
    let (mut xs, mut fs, mut ca2) = (Vec::new(), Vec::new(), Vec::new());
    for &a in &seps {
        let f = force(ntot, a);
        rec!("   a={a:>3} | F={f:.6e} | |F|·a²={:.5}", f.abs() * (a * a) as f64);
        xs.push(a as f64);
        fs.push(f);
        ca2.push(f.abs() * (a * a) as f64);
    }
    let attractive = fs.iter().all(|&f| f < 0.0);

    // P2 — discover the law: exponent from log|F| vs log a, coefficient from mean |F|·a²
    let logx: Vec<f64> = xs.iter().map(|a| a.ln()).collect();
    let logy: Vec<f64> = fs.iter().map(|f| f.abs().ln()).collect();
    let exponent = slope(&logx, &logy);
    let coeff = ca2.iter().sum::<f64>() / ca2.len() as f64;
    let coeff_err = (coeff - coeff_theory).abs() / coeff_theory;

    // P3 — far wall irrelevant: double the bath, compare at a mid separation
    let a_mid = 32;
    let f_n = force(ntot, a_mid);
    let f_2n = force(2 * ntot, a_mid);
    let wall_dep = (f_n - f_2n).abs() / f_n.abs();

    rec!("\n[P0] symmetric split (a=N_tot/2): F = {f_sym:.3e} (want |·|<1e-9)");
    rec!("[P1] attractive (F<0 for all a): {attractive}");
    rec!("[P2] DISCOVERED force law: exponent = {exponent:.4} (theory −2); coefficient |F|·a² = {coeff:.5} (theory π/24={coeff_theory:.5}, err {:.2}%)", coeff_err * 100.0);
    rec!("[P3] far wall: F(N_tot)={f_n:.4e} vs F(2·N_tot)={f_2n:.4e} → dep {wall_dep:.2e} (want <1e-3)");

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-4-vacuum/0401-casimir-force-piston/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let mut sweep = String::from("a,force,abs_f_a2\n");
    for (i, &a) in seps.iter().enumerate() {
        sweep.push_str(&format!("{a},{:.9},{:.6}\n", fs[i], ca2[i]));
    }
    std::fs::write(format!("{dir}/force_sweep.csv"), sweep).expect("write force_sweep.csv");
    let fit = format!(
        "metric,value,theory\nexponent,{exponent:.6},-2.0\ncoefficient,{coeff:.6},{coeff_theory:.6}\n\
         coeff_err_frac,{coeff_err:.6},0.0\nf_symmetric,{f_sym:.3e},0.0\nwall_dependence,{wall_dep:.3e},0.0\n"
    );
    std::fs::write(format!("{dir}/force_fit.csv"), fit).expect("write force_fit.csv");

    // verdicts
    let p0 = f_sym.abs() < 1e-9;
    let p1 = attractive;
    let p2 = (exponent + 2.0).abs() < 0.10 && coeff_err < 0.03;
    let p3 = wall_dep < 1e-3;

    let verdict = if p0 && p1 && p2 && p3 {
        format!("THE VACUUM PULLS THE PLATES TOGETHER — SUBTRACTION-FREE, AND THE BENCH FINDS A NEW LAW (R10). The \
             piston force is attractive at every separation, vanishes for a symmetric split (F={f_sym:.0e}), and \
             is independent of the far wall ({wall_dep:.0e}) — so no bulk subtraction is needed. The automated \
             log–log fit discovers a power law with exponent {exponent:.2} (theory −2, DISTINCT from 4.0's −1) \
             and coefficient |F|·a²={coeff:.4} — within {:.1}% of π/24={coeff_theory:.4}. The bench read the \
             force physics, not a hardcoded number. FIREWALL (R3): toy zero-point bookkeeping.", coeff_err * 100.0)
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; f_sym={f_sym:.1e} attractive={attractive} exp={exponent:.3} coeff={coeff:.4} (π/24={coeff_theory:.4}, err {:.1}%) wall={wall_dep:.1e}. FIREWALL (R3).", coeff_err * 100.0)
    };
    rec!("\n[lab/0401 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} exponent={exponent:.4} coeff={coeff:.5} coeff_err={coeff_err:.5} f_sym={f_sym:.2e} wall_dep={wall_dep:.2e}]");

    assert!(p0, "P0: a symmetric split gives no net force");
    assert!(p1, "P1: the Casimir force is attractive");
    assert!(p2, "P2: the bench discovers the force law (exponent −2, coefficient π/24)");
    assert!(p3, "P3: the force is independent of the far wall (subtraction-free)");
}
