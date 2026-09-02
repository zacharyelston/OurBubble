//! lab/warp-5-universality/0510 — Warp-5.10: reprocess rung **5.6's** SITE-percolation `d_f`
//! NEGATIVE with 5.8's crossing-drift locator and 5.9's propagated band. Issue **#306**; carries the
//! decisive extra evidence for issue **#305** (the estimator-ordering fork).
//!
//! 5.6 registered a first-class negative: `d_f = 2.43782` at its crossing-located threshold, missing
//! its registered band `2.52295 ± 0.06`, locked with a post-hoc diagnosis (`∂d_f/∂p ≈ 117`;
//! `d_f = 2.52498` at its pre-registered constant `0.1752`). It never computed its locator's standard
//! error, so that band was never propagated. This gate decides, on numbers registered before the run
//! (spec.md), between:
//!   • H-DISSOLVE — every candidate locator lands within 2σ of the class value once the locator's own
//!     error is propagated through the MEASURED amplification ⇒ 5.6's miss was the locator's error,
//!     unpropagated (registered branch);
//!   • H-CERTIFY  — the miss survives a propagated band ⇒ the negative stands harder, scoped to this
//!     family/graph at `L ≤ 48`, next discriminator named in advance (`L` up to ~96–128).
//! The verdict is evaluated at ALL THREE candidate locators (5.6's own, per-batch-extrapolated,
//! aggregate-extrapolated), each with its own quoted error, so it cannot hinge on #305's fork.
//!
//! Two things this rung has that 5.9 did not: an **exact** zero-location-error control (triangular
//! site — `p_c = 1/2` exactly, Sykes–Essam 1964 / Kesten 1980, AND `d_f = 91/48` exactly, den Nijs
//! 1979 / SLE₆, so no literature uncertainty enters at either end), and a **second** answer key for
//! the ordering fork (FCC-site `0.1992365(10)`, Lorenz & Ziff 2000). On both site keys the ordering
//! verdict comes out OPPOSITE to 5.9's single bond key — which is #305's honest answer (P2c).
//!
//! The percolation machinery below (`Rng`, `Graph`, `triangular`, `fcc`, `stella`, `Uf`, `measure`,
//! `sample`, `crossings_of`, `crossing_estimate`, `sweep_batch`, the `measure_at` seed scheme) is
//! **copied verbatim** from `uf5_6_stella_percolation_gate.rs` — 5.6's gate and its `data/` are the
//! immutable record and are never modified. Copy fidelity is gated, not assumed: P0a reproduces
//! 5.6's committed per-batch estimates for all three families and P0b BOTH of its committed `d_f`
//! values. (One deliberate difference: `measure` does not accumulate χ' or the log-s histogram, which
//! no arm of this rung uses — R7 forbids a dead field. The RNG, the site draw order, the union-find
//! and the `s_max` path are unchanged.)
//!
//! Run: `cargo test -p uniforge --release --test uf5_10_site_locator_reprocess_gate -- --nocapture` (~28 s)
//!
//! FIREWALL (R3): site-diluted TOY graphs. `p_c(stella-site)` is a 🔵 constant of THIS complex (graph
//! mathematics, never a property of matter); `d_f` is a dimensionless universal invariant of the
//! percolation class — class-membership resolution, computed, and where a previous miss dissolves it
//! dissolves into a statement about OUR estimator, not about nature.

use kinematics::{crossing_extrapolate, crossing_extrapolate_best_w, power_law_fit, replica_stats};
use std::collections::BTreeMap;
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

// ---- answer keys (independent of anything this repo computed) ----
const PC_TRI_EXACT: f64 = 0.5; // EXACT: Sykes & Essam 1964; rigorous Kesten 1980/82
const DF_2D_EXACT: f64 = 91.0 / 48.0; // EXACT: den Nijs 1979 / SLE₆
const PC_FCC_LIT: f64 = 0.199_236_5; // Lorenz & Ziff, J. Stat. Phys. 98, 961 (2000)
const DF_3D: f64 = 2.522_95; // = 3 − β/ν, β/ν = 0.47705(15) (Wang et al., PRE 87, 052107 (2013))

// ---- 5.6's committed record (read-only oracles; its data/percolation_summary.csv + pc_batches.csv) ----
const PC_TRI_56: f64 = 0.500986;
const SIG_TRI_56: f64 = 0.001348;
const PC_FCC_56: f64 = 0.199457;
const SIG_FCC_56: f64 = 0.000296;
const PC_ST_56: f64 = 0.174453;
const SIG_ST_56: f64 = 0.000410;
const DF_ST_56: f64 = 2.43782;
const PC_ST_56_REG: f64 = 0.1752;
const DF_ST_56_REG: f64 = 2.52498;
const TOL_DF_56_REGISTERED: f64 = 0.06; // 5.6's own registered d_f tolerance (its spec.md P3)
const MISS_56: f64 = 0.085_13; // |2.43782 − 2.52295|

// ---- the registered predictions (spec.md, committed before the run) ----
const TOL_COPY_PC: f64 = 1e-6; // P0a — 5.6's numbers are printed to 6 decimals
const TOL_COPY_DF: f64 = 1e-3; // P0b — probed residues 1.15e-4 and 7.2e-7
const TOL_P0C_TRI_EXACT: f64 = 0.02; // P0c — probed |Δ| = 3.0e-4 (0.04 σ_stat)
const TOL_P0D_FCC_KEY: f64 = 0.05; // P0d — probed |Δ| = 0.0148 (1.1 σ_stat), measured LOW
const PC_ST_EXTRAP_REG: f64 = 0.174911; // P1a — 5.8's own committed value
const TOL_P1A: f64 = 1e-5;
const SE_LO: f64 = 3.0e-4; // P1b — probed 5.14e-4
const SE_HI: f64 = 8.0e-4;
const R2_MAX: f64 = 0.50; // P1b — probed 0.2424 / 0.4050 / 0.1758
const P1C_SE_COVER: f64 = 1.5; // P1c — probed 0.81× (tri) and 0.55× (fcc)
const P1C_SPREAD_UNDER: f64 = 2.0; // P1c — probed 5.28× (tri) and 2.25× (fcc)
const SENS_LO: f64 = 80.0; // P2a — probed 113.4; LESSONS' ~117 and 5.6's 116.7 both in band
const SENS_HI: f64 = 150.0;
const ORDER_LO: f64 = 3e-4; // P2b — probed 5.42e-4
const ORDER_HI: f64 = 9e-4;
const BAND_LO: f64 = 0.045; // P2d — probed 0.0623
const BAND_HI: f64 = 0.090;
const P2D_OWN_SIGMA_FRACTION: f64 = 0.70; // P2d — probed 0.0478 / 0.06 = 0.80
const DF_ST_EXTRAP_REG: f64 = 2.49050; // P3a
const TOL_P3A: f64 = 0.01;
const P3B_CLOSE_FRACTION: f64 = 0.5; // P3b — probed 0.0325 / 0.08513 = 0.38
const Z_DISSOLVE: f64 = 2.0; // P3c — probed z = 1.69 / 1.73 / 0.52
const TOL_P4A_TRI: f64 = 2e-4; // P4a — probed −2.92e-5 against the EXACT 1/2
const TOL_P4B_FCC: f64 = 3e-4; // P4b — probed +1.49e-4

const DELTA_3D: f64 = 0.0006; // paired central-difference step, 3-D (probe-informed)
const DELTA_2D: f64 = 0.005; // 2-D: the amplification is ~10× gentler, so the step is ~10× wider
const DRIFT_W: f64 = 2.0; // fixed class drift exponent w = 1/ν + θ
const W_SCAN: [f64; 17] = [
    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6,
];
const W_STABLE_LO: usize = 6; // W_SCAN[6] = 1.6 — 5.8's stability sub-range, kept identical
const W_STABLE_HI: usize = 14; // W_SCAN[14] = 2.4
// 5.9's committed bond sensitivities (its data/verdict.csv + probe log) — report-only, for the
// cross-rung table showing the amplification is dimension- AND dilution-rule dependent.
const SENS_BOND_FCC_59: f64 = 275.7;
const SENS_BOND_STELLA_59: f64 = 340.1;

// ---------------- copied verbatim from uf5_6_stella_percolation_gate.rs ----------------

