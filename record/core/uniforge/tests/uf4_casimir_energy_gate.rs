//! lab/0400 — Warp-4.0: the Casimir vacuum is negative — and the lattice discovers the law.
//!
//! Chapters 2–3 showed classical fields can't source the warp wall's negative energy and a shield only
//! reaches zero. The one mechanism that genuinely gives ρ<0 is the QUANTUM VACUUM with boundaries — the
//! Casimir effect. We build it as the zero-point energy E₀ = ½Σℏωₖ of a toy scalar field on a fixed–fixed
//! lattice chain (the engine's 1-D Dirichlet Laplacian d†d; ωₖ² are its eigenvalues). The lattice spectrum
//! is its own UV cutoff, so E₀ is finite with NO zeta regularization; subtracting the bulk vacuum leaves a
//! genuinely NEGATIVE confined energy.
//!
//! This is also the chapter's automation proof: the gate does not check a hardcoded number — it SWEEPS the
//! plate separation, least-squares-fits E_C(a)=c₀+c₁/a, and DISCOVERS the surface term (c₀→−½) and the
//! Casimir coefficient (c₁→−π/24), then holds them against theory. The lattice runs the experiment; the
//! automation extracts and checks the law.
//!
//! Run: `cargo test -p uniforge --release --test uf4_casimir_energy_gate -- --nocapture`
//!
//! FIREWALL (R3): zero-point energy ½Σℏωₖ of a TOY scalar field (fixed–fixed chain = Dirichlet Laplacian)
//! on a TOY lattice. ℏ dimensionless; standard QFT bookkeeping, NOT a real device/spacetime/free energy. c=1.

use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

/// Mode frequencies of the fixed–fixed chain of `n` interior sites: ωₖ = 2 sin(kπ/2(n+1)),
/// k=1..n — the closed-form spectrum of the 1-D Dirichlet Laplacian (ωₖ² = its eigenvalues).
fn omegas(n: usize) -> Vec<f64> {
    (1..=n).map(|k| 2.0 * (k as f64 * std::f64::consts::PI / (2.0 * (n as f64 + 1.0))).sin()).collect()
}

/// Zero-point energy E₀ = ½ Σ ωₖ.
fn e0(n: usize) -> f64 {
    0.5 * omegas(n).iter().sum::<f64>()
}

/// Bulk vacuum density per unit length: ε∞ = (1/π)∫₀^π sin(q/2) dq = 2/π.
const EPS_INF: f64 = std::f64::consts::FRAC_2_PI; // 2/π

/// Confined (Casimir) energy at plate separation `a` (= n+1 sites of length): E_C = E₀(n) − ε∞·a.
fn e_confined(a: usize) -> f64 {
    let n = a - 1;
    e0(n) - EPS_INF * a as f64
}

/// Two-parameter least-squares fit E_C(a) = c₀ + c₁·(1/a). Returns (c₀, c₁, R²).
fn fit_c0_c1(xs: &[f64], ys: &[f64]) -> (f64, f64, f64) {
    let m = xs.len() as f64;
    let inv: Vec<f64> = xs.iter().map(|a| 1.0 / a).collect();
    let (s1, su, suu) = (m, inv.iter().sum::<f64>(), inv.iter().map(|u| u * u).sum::<f64>());
    let sy = ys.iter().sum::<f64>();
    let suy: f64 = inv.iter().zip(ys).map(|(u, y)| u * y).sum();
    // [s1 su; su suu][c0;c1] = [sy; suy]
    let det = s1 * suu - su * su;
    let c0 = (suu * sy - su * suy) / det;
    let c1 = (s1 * suy - su * sy) / det;
    let mean = sy / m;
    let ss_tot: f64 = ys.iter().map(|y| (y - mean).powi(2)).sum();
    let ss_res: f64 = xs.iter().zip(ys).map(|(a, y)| (y - (c0 + c1 / a)).powi(2)).sum();
    (c0, c1, 1.0 - ss_res / ss_tot)
}

/// Slope of a simple linear regression y = m·x + b (returns m) — used to DISCOVER the power-law exponent.
fn slope(xs: &[f64], ys: &[f64]) -> f64 {
    let m = xs.len() as f64;
    let (sx, sy) = (xs.iter().sum::<f64>(), ys.iter().sum::<f64>());
    let sxy: f64 = xs.iter().zip(ys).map(|(x, y)| x * y).sum();
    let sxx: f64 = xs.iter().map(|x| x * x).sum();
    (m * sxy - sx * sy) / (m * sxx - sx * sx)
}

