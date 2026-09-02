//! lab/0117 — Warp-1.7: the discovery bench recovers `ω = c·k` blind, in five directions at once.
//!
//! **What.** Rung 1.6/1.6b measured the lattice dispersion along **z only** (a z-periodic mesh, the
//! transverse-constant plane wave keeping the open x,y boundaries out of the Rayleigh quotient).
//! #46's dispersion task wants the full statement — `ω = c·k`, discovered blind, **and isotropic**.
//! This gate sweeps `ω(|k|)` on a **fully periodic 3-torus** (`mesh_3d_tetrahedral_grid_periodic`,
//! seam-correct `unfolded_scalar_stars` — on a 3-torus every axis has a seam, #177/#153-Stage-2)
//! along `[100]`, `[010]`, `[001]`, `[110]`, `[111]`, and hands the raw `(|k|, ω)` pairs to
//! `kinematics::select_power_law` (answer-free model selection over a fixed menu of candidate laws)
//! and `kinematics::power_law_fit` (free exponent).
//!
//! **Why blind is checkable.** `discover_law` below is the ONLY path from swept data to a stated
//! law, and its whole signature is `(&[f64], &[f64]) -> Discovery` — there is no parameter through
//! which an expected exponent could enter. The menu `CANDIDATES` is a standard physics menu
//! (flat / diffusive / linear / 3-2 / quadratic / cubic), registered before the run; the winner is
//! whichever the data's own log-space `R²` prefers. Every assertion reads the *returned* law.
//!
//! **P0's answer key.** On this mesh the geometric ⋆ gives `⋆₁ = 1` on axis edges and EXACTLY `0`
//! on every diagonal edge (rung 3.5's `cot 90° = 0`, in 3-D), so `Δ₀` here IS the 7-point
//! simple-cubic stencil with the closed-form symbol `Σ_a (2 − 2 cos k_a)`. P0 checks the machinery
//! against that absolute key (#153's rule); P1–P4 are the discovery and its honesty arms.
//!
//! Run: `cargo test -p uniforge --release --test uf1_7_dispersion_isotropy_gate -- --nocapture`
//!
//! FIREWALL (R3): a toy DEC scalar wave on a tetrahedral 3-torus. `ω`, `k`, "dispersion",
//! "light cone", "speed", "isotropy" name numerical properties of the discrete operator
//! `Δ₀ = ⋆₀⁻¹D₀ᵀ⋆₁D₀` and of least-squares fits to its Rayleigh quotients — never a real photon,
//! a real light cone, or a measurement of `c`. The prediction-grade quantities are the dimensionless
//! exponent and the dimensionless anisotropy ratio; the fitted coefficient is an emergent lattice
//! wave speed in code units. `c = 1` in code units only. Nothing here is a claim about nature.

use dec::operators::apply_laplacian_0_metric;
use kinematics::{power_law_fit, select_power_law};
use solve::bloch::{unfolded_scalar_stars, Lattice};
use std::io::Write;
use uniforge::mesh::mesh_3d_tetrahedral_grid_periodic;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

/// Torus size (registered): 64³ vertices, 6·64³ tets, unit spacing.
const N: usize = 64;
/// Long-wavelength window (registered): between `π/3` and the next `[100]` mode, so every direction
/// keeps ≥ 6 modes and the halved window keeps ≥ 3.
const K_CUT: f64 = 1.05;

/// The five probed directions. `k_m = (2π m / N)·n` is exactly commensurate with the torus for every
/// integer `m`, so `cos(k·x)` is a genuine periodic field on the mesh.
const DIRS: [([i32; 3], &str); 5] = [
    ([1, 0, 0], "100"),
    ([0, 1, 0], "010"),
    ([0, 0, 1], "001"),
    ([1, 1, 0], "110"),
    ([1, 1, 1], "111"),
];

/// The candidate menu handed to the model selector — a standard physics menu, registered before the
/// run: flat/gapped, diffusive, **linear/lightlike**, 3/2, quadratic/massive-like, cubic. Nothing
/// here tells the selector which one to prefer.
const CANDIDATES: [f64; 6] = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0];