const LS_TRI_SWEEP: [usize; 6] = [16, 24, 32, 48, 64, 96];
const LS_TRI_MEAS: [usize; 5] = [24, 32, 48, 64, 96];
const LS_3D_SWEEP: [usize; 5] = [12, 18, 24, 36, 48];
const LS_3D_MEAS: [usize; 4] = [18, 24, 36, 48];
const SEED_SWEEP: u64 = 0x5EED; // batch k uses SEED_SWEEP ^ (k << 50)
const SEED_MEAS: u64 = 0xABCD;
const KBATCH: usize = 5;
const R_SWEEP: usize = 300;
const R_MEAS: usize = 2400;
const NSTRIPES: usize = 4;

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

struct Graph {
    n: usize,
    edges: Vec<(u32, u32, [i32; 3])>,
}

/// Triangular lattice as the square torus + one fixed diagonal per face (6-regular).
fn triangular(l: usize) -> Graph {
    let li = l as i64;
    let idx = |a: i64, b: i64| (a.rem_euclid(li) * li + b.rem_euclid(li)) as u32;
    let mut edges = Vec::with_capacity(3 * l * l);
    for a in 0..li {
        for b in 0..li {
            let u = idx(a, b);
            for d in [[1i64, 0], [0, 1], [1, 1]] {
                edges.push((u, idx(a + d[0], b + d[1]), [d[0] as i32, d[1] as i32, 0]));
            }
        }
    }
    Graph { n: l * l, edges }
}

/// FCC forward hops in the n-coordinates of rung 7.0 (a₁=(1,1,0), a₂=(0,1,1), a₃=(1,0,1)).
const FCC_FWD: [[i64; 3]; 6] = [[1, 0, 0], [0, 1, 0], [0, 0, 1], [1, -1, 0], [0, 1, -1], [-1, 0, 1]];
/// The long diagonals 2eₓ, 2e_y, 2e_z in n-coordinates (rung 7.0).
const LONG_N: [[i64; 3]; 3] = [[1, -1, 1], [1, 1, -1], [-1, 1, 1]];

fn fcc(m: usize) -> Graph {
    let mi = m as i64;
    let idx = |a: i64, b: i64, c: i64| {
        (a.rem_euclid(mi) * mi * mi + b.rem_euclid(mi) * mi + c.rem_euclid(mi)) as u32
    };
    let mut edges = Vec::with_capacity(6 * m * m * m);
    for a in 0..mi {
        for b in 0..mi {
            for c in 0..mi {
                let u = idx(a, b, c);
                for d in FCC_FWD {
                    edges.push((u, idx(a + d[0], b + d[1], c + d[2]), [d[0] as i32, d[1] as i32, d[2] as i32]));
                }
            }
        }
    }
    Graph { n: m * m * m, edges }
}

fn stella(m: usize) -> Graph {
    assert_eq!(m % 3, 0, "stella torus needs M ≡ 0 mod 3 (screw-rule consistency)");
    let mi = m as i64;
    let idx = |a: i64, b: i64, c: i64| {
        (a.rem_euclid(mi) * mi * mi + b.rem_euclid(mi) * mi + c.rem_euclid(mi)) as u32
    };
    let mut edges = Vec::with_capacity(7 * m * m * m);
    for a in 0..mi {
        for b in 0..mi {
            for c in 0..mi {
                let u = idx(a, b, c);
                for d in FCC_FWD {
                    edges.push((u, idx(a + d[0], b + d[1], c + d[2]), [d[0] as i32, d[1] as i32, d[2] as i32]));
                }
                let tau = ((a + b + c) % 3) as usize;
                let sclass = (2 * tau) % 3;
                let f = LONG_N[(sclass + 1) % 3];
                edges.push((u, idx(a + f[0], b + f[1], c + f[2]), [f[0] as i32, f[1] as i32, f[2] as i32]));
            }
        }
    }
    Graph { n: m * m * m, edges }
}

struct Uf {
    parent: Vec<u32>,
    off: Vec<[i32; 3]>,
    size: Vec<u32>,
    wrapped: Vec<bool>,
    path: Vec<u32>,
}
impl Uf {
    fn new(n: usize) -> Self {
        Uf {
            parent: (0..n as u32).collect(),
            off: vec![[0; 3]; n],
            size: vec![1; n],
            wrapped: vec![false; n],
            path: Vec::new(),
        }
    }
    fn find(&mut self, x: u32) -> (u32, [i32; 3]) {
        self.path.clear();
        let mut cur = x;
        while self.parent[cur as usize] != cur {
            self.path.push(cur);
            cur = self.parent[cur as usize];
        }
        let root = cur;
        let mut acc = [0i32; 3];
        for &n in self.path.iter().rev() {
            let node = n as usize;
            let o = self.off[node];
            acc = [acc[0] + o[0], acc[1] + o[1], acc[2] + o[2]];
            self.parent[node] = root;
            self.off[node] = acc;
        }
        (root, self.off[x as usize])
    }
    fn union(&mut self, u: u32, v: u32, d: [i32; 3]) {
        let (ru, ou) = self.find(u);
        let (rv, ov) = self.find(v);
        if ru == rv {
            let w = [ou[0] + d[0] - ov[0], ou[1] + d[1] - ov[1], ou[2] + d[2] - ov[2]];
            if w != [0, 0, 0] {
                self.wrapped[ru as usize] = true;
            }
            return;
        }
        let (big, small, os) = if self.size[ru as usize] >= self.size[rv as usize] {
            (ru, rv, [ou[0] + d[0] - ov[0], ou[1] + d[1] - ov[1], ou[2] + d[2] - ov[2]])
        } else {
            (rv, ru, [ov[0] - d[0] - ou[0], ov[1] - d[1] - ou[1], ov[2] - d[2] - ou[2]])
        };
        self.parent[small as usize] = big;
        self.off[small as usize] = os;
        self.size[big as usize] += self.size[small as usize];
        self.wrapped[big as usize] = self.wrapped[big as usize] || self.wrapped[small as usize];
    }
}

struct Obs {
    wrap: bool,
    pmax: f64,
}

/// Cluster statistics of a fixed SITE-occupation pattern: wrap-any indicator and `s_max/N`.
fn measure(g: &Graph, occ: &[bool]) -> Obs {
    let mut uf = Uf::new(g.n);
    for &(u, v, d) in &g.edges {
        if occ[u as usize] && occ[v as usize] {
            uf.union(u, v, d);
        }
    }
    let mut wrap = false;
    let mut smax = 0u32;
    for (i, &o) in occ.iter().enumerate() {
        if o && uf.parent[i] == i as u32 {
            if uf.wrapped[i] {
                wrap = true;
            }
            if uf.size[i] > smax {
                smax = uf.size[i];
            }
        }
    }
    Obs { wrap, pmax: smax as f64 / g.n as f64 }
}

/// One canonical sample: occupy sites i.i.d. with probability p under the seed, then measure.
fn sample(g: &Graph, p: f64, seed: u64) -> Obs {
    let mut r = Rng(seed);
    let occ: Vec<bool> = (0..g.n).map(|_| r.f() < p).collect();
    measure(g, &occ)
}

/// Sign-change crossings of consecutive-L wrapping curves, as (pair index, p*).
fn crossings_of(rw: &[Vec<f64>], ps: &[f64]) -> Vec<(usize, f64)> {
    let mut out = Vec::new();
    for a in 0..rw.len() - 1 {
        for pi in 0..ps.len() - 1 {
            let d1 = rw[a][pi] - rw[a + 1][pi];
            let d2 = rw[a][pi + 1] - rw[a + 1][pi + 1];
            if d1 == 0.0 && d2 == 0.0 {
                continue;
            }
            if d1 == 0.0 || d1 * d2 < 0.0 {
                let f = d1 / (d1 - d2);
                out.push((a, ps[pi] + f * (ps[pi + 1] - ps[pi])));
            }
        }
    }
    out
}

/// 5.6's registered naive estimator: mean of all crossings excluding the smallest-L pair.
fn crossing_estimate(crossings: &[(usize, f64)]) -> f64 {
    let kept: Vec<f64> = crossings.iter().filter(|(a, _)| *a > 0).map(|(_, x)| *x).collect();
    assert!(!kept.is_empty(), "no crossings above the smallest pair — window misses p_c");
    kept.iter().sum::<f64>() / kept.len() as f64
}

