//! lab/0200 — Warp-2.0: the shaped shift's energy structure (the tenet, tested on warp).
//!
//! **The genesis tenet, tested on warp** (GENESIS.md): only geometry, nothing added by hand. Build a
//! shaped shift `N = vs·f(r)·ẑ` — a purely geometric deformation of the lattice — and read its energy off
//! the purely-geometric extrinsic-curvature functional `16πρ = (trK)² − K_ijK^ij` (`kinematics::eulerian`).
//! Prior known physics (Alcubierre) fixes the answer: negative (exotic), wall-localized, toroidal. We
//! hand-derived that our functional collapses to `16πρ = −½·vs²·f'(r)²·sin²θ`; this gate checks the
//! *discrete lattice* reproduces all three features with nothing tuned.
//!
//! Kinematics-only (static energy-structure measurement, no time evolution). Run:
//! `cargo test -p uniforge --release --test uf2_energy_structure_gate -- --nocapture`
//!
//! FIREWALL (R3): *shift, energy, warp bubble, exotic* name structures of a TOY lattice — `N` is a
//! prescribed field, `16πρ` the quadratic invariant of its gradients. No spacetime, no measurement, no
//! device. c = G = 1; unit spacing.

use kinematics::{eulerian_16pi_rho, top_hat, Grid};
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

const NB: usize = 48;
const VS: f64 = 1.0; // bubble speed (dimensionless)
const R: f64 = 14.0; // wall radius
const WALL: f64 = 2.5; // wall thickness

/// Fill the z-shift `N = (0, 0, vs·f(r))` on the grid. `uniform=true` ⇒ `f≡1` (a bare translation, no wall).
/// The wall profile is `kinematics::top_hat` (extracted from this gate — the "top-hat primitive" menu item).
fn shift_field(g: &Grid, uniform: bool) -> (Vec<f64>, Vec<f64>, Vec<f64>) {
    let c0 = NB as f64 / 2.0;
    let (nx, ny) = (vec![0.0; g.nv()], vec![0.0; g.nv()]);
    let mut nz = vec![0.0; g.nv()];
    for v in 0..g.nv() {
        let (i, j, k) = g.coord(v);
        let (x, y, z) = (i as f64 - c0, j as f64 - c0, k as f64 - c0);
        let r = (x * x + y * y + z * z).sqrt();
        let f = if uniform { 1.0 } else { top_hat(r, R, WALL) };
        nz[v] = VS * f;
    }
    (nx, ny, nz)
}

