//! lab/0304 — Warp-3.4: the four-source null — can orthogonal polarizations empty a volume?
//!
//! Tests the chapter-endgame conjecture ("~4 orthogonal polarizations null an area completely → a
//! negative-energy region") head-on. We superpose coherent monochromatic plane waves on the lattice and
//! read the time-averaged energy `⟨ρ⟩ = ¼(|Ê|²+|B̂|²)` off the engine's own `kinematics::em_energy`. The
//! physics says the conjecture is BACKWARDS:
//!   • orthogonally-polarized fields don't interfere — their energies ADD (no cross term), so orthogonality
//!     is the wrong tool for cancellation (P2);
//!   • a standing wave nulls E on planes but leaves ⟨ρ⟩ uniform (E-node = B-antinode) (P1);
//!   • the only superposition that empties a volume is the trivial one — parallel antiphase waves that zero
//!     the field EVERYWHERE (unique continuation for Maxwell) (P3).
//! A first-class negative (R5) that names the achievable alternative (a bounding current: Faraday/Huygens).
//!
//! Run: `cargo test -p uniforge --release --test uf3_4_four_source_null_gate -- --nocapture`
//!
//! FIREWALL (R3): coherent classical plane-wave superposition on a TOY lattice; ⟨ρ⟩=¼(|Ê|²+|B̂|²) via
//! `kinematics::em_energy`. Quantum vacuum NOT modelled. No device/spacetime claim. c=1, dimensionless.

use kinematics::em_energy;
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

type V3 = [f64; 3];
const N: usize = 24;
const LAMBDA: f64 = 8.0;

/// A coherent plane wave: real wavevector `k`, complex polarization amplitude `e_re + i e_im`, extra phase.
#[derive(Clone, Copy)]
struct Wave {
    k: V3,
    e_re: V3,
    e_im: V3,
    phase: f64,
}