fn sweep_batch(build: &(dyn Fn(usize) -> Graph + Sync), ls: &[usize], ps: &[f64], seed0: u64) -> Vec<Vec<f64>> {
    let mut rw = vec![vec![0.0; ps.len()]; ls.len()];
    for (li, &l) in ls.iter().enumerate() {
        let g = build(l);
        let row: Vec<f64> = std::thread::scope(|sc| {
            let handles: Vec<_> = ps
                .iter()
                .enumerate()
                .map(|(pi, &p)| {
                    let g = &g;
                    sc.spawn(move || {
                        let mut w = 0.0;
                        for rep in 0..R_SWEEP {
                            let seed = seed0 ^ (l as u64) << 40 ^ (pi as u64) << 20 ^ rep as u64;
                            if sample(g, p, seed).wrap {
                                w += 1.0;
                            }
                        }
                        w / R_SWEEP as f64
                    })
                })
                .collect();
            handles.into_iter().map(|h| h.join().unwrap()).collect()
        });
        rw[li] = row;
    }
    rw
}

// ---------------- this rung's own measurement wrapper ----------------

/// FSS `d_f` at a fixed `p` from `s_max(L) ~ L^{d_f}` over the largest three sizes (the 5.1 rule),
/// with 5.6's `measure_at` seeds (`SEED_MEAS ^ (l<<40) ^ (rep<<2)`, **independent of `p`**, so two
/// `p`-points are a PAIRED comparison and a finite difference is far quieter than two independent
/// runs). The 4 seed stripes are independent sub-replicas of the whole fit, so `d_f`'s own
/// statistical error comes free via `kinematics::replica_stats` (the 5.5 rule).
fn df_at(build: &(dyn Fn(usize) -> Graph + Sync), ls: &[usize], p: f64, dim: f64) -> (f64, f64, Vec<f64>) {
    let mut per_stripe: Vec<Vec<f64>> = Vec::new();
    for &l in ls {
        let g = build(l);
        let row = std::thread::scope(|scope| {
            let handles: Vec<_> = (0..NSTRIPES)
                .map(|t| {
                    let g = &g;
                    scope.spawn(move || {
                        let (mut sp, mut n) = (0.0, 0usize);
                        let mut rep = t;
                        while rep < R_MEAS {
                            let seed = SEED_MEAS ^ (l as u64) << 40 ^ (rep as u64) << 2;
                            sp += sample(g, p, seed).pmax;
                            n += 1;
                            rep += NSTRIPES;
                        }
                        sp / n as f64
                    })
                })
                .collect();
            handles.into_iter().map(|h| h.join().unwrap()).collect::<Vec<f64>>()
        });
        per_stripe.push(row);
    }
    let lv: Vec<f64> = ls.iter().map(|&l| l as f64).collect();
    let k = ls.len();
    let pmax: Vec<f64> = per_stripe.iter().map(|r| r.iter().sum::<f64>() / NSTRIPES as f64).collect();
    let smax: Vec<f64> = pmax.iter().zip(ls).map(|(pm, &l)| pm * (l as f64).powf(dim)).collect();
    let df = power_law_fit(&lv[k - 3..], &smax[k - 3..]).exponent;
    let sub: Vec<f64> = (0..NSTRIPES)
        .map(|t| {
            let s: Vec<f64> =
                per_stripe.iter().zip(ls).map(|(r, &l)| r[t] * (l as f64).powf(dim)).collect();
            power_law_fit(&lv[k - 3..], &s[k - 3..]).exponent
        })
        .collect();
    let (_, sigma_df) = replica_stats(&sub);
    (df, sigma_df, smax)
}

// ---------------- 5.6's committed curves → pair crossings (5.8/5.9's pattern, a copy not an import) ----

struct Curve {
    ls: Vec<usize>,
    ps: Vec<f64>,
    rw: Vec<Vec<f64>>,
}

/// Parse 5.6's `lattice,L,p,R_wrap` CSV for one family. Keeps the original `{p:.4}` string as the
/// join key so float round-trips can never mismatch a lookup (5.8's convention).
fn load_curve(raw: &str, lattice: &str) -> Curve {
    let mut by_l: BTreeMap<usize, BTreeMap<String, f64>> = BTreeMap::new();
    for line in raw.lines().skip(1) {
        let f: Vec<&str> = line.split(',').collect();
        if f.len() < 4 || f[0] != lattice {
            continue;
        }
        let l: usize = f[1].parse().expect("bad L in 5.6's rw_curves.csv");
        let rw: f64 = f[3].parse().expect("bad R_wrap in 5.6's rw_curves.csv");
        by_l.entry(l).or_default().insert(f[2].to_string(), rw);
    }
    assert!(!by_l.is_empty(), "no rw_curves.csv rows for lattice {lattice}");
    let ls: Vec<usize> = by_l.keys().copied().collect();
    let p_keys: Vec<String> = by_l[&ls[0]].keys().cloned().collect();
    let ps: Vec<f64> = p_keys.iter().map(|s| s.parse().expect("bad p key")).collect();
    let rw: Vec<Vec<f64>> = ls.iter().map(|l| p_keys.iter().map(|k| by_l[l][k]).collect()).collect();
    Curve { ls, ps, rw }
}

/// Per-pair effective size `L_eff = √(L_a·L_b)` and crossing `p*`, one point per consecutive-L pair.
fn pair_crossings(ls: &[usize], ps: &[f64], rw: &[Vec<f64>]) -> (Vec<f64>, Vec<f64>) {
    let mut by_pair: BTreeMap<usize, Vec<f64>> = BTreeMap::new();
    for (a, x) in crossings_of(rw, ps) {
        by_pair.entry(a).or_default().push(x);
    }
    let mut sizes = Vec::new();
    let mut crossings = Vec::new();
    for (a, xs) in by_pair {
        sizes.push(((ls[a] * ls[a + 1]) as f64).sqrt());
        crossings.push(xs.iter().sum::<f64>() / xs.len() as f64);
    }
    (sizes, crossings)
}

/// Neighbor sets induced by a Graph's edge list.
fn neighbor_sets(g: &Graph) -> Vec<Vec<u32>> {
    let mut nbrs: Vec<Vec<u32>> = vec![Vec::new(); g.n];
    for &(u, v, _) in &g.edges {
        nbrs[u as usize].push(v);
        nbrs[v as usize].push(u);
    }
    for l in nbrs.iter_mut() {
        l.sort_unstable();
        l.dedup();
    }
    nbrs
}

/// Rung 7.0's rule-built stella torus adjacency (R9 oracle for the copied edge list).
fn stella_torus_adjacency(m: usize) -> Vec<Vec<u32>> {
    let mm = m as i64;
    let idx = |a: i64, b: i64, c: i64| {
        (a.rem_euclid(mm) * mm * mm + b.rem_euclid(mm) * mm + c.rem_euclid(mm)) as usize
    };
    let diffs_n: [[i64; 3]; 3] = [[1, -1, 0], [0, 1, -1], [-1, 0, 1]];
    let mut adj: Vec<Vec<u32>> = vec![Vec::new(); m * m * m];
    for a in 0..mm {
        for b in 0..mm {
            for c in 0..mm {
                let tau = ((a + b + c) % 3) as usize;
                let i = idx(a, b, c);
                let mut hops: Vec<[i64; 3]> = Vec::with_capacity(14);
                for d in [[1i64, 0, 0], [0, 1, 0], [0, 0, 1]] {
                    hops.push(d);
                    hops.push([-d[0], -d[1], -d[2]]);
                }
                for d in diffs_n {
                    hops.push(d);
                    hops.push([-d[0], -d[1], -d[2]]);
                }
                let sclass = (2 * tau) % 3;
                let f = LONG_N[(sclass + 1) % 3];
                let bk = LONG_N[(sclass + 2) % 3];
                hops.push(f);
                hops.push([-bk[0], -bk[1], -bk[2]]);
                for d in hops {
                    adj[i].push(idx(a + d[0], b + d[1], c + d[2]) as u32);
                }
            }
        }
    }
    adj
}

// ---------------- R9 unit tests — hand-derivable building blocks of the copy ----------------

