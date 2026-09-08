//! Gate for lab/bridge/0802-electrical (rung 8.2, R1) — the 4th view: electrical / random-walk.
//!
//! The same graph Laplacian read as a resistor network and as a random walk. Membership gate: the
//! walks↔circuits duality commute(a,b) = 2·|E|·R_eff(a,b) (two independent solves agree). Flagship
//! constant: the stella spanning-tree entropy z = lim(ln τ)/N = ⟨ln λ_L⟩_BZ (Kirchhoff), via the
//! Bloch k-sum (reusing 7.1's cmat) + Richardson — log-singularity-limited to ~5 digits.
//!
//! Run: cargo test -p uniforge --release --test uf8_2_electrical_gate -- --nocapture   (~5 s)
//!
//! FIREWALL (R3): random walk / resistance / spanning trees of a TOY 14-regular complex — z_stella is
//! a 🔵 graph constant, the walks↔circuits duality a cross-check, never a claim about nature.

use kinematics::views::{commute_time, effective_resistance, jacobi_eigs, spanning_tree_ln};
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

const Z_STELLA_REG: f64 = 2.576122; // P1
const TOL_Z: f64 = 2e-5; // honest log-singularity resolution
const DEG: f64 = 14.0;
const DIFFS_N: [[i64; 3]; 3] = [[1, -1, 0], [0, 1, -1], [-1, 0, 1]];
const LONG_N: [[i64; 3]; 3] = [[1, -1, 1], [1, 1, -1], [-1, 1, 1]];

type C64 = (f64, f64);
fn cadd(a: C64, b: C64) -> C64 { (a.0 + b.0, a.1 + b.1) }
fn csub(a: C64, b: C64) -> C64 { (a.0 - b.0, a.1 - b.1) }
fn cmul(a: C64, b: C64) -> C64 { (a.0 * b.0 - a.1 * b.1, a.0 * b.1 + a.1 * b.0) }

fn herm3_eigs(h: &[[C64; 3]; 3]) -> [f64; 3] {
    let tr = h[0][0].0 + h[1][1].0 + h[2][2].0;
    let mut tr2 = 0.0;
    for r in 0..3 { for c in 0..3 { tr2 += h[r][c].0 * h[r][c].0 + h[r][c].1 * h[r][c].1; } }
    let c1 = 0.5 * (tr * tr - tr2);
    let cof0 = csub(cmul(h[1][1], h[2][2]), cmul(h[1][2], h[2][1]));
    let cof1 = csub(cmul(h[1][0], h[2][2]), cmul(h[1][2], h[2][0]));
    let cof2 = csub(cmul(h[1][0], h[2][1]), cmul(h[1][1], h[2][0]));
    let det = cadd(csub(cmul(h[0][0], cof0), cmul(h[0][1], cof1)), cmul(h[0][2], cof2));
    let (a, b, c) = (tr, c1, det.0);
    let p = b - a * a / 3.0;
    let q = -(2.0 * a * a * a) / 27.0 + (a * b) / 3.0 - c;
    let shift = a / 3.0;
    if p.abs() < 1e-14 { let r = (-q).cbrt() + shift; return [r, r, r]; }
    let m = 2.0 * (-p / 3.0).sqrt();
    let arg = ((3.0 * q) / (p * m)).clamp(-1.0, 1.0);
    let th = arg.acos() / 3.0;
    let t23 = 2.0 * std::f64::consts::PI / 3.0;
    let mut r = [m * th.cos() + shift, m * (th - t23).cos() + shift, m * (th - 2.0 * t23).cos() + shift];
    r.sort_by(|x, y| x.partial_cmp(y).unwrap());
    r
}

