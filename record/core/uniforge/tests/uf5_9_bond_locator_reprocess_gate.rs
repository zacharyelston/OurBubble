//! lab/warp-5-universality/0509 — Warp-5.9: reprocess rung 5.7's `d_f` NEGATIVE with rung 5.8's
//! crossing-drift locator. Menu row: "apply 5.8's estimator to 5.7 (bond)".
//!
//! 5.7 registered a first-class negative: on the stella tet-oct graph under BOND dilution, `d_f`
//! measured at the crossing-located threshold missed the 3-D percolation-class value 2.52295 badly
//! (2.028 at the located `p_c`, 1.906 at a differently-windowed pre-registered constant), predicted
//! in advance from a probed `∂d_f/∂p ≈ 338`. 5.8 then built a better locator (fit the pair-crossing
//! drift `p*(L_eff) = p_c + c·L_eff^{-w}`, take the intercept) and demonstrated it on 5.6's SITE
//! curves only. This gate applies it to 5.7's committed BOND curves and decides, on numbers
//! registered before the run (spec.md), between:
//!   • H-DISSOLVE — at a locator whose error is honestly quantified, `d_f` is statistically
//!     consistent with the class value ⇒ 5.7's miss was the LOCATOR (registered branch, `z < 2`);
//!   • H-CERTIFY  — the miss survives ⇒ the negative stands harder, scoped to this family/graph at
//!     `L ≤ 48`, with the next discriminator named in advance (`L` up to ~96–128).
//!
//! Because the question IS "how much locator error is there", the locator's own error bar is the
//! first thing measured — `kinematics::CrossingExtrapolation::p_c_stderr`, added by this rung — and
//! it is calibrated against a published answer key at ZERO location error (FCC-bond,
//! `p_c = 0.1201635(10)`, Lorenz & Ziff, PRE 57, 230 (1998); Tarasevich & van der Marck, IJMPC 10,
//! 1193 (1999)). A `w`-scan spread — 5.8's stability yardstick — is NOT that error bar: P1c gates
//! the difference.
//!
//! The percolation machinery below (`Rng`, `Graph`, `fcc`, `stella`, `Uf`, `measure`, `sample`,
//! `crossings_of`, `sweep_batch`, the `measure_at` seed scheme) is **copied verbatim** from
//! `uf5_7_stella_bond_percolation_gate.rs` — 5.7's gate and its `data/` are the immutable record and
//! are never modified. Copy fidelity is gated, not assumed: P0a reproduces 5.7's committed per-batch
//! threshold estimates and P0b its committed `d_f`. (One deliberate difference: `measure` does not
//! accumulate the χ' second moment, which no arm of this rung uses — R7 forbids a dead field. The
//! RNG, the edge draw order, the union-find and the `s_max` path are unchanged.)
//!
//! Run: `cargo test -p uniforge --release --test uf5_9_bond_locator_reprocess_gate -- --nocapture` (~55 s)
//!
//! FIREWALL (R3): edge-diluted TOY graphs. `p_c(stella-bond)` is a 🔵 constant of THIS complex
//! (graph mathematics, never a property of matter); `d_f` is a dimensionless universal invariant of
//! the 3-D percolation class — class-membership resolution, computed, never a materials claim, and
//! where a previous miss dissolves it dissolves into a statement about OUR estimator, not nature.

use kinematics::{crossing_extrapolate, crossing_extrapolate_best_w, power_law_fit, replica_stats};
use std::collections::BTreeMap;
use std::io::Write;

macro_rules! rec {
    ($($a:tt)*) => {{ eprintln!($($a)*); let _ = std::io::stderr().flush(); }};
}

// ---- answer keys (independent of anything this repo computed) ----
const PC_FCC_BOND_LIT: f64 = 0.120_163_5; // Lorenz & Ziff 1998; Tarasevich & van der Marck 1999
const DF_3D: f64 = 2.522_95; // = 3 − β/ν, β/ν = 0.47705(15) (Wang et al., PRE 87, 052107 (2013))

// ---- 5.7's committed record (read-only inputs / oracles; data/percolation_summary.csv) ----
const PC_ST_57: f64 = 0.099641;
const SIG_ST_57: f64 = 0.000312;
const DF_ST_57: f64 = 2.02762;
const MISS_57: f64 = 0.495_33; // |2.02762 − 2.52295|, 5.7's registered miss

// ---- the registered predictions (spec.md, committed before the run) ----
const TOL_P0A: f64 = 1e-6; // 5.7's numbers are printed to 6 decimals — the paper trail's resolution
const TOL_P0B: f64 = 1e-3; // probed residue 1.62e-4 = 340 × the 6-decimal rounding of 5.7's p_c
const TOL_P0C_DF_AT_KEY: f64 = 0.05; // probed |d_f(p_lit) − class| = 0.0035 (0.27 σ_stat)
const PC_ST_EXTRAP_REG: f64 = 0.100648; // P1a target (deterministic re-analysis)
const TOL_P1A: f64 = 1e-5;
const SE_LO: f64 = 3.0e-4; // P1b: the fit's OLS intercept standard error (probed 5.18e-4)
const SE_HI: f64 = 8.0e-4;
const R2_MAX: f64 = 0.30; // P1b: the drift is NOT resolvable in bond data (probed 0.0022 / 0.1527)
const P1C_SE_COVER: f64 = 2.5; // P1c: |err| < 2.5 × stderr   (probed 1.10 ×)
const P1C_SPREAD_UNDER: f64 = 3.0; // P1c: |err| > 3 × w-spread (probed 6.09 ×)
const SENS_LO: f64 = 250.0; // P2a: local paired ∂d_f/∂p at the NEW locator (probed 340.1)
const SENS_HI: f64 = 450.0;
const ORDER_LO: f64 = 8e-4; // P2b: the aggregate-vs-per-batch ordering systematic (probed 1.330e-3)
const ORDER_HI: f64 = 2e-3;
const BAND_LO: f64 = 0.10; // P2d: the propagated 1σ band in d_f (probed 0.1766)
const BAND_HI: f64 = 0.30;
const DF_ST_EXTRAP_REG: f64 = 2.37985; // P3a target
const TOL_P3A: f64 = 0.01;
const P3B_CLOSE_FRACTION: f64 = 0.5; // P3b: close at least half of 5.7's registered miss
const Z_DISSOLVE: f64 = 2.0; // P3c: z < 2 ⇒ H-DISSOLVE (registered branch; probed z = 0.81)
const TOL_P4A_INVERSION: f64 = 5e-5; // P4a: the inverted estimator vs the answer key (probed 1.28e-5)