#[test]
fn r9_ring_wraps_iff_fully_occupied() {
    // 1-D ring of 8, SITE semantics: only the full ring winds; holing one SITE leaves one cluster
    // of 7 (contrast 5.9's bond gate, where removing an EDGE leaves all 8 vertices connected).
    let n = 8usize;
    let edges: Vec<(u32, u32, [i32; 3])> =
        (0..n).map(|i| (i as u32, ((i + 1) % n) as u32, [1, 0, 0])).collect();
    let g = Graph { n, edges };
    let o = measure(&g, &vec![true; n]);
    assert!(o.wrap && (o.pmax - 1.0).abs() < 1e-15);
    let mut holed = vec![true; n];
    holed[3] = false;
    let o = measure(&g, &holed);
    assert!(!o.wrap, "a broken ring must not wind");
    assert!((o.pmax - 7.0 / 8.0).abs() < 1e-15, "one cluster of 7");
}

#[test]
fn r9_wrap_detects_a_straight_winding_row() {
    // triangular torus, one fully-occupied column: winds along a; broken, it must not.
    let l = 6usize;
    let g = triangular(l);
    let mut occ = vec![false; l * l];
    for a in 0..l {
        occ[a * l + 2] = true;
    }
    assert!(measure(&g, &occ).wrap);
    occ[3 * l + 2] = false;
    assert!(!measure(&g, &occ).wrap);
}

#[test]
fn r9_graphs_are_regular_and_match_rung_7_0_adjacency() {
    for (nb, z) in [
        (neighbor_sets(&triangular(8)), 6usize),
        (neighbor_sets(&fcc(6)), 12),
        (neighbor_sets(&stella(6)), 14),
    ] {
        for (i, l) in nb.iter().enumerate() {
            assert_eq!(l.len(), z, "vertex {i} is not {z}-distinct-regular");
            for &j in l {
                assert!(nb[j as usize].contains(&(i as u32)), "asymmetric hop {i}→{j}");
            }
        }
    }
    let ours = neighbor_sets(&stella(6));
    let oracle = stella_torus_adjacency(6);
    for (i, l) in ours.iter().enumerate() {
        let mut o = oracle[i].clone();
        o.sort_unstable();
        o.dedup();
        assert_eq!(*l, o, "copied edge list ≠ rung 7.0 adjacency at vertex {i}");
    }
}

#[test]
fn r9_crossing_interpolation_and_pair_folding_hand_case() {
    let ps = [0.3, 0.4];
    let rw = vec![vec![0.2, 0.4], vec![0.1, 0.5]];
    let cr = crossings_of(&rw, &ps);
    assert_eq!(cr.len(), 1);
    assert!((cr[0].1 - 0.35).abs() < 1e-15);
    let (sizes, crossings) = pair_crossings(&[10, 40], &ps, &rw);
    assert_eq!(sizes.len(), 1);
    assert!((sizes[0] - 20.0).abs() < 1e-12, "L_eff = √(10·40) = 20");
    assert!((crossings[0] - 0.35).abs() < 1e-15);
}

#[test]
fn r9_naive_estimator_drops_the_smallest_pair() {
    let est = crossing_estimate(&[(0, 0.10), (1, 0.20), (2, 0.30)]);
    assert!((est - 0.25).abs() < 1e-15, "est = {est}");
}

// ---------------- the gate (P0–P4) ----------------

/// One family's re-analysis of 5.6's committed aggregate curve.
struct Reanalysis {
    p_c: f64,
    stderr: f64,
    r2: f64,
    w_spread: f64,
    naive_all: f64,
    naive_excl: f64,
    sizes: Vec<f64>,
    crossings: Vec<f64>,
}

fn reanalyze(raw: &str, lattice: &str) -> Reanalysis {
    let c = load_curve(raw, lattice);
    let (sizes, crossings) = pair_crossings(&c.ls, &c.ps, &c.rw);
    let fit = crossing_extrapolate(&sizes, &crossings, DRIFT_W);
    let stable: Vec<f64> = (W_STABLE_LO..=W_STABLE_HI)
        .map(|i| crossing_extrapolate(&sizes, &crossings, W_SCAN[i]).p_c)
        .collect();
    let w_spread = stable.iter().cloned().fold(f64::MIN, f64::max)
        - stable.iter().cloned().fold(f64::MAX, f64::min);
    let n = crossings.len() as f64;
    Reanalysis {
        p_c: fit.p_c,
        stderr: fit.p_c_stderr,
        r2: fit.r2,
        w_spread,
        naive_all: crossings.iter().sum::<f64>() / n,
        naive_excl: crossings[1..].iter().sum::<f64>() / (n - 1.0),
        sizes,
        crossings,
    }
}