/// What the bench states after looking at one direction's sweep. Built by [`discover_law`] from the
/// data ALONE.
struct Discovery {
    /// exponent of the candidate the data selected (an element of `CANDIDATES`)
    selected_exponent: f64,
    /// the selected candidate's log-space `R²`
    selected_r2: f64,
    /// its `R²` margin over the runner-up
    margin: f64,
    /// free-exponent fit: the discovered exponent
    exponent: f64,
    /// free-exponent fit: the discovered coefficient (an emergent lattice speed, code units)
    coefficient: f64,
    /// free-exponent fit: log-space `R²`
    r2: f64,
}

/// **The only path from swept data to a stated law.** Signature is `(xs, ys) -> Discovery`: no
/// expected exponent, target, tolerance or direction label can enter here. Blindness is structural,
/// not a promise.
fn discover_law(xs: &[f64], ys: &[f64]) -> Discovery {
    let sel = select_power_law(xs, ys, &CANDIDATES);
    let free = power_law_fit(xs, ys);
    Discovery {
        selected_exponent: sel.law.exponent,
        selected_r2: sel.law.r2,
        margin: sel.margin,
        exponent: free.exponent,
        coefficient: free.coefficient,
        r2: free.r2,
    }
}

fn rayleigh(
    mesh: &geom::mesh::SimplicialComplex,
    star0: &[f64],
    star1: &[f64],
    phi: &[f64],
) -> f64 {
    let a = apply_laplacian_0_metric(mesh, star0, star1, phi);
    let num: f64 = phi.iter().zip(&a).map(|(p, av)| p * av).sum();
    let den: f64 = phi.iter().map(|p| p * p).sum();
    num / den
}

/// One directional sweep: `(|k|, ω, λ)` for `m = 1,2,…` while `|k| ≤ k_max`.
fn direction_sweep(
    mesh: &geom::mesh::SimplicialComplex,
    coords: &[[f64; 3]],
    star0: &[f64],
    star1: &[f64],
    nvec: [i32; 3],
    k_max: f64,
) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let tau = std::f64::consts::TAU;
    let norm = ((nvec[0] * nvec[0] + nvec[1] * nvec[1] + nvec[2] * nvec[2]) as f64).sqrt();
    let (mut ks, mut ws, mut lams) = (Vec::new(), Vec::new(), Vec::new());
    for m in 1..=256usize {
        let kmag = tau * m as f64 * norm / N as f64;
        if kmag > k_max {
            break;
        }
        let kv = [
            tau * m as f64 * nvec[0] as f64 / N as f64,
            tau * m as f64 * nvec[1] as f64 / N as f64,
            tau * m as f64 * nvec[2] as f64 / N as f64,
        ];
        let phi: Vec<f64> =
            coords.iter().map(|p| (kv[0] * p[0] + kv[1] * p[1] + kv[2] * p[2]).cos()).collect();
        let lam = rayleigh(mesh, star0, star1, &phi);
        ks.push(kmag);
        ws.push(lam.max(0.0).sqrt());
        lams.push(lam);
    }
    (ks, ws, lams)
}

/// Anisotropy of the discovered speed over a `|k| ≤ k_cut` window: `(C_max − C_min)/C̄` across the
/// five directions, plus `(C_min, C_max)`. Every per-direction law comes from [`discover_law`].
fn anisotropy(
    mesh: &geom::mesh::SimplicialComplex,
    coords: &[[f64; 3]],
    star0: &[f64],
    star1: &[f64],
    k_cut: f64,
) -> (f64, f64, f64) {
    let mut cs = Vec::new();
    for (nvec, name) in DIRS {
        let (ks, ws, _) = direction_sweep(mesh, coords, star0, star1, nvec, k_cut);
        assert!(ks.len() >= 3, "[{name}] window |k|<={k_cut} holds only {} modes", ks.len());
        cs.push(discover_law(&ks, &ws).coefficient);
    }
    let cmin = cs.iter().cloned().fold(f64::INFINITY, f64::min);
    let cmax = cs.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let cmean = cs.iter().sum::<f64>() / cs.len() as f64;
    ((cmax - cmin) / cmean, cmin, cmax)
}

/// Minimum-image displacement of an edge on the `N`-torus (unit spacing), as an integer `|d|²`
/// class: 1 = axis, 2 = face diagonal, 3 = body diagonal.
fn edge_class(a: [f64; 3], b: [f64; 3]) -> i64 {
    let mut len2 = 0.0;
    for c in 0..3 {
        let mut x = b[c] - a[c];
        let p = N as f64;
        while x > p / 2.0 {
            x -= p;
        }
        while x < -p / 2.0 {
            x += p;
        }
        len2 += x * x;
    }
    len2.round() as i64
}

