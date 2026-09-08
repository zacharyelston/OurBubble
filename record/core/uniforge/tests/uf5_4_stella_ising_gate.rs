//! lab/0504 — Warp-5.4: Ising on the stella lattice — universality tested on our own geometry.
//!
//! Chapters 4–5 ran on chains and cubic grids; this rung brings the method home. Ising spins live on the
//! vertices of the ENGINE'S OWN stella complex (mesh_3d_chiral_tetoct_yz_periodic), bonds on its edges,
//! adjacency read straight from d0_sparse. Universality says the lattice doesn't matter:
//!   • T_c is a NEW number (nobody tabulates this graph) — located blind by the Binder crossing,
//!   • U* is amplitude — boundary-condition-dependent, so it should NOT match periodic-cubic 0.484,
//!   • the exponent ratios are class-universal — they MUST match 3-D Ising (and 5.3's cubic run).
//!
//! Run: `cargo test -p uniforge --release --test uf5_4_stella_ising_gate -- --nocapture`  (~40 s)
//!
//! FIREWALL (R3): a seeded Wolff simulation on the TOY engine mesh; universality-class membership shared
//! with real materials. Class values and 5.3's cubic run are post-hoc checks. Not a magnet/spacetime claim.

use kinematics::power_law_fit;
use std::io::Write;
use uniforge::engine_operator::oct_axis;
use uniforge::mesh_3d_chiral_tetoct_yz_periodic;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 = self.0.wrapping_add(0x9E37_79B9_7F4A_7C15);
        let mut z = self.0;
        z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
        z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
        z ^ (z >> 31)
    }
    fn f(&mut self) -> f64 {
        (self.next() >> 11) as f64 / (1u64 << 53) as f64
    }
}

/// Quadratic least squares y = a + b·x + c·x²; returns (a, b, c).
fn quad(xs: &[f64], ys: &[f64]) -> (f64, f64, f64) {
    let (mut m, mut v) = ([[0.0f64; 3]; 3], [0.0f64; 3]);
    for (k, &x) in xs.iter().enumerate() {
        let b = [1.0, x, x * x];
        for i in 0..3 {
            v[i] += b[i] * ys[k];
            for j in 0..3 {
                m[i][j] += b[i] * b[j];
            }
        }
    }
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
    (a[0][3], a[1][3], a[2][3])
}

/// The stella complex's vertex adjacency, read from the ENGINE mesh's own incidence (d0_sparse),
/// compacted to the degree>0 vertices (the FCC sublattice; dense odd-sum points are isolated).
/// Returns (neighbor lists, most-common coordination, connected?).
fn stella_adjacency(n: usize) -> (Vec<Vec<u32>>, usize, bool) {
    let mesh = mesh_3d_chiral_tetoct_yz_periodic(n, n, n, oct_axis);
    let nv = (n + 1) * n * n;
    let mut nbrs: Vec<Vec<u32>> = vec![Vec::new(); nv];
    for row in &mesh.d0_sparse {
        let (mut h, mut t) = (usize::MAX, usize::MAX);
        for &(v, s) in row {
            if s > 0 {
                h = v
            } else {
                t = v
            }
        }
        nbrs[h].push(t as u32);
        nbrs[t].push(h as u32);
    }
    let mut map = vec![u32::MAX; nv];
    let mut active = Vec::new();
    for (v, l) in nbrs.iter().enumerate() {
        if !l.is_empty() {
            map[v] = active.len() as u32;
            active.push(v);
        }
    }
    let mut adj: Vec<Vec<u32>> = Vec::with_capacity(active.len());
    for &v in &active {
        adj.push(nbrs[v].iter().map(|&w| map[w as usize]).collect());
    }
    // mode coordination
    let mut hist = std::collections::BTreeMap::new();
    for l in &adj {
        *hist.entry(l.len()).or_insert(0usize) += 1;
    }
    let mode = hist.iter().max_by_key(|(_, &c)| c).map(|(&z, _)| z).unwrap_or(0);
    // connectivity (BFS)
    let mut seen = vec![false; adj.len()];
    let mut stack = vec![0u32];
    seen[0] = true;
    let mut count = 1usize;
    while let Some(i) = stack.pop() {
        for &j in &adj[i as usize] {
            if !seen[j as usize] {
                seen[j as usize] = true;
                count += 1;
                stack.push(j);
            }
        }
    }
    let connected = count == adj.len();
    (adj, mode, connected)
}

