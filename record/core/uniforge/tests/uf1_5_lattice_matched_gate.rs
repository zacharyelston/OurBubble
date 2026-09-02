//! lab/0115 — Warp-1.5: the lattice-matched bubble — does matching the lattice make motion isotropic?
//!
//! **Ported to UniForge (#7 scout — the engine-via-facade path).** Behaviour-identical to
//! `stellamax-core/tests/uf1_5_lattice_matched_gate.rs`. This is the deep one: the engine comes
//! through the `uniforge` facade — `MeshWaveSolver::with_geometric_hodge` pulls **geom → dec → solve**
//! together (the geometric ⋆ lives in `dec::hodge`, called from `solve::wave_solver`, on a
//! `geom` mesh), and the lattice helpers come from `kinematics::Grid`. Every float op is preserved,
//! so the P0/P1 verdict and numbers are unchanged.
//! Run: `cargo test -p uniforge --release --test uf1_5_lattice_matched_gate -- --nocapture`
//!
//! Cycle Warp-1, rung 5 (#101). "Matching the lattice" IS the geometric Hodge star (the metric-carrying ⋆),
//! where the trivial ⋆=I gives an anisotropic light cone (the #23 defect). We evolve a scalar pulse from the
//! center with step_scalar_wave and measure its speed along a lattice axis [100] vs a body diagonal [111],
//! under ⋆=I (MeshWaveSolver::new) vs the geometric Hodge (with_geometric_hodge).
//!
//! FIREWALL (R3): internal lattice numerics — a toy DEC scalar pulse on a tetrahedral mesh; light cone / isotropy /
//! lattice-matched name solver behaviour, never a real EM/gravity measurement or a real warp bubble. c=1.

use kinematics::Grid;
use std::io::Write;
// Engine via the compatibility facade (geom mesh + the wave solver that calls dec::hodge).
use uniforge::mesh::mesh_3d_tetrahedral_grid;
use uniforge::wave_solver::MeshWaveSolver;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

const NB: usize = 24;
const C: f64 = 1.0;

/// Evolve a centered Gaussian pulse; return (v_axis, v_diag) from time-of-peak |φ| at equal-symmetry probes.
fn run_iso(geometric: bool, nb: usize, dt: f64, steps: usize) -> (f64, f64) {
    let g = Grid::new(nb);
    let nv = g.nv();
    let c0 = nb as f64 / 2.0;
    // vertex coords via the shared Grid (replaces the gate's local `coord`)
    let coords: Vec<[f64; 3]> = (0..nv)
        .map(|v| {
            let (i, j, k) = g.coord(v);
            [i as f64, j as f64, k as f64]
        })
        .collect();
    let mesh = mesh_3d_tetrahedral_grid(nb, nb, nb);
    let solver = if geometric {
        MeshWaveSolver::with_geometric_hodge(mesh, &coords)
    } else {
        MeshWaveSolver::new(mesh)
    };
    let sigma = 2.0;
    let phi0: Vec<f64> = coords
        .iter()
        .map(|p| {
            let r2 = (p[0] - c0).powi(2) + (p[1] - c0).powi(2) + (p[2] - c0).powi(2);
            (-r2 / (2.0 * sigma * sigma)).exp()
        })
        .collect();
    let mut phi = phi0.clone();
    let mut phi_old = phi0; // at rest

    // probes: axes at offset oa (dist oa), diagonals at offset od each axis (dist od√3); pick oa,od ~ equal dist
    let oa = 8i64;
    let od = 5i64; // 5√3 ≈ 8.66
    let ci = c0 as i64;
    // index via the shared Grid::vid (offsets stay in-range, so the i64→usize cast is exact)
    let vid = |i: i64, j: i64, k: i64| g.vid(i as usize, j as usize, k as usize);
    let axis_probes = [
        vid(ci + oa, ci, ci), vid(ci - oa, ci, ci),
        vid(ci, ci + oa, ci), vid(ci, ci - oa, ci),
        vid(ci, ci, ci + oa), vid(ci, ci, ci - oa),
    ];
    let diag_probes = [
        vid(ci + od, ci + od, ci + od), vid(ci - od, ci + od, ci + od),
        vid(ci + od, ci - od, ci + od), vid(ci + od, ci + od, ci - od),
        vid(ci - od, ci - od, ci + od), vid(ci - od, ci + od, ci - od),
        vid(ci + od, ci - od, ci - od), vid(ci - od, ci - od, ci - od),
    ];
    let dist_axis = oa as f64;
    let dist_diag = (od as f64) * (3.0f64).sqrt();

    let mut t_peak_axis = vec![(0.0f64, 0usize); axis_probes.len()]; // (max|φ|, step)
    let mut t_peak_diag = vec![(0.0f64, 0usize); diag_probes.len()];
    for s in 1..=steps {
        let next = solver.step_scalar_wave(&phi, &phi_old, C, dt);
        phi_old = phi;
        phi = next;
        for (pi, &p) in axis_probes.iter().enumerate() {
            let a = phi[p].abs();
            if a > t_peak_axis[pi].0 {
                t_peak_axis[pi] = (a, s);
            }
        }
        for (pi, &p) in diag_probes.iter().enumerate() {
            let a = phi[p].abs();
            if a > t_peak_diag[pi].0 {
                t_peak_diag[pi] = (a, s);
            }
        }
    }
    let mean_t = |v: &[(f64, usize)]| {
        let s: f64 = v.iter().map(|x| x.1 as f64).sum();
        s / v.len() as f64 * dt
    };
    let v_axis = dist_axis / mean_t(&t_peak_axis).max(1e-9);
    let v_diag = dist_diag / mean_t(&t_peak_diag).max(1e-9);
    (v_axis, v_diag)
}