/// ⟨ln λ_L⟩ over the M³ torus (excluding zero modes) — the spanning-tree entropy z at size M.
fn bloch_lnmean(m: usize) -> f64 {
    let wq = 2.0 * std::f64::consts::PI / m as f64;
    let cs: Vec<f64> = (0..m).map(|p| (wq * p as f64).cos()).collect();
    let sn: Vec<f64> = (0..m).map(|p| (wq * p as f64).sin()).collect();
    let (mut sum, mut cnt) = (0.0, 0.0);
    for p1 in 0..m { for p2 in 0..m { for p3 in 0..m {
        let p = [p1, p2, p3];
        let cd = |a: usize, b: usize| cs[p[a]] * cs[p[b]] + sn[p[a]] * sn[p[b]];
        let f0 = 2.0 * (cd(0, 1) + cd(1, 2) + cd(2, 0));
        let ax = (cs[p1] + cs[p2] + cs[p3], sn[p1] + sn[p2] + sn[p3]);
        let ph = |v: [i64; 3]| {
            let mut z = (1.0, 0.0);
            for (k, &vk) in v.iter().enumerate() {
                if vk != 0 { z = cmul(z, (cs[p[k]], if vk > 0 { sn[p[k]] } else { -sn[p[k]] })); }
            }
            z
        };
        let mut cmat = [[(0.0, 0.0); 3]; 3];
        for tau in 0..3 {
            let sc = (2 * tau) % 3;
            let up = cadd(ax, ph(LONG_N[(sc + 1) % 3]));
            let bwd = ph(LONG_N[(sc + 2) % 3]);
            let dn = (ax.0 + bwd.0, -(ax.1 + bwd.1));
            cmat[tau][tau] = (1.0 - f0 / DEG, 0.0);
            cmat[tau][(tau + 1) % 3] = (-up.0 / DEG, -up.1 / DEG);
            cmat[tau][(tau + 2) % 3] = (-dn.0 / DEG, -dn.1 / DEG);
        }
        for &ev in &herm3_eigs(&cmat) {
            let lam = DEG * ev;
            if lam > 1e-9 { sum += lam.ln(); cnt += 1.0; }
        }
    }}}
    sum / cnt
}

fn richardson(a: f64, b: f64, order: i32) -> f64 { let r = 2f64.powi(order); (r * b - a) / (r - 1.0) }

// rule-built 14-regular stella torus (7.0's graph)
fn stella_hops(tau: usize) -> Vec<[i64; 3]> {
    let mut hops = Vec::with_capacity(14);
    for d in [[1i64, 0, 0], [0, 1, 0], [0, 0, 1]] { hops.push(d); hops.push([-d[0], -d[1], -d[2]]); }
    for d in DIFFS_N { hops.push(d); hops.push([-d[0], -d[1], -d[2]]); }
    let sc = (2 * tau) % 3;
    hops.push(LONG_N[(sc + 1) % 3]);
    let b = LONG_N[(sc + 2) % 3];
    hops.push([-b[0], -b[1], -b[2]]);
    hops
}
fn stella_torus_laplacian(m: usize) -> Vec<Vec<f64>> {
    let mm = m as i64;
    let idx = |a: i64, b: i64, c: i64| (a.rem_euclid(mm) * mm * mm + b.rem_euclid(mm) * mm + c.rem_euclid(mm)) as usize;
    let n = m * m * m;
    let mut l = vec![vec![0.0f64; n]; n];
    for a in 0..mm { for b in 0..mm { for c in 0..mm {
        let tau = ((a + b + c) % 3) as usize;
        let i = idx(a, b, c);
        for d in stella_hops(tau) {
            let j = idx(a + d[0], b + d[1], c + d[2]);
            l[i][i] += 1.0; l[i][j] -= 1.0;
        }
    }}}
    l
}
fn complete_laplacian(m: usize) -> Vec<Vec<f64>> {
    let mut l = vec![vec![-1.0; m]; m];
    for i in 0..m { l[i][i] = (m - 1) as f64; }
    l
}
fn cycle_laplacian(n: usize) -> Vec<Vec<f64>> {
    let mut l = vec![vec![0.0; n]; n];
    for i in 0..n { l[i][i] = 2.0; l[i][(i + 1) % n] -= 1.0; l[i][(i + n - 1) % n] -= 1.0; }
    l
}