/// Seeded Wolff on a graph, incremental magnetization. Returns (⟨m²⟩, ⟨m⁴⟩, ⟨|m|⟩, χ=N⟨m²⟩).
fn wolff(adj: &[Vec<u32>], t: f64, warm: usize, meas: usize, seed: u64) -> (f64, f64, f64, f64) {
    let n = adj.len();
    let mut s = vec![1i8; n];
    let mut r = Rng(seed);
    let padd = 1.0 - (-2.0 / t).exp();
    let mut st: Vec<u32> = Vec::with_capacity(n);
    let mut mm: i64 = n as i64;
    let mut step = |s: &mut Vec<i8>, r: &mut Rng, mm: &mut i64| {
        let si = (r.next() as usize) % n;
        let old = s[si];
        s[si] = -old;
        st.clear();
        st.push(si as u32);
        let mut cs: i64 = 1;
        while let Some(i) = st.pop() {
            for &j in &adj[i as usize] {
                if s[j as usize] == old && r.f() < padd {
                    s[j as usize] = -old;
                    st.push(j);
                    cs += 1;
                }
            }
        }
        *mm -= 2 * (old as i64) * cs;
    };
    for _ in 0..warm {
        step(&mut s, &mut r, &mut mm);
    }
    let (mut m2, mut m4, mut ma, mut c) = (0.0, 0.0, 0.0, 0.0);
    for _ in 0..meas {
        step(&mut s, &mut r, &mut mm);
        let m = mm as f64 / n as f64;
        m2 += m * m;
        m4 += m * m * m * m;
        ma += m.abs();
        c += 1.0;
    }
    (m2 / c, m4 / c, ma / c, m2 / c * n as f64)
}

