//! lab/dna-thz/0001 — rung 1: dielectric shift law Ω ∝ ε_r^p
//!
//! Does the steady-state resonant peak of the driven lattice follow a power law in the inclusion's
//! star0 weight ε_r? Is the exponent consistent with the naive −1/2 expected from uniform
//! mass/permittivity scaling?
//!
//! Run: `cargo test -p uniforge --release --test uf6_1_thz_shift_law_gate -- --nocapture`
//!
//! FIREWALL (R3): toy DEC 1-form wave on a 16×8×8 tet lattice. ε_r is a dimensionless star0 scale
//! factor, not a physical permittivity. Ω is a dimensionless drive frequency. The fitted exponent p is
//! an empirical lattice-law, not a physical constant. No claim about real THz frequencies, DNA,
//! cells, or SI material properties. c=1 (code units).

use kinematics::discover::power_law_fit;
use std::io::Write;
use testkit::mesh_setup::tet_wave_geometric;
use uniforge::wave_solver::MeshEdgePotential;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

// ── lattice geometry ───────────────────────────────────────────────────────
const NX: usize = 16;
const NY: usize = 8;
const NZ: usize = 8;
const C: f64 = 1.0;
// Restrict sweep to the driven-mode band; avoids the low-frequency box-mode artifact.
const N_FREQ: usize = 40;
const OMEGA_LO: f64 = 0.20;
const OMEGA_HI: f64 = 0.80;
const N_SETTLE: usize = 400;
const N_MEAS: usize = 300;
const GAMMA: f64 = 0.04;
const EPS_CASES: &[f64] = &[1.0, 4.0, 9.0, 16.0, 25.0, 36.0, 49.0];

fn vid(i: usize, j: usize, k: usize) -> usize {
    i * (NY + 1) * (NZ + 1) + j * (NZ + 1) + k
}


fn find_x_edge(mesh: &uniforge::mesh::SimplicialComplex, i: usize, j: usize, k: usize) -> usize {
    let v0 = vid(i, j, k);
    let v1 = vid(i + 1, j, k);
    for (e, row) in mesh.d0_sparse.iter().enumerate() {
        let vs: Vec<usize> = row.iter().map(|&(v, _)| v).collect();
        if vs.contains(&v0) && vs.contains(&v1) {
            return e;
        }
    }
    panic!("x-edge ({i},{j},{k})→({},{j},{k}) not found", i + 1)
}

fn sweep(eps_r: f64) -> Vec<(f64, f64)> {
    let mut solver = tet_wave_geometric(NX, NY, NZ);

    if (eps_r - 1.0).abs() > 1e-6 {
        let ci = NX / 2;
        let cj = NY / 2;
        let ck = NZ / 2;
        let nv = (NX + 1) * (NY + 1) * (NZ + 1);
        let mut w = vec![1.0f64; nv];
        for i in ci.saturating_sub(2)..=(ci + 2).min(NX) {
            for j in cj.saturating_sub(1)..=(cj + 1).min(NY) {
                for k in ck.saturating_sub(1)..=(ck + 1).min(NZ) {
                    w[vid(i, j, k)] = eps_r;
                }
            }
        }
        solver.scale_star0(&w);
    }

    let ci = NX / 2;
    let cj = NY / 2;
    let ck = NZ / 2;
    let feed_edge = find_x_edge(solver.mesh(), ci - 1, cj, ck);
    let probe_edge = find_x_edge(solver.mesh(), ci + 3, cj, ck);
    let n_edges = solver.mesh().num_k_forms(1);
    let dt = 0.4 / C;

    let mut results = Vec::with_capacity(N_FREQ);
    for fi in 0..N_FREQ {
        let omega = OMEGA_LO + (OMEGA_HI - OMEGA_LO) * (fi as f64) / (N_FREQ as f64 - 1.0);
        let mut a = MeshEdgePotential { a_e: vec![0.0; n_edges] };
        let mut v = MeshEdgePotential { a_e: vec![0.0; n_edges] };
        let mut rms_acc = 0.0f64;
        for step in 0..(N_SETTLE + N_MEAS) {
            let t = step as f64 * dt;
            let mut src = MeshEdgePotential { a_e: vec![0.0; n_edges] };
            src.a_e[feed_edge] = (omega * t).sin();
            let (a_next, v_next) =
                solver.evolve_wave_equation_with_source(&a, &v, C, dt, GAMMA, &src);
            a = a_next;
            v = v_next;
            if step >= N_SETTLE {
                rms_acc += a.a_e[probe_edge] * a.a_e[probe_edge];
            }
        }
        results.push((omega, (rms_acc / N_MEAS as f64).sqrt()));
    }
    results
}

fn peak_omega(sweep: &[(f64, f64)]) -> f64 {
    sweep
        .iter()
        .max_by(|a, b| a.1.partial_cmp(&b.1).unwrap())
        .map(|&(o, _)| o)
        .unwrap_or(0.0)
}