#[test]
fn uf8_2_electrical_gate() {
    rec!("=== rung 8.2 — the 4th view: electrical / random-walk ===");
    rec!("FIREWALL: random walk / resistance / spanning trees of a TOY complex — z is a 🔵 graph constant.");

    // ---- P0: Kirchhoff controls (closed forms) ----
    let mut p0 = true;
    let mut ctrl_rows = Vec::new();
    for &m in &[4usize, 5, 6] {
        let lt = spanning_tree_ln(&jacobi_eigs(complete_laplacian(m)));
        let cayley = ((m - 2) as f64) * (m as f64).ln();
        p0 &= (lt - cayley).abs() < 1e-9;
        rec!("[P0] K_{m}: ln τ={lt:.9} Cayley={cayley:.9} |Δ|={:.1e}", (lt - cayley).abs());
        ctrl_rows.push(format!("K_{m},{:.9},{cayley:.9}", lt));
    }
    for &n in &[5usize, 8, 12] {
        let lt = spanning_tree_ln(&jacobi_eigs(cycle_laplacian(n)));
        p0 &= (lt - (n as f64).ln()).abs() < 1e-9;
        rec!("[P0] C_{n}: τ={:.6} (expect {n})", lt.exp());
        ctrl_rows.push(format!("C_{n},{:.9},{:.9}", lt, (n as f64).ln()));
    }

    // ---- P1: the spanning-tree entropy constant via Bloch + Richardson ----
    let ms = [24usize, 48, 96, 192];
    let mut z = [0.0; 4];
    let mut z_rows = Vec::new();
    for (i, &m) in ms.iter().enumerate() {
        z[i] = bloch_lnmean(m);
        rec!("[P1] M={m:4} z_M={:.10}", z[i]);
        z_rows.push(format!("{m},{:.10}", z[i]));
    }
    let l1: Vec<f64> = z.windows(2).map(|w| richardson(w[0], w[1], 2)).collect();
    let l2: Vec<f64> = l1.windows(2).map(|w| richardson(w[0], w[1], 2)).collect();
    let z_ext = l2[l2.len() - 1];
    let internal = (z[3] - z[2]).abs();
    rec!("[P1] z_stella (Richardson) = {z_ext:.10}  (reg {Z_STELLA_REG} ± {TOL_Z})  internal={internal:.2e}");
    let p1 = (z_ext - Z_STELLA_REG).abs() < TOL_Z && internal < 1e-4;

    // ---- P2: walks↔circuits identity (membership gate) on stella(3) ----
    let ls = stella_torus_laplacian(3);
    let ne = 27 * 14 / 2; // |E| = 189
    let mut p2 = true;
    let mut p2_worst = 0.0f64;
    let mut walk_rows = Vec::new();
    for (a, b) in [(0usize, 1usize), (0, 13), (5, 20), (2, 25)] {
        let r = effective_resistance(&ls, a, b);
        let elec = 2.0 * ne as f64 * r;
        let walk = commute_time(&ls, a, b);
        let d = (elec - walk).abs();
        p2 &= d < 1e-9;
        p2_worst = p2_worst.max(d);
        rec!("[P2] nodes {a},{b}: R_eff={r:.8} 2E·R={elec:.6} walk commute={walk:.6} |Δ|={d:.1e}");
        walk_rows.push(format!("{a}-{b},{r:.8},{elec:.6},{walk:.6}"));
    }

    // ---- P3: Bloch↔dense cross-check for z at M=6 (rule-built torus, 215 nonzero modes) ----
    let ev = jacobi_eigs(stella_torus_laplacian(6));
    let nz: Vec<f64> = ev.iter().copied().filter(|&x| x > 1e-8).collect();
    let dense_z6 = nz.iter().map(|&x| x.ln()).sum::<f64>() / nz.len() as f64;
    let bloch_z6 = bloch_lnmean(6);
    let xcheck = (dense_z6 - bloch_z6).abs();
    rec!("[P3] z_6 dense ({} modes)={dense_z6:.10} Bloch={bloch_z6:.10} |Δ|={xcheck:.1e}", nz.len());
    let p3 = xcheck < 1e-9;

    // ---- emit data (R10) ----
    let dir = std::path::PathBuf::from(concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/bridge/0802-electrical/data"));
    std::fs::create_dir_all(&dir).unwrap();
    let write = |name: &str, header: &str, rows: &[String]| {
        let mut f = std::fs::File::create(dir.join(name)).unwrap();
        writeln!(f, "{header}").unwrap();
        for r in rows { writeln!(f, "{r}").unwrap(); }
    };
    write("kirchhoff_controls.csv", "graph,ln_tau,expected", &ctrl_rows);
    write("entropy_ksum.csv", "M,z_M", &z_rows);
    write("walks_circuits.csv", "pair,R_eff,elec_2ER,walk_commute", &walk_rows);
    write("summary.csv", "quantity,value", &[
        format!("z_stella,{z_ext:.10}"),
        format!("z_6_dense,{dense_z6:.10}"),
        format!("z_6_bloch,{bloch_z6:.10}"),
        format!("walks_circuits_worst,{p2_worst:.2e}"),
    ]);

    rec!("--------------------------------------------------------------------");
    rec!("[VERDICT] P0(Kirchhoff)={p0} P1(z={z_ext:.6}±{TOL_Z})={p1} P2(walks↔circuits, worst={p2_worst:.1e})={p2} P3(Bloch=dense)={p3}");
    rec!("[FIREWALL] z_stella = {z_ext:.6} is a 🔵 constant of a TOY 14-regular graph (spanning-tree");
    rec!("           entropy); the walks↔circuits duality is a cross-check between two views, not nature.");
    assert!(p0, "P0 failed: Kirchhoff controls (Cayley / cycle)");
    assert!(p1, "P1 failed: z_stella outside registered band or ladder inconsistent");
    assert!(p2, "P2 failed: commute ≠ 2E·R_eff (the 4th view fails its membership test)");
    assert!(p3, "P3 failed: Bloch z ≠ dense z at M=6");
}