#[test]
fn uf5_4_stella_ising_gate() {
    let (gonu_class, bonu_class) = (1.963, 0.518);
    let (gonu_cubic, bonu_cubic) = (2.0273, 0.4855); // 5.3's measured cubic values (post-hoc check)
    rec!("\n######## lab/0504 — Warp-5.4: Ising on the stella lattice ########");
    rec!("FIREWALL (R3): seeded Wolff on the TOY engine mesh's own vertices and edges. Class values = post-hoc checks.\n");

    // P0 — the graph is the engine's
    let (adj16, mode16, conn16) = stella_adjacency(16);
    let fcc16 = 17 * 16 * 16 / 2;
    rec!("[P0] n=16 graph from d0_sparse: active={} (FCC count {}), bulk coordination mode={mode16}, connected={conn16}", adj16.len(), fcc16);

    // sweep
    let ls = [8usize, 12, 16, 24];
    let ts: Vec<f64> = (0..9).map(|i| 11.30 + 0.05 * i as f64).collect();
    let nt = ts.len();
    let (mut u, mut chi, mut am) = (vec![vec![0.0; nt]; 4], vec![vec![0.0; nt]; 4], vec![vec![0.0; nt]; 4]);
    for (li, &n) in ls.iter().enumerate() {
        let (adj, _, _) = stella_adjacency(n);
        for (ti, &t) in ts.iter().enumerate() {
            let (m2, m4, ma, c) = wolff(&adj, t, 4000, 60000, 42 + n as u64 * 17 + ti as u64);
            u[li][ti] = 1.0 - m4 / (3.0 * m2 * m2);
            chi[li][ti] = c;
            am[li][ti] = ma;
        }
    }

    // P1 — locate the stella T_c
    let mut cross = Vec::new();
    for a in 0..3 {
        let b = a + 1;
        for ti in 0..nt - 1 {
            let (d1, d2) = (u[a][ti] - u[b][ti], u[a][ti + 1] - u[b][ti + 1]);
            if d1 == 0.0 || d1 * d2 < 0.0 {
                let f = d1 / (d1 - d2);
                cross.push(ts[ti] + f * (ts[ti + 1] - ts[ti]));
            }
        }
    }
    let tc = cross.iter().sum::<f64>() / cross.len() as f64;
    let spread = cross.iter().cloned().fold(f64::MIN, f64::max) - cross.iter().cloned().fold(f64::MAX, f64::min);
    rec!("[P1] crossings {:?} → stella T_c = {tc:.4} (spread {spread:.3}) — a new number; sanity 9.79·14/12 ≈ 11.4",
        cross.iter().map(|x| (x * 1e3).round() / 1e3).collect::<Vec<_>>());

    // per-L quadratic values at T_c
    let (mut ustars, mut lchi, mut lm) = (Vec::new(), Vec::new(), Vec::new());
    for li in 0..4 {
        let (a, b, c2) = quad(&ts, &u[li]);
        ustars.push(a + b * tc + c2 * tc * tc);
        let lnchi: Vec<f64> = chi[li].iter().map(|x| x.ln()).collect();
        let (a, b, c2) = quad(&ts, &lnchi);
        lchi.push(a + b * tc + c2 * tc * tc);
        let lnm: Vec<f64> = am[li].iter().map(|x| x.ln()).collect();
        let (a, b, c2) = quad(&ts, &lnm);
        lm.push(a + b * tc + c2 * tc * tc);
    }
    let ustar = ustars.iter().sum::<f64>() / 4.0;
    let uspread = ustars.iter().cloned().fold(f64::MIN, f64::max) - ustars.iter().cloned().fold(f64::MAX, f64::min);
    rec!("[P2] U* per L: {:?} → U* = {ustar:.3} (spread {uspread:.3}); periodic-cubic was 0.484 — amplitudes are BC-dependent",
        ustars.iter().map(|x| (x * 1e3).round() / 1e3).collect::<Vec<_>>());

    // P3 — the class ratios on our lattice
    let lvec: Vec<f64> = ls.iter().map(|&l| l as f64).collect();
    let expchi: Vec<f64> = lchi.iter().map(|x| x.exp()).collect();
    let expm: Vec<f64> = lm.iter().map(|x| x.exp()).collect();
    let gonu = power_law_fit(&lvec, &expchi).exponent;
    let bonu = -power_law_fit(&lvec, &expm).exponent;
    let (g_err, b_err) = ((gonu - gonu_class).abs() / gonu_class, (bonu - bonu_class).abs() / bonu_class);
    let (g_x, b_x) = ((gonu - gonu_cubic).abs() / gonu_cubic, (bonu - bonu_cubic).abs() / bonu_cubic);
    rec!("[P3] at located T_c: γ/ν = {gonu:.4} (class {gonu_class}, {:.1}%; cubic-5.3 {gonu_cubic}, {:.1}%)", g_err * 100.0, g_x * 100.0);
    rec!("     β/ν = {bonu:.4} (class {bonu_class}, {:.1}%; cubic-5.3 {bonu_cubic}, {:.1}%)", b_err * 100.0, b_x * 100.0);

    // R10 artifacts
    let dir = concat!(env!("CARGO_MANIFEST_DIR"), "/../../lab/warp-5-universality/0504-stella-ising/data");
    std::fs::create_dir_all(dir).expect("create lab data dir");
    let mut g = String::from("n,active_vertices,coordination_mode,connected\n");
    g.push_str(&format!("16,{},{mode16},{conn16}\n", adj16.len()));
    std::fs::write(format!("{dir}/stella_graph.csv"), g).expect("write stella_graph.csv");
    let mut bd = String::from("L,T,U,chi,abs_m\n");
    for (li, &l) in ls.iter().enumerate() {
        for (ti, &t) in ts.iter().enumerate() {
            bd.push_str(&format!("{l},{t:.3},{:.5},{:.4},{:.6}\n", u[li][ti], chi[li][ti], am[li][ti]));
        }
    }
    std::fs::write(format!("{dir}/binder_stella.csv"), bd).expect("write binder_stella.csv");
    let res = format!(
        "quantity,measured,check\nT_c_stella,{tc:.4},new (sanity ~11.4)\nU_star,{ustar:.4},cubic-periodic 0.484 (should differ)\n\
         gamma_over_nu,{gonu:.4},{gonu_class}\nbeta_over_nu,{bonu:.4},{bonu_class}\n\
         gamma_over_nu_cubic53,{gonu_cubic},cross-lattice\nbeta_over_nu_cubic53,{bonu_cubic},cross-lattice\n"
    );
    std::fs::write(format!("{dir}/results.csv"), res).expect("write results.csv");

    // verdicts
    let p0 = adj16.len() == fcc16 && mode16 == 14 && conn16;
    let p1 = !cross.is_empty() && spread < 0.15 && (11.3..=12.0).contains(&tc);
    let p2 = (0.24..=0.38).contains(&ustar) && uspread < 0.06 && (0.484 - ustar) > 0.05;
    let p3 = g_err < 0.06 && b_err < 0.08 && g_x < 0.10 && b_x < 0.10;

    let verdict = if p0 && p1 && p2 && p3 {
        format!("UNIVERSALITY HOLDS ON OUR OWN LATTICE (R10). Ising spins on the engine's stella complex — the \
             graph read from its own d0_sparse (FCC vertices, coordination 14, connected) — order at a NEW \
             critical temperature T_c = {tc:.3}, located blind by the Binder crossing. The amplitude U* = \
             {ustar:.3} differs from the periodic-cubic 0.484 (amplitudes depend on boundary geometry), but the \
             exponent ratios do not: γ/ν = {gonu:.3} and β/ν = {bonu:.3} sit in the 3-D Ising class and agree \
             with 5.3's cubic run — a different lattice, the same class. The lattice doesn't matter; that is \
             universality, tested on the lattice we actually built. FIREWALL (R3): toy mesh, not a magnet.")
    } else {
        format!("CHECK (R5) — p0={p0} p1={p1} p2={p2} p3={p3}; T_c={tc:.4} U*={ustar:.3} γ/ν={gonu:.3} β/ν={bonu:.3}. FIREWALL (R3).")
    };
    rec!("\n[lab/0504 VERDICT] {verdict}");
    rec!("\n  [recorded: p0={p0} p1={p1} p2={p2} p3={p3} tc={tc:.4} spread={spread:.4} ustar={ustar:.4} gonu={gonu:.4} bonu={bonu:.4} g_err={g_err:.4} b_err={b_err:.4}]");

    assert!(p0, "P0: the spin graph is the engine mesh's own adjacency (FCC, z=14, connected)");
    assert!(p1, "P1: the Binder crossing locates the stella T_c (a new number)");
    assert!(p2, "P2: U* is stable, and differs from periodic-cubic — amplitudes are BC-dependent");
    assert!(p3, "P3: the exponent ratios match the 3-D Ising class and the cubic run — same class, different lattice");
}
