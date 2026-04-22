use std::sync::Arc;
use pyo3::prelude::*;
use pyo3::types::PyTuple;
use pyo3_stub_gen::define_stub_info_gatherer;
use pyo3_stub_gen::derive::{gen_stub_pyclass, gen_stub_pyfunction, gen_stub_pymethods};

#[derive(Clone)]
enum TreeImpl {
    Leaf{ key: i64, values: Vec<Arc<Py<PyAny>>>},
    Node{ pivot: i64, left: Arc<TreeImpl>, right: Arc<TreeImpl>}
}

impl TreeImpl {
    pub fn search(&self, key: i64) -> Option<&Vec<Arc<Py<PyAny>>>> {
        match self {
            TreeImpl::Leaf{ key: k, values } => {
                if *k == key {
                    Some(values)
                } else {
                    None
                }
            },
            TreeImpl::Node{ pivot, left, right } => {
                if *pivot >= key {
                    left.search(key)
                } else {
                    right.search(key)
                }
            }
        }
    }

    pub fn add(&self, key: i64, value: Py<PyAny>) -> TreeImpl {
        match self {
            TreeImpl::Leaf {
                key: k,
                values
            } => {
                if *k == key {
                    let mut new_values = values.clone();
                    new_values.push(Arc::new(value));
                    TreeImpl::Leaf{ key: *k, values: new_values }
                } else if *k > key {
                    TreeImpl::Node {pivot: key, left: Arc::new(TreeImpl::Leaf{ key, values: vec![Arc::new(value)] }), right: Arc::new(self.clone())}
                } else {
                    TreeImpl::Node {pivot: *k, left: Arc::new(self.clone()), right: Arc::new(TreeImpl::Leaf{ key, values: vec![Arc::new(value)] })}
                }
            },
            TreeImpl::Node {
                pivot, left, right
            } => {
                if *pivot >= key {
                    let new_left = left.add(key, value);
                    TreeImpl::Node {
                        pivot: *pivot,
                        left: Arc::new(new_left),
                        right: right.clone()
                    }
                } else {
                    let new_right = right.add(key, value);
                    TreeImpl::Node {
                        pivot: *pivot,
                        left: left.clone(),
                        right: Arc::new(new_right)
                    }
                }
            }
        }
    }
}

#[pyclass(frozen)]
#[gen_stub_pyclass]
struct Tree(TreeImpl);

#[pymethods]
#[gen_stub_pymethods]
impl Tree {
    fn add(&self, key: i64, val: Py<PyAny>) -> Self {
        Tree(self.0.add(key, val))
    }

    fn search<'py>(&self, key: i64, python: Python<'py>) -> PyResult<Bound<'py, PyTuple>> {
        let results = self.0.search(key);
        if let Some(results) = results {
           PyTuple::new(python, results.iter().map(|t| t.as_ref().clone_ref(python)))
        } else {
            Ok(PyTuple::empty(python))
        }

    }
}

#[pyfunction]
#[gen_stub_pyfunction]
fn make_unit(key: i64, val: Py<PyAny>) -> Tree {
    Tree(TreeImpl::Leaf{ key, values: vec![Arc::new(val)] })
}


#[pymodule]
#[pyo3(name = "native")]
fn native(m: &Bound<PyModule>) -> PyResult<()> {
    m.add_class::<Tree>()?;
    m.add_function(wrap_pyfunction!(make_unit, m)?)?;
    Ok(())
}

define_stub_info_gatherer!(stub_info);