#[test]
fn uf2_energy_structure_gate() {
    rec!("\n######## lab/0200 — Warp-2.0: the shaped shift's energy structure (the tenet, tested on warp) ########");
    rec!("FIREWALL (R3): a prescribed shift field on a TOY lattice; 16πρ = (trK)²−K_ijK^ij is the quadratic");
    rec!("  invariant of its gradients (kinematics::eulerian) — NOT a spacetime/measurement/device. c=G=1.");
    rec!("  Hand-derived target: 16πρ = −½·vs²·f'(r)²·sin²θ  (negative · wall-localized · toroidal).");
    rec!("  nb={NB} vs={VS} R={R} wall={WALL}\n");

    let g = Grid::new(NB);
    let c0 = NB as f64 / 2.0;

    // ---- P0: uniform shift (no wall) must cost zero energy everywhere. ----
    let (ux, uy, uz) = shift_field(&g, true);
    let mut uni_max = 0.0_f64;
    for i in 1..NB {
        for j in 1..NB {
            for k in 1..NB {
                uni_max = uni_max.max(eulerian_16pi_rho(&g, &ux, &uy, &uz, i, j, k).abs());
            }
        }
    }

    // ---- shaped shift: energy per interior cell, classified by band and (in the wall) by polar angle. ----
    let (sx, sy, sz) = shift_field(&g, false);

    // pass 1: find the peak |16πρ| so "significant" is defined relative to it.
    let mut peak = 0.0_f64;
    for i in 1..NB {
        for j in 1..NB {
            for k in 1..NB {
                peak = peak.max(eulerian_16pi_rho(&g, &sx, &sy, &sz, i, j, k).abs());
            }
        }
    }
    let sig = 1e-3 * peak; // significance floor

    // band accumulators: (sum|e|, count)
    let (mut in_s, mut in_n) = (0.0, 0usize); // interior  r < R − 2w
    let (mut wl_s, mut wl_n) = (0.0, 0usize); // wall      |r − R| < 2w
    let (mut ex_s, mut ex_n) = (0.0, 0usize); // exterior  r > R + 2w
    // sign stats over significant cells
    let (mut sig_n, mut neg_n) = (0usize, 0usize);
    let mut emin = 0.0_f64;
    // toroidal stats within the wall shell, significant cells only
    let (mut eq_s, mut eq_n) = (0.0, 0usize); // |cosθ| < 0.3  (equator)
    let (mut po_s, mut po_n) = (0.0, 0usize); // |cosθ| > 0.85 (poles / travel axis)
    // angle profile: 9 bins of |cosθ| ∈ [0,1) → (sum|e|, count)
    let mut ang = [(0.0_f64, 0usize); 9];

    for i in 1..NB {
        for j in 1..NB {
            for k in 1..NB {
                let e = eulerian_16pi_rho(&g, &sx, &sy, &sz, i, j, k);
                let (x, y, z) = (i as f64 - c0, j as f64 - c0, k as f64 - c0);
                let r = (x * x + y * y + z * z).sqrt();
                let ae = e.abs();

                if r < R - 2.0 * WALL {
                    in_s += ae;
                    in_n += 1;
                } else if (r - R).abs() < 2.0 * WALL {
                    wl_s += ae;
                    wl_n += 1;
                } else if r > R + 2.0 * WALL {
                    ex_s += ae;
                    ex_n += 1;
                }

                if ae > sig {
                    sig_n += 1;
                    if e < 0.0 {
                        neg_n += 1;
                    }
                    emin = emin.min(e);

                    // toroidal structure: only meaningful on the wall shell where the energy lives
                    if (r - R).abs() < 2.0 * WALL && r > 1e-9 {
                        let cos_t = (z / r).abs();
                        let b = ((cos_t * 9.0) as usize).min(8);
                        ang[b].0 += ae;
                        ang[b].1 += 1;
                        if cos_t < 0.3 {
                            eq_s += ae;
                            eq_n += 1;
                        } else if cos_t > 0.85 {
                            po_s += ae;
                            po_n += 1;
                        }
                    }
                }
            }
        }
    }

    let mean = |s: f64, n: usize| if n > 0 { s / n as f64 } else { 0.0 };
    let (in_m, wl_m, ex_m) = (mean(in_s, in_n), mean(wl_s, wl_n), mean(ex_s, ex_n));
    let (eq_m, po_m) = (mean(eq_s, eq_n), mean(po_s, po_n));
    let neg_frac = if sig_n > 0 { neg_n as f64 / sig_n as f64 } else { 0.0 };
    let wall_vs_in = if in_m > 0.0 { wl_m / in_m } else { f64::INFINITY };
    let wall_vs_ex = if ex_m > 0.0 { wl_m / ex_m } else { f64::INFINITY };
    let eq_vs_po = if po_m > 0.0 { eq_m / po_m } else { f64::INFINITY };

    rec!("[P0] uniform shift (bare translation): max|16πρ| = {uni_max:.3e}   (want < 1e-9 — moving is free)");
    rec!("[P1] sign: {sig_n} significant cells, negative fraction = {neg_frac:.4}, min = {emin:.4} (peak |e| = {peak:.4})");
    rec!("[P2] band mean|16πρ|:  interior={in_m:.3e} ({in_n})  wall={wl_m:.3e} ({wl_n})  exterior={ex_m:.3e} ({ex_n})");
    rec!("     wall/interior = {wall_vs_in:.1}× · wall/exterior = {wall_vs_ex:.1}×  (want ≥ 10×)");
    rec!("[P3] toroidal:  equator mean={eq_m:.3e} ({eq_n})  pole mean={po_m:.3e} ({po_n})  equator/pole = {eq_vs_po:.1}× (want ≥ 5×)");
    rec!("     |cosθ| profile (0=equator … 8=pole):");
    for (b, (s, n)) in ang.iter().enumerate() {
        rec!("        {:.2}–{:.2} | mean|e| {:.3e}  ({} cells)", b as f64 / 9.0, (b + 1) as f64 / 9.0, mean(*s, *n), n);
    }

    // ---- R10 artifacts (anchored to the crate dir, not cwd → warp/lab/warp-2-energy/0200/data). ----
    let data_dir = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-2-energy/0200-shaped-shift-energy/data"
    );
    std::fs::create_dir_all(data_dir).expect("create lab data dir");
    let band_csv = format!(
        "band,mean_abs_16pi_rho,cell_count\ninterior,{in_m:.6e},{in_n}\nwall,{wl_m:.6e},{wl_n}\nexterior,{ex_m:.6e},{ex_n}\n"
    );
    std::fs::write(format!("{data_dir}/energy_by_band.csv"), band_csv).expect("write energy_by_band.csv");
    let mut ang_csv = String::from("abscos_theta_lo,abscos_theta_hi,region,mean_abs_16pi_rho,cell_count\n");
    for (b, (s, n)) in ang.iter().enumerate() {
        let region = if b < 3 { "equator" } else if b >= 8 { "pole" } else { "mid" };
        ang_csv.push_str(&format!(
            "{:.4},{:.4},{region},{:.6e},{n}\n",
            b as f64 / 9.0,
            (b + 1) as f64 / 9.0,
            mean(*s, *n)
        ));
    }
    std::fs::write(format!("{data_dir}/energy_by_angle.csv"), ang_csv).expect("write energy_by_angle.csv");

    // ---- verdicts ----
    let p0 = uni_max < 1e-9;
    let p1 = neg_frac >= 0.98 && emin < -1e-3;
    let p2 = wall_vs_in >= 10.0 && wall_vs_ex >= 10.0;
    let p3 = eq_vs_po >= 5.0;

    let neg_pct = neg_frac * 100.0;
    let verdict = if p0 && p1 && p2 && p3 {
        format!(
            "TENET HOLDS ON WARP (R10) — a shaped shift, read through the purely-geometric functional, \
             reproduces the Alcubierre energy structure with NOTHING added by hand. A bare translation is \
             free (uniform max|16πρ|={uni_max:.1e}); the shaped wall pays, and the price is EXOTIC \
             ({neg_pct:.0}% of significant cells negative, min {emin:.3}), WALL-LOCALIZED (wall/interior \
             {wall_vs_in:.0}×, wall/exterior {wall_vs_ex:.0}×), and TOROIDAL (equator/pole {eq_vs_po:.0}× — \
             energy rings the travel axis, vanishing on it). Matches the hand-derived −½vs²f'²sin²θ. The \
             genesis tenet (geometry only) holds for warp. FIREWALL (R3): toy lattice; c=G=1."
        )
    } else {
        format!(
            "BOUNDARY FOUND (R5, honest) — p0={p0} p1={p1} p2={p2} p3={p3}. \
             uniform_max={uni_max:.1e} neg_frac={neg_frac:.3} min={emin:.3} wall/in={wall_vs_in:.1} \
             wall/ex={wall_vs_ex:.1} eq/pole={eq_vs_po:.1}. One geometric feature did not survive the \
             lattice — inspect before claiming. FIREWALL (R3): toy lattice; c=G=1."
        )
    };
    rec!("\n[lab/0200 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} uni_max={uni_max:.3e} neg_frac={neg_frac:.4} min={emin:.4} peak={peak:.4} wall/in={wall_vs_in:.2} wall/ex={wall_vs_ex:.2} eq/pole={eq_vs_po:.2}]");

    assert!(p0, "P0: a uniform shift (bare translation) must cost zero energy");
    assert!(p1, "P1: the shaped shift's energy is negative (exotic) where significant");
    assert!(p2, "P2: the energy is localized on the bubble wall");
    assert!(p3, "P3: the wall energy is toroidal (equator ≫ poles / travel axis)");
}