fn cross(a: V3, b: V3) -> V3 {
    [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
}
fn khat(k: V3) -> V3 {
    let m = (k[0] * k[0] + k[1] * k[1] + k[2] * k[2]).sqrt();
    if m < 1e-12 { [0.0, 0.0, 0.0] } else { [k[0] / m, k[1] / m, k[2] / m] }
}

/// A plane wave from a propagation direction `dir` (magnitude ignored), polarization `e`, phase `ph`.
fn wave(dir: V3, e: V3, ph: f64) -> Wave {
    let k = khat(dir);
    let kmag = 2.0 * std::f64::consts::PI / LAMBDA;
    Wave { k: [k[0] * kmag, k[1] * kmag, k[2] * kmag], e_re: e, e_im: [0.0, 0.0, 0.0], phase: ph }
}

/// Total complex field (E_re,E_im,B_re,B_im) at position `x` from a set of waves. B̂ = k̂ × Ê.
fn field_at(x: V3, waves: &[Wave]) -> (V3, V3, V3, V3) {
    let (mut ere, mut eim, mut bre, mut bim) = ([0.0; 3], [0.0; 3], [0.0; 3], [0.0; 3]);
    for w in waves {
        let kd = w.k[0] * x[0] + w.k[1] * x[1] + w.k[2] * x[2] + w.phase;
        let (c, s) = (kd.cos(), kd.sin());
        let b_re = cross(khat(w.k), w.e_re);
        let b_im = cross(khat(w.k), w.e_im);
        for i in 0..3 {
            // (e_re + i e_im)(c + i s) = (e_re c − e_im s) + i(e_re s + e_im c)
            ere[i] += w.e_re[i] * c - w.e_im[i] * s;
            eim[i] += w.e_re[i] * s + w.e_im[i] * c;
            bre[i] += b_re[i] * c - b_im[i] * s;
            bim[i] += b_re[i] * s + b_im[i] * c;
        }
    }
    (ere, eim, bre, bim)
}

/// Time-averaged energy density ⟨ρ⟩ = ¼(|Ê|²+|B̂|²) = ½(em_energy(E_re,B_re)+em_energy(E_im,B_im)).
fn rho_avg(x: V3, waves: &[Wave]) -> f64 {
    let (ere, eim, bre, bim) = field_at(x, waves);
    0.5 * (em_energy(ere, bre) + em_energy(eim, bim))
}

/// Sample ⟨ρ⟩ over the whole grid + a central λ/2 cube; return (domain_mean, cube_mean, center, cov, max, min).
fn scan(waves: &[Wave]) -> (f64, f64, f64, f64, f64, f64) {
    let c = (N as f64 - 1.0) / 2.0; // domain center
    let half = LAMBDA / 4.0; // cube half-side = λ/4 → side λ/2
    let (mut sum, mut sq, mut n) = (0.0, 0.0, 0.0);
    let (mut csum, mut cn) = (0.0, 0.0);
    let (mut mx, mut mn) = (f64::MIN, f64::MAX);
    for iz in 0..N {
        for iy in 0..N {
            for ix in 0..N {
                let x = [ix as f64, iy as f64, iz as f64];
                let r = rho_avg(x, waves);
                sum += r;
                sq += r * r;
                n += 1.0;
                mx = mx.max(r);
                mn = mn.min(r);
                if (x[0] - c).abs() <= half && (x[1] - c).abs() <= half && (x[2] - c).abs() <= half {
                    csum += r;
                    cn += 1.0;
                }
            }
        }
    }
    let mean = sum / n;
    let var = (sq / n - mean * mean).max(0.0);
    let cov = if mean.abs() > 1e-12 { var.sqrt() / mean } else { 0.0 };
    let center = rho_avg([c, c, c], waves);
    (mean, csum / cn, center, cov, mx, mn)
}

// ---- configs ----
fn x_() -> V3 { [1.0, 0.0, 0.0] }
fn y_() -> V3 { [0.0, 1.0, 0.0] }
fn z_() -> V3 { [0.0, 0.0, 1.0] }

fn cfg_single() -> Vec<Wave> {
    vec![wave(z_(), x_(), 0.0)]
}
fn cfg_standing() -> Vec<Wave> {
    // counter-propagating, PARALLEL polarization (x̂): E-nodes on planes, energy uniform.
    vec![wave(z_(), x_(), 0.0), wave([0.0, 0.0, -1.0], x_(), 0.0)]
}
/// Three perpendicular standing-wave pairs — the "orthogonal polarization" set. Per-pair phases pa,pb,pc.
fn cfg_ortho(pa: f64, pb: f64, pc: f64) -> Vec<Wave> {
    vec![
        wave(z_(), x_(), pa),
        wave([0.0, 0.0, -1.0], x_(), pa), // pair A: ±ẑ, x̂
        wave(x_(), y_(), pb),
        wave([-1.0, 0.0, 0.0], y_(), pb), // pair B: ±x̂, ŷ
        wave(y_(), z_(), pc),
        wave([0.0, -1.0, 0.0], z_(), pc), // pair C: ±ŷ, ẑ
    ]
}
fn cfg_antiphase() -> Vec<Wave> {
    // parallel, CO-propagating, antiphase → cancels the field everywhere (the trivial volume null).
    vec![wave(z_(), x_(), 0.0), wave(z_(), x_(), std::f64::consts::PI)]
}

#[test]
fn uf3_4_four_source_null_gate() {
    rec!("\n######## lab/0304 — Warp-3.4: the four-source null — can orthogonal polarizations empty a volume? ########");
    rec!("FIREWALL (R3): coherent plane-wave superposition on a TOY lattice; ⟨ρ⟩=¼(|Ê|²+|B̂|²) via kinematics::em_energy.");
    rec!("  N={N} λ={LAMBDA} (domain = {:.0}λ). Quantum vacuum NOT modelled. c=1.\n", N as f64 / LAMBDA);

    // P0 — single traveling wave: uniform energy
    let (m0, cube0, cen0, cov0, mx0, mn0) = scan(&cfg_single());
    let res0 = cube0 / m0;

    // P1 — standing wave (parallel pol): E-nodes but uniform energy
    let (m1, cube1, cen1, cov1, mx1, mn1) = scan(&cfg_standing());
    let res1 = cube1 / m1;

    // P2 — orthogonal-polarization set: phase-independent, additive, cannot null
    let base = cfg_ortho(0.0, 0.0, 0.0);
    let (m2, cube2, cen2, cov2, _mx2, _mn2) = scan(&base);
    let res2 = cube2 / m2;
    // phase sweep: vary all three pair phases; center ⟨ρ⟩ must stay constant
    rec!("[P2] orthogonal-pol phase sweep — center ⟨ρ⟩ vs (pa,pb,pc):");
    let mut sweep = Vec::new();
    let (mut smin, mut smax) = (f64::MAX, f64::MIN);
    for i in 0..=8 {
        let t = std::f64::consts::PI * i as f64 / 4.0;
        let cen = scan(&cfg_ortho(t, 0.7 * t, 1.9 * t)).2;
        smin = smin.min(cen);
        smax = smax.max(cen);
        rec!("   t={:.2}π | center ⟨ρ⟩={cen:.6}", i as f64 / 4.0);
        sweep.push((i as f64 / 4.0, cen));
    }
    let sweep_mean = sweep.iter().map(|s| s.1).sum::<f64>() / sweep.len() as f64;
    let sweep_cov = if sweep_mean.abs() > 1e-12 {
        (sweep.iter().map(|s| (s.1 - sweep_mean).powi(2)).sum::<f64>() / sweep.len() as f64).sqrt() / sweep_mean
    } else {
        0.0
    };
    // "sum of the parts": each pair alone contributes its own energy; three pairs → 3× a single pair's center.
    let one_pair = scan(&[base[0], base[1]]).2;
    let sum_of_parts = 3.0 * one_pair;
    let additivity_err = (cen2 - sum_of_parts).abs() / sum_of_parts;

    // P3 — parallel antiphase (trivial global null)
    let (m3, _cube3, _cen3, _cov3, mx3, mn3) = scan(&cfg_antiphase());

    rec!("\n[P0] single wave: cube residual={res0:.4} (want ~1), CoV={cov0:.2e} (want <1%) [mean={m0:.3} min={mn0:.3} max={mx0:.3}]");
    rec!("[P1] standing (parallel pol): cube residual={res1:.4} (want ~1), CoV={cov1:.2e} (want <2%) — E-nodes, but energy UNIFORM [center={cen1:.3}]");
    rec!("[P2] orthogonal-pol set: cube residual={res2:.4} (want >0.8), CoV(space)={cov2:.2e}, center={cen2:.4}");
    rec!("     phase-sweep center CoV={sweep_cov:.2e} (want <0.1% — phase-INDEPENDENT), min={smin:.4} max={smax:.4}");
    rec!("     center vs sum-of-parts: {cen2:.4} vs {sum_of_parts:.4} (err {additivity_err:.2e}, want <1% — energies ADD)");
    rec!("[P3] parallel antiphase: max ⟨ρ⟩={mx3:.2e} (want <1e-9 — field zero EVERYWHERE) [min={mn3:.2e} mean={m3:.2e}]");

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-3-shield/0304-four-source-null/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let configs = format!(
        "config,cube_residual,center_rho,domain_mean,cov,max_rho,min_rho\n\
         single,{res0:.6},{cen0:.6},{m0:.6},{cov0:.6},{mx0:.6},{mn0:.6}\n\
         standing_1pol,{res1:.6},{cen1:.6},{m1:.6},{cov1:.6},{mx1:.6},{mn1:.6}\n\
         orthogonal_3pair,{res2:.6},{cen2:.6},{m2:.6},{cov2:.6},{cen2:.6},{cen2:.6}\n\
         parallel_antiphase,{:.6},{:.6},{m3:.9},{:.6},{mx3:.9},{mn3:.9}\n",
        0.0_f64, 0.0_f64, 0.0_f64
    );
    std::fs::write(format!("{dir}/null_configs.csv"), configs).expect("write null_configs.csv");
    let mut ph = String::from("t_over_pi,center_rho\n");
    for (t, cen) in &sweep {
        ph.push_str(&format!("{t:.4},{cen:.6}\n"));
    }
    std::fs::write(format!("{dir}/phase_sweep.csv"), ph).expect("write phase_sweep.csv");
    // radial profile out from center along the diagonal — the ortho set (flat) vs single (flat) show no null
    let c = (N as f64 - 1.0) / 2.0;
    let mut rad = String::from("r,ortho_rho,standing_rho\n");
    let sqrt3 = 3.0_f64.sqrt();
    for i in 0..=40 {
        let d = i as f64 * 0.2;
        let x = [c + d / sqrt3, c + d / sqrt3, c + d / sqrt3];
        rad.push_str(&format!("{d:.3},{:.6},{:.6}\n", rho_avg(x, &base), rho_avg(x, &cfg_standing())));
    }
    std::fs::write(format!("{dir}/radial.csv"), rad).expect("write radial.csv");

    // verdicts
    let p0 = cov0 < 0.01 && (0.98..=1.02).contains(&res0);
    let p1 = cov1 < 0.02 && (0.95..=1.05).contains(&res1);
    let p2 = sweep_cov < 0.001 && additivity_err < 0.01 && res2 > 0.8;
    let p3 = mx3 < 1e-9;

    let verdict = if p0 && p1 && p2 && p3 {
        format!("THE CONJECTURE IS BACKWARDS (R5) — orthogonal polarizations CANNOT empty a volume. A single \
             wave carries uniform energy (control). A standing wave nulls E on planes but leaves ⟨ρ⟩ UNIFORM \
             (residual {res1:.2}) — the E-node is a B-antinode, energy just sloshes. The 'orthogonal \
             polarization' set is the decisive test: its energy is phase-INDEPENDENT (sweep CoV {sweep_cov:.0e}) \
             and equals the SUM of the parts ({cen2:.2} = 3×{one_pair:.2}, err {additivity_err:.0e}) — \
             orthogonal fields don't interfere, so they can't cancel; the cube stays full (residual {res2:.2}). \
             The only superposition that empties a volume is the trivial one: parallel antiphase waves that \
             zero the field EVERYWHERE (max ⟨ρ⟩ {mx3:.0e}) — no field, no shield (unique continuation). A \
             complete null needs a BOUNDARY of real currents (Faraday/Huygens), and even then EM ρ≥0 (rung \
             2.4) → a null is ZERO, never negative. FIREWALL (R3): toy Huygens/EM optics.")
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; res0={res0:.3} res1={res1:.3} res2={res2:.3} \
             sweepCoV={sweep_cov:.1e} addErr={additivity_err:.1e} maxAntiphase={mx3:.1e}. FIREWALL (R3).")
    };
    rec!("\n[lab/0304 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} res0={res0:.4} res1={res1:.4} res2={res2:.4} sweep_cov={sweep_cov:.3e} add_err={additivity_err:.3e} center2={cen2:.4} sum_parts={sum_of_parts:.4} max_antiphase={mx3:.3e}]");

    assert!(p0, "P0: a single traveling wave carries spatially uniform energy");
    assert!(p1, "P1: a standing wave nulls E on planes but leaves the energy uniform (no energy null)");
    assert!(p2, "P2: orthogonal polarizations ADD (phase-independent, sum-of-parts) — they cannot null");
    assert!(p3, "P3: the only volume null from superposition is the trivial field-zero-everywhere case");
}
