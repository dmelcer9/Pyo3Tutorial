use std::time::Instant;
use pyo3::prelude::*;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pyfunction};
use rand::rngs::SmallRng;
use rand::{Rng, SeedableRng, seq::SliceRandom};

use crate::TreeImpl;

fn build_i64_tree(keys: &[i64]) -> TreeImpl<i64> {
    let mut t = TreeImpl::Leaf { key: keys[0], values: vec![keys[0]] };
    for &k in &keys[1..] {
        t = t.add(k, k);
    }
    t
}

#[pyclass]
#[gen_stub_pyclass]
pub struct Scenario {
    #[pyo3(get)]
    pub name: String,
    #[pyo3(get)]
    pub n: usize,
    #[pyo3(get)]
    pub seconds: f64,
    #[pyo3(get)]
    pub ops_per_sec: f64,
}

#[pyclass]
#[gen_stub_pyclass]
pub struct BenchmarkResults {
    #[pyo3(get)]
    pub label: String,
    #[pyo3(get)]
    pub scenarios: Vec<Py<Scenario>>,
}

#[gen_stub_pyfunction]
#[pyfunction]
#[pyo3(signature = (sizes=None, n_queries=10_000, seed=42, label=None))]
pub fn benchmark_rust(
    py: Python<'_>,
    sizes: Option<Vec<usize>>,
    n_queries: usize,
    seed: u64,
    label: Option<String>,
) -> PyResult<Py<BenchmarkResults>> {
    let sizes = sizes.unwrap_or_else(|| vec![1_000, 3_000]);
    let label = label.unwrap_or_else(|| "rust_native".to_string());
    let mut rng = SmallRng::seed_from_u64(seed);
    let mut scenarios: Vec<Py<Scenario>> = Vec::new();

    macro_rules! record {
        ($name:expr, $n:expr, $secs:expr) => {
            scenarios.push(Py::new(py, Scenario {
                name: $name,
                n: $n,
                seconds: $secs,
                ops_per_sec: $n as f64 / $secs,
            })?);
        };
    }

    for &n in &sizes {
        let asc: Vec<i64> = (0..n as i64).collect();
        let desc: Vec<i64> = (0..n as i64).rev().collect();
        let mut rand: Vec<i64> = (0..n as i64).collect();
        rand.shuffle(&mut rng);

        let t0 = Instant::now();
        build_i64_tree(&asc);
        record!(format!("build_ascending (n={n})"), n, t0.elapsed().as_secs_f64());

        let t0 = Instant::now();
        build_i64_tree(&desc);
        record!(format!("build_descending (n={n})"), n, t0.elapsed().as_secs_f64());

        let t0 = Instant::now();
        let t_random = build_i64_tree(&rand);
        record!(format!("build_random (n={n})"), n, t0.elapsed().as_secs_f64());

        let hit_keys: Vec<i64> = (0..n_queries).map(|_| rng.gen_range(0..n) as i64).collect();
        let t0 = Instant::now();
        for &k in &hit_keys {
            t_random.search(k);
        }
        record!(format!("search_hits (n={n}, q={n_queries})"), n_queries, t0.elapsed().as_secs_f64());

        let miss_keys: Vec<i64> = (0..n_queries).map(|_| n as i64 + rng.gen_range(0..n) as i64).collect();
        let t0 = Instant::now();
        for &k in &miss_keys {
            t_random.search(k);
        }
        record!(format!("search_misses (n={n}, q={n_queries})"), n_queries, t0.elapsed().as_secs_f64());

        let t0 = Instant::now();
        {
            let mut t = TreeImpl::Leaf { key: 0, values: vec![0i64] };
            for i in 1..n as i64 {
                t = t.add(0, i);
            }
        }
        record!(format!("duplicate_adds (n={n})"), n, t0.elapsed().as_secs_f64());

        let branch_keys: Vec<i64> = (0..n as i64).map(|i| -(i + 1)).collect();
        let t0 = Instant::now();
        for &k in &branch_keys {
            let _ = t_random.add(k, k);
        }
        record!(format!("persistent_branch (n={n})"), n, t0.elapsed().as_secs_f64());
    }

    Py::new(py, BenchmarkResults { label, scenarios })
}