#[test]
fn uf6_1_thz_shift_law_gate() {
    rec!("\n######## dna-thz/0001 — rung 1: dielectric shift law ########");
    rec!("FIREWALL (R3): toy DEC 1-form wave on a {}x{}x{} tet lattice.", NX, NY, NZ);
    rec!("  ε_r = dimensionless star0 scale. Ω = dimensionless drive frequency.");
    rec!("  Fitted p is a lattice-law, not a physical exponent. c=1.\n");

    let data_dir = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/dna-thz/0001-dna-permittivity-shift-law/data"
    );
    std::fs::create_dir_all(data_dir).expect("create data dir");

    let mut csv = String::from("eps_r,peak_omega\n");
    let mut eps_vec: Vec<f64> = Vec::new();
    let mut peak_vec: Vec<f64> = Vec::new();

    for &eps in EPS_CASES {
        rec!("  Sweeping ε_r = {eps:.0} ...");
        let s = sweep(eps);
        let pk = peak_omega(&s);
        eps_vec.push(eps);
        peak_vec.push(pk);
        csv.push_str(&format!("{eps:.1},{pk:.6}\n"));
        rec!("    peak Ω = {pk:.4}");
    }

    std::fs::write(format!("{data_dir}/shift_law.csv"), &csv).expect("write shift_law.csv");

    let law = power_law_fit(&eps_vec, &peak_vec);
    let bare_peak = peak_vec[0];

    // ── scorecard ──────────────────────────────────────────────────────────
    rec!("\n  ε_r      peak Ω     shift vs bare");
    for (i, &eps) in EPS_CASES.iter().enumerate() {
        let pk = peak_vec[i];
        let shift = (pk - bare_peak) / bare_peak * 100.0;
        rec!("  {eps:>5.0}    {pk:.4}     {shift:+.2}%");
    }

    rec!("\n  Power-law fit Ω = C · ε_r^p:");
    rec!("    p  = {:.4}  (pre-registered target: -0.5000)", law.exponent);
    rec!("    C  = {:.4}", law.coefficient);
    rec!("    R² = {:.4}", law.r2);

    let p0 = bare_peak > OMEGA_LO && bare_peak < OMEGA_HI;
    let p1 = law.r2 > 0.95;
    let p2 = law.exponent < -0.10;
    // P3 is an R5 NEGATIVE lock (#119). The pre-registered naive √ε_r law (p = -1/2) is FALSIFIED
    // for this small-inclusion geometry, and that falsification IS the rung's result (eval.md:
    // NEGATIVE, clean power law p ≈ -0.28). So the gate asserts the negative — √ε_r refuted AND the
    // emergent exponent held at its measured value — rather than asserting the refuted prediction
    // (which kept the workspace suite permanently red on main). `p` reproduces bit-stable.
    const P_MEASURED: f64 = -0.2753; // emergent exponent, run 7fdb4c3
    let sqrt_law_falsified = (law.exponent + 0.5).abs() > 0.10;
    let exponent_locked = (law.exponent - P_MEASURED).abs() < 0.02;
    let p3 = sqrt_law_falsified && exponent_locked;

    rec!("\n  P0 bare peak inside restricted band ({OMEGA_LO},{OMEGA_HI}): {}", if p0 { "PASS" } else { "FAIL" });
    rec!("  P1 power-law fit R² > 0.95: {}", if p1 { "PASS" } else { "FAIL" });
    rec!("  P2 exponent p < -0.10 (downward shift): {}", if p2 { "PASS" } else { "FAIL" });
    rec!(
        "  P3 (R5 negative) √ε_r FALSIFIED |p+1/2|={:.4}>0.10 AND exponent locked |p-({:.4})|={:.4}<0.02: {}",
        (law.exponent + 0.5).abs(),
        P_MEASURED,
        (law.exponent - P_MEASURED).abs(),
        if p3 { "PASS" } else { "FAIL" }
    );

    rec!(
        "\n  VERDICT: clean power law Ω ∝ ε_r^p with p = {:.4} — the naive √ε_r law is FALSIFIED for this \
         small-inclusion geometry (R5 negative, locked into the gate; see #119).",
        law.exponent
    );
    rec!("  FIREWALL: toy lattice-law only — no claim about real dielectrics or SI frequencies.\n");

    assert!(p0, "P0 FAIL: bare peak {bare_peak:.4} outside restricted band [{OMEGA_LO},{OMEGA_HI}]");
    assert!(p1, "P1 FAIL: R² = {:.4} < 0.95", law.r2);
    assert!(p2, "P2 FAIL: p = {:.4} is not negative enough", law.exponent);
    assert!(
        p3,
        "P3 FAIL (R5 negative not held): expected √ε_r falsified (|p+1/2|>0.10) AND p≈{:.4} (|Δ|<0.02); got p = {:.4}",
        P_MEASURED, law.exponent
    );
}
