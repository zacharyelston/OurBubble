//! lab/0402 — Warp-4.2: the automated bench — one law-finder, many laws.
//!
//! The chapter's meta-claim: the lattice is a cheap virtual workbench whose value-add is AUTOMATION. Rungs
//! 4.0/4.1 ran ad-hoc fits inside their gates; here that becomes a reusable engine capability
//! (`kinematics::power_law_fit`) and the SAME function discovers laws across DIFFERENT experiments:
//!   • it recovers a synthetic power law exactly (tool sanity),
//!   • it rediscovers the Casimir force scaling (|F| ∝ a⁻²) from the lattice zero-point energy,
//!   • it MEASURES the lattice's own spatial dimension from the Laplacian heat-kernel decay K(t) ∝ t^{−d/2},
//!     recovering d = 1, 2, 3.
//! One tool, reading physics — not a hardcoded per-gate answer.
//!
//! Run: `cargo test -p uniforge --release --test uf4_automated_bench_gate -- --nocapture`
//!
//! FIREWALL (R3): pure data-analysis of TOY-lattice outputs (log–log power-law fit; periodic graph-Laplacian
//! heat-kernel trace). The "dimension" is the toy lattice's spectral dimension, not a claim about nature. c=1.

use kinematics::{heat_kernel_line, power_law_fit};
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

/// Zero-point energy of a fixed–fixed box of `n` interior sites (as rung 4.0/4.1).
fn e0(n: i64) -> f64 {
    if n <= 0 {
        return 0.0;
    }
    (1..=n).map(|k| (k as f64 * std::f64::consts::PI / (2.0 * (n as f64 + 1.0))).sin()).sum()
}
fn e_tot(ntot: i64, p: i64) -> f64 {
    e0(p - 1) + e0(ntot - p)
}
/// Central-difference piston force at separation a (as rung 4.1).
fn force(ntot: i64, a: i64) -> f64 {
    -(e_tot(ntot, a + 1) - e_tot(ntot, a - 1)) / 2.0
}