#[test]
fn uf5_10_site_locator_reprocess_gate() {
    rec!("\n######## lab/warp-5-universality/0510 — Warp-5.10: 5.8's locator on 5.6's SITE negative ########");
    rec!("FIREWALL (R3): site-diluted TOY graphs. p_c(stella-site) is a constant of THIS complex; d_f is");
    rec!("a percolation-class invariant — class-membership RESOLUTION, computed, not a materials claim.\n");
    let t0 = std::time::Instant::now();

    // ---- stage 1: 5.8's estimator on 5.6's committed aggregate curves (read-only) ----
    let src = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-5-universality/0506-stella-percolation/data/rw_curves.csv"
    );
    let raw = std::fs::read_to_string(src).expect("read 5.6's committed rw_curves.csv (read-only)");
    let tri = reanalyze(&raw, "triangular");
    let fc = reanalyze(&raw, "fcc");
    let st = reanalyze(&raw, "stella");
    for (name, r, key) in
        [("TRIANGULAR", &tri, Some(PC_TRI_EXACT)), ("FCC-SITE", &fc, Some(PC_FCC_LIT)), ("STELLA-SITE", &st, None)]
    {
        let best = crossing_extrapolate_best_w(&r.sizes, &r.crossings, &W_SCAN);
        rec!("[{name}] {} pair-crossings at L_eff {:?}", r.crossings.len(),
            r.sizes.iter().map(|s| (s * 100.0).round() / 100.0).collect::<Vec<_>>());
        rec!("  extrap(w={DRIFT_W}): p_c = {:.6} ± {:.6} (OLS intercept se)  r2 = {:.4}", r.p_c, r.stderr, r.r2);
        rec!("  w-scan best w = {:.1}; w∈[1.6,2.4] spread = {:.6} (5.8's yardstick)", best.drift_exponent, r.w_spread);
        rec!("  naive mean: all = {:.6}, excl smallest = {:.6}", r.naive_all, r.naive_excl);
        if let Some(k) = key {
            let e = (r.p_c - k).abs();
            rec!("  [P1c] |p_c − {k}| = {e:.6} = {:.2}× the OLS se, {:.2}× the w-spread   (naive-all err {:.6}, naive-excl err {:.6})",
                e / r.stderr, e / r.w_spread, (r.naive_all - k).abs(), (r.naive_excl - k).abs());
        }
    }

    // ---- stage 2: the ORDERING fork (#305) — re-runs 5.6's sweeps with 5.6's seeds ----
    let ps_tri: Vec<f64> = (0..7).map(|i| 0.485 + 0.005 * i as f64).collect();
    let ps_fcc: Vec<f64> = (0..7).map(|i| 0.193 + 0.002 * i as f64).collect();
    let ps_st: Vec<f64> = (0..8).map(|i| 0.170 + 0.002 * i as f64).collect();
    let mut pb: BTreeMap<&str, (f64, f64, f64, f64)> = BTreeMap::new();
    for (lat, build, ps, ls) in [
        ("triangular", &triangular as &(dyn Fn(usize) -> Graph + Sync), &ps_tri, &LS_TRI_SWEEP[..]),
        ("fcc", &fcc as &(dyn Fn(usize) -> Graph + Sync), &ps_fcc, &LS_3D_SWEEP[..]),
        ("stella", &stella as &(dyn Fn(usize) -> Graph + Sync), &ps_st, &LS_3D_SWEEP[..]),
    ] {
        let (mut ex, mut na) = (Vec::new(), Vec::new());
        for k in 0..KBATCH {
            let rw = sweep_batch(build, ls, ps, SEED_SWEEP ^ (k as u64) << 50);
            let (sz, cr) = pair_crossings(ls, ps, &rw);
            let fit = crossing_extrapolate(&sz, &cr, DRIFT_W);
            let naive = crossing_estimate(&crossings_of(&rw, ps));
            rec!("  [R8] {lat} batch {k}: naive(5.6's) = {naive:.6}  extrap = {:.6} (r2 = {:.4})  [{:?}]",
                fit.p_c, fit.r2, t0.elapsed());
            ex.push(fit.p_c);
            na.push(naive);
        }
        let (p_ex, s_ex) = replica_stats(&ex);
        let (p_na, s_na) = replica_stats(&na);
        rec!("[{lat}] per-batch EXTRAP {p_ex:.6} ± {s_ex:.6}   per-batch NAIVE (5.6's own) {p_na:.6} ± {s_na:.6}");
        pb.insert(lat, (p_ex, s_ex, p_na, s_na));
    }
    let ordering = (st.p_c - pb["stella"].0).abs();
    rec!("[P2b ORDERING SYSTEMATIC] stella: aggregate {:.6} vs per-batch {:.6} ⇒ |Δ| = {ordering:.6}", st.p_c, pb["stella"].0);
    let tri_agg_err = (tri.p_c - PC_TRI_EXACT).abs();
    let tri_pb_err = (pb["triangular"].0 - PC_TRI_EXACT).abs();
    let fcc_agg_err = (fc.p_c - PC_FCC_LIT).abs();
    let fcc_pb_err = (pb["fcc"].0 - PC_FCC_LIT).abs();
    rec!("[P2c ORDERING LICENCE — #305] triangular (EXACT key): aggregate {tri_agg_err:.6} vs per-batch {tri_pb_err:.6} ⇒ {} closer",
        if tri_pb_err < tri_agg_err { "PER-BATCH" } else { "AGGREGATE" });
    rec!("                              fcc-site (published):    aggregate {fcc_agg_err:.6} vs per-batch {fcc_pb_err:.6} ⇒ {} closer",
        if fcc_pb_err < fcc_agg_err { "PER-BATCH" } else { "AGGREGATE" });
    rec!("  (rung 5.9's single BOND key licensed the AGGREGATE ordering: 0.000360 vs 0.000588 — the OPPOSITE way)");

    // ---- stage 3: the d_f ladder on stella-site (paired seeds) ----
    let ladder: Vec<(&str, f64)> = vec![
        ("5.6-located", PC_ST_56),
        ("5.6-registered-constant", PC_ST_56_REG),
        ("per-batch-extrap", pb["stella"].0),
        ("extrap-minus-delta", st.p_c - DELTA_3D),
        ("extrap (5.8 locator)", st.p_c),
        ("extrap-plus-delta", st.p_c + DELTA_3D),
    ];
    let mut lad: Vec<(&str, f64, f64, f64, Vec<f64>)> = Vec::new();
    for (label, p) in &ladder {
        let (df, sig, smax) = df_at(&stella, &LS_3D_MEAS, *p, 3.0);
        rec!("  [R8] stella d_f @ {label:24} p = {p:.6} -> d_f = {df:.5} ± {sig:.5} (stat)  [{:?}]", t0.elapsed());
        lad.push((label, *p, df, sig, smax));
    }
    let (df_56, df_56_reg, df_pb) = (lad[0].2, lad[1].2, lad[2].2);
    let (df_new, sig_new) = (lad[4].2, lad[4].3);
    let sens = (lad[5].2 - lad[3].2) / (2.0 * DELTA_3D);
    let sens_56_secant = (DF_ST_56_REG - DF_ST_56) / (PC_ST_56_REG - PC_ST_56);
    let band = ((sens * st.stderr).powi(2) + sig_new * sig_new).sqrt();
    let miss_new = (df_new - DF_3D).abs();
    rec!("[P0b COPY FIDELITY] d_f @ 5.6's located p_c = {df_56:.5} vs committed {DF_ST_56} (|Δ| = {:.2e}); @ its registered constant = {df_56_reg:.5} vs committed {DF_ST_56_REG} (|Δ| = {:.2e})",
        (df_56 - DF_ST_56).abs(), (df_56_reg - DF_ST_56_REG).abs());
    rec!("[P2a LOCAL SENSITIVITY] ∂d_f/∂p at the new locator = {sens:.1}  (LESSONS ~117; 5.6's own secant recomputes to {sens_56_secant:.1} — both in the registered band)");
    rec!("[P2d BAND] √((sens·se)² + σ_stat²) = √(({:.4})² + ({sig_new:.4})²) = ±{band:.4} (1σ); 5.6's OWN quoted σ={SIG_ST_56} propagates to ±{:.4} = {:.0}% of its registered ±{TOL_DF_56_REGISTERED}",
        sens * st.stderr, sens_56_secant * SIG_ST_56, 100.0 * sens_56_secant * SIG_ST_56 / TOL_DF_56_REGISTERED);

    // the ordering-robust verdict: every candidate locator, each with ITS OWN quoted error
    let verdict_rows: Vec<(&str, f64, f64, f64, f64)> = vec![
        ("5.6's own located p_c", PC_ST_56, df_56, SIG_ST_56, lad[0].3),
        ("per-batch extrapolated", pb["stella"].0, df_pb, pb["stella"].1, lad[2].3),
        ("aggregate extrapolated", st.p_c, df_new, st.stderr, sig_new),
    ];
    let mut zs: Vec<(String, f64, f64, f64)> = Vec::new(); // (label, band, |Δ|, z)
    rec!("[P3c ORDERING-ROBUST VERDICT] each locator with its own quoted error:");
    for (label, p, df, loc_err, sig_stat) in &verdict_rows {
        let b = ((sens * loc_err).powi(2) + sig_stat * sig_stat).sqrt();
        let d = (df - DF_3D).abs();
        rec!("   {label:24} p={p:.6} d_f={df:.5} loc_err={loc_err:.6} band=±{b:.4} |Δ|={d:.4} z={:.2}", d / b);
        zs.push((label.to_string(), b, d, d / b));
    }

    // ---- stage 4: the ZERO-LOCATION-ERROR controls (one EXACT, one published) ----
    let (df_tri_key, sig_tri, smax_tri) = df_at(&triangular, &LS_TRI_MEAS, PC_TRI_EXACT, 2.0);
    let (df_tri_lo, _, _) = df_at(&triangular, &LS_TRI_MEAS, PC_TRI_EXACT - DELTA_2D, 2.0);
    let (df_tri_hi, _, _) = df_at(&triangular, &LS_TRI_MEAS, PC_TRI_EXACT + DELTA_2D, 2.0);
    let sens_tri = (df_tri_hi - df_tri_lo) / (2.0 * DELTA_2D);
    let inv_tri = PC_TRI_EXACT + (DF_2D_EXACT - df_tri_key) / sens_tri;
    rec!("[P0c EXACT ZERO-LOCATION-ERROR CONTROL] triangular d_f @ EXACTLY 1/2 = {df_tri_key:.5} ± {sig_tri:.5} vs the EXACT 91/48 = {DF_2D_EXACT:.6}; |Δ| = {:.5} ({:.2} σ_stat)",
        (df_tri_key - DF_2D_EXACT).abs(), (df_tri_key - DF_2D_EXACT).abs() / sig_tri);
    rec!("  sens_tri (paired, ±{DELTA_2D}) = {sens_tri:.1};  [P4a] inversion p = {inv_tri:.7} vs the EXACT 1/2 (err {:+.7})", inv_tri - PC_TRI_EXACT);
    let (df_fcc_key, sig_fcc, smax_fcc) = df_at(&fcc, &LS_3D_MEAS, PC_FCC_LIT, 3.0);
    let (df_fcc_ex, _, _) = df_at(&fcc, &LS_3D_MEAS, fc.p_c, 3.0);
    let sens_fcc = (df_fcc_key - df_fcc_ex) / (PC_FCC_LIT - fc.p_c);
    let inv_fcc = PC_FCC_LIT + (DF_3D - df_fcc_key) / sens_fcc;
    let inv_st = st.p_c + (DF_3D - df_new) / sens;
    rec!("[P0d PUBLISHED ZERO-LOCATION-ERROR CONTROL] fcc d_f @ {PC_FCC_LIT} = {df_fcc_key:.5} ± {sig_fcc:.5} vs class {DF_3D}; |Δ| = {:.5} (LOW — 5.6 pre-registered HIGH; see eval)",
        (df_fcc_key - DF_3D).abs());
    rec!("  sens_fcc = {sens_fcc:.1};  [P4b] inversion p = {inv_fcc:.7} vs {PC_FCC_LIT} (err {:+.7})", inv_fcc - PC_FCC_LIT);
    rec!("  derived: inversion (stella) = {inv_st:.6}, which is {:.1e} from 5.6's PRE-REGISTERED constant {PC_ST_56_REG} — not independent (it restates 5.6's own diagnosis arm), but it explains why that arm recovered the class value",
        (inv_st - PC_ST_56_REG).abs());
    rec!("[SENSITIVITY TABLE, report-only] 2-D site {sens_tri:.1} | 3-D site fcc {sens_fcc:.1} stella {sens:.1} | 3-D bond (5.9) fcc {SENS_BOND_FCC_59} stella {SENS_BOND_STELLA_59}");

    // ---- verdicts (the registered predictions, spec.md) ----
    let p0a = (pb["triangular"].2 - PC_TRI_56).abs() < TOL_COPY_PC
        && (pb["triangular"].3 - SIG_TRI_56).abs() < TOL_COPY_PC
        && (pb["fcc"].2 - PC_FCC_56).abs() < TOL_COPY_PC
        && (pb["fcc"].3 - SIG_FCC_56).abs() < TOL_COPY_PC
        && (pb["stella"].2 - PC_ST_56).abs() < TOL_COPY_PC
        && (pb["stella"].3 - SIG_ST_56).abs() < TOL_COPY_PC;
    let p0b = (df_56 - DF_ST_56).abs() < TOL_COPY_DF && (df_56_reg - DF_ST_56_REG).abs() < TOL_COPY_DF;
    let p0c = (df_tri_key - DF_2D_EXACT).abs() < TOL_P0C_TRI_EXACT;
    let p0d = (df_fcc_key - DF_3D).abs() < TOL_P0D_FCC_KEY;
    let p1a = (st.p_c - PC_ST_EXTRAP_REG).abs() < TOL_P1A && st.p_c > PC_ST_56;
    let p1b = (SE_LO..=SE_HI).contains(&st.stderr)
        && tri.r2 < R2_MAX
        && fc.r2 < R2_MAX
        && st.r2 < R2_MAX;
    let p1c = tri_agg_err < P1C_SE_COVER * tri.stderr
        && tri_agg_err > P1C_SPREAD_UNDER * tri.w_spread
        && fcc_agg_err < P1C_SE_COVER * fc.stderr
        && fcc_agg_err > P1C_SPREAD_UNDER * fc.w_spread;
    let p2a = (SENS_LO..=SENS_HI).contains(&sens)
        && (SENS_LO..=SENS_HI).contains(&sens_56_secant);
    let p2b = (ORDER_LO..=ORDER_HI).contains(&ordering) && st.p_c > pb["stella"].0;
    let p2c = tri_pb_err < tri_agg_err && fcc_pb_err < fcc_agg_err;
    let p2d = (BAND_LO..=BAND_HI).contains(&band)
        && sens_56_secant * SIG_ST_56 > P2D_OWN_SIGMA_FRACTION * TOL_DF_56_REGISTERED;
    let p3a = (df_new - DF_ST_EXTRAP_REG).abs() < TOL_P3A;
    let p3b = miss_new < P3B_CLOSE_FRACTION * MISS_56 && df_new > DF_ST_56;
    let p3c = zs.iter().all(|(_, _, _, z)| *z < Z_DISSOLVE);
    let p4a = (inv_tri - PC_TRI_EXACT).abs() < TOL_P4A_TRI;
    let p4b = (inv_fcc - PC_FCC_LIT).abs() < TOL_P4B_FCC;
    let p0 = p0a && p0b && p0c && p0d;
    let p1 = p1a && p1b && p1c;
    let p2 = p2a && p2b && p2c && p2d;
    let p3 = p3a && p3b && p3c;

    // ---- data (R10 source of truth) ----
    let dir = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-5-universality/0510-site-locator-reprocess/data"
    );
    std::fs::create_dir_all(dir).expect("create lab data dir");

    let mut ladder_csv = String::from("family,label,p,d_f,sigma_df,smax_a,smax_b,smax_c,smax_d,smax_e\n");
    for (label, p, df, sig, smax) in &lad {
        ladder_csv.push_str(&format!(
            "stella_site,{label},{p:.6},{df:.5},{sig:.5},{:.3},{:.3},{:.3},{:.3},\n",
            smax[0], smax[1], smax[2], smax[3]
        ));
    }
    ladder_csv.push_str(&format!(
        "triangular,exact key p=1/2 (0 loc err),{PC_TRI_EXACT:.6},{df_tri_key:.5},{sig_tri:.5},{:.3},{:.3},{:.3},{:.3},{:.3}\n",
        smax_tri[0], smax_tri[1], smax_tri[2], smax_tri[3], smax_tri[4]
    ));
    ladder_csv.push_str(&format!("triangular,exact key minus delta,{:.6},{df_tri_lo:.5},,,,,,\n", PC_TRI_EXACT - DELTA_2D));
    ladder_csv.push_str(&format!("triangular,exact key plus delta,{:.6},{df_tri_hi:.5},,,,,,\n", PC_TRI_EXACT + DELTA_2D));
    ladder_csv.push_str(&format!(
        "fcc_site,published key (0 loc err),{PC_FCC_LIT:.7},{df_fcc_key:.5},{sig_fcc:.5},{:.3},{:.3},{:.3},{:.3},\n",
        smax_fcc[0], smax_fcc[1], smax_fcc[2], smax_fcc[3]
    ));
    ladder_csv.push_str(&format!("fcc_site,extrap (5.8 locator),{:.7},{df_fcc_ex:.5},,,,,,\n", fc.p_c));
    std::fs::write(format!("{dir}/locator_ladder.csv"), ladder_csv).expect("write locator_ladder.csv");

    // `kind` separates a threshold estimate (a distance to an answer key is meaningful) from an
    // error-bar WIDTH — the 5.9 lesson; the figure reads that column. No commas inside any field.
    let mut est_csv = String::from("family,kind,estimator,p_c_or_width,error_bar,r2,err_vs_key\n");
    let key_of = |fam: &str| match fam {
        "triangular" => Some(PC_TRI_EXACT),
        "fcc_site" => Some(PC_FCC_LIT),
        _ => None,
    };
    let push = |csv: &mut String, fam: &str, kind: &str, name: &str, v: f64, eb: Option<f64>, r2: Option<f64>| {
        let err = if kind == "threshold" {
            key_of(fam).map(|k| format!("{:.6}", (v - k).abs())).unwrap_or_default()
        } else {
            String::new()
        };
        csv.push_str(&format!(
            "{fam},{kind},{name},{v:.7},{},{},{err}\n",
            eb.map(|e| format!("{e:.6}")).unwrap_or_default(),
            r2.map(|r| format!("{r:.4}")).unwrap_or_default()
        ));
    };
    for (fam, r, key) in
        [("triangular", &tri, "triangular"), ("fcc_site", &fc, "fcc"), ("stella_site", &st, "stella")]
    {
        let (p_ex, s_ex, p_na, s_na) = pb[key];
        push(&mut est_csv, fam, "threshold", "aggregate-extrapolated (w=2)", r.p_c, Some(r.stderr), Some(r.r2));
        push(&mut est_csv, fam, "threshold", "aggregate-naive (all pairs)", r.naive_all, None, None);
        push(&mut est_csv, fam, "threshold", "aggregate-naive (excl smallest)", r.naive_excl, None, None);
        push(&mut est_csv, fam, "threshold", "per-batch-extrapolated", p_ex, Some(s_ex), None);
        push(&mut est_csv, fam, "threshold", "per-batch-naive (5.6's registered)", p_na, Some(s_na), None);
        push(&mut est_csv, fam, "error_bar_candidate", "OLS intercept standard error", r.stderr, None, None);
        push(&mut est_csv, fam, "error_bar_candidate", "w-scan spread over w in [1.6..2.4] (5.8's yardstick)", r.w_spread, None, None);
        push(&mut est_csv, fam, "error_bar_candidate", "per-batch replica sigma", s_ex, None, None);
    }
    push(&mut est_csv, "triangular", "threshold", "EXACT (Sykes-Essam 1964 / Kesten 1980)", PC_TRI_EXACT, None, None);
    push(&mut est_csv, "fcc_site", "threshold", "published (Lorenz-Ziff 2000)", PC_FCC_LIT, None, None);
    push(&mut est_csv, "triangular", "threshold", "d_f-anchored inversion", inv_tri, None, None);
    push(&mut est_csv, "fcc_site", "threshold", "d_f-anchored inversion", inv_fcc, None, None);
    push(&mut est_csv, "stella_site", "threshold", "d_f-anchored inversion", inv_st, None, None);
    push(&mut est_csv, "triangular", "error_bar_candidate", "actual error of the aggregate-extrapolated fit vs the key", tri_agg_err, None, None);
    push(&mut est_csv, "fcc_site", "error_bar_candidate", "actual error of the aggregate-extrapolated fit vs the key", fcc_agg_err, None, None);
    push(&mut est_csv, "stella_site", "error_bar_candidate", "aggregate-vs-per-batch ordering systematic", ordering, None, None);
    push(&mut est_csv, "stella_site", "error_bar_candidate", "5.6's own replica sigma propagated through its own sensitivity", sens_56_secant * SIG_ST_56, None, None);
    std::fs::write(format!("{dir}/locator_estimates.csv"), est_csv).expect("write locator_estimates.csv");

    let mut pairs_csv = String::from("family,l_eff,p_star\n");
    for (fam, r) in [("triangular", &tri), ("fcc_site", &fc), ("stella_site", &st)] {
        for (l, c) in r.sizes.iter().zip(&r.crossings) {
            pairs_csv.push_str(&format!("{fam},{l:.4},{c:.6}\n"));
        }
    }
    std::fs::write(format!("{dir}/crossing_pairs.csv"), pairs_csv).expect("write crossing_pairs.csv");

    let mut wscan_csv = String::from("family,w,p_c\n");
    for (fam, r) in [("triangular", &tri), ("fcc_site", &fc), ("stella_site", &st)] {
        for &w in &W_SCAN {
            wscan_csv.push_str(&format!("{fam},{w:.1},{:.6}\n", crossing_extrapolate(&r.sizes, &r.crossings, w).p_c));
        }
    }
    std::fs::write(format!("{dir}/w_scan.csv"), wscan_csv).expect("write w_scan.csv");

    let mut zs_csv = String::from("locator,p,d_f,loc_err,band,abs_delta,z,dissolves\n");
    for ((label, b, d, z), (_, p, df, loc_err, _)) in zs.iter().zip(&verdict_rows) {
        zs_csv.push_str(&format!("{label},{p:.6},{df:.5},{loc_err:.6},{b:.4},{d:.4},{z:.2},{}\n", *z < Z_DISSOLVE));
    }
    std::fs::write(format!("{dir}/verdict_by_locator.csv"), zs_csv).expect("write verdict_by_locator.csv");

    let sens_csv = format!(
        "dimension,dilution,lattice,sensitivity,source\n\
         2,site,triangular,{sens_tri:.1},this run (paired ±{DELTA_2D})\n\
         3,site,fcc,{sens_fcc:.1},this run\n\
         3,site,stella,{sens:.1},this run (paired ±{DELTA_3D})\n\
         3,site,stella (5.6's secant),{sens_56_secant:.1},recomputed from 5.6's committed record\n\
         3,bond,fcc,{SENS_BOND_FCC_59},rung 5.9's committed record\n\
         3,bond,stella,{SENS_BOND_STELLA_59},rung 5.9's committed record\n"
    );
    std::fs::write(format!("{dir}/sensitivity_table.csv"), sens_csv).expect("write sensitivity_table.csv");

    let verdict_csv = format!(
        "prediction,quantity,measured,registered,pass\n\
         P0a,per-batch naive mean/sigma vs 5.6's committed (3 families),tri {:.6}/{:.6} fcc {:.6}/{:.6} st {:.6}/{:.6},5.6's committed values (±{TOL_COPY_PC}),{p0a}\n\
         P0b,d_f at 5.6's two quoted thresholds,{df_56:.5} | {df_56_reg:.5},{DF_ST_56} | {DF_ST_56_REG} (±{TOL_COPY_DF}),{p0b}\n\
         P0c,d_f (triangular) at the EXACT 1/2,{df_tri_key:.5},{DF_2D_EXACT:.6} exact (±{TOL_P0C_TRI_EXACT}),{p0c}\n\
         P0d,d_f (fcc) at the PUBLISHED threshold,{df_fcc_key:.5},{DF_3D} (±{TOL_P0D_FCC_KEY}),{p0d}\n\
         P1a,p_c (stella aggregate-extrapolated),{:.6},{PC_ST_EXTRAP_REG} (±{TOL_P1A}) and > {PC_ST_56},{p1a}\n\
         P1b,OLS se (stella) | r2 tri/fcc/stella,{:.6} | {:.4}/{:.4}/{:.4},se in [{SE_LO}..{SE_HI}] and all r2 < {R2_MAX},{p1b}\n\
         P1c,key error in units of (se | w-spread),tri {:.2}|{:.2}  fcc {:.2}|{:.2},< {P1C_SE_COVER} and > {P1C_SPREAD_UNDER} on BOTH keys,{p1c}\n\
         P2a,local d(d_f)/dp | 5.6's secant,{sens:.1} | {sens_56_secant:.1},both in [{SENS_LO}..{SENS_HI}],{p2a}\n\
         P2b,ordering systematic (stella),{ordering:.6},[{ORDER_LO}..{ORDER_HI}] aggregate higher,{p2b}\n\
         P2c,ordering licence on BOTH site keys,tri {tri_pb_err:.6} vs {tri_agg_err:.6} | fcc {fcc_pb_err:.6} vs {fcc_agg_err:.6},PER-BATCH closer on both (opposite to 5.9's bond key),{p2c}\n\
         P2d,propagated band | 5.6's own sigma propagated,{band:.4} | {:.4},band in [{BAND_LO}..{BAND_HI}] and 5.6's own > {P2D_OWN_SIGMA_FRACTION} x {TOL_DF_56_REGISTERED},{p2d}\n\
         P3a,d_f at the 5.8 locator,{df_new:.5},{DF_ST_EXTRAP_REG} (±{TOL_P3A}),{p3a}\n\
         P3b,|d_f − class| vs 5.6's miss,{miss_new:.4} vs {MISS_56},< {P3B_CLOSE_FRACTION} x 5.6's miss and upward,{p3b}\n\
         P3c,z at ALL THREE locators (ordering-robust),{:.2} | {:.2} | {:.2},all < {Z_DISSOLVE} (H-DISSOLVE branch),{p3c}\n\
         P4a,d_f-anchored inversion (triangular) vs the EXACT 1/2,{:+.7},±{TOL_P4A_TRI},{p4a}\n\
         P4b,d_f-anchored inversion (fcc) vs the published key,{:+.7},±{TOL_P4B_FCC},{p4b}\n\
         report-only,d_f at the per-batch-extrapolated locator,{df_pb:.5},—,\n\
         report-only,inversion (stella) vs 5.6's pre-registered constant,{inv_st:.6} vs {PC_ST_56_REG},— (not independent),\n\
         report-only,naive-vs-extrapolated accuracy on the keys,tri {:.6} vs {tri_agg_err:.6} | fcc {:.6} vs {fcc_agg_err:.6},— (naive closer on both),\n",
        pb["triangular"].2, pb["triangular"].3, pb["fcc"].2, pb["fcc"].3, pb["stella"].2, pb["stella"].3,
        st.p_c, st.stderr, tri.r2, fc.r2, st.r2,
        tri_agg_err / tri.stderr, tri_agg_err / tri.w_spread, fcc_agg_err / fc.stderr, fcc_agg_err / fc.w_spread,
        sens_56_secant * SIG_ST_56,
        zs[0].3, zs[1].3, zs[2].3,
        inv_tri - PC_TRI_EXACT, inv_fcc - PC_FCC_LIT,
        (tri.naive_all - PC_TRI_EXACT).abs(), (fc.naive_excl - PC_FCC_LIT).abs()
    );
    std::fs::write(format!("{dir}/verdict.csv"), verdict_csv).expect("write verdict.csv");

    let seeds = format!(
        "purpose,value\nsweep_base,0x{SEED_SWEEP:X} ^ (k<<50)\nmeasure_base,0x{SEED_MEAS:X}\n\
         kbatch,{KBATCH}\nr_sweep,{R_SWEEP}\nr_meas,{R_MEAS}\nstripes,{NSTRIPES}\n\
         drift_exponent_w,{DRIFT_W}\ndelta_p 3-D (paired central difference),{DELTA_3D}\n\
         delta_p 2-D (paired central difference),{DELTA_2D}\n\
         input (read-only),lab/warp-5-universality/0506-stella-percolation/data/rw_curves.csv\n"
    );
    std::fs::write(format!("{dir}/seeds.csv"), seeds).expect("write seeds.csv");

    let verdict = if p0 && p1 && p2 && p3 && p4a && p4b {
        format!(
            "5.6's SITE d_f NEGATIVE DISSOLVES TOO — AND IT WAS INSIDE AN ERROR BAR 5.6 COULD HAVE \
             COMPUTED FROM ITS OWN PUBLISHED NUMBERS. Applying 5.8's crossing-drift locator to 5.6's \
             committed SITE curves moves the stella threshold from 5.6's {PC_ST_56} to {:.6} ± {:.6} \
             (the fit's own OLS intercept standard error), and d_f there rises from 5.6's {DF_ST_56} \
             to {df_new:.5} ± {sig_new:.5} — inside 5.6's OWN registered ±{TOL_DF_56_REGISTERED} band, \
             closing {:.0}% of its {MISS_56} miss. But the sharper statement needs no new estimator at \
             all: 5.6's own quoted replica error {SIG_ST_56}, propagated through the amplification 5.6 \
             ITSELF measured ({sens_56_secant:.1}), is ±{:.4} — {:.0}% of the ±{TOL_DF_56_REGISTERED} \
             band it registered. Every candidate locator dissolves (z = {:.2} / {:.2} / {:.2} for 5.6's \
             own, per-batch-extrapolated and aggregate-extrapolated), so unlike 5.9 the verdict does \
             NOT depend on the estimator-ordering fork. The machinery is exonerated against an EXACT \
             answer at both ends: triangular d_f at exactly p = 1/2 is {df_tri_key:.5} vs the exact \
             91/48 = {DF_2D_EXACT:.6} — {:.5}, or {:.2} of one statistical sigma. And #305 gets its \
             honest answer: on BOTH site keys the PER-BATCH ordering is the more accurate one \
             (tri {tri_pb_err:.6} vs {tri_agg_err:.6}; fcc {fcc_pb_err:.6} vs {fcc_agg_err:.6}), the \
             OPPOSITE of 5.9's single bond key — so the ordering has NO universal licence and must be \
             registered per rung. The inverted locator, anchored on the exact 2-D exponent, recovers \
             the exact threshold 1/2 to {:+.7}. FIREWALL (R3): 🔵 graph mathematics of a toy complex \
             and class-membership resolution, computed — never a claim about matter.",
            st.p_c, st.stderr, 100.0 * (1.0 - miss_new / MISS_56), sens_56_secant * SIG_ST_56,
            100.0 * sens_56_secant * SIG_ST_56 / TOL_DF_56_REGISTERED,
            zs[0].3, zs[1].3, zs[2].3, (df_tri_key - DF_2D_EXACT).abs(),
            (df_tri_key - DF_2D_EXACT).abs() / sig_tri, inv_tri - PC_TRI_EXACT
        )
    } else {
        format!(
            "CHECK (R5) — p0={p0} (a={p0a} b={p0b} c={p0c} d={p0d}) p1={p1} (a={p1a} b={p1b} c={p1c}) \
             p2={p2} (a={p2a} b={p2b} c={p2c} d={p2d}) p3={p3} (a={p3a} b={p3b} c={p3c}) p4a={p4a} p4b={p4b}; \
             p_c(stella extrap) = {:.6} ± {:.6}; d_f = {df_new:.5}; sens = {sens:.1}; band = ±{band:.4}; \
             z = {:.2}/{:.2}/{:.2}; ordering = {ordering:.6}. If any z ≥ {Z_DISSOLVE} at the licensed \
             locator this is the pre-registered H-CERTIFY branch (spec.md P3c), NOT a broken rung. \
             FIREWALL (R3).",
            st.p_c, st.stderr, zs[0].3, zs[1].3, zs[2].3
        )
    };
    rec!("\n[lab/0510 VERDICT] {verdict}");
    rec!("\n  [recorded: p0a={p0a} p0b={p0b} p0c={p0c} p0d={p0d} p1a={p1a} p1b={p1b} p1c={p1c} p2a={p2a} p2b={p2b} p2c={p2c} p2d={p2d} p3a={p3a} p3b={p3b} p3c={p3c} p4a={p4a} p4b={p4b} \
        pc_extrap={:.6} se={:.6} df_new={df_new:.5} sig_df={sig_new:.5} sens={sens:.1} sens_tri={sens_tri:.1} sens_fcc={sens_fcc:.1} band={band:.4} z=({:.2},{:.2},{:.2}) ordering={ordering:.6} \
        df_tri_key={df_tri_key:.5} df_fcc_key={df_fcc_key:.5} inv_tri={inv_tri:.7} inv_fcc={inv_fcc:.7} inv_st={inv_st:.6} elapsed={:?}]",
        st.p_c, st.stderr, zs[0].3, zs[1].3, zs[2].3, t0.elapsed());

    assert!(p0a, "P0a: the re-run sweeps must reproduce 5.6's committed per-batch estimates for all three families");
    assert!(p0b, "P0b: d_f at 5.6's two quoted thresholds must reproduce its committed {DF_ST_56} and {DF_ST_56_REG} (got {df_56:.5}, {df_56_reg:.5})");
    assert!(p0c, "P0c: at the EXACT triangular threshold 1/2, d_f must recover the EXACT 91/48 (got {df_tri_key:.5})");
    assert!(p0d, "P0d: at the PUBLISHED fcc-site threshold, d_f must recover the class value (got {df_fcc_key:.5})");
    assert!(p1a, "P1a: the extrapolated stella locator must reproduce {PC_ST_EXTRAP_REG} and sit above 5.6's (got {:.6})", st.p_c);
    assert!(p1b, "P1b: se = {:.6} in [{SE_LO},{SE_HI}] and r2 {:.4}/{:.4}/{:.4} all < {R2_MAX}", st.stderr, tri.r2, fc.r2, st.r2);
    assert!(p1c, "P1c: on BOTH keys the OLS se must cover the real error and the w-spread must not (tri {:.2}/{:.2}, fcc {:.2}/{:.2})",
        tri_agg_err / tri.stderr, tri_agg_err / tri.w_spread, fcc_agg_err / fc.stderr, fcc_agg_err / fc.w_spread);
    assert!(p2a, "P2a: the local sensitivity {sens:.1} and 5.6's own secant {sens_56_secant:.1} must both land in [{SENS_LO},{SENS_HI}]");
    assert!(p2b, "P2b: the ordering systematic must land in [{ORDER_LO},{ORDER_HI}] with the aggregate arm higher (got {ordering:.6})");
    assert!(p2c, "P2c (#305): on BOTH site answer keys the per-batch ordering must be closer (tri {tri_pb_err:.6} vs {tri_agg_err:.6}; fcc {fcc_pb_err:.6} vs {fcc_agg_err:.6})");
    assert!(p2d, "P2d: band {band:.4} in [{BAND_LO},{BAND_HI}], and 5.6's own sigma propagated ({:.4}) must exceed {P2D_OWN_SIGMA_FRACTION} x its registered {TOL_DF_56_REGISTERED}", sens_56_secant * SIG_ST_56);
    assert!(p3a, "P3a: d_f at the 5.8 locator must reproduce {DF_ST_EXTRAP_REG} (got {df_new:.5})");
    assert!(p3b, "P3b: the better locator must close ≥{P3B_CLOSE_FRACTION} of 5.6's {MISS_56} miss, upward (got {miss_new:.4}, d_f {df_new:.5} vs {DF_ST_56})");
    assert!(p3c, "P3c: the registered H-DISSOLVE branch needs z < {Z_DISSOLVE} at ALL THREE locators (got {:.2}/{:.2}/{:.2}); any z ≥ {Z_DISSOLVE} at the licensed locator is the pre-registered H-CERTIFY outcome — see spec.md",
        zs[0].3, zs[1].3, zs[2].3);
    assert!(p4a, "P4a: the d_f-anchored inversion must recover the EXACT triangular 1/2 to ±{TOL_P4A_TRI} (got {:+.7})", inv_tri - PC_TRI_EXACT);
    assert!(p4b, "P4b: the d_f-anchored inversion must recover the published fcc-site threshold to ±{TOL_P4B_FCC} (got {:+.7})", inv_fcc - PC_FCC_LIT);
}