fn main() {
    let t0 = std::time::Instant::now();
    let mesh = mesh_3d_tetrahedral_grid_periodic(N, N, N);
    let coords: Vec<[f64; 3]> = (0..N)
        .flat_map(|i| (0..N).flat_map(move |j| (0..N).map(move |k| [i as f64, j as f64, k as f64])))
        .collect();
    assert_eq!(coords.len(), mesh.num_k_forms(0), "coords must match vertex count");

    let lat = Lattice::orthorhombic([N as f64, N as f64, N as f64]);
    let (star0, star1) = unfolded_scalar_stars(&mesh, &coords, &lat);
    let star0_i = vec![1.0; mesh.num_k_forms(0)];
    let star1_i = vec![1.0; mesh.num_k_forms(1)];

    rec!("\n######## lab/0117 — Warp-1.7: `ω = c·k` discovered blind, in five directions ########");
    rec!("FIREWALL (R3): toy DEC scalar wave on a {N}x{N}x{N} periodic tet lattice; ω, k, 'speed',");
    rec!("  'isotropy' name operator properties, never a real light cone. Prediction-grade = the");
    rec!("  dimensionless exponent and the dimensionless anisotropy ratio. c = 1 in code units only.");
    rec!(
        "\n  mesh: V={} E={} T={}   candidate menu {CANDIDATES:?}   K_CUT={K_CUT}",
        mesh.num_k_forms(0),
        mesh.num_k_forms(1),
        mesh.cells_3.len()
    );

    // ---------------- P0: the machinery, against an absolute answer key ----------------
    let mut star0_dev: f64 = 0.0;
    for s in &star0 {
        star0_dev = star0_dev.max((s - 1.0).abs());
    }
    let (mut axis_dev, mut diag_max, mut n_axis, mut n_diag) = (0.0f64, 0.0f64, 0usize, 0usize);
    for (ei, e) in mesh.edges.iter().enumerate() {
        match edge_class(coords[e.0 .0], coords[e.1 .0]) {
            1 => {
                axis_dev = axis_dev.max((star1[ei] - 1.0).abs());
                n_axis += 1;
            }
            _ => {
                diag_max = diag_max.max(star1[ei].abs());
                n_diag += 1;
            }
        }
    }

    let tau = std::f64::consts::TAU;
    let mut symbol_dev: f64 = 0.0;
    let mut min_lambda = f64::INFINITY;
    let mut max_lambda: f64 = 0.0;
    let mut axis_lams: Vec<Vec<f64>> = Vec::new();
    let mut sweeps: Vec<(&str, Vec<f64>, Vec<f64>, Vec<f64>)> = Vec::new();
    for (nvec, name) in DIRS {
        let (ks, ws, lams) =
            direction_sweep(&mesh, &coords, &star0, &star1, nvec, 2.0 * K_CUT);
        for (i, lam) in lams.iter().enumerate() {
            let m = (i + 1) as f64;
            let sym: f64 = (0..3)
                .map(|c| 2.0 - 2.0 * (tau * m * nvec[c] as f64 / N as f64).cos())
                .sum();
            symbol_dev = symbol_dev.max((lam - sym).abs());
            min_lambda = min_lambda.min(*lam);
            max_lambda = max_lambda.max(*lam);
        }
        if nvec[0] + nvec[1] + nvec[2] == 1 {
            axis_lams.push(lams.clone());
        }
        sweeps.push((name, ks, ws, lams));
    }
    let mut axis_disagree: f64 = 0.0;
    for i in 0..axis_lams[0].len() {
        let (a, b, c) = (axis_lams[0][i], axis_lams[1][i], axis_lams[2][i]);
        let scale = a.abs().max(b.abs()).max(c.abs()).max(1e-300);
        axis_disagree = axis_disagree.max((a - b).abs().max((a - c).abs()) / scale);
    }

    rec!("\n  --- P0: machinery vs the closed-form key ---");
    rec!("  ⋆₀ uniform:            max|⋆₀-1| = {star0_dev:.3e}   (over {} vertices)", star0.len());
    rec!("  ⋆₁ on {n_axis} axis edges:  max|⋆₁-1| = {axis_dev:.3e}");
    rec!("  ⋆₁ on {n_diag} diagonal edges: max|⋆₁|  = {diag_max:.3e}   (exact zeros: the 3-D cot 90° = 0)");
    rec!("  7-point symbol:        max|λ - Σ(2-2cos k_a)| = {symbol_dev:.3e}  (λ ≤ {max_lambda:.4})");
    rec!("  axis-triple agreement: max relative spread = {axis_disagree:.3e}");
    rec!("  min λ over all probed modes = {min_lambda:.3e}");

    // ---------------- P1 / P3: the blind discovery, per direction ----------------
    rec!("\n  --- P1/P3: the blind discovery, per direction (long-λ |k| ≤ {K_CUT}, full |k| ≤ {}) ---", 2.0 * K_CUT);
    rec!("  dir    n_long  n_full   selected  sel_R²      margin    free_p     C          R²           p_full   bend");
    let mut rows: Vec<(String, usize, usize, f64, f64, f64, f64, f64, f64, f64, f64)> = Vec::new();
    let (mut worst_sel_margin, mut worst_p_dev, mut worst_r2) = (f64::INFINITY, 0.0f64, 1.0f64);
    let mut all_selected_linear = true;
    let (mut min_bend, mut pfull_lo, mut pfull_hi) = (f64::INFINITY, f64::INFINITY, f64::NEG_INFINITY);
    for (name, ks, ws, _) in &sweeps {
        let n_long = ks.iter().filter(|&&k| k <= K_CUT).count();
        assert!(n_long >= 3, "[{name}] long-λ window holds only {n_long} modes");
        let long = discover_law(&ks[..n_long], &ws[..n_long]);
        let full = discover_law(ks, ws);
        all_selected_linear &= long.selected_exponent == 1.0;
        worst_sel_margin = worst_sel_margin.min(long.margin);
        worst_p_dev = worst_p_dev.max((long.exponent - 1.0).abs());
        worst_r2 = worst_r2.min(long.r2);
        min_bend = min_bend.min(long.exponent - full.exponent);
        pfull_lo = pfull_lo.min(full.exponent);
        pfull_hi = pfull_hi.max(full.exponent);
        rec!(
            "  [{name}]  {n_long:>5}  {:>5}     p={:.1}    {:.7}  {:.6}  {:.6}  {:.6}  {:.9}  {:.6}  {:.6}",
            ks.len(),
            long.selected_exponent,
            long.selected_r2,
            long.margin,
            long.exponent,
            long.coefficient,
            long.r2,
            full.exponent,
            long.exponent - full.exponent
        );
        rows.push((
            name.to_string(),
            n_long,
            ks.len(),
            long.selected_exponent,
            long.selected_r2,
            long.margin,
            long.exponent,
            long.coefficient,
            long.r2,
            full.exponent,
            long.exponent - full.exponent,
        ));
    }

    // ---------------- P2: isotropy of the discovered speed, and its k-scaling ----------------
    let (a_full, c_lo, c_hi) = anisotropy(&mesh, &coords, &star0, &star1, K_CUT);
    let (a_half, c_lo_h, c_hi_h) = anisotropy(&mesh, &coords, &star0, &star1, K_CUT / 2.0);
    let ratio = a_full / a_half;
    let key_dev = (1.0 - c_lo_h).abs().max((1.0 - c_hi_h).abs());
    rec!("\n  --- P2: isotropy of the discovered speed ---");
    rec!("  A(K)   = {a_full:.6}   C ∈ [{c_lo:.6}, {c_hi:.6}]");
    rec!("  A(K/2) = {a_half:.6}   C ∈ [{c_lo_h:.6}, {c_hi_h:.6}]   max|1-C| = {key_dev:.6}");
    rec!("  ratio A(K)/A(K/2) = {ratio:.4}   (>1 ⇒ finite-k; ≈1 ⇒ leading-order cone defect)");

    // ---------------- P4: the negative control — the same pipeline on ⋆ = I ----------------
    let (ai_full, ci_lo, ci_hi) = anisotropy(&mesh, &coords, &star0_i, &star1_i, K_CUT);
    let (ai_half, _, _) = anisotropy(&mesh, &coords, &star0_i, &star1_i, K_CUT / 2.0);
    let ratio_i = ai_full / ai_half;
    rec!("\n  --- P4: negative control, the SAME pipeline on the trivial ⋆ = I (rung 1.5 / #23) ---");
    rec!("  A_I(K)   = {ai_full:.6}   C ∈ [{ci_lo:.6}, {ci_hi:.6}]   ({:.1}× the geometric ⋆'s)", ai_full / a_full);
    rec!("  A_I(K/2) = {ai_half:.6}   ratio = {ratio_i:.4}   (≈1 ⇒ a LEADING-ORDER defect, as expected)");

    // ---------------- data (R10 source of truth) ----------------
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-1-move/0117-dispersion-isotropy/data");
    std::fs::create_dir_all(dir).expect("create data dir");
    let mut sweep_csv = String::from("direction,m,k,lambda,omega,phase_speed,symbol_lambda\n");
    for (name, ks, ws, lams) in &sweeps {
        let nvec = DIRS.iter().find(|(_, s)| s == name).unwrap().0;
        for (i, ((k, w), lam)) in ks.iter().zip(ws).zip(lams).enumerate() {
            let m = (i + 1) as f64;
            let sym: f64 =
                (0..3).map(|c| 2.0 - 2.0 * (tau * m * nvec[c] as f64 / N as f64).cos()).sum();
            sweep_csv.push_str(&format!(
                "{name},{},{k:.9},{lam:.9},{w:.9},{:.9},{sym:.9}\n",
                i + 1,
                w / k
            ));
        }
    }
    std::fs::write(format!("{dir}/dispersion_directions.csv"), sweep_csv)
        .expect("write dispersion_directions.csv");

    let mut disc_csv = String::from(
        "direction,n_long,n_full,selected_exponent,selected_r2,margin,exponent,coefficient,r2,exponent_full,bend\n",
    );
    for r in &rows {
        disc_csv.push_str(&format!(
            "{},{},{},{:.1},{:.9},{:.9},{:.9},{:.9},{:.9},{:.9},{:.9}\n",
            r.0, r.1, r.2, r.3, r.4, r.5, r.6, r.7, r.8, r.9, r.10
        ));
    }
    std::fs::write(format!("{dir}/discovery.csv"), disc_csv).expect("write discovery.csv");

    // candidate scorecard on the long-λ window, per direction — the model-selection panel's source
    let mut cand_csv = String::from("direction,candidate_exponent,r2,selected\n");
    for (name, ks, ws, _) in &sweeps {
        let n_long = ks.iter().filter(|&&k| k <= K_CUT).count();
        let sel = select_power_law(&ks[..n_long], &ws[..n_long], &CANDIDATES);
        for p in CANDIDATES {
            let f = kinematics::fit_fixed_exponent(&ks[..n_long], &ws[..n_long], p);
            cand_csv.push_str(&format!(
                "{name},{p:.1},{:.9},{}\n",
                f.r2,
                if p == sel.law.exponent { 1 } else { 0 }
            ));
        }
    }
    std::fs::write(format!("{dir}/candidates.csv"), cand_csv).expect("write candidates.csv");

    let mut iso_csv = String::from("star,window,k_cut,c_min,c_max,anisotropy\n");
    iso_csv.push_str(&format!("geometric,long,{K_CUT:.6},{c_lo:.9},{c_hi:.9},{a_full:.9}\n"));
    iso_csv.push_str(&format!(
        "geometric,half,{:.6},{c_lo_h:.9},{c_hi_h:.9},{a_half:.9}\n",
        K_CUT / 2.0
    ));
    iso_csv.push_str(&format!("identity,long,{K_CUT:.6},{ci_lo:.9},{ci_hi:.9},{ai_full:.9}\n"));
    iso_csv.push_str(&format!("identity,half,{:.6},,,{ai_half:.9}\n", K_CUT / 2.0));
    std::fs::write(format!("{dir}/isotropy.csv"), iso_csv).expect("write isotropy.csv");

    let mut key_csv = String::from("quantity,value,bound\n");
    key_csv.push_str(&format!("star0_max_dev,{star0_dev:.6e},1e-12\n"));
    key_csv.push_str(&format!("star1_axis_max_dev,{axis_dev:.6e},1e-12\n"));
    key_csv.push_str(&format!("star1_diagonal_max_abs,{diag_max:.6e},1e-14\n"));
    key_csv.push_str(&format!("symbol_max_dev,{symbol_dev:.6e},1e-9\n"));
    key_csv.push_str(&format!("axis_triple_max_rel_spread,{axis_disagree:.6e},1e-9\n"));
    key_csv.push_str(&format!("min_lambda,{min_lambda:.6e},-1e-9\n"));
    std::fs::write(format!("{dir}/answer_key.csv"), key_csv).expect("write answer_key.csv");

    // ---------------- scorecard + verdict ----------------
    let p0 = min_lambda > -1e-9
        && star0_dev < 1e-12
        && axis_dev < 1e-12
        && diag_max < 1e-14
        && symbol_dev < 1e-9
        && axis_disagree < 1e-9;
    let p1 = all_selected_linear && worst_sel_margin > 0.15 && worst_p_dev < 0.03 && worst_r2 > 0.9995;
    let p2 = a_full < 0.03 && (2.0..=3.2).contains(&ratio) && key_dev < 0.02;
    let p3 = min_bend > 0.008 && pfull_lo > 0.90 && pfull_hi < 1.00;
    let p4 = ai_full > 0.25 && (0.8..=1.2).contains(&ratio_i);

    rec!("\n  ======== SCORECARD ========");
    rec!("  P0 (valid operator + closed-form 7-point key + cubic symmetry): {}", if p0 { "PASS" } else { "FAIL" });
    rec!("  P1 (blind: linear law selected in all 5 dirs, margin {:.4}>0.15; |p-1| {:.4}<0.03; R² {:.7}>0.9995): {}",
        worst_sel_margin, worst_p_dev, worst_r2, if p1 { "PASS" } else { "FAIL" });
    rec!("  P2 (isotropy A={a_full:.5}<0.03; ratio {ratio:.4}∈[2.0,3.2]; max|1-C|={key_dev:.5}<0.02): {}", if p2 { "PASS" } else { "FAIL" });
    rec!("  P3 (pre-registered short-λ bend: min bend {min_bend:.5}>0.008; p_full ∈ [{pfull_lo:.5},{pfull_hi:.5}] ⊂ (0.90,1.00)): {}", if p3 { "PASS" } else { "FAIL" });
    rec!("  P4 (⋆=I control anisotropic: A_I={ai_full:.5}>0.25; ratio {ratio_i:.4}∈[0.8,1.2] ⇒ leading-order): {}", if p4 { "PASS" } else { "FAIL" });
    rec!("\n  VERDICT: handed a sweep with no dispersion relation supplied, the bench selects the LINEAR");
    rec!("  law in all five directions (margin {worst_sel_margin:.3} over the runner-up) and returns exponent");
    rec!("  1.00 to {:.1}%, R² ≥ {worst_r2:.6}. The discovered speeds agree to {:.2}% and that residue", worst_p_dev * 100.0, a_full * 100.0);
    rec!("  SHRINKS with the window (ratio {ratio:.2}) — a finite-k effect, not a cone defect: the same");
    rec!("  pipeline on ⋆=I returns {:.1}% anisotropy that does NOT shrink (ratio {ratio_i:.2}). The finite", ai_full * 100.0);
    rec!("  lattice bends the cone down at short λ, as pre-registered. FIREWALL: toy operator, not nature.");
    rec!("  (elapsed {:.1}s)", t0.elapsed().as_secs_f64());

    assert!(p0, "P0 failed: minλ={min_lambda:.3e} ⋆₀dev={star0_dev:.3e} axis={axis_dev:.3e} diag={diag_max:.3e} symbol={symbol_dev:.3e} axes={axis_disagree:.3e}");
    assert!(p1, "P1 failed: all_linear={all_selected_linear} margin={worst_sel_margin:.4} |p-1|={worst_p_dev:.4} R²={worst_r2:.7}");
    assert!(p2, "P2 failed: A={a_full:.5} ratio={ratio:.4} max|1-C|={key_dev:.5}");
    assert!(p3, "P3 failed: min bend={min_bend:.5} p_full ∈ [{pfull_lo:.5},{pfull_hi:.5}]");
    assert!(p4, "P4 failed: A_I={ai_full:.5} ratio_I={ratio_i:.4}");
}

#[test]
fn uf1_7_dispersion_isotropy_gate() {
    main();
}