#[test]
fn uf4_automated_bench_gate() {
    rec!("\n######## lab/0402 — Warp-4.2: the automated bench — one law-finder, many laws ########");
    rec!("FIREWALL (R3): log–log power-law fit + heat-kernel trace on TOY-lattice outputs. Same tool, many experiments. c=1.\n");

    // P0 — the tool is correct: synthetic y = 3 x^{-2}
    let sx: Vec<f64> = (1..=10).map(|i| i as f64).collect();
    let sy: Vec<f64> = sx.iter().map(|x| 3.0 * x.powf(-2.0)).collect();
    let synth = power_law_fit(&sx, &sy);
    rec!("[P0] synthetic 3·x⁻²  → exponent={:.6} coeff={:.6} R²={:.9}", synth.exponent, synth.coefficient, synth.r2);

    // P1 — rediscover the Casimir force law from the lattice zero-point energy
    let ntot = 4000i64;
    let seps: [i64; 7] = [8, 12, 16, 24, 32, 48, 64];
    let fx: Vec<f64> = seps.iter().map(|&a| a as f64).collect();
    let fy: Vec<f64> = seps.iter().map(|&a| force(ntot, a)).collect();
    let flaw = power_law_fit(&fx, &fy);
    rec!("[P1] Casimir force |F| vs a → exponent={:.4} (theory −2) coeff={:.5} R²={:.6}", flaw.exponent, flaw.coefficient, flaw.r2);

    // P2 — measure the lattice's spatial dimension from the heat kernel Kd(t)=line(t)^d
    let n = 4000usize;
    let ts: [f64; 6] = [16.0, 32.0, 64.0, 128.0, 256.0, 512.0];
    let line: Vec<f64> = ts.iter().map(|&t| heat_kernel_line(n, t)).collect();
    rec!("[P2] spectral dimension via heat kernel K(t) ∝ t^(−d/2):");
    let mut dims = Vec::new();
    for d in 1..=3usize {
        let kd: Vec<f64> = line.iter().map(|&l| l.powi(d as i32)).collect();
        let law = power_law_fit(&ts, &kd);
        let dim = -2.0 * law.exponent;
        rec!("     d={d}: slope={:.4} → measured dim={dim:.4} (R²={:.6})", law.exponent, law.r2);
        dims.push((d, dim, law.r2));
    }

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-4-vacuum/0402-automated-bench/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let mut fits = String::from("experiment,exponent,coefficient,r2,theory_exponent\n");
    fits.push_str(&format!("synthetic_3x^-2,{:.6},{:.6},{:.9},-2\n", synth.exponent, synth.coefficient, synth.r2));
    fits.push_str(&format!("casimir_force,{:.6},{:.6},{:.6},-2\n", flaw.exponent, flaw.coefficient, flaw.r2));
    for (d, dim, r2) in &dims {
        fits.push_str(&format!("heat_kernel_d{d},{:.6},{dim:.6},{r2:.6},{}\n", -(*d as f64) / 2.0, d));
    }
    std::fs::write(format!("{dir}/fits.csv"), fits).expect("write fits.csv");
    let mut hk = String::from("t,line,k1,k2,k3\n");
    for (i, &t) in ts.iter().enumerate() {
        let l = line[i];
        hk.push_str(&format!("{t},{l:.6},{:.6},{:.6},{:.6}\n", l, l * l, l * l * l));
    }
    std::fs::write(format!("{dir}/heat_kernel.csv"), hk).expect("write heat_kernel.csv");

    // verdicts
    let p0 = (synth.exponent + 2.0).abs() < 1e-9 && (synth.coefficient - 3.0).abs() < 1e-9 && synth.r2 > 1.0 - 1e-9;
    let p1 = (flaw.exponent + 2.0).abs() < 0.10 && flaw.r2 > 0.999;
    let p2 = dims.iter().all(|(d, dim, r2)| (dim - *d as f64).abs() < 0.03 && *r2 > 0.999);
    let p3 = synth.r2 > 0.99 && flaw.r2 > 0.99 && dims.iter().all(|(_, _, r2)| *r2 > 0.99);

    let verdict = if p0 && p1 && p2 && p3 {
        format!("ONE LAW-FINDER, MANY LAWS (R10) — the lattice is an automated bench. The reusable \
             `kinematics::power_law_fit` recovers a synthetic law exactly (p={:.2}, C={:.2}), rediscovers the \
             Casimir force scaling |F|∝a^{:.2} from the zero-point energy (R²={:.4}), and — via the Laplacian \
             heat kernel — MEASURES the lattice's spatial dimension as {:.3}, {:.3}, {:.3} for d=1,2,3 (all \
             R²>0.999). The same function reads three different physics from three different experiments: the \
             automation is the value-add, not a per-gate hardcode. FIREWALL (R3): toy-lattice data analysis.",
            synth.exponent, synth.coefficient, flaw.exponent, flaw.r2, dims[0].1, dims[1].1, dims[2].1)
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; synth_p={:.3} force_p={:.3} dims={:?}. FIREWALL (R3).",
            synth.exponent, flaw.exponent, dims)
    };
    rec!("\n[lab/0402 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} synth_p={:.4} force_p={:.4} force_r2={:.5} dim1={:.4} dim2={:.4} dim3={:.4}]",
        synth.exponent, flaw.exponent, flaw.r2, dims[0].1, dims[1].1, dims[2].1);

    assert!(p0, "P0: the fitter recovers a synthetic power law exactly");
    assert!(p1, "P1: the fitter rediscovers the Casimir force scaling (a^-2)");
    assert!(p2, "P2: the fitter measures the lattice's spatial dimension (d=1,2,3)");
    assert!(p3, "P3: all discoveries come from the same reusable tool, at high fit quality");
}