#[test]
fn uf4_casimir_energy_gate() {
    let casimir_coeff = -std::f64::consts::PI / 24.0; // the 1+1D Dirichlet Casimir coefficient
    rec!("\n######## lab/0400 — Warp-4.0: the Casimir vacuum is negative — the lattice discovers the law ########");
    rec!("FIREWALL (R3): zero-point energy ½Σℏωₖ of a TOY scalar field (fixed–fixed chain = Dirichlet Laplacian).");
    rec!("  Lattice = its own UV cutoff (no zeta). ε∞={EPS_INF:.6} (2/π). Target Casimir coeff −π/24={casimir_coeff:.6}. c=1.\n");

    // P0 — the spectrum IS the engine's Dirichlet Laplacian (match two spectral moments to the trace).
    let n = 15usize;
    let w = omegas(n);
    let m2: f64 = w.iter().map(|o| o * o).sum(); // Σωₖ² = tr Δ  = 2N
    let m4: f64 = w.iter().map(|o| o.powi(4)).sum(); // Σωₖ⁴ = tr Δ² = 6N−2
    let tr1 = 2.0 * n as f64;
    let tr2 = 6.0 * n as f64 - 2.0;
    rec!("[P0] spectrum vs Laplacian (n={n}): Σωₖ²={m2:.9} (tr Δ={tr1}), Σωₖ⁴={m4:.9} (tr Δ²={tr2})");

    // Sweep the plate separation and record the confined vacuum energy.
    let seps: [usize; 7] = [8, 12, 16, 24, 32, 48, 64];
    rec!("\n[sweep] plate separation a → confined vacuum energy E_C(a):");
    let (mut xs, mut ys) = (Vec::new(), Vec::new());
    for &a in &seps {
        let ec = e_confined(a);
        rec!("   a={a:>3} | E₀={:.5} | E_C={ec:.6} | E_C·a={:.5}", e0(a - 1), ec * a as f64);
        xs.push(a as f64);
        ys.push(ec);
    }
    let all_negative = ys.iter().all(|&y| y < 0.0);
    let monotone = ys.windows(2).all(|w| w[1] > w[0]); // E_C rises toward the bulk as a grows

    // P2 — the lattice DISCOVERS the law: fit E_C(a) = c₀ + c₁/a.
    let (c0, c1, r2) = fit_c0_c1(&xs, &ys);
    // discovered exponent: log|E_C − c₀| vs log a → slope ≈ −1
    let logx: Vec<f64> = xs.iter().map(|a| a.ln()).collect();
    let logy: Vec<f64> = ys.iter().map(|y| (y - c0).abs().ln()).collect();
    let exponent = slope(&logx, &logy);
    let coeff_err = (c1 - casimir_coeff).abs() / casimir_coeff.abs();
    rec!("\n[P2] DISCOVERED law  E_C(a) = c₀ + c₁/a :");
    rec!("     c₀ (surface) = {c0:.6}   (theory −0.5)");
    rec!("     c₁ (Casimir) = {c1:.6}   (theory −π/24 = {casimir_coeff:.6}, err {coeff_err:.2}%→{:.3}%)", coeff_err * 100.0);
    rec!("     R² = {r2:.8}   discovered exponent (log-log slope) = {exponent:.4}  (theory −1)");

    rec!("\n[P1] E_C(a) < 0 for all a: {all_negative}");
    rec!("[P3] E_C(a) strictly increasing in a (attractive): {monotone}");

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-4-vacuum/0400-casimir-negative-energy/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let mut spec = String::from("k,omega\n");
    for (k, o) in w.iter().enumerate() {
        spec.push_str(&format!("{},{o:.6}\n", k + 1));
    }
    std::fs::write(format!("{dir}/spectrum.csv"), spec).expect("write spectrum.csv");
    let mut sweep = String::from("a,e0,e_confined,ec_times_a\n");
    for &a in &seps {
        sweep.push_str(&format!("{a},{:.6},{:.6},{:.6}\n", e0(a - 1), e_confined(a), e_confined(a) * a as f64));
    }
    std::fs::write(format!("{dir}/energy_sweep.csv"), sweep).expect("write energy_sweep.csv");
    let fit = format!(
        "metric,value,theory\nc0_surface,{c0:.6},-0.5\nc1_casimir,{c1:.6},{casimir_coeff:.6}\n\
         r_squared,{r2:.8},1.0\nexponent,{exponent:.6},-1.0\ncoeff_err_frac,{coeff_err:.6},0.0\n"
    );
    std::fs::write(format!("{dir}/fit.csv"), fit).expect("write fit.csv");

    // verdicts
    let p0 = (m2 - tr1).abs() < 1e-9 && (m4 - tr2).abs() < 1e-9;
    let p1 = all_negative;
    let p2 = r2 > 0.999 && (c0 + 0.5).abs() < 0.02 && coeff_err < 0.03;
    let p3 = monotone;

    let verdict = if p0 && p1 && p2 && p3 {
        format!("THE VACUUM GOES NEGATIVE — AND THE LATTICE FINDS THE LAW ITSELF (R10). The confined zero-point \
             energy of the toy field is negative at every plate separation (bulk-subtracted), and an automated \
             two-parameter fit of the swept data DISCOVERS the Casimir law: E_C(a) = c₀ + c₁/a with the surface \
             term c₀={c0:.3} (theory −0.5) and the Casimir coefficient c₁={c1:.4} — within {:.1}% of the exact \
             1+1D value −π/24={casimir_coeff:.4} — at R²={r2:.5}, discovered exponent {exponent:.2} (theory −1). \
             The spectrum matches the engine's Dirichlet Laplacian to two trace moments. So the quantum vacuum \
             is the one place ρ<0 is real, the lattice reproduces it with no zeta trick (it is its own \
             regulator), and the bench AUTO-EXTRACTS the physical law — the value-add. FIREWALL (R3): toy \
             zero-point bookkeeping; not a device, not free energy.", coeff_err * 100.0)
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; c0={c0:.4} c1={c1:.4} (−π/24={casimir_coeff:.4}, err {:.1}%) R²={r2:.5} exp={exponent:.3} allneg={all_negative} mono={monotone}. FIREWALL (R3).", coeff_err * 100.0)
    };
    rec!("\n[lab/0400 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} c0={c0:.5} c1={c1:.5} coeff_err={coeff_err:.5} r2={r2:.6} exponent={exponent:.4} m2={m2:.3} m4={m4:.3}]");

    assert!(p0, "P0: the mode spectrum matches the engine's Dirichlet Laplacian (two trace moments)");
    assert!(p1, "P1: the confined vacuum energy is negative at every plate separation");
    assert!(p2, "P2: the lattice discovers the Casimir law (1/a, coefficient −π/24) by least-squares fit");
    assert!(p3, "P3: the Casimir energy deepens as the plates approach (attractive)");
}