#[test]
fn uf1_5_lattice_matched_gate() {
    rec!("\n######## lab/0115 — Warp-1.5: the lattice-matched bubble (isotropy of motion) ########");
    rec!("FIREWALL (R3): toy DEC scalar pulse on a tetrahedral mesh — light cone/isotropy/lattice-matched name");
    rec!("  solver behaviour, not a real EM/gravity measurement or warp bubble. nb={NB}, c={C}.\n");
    // pick a dt stable for both solvers (the smaller bound), with margin
    let nb = NB;
    let dt = 0.04;
    let steps = (14.0 / dt) as usize; // enough for the front to pass distance ~8.7

    rec!("[P0] trivial Hodge ⋆=I (combinatorial Laplacian) — axis vs diagonal speed:");
    let (va_i, vd_i) = run_iso(false, nb, dt, steps);
    let aniso_i = (va_i / vd_i - 1.0).abs();
    rec!("   v_axis[100]={va_i:.4}  v_diag[111]={vd_i:.4}  anisotropy |v_ax/v_di−1| = {:.1}%", 100.0 * aniso_i);

    rec!("\n[P1] geometric Hodge (lattice-matched ⋆) — axis vs diagonal speed:");
    let (va_g, vd_g) = run_iso(true, nb, dt, steps);
    let aniso_g = (va_g / vd_g - 1.0).abs();
    rec!("   v_axis[100]={va_g:.4}  v_diag[111]={vd_g:.4}  anisotropy |v_ax/v_di−1| = {:.1}%", 100.0 * aniso_g);

    // P0: ⋆=I is clearly anisotropic
    let p0 = aniso_i > 0.05;
    // P1: geometric Hodge is markedly less anisotropic (isotropy restored)
    let p1 = aniso_g < 0.5 * aniso_i && aniso_g < aniso_i - 0.03;
    let improvement = if aniso_g > 1e-9 { aniso_i / aniso_g } else { f64::INFINITY };

    rec!("\n[summary] ⋆=I anisotropic (P0): {p0}  geometric Hodge restores isotropy (P1): {p1}");
    rec!("   anisotropy: ⋆=I {:.1}%  →  geometric {:.1}%   (×{improvement:.1} more isotropic when lattice-matched)",
        100.0 * aniso_i, 100.0 * aniso_g);

    // R10 — the sim IS the graphic: write the data-true artifact into this rung's lab entry.
    // Path is anchored to the crate dir (CARGO_MANIFEST_DIR = core/uniforge), NOT the cwd, so it
    // resolves wherever `cargo test` is run from. → warp/lab/warp-1-move/0115-.../data/isotropy.csv
    let data_dir = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-1-move/0115-lattice-matched-isotropy/data"
    );
    std::fs::create_dir_all(data_dir).expect("create lab data dir");
    let csv = format!(
        "solver,v_axis_100,v_diag_111,anisotropy\n\
         trivial_star_I,{va_i:.4},{vd_i:.4},{aniso_i:.3}\n\
         geometric_hodge,{va_g:.4},{vd_g:.4},{aniso_g:.3}\n"
    );
    std::fs::write(format!("{data_dir}/isotropy.csv"), csv).expect("write isotropy.csv");
    rec!("   [R10] wrote {data_dir}/isotropy.csv");

    rec!("\n[lab/0115 VERDICT] {}", if p0 && p1 {
        format!("LATTICE-MATCHING CONFIRMED (R5) — 'matching the lattice' (the geometric Hodge ⋆) turns the \
         anisotropic ⋆=I light cone ISOTROPIC: the trivial combinatorial Laplacian propagates the pulse \
         {:.1}% faster/slower along a lattice axis than a body diagonal (the #23 defect), and the geometric Hodge \
         cuts that to {:.1}% (×{improvement:.0} more isotropic). So a bubble moves — and STEERS — at the same speed \
         in every direction ONLY when lattice-matched; on ⋆=I the Warp-1.2 steering would point untrue (faster \
         along axes than diagonals). Matching the lattice is what makes directional control honest. Firewall (R3): \
         internal lattice numerics — a toy scalar pulse, not a real light cone / warp bubble.",
         100.0 * aniso_i, 100.0 * aniso_g)
    } else if !p0 {
        "INCONCLUSIVE — ⋆=I did not show clear anisotropy at this resolution (under-resolved). Adjust σ/distance. Firewall (R3)."
            .to_string()
    } else {
        format!("PARTIAL / CHECK (R5) — ⋆=I is anisotropic ({:.1}%) but the geometric Hodge did not clearly reduce \
         it ({:.1}%) at this resolution. Report the residual. Firewall (R3).", 100.0 * aniso_i, 100.0 * aniso_g)
    });

    assert!(p0, "P0: trivial ⋆=I must be anisotropic (axis vs diagonal speed differ — the #23 defect)");
    assert!(p1, "P1: the geometric Hodge must markedly reduce the anisotropy (lattice-matched ⇒ isotropic motion)");
    rec!("\n  [recorded: aniso_trivial={:.1}% aniso_geometric={:.1}% improvement=×{improvement:.1}]",
        100.0 * aniso_i, 100.0 * aniso_g);
}