const DELTA_P: f64 = 0.0006; // P2a's paired central-difference step (probe-informed)
const DRIFT_W: f64 = 2.0; // fixed class drift exponent w = 1/ν + θ ≈ 1.141 + 0.86 (Wang et al. 2013)
const W_SCAN: [f64; 17] = [
    1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6,
];
const W_STABLE_LO: usize = 6; // W_SCAN[6] = 1.6 — 5.8's stability sub-range, kept identical
const W_STABLE_HI: usize = 14; // W_SCAN[14] = 2.4

// ---------------- copied verbatim from uf5_7_stella_bond_percolation_gate.rs ----------------

const LS_3D_SWEEP: [usize; 5] = [12, 18, 24, 36, 48];
const LS_3D_MEAS: [usize; 4] = [18, 24, 36, 48];
const SEED_SWEEP: u64 = 0x5EED; // batch k uses SEED_SWEEP ^ (k << 50) — shared across families
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

/// Cluster statistics of a fixed BOND-occupation pattern: every VERTEX counts (bond percolation
/// keeps every site present — a vertex touching no occupied edge is its own size-1 cluster).
fn measure(g: &Graph, edge_occ: &[bool]) -> Obs {
    let mut uf = Uf::new(g.n);
    for (ei, &(u, v, d)) in g.edges.iter().enumerate() {
        if edge_occ[ei] {
            uf.union(u, v, d);
        }
    }
    let mut wrap = false;
    let mut smax = 0u32;
    for i in 0..g.n {
        if uf.parent[i] == i as u32 {
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

/// One canonical BOND sample: occupy each EDGE i.i.d. with probability p (drawn in edge-list order).
fn sample(g: &Graph, p: f64, seed: u64) -> Obs {
    let mut r = Rng(seed);
    let edge_occ: Vec<bool> = (0..g.edges.len()).map(|_| r.f() < p).collect();
    measure(g, &edge_occ)
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

/// 5.7's registered naive estimator: mean of all crossings excluding the smallest-L pair.
fn crossing_estimate(crossings: &[(usize, f64)]) -> f64 {
    let kept: Vec<f64> = crossings.iter().filter(|(a, _)| *a > 0).map(|(_, x)| *x).collect();
    assert!(!kept.is_empty(), "no crossings above the smallest pair — window misses p_c");
    kept.iter().sum::<f64>() / kept.len() as f64
}

/// One batch's wrapping-probability sweep: R(p) per (L, p); seeds fixed per (L, p-index, rep).
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

/// FSS `d_f` at a fixed `p`, from `s_max(L) ~ L^{d_f}` over the largest three sizes (the 5.1 rule).
/// Seeds are 5.7's `measure_at` scheme (`SEED_MEAS ^ (l<<40) ^ (rep<<2)`, **independent of `p`**), so
/// two `p`-points are a PAIRED comparison and a finite difference is far less noisy than two
/// independent runs. The 4 seed stripes are independent sub-replicas of the whole fit, so `d_f`'s own
/// statistical error comes free via `kinematics::replica_stats` (the 5.5 rule).
fn df_at(build: &(dyn Fn(usize) -> Graph + Sync), ls: &[usize], p: f64) -> (f64, f64, Vec<f64>) {
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
    let smax: Vec<f64> = pmax.iter().zip(ls).map(|(pm, &l)| pm * (l as f64).powi(3)).collect();
    let df = power_law_fit(&lv[k - 3..], &smax[k - 3..]).exponent;
    let sub: Vec<f64> = (0..NSTRIPES)
        .map(|t| {
            let s: Vec<f64> =
                per_stripe.iter().zip(ls).map(|(r, &l)| r[t] * (l as f64).powi(3)).collect();
            power_law_fit(&lv[k - 3..], &s[k - 3..]).exponent
        })
        .collect();
    let (_, sigma_df) = replica_stats(&sub);
    (df, sigma_df, smax)
}

// ---------------- 5.7's committed curves → pair crossings (5.8's pattern, a copy not an import) ----

struct Curve {
    ls: Vec<usize>,
    ps: Vec<f64>,
    rw: Vec<Vec<f64>>,
}

/// Parse 5.7's `lattice,L,p,R_wrap` CSV for one family. Keeps the original `{p:.4}` string as the
/// join key so float round-trips can never mismatch a lookup (5.8's convention).
fn load_curve(raw: &str, lattice: &str) -> Curve {
    let mut by_l: BTreeMap<usize, BTreeMap<String, f64>> = BTreeMap::new();
    for line in raw.lines().skip(1) {
        let f: Vec<&str> = line.split(',').collect();
        if f.len() < 4 || f[0] != lattice {
            continue;
        }
        let l: usize = f[1].parse().expect("bad L in 5.7's rw_curves.csv");
        let rw: f64 = f[3].parse().expect("bad R_wrap in 5.7's rw_curves.csv");
        by_l.entry(l).or_default().insert(f[2].to_string(), rw);
    }
    assert!(!by_l.is_empty(), "no rw_curves.csv rows for lattice {lattice}");
    let ls: Vec<usize> = by_l.keys().copied().collect();
    let p_keys: Vec<String> = by_l[&ls[0]].keys().cloned().collect();
    let ps: Vec<f64> = p_keys.iter().map(|s| s.parse().expect("bad p key")).collect();
    let rw: Vec<Vec<f64>> = ls.iter().map(|l| p_keys.iter().map(|k| by_l[l][k]).collect()).collect();
    Curve { ls, ps, rw }
}

/// Per-pair effective size `L_eff = √(L_a·L_b)` and crossing `p*`, one point per consecutive-L pair
/// (multiple sign-changes inside one pair are averaged first — 5.8's rule).
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
    // 1-D ring of 8, BOND semantics: only the full ring winds; removing one EDGE leaves ONE
    // 8-vertex path (every vertex present), unwound — the site/bond distinction, in one assert.
    let n = 8usize;
    let edges: Vec<(u32, u32, [i32; 3])> =
        (0..n).map(|i| (i as u32, ((i + 1) % n) as u32, [1, 0, 0])).collect();
    let g = Graph { n, edges };
    let o = measure(&g, &vec![true; n]);
    assert!(o.wrap && (o.pmax - 1.0).abs() < 1e-15);
    let mut opened = vec![true; n];
    opened[3] = false;
    let o = measure(&g, &opened);
    assert!(!o.wrap, "an opened ring must not wind");
    assert!((o.pmax - 1.0).abs() < 1e-15, "an opened ring is still one path of all 8 vertices");
}

#[test]
fn r9_graphs_are_regular_and_match_rung_7_0_adjacency() {
    for (nb, z) in [(neighbor_sets(&fcc(6)), 12usize), (neighbor_sets(&stella(6)), 14)] {
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
    // two straight lines crossing at p = 0.35 exactly (5.6/5.7/5.8's shared hand case)
    let ps = [0.3, 0.4];
    let rw = vec![vec![0.2, 0.4], vec![0.1, 0.5]];
    let cr = crossings_of(&rw, &ps);
    assert_eq!(cr.len(), 1);
    assert!((cr[0].1 - 0.35).abs() < 1e-15);
    // …and the pair folding gives one point at the geometric-mean effective size
    let (sizes, crossings) = pair_crossings(&[10, 40], &ps, &rw);
    assert_eq!(sizes.len(), 1);
    assert!((sizes[0] - 20.0).abs() < 1e-12, "L_eff = √(10·40) = 20");
    assert!((crossings[0] - 0.35).abs() < 1e-15);
}

#[test]
fn r9_naive_estimator_drops_the_smallest_pair() {
    // 5.7's registered estimator, in one hand case: pair 0 is excluded, pairs 1 and 2 averaged.
    let est = crossing_estimate(&[(0, 0.10), (1, 0.20), (2, 0.30)]);
    assert!((est - 0.25).abs() < 1e-15, "est = {est}");
}

// ---------------- the gate (P0–P4) ----------------

/// One family's re-analysis of 5.7's committed aggregate curve.
struct Reanalysis {
    p_c: f64,
    stderr: f64,
    r2: f64,
    w_spread: f64,
    best_w: f64,
    best_p_c: f64,
    naive_all: f64,
    naive_excl: f64,
    sizes: Vec<f64>,
    crossings: Vec<f64>,
}

fn reanalyze(raw: &str, lattice: &str) -> Reanalysis {
    let c = load_curve(raw, lattice);
    let (sizes, crossings) = pair_crossings(&c.ls, &c.ps, &c.rw);
    let fit = crossing_extrapolate(&sizes, &crossings, DRIFT_W);
    let best = crossing_extrapolate_best_w(&sizes, &crossings, &W_SCAN);
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
        best_w: best.drift_exponent,
        best_p_c: best.p_c,
        naive_all: crossings.iter().sum::<f64>() / n,
        naive_excl: crossings[1..].iter().sum::<f64>() / (n - 1.0),
        sizes,
        crossings,
    }
}

#[test]
fn uf5_9_bond_locator_reprocess_gate() {
    rec!("\n######## lab/warp-5-universality/0509 — Warp-5.9: 5.8's locator on 5.7's bond negative ########");
    rec!("FIREWALL (R3): edge-diluted TOY graphs. p_c(stella-bond) is a constant of THIS complex; d_f is");
    rec!("a 3-D-percolation-class invariant — class-membership RESOLUTION, computed, not a materials claim.\n");
    let t0 = std::time::Instant::now();

    // ---- stage 1: 5.8's estimator on 5.7's committed aggregate curves (read-only) ----
    let src = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-5-universality/0507-stella-bond-percolation/data/rw_curves.csv"
    );
    let raw = std::fs::read_to_string(src).expect("read 5.7's committed rw_curves.csv (read-only)");
    let st = reanalyze(&raw, "stella_bond");
    let fc = reanalyze(&raw, "fcc_bond");
    for (name, r) in [("STELLA-BOND", &st), ("FCC-BOND", &fc)] {
        rec!("[{name}] {} pair-crossings at L_eff {:?}", r.crossings.len(),
            r.sizes.iter().map(|s| (s * 100.0).round() / 100.0).collect::<Vec<_>>());
        rec!("  p* = {:?}", r.crossings.iter().map(|c| (c * 1e6).round() / 1e6).collect::<Vec<_>>());
        rec!("  extrap(w={DRIFT_W}): p_c = {:.6} ± {:.6} (OLS intercept se)  r2 = {:.4}", r.p_c, r.stderr, r.r2);
        rec!("  w-scan best: w = {:.1} p_c = {:.6};  w∈[1.6,2.4] spread = {:.6} (5.8's yardstick)", r.best_w, r.best_p_c, r.w_spread);
        rec!("  naive mean of pair-crossings: all = {:.6}, excl smallest = {:.6}", r.naive_all, r.naive_excl);
    }
    let fcc_key_err = (fc.p_c - PC_FCC_BOND_LIT).abs();
    rec!("[P1c ANSWER-KEY CALIBRATION] |p_c(fcc) − {PC_FCC_BOND_LIT}| = {fcc_key_err:.6} = {:.2}× the OLS se, {:.2}× the w-spread",
        fcc_key_err / fc.stderr, fcc_key_err / fc.w_spread);
    rec!("  (naive aggregate mean's own error vs the key: {:.6})", (fc.naive_all - PC_FCC_BOND_LIT).abs());

    // ---- stage 2: the estimator-ORDERING systematic (re-runs 5.7's sweep, 5.7's seeds) ----
    let ps_st: Vec<f64> = (0..8).map(|i| 0.094 + 0.002 * i as f64).collect();
    let ps_fcc: Vec<f64> = (0..7).map(|i| 0.114 + 0.002 * i as f64).collect();
    let mut per_batch: BTreeMap<&str, (f64, f64, f64, f64, Vec<f64>, Vec<f64>)> = BTreeMap::new();
    for (fam, build, ps) in [
        ("stella_bond", &stella as &(dyn Fn(usize) -> Graph + Sync), &ps_st),
        ("fcc_bond", &fcc as &(dyn Fn(usize) -> Graph + Sync), &ps_fcc),
    ] {
        let (mut ex, mut na) = (Vec::new(), Vec::new());
        for k in 0..KBATCH {
            let rw = sweep_batch(build, &LS_3D_SWEEP, ps, SEED_SWEEP ^ (k as u64) << 50);
            let (sizes, crossings) = pair_crossings(&LS_3D_SWEEP, ps, &rw);
            let fit = crossing_extrapolate(&sizes, &crossings, DRIFT_W);
            let naive = crossing_estimate(&crossings_of(&rw, ps));
            rec!("  [R8] {fam} batch {k}: naive(5.7's) = {naive:.6}  extrap = {:.6} (r2 = {:.4})  [{:?}]",
                fit.p_c, fit.r2, t0.elapsed());
            ex.push(fit.p_c);
            na.push(naive);
        }
        let (p_ex, s_ex) = replica_stats(&ex);
        let (p_na, s_na) = replica_stats(&na);
        rec!("[{fam}] per-batch EXTRAP {p_ex:.6} ± {s_ex:.6}   per-batch NAIVE (5.7's own) {p_na:.6} ± {s_na:.6}");
        per_batch.insert(fam, (p_ex, s_ex, p_na, s_na, ex, na));
    }
    let (pb_st_ex, pb_st_sig, pb_st_na, pb_st_na_sig, _, _) = per_batch["stella_bond"].clone();
    let (pb_fc_ex, pb_fc_sig, pb_fc_na, pb_fc_na_sig, _, _) = per_batch["fcc_bond"].clone();
    let ordering = (st.p_c - pb_st_ex).abs();
    rec!("[P2b ORDERING SYSTEMATIC] stella: aggregate-then-extrapolate {:.6} vs extrapolate-then-average {pb_st_ex:.6} ⇒ |Δ| = {ordering:.6}", st.p_c);
    rec!("  (5.7's bond window systematic, the one 5.8 set out to remove: 0.00036; per-batch replica σ: {pb_st_sig:.6})");
    let err_agg = (fc.p_c - PC_FCC_BOND_LIT).abs();
    let err_pb = (pb_fc_ex - PC_FCC_BOND_LIT).abs();
    rec!("[P2c ORDERING LICENSE] fcc vs the key: aggregate {err_agg:.6} vs per-batch {err_pb:.6} (per-batch naive, 5.7's own: {:.6})",
        (pb_fc_na - PC_FCC_BOND_LIT).abs());

    // ---- stage 3: the d_f ladder at the new locator (paired seeds) ----
    let ladder: Vec<(&str, f64)> = vec![
        ("5.7-located", PC_ST_57),
        ("per-batch-extrap", pb_st_ex),
        ("extrap-minus-delta", st.p_c - DELTA_P),
        ("extrap (5.8 locator)", st.p_c),
        ("extrap-plus-delta", st.p_c + DELTA_P),
    ];
    let mut lad: Vec<(&str, f64, f64, f64, Vec<f64>)> = Vec::new();
    for (label, p) in &ladder {
        let (df, sig, smax) = df_at(&stella, &LS_3D_MEAS, *p);
        rec!("  [R8] stella d_f @ {label:20} p = {p:.6} -> d_f = {df:.5} ± {sig:.5} (stat)  [{:?}]", t0.elapsed());
        lad.push((label, *p, df, sig, smax));
    }
    let df_57 = lad[0].2;
    let df_pb = lad[1].2;
    let (df_new, sig_new) = (lad[3].2, lad[3].3);
    let sens = (lad[4].2 - lad[2].2) / (2.0 * DELTA_P);
    let band = ((sens * st.stderr).powi(2) + sig_new * sig_new).sqrt();
    let miss_new = (df_new - DF_3D).abs();
    let z = miss_new / band;
    rec!("[P0b COPY FIDELITY] d_f @ 5.7's own located p_c = {df_57:.5} vs 5.7's committed {DF_ST_57} (|Δ| = {:.2e}; expected ≈ sens × the 6-decimal rounding of p_c)", (df_57 - DF_ST_57).abs());
    rec!("[P2a LOCAL SENSITIVITY] ∂d_f/∂p at the new locator = {sens:.1} (5.7's secant over the LOWER interval: 337.6)");
    rec!("[P2d PROPAGATED BAND] √((sens·se)² + σ_stat²) = √(({:.4})² + ({sig_new:.4})²) = ±{band:.4} (1σ)", sens * st.stderr);
    rec!("[P3 VERDICT INPUTS] d_f(new locator) = {df_new:.5}; |d_f − {DF_3D}| = {miss_new:.4}; 5.7's miss = {MISS_57}; z = {z:.2}");

    // ---- stage 4: the FCC-bond zero-location-error control + the inverted estimator ----
    let (df_key, sig_key, smax_key) = df_at(&fcc, &LS_3D_MEAS, PC_FCC_BOND_LIT);
    let (df_fcc_ex, sig_fcc_ex, smax_fcc_ex) = df_at(&fcc, &LS_3D_MEAS, fc.p_c);
    let sens_fcc = (df_key - df_fcc_ex) / (PC_FCC_BOND_LIT - fc.p_c);
    let inv_fcc = PC_FCC_BOND_LIT + (DF_3D - df_key) / sens_fcc;
    let inv_st = st.p_c + (DF_3D - df_new) / sens;
    rec!("[P0c ZERO-LOCATION-ERROR LICENSE] fcc d_f @ the PUBLISHED {PC_FCC_BOND_LIT} = {df_key:.5} ± {sig_key:.5}; |Δ vs class| = {:.5}", (df_key - DF_3D).abs());
    rec!("  fcc d_f @ its extrapolated locator {:.7} = {df_fcc_ex:.5} ± {sig_fcc_ex:.5}; sens_fcc = {sens_fcc:.1}", fc.p_c);
    rec!("[P4a INVERTED ESTIMATOR vs THE KEY] p_c(d_f-anchored, fcc) = {inv_fcc:.7} vs {PC_FCC_BOND_LIT} (err {:+.7})", inv_fcc - PC_FCC_BOND_LIT);
    rec!("  derived (not independent — algebraically P3c in p-space): p_c(d_f-anchored, stella) = {inv_st:.6}, |Δ vs the 5.8 locator| = {:.6} = {:.2}× its se",
        (inv_st - st.p_c).abs(), (inv_st - st.p_c).abs() / st.stderr);

    // ---- verdicts (the registered predictions, spec.md) ----
    let p0a = (pb_st_na - PC_ST_57).abs() < TOL_P0A && (pb_st_na_sig - SIG_ST_57).abs() < TOL_P0A;
    let p0b = (df_57 - DF_ST_57).abs() < TOL_P0B;
    let p0c = (df_key - DF_3D).abs() < TOL_P0C_DF_AT_KEY;
    let p1a = (st.p_c - PC_ST_EXTRAP_REG).abs() < TOL_P1A && st.p_c > PC_ST_57;
    let p1b = (SE_LO..=SE_HI).contains(&st.stderr) && st.r2 < R2_MAX && fc.r2 < R2_MAX;
    let p1c = fcc_key_err < P1C_SE_COVER * fc.stderr && fcc_key_err > P1C_SPREAD_UNDER * fc.w_spread;
    let p2a = (SENS_LO..=SENS_HI).contains(&sens);
    let p2b = (ORDER_LO..=ORDER_HI).contains(&ordering) && st.p_c > pb_st_ex;
    let p2c = err_agg < err_pb;
    let p2d = (BAND_LO..=BAND_HI).contains(&band);
    let p3a = (df_new - DF_ST_EXTRAP_REG).abs() < TOL_P3A;
    let p3b = miss_new < P3B_CLOSE_FRACTION * MISS_57 && df_new > DF_ST_57;
    let p3c = z < Z_DISSOLVE;
    let p4a = (inv_fcc - PC_FCC_BOND_LIT).abs() < TOL_P4A_INVERSION;
    let p0 = p0a && p0b && p0c;
    let p1 = p1a && p1b && p1c;
    let p2 = p2a && p2b && p2c && p2d;
    let p3 = p3a && p3b && p3c;

    // ---- data (R10 source of truth) ----
    let dir = concat!(
        env!("CARGO_MANIFEST_DIR"),
        "/../../lab/warp-5-universality/0509-bond-locator-reprocess/data"
    );
    std::fs::create_dir_all(dir).expect("create lab data dir");

    let mut ladder_csv = String::from("family,label,p,d_f,sigma_df,smax_18,smax_24,smax_36,smax_48\n");
    for (label, p, df, sig, smax) in &lad {
        ladder_csv.push_str(&format!(
            "stella_bond,{label},{p:.6},{df:.5},{sig:.5},{:.3},{:.3},{:.3},{:.3}\n",
            smax[0], smax[1], smax[2], smax[3]
        ));
    }
    // 5.7's own registered-constant arm, carried over from its committed record so the money plot
    // shows the FULL locator span (read-only — this rung never re-measures 5.7's numbers).
    ladder_csv.push_str("stella_bond,5.7-registered-constant (from 0507 data),0.099280,1.90585,,1008.468,1916.692,4259.792,7160.165\n");
    for (label, p, df, sig, smax) in [
        ("published key (0 loc err)", PC_FCC_BOND_LIT, df_key, sig_key, &smax_key),
        ("extrap (5.8 locator)", fc.p_c, df_fcc_ex, sig_fcc_ex, &smax_fcc_ex),
    ] {
        ladder_csv.push_str(&format!(
            "fcc_bond,{label},{p:.7},{df:.5},{sig:.5},{:.3},{:.3},{:.3},{:.3}\n",
            smax[0], smax[1], smax[2], smax[3]
        ));
    }
    std::fs::write(format!("{dir}/locator_ladder.csv"), ladder_csv).expect("write locator_ladder.csv");

    // `kind` separates rows that ARE a threshold estimate (so a distance to the published FCC key is
    // meaningful) from rows that are an error-bar CANDIDATE (a width — comparing a width to a
    // threshold would be nonsense; the figure reads that column).
    let mut est_csv = String::from("family,kind,estimator,p_c_or_width,error_bar,r2,err_vs_key\n");
    let push_est = |csv: &mut String,
                    fam: &str,
                    kind: &str,
                    name: &str,
                    v: f64,
                    eb: Option<f64>,
                    r2: Option<f64>| {
        let err = if kind == "threshold" && fam == "fcc_bond" {
            format!("{:.6}", (v - PC_FCC_BOND_LIT).abs())
        } else {
            String::new()
        };
        let ebs = eb.map(|e| format!("{e:.6}")).unwrap_or_default();
        let r2s = r2.map(|r| format!("{r:.4}")).unwrap_or_default();
        csv.push_str(&format!("{fam},{kind},{name},{v:.7},{ebs},{r2s},{err}\n"));
    };
    for (fam, r, pb_ex, pb_sig, pb_na, pb_na_sig) in [
        ("stella_bond", &st, pb_st_ex, pb_st_sig, pb_st_na, pb_st_na_sig),
        ("fcc_bond", &fc, pb_fc_ex, pb_fc_sig, pb_fc_na, pb_fc_na_sig),
    ] {
        push_est(&mut est_csv, fam, "threshold", "aggregate-extrapolated (w=2)", r.p_c, Some(r.stderr), Some(r.r2));
        push_est(&mut est_csv, fam, "threshold", "aggregate-naive (all pairs)", r.naive_all, None, None);
        push_est(&mut est_csv, fam, "threshold", "aggregate-naive (excl smallest)", r.naive_excl, None, None);
        push_est(&mut est_csv, fam, "threshold", "per-batch-extrapolated", pb_ex, Some(pb_sig), None);
        push_est(&mut est_csv, fam, "threshold", "per-batch-naive (5.7's registered)", pb_na, Some(pb_na_sig), None);
        push_est(&mut est_csv, fam, "error_bar_candidate", "OLS intercept standard error", r.stderr, None, None);
        push_est(&mut est_csv, fam, "error_bar_candidate", "w-scan spread over w in [1.6..2.4] (5.8's yardstick)", r.w_spread, None, None);
        push_est(&mut est_csv, fam, "error_bar_candidate", "per-batch replica sigma", pb_sig, None, None);
    }
    push_est(&mut est_csv, "fcc_bond", "threshold", "published (Lorenz-Ziff 1998)", PC_FCC_BOND_LIT, None, None);
    push_est(&mut est_csv, "fcc_bond", "threshold", "d_f-anchored inversion", inv_fcc, None, None);
    push_est(&mut est_csv, "stella_bond", "threshold", "d_f-anchored inversion", inv_st, None, None);
    push_est(&mut est_csv, "fcc_bond", "error_bar_candidate", "actual error of the aggregate-extrapolated fit vs the key", fcc_key_err, None, None);
    push_est(&mut est_csv, "stella_bond", "error_bar_candidate", "aggregate-vs-per-batch ordering systematic", ordering, None, None);
    std::fs::write(format!("{dir}/locator_estimates.csv"), est_csv).expect("write locator_estimates.csv");

    let mut pairs_csv = String::from("family,l_eff,p_star\n");
    for (fam, r) in [("stella_bond", &st), ("fcc_bond", &fc)] {
        for (l, c) in r.sizes.iter().zip(&r.crossings) {
            pairs_csv.push_str(&format!("{fam},{l:.4},{c:.6}\n"));
        }
    }
    std::fs::write(format!("{dir}/crossing_pairs.csv"), pairs_csv).expect("write crossing_pairs.csv");

    let mut wscan_csv = String::from("family,w,p_c\n");
    for (fam, r) in [("stella_bond", &st), ("fcc_bond", &fc)] {
        for &w in &W_SCAN {
            wscan_csv.push_str(&format!(
                "{fam},{w:.1},{:.6}\n",
                crossing_extrapolate(&r.sizes, &r.crossings, w).p_c
            ));
        }
    }
    std::fs::write(format!("{dir}/w_scan.csv"), wscan_csv).expect("write w_scan.csv");

    let verdict_csv = format!(
        "prediction,quantity,measured,registered,pass\n\
         P0a,stella per-batch naive mean / sigma (5.7 copy fidelity),{pb_st_na:.6} / {pb_st_na_sig:.6},{PC_ST_57} / {SIG_ST_57} (±{TOL_P0A}),{p0a}\n\
         P0b,d_f at 5.7's located p_c,{df_57:.5},{DF_ST_57} (±{TOL_P0B}),{p0b}\n\
         P0c,d_f (fcc) at the PUBLISHED threshold,{df_key:.5},{DF_3D} (±{TOL_P0C_DF_AT_KEY}),{p0c}\n\
         P1a,p_c (stella aggregate-extrapolated),{:.6},{PC_ST_EXTRAP_REG} (±{TOL_P1A}) and > {PC_ST_57},{p1a}\n\
         P1b,OLS intercept se (stella) / r2 stella / r2 fcc,{:.6} / {:.4} / {:.4},[{SE_LO}..{SE_HI}] / both < {R2_MAX},{p1b}\n\
         P1c,fcc key error in units of (se | w-spread),{:.2} / {:.2},< {P1C_SE_COVER} and > {P1C_SPREAD_UNDER},{p1c}\n\
         P2a,local ∂d_f/∂p at the new locator,{sens:.1},[{SENS_LO}..{SENS_HI}],{p2a}\n\
         P2b,ordering systematic (aggregate vs per-batch),{ordering:.6},[{ORDER_LO}..{ORDER_HI}] aggregate higher,{p2b}\n\
         P2c,fcc key error aggregate vs per-batch,{err_agg:.6} vs {err_pb:.6},aggregate closer,{p2c}\n\
         P2d,propagated 1-sigma band in d_f,{band:.4},[{BAND_LO}..{BAND_HI}],{p2d}\n\
         P3a,d_f at the 5.8 locator,{df_new:.5},{DF_ST_EXTRAP_REG} (±{TOL_P3A}),{p3a}\n\
         P3b,|d_f − class| vs 5.7's miss,{miss_new:.4} vs {MISS_57},< {P3B_CLOSE_FRACTION} × 5.7's miss and upward,{p3b}\n\
         P3c,z = |d_f − class| / band (DISSOLVE if < 2),{z:.2},< {Z_DISSOLVE} (H-DISSOLVE branch),{p3c}\n\
         P4a,d_f-anchored inversion (fcc) vs the published key,{:+.7},±{TOL_P4A_INVERSION},{p4a}\n\
         report-only,d_f at the per-batch-extrapolated locator,{df_pb:.5},—,\n\
         report-only,p_c(d_f-anchored | stella) [derived | = P3c in p-space],{inv_st:.6},—,\n\
         report-only,fcc aggregate-naive error vs the key,{:.6},— (vs extrapolated {err_agg:.6}),\n",
        st.p_c, st.stderr, st.r2, fc.r2, fcc_key_err / fc.stderr, fcc_key_err / fc.w_spread,
        inv_fcc - PC_FCC_BOND_LIT, (fc.naive_all - PC_FCC_BOND_LIT).abs()
    );
    std::fs::write(format!("{dir}/verdict.csv"), verdict_csv).expect("write verdict.csv");

    let seeds = format!(
        "purpose,value\nsweep_base,0x{SEED_SWEEP:X} ^ (k<<50)\nmeasure_base,0x{SEED_MEAS:X}\n\
         kbatch,{KBATCH}\nr_sweep,{R_SWEEP}\nr_meas,{R_MEAS}\nstripes,{NSTRIPES}\n\
         drift_exponent_w,{DRIFT_W}\ndelta_p (paired central difference),{DELTA_P}\n\
         input (read-only),lab/warp-5-universality/0507-stella-bond-percolation/data/rw_curves.csv\n"
    );
    std::fs::write(format!("{dir}/seeds.csv"), seeds).expect("write seeds.csv");

    let verdict = if p0 && p1 && p2 && p3 && p4a {
        format!(
            "5.7's d_f NEGATIVE DISSOLVES INTO THE LOCATOR — AND THE ESTIMATOR THAT DISSOLVED IT \
             NEEDED ITS OWN ERROR BAR FIRST. Applying 5.8's crossing-drift locator to 5.7's \
             committed BOND curves moves the stella threshold from 5.7's naive {PC_ST_57} up to \
             {:.6} ± {:.6} (the fit's own OLS intercept standard error), and d_f there rises from \
             5.7's {DF_ST_57} to {df_new:.5} ± {sig_new:.5} — closing {:.0}% of 5.7's registered \
             {MISS_57} miss and landing {z:.2}σ from the 3-D percolation-class value {DF_3D} once \
             the locator's error is propagated through the measured sensitivity ({sens:.0}, band \
             ±{band:.4}). The machinery is exonerated at zero location error: on FCC-bond at the \
             PUBLISHED threshold, d_f = {df_key:.5} vs class {DF_3D} ({:.4}). Three things the \
             estimator's own record did not have, now measured: (1) a w-scan spread is NOT the \
             locator's error bar — on the answer key the real error is {:.2}× the standard error \
             but {:.2}× the w-spread; (2) aggregate-then-extrapolate and extrapolate-then-average \
             differ by {ordering:.6}, ~3.7× the window systematic 5.8 was built to remove, and the \
             answer key licenses the aggregate ordering ({err_agg:.6} vs {err_pb:.6}); (3) on bond \
             data the drift is unresolvable (r2 = {:.4}), so this locator is better-CENTRED, not a \
             better fit. Inverting the same steep sensitivity gives a licensed by-product: anchoring \
             d_f at the class value recovers the published FCC-bond threshold to {:+.7}. VERDICT: \
             5.7's registered scope-statement stands verbatim; its interpretation is upgraded — the \
             miss measured OUR ESTIMATOR, not the lattice. FIREWALL (R3): 🔵 graph mathematics of a \
             toy complex and class-membership resolution, computed — never a claim about matter.",
            st.p_c, st.stderr, 100.0 * (1.0 - miss_new / MISS_57), (df_key - DF_3D).abs(),
            fcc_key_err / fc.stderr, fcc_key_err / fc.w_spread, st.r2,
            inv_fcc - PC_FCC_BOND_LIT
        )
    } else {
        format!(
            "CHECK (R5) — p0={p0} (a={p0a} b={p0b} c={p0c}) p1={p1} (a={p1a} b={p1b} c={p1c}) \
             p2={p2} (a={p2a} b={p2b} c={p2c} d={p2d}) p3={p3} (a={p3a} b={p3b} c={p3c}) p4a={p4a}; \
             p_c(stella extrap) = {:.6} ± {:.6}; d_f = {df_new:.5} ± {sig_new:.5}; sens = {sens:.1}; \
             band = ±{band:.4}; z = {z:.2}; ordering = {ordering:.6}. If z ≥ {Z_DISSOLVE} this is the \
             pre-registered H-CERTIFY branch (spec.md P3c), NOT a broken rung: the bond d_f miss \
             survives a better-centred locator with a propagated band, scoped to this family/graph at \
             L ≤ 48, and the named next discriminator is L up to ~96-128 at fixed locator. \
             FIREWALL (R3).",
            st.p_c, st.stderr
        )
    };
    rec!("\n[lab/0509 VERDICT] {verdict}");
    rec!("\n  [recorded: p0a={p0a} p0b={p0b} p0c={p0c} p1a={p1a} p1b={p1b} p1c={p1c} p2a={p2a} p2b={p2b} p2c={p2c} p2d={p2d} p3a={p3a} p3b={p3b} p3c={p3c} p4a={p4a} \
        pc_extrap={:.6} se={:.6} r2_st={:.4} r2_fcc={:.4} wspread_fcc={:.6} df_new={df_new:.5} sig_df={sig_new:.5} sens={sens:.1} band={band:.4} z={z:.2} \
        ordering={ordering:.6} pb_extrap={pb_st_ex:.6} df_pb={df_pb:.5} df_key={df_key:.5} inv_fcc={inv_fcc:.7} inv_st={inv_st:.6} elapsed={:?}]",
        st.p_c, st.stderr, st.r2, fc.r2, fc.w_spread, t0.elapsed());

    assert!(p0a, "P0a: the re-run sweep must reproduce 5.7's committed per-batch estimates ({pb_st_na:.6} ± {pb_st_na_sig:.6} vs {PC_ST_57} ± {SIG_ST_57})");
    assert!(p0b, "P0b: d_f at 5.7's located p_c must reproduce 5.7's committed {DF_ST_57} (got {df_57:.5})");
    assert!(p0c, "P0c: at the PUBLISHED FCC-bond threshold (zero location error) d_f must recover the class value (got {df_key:.5} vs {DF_3D})");
    assert!(p1a, "P1a: the extrapolated stella locator must reproduce {PC_ST_EXTRAP_REG} and sit above 5.7's (got {:.6})", st.p_c);
    assert!(p1b, "P1b: se = {:.6} in [{SE_LO},{SE_HI}], r2 stella {:.4} / fcc {:.4} both < {R2_MAX}", st.stderr, st.r2, fc.r2);
    assert!(p1c, "P1c: on the answer key the OLS se must cover the real error and the w-spread must not ({:.2}× se, {:.2}× spread)", fcc_key_err / fc.stderr, fcc_key_err / fc.w_spread);
    assert!(p2a, "P2a: local ∂d_f/∂p at the new locator must land in [{SENS_LO},{SENS_HI}] (got {sens:.1})");
    assert!(p2b, "P2b: the ordering systematic must land in [{ORDER_LO},{ORDER_HI}] with the aggregate arm higher (got {ordering:.6})");
    assert!(p2c, "P2c: the answer key must license the aggregate ordering ({err_agg:.6} vs per-batch {err_pb:.6})");
    assert!(p2d, "P2d: the propagated band must land in [{BAND_LO},{BAND_HI}] (got {band:.4})");
    assert!(p3a, "P3a: d_f at the 5.8 locator must reproduce {DF_ST_EXTRAP_REG} (got {df_new:.5})");
    assert!(p3b, "P3b: the better locator must close ≥{P3B_CLOSE_FRACTION} of 5.7's {MISS_57} miss, upward (got {miss_new:.4}, d_f {df_new:.5} vs {DF_ST_57})");
    assert!(p3c, "P3c: the registered H-DISSOLVE branch needs z < {Z_DISSOLVE} (got z = {z:.2}); z ≥ {Z_DISSOLVE} is the pre-registered H-CERTIFY outcome — see spec.md");
    assert!(p4a, "P4a: the d_f-anchored inversion must recover the published FCC-bond threshold to ±{TOL_P4A_INVERSION} (got {:+.7})", inv_fcc - PC_FCC_BOND_LIT);
}
